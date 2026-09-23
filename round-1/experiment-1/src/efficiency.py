#!/usr/bin/env python3
"""Abliteration EFFICIENCY of the two siblings on the SAME edits (CPU, from the journals).

The A3 screen asks whether the siblings' outcomes agree in rank. This asks a different and more
behavioural question: for one and the same edit, how much refusal does each model give up per unit of
representational damage (first-token KL on harmless prompts)? Because the edits are identical, the
edit itself is held constant by construction, so the comparison needs no strength control: it is a
paired, within-edit contrast with the edit as the resampling unit.

Reported for the 60 shared startup edits and (if both journals have them) for every shared trial:
  * refusal drop per unit KL, per model, median over edits, paired bootstrap over edits
  * the ratio of those medians (the "efficiency gap"), paired bootstrap
  * a KL-matched contrast: for each edit, Gemma's refusals minus GaMS's refusals restricted to edits
    whose KL is similar in both models (|log KL_A - log KL_B| below its median), which removes the
    "maybe Gemma was just edited less hard" explanation
  * the same numbers computed with refusal RATE change instead of count, and with log KL
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from loguru import logger

WS = Path(__file__).resolve().parent
sys.path.insert(0, str(WS))
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")

BASELINE_REFUSALS = {"gams": 98, "gemma": 100}  # printed by Heretic before optimization (out of 100)


def boot_median(x: np.ndarray, n: int = 5000, seed: int = 0) -> list[float]:
    rng = np.random.default_rng(seed)
    b = [np.median(x[rng.integers(0, len(x), len(x))]) for _ in range(n)]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def boot_ratio_of_medians(x: np.ndarray, y: np.ndarray, n: int = 5000, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    b = []
    for _ in range(n):
        i = rng.integers(0, len(x), len(x))  # paired resample: same edits for both models
        my, mx = np.median(y[i]), np.median(x[i])
        if my > 0:
            b.append(mx / my)
    return {"ratio_of_medians": float(np.median(x) / np.median(y)),
            "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]}


def main() -> None:
    import a3_screen as A

    a, b = A.load_trials("gams"), A.load_trials("gemma")
    pcols = sorted(c for c in a.columns if c.startswith("p."))

    def identical(i: int) -> bool:
        return (a.iloc[i]["state"] == "COMPLETE" and b.iloc[i]["state"] == "COMPLETE"
                and a.iloc[i]["abl_params"] == b.iloc[i]["abl_params"]
                and all(a.iloc[i][c] == b.iloc[i][c] for c in pcols))

    # PRE-REGISTERED unit of analysis: the 60 TPE startup trials, which are identical by construction
    # because both runs share one sampler seed. Later TPE proposals depend on the observed objective
    # values and so generally differ; occasionally one coincides, and those are reported separately
    # rather than folded into the headline (their number would otherwise grow as a run progresses).
    shared = [i for i in range(min(60, len(a), len(b))) if identical(i)]
    extra = [i for i in range(60, min(len(a), len(b))) if identical(i)]
    out = {"n_shared_identical_edits": len(shared),
           "unit_of_analysis": "the 60 TPE startup edits (identical parameter draws in both models)",
           "coincidentally_identical_later_trials": extra,
           "baseline_refusals": BASELINE_REFUSALS}

    A_, B_ = a.iloc[shared], b.iloc[shared]
    ra, rb = A_.refusals.values.astype(float), B_.refusals.values.astype(float)
    ka, kb = A_.kl.values.astype(float), B_.kl.values.astype(float)
    da, db = BASELINE_REFUSALS["gams"] - ra, BASELINE_REFUSALS["gemma"] - rb
    ea, eb = da / np.maximum(ka, 1e-9), db / np.maximum(kb, 1e-9)

    out["refusals"] = {"gams": {"median": float(np.median(ra)), "min": float(ra.min()), "max": float(ra.max())},
                       "gemma": {"median": float(np.median(rb)), "min": float(rb.min()), "max": float(rb.max())}}
    out["kl"] = {"gams_median": float(np.median(ka)), "gemma_median": float(np.median(kb))}
    out["efficiency_refusal_drop_per_unit_kl"] = {
        "gams_median": float(np.median(ea)), "gams_ci95": boot_median(ea),
        "gemma_median": float(np.median(eb)), "gemma_ci95": boot_median(eb),
        "gap": boot_ratio_of_medians(ea, eb)}

    # paired within-edit refusal difference (Gemma - GaMS), the edit is the resampling unit
    diff = rb - ra
    out["paired_refusal_difference_gemma_minus_gams"] = {
        "median": float(np.median(diff)), "ci95": boot_median(diff),
        "mean": float(diff.mean()),
        "n_edits_where_gemma_refuses_more": int((diff > 0).sum()),
        "n_edits_where_gams_refuses_more": int((diff < 0).sum())}

    # KL-matched subset: edits whose damage is comparable in the two models
    lk = np.abs(np.log(ka + 1e-9) - np.log(kb + 1e-9))
    sel = lk <= np.median(lk)
    out["kl_matched_subset"] = {
        "criterion": "|log KL_gams - log KL_gemma| <= its median over the shared edits",
        "n": int(sel.sum()),
        "kl_median_gams": float(np.median(ka[sel])), "kl_median_gemma": float(np.median(kb[sel])),
        "refusals_median_gams": float(np.median(ra[sel])), "refusals_median_gemma": float(np.median(rb[sel])),
        "paired_diff_median": float(np.median(diff[sel])), "paired_diff_ci95": boot_median(diff[sel])}

    # the subset where the edit actually worked on GaMS
    m = ra <= 50
    out["edits_effective_on_gams"] = {
        "criterion": "GaMS refusals <= 50/100", "n": int(m.sum()),
        "gams_refusals_mean": float(ra[m].mean()) if m.any() else None,
        "gemma_refusals_mean": float(rb[m].mean()) if m.any() else None,
        "gemma_refusals_min": float(rb[m].min()) if m.any() else None,
        "gams_kl_median": float(np.median(ka[m])) if m.any() else None,
        "gemma_kl_median": float(np.median(kb[m])) if m.any() else None}
    m2 = rb <= 50
    out["edits_effective_on_gemma"] = {
        "criterion": "Gemma refusals <= 50/100", "n": int(m2.sum()),
        "gams_refusals_mean": float(ra[m2].mean()) if m2.any() else None,
        "gemma_refusals_mean": float(rb[m2].mean()) if m2.any() else None}
    out["interpretation_limits"] = (
        "Two models are two units: this quantifies a difference between THESE two checkpoints under "
        "THESE conditions (bnb_4bit NF4, one optimizer seed, English keyword refusal scoring, 4-bit "
        "dequantized edits). It does not attribute the difference to Slovene continued pretraining, to "
        "instruction tuning or to any particular training stage - GaMS3-12B-Instruct is a same-family "
        "reference, not a controlled derivative of this Gemma checkpoint. The published bf16 Heretic edit "
        "of gemma-3-12b-it reaches 3/100 refusals with 200 trials, so the Gemma arm's resistance here is "
        "confounded with quantization and with the reduced trial budget and must not be read as "
        "'gemma-3-12b-it cannot be abliterated'.")
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results" / "efficiency.json").write_text(json.dumps(out, indent=1))
    logger.info(json.dumps({k: v for k, v in out.items()
                            if k in ("n_shared_identical_edits", "efficiency_refusal_drop_per_unit_kl",
                                     "paired_refusal_difference_gemma_minus_gams", "kl_matched_subset")},
                           indent=1))


if __name__ == "__main__":
    main()

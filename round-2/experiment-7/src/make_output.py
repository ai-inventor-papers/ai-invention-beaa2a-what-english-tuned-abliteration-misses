#!/usr/bin/env python3
"""STEP 9: method_out.json (exp_gen_sol_out). examples = one row per scored edit (params in, traits out), plus the
original model's per-item rows; metadata = gates, Gap/B/SIMEX/stability/margin tables, carrier, forecasts, verdicts."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

WS = Path(__file__).resolve().parent
RES = WS / "results"


def rj(p: Path, default=None):
    return json.loads(p.read_text()) if p.exists() else default


def main() -> None:
    A = rj(RES / "analysis.json", {})
    it = pd.read_parquet(RES / "panel" / "item_traits.parquet")
    cov = pd.read_parquet(RES / "panel" / "edit_covariates.parquet")
    VL = rj(RES / "validity" / "judged.json", {}) or {}
    VA = rj(RES / "validity" / "judged_api.json", {}) or {}
    use_api = bool(VA) and set(VL) <= set(VA)
    V = VA if use_api else VL
    V2 = VL if use_api else VA
    lvl = it.groupby(["edit_id", "trait_key", "role", "lang", "half"])["delta"].mean()
    ex = []
    for _, c in cov.iterrows():
        e = c["edit_id"]
        raw = json.loads((RES / "panel" / "edits" / f"{e}.json").read_text())
        traits = {}
        for (tk, role, lg, h), v in lvl.loc[e].items():
            name = {"R_seq": "Rb" if role == "harmless" else "R_seq", "R1": "R1_benign" if role == "harmless" else "R1"}.get(tk, tk)
            if tk in ("lp_ref", "lp_comp"):
                name = f"{tk}_{role}"
            traits[f"{name}_{lg}_{h}"] = float(v)
        vrec = None
        if e in V:
            vrec = {f"{lg}_{ro}": float(np.mean([x["label"] == "refused" for x in V[e] if x["lang"] == lg and x["role"] == ro]))
                    for lg in ("en", "sl") for ro in ("harmful", "harmless")}
        vrec2 = None
        if e in V2:
            vrec2 = {f"{lg}_{ro}": float(np.mean([x["label"] == "refused" for x in V2[e] if x["lang"] == lg and x["role"] == ro]))
                     for lg in ("en", "sl") for ro in ("harmful", "harmless")}
        row = {"input": json.dumps({"edit_id": e, "set": c["set"], "trial": None if pd.isna(c["trial"]) else int(c["trial"]),
                                    "direction_index": raw["direction_index"], "parameters": raw["parameters"], "raw_params": raw["raw_params"]}),
               "output": json.dumps({"traits_edit_level_delta_vs_original": traits, "collapsed": bool(c["collapsed"]),
                                     "judged_refusal_rates_halfB": vrec, "judged_refusal_rates_halfB_secondary_judge": vrec2,
                                     "primary_judge": "api_gpt-4.1" if use_api else "local_gemma-3-12b-it"}),
               "metadata_edit_id": e, "metadata_set": c["set"], "metadata_collapsed": bool(c["collapsed"]),
               "metadata_journal_refusals_en_keyword": None if pd.isna(c["journal_refusals"]) else int(c["journal_refusals"]),
               "metadata_journal_kl": None if pd.isna(c["journal_kl"]) else float(c["journal_kl"]),
               "metadata_covariates": {k: (None if (isinstance(v, float) and np.isnan(v)) else (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v))
                                       for k, v in c.items() if k not in ("edit_id", "set")},
               "metadata_timing_s": raw["timing"], "metadata_trim": raw["trim"],
               "predict_EN_A_Rseq_delta": f"{traits.get('R_seq_en_A', float('nan')):.4f}",
               "predict_SL_B_Rseq_delta": f"{traits.get('R_seq_sl_B', float('nan')):.4f}"}
        ex.append(row)
    orig = rj(RES / "orig_generations.json", {})
    jl = rj(RES / "judge_local.json", {})
    ox = []
    api_o = rj(RES / "judged_api_orig.json", []) or []
    for n, (g, j) in enumerate(zip(orig.get("jbb", []) + orig.get("dolly_A", []), jl.get("orig", []))):
        r = {"input": g["prompt"], "output": g["text"], "metadata_sid": g["sid"], "metadata_lang": g["lang"], "metadata_role": g["role"],
             "metadata_half": g["half"], "predict_local_judge_label": j["label"]}
        if n < len(api_o):
            r["predict_api_gpt41_judge_label"] = api_o[n]["label"]
        ox.append(r)
    geo = rj(RES / "geometry_report.json", {})
    meta = {
        "method_name": "Gemma P1 random-edit panel: what English misses in Slovene",
        "model": "google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80 (bnb_4bit NF4, bf16 compute), Heretic 3521f864",
        "workspace": str(WS),
        "setup_checks": rj(RES / "setup_checks.json"), "smoke_T1": rj(RES / "smoke_T1.json"), "T0_synthetic": rj(RES / "T0_synthetic.json"),
        "E0_redraw_certificate": rj(WS / "edits" / "E0_redraw_certificate.json"),
        "trim_decision": rj(WS / "protocol" / "trim_decision.json"), "validity_edits": rj(WS / "protocol" / "validity_edits.json"),
        "frozen_predictions": rj(WS / "protocol" / "frozen_predictions.json"),
        "protocol_hash": (WS / "protocol" / "protocol_hash.txt").read_text().strip() if (WS / "protocol" / "protocol_hash.txt").exists() else None,
        "local_judge_validation_vs_gpt41": {k: v for k, v in (jl.get("validation_vs_gpt41") or {}).items() if k != "rows"},
        "judge_references_and_r_prior": jl.get("judge"), "judge_deviation": jl.get("deviation"),
        "judge_validity_primary": "api_gpt-4.1" if use_api else "local_gemma-3-12b-it",
        "api_cost_usd": sum(json.loads(x)["cost"] for x in (WS / "logs" / "cost_log.jsonl").read_text().splitlines() if x.strip()) if (WS / "logs" / "cost_log.jsonl").exists() else 0.0,
        "references_source_counts": (rj(WS / "references" / "refs.json", {}) or {}).get("source_counts"),
        "geometry": {k: v for k, v in geo.items() if not k.startswith("auroc_") or k in ("auroc_P_halfB_jbb_benign", "auroc_H_halfB")},
        "analysis": A, "audit": rj(RES / "audit.json"), "api_probe": rj(RES / "api_probe.json"), "api_budget_block": rj(RES / "api_budget_block.json"),
        "what_this_does_NOT_show": [
            "The carrier regression is CORRELATIONAL across random edits: P can be said to predict, not to carry, the SL-specific residual (no causal intervention in this pod).",
            "4-bit NF4 weights: absolute refusal/KL levels are not comparable to published bf16 Heretic numbers.",
            "One model (gemma-3-12b-it); every GaMS-vs-Gemma comparison belongs to the downstream synthesis.",
            "DEV-only items (S3 JBB/Dolly/FLORES/MC halves); FINAL splits S5-S7 were never touched.",
            "Slovene items are machine-translated with automated QC; native review is PENDING.",
            ("Validity-gate refusal labels come from the frozen gpt-4.1 judge; the refusal/compliance REFERENCES and r_prior were frozen earlier from a LOCAL judge (original gemma-3-12b-it, same rubric) while the API key was blocked, and were not refit; local-vs-gpt-4.1 agreement on exactly those rows is reported."
             if use_api else
             "Refusal labels of the validity edits come from a LOCAL judge (the original gemma-3-12b-it with the frozen gpt-4.1 rubric), because the API judge was blocked (daily key limit, then the run-wide phase budget); its agreement with gpt-4.1 on the original's 440 generations and with the iteration-1 gpt-4.1 labels is reported and bounds every judged claim."),
            "Prompt/item-level CIs do not measure run-to-run optimizer variance; the edit bootstrap covers edit sampling only within Heretic's prior.",
            "The carrier covariate H (language asymmetry of the removal along the directly targeted d_EN) was added after the freeze: its incremental R2 is EXPLORATORY and correlational.",
            "The panel ran on three GPUs (RTX 4090, L4, RTX 4000 Ada) across session interruptions; every edit is zero-pointed against the original scored on the same device and trim, and E0_000 was re-scored on each later device (cross_device_reproducibility), but device is confounded with edit set order (E0 mostly 4090; late E1 on RTX 4000 Ada).",
            "Judged SL harmful refusal among the validity edits is near-saturated (most edits 39-41/41), so SL validity rests on few informative edits.",
        ],
    }
    out = {"metadata": meta, "datasets": [{"dataset": "gemma_p1_edit_panel", "examples": ex},
                                          {"dataset": "gemma_original_generations_S3_jbb_dolly", "examples": ox}]}
    (WS / "method_out.json").write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    print(f"method_out.json: {len(ex)} edit rows, {len(ox)} original rows")


if __name__ == "__main__":
    main()

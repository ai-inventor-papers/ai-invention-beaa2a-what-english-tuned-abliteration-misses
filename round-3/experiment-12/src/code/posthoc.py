#!/usr/bin/env python3
"""POST-HOC / EXPLORATORY decomposition, run AFTER the frozen analysis and clearly separated from it.
It does not change any verdict: the pre-registered P1 is a POOLED Spearman and it FAILED. This script only asks *why*
it failed, and is reported as exploratory.

Motivation: the re-derivation's language-shuffle placebo returned a systematically negative correlation (-0.356) rather
than ~0. That is the signature of a predictor whose within-group signal is cancelled by a between-group offset, so the
decomposition below is the diagnostic that placebo demanded.

Reports, per model: Spearman(predictor, residual) within that model, the index's variance there, and the pooled
within-model-centred Spearman. Output: results/posthoc_decomposition.json."""
from __future__ import annotations

import numpy as np
from loguru import logger

import common as C
from analysis import spearman

PREDS = ["index", "auc", "B_cos", "B_ss", "B_base", "B_margin"]


def main() -> None:
    C.setup_logging("posthoc")
    A = C.jload(C.RES / "analysis.json")
    rows = A["rows"]
    out: dict = {"status": "POST-HOC / EXPLORATORY - not part of the freeze, changes no verdict",
                 "frozen_P1_pooled_spearman": A["P1"]["spearman"], "frozen_verdict": A["verdict"], "per_model": {}}
    for m in sorted({r["m"] for r in rows}):
        sub = [r for r in rows if r["m"] == m]
        y = [r["residual"] for r in sub]
        d = {"n_rows": len(sub), "n_languages": len({r["L"] for r in sub}),
             "index_values": sorted({r["index"] for r in sub}),
             "index_has_variance": len({r["index"] for r in sub}) > 1,
             "mean_residual": float(np.mean(y))}
        for p in PREDS:
            d[f"rho_{p}"] = spearman([r[p] for r in sub], y)
        out["per_model"][m] = d
    # pooled after removing each model's mean predictor and mean residual (a within-model / fixed-effects view)
    cent: dict = {p: ([], []) for p in PREDS}
    for m in sorted({r["m"] for r in rows}):
        sub = [r for r in rows if r["m"] == m]
        yv = np.array([r["residual"] for r in sub], float)
        for p in PREDS:
            xv = np.array([r[p] for r in sub], float)
            cent[p][0].extend((xv - xv.mean()).tolist())
            cent[p][1].extend((yv - yv.mean()).tolist())
    out["pooled_within_model_centred"] = {p: spearman(*cent[p]) for p in PREDS}
    out["interpretation"] = (
        "The pre-registered P1 pools rows across models. Within the anchor model (gemma) the frozen index orders the four "
        "languages' residuals well, but in qwen3 every eligible language shares the SAME index value (0.75), so the index "
        "has zero variance there and cannot predict qwen3's residual spread by construction, while still contributing "
        "residual variance to the pooled statistic. Together with a between-model offset in residual level this cancels "
        "the pooled correlation to ~0. The pooled test is the one that was frozen, so FALSIFY stands; what this "
        "decomposition shows is that the index is not pure noise, it is a WITHIN-MODEL quantity that the pre-registered "
        "pooled test was not able to detect - and that the two baselines which do survive pooling (single-site transfer "
        "and baseline refusal) survive precisely because they are measured on the same 0-1 refusal scale in every model, "
        "so they need no per-model calibration. That is also what makes them the more useful practical predictors.")
    C.jdump(out, C.RES / "posthoc_decomposition.json")
    for m, d in out["per_model"].items():
        logger.info(f"{m}: n={d['n_rows']} index_var={d['index_has_variance']} rho_index={d['rho_index']} "
                    f"rho_B_ss={d['rho_B_ss']:.3f} rho_B_cos={d['rho_B_cos']:.3f}")
    logger.info(f"pooled within-model-centred: { {k: (round(v, 3) if v == v else None) for k, v in out['pooled_within_model_centred'].items()} }")


if __name__ == "__main__":
    main()

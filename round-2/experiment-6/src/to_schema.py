#!/usr/bin/env python3
"""Build method_out.json (exp_gen_sol_out schema): one example per panel edit (input = Heretic parameters + set;
output = EN/SL trait aggregates + covariates; predict_* = out-of-fold SL forecasts from EN traits with / without D);
metadata = verdict, gap table, carrier, forecast, validity, reselection, unit tests, deviations, costs, kept paths.

  uv run to_schema.py
"""
from __future__ import annotations

import json

import numpy as np

import analysis as AN
from common import CostLedger, RES, ROOT, jdump, jload, setup_logging


def main() -> None:
    setup_logging("to_schema")
    res = jload(RES / "analysis_results.json")
    p, _ = AN.build_panel()
    ed = p.edits
    F = np.where(AN.fitted_mask(ed))[0]
    w0 = AN.unit_weights(p)
    allE = np.arange(len(ed))
    kind = res["learner_adequacy"]["primary"]
    X = AN.xmat(p, w0, "A", 0, allE)
    Xd = np.concatenate([X, ed["D"].values[:, None]], 1)
    preds = {}
    for t in ("R", "K", "N", "M"):
        y = AN.aggregate(p.traits[t], w0[t], "B", 1, None, allE)
        oof_b = np.full(len(ed), np.nan)
        oof_d = np.full(len(ed), np.nan)
        oof_b[F] = AN.oof_pred(X[F], y[F], kind, AN.SEEDS[0])
        oof_d[F] = AN.oof_pred(Xd[F], y[F], kind, AN.SEEDS[0])
        nf = np.setdiff1d(allE, F)
        if len(nf):
            oof_b[nf] = AN.make_learner(kind).fit(X[F], y[F]).predict(X[nf])
            oof_d[nf] = AN.make_learner(kind).fit(Xd[F], y[F]).predict(Xd[nf])
        preds[t] = (oof_b, oof_d)
    cov_cols = [c for c in ed.columns if c in ("D", "D_mean", "D_var", "D_resp", "E_en", "E_sl", "b1", "b2", "Omega", "b3_total",
                                               "H_en", "H_sl", "P_en", "P_sl", "realized_E_en", "realized_E_sl", "collapsed",
                                               "journal_refusals", "journal_kl", "t_total_s", "peak_vram_gb")]
    examples = []
    for i, r in ed.iterrows():
        agg = {}
        for t in AN.GAP_TRAITS + ["NLLrise"]:
            tm = p.traits[t]
            for li, l in enumerate(("en", "sl")):
                for h in ("A", "B"):
                    agg[f"{t}_{l}_{h}"] = float(AN.aggregate(tm, w0[t], h, li, None, np.array([i]))[0])
        out = {"traits": agg, "covariates": {c: (None if isinstance(r[c], float) and not np.isfinite(r[c]) else r[c]) for c in cov_cols}}
        ex = {"input": json.dumps({"edit_id": r.edit_id, "set": r.set, "raw_params": r.raw_params, "direction_index": r.direction_index},
                                  default=str),
              "output": json.dumps(out, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
              "metadata_edit_id": r.edit_id, "metadata_set": r.set, "metadata_fitted": bool(i in set(F)),
              "metadata_is_core": bool(r.is_core), "metadata_collapsed": bool(r.collapsed)}
        for t in ("R", "K", "N", "M"):
            ex[f"predict_baseline_en_traits_sl_{t}"] = f"{preds[t][0][i]:.5f}"
            ex[f"predict_our_method_en_traits_plus_D_sl_{t}"] = f"{preds[t][1][i]:.5f}"
        examples.append(ex)
    ut = jload(RES / "unit_tests.json")
    meta = {"method_name": "P1 random-edit panel (GaMS3-12B-Instruct): placebo-controlled EN->SL surrogacy of Heretic edits",
            "model": "cjvt/GaMS3-12B-Instruct@1d0b27af (bnb_4bit NF4, Heretic 3521f864)",
            "predict_fields": "predict_baseline_* = SL half-B trait forecast from EN half-A traits (out-of-fold on F, fitted-on-F for "
                              "E_TPE/E_R); predict_our_method_* = same + exposure D",
            "verdict": res["verdict"], "gap": {t: {k: v for k, v in g.items() if k != "directions"} for t, g in res["gap"].items()},
            "bootstrap": res["bootstrap"], "B_t": res["B_t"], "simex": res["simex"], "margin_matched": res["margin_matched"],
            "stability": res["stability"], "reliability": res["reliability"], "no_signal_F8": res["no_signal_F8"],
            "learner_adequacy": res["learner_adequacy"], "carrier": res.get("carrier"), "forecast": res["forecast"],
            "gap_heretic": res["gap_heretic"], "reselection": {k: v for k, v in res["reselection"].items() if k != "pareto_points"},
            "validity": res["validity"], "unit_tests": {k: v for k, v in ut.items() if k != "template"},
            "ladder_decision": jload(RES / "ladder_decision.json"), "n_F": res["n_F"],
            "judge_meta": jload(RES / "judge_meta.json") if (RES / "judge_meta.json").exists() else None,
            "deviations": jload(RES / "deviations.json") if (RES / "deviations.json").exists() else None,
            "mixed_model": res.get("mixed_model"), "transfer_slopes": res.get("transfer_slopes"), "param_attribution": res.get("param_attribution"),
            "source_carrier": res.get("source_carrier"), "k_ratio_carriers": res.get("k_ratio_carriers"), "core_logratio": res.get("core_logratio"),
            "forecast_quantile_gbt": res.get("forecast_quantile_gbt"), "judge_recounts": res.get("judge_recounts"),
            "post_tests": jload(RES / "post_tests.json") if (RES / "post_tests.json").exists() else None,
            "repro_check": jload(RES / "repro_check.json") if (RES / "repro_check.json").exists() else None,
            "audit": jload(RES / "audit.json") if (RES / "audit.json").exists() else None,
            "rederive_headlines": jload(RES / "rederive_headlines.json") if (RES / "rederive_headlines.json").exists() else None,
            "u6_flores_check": jload(RES / "u6_flores_check.json") if (RES / "u6_flores_check.json").exists() else None,
            "synth_test": jload(RES / "synth_test.json") if (RES / "synth_test.json").exists() else None,
            "frozen_hashes": {f: (RES / f"{f}.sha256").read_text().strip() for f in ("frozen_protocol.json", "frozen_predictions.json",
                                                                                     "ladder_decision.json", "references.json",
                                                                                     "compliance_refs_gams_core.json") if (RES / f"{f}.sha256").exists()},
            "api_cost_usd": CostLedger().spent(),
            "kept_paths": {"workspace": str(ROOT), "results": str(RES), "panel_items": str(RES / "panel_items"),
                           "references": str(RES / "references.json"), "compliance_refs_export": str(RES / "compliance_refs_gams_core.json")}}
    jdump({"metadata": meta, "datasets": [{"dataset": "P1_panel_gams3_S3dev", "examples": examples}]}, ROOT / "method_out.json")
    print(f"wrote {len(examples)} examples")


if __name__ == "__main__":
    main()

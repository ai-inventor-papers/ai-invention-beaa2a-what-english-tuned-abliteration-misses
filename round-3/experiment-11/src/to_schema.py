#!/usr/bin/env python3
"""STEP 7.5 - method_out.json in the exp_gen_sol_out schema.

datasets[0] "final_eval_S5X_S4hoc_XSTest": one example per evaluation prompt; input = prompt, output = expected behaviour
            (refuse for harmful, comply for XSTest-safe); predict_<arm> = that arm's greedy response; metadata_* =
            set/lang/pair ids and every judge's label per arm (Qwen3-14B class, PolyGuard refusal/harm, Llama-Guard).
datasets[1] "heretic_inloop_draws": one example per Heretic draw (116 iteration-1 draws re-measured here + the
            corrected run's 116 trials); input = the draw's parameters, output = Qwen3-14B judged refusals/100 (when
            judged), predict_keyword_objective / predict_partial_aware_objective = the two objectives' counts.
metadata   = every analysis object, the certification, coverage, frozen predictions WITH verdicts, cost log, deviations,
            cut order, pins, and the absolute workspace paths of kept artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

WS = Path(__file__).resolve().parent


def rj(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def jl(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main() -> None:
    arms = json.loads((WS / "arms.json").read_text())
    names = [a["arm"] for a in arms]
    items = json.loads((WS / "results/eval_items.json").read_text())["items"]
    gen = {(r["arm"], r["item_key"]): r for a in names for r in rj(WS / f"results/eval_gen/{a}.jsonl")}
    Q = {r["key"]: r for r in rj(WS / "results/judge_out/eval_qwen.jsonl") if not r.get("judge_fail")}
    PG = {r["key"]: r for r in rj(WS / "results/judge_out/eval_polyguard.jsonl")}
    LG = {r["key"]: r for r in rj(WS / "results/judge_out/eval_llamaguard.jsonl")}
    def key(a: str) -> str:  # schema keys must match ^[a-zA-Z_][a-zA-Z0-9_]*$ (arm names contain '.')
        return a.replace(".", "_")
    ex = []
    for it in items:
        e = {"input": it["prompt"], "output": "refuse" if it["role"] == "harmful" else "comply",
             "metadata_item_key": it["item_key"], "metadata_set": it["set"], "metadata_lang": it["lang"],
             "metadata_semantic_id": it["semantic_id"], "metadata_pair_id": it.get("pair_id") or ""}
        for a in names:
            g = gen.get((a, it["item_key"]))
            if g is None:
                continue
            k = f"{a}|{it['item_key']}"
            e[f"predict_{key(a)}"] = g["response_text"]
            e[f"metadata_qwen_class_{key(a)}"] = Q.get(k, {}).get("cls")
            e[f"metadata_hit_max_{key(a)}"] = g["hit_max"]
            if k in PG:
                e[f"metadata_polyguard_refusal_{key(a)}"] = PG[k].get("pg_refusal")
                e[f"metadata_polyguard_harmful_response_{key(a)}"] = PG[k].get("pg_harmful_response")
            if k in LG:
                e[f"metadata_llamaguard_{key(a)}"] = LG[k].get("lg_label")
        ex.append(e)
    draws = []
    mt = pd.read_csv(WS / "results/miscalibration_table.csv")
    it1 = pd.read_csv(WS / "inputs/iter1_trials_gemma.csv")
    it1 = it1.set_index("number")
    for _, r in mt.iterrows():
        t = int(r["trial"])
        draws.append({"input": json.dumps({"run": "iteration-1 draw (re-measured on this GPU)", "trial": t,
                                           "direction_scope": r["direction_scope"],
                                           "abl_params": json.loads(it1.loc[t, "abl_params"])}),
                      "output": "" if pd.isna(r["judge_refused"]) else f"{int(r['judge_refused'])}/100 judged refusals (Qwen3-14B)",
                      "predict_keyword_objective": f"{int(r['keyword_refusals'])}/100",
                      "predict_partial_aware_objective": f"{int(r['classifier_refusals'])}/100",
                      "metadata_kl": float(r["kl"]), "metadata_source": r["source"],
                      "metadata_judge_partial": None if pd.isna(r["judge_partial"]) else int(r["judge_partial"]),
                      "metadata_iter1_keyword_refusals": int(r["iter1_keyword_refusals"]), "metadata_iter1_kl": float(r["iter1_kl"])})
    tc = WS / "results/trials_gemma_corrected.csv"
    if tc.exists():
        for _, r in pd.read_csv(tc).iterrows():
            draws.append({"input": json.dumps({"run": "corrected-objective run", "trial": int(r["number"]),
                                               "direction_scope": r["p.direction_scope"], "abl_params": json.loads(r["abl_params"])}),
                          "output": "", "predict_partial_aware_objective": f"{int(r['corrected_refusals'])}/100",
                          "metadata_kl": float(r["kl"]), "metadata_source": "corrected_run"})
    costs = rj(WS / "results/cost_log.jsonl")
    meta = {
        "method_name": "C3: partial-aware refusal objective for Heretic abliteration (gemma-3-12b-it, EN/SL)",
        "workspace": str(WS),
        "protocol": (WS / "protocol.yaml").read_text(),
        "freeze_hashes": (WS / "logs/freeze_hashes.txt").read_text(),
        "arms": arms,
        "certification_base": jl(WS / "scorer/certification_base.json"),
        "certification_refit": jl(WS / "scorer/certification.json"),
        "classifier_train_report": jl(WS / "scorer/train_report.json"),
        "classifier_refit_report": jl(WS / "scorer/train_report_refit.json"),
        "scorer_unit_test": jl(WS / "results/test_scorer.json"),
        "coverage_summary": jl(WS / "results/coverage_summary.json"),
        "coverage_correlations": jl(WS / "results/coverage_correlations.json"),
        "inloop_analysis": jl(WS / "results/inloop_analysis.json"),
        "eval_analysis": jl(WS / "results/eval_analysis.json"),
        "guard_analysis": jl(WS / "results/guard_analysis.json"),
        "frozen_predictions_with_verdicts": jl(WS / "results/frozen_predictions_with_verdicts.json"),
        "audit_headline": {k: v for k, v in (jl(WS / "results/audit_headline.json") or {}).items() if k != "checks"},
        "audit_extra": jl(WS / "results/audit_extra.json"),
        "replay_fidelity": jl(WS / "results/replay_fidelity.json"),
        "selection_point_certification": jl(WS / "results/selection_point_cert.json"),
        "second_seed": jl(WS / "results/seed2_analysis.json"),
        "kl_per_arm": jl(WS / "results/kl_arms.json"),
        "adapter_delta_norms": jl(WS / "results/adapter_delta_norms.json"),
        "direction_drift_corrected_vs_iter1": jl(WS / "results/direction_drift_corrected_vs_iter1.json"),
        "verify_numbers": jl(WS / "results/verify_numbers.json"),
        "judge_ceiling": jl(WS / "results/judge_ceiling.json"),
        "deviations": jl(WS / "results/deviations.json"),
        "api_cost_usd": sum(float(c.get("cost") or 0) for c in costs),
        "kept_artifacts": {"corrected_run_journal": str(WS / "checkpoints/gemma_corrected"),
                           "corrected_adapter": str(WS / "adapters_corrected"),
                           "classifier": str(WS / "scorer/refusal_clf.joblib"),
                           "results": str(WS / "results"), "logs": str(WS / "logs")},
    }
    out = {"metadata": meta, "datasets": [{"dataset": "final_eval_S5X_S4hoc_XSTest", "examples": ex},
                                          {"dataset": "heretic_inloop_draws", "examples": draws}]}
    (WS / "method_out.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    print(f"method_out.json: {len(ex)} eval examples, {len(draws)} draws")


if __name__ == "__main__":
    main()

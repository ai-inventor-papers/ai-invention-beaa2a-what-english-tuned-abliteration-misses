#!/usr/bin/env python3
"""STAGE S9 - method_out.json in the exp_gen_sol_out schema.

One dataset per search; one example per CANDIDATE (model x trial):
  input   = the candidate (model, trial, phase, direction scope, Heretic parameters) as JSON text
  output  = the OBJECTIVE's count (Heretic KeywordRate, what the optimiser saw)            [baseline]
  predict_certified_classifier = the corrected count C (partial-aware classifier @0.52)   [method]
  predict_keyword_objective    = K again (explicit baseline column)
  predict_keyword_repaired / predict_keyword_oracle_t = the incumbent given its best shot
  predict_judge_qwen3_14b      = judged REFUSED(+empty) count /100 where the candidate was fully judged, else "NA"
  metadata_*                   = KL (replay, journal), sigma_K, per-candidate GBF, descriptors, flags
Top-level metadata = the full analysis, frozen predictions + verdicts, both certifications, deviations, audits.
"""
from __future__ import annotations

import json
import math

import pandas as pd

from common import CONFIGS, RESULTS, WS, write_json


def fmt(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "NA"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return f"{v:.4g}" if isinstance(v, float) else str(v)


def clean(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if hasattr(v, "item"):
        return clean(v.item())
    return v


def sanitize(o):
    """NaN/inf -> None so the file is strict JSON."""
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, list):
        return [sanitize(v) for v in o]
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    return o


def main() -> None:
    pc = pd.read_csv(RESULTS / "per_candidate.csv")
    an = json.loads((RESULTS / "analysis.json").read_text())
    desc_cols = [c for c in pc.columns if c.startswith(("sum_", "attn_", "mlp_")) or c == "mean_cos_in_support"]
    datasets = []
    for m, dsname in (("gemma", "gemma-3-12b-it_heretic_search1_inloop_candidates"),
                      ("gams", "GaMS3-12B-Instruct_heretic_search2_inloop_candidates")):
        d = pc[pc.model == m].sort_values("trial")
        ex = []
        for r in d.to_dict(orient="records"):
            inp = {"model": m, "trial": int(r["trial"]), "phase": r["phase"], "direction_scope": r.get("direction_scope"),
                   "heretic_params": json.loads(r["params_json"]) if isinstance(r.get("params_json"), str) else None,
                   "in_loop_view": "mlabonne/harmful_behaviors test[:100], greedy, 100 new tokens, NF4"}
            e = {"input": json.dumps(inp), "output": fmt(float(r["K"])),
                 "predict_keyword_objective": fmt(float(r["K"])),
                 "predict_certified_classifier": fmt(float(r["C"])),
                 "predict_keyword_repaired": fmt(float(r["K_repaired"])),
                 "predict_judge_qwen3_14b": fmt(r["J"]) if r.get("J_full") else "NA"}
            if "K_oracle" in r:
                e["predict_keyword_oracle_t"] = fmt(float(r["K_oracle"]))
            e["metadata_trial"] = int(r["trial"])
            e["metadata_phase"] = r["phase"]
            for k in ("KL_replay", "KL_journal", "K_journal", "sigma_K", "gbf_i_C", "J_partial", "J_n", "n_judged",
                      "mean_tokens", "share_truncated", "K_empty"):
                if k in r:
                    e[f"metadata_{k}"] = clean(r[k])
            for k in ("in_paired_60", "is_certification_trial", "selected_by_K", "selected_by_C", "selected_by_J"):
                if k in r:
                    e[f"metadata_{k}"] = bool(r[k]) if r[k] == r[k] else False
            e["metadata_descriptors"] = {k: clean(r[k]) for k in desc_cols if k in r}
            ex.append(e)
        datasets.append({"dataset": dsname, "examples": ex})
    def load(p):
        return json.loads(p.read_text()) if p.exists() else None
    meta = {
        "method_name": "Gradient-blind fraction of Heretic's keyword refusal objective, measured on a second search",
        "description": ("Replay-only measurement study. Both Heretic searches (gemma-3-12b-it and GaMS3-12B-Instruct, "
                        "116 candidates each, 60 identical startup draws) re-scored on the optimiser's own in-loop view by "
                        "(i) Heretic's keyword objective K (baseline/incumbent), (ii) the certified partial-aware classifier "
                        "C (method/reference), (iii) a frozen 4-way LLM-judge rubric on certification trials. No new search, "
                        "no new edit selected, exported or recommended."),
        "baseline": "Heretic KeywordRate (imported, shipped rule) + oracle marker-count threshold + repaired marker list",
        "method": "certified partial-aware classifier as reference; gradient-blind fraction (GBF) and secondaries",
        "not_a_better_edit": an["reselection"][0]["not_a_better_edit"] if an.get("reselection") else None,
        "frozen_predictions": load(CONFIGS / "frozen_predictions.json"),
        "freeze_sha256": (CONFIGS / "FREEZE.sha256").read_text().split()[0],
        "analysis": an,
        "gams_certification": load(RESULTS / "gams_certification.json"),
        "judge_certification": load(RESULTS / "judge_certification.json"),
        "journals_G1": load(RESULTS / "s1_journals.json"),
        "replay_fidelity_s3": load(RESULTS / "replay_fidelity_s3.json"),
        "t0_instrument": load(RESULTS / "t0_instrument.json"),
        "rehearsal_gemma_checks": {k: v for k, v in (load(RESULTS / "rehearsal_gemma.json") or {}).items() if k != "analysis"},
        "descriptors_validation": load(RESULTS / "descriptors_validation.json"),
        "rederive": {k: v for k, v in (load(RESULTS / "rederive.json") or {}).items() if k != "checks"},
        "checks": load(RESULTS / "checks.json"),
        "deviations": load(RESULTS / "deviations.json"),
        "api_costs_usd": sum(json.loads(l).get("cost") or 0 for l in (RESULTS / "api_costs.jsonl").read_text().splitlines()
                             if l.strip()) if (RESULTS / "api_costs.jsonl").exists() else 0.0,
    }
    out = sanitize({"metadata": meta, "datasets": datasets})
    write_json(WS / "method_out.json", out)
    print(f"method_out.json: {sum(len(d['examples']) for d in datasets)} examples in {len(datasets)} datasets")


if __name__ == "__main__":
    main()

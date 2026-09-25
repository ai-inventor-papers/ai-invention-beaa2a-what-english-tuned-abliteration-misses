#!/usr/bin/env python3
"""Assemble method_out.json (exp_gen_sol_out): metadata = analysis + frozen predictions + verdicts + deviations + costs +
SHAs + workspace paths; examples = one row per OUTCOME item x language with per-arm responses, labels and R scores."""
from __future__ import annotations

import json

import pandas as pd

import common as C
from common import jdump, jload


def main() -> None:
    S = jload(C.RES / "analysis_summary.json")
    pq = pd.read_parquet(C.RES / "per_item.parquet")
    lab = {r.gid: (r.label, r.label_source) for r in pq.itertuples()}  # the analysis' final labels
    gens = []
    for p in sorted(C.RES.glob("*/gens/*.json")):
        gens += [r for r in jload(p) if r["arm"] not in ("halfA_original", "s2_original")]
    rows = []
    for m in ("gemma", "community", "gams3"):
        p = C.RES / m / "per_item_rows.jsonl"
        if p.exists():
            rows += [json.loads(l) for l in p.read_text().splitlines()]
    rr = pd.DataFrame(rows)
    rr = rr[rr.kind == "out"] if len(rr) else rr
    rix = {(r.model, r.arm, r.uid, r.lang): (r.R1, r.Rseq) for r in rr.itertuples()} if len(rr) else {}
    by: dict = {}
    for g in gens:
        key = (g["uid"], g["lang"])
        e = by.setdefault(key, {"input": g["prompt"], "output": "refuse" if g["role"] == "harmful" else "comply",
                                "metadata_uid": g["uid"], "metadata_semantic_id": g["semantic_id"], "metadata_lang": g["lang"],
                                "metadata_role": g["role"], "metadata_source": g["source"]})
        tag = f"{g['model']}_{g['arm']}".replace(".", "p").replace("-", "_")
        e[f"predict_{tag}"] = g["response"]
        lb, src = lab.get(g["gid"], (g["rule_label"], "rule"))
        e[f"metadata_label_{tag}"] = lb if src != "rule" else f"rule:{lb}"
        r = rix.get((g["model"], g["arm"], g["uid"], g["lang"]))
        if r:
            e[f"metadata_R1_{tag}"] = float(r[0])
            e[f"metadata_Rseq_{tag}"] = float(r[1])
    ds: dict = {}
    for (uid, lang), e in sorted(by.items()):
        name = "outcome_" + ("hoc_" if e["metadata_source"] == "hoc" else "jbbB_") + e["metadata_role"]
        ds.setdefault(name, []).append(e)
    costs = sum(json.loads(l).get("cost", 0) for l in (C.RES / "api_costs.jsonl").read_text().splitlines()) if (C.RES / "api_costs.jsonl").exists() else 0.0
    meta = {"method_name": "r_prior causal test: language-conditioned refusal prior as the carrier of English abliteration's Slovene residual",
            "models": C.MODELS, "adapter_core_edit": {k: str(v) for k, v in C.ADAPTERS["gemma"].items()},
            "frozen_predictions": jload(C.RES / "frozen_predictions.json") if (C.RES / "frozen_predictions.json").exists() else None,
            "frozen_protocol_gemma": jload(C.CFG / "frozen_protocol_gemma.json"),
            "analysis": S, "novelty": jload(C.RES / "novelty.json") if (C.RES / "novelty.json").exists() else None,
            "deviations": jload(C.RES / "deviations.json") if (C.RES / "deviations.json").exists() else None,
            "verify_numbers": jload(C.RES / "verify_numbers.json") if (C.RES / "verify_numbers.json").exists() else None,
            "audit_headline": jload(C.RES / "audit_headline.json") if (C.RES / "audit_headline.json").exists() else None,
            "api_cost_usd": costs,
            "workspace": str(C.ROOT), "paths": {"directions": str(C.DIRS), "results": str(C.RES), "configs": str(C.CFG),
                                                 "figures": str(C.FIGS), "references": str(C.REFS)},
            "column_legend": "predict_<model>_<arm> = greedy response (96 new tokens); metadata_label_<model>_<arm> = gpt-4.1 blind "
                             "label ('rule:<x>' = opener-rule fallback where no judge label exists); R1/Rseq teacher-forced refusal log-odds"}
    out = {"metadata": meta, "datasets": [{"dataset": k, "examples": v} for k, v in sorted(ds.items())]}
    jdump(out, C.ROOT / "method_out.json", indent=None)
    print({k: len(v) for k, v in ds.items()})


if __name__ == "__main__":
    main()

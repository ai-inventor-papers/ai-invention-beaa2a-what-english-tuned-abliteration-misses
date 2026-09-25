#!/usr/bin/env python3
"""Assemble method_out.json (exp_gen_sol_out schema): metadata = pins, protocol hash, deviations, all result tables;
datasets = one per model, examples = one row per S4 item x language x role with judged labels per checkpoint, R_seq/R1
per checkpoint, the original frozen probe score s_i, the r_prior projection p_i, KL1 and KL32, and the responses."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import common as C
from common import MODELS, jdump, jload


def fnum(x):
    try:
        f = float(x)
        return None if not np.isfinite(f) else round(f, 6)
    except (TypeError, ValueError):
        return None


def main() -> None:
    S = jload(C.RES / "analysis" / "summary.json")
    meta = jload(C.RES / "metadata_extra.json") if (C.RES / "metadata_extra.json").exists() else {}
    gv = pd.read_parquet(C.RES / "generation_validity.parquet")
    datasets = []
    for m in MODELS:
        p = C.RES / m / "a2_items.parquet"
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        gens = {(g["ckpt"], g["kind"], g["semantic_id"], g["lang"]): g for g in jload(C.RES / "gens" / f"{m}_gens.json")}
        s4 = {(r["metadata_semantic_id"], r["metadata_lang"], r["metadata_role"]): r["input"]
              for r in (json.loads(l) for l in (C.SPLITS / "S4_strongreject_pairs.jsonl").read_text().splitlines())}
        lab = {(r.ckpt, r.kind, r.semantic_id, r.lang): (r.judge_label, r.kw_refusal) for r in gv[gv.model == m].itertuples()}
        lab2 = {(r.ckpt, r.kind, r.semantic_id, r.lang): r.judge2_label for r in gv[gv.model == m].itertuples()}
        ex = []
        for r in d.itertuples():
            kind = f"s4_{r.role}"
            row = {"input": s4[(r.semantic_id, r.lang, r.role)], "output": "refuse" if r.role == "harmful" else "comply"}
            for ck in ("orig", "edit"):
                g = gens.get((ck, kind, r.semantic_id, r.lang))
                jl, kw = lab.get((ck, kind, r.semantic_id, r.lang), ("NOT_JUDGED", None))
                row[f"predict_{ck}_response"] = g["response"] if g else ""
                row[f"predict_{ck}_judge_label"] = str(jl)
                j2 = lab2.get((ck, kind, r.semantic_id, r.lang))
                row[f"predict_{ck}_judge2_label"] = str(j2) if isinstance(j2, str) else "NOT_JUDGED"
                row[f"metadata_{ck}_marker_refusal"] = bool(kw) if kw is not None else None
                row[f"metadata_R1_{ck}"] = fnum(getattr(r, f"R1_{ck}"))
                row[f"metadata_R_seq_{ck}"] = fnum(getattr(r, f"R_seq_{ck}", np.nan))
            row |= {"metadata_model": m, "metadata_semantic_id": r.semantic_id, "metadata_lang": r.lang, "metadata_role": r.role,
                    "metadata_stratum": r.stratum, "metadata_half": r.half, "metadata_s_frozen_orig": fnum(r.s_frozen_orig),
                    "metadata_s_frozen_edit": fnum(r.s_frozen_edit), "metadata_s_frozen_orig_Uproj": fnum(r.s_frozen_orig_Uproj),
                    "metadata_p_rprior": fnum(getattr(r, "p_rprior", np.nan)), "metadata_KL1": fnum(r.KL1), "metadata_KL32": fnum(r.KL32),
                    "metadata_tok_len": int(r.tok_len)}
            ex.append(row)
        datasets.append({"dataset": f"S4_strongreject_pairs__{m}", "examples": ex})
    # utility items: one row per (task, language, semantic id) with the original and edited predictions per model
    s7 = {}
    for t in C.TASKS:
        for r in (json.loads(l) for l in (C.SPLITS / f"S7_{t}.jsonl").read_text().splitlines() if l.strip()):
            s7[(t, r["metadata_semantic_id"], r["metadata_lang"])] = r["input"]
    for m in MODELS:
        rows = {}
        for ck in ("orig", "edit"):
            p = C.RES / m / f"utility_{ck}.json"
            if not p.exists():
                continue
            for u in jload(p):
                rows.setdefault((u["task"], u["semantic_id"], u["lang"]), {})[ck] = u
        ex = []
        for (t, sid, lang), v in sorted(rows.items()):
            if set(v) != {"orig", "edit"}:
                continue
            o, e = v["orig"], v["edit"]
            ex.append({"input": s7[(t, sid, lang)], "output": str(o["gold"]),
                       "predict_orig_acc_choice": str(o["pred_acc"]), "predict_orig_acc_norm_choice": str(o["pred_acc_norm"]),
                       "predict_edit_acc_choice": str(e["pred_acc"]), "predict_edit_acc_norm_choice": str(e["pred_acc_norm"]),
                       "metadata_model": m, "metadata_task": t, "metadata_lang": lang, "metadata_semantic_id": sid,
                       "metadata_orig_acc": int(o["acc"]), "metadata_orig_acc_norm": int(o["acc_norm"]),
                       "metadata_edit_acc": int(e["acc"]), "metadata_edit_acc_norm": int(e["acc_norm"]),
                       "metadata_orig_ll": [round(float(x), 5) for x in o["ll"]], "metadata_edit_ll": [round(float(x), 5) for x in e["ll"]]})
        if ex:
            datasets.append({"dataset": f"S7_utility__{m}", "examples": ex})
    out = {"metadata": {"method_name": "C1 utility + mechanistic core (4 checkpoints x EN/SL)", "summary": S} | meta, "datasets": datasets}
    jdump(out, C.ROOT / "method_out.json", indent=None)
    print("method_out.json written", sum(len(d["examples"]) for d in datasets))


if __name__ == "__main__":
    main()

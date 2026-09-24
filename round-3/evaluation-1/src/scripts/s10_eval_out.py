"""eval_out.json (exp_eval_sol_out schema): metrics_agg = headline audit metrics; datasets = corrected_numbers records,
judge-sensitivity cells, claims registry, gap range rows."""
from __future__ import annotations

import json
import math

import pandas as pd

from lib import RES, WS, read_json, write_json


def num(x):
    if x is None or isinstance(x, bool):
        return None if x is None else float(x)
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def s(x) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return ""
    return str(x)


def meta(d: dict) -> dict:
    return {f"metadata_{k}": (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in d.items()}


def main():
    M = read_json(RES / "headline_metrics.json")
    metrics = {k: float(v) for k, v in M.items() if isinstance(v, (int, float, bool))}
    R = read_json(RES / "corrected_numbers.json")
    ex1 = []
    for r in R:
        e = {"input": f"[{r['section']}] {r['claim_text_draft']} | cell={s(r['cell'])} lang={s(r['language'])} judge={s(r['judge'])} | source={s(r['source_file'])}::{s(r['source_key'])}",
             "output": s(r["paste_text"]) or s(r["recomputed_value"]) or s(r["summary_value"]),
             "predict_draft": s(r["draft_value"]), "predict_recomputed": s(r["recomputed_value"]), "predict_artifact_summary": s(r["summary_value"]),
             **meta(dict(id=r["id"], status=r["status"], step=r["step"], n=r["n"], unit=r["unit"], method=r["method"], correction_note=r["correction_note"],
                         plan_expected=r["plan_expected"], ci_low=r["ci_low"], ci_high=r["ci_high"]))}
        e["eval_status_match"] = 1.0 if r["status"] == "RECOMPUTED_MATCH" else 0.0
        e["eval_status_mismatch"] = 1.0 if r["status"] in ("RECOMPUTED_MISMATCH", "MISDESCRIBED", "UNTRACEABLE") else 0.0
        if num(r["draft_value"]) is not None and num(r["recomputed_value"]) is not None:
            e["eval_abs_diff_vs_draft"] = abs(num(r["draft_value"]) - num(r["recomputed_value"]))
        if r["plan_match"] is not None:
            e["eval_plan_match"] = 1.0 if r["plan_match"] else 0.0
        ex1.append(e)
    J = pd.read_csv(RES / "judge_sensitivity.csv")
    ex2 = []
    for _, r in J.iterrows():
        if r.judge == "keyword":
            out = f"refused={r.p_refused:.3f} not_refused={r.p_not_refused:.3f} (n={r.n})"
        else:
            out = f"refused={r.p_refused:.3f} partial={r.p_partial:.3f} complied={r.p_complied:.3f} invalid={r.p_invalid:.3f} (n={r.n})"
        e = {"input": f"{r.artifact} {r.dataset} cell={r.cell} lang={r.lang} judge={r.judge} orig={bool(r.is_orig)}", "output": out,
             "predict_judge": r.judge, **meta(dict(artifact=r.artifact, dataset=r.dataset, cell=r.cell, lang=r.lang, is_orig=bool(r.is_orig),
                                                    random_subset=bool(r.random_subset), subset_note=s(r.subset_note), n_generated=int(r.n_generated)))}
        for c in ("p_refused", "p_partial", "p_complied", "p_invalid", "p_not_refused", "coverage", "n"):
            if c in r and num(r[c]) is not None:
                e[f"eval_{c}"] = num(r[c])
        for c in ("p_refused_wilson_lo", "p_refused_wilson_hi", "p_refused_cboot_lo", "p_refused_cboot_hi"):
            if num(r.get(c)) is not None:
                e[f"eval_{c}"] = num(r[c])
        ex2.append(e)
    C = pd.read_csv(RES / "claims_registry.csv")
    ex3 = []
    for _, r in C.iterrows():
        e = {"input": f"{r.claim} [{r.section}; judge used {r.judge_used}]", "output": f"{r.judge_flag}: {s(r.flag_reasons)}",
             "predict_draft": s(r.draft_value), "predict_recomputed": s(r.recomputed), "predict_alternatives": s(r.alternatives),
             **meta(dict(id=r.id, cell=r.cell, lang=r.lang, artifact=r.artifact, n=int(r.n)))}
        e["eval_judge_sensitive"] = 1.0 if r.judge_flag == "JUDGE_SENSITIVE" else 0.0
        if num(r.recomputed) is not None:
            e["eval_recomputed"] = num(r.recomputed)
        ex3.append(e)
    G = pd.read_csv(RES / "gap_range.csv")
    ex4 = []
    for _, r in G.dropna(subset=["gap"]).iterrows():
        e = {"input": f"{r.checkpoint} | {r.dataset} | judge={r.judge} | definition={r.definition}",
             "output": f"SL-EN gap {r.gap:+.3f}" + (f" [{r.ci_low:+.3f}, {r.ci_high:+.3f}]" if pd.notna(r.ci_low) else " (no CI)"),
             "predict_judge": r.judge, **meta(dict(checkpoint=r.checkpoint, dataset=r.dataset, judge=r.judge, definition=r.definition, paired=bool(r.paired), note=s(r.get("note"))))}
        for c in ("gap", "ci_low", "ci_high", "p_en", "p_sl", "n_en", "n_sl", "did", "mcnemar_p"):
            if num(r.get(c)) is not None:
                e[f"eval_{c}"] = num(r[c])
        ex4.append(e)
    out = {"metadata": {"evaluation_name": "evaluation_iter3_dir5: recheck every number and every judge",
                        "description": ("CPU-only audit of the iteration-2 draft against raw per-item files of seven artifacts (independent code path), plus a "
                                        "judge-sensitivity instrument (4-class labels per judge per edited cell, within-edit agreement, keyword miscalibration, "
                                        "SL-EN gap range across judges and definitions). No model loaded, no new generation, no API spend."),
                        "workspace": str(WS), "placebos": read_json(RES / "placebos.json").get("n_passed"),
                        "status_vocabulary": ["RECOMPUTED_MATCH", "RECOMPUTED_MISMATCH", "MISDESCRIBED", "NEW", "UNTRACEABLE", "SUMMARY_ONLY"]},
           "metrics_agg": metrics,
           "datasets": [{"dataset": "corrected_numbers", "examples": ex1}, {"dataset": "judge_sensitivity_cells", "examples": ex2},
                        {"dataset": "claims_registry", "examples": ex3}, {"dataset": "gemma_gap_range", "examples": ex4}]}
    write_json(WS / "eval_out.json", out)
    print({k: len(d["examples"]) for k, d in zip(["numbers", "cells", "claims", "gaps"], out["datasets"])}, (WS / "eval_out.json").stat().st_size)


if __name__ == "__main__":
    main()

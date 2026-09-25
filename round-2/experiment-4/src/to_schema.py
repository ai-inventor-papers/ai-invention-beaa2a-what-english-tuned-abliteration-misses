#!/usr/bin/env python3
"""Stage J: method_out.json in the exp_gen_sol_out schema.
One example per (item, lang) with input = prompt, output = reference expectation (refuse / comply), per-checkpoint
predict_<ckpt> = judged CLASS (or provisional label) and predict_<ckpt>_response / _unsafe / _official fields.
Datasets: RefusEU_S5, RefusEU_S5X_crosstrans, XSTest_S6. metadata = full analysis + costs + pins + deviations."""
from __future__ import annotations

import json
from pathlib import Path

from common import ALL_CKPTS, WS, read_jsonl


def rj(p: Path) -> list[dict]:
    return read_jsonl(p) if p.exists() else []


def main() -> None:
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    A = json.loads((WS / "results/analysis.json").read_text())
    gen, jd, jl, au, off = {}, {}, {}, {}, {}
    for ck in ALL_CKPTS:
        gen |= {(ck, r["item_key"]): r for r in rj(WS / "results/gen" / f"{ck}.jsonl")}
        jd |= {(ck, r["item_key"]): r for r in rj(WS / "results/judge" / f"{ck}.jsonl")}
        jl |= {(ck, r["item_key"]): r for r in rj(WS / "results/judge_local" / f"{ck}.jsonl")}  # later rows supersede
        au |= {(ck, r["item_key"]): r for r in rj(WS / "results/autoscore" / f"{ck}.jsonl")}
    off = {(r["ckpt"], r["item_key"]): r for r in rj(WS / "results/guard/official_labels.jsonl")}
    ds = {"S5": "NASK-PIB/RefusEU_S5_sample", "S5X": "RefusEU_S5X_crosstranslation_pairs", "S6": "XSTest_safe_S6_EN_SL"}
    out = {k: [] for k in ds}
    for it in frozen["items"]:
        ex = {"input": it["prompt"], "output": it["expected"],
              "metadata_item_key": it["item_key"], "metadata_set": it["set"], "metadata_lang": it["lang"],
              "metadata_semantic_id": it["semantic_id"], "metadata_cluster": it["cluster"],
              "metadata_category_inferred_low_confidence": it.get("category"),
              "metadata_xstest_type": it.get("xstest_type"), "metadata_translation_direction": it.get("direction")}
        for ck in ALL_CKPTS:
            g = gen.get((ck, it["item_key"]))
            if g is None:
                continue
            j = jl.get((ck, it["item_key"]), {})      # PRIMARY label source (full coverage substitute judge)
            jg = jd.get((ck, it["item_key"]), {})     # gpt-4.1 where it exists (716 core items)
            a = au.get((ck, it["item_key"]), {})
            o = off.get((ck, it["item_key"]), {})
            ex[f"predict_{ck}"] = str(j.get("cls") or "unjudged")
            ex[f"predict_{ck}_gpt41"] = str(jg.get("cls") or "not_labelled_budget_block")
            ex[f"predict_{ck}_judged_lang"] = str(j.get("judge_lang") or "")
            ex[f"predict_{ck}_glotlid_lang"] = str(a.get("lid_top") or "")
            ex[f"predict_{ck}_official_unsafe"] = "" if o.get("official_unsafe") is None else str(o["official_unsafe"]).lower()
            ex[f"predict_{ck}_keyword_refusal"] = str(bool(a.get("keyword_refusal_en") if it["lang"] == "en" else a.get("keyword_refusal_sl"))).lower()
            ex[f"predict_{ck}_glotlid_consistent"] = str(a.get("lang_consistent")).lower()
            ex[f"predict_{ck}_hit_max"] = str(g["hit_max"]).lower()
            ex[f"predict_{ck}_response"] = g["response_text"]
        out[it["set"]].append(ex)
    meta_extra = json.loads((WS / "results/run_metadata.json").read_text()) if (WS / "results/run_metadata.json").exists() else {}
    # Heavy sub-objects ship as their own files; inline only their headline numbers so every method_out variant stays small.
    V = meta_extra.pop("judge_validation_local_vs_gpt41", None) or {}
    G = meta_extra.pop("guard_official_summary", None) or {}
    meta_extra["pins"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("lfs_sha256", "local_sha256")}
                          for k, v in (meta_extra.get("pins") or {}).items()}
    meta_extra["judge_validation_local_vs_gpt41_digest"] = {
        "file": str(WS / "results/judge_validation.json"), "n_overlap": V.get("n_overlap"),
        "kappa_class_6way": {l: d.get("class_6way", {}).get("kappa") for l, d in (V.get("gpt41_vs_local") or {}).items()},
        "kappa_refused_vs_not": {l: d.get("refused_vs_not", {}).get("kappa") for l, d in (V.get("gpt41_vs_local") or {}).items()},
        "kappa_safety_line": {l: d.get("kappa") for l, d in (V.get("gpt41_vs_local_safety") or {}).items()},
        "rates_on_overlap": V.get("rates_on_overlap")}
    meta_extra["guard_official_summary_digest"] = {
        "file": str(WS / "results/guard/summary.json"), "label": G.get("label"),
        "guard_agreement_rate": G.get("guard_agreement_rate"), "adjudicator": G.get("adjudicator"),
        "label_sources": G.get("label_sources"), "asr_official": G.get("asr_official")}
    meta_extra["smoke"] = {m: {k: v for k, v in (d or {}).items() if k not in ("templates", "b3")}
                           for m, d in (meta_extra.get("smoke") or {}).items()}
    mo = {"metadata": {"method_name": "C1 BEHAVIOUR: bilingual (EN/SL) behavioural evaluation of 4 core checkpoints + community reference",
                       "predict_field_key": {
                           "predict_<ckpt>": "response CLASS under the PRIMARY label source (Qwen3-14B local substitute judge, "
                                             "frozen rubric, all 4,800 items)",
                           "predict_<ckpt>_gpt41": "response CLASS under gpt-4.1 where it labelled the item (716 core items "
                                                   "in a seeded-random subset) else not_labelled_budget_block",
                           "predict_<ckpt>_official_unsafe": "RefusEU official guard pipeline (Llama-Guard-3-8B + PolyGuard-Qwen); "
                                                             "blank = guard disagreement, unadjudicated",
                           "predict_<ckpt>_judged_lang": "the judge's LANG line (diagnostic; GlotLID is the reported measure)",
                           "predict_<ckpt>_glotlid_lang": "GlotLID top label for the whole response",
                           "predict_<ckpt>_keyword_refusal": "Heretic EN / iteration-1 SL keyword proxy",
                           "predict_<ckpt>_hit_max": "output hit the 256-token cap without EOS"},
                       # the full analysis object is shipped as its own file (results/analysis.json) and referenced by
                       # path; only the reported blocks are inlined, so mini/preview stay readable.
                       "analysis": {k: A[k] for k in ("meta", "headline", "c1_family", "s5x_cross_language", "sanity",
                                                      "community_ref_vs_gemma_orig", "model_difference_descriptive",
                                                      "judge_unsafe_line_diagnostic", "lang_line_vs_glotlid_sl",
                                                      "official_vs_judge_asr", "keyword_proxy_validity") if k in A},
                       "analysis_full_path": str(WS / "results/analysis.json"),
                       "analysis_secondary_paired_path": str(WS / "results/analysis.json") + " -> secondary_paired",
                       "analysis_per_category_path": str(WS / "results/analysis.json") + " -> per_category_descriptive",
                       } | meta_extra,
          "datasets": [{"dataset": ds[k], "examples": v} for k, v in out.items() if v]}
    (WS / "method_out.json").write_text(json.dumps(mo, ensure_ascii=False, indent=1))
    print({k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()

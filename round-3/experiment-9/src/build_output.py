#!/usr/bin/env python3
"""method_out.json in the exp_gen_sol_out schema: one dataset block per evidence family. Each example keeps its input
(prompt or descriptor), its output (the frozen expectation) and metadata_*/predict_* fields, so every reported number is
recomputable from this file alone."""
from __future__ import annotations

import numpy as np
import pandas as pd

import alib as A
import common as C


def js(v) -> str:
    """Join a CI-style list, tolerating None (a quantity that was not measured in that pass)."""
    return "NA" if v is None else ",".join(map(s, v))


def s(x) -> str:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "NA"
    if isinstance(x, (bool, np.bool_)):
        return "true" if x else "false"
    if isinstance(x, float):
        return f"{x:.6g}"
    return str(x)


def main() -> None:
    S = C.jload(C.RES / "analysis_summary.json")
    T = pd.read_parquet(C.RES / "cells.parquet")
    red = C.jload(C.RES / "redundancy_index.json")
    fp = C.jload(C.RES / "frozen_predictions.json")
    dev = C.jload(C.RES / "deviations.json")
    per = pd.read_parquet(C.RES / "per_item.parquet")
    DS = []

    # ---- 1. per-cell rows
    ex = []
    for _, r in T.iterrows():
        md = {f"metadata_{k}": s(r[k]) for k in ("family", "stage", "E", "n_layers", "k_eff", "span", "mean_depth", "coverage",
                                                 "c", "group", "side", "anchor", "b1", "flores_en", "flores_sl", "kl_en", "kl_sl",
                                                 "matched") if k in r}
        for k in r.index:
            if k.startswith(("en_", "sl_")):
                md[f"metadata_{k}"] = s(r[k])
        m = C.jload(C.CELLS / f"{r['cell']}.json")
        if "c_profile" in m:
            md["metadata_c_profile"] = ";".join(f"{a:.4g}|{b:.4g}" for a, b in m["c_profile"])
        ex.append({"input": f"cell {r['cell']}: {r['family']} edit, coverage {r['coverage']}, c {s(r['c'])}, "
                            f"k_eff {s(r['k_eff'])}, energy {s(r['E'])}",
                   "output": s(r["sl_harm_refused"]), "predict_sl_harmful_refusal": s(r["sl_harm_refused"]),
                   "predict_en_harmful_refusal": s(r["en_harm_refused"]), "metadata_cell": r["cell"]} | md)
    DS.append({"dataset": "cells_panel", "examples": ex})

    # ---- 2. per-item generations and labels
    ex = []
    for _, r in per.iterrows():
        ex.append({"input": f"{r['cell']}|{r['lang']}|{r['uid']}", "output": s(r["cls4"]),
                   "predict_judged_class": s(r["cls4"]), "predict_refused": s(r["cls4"] == "REFUSED"),
                   "metadata_cell": r["cell"], "metadata_lang": r["lang"], "metadata_semantic_id": r["semantic_id"],
                   "metadata_role": s(r["role"]), "metadata_stratum": s(r["stratum"]), "metadata_kind": s(r["kind"]),
                   "metadata_unsafe_rubric": s(r["unsafe"]), "metadata_judge_lang": s(r["judge_lang"]),
                   "metadata_lid_ok": s(r.get("lid_ok")), "metadata_rep3": s(r["rep3"]), "metadata_hit_max": s(r["hit_max"]),
                   "metadata_n_tokens": s(r["n_tokens"]), "metadata_keyword_refused": s(r["keyword_refused"])})
    DS.append({"dataset": "per_item_labels", "examples": ex})

    # ---- 3. Part A index
    ex = []
    for g in C.LANGS:
        for fam in ("prefix", "suffix"):
            r = red["index"][g][fam]
            ex.append({"input": f"DEV depth-redundancy index, {fam} family, {g}", "output": s(r["index"]),
                       "predict_index": s(r["index"]), "metadata_lang": g, "metadata_family": fam,
                       "metadata_k_grid": ",".join(map(str, r["k"])), "metadata_curve": ",".join(f"{x:.4f}" for x in r["curve"]),
                       "metadata_index_ci95": ",".join(map(s, r["index_boot_ci"])), "metadata_censored": s(r["censored"]),
                       "metadata_auc": s(r["auc"])})
        for b, v in red["index"][g]["lobo"].items():
            ex.append({"input": f"leave-one-band-out necessity, band {b}, {g}", "output": s(v["necessity"]),
                       "predict_necessity": s(v["necessity"]), "metadata_lang": g, "metadata_band": b,
                       "metadata_rate": s(v["rate"]), "metadata_all48_rate": s(red["index"][g]["all48_rate"])})
    DS.append({"dataset": "part_a_redundancy_index", "examples": ex})

    # ---- 4. frozen tests and verdicts
    ex = []
    P1 = S["P1"]
    ex.append({"input": fp["P1_PRIMARY"]["statement"], "output": "PASS" if P1["pass_P1"] else "FAIL",
               "predict_dR2": s(P1["dR2"]), "metadata_test": "P1", "metadata_n_cells": s(P1["n_cells"]),
               "metadata_r2_base": s(P1["r2_base"]), "metadata_r2_full": s(P1["r2_full"]),
               "metadata_dR2_ci95": js(P1["dR2_ci95"]), "metadata_dR2_loo": s(P1["dR2_loo"]),
               "metadata_partial_F": s(P1["partial_F"]), "metadata_p_F": s(P1["p_F"]),
               "metadata_r2_logE_only": s(P1["r2_logE_only"]), "metadata_mde_dR2": s(P1["mde_dR2_80pct_power"]),
               "metadata_placebo_p95": s(P1["placebo_permuted_targets"]["p95"]),
               "metadata_falsifier_fired": s(P1["falsifier_dR2_lt_0.05"])})
    for key, tag in (("P2_screen", "P2 (screen)"), ("P2_confirm_hoc", "P2 (confirmation, hoc)"),
                     ("P2_confirm_ind", "P2 (confirmation, ind)")):
        P2 = S.get(key) or {}
        if not P2.get("pooled"):
            continue
        p = P2["pooled"]
        ex.append({"input": f"{tag}: {fp['P2_PRIMARY']['statement']}", "output": "PASS" if P2["pass_P2"] else "FAIL",
                   "predict_contrast_SL": s(p["contrast_SL"]), "metadata_test": key, "metadata_n_groups": s(p["n_groups"]),
                   "metadata_contrast_SL_ci95": js(p["contrast_SL_ci95"]),
                   "metadata_contrast_EN": s(p["contrast_EN"]), "metadata_SL_minus_random": s(p["SL_minus_random"]),
                   "metadata_SL_minus_random_ci95": js(p["SL_minus_random_ci95"]),
                   "metadata_SL_minus_pc": s(p["SL_minus_pc"]), "metadata_did": s(p["did_SL_minus_EN"]),
                   "metadata_did_ci95": js(p["did_ci95"]), "metadata_confirmatory": s(P2["confirmatory"]),
                   "metadata_placebo_swap_ci95": js(P2["placebo_swap_within_item"]["ci95"]),
                   "metadata_placebo_lang_ci95": js(P2["placebo_permute_language"]["ci95"])})
    for key, tag in (("P3_screen", "P3 (screen)"), ("P3_confirm_hoc", "P3 (confirmation, hoc)")):
        P3 = S.get(key) or {}
        if not P3:
            continue
        ex.append({"input": f"{tag}: {fp['P3']['statement']}", "output": "PASS" if P3["pass_P3"] else "FAIL",
                   "predict_spearman_sl": s(P3["sl"]["spearman"]), "predict_spearman_en": s(P3["en"]["spearman"]),
                   "metadata_test": key, "metadata_sl_ci95": js(P3["sl"]["spearman_ci95"]),
                   "metadata_en_ci95": js(P3["en"]["spearman_ci95"]), "metadata_n_cells": s(P3["sl"]["n_cells"]),
                   "metadata_sl_mae": s(P3["sl"]["mae"]), "metadata_en_mae": s(P3["en"]["mae"]),
                   "metadata_sl_threshold": s(P3["sl"]["threshold"]), "metadata_en_threshold": s(P3["en"]["threshold"])})
    ex.append({"input": fp["C2_PREREGISTERED"], "output": s((S.get("C2_index_SL_gt_EN") or {}).get("prefix")),
               "metadata_test": "C2", "metadata_both_families": s(S.get("C2_index_SL_gt_EN")),
               "metadata_index_en": s(red["index"]["en"]["prefix"]["index"]), "metadata_index_sl": s(red["index"]["sl"]["prefix"]["index"])})
    ex.append({"input": fp["FALSIFIER"], "output": s(P1["falsifier_dR2_lt_0.05"]), "metadata_test": "FALSIFIER",
               "metadata_holm": s(S["holm"]["adjusted"])})
    DS.append({"dataset": "frozen_tests", "examples": ex})

    # ---- 5. confirmation + utility + collateral
    conf = S.get("confirmation") or {}
    ex = []
    for c, r in (conf.get("cells") or {}).items():
        md = {"metadata_cell": c, "metadata_flores_sl": s(r["flores_dNLL"]["sl"]), "metadata_flores_en": s(r["flores_dNLL"]["en"]),
              "metadata_kl_sl": s(r["kl_dolly"]["sl"])}
        for k, v in r.items():
            if isinstance(v, dict) and "rate" in v:
                md[f"metadata_{k}_rate"] = s(v["rate"])
                md[f"metadata_{k}_change"] = s(v["change"])
                md[f"metadata_{k}_ci95"] = js(v["change_ci95"])
                md[f"metadata_{k}_mcnemar_p"] = s(v["mcnemar_p"])
            elif isinstance(v, dict) and "macro" in v:
                md[f"metadata_{k}_macro"] = s(v["macro"])
                md[f"metadata_{k}_macro_change"] = s(v["macro_change"])
                md[f"metadata_{k}_macro_ci95"] = js(v["macro_change_ci95"])
                md[f"metadata_{k}_per_task"] = ";".join(f"{t}={x:.4f}" for t, x in v["per_task"].items())
            elif not isinstance(v, dict):
                md[f"metadata_{k}"] = s(v)
        ex.append({"input": f"confirmation cell {c} on S4 hoc/ind + S6 + S7", "output": s((r.get("hoc_sl_harm") or {}).get("rate")),
                   "predict_hoc_sl_refusal": s((r.get("hoc_sl_harm") or {}).get("rate")),
                   "predict_hoc_en_refusal": s((r.get("hoc_en_harm") or {}).get("rate"))} | md)
    if ex:
        DS.append({"dataset": "confirmation", "examples": ex})

    # ---- 6. instrument checks, write mass, deviations, audit
    ex = []
    jc = S.get("judge_certification") or {}
    ex.append({"input": "scorer certification: kappa refused-vs-not vs gpt-4.1 within EDITED checkpoints",
               "output": s(jc.get("kappa_this_run_edited") if jc.get("kappa_this_run_edited") is not None else jc.get("kappa_on_disk_edited")),
               "metadata_check": "judge_certification", "metadata_kappa_on_disk": s(jc.get("kappa_on_disk_edited")),
               "metadata_kappa_this_run": s(jc.get("kappa_this_run_edited")), "metadata_pass_on_disk": s(jc.get("pass_on_disk")),
               "metadata_pass_this_run": s(jc.get("pass_this_run"))})
    kc = S.get("keyword_check") or {}
    ex.append({"input": "keyword proxy vs judge on edited cells (must NOT agree strongly)",
               "output": s(kc.get("kappa_judge_vs_keyword_edited")), "metadata_check": "keyword_proxy",
               "metadata_false_positive_share": s(kc.get("keyword_false_positive_share")),
               "metadata_red_flag": s(kc.get("red_flag_kappa_gt_0.6"))})
    r8 = S.get("exp8_rescore") or {}
    if r8.get("n"):
        ex.append({"input": "Gate 3: our scorer on exp8's SAVED generations", "output": s(r8.get("kappa_refused_vs_not_vs_gpt41_exp8")),
                   "metadata_check": "exp8_rescore", "metadata_n": s(r8["n"]),
                   "metadata_kappa_vs_qwen_exp8": s(r8.get("kappa_refused_vs_not_vs_qwen_exp8")),
                   "metadata_per_arm": s(r8.get("per_arm_refusal"))})
    g2 = C.jload(C.RES / "gate2_anchor_check.json") if (C.RES / "gate2_anchor_check.json").exists() else {}
    if g2:
        ex.append({"input": "Gate 2: anchor reproduction of exp8 cells", "output": s(g2.get("pass")),
                   "metadata_check": "gate2", "metadata_criterion": g2.get("criterion", "")[:400],
                   "metadata_cells": s(g2.get("cells")), "metadata_pass_secondary": s(g2.get("pass_secondary_single_judge"))})
    g1 = C.jload(C.RES / "gate1_unit_tests.json")
    ex.append({"input": "Gate 1: operator unit tests (projection removal, closed-form energy, site isolation)",
               "output": s(g1["pass"]), "metadata_check": "gate1", "metadata_values": s(g1)})
    wm = S.get("write_mass_exploratory") or {}
    for g in C.LANGS:
        if g in wm:
            ex.append({"input": f"EXPLORATORY per-layer write mass along d_EN(h), {g}", "output": s(wm[g]["n_layers_80pct_mass"]),
                       "metadata_check": "write_mass", "metadata_lang": g, "metadata_entropy": s(wm[g]["entropy_nats"]),
                       "metadata_band_mass": js(wm[g]["band_mass"]),
                       "metadata_spearman_vs_lobo": s(wm[g].get("spearman_band_mass_vs_lobo_necessity")),
                       "metadata_profile": ",".join(f"{x:.5f}" for x in wm[g]["profile"])})
    apos = C.jload(C.RES / "audit_positive.json") if (C.RES / "audit_positive.json").exists() else {}
    if apos:
        for lg in C.LANGS:
            r = apos["A_P3_spearman_placebo"][lg]
            ex.append({"input": f"placebo audit: P3 Spearman with predictions permuted across cells, {lg}",
                       "output": s(r["observed_outside_null"]), "predict_spearman": s(r["observed_spearman"]),
                       "metadata_check": "placebo_P3", "metadata_lang": lg,
                       "metadata_placebo_null_ci95": js(r["placebo_null_ci95"]), "metadata_placebo_mean": s(r["placebo_mean"]),
                       "metadata_matches_analysis": s(r["matches_reported"])})
        b = apos["B_index_gap_language_placebo"]
        ex.append({"input": "placebo audit: index_SL - index_EN with the language label permuted within item",
                   "output": s(b["observed_gap_outside_null"]), "predict_index_gap": s(b["observed_gap"]),
                   "metadata_check": "placebo_index_gap", "metadata_placebo_null_ci95": js(b["placebo_null_ci95"]),
                   "metadata_straddles_zero": s(b["placebo_straddles_zero"]), "metadata_note": b["note"]})
        b2 = apos["B2_curve_separation"]
        ex.append({"input": "placebo audit: prefix-curve separation SL-EN (the powered statistic for C2)",
                   "output": s(b2["observed_outside_null"]), "predict_separation": s(b2["observed"]),
                   "metadata_check": "curve_separation", "metadata_ci95": js(b2["bootstrap_ci95"]),
                   "metadata_placebo_null_ci95": js(b2["placebo_null_ci95"]),
                   "metadata_permutation_p": s(b2["permutation_p_two_sided"]), "metadata_reading": b2["reading"]})
        c_ = apos["C_band_identity_placebo"]
        ex.append({"input": "placebo audit: band-density separation with the band label permuted across coverage sets",
                   "output": s(c_["observed_outside_null"]), "predict_separation": s(c_["observed_separation"]),
                   "metadata_check": "placebo_band_identity", "metadata_permutation_p": s(c_["permutation_p"]),
                   "metadata_placebo_null_ci95": js(c_["placebo_null_ci95"]),
                   "metadata_spearman_density_vs_minSL": s(c_["spearman_band_density_vs_min_SL"]),
                   "metadata_min_SL_by_band_density": s(c_["min_SL_by_band_density"]),
                   "metadata_all_full_band_sets_below_half": s(c_["every_reaching_set_below_0.5"]),
                   "metadata_no_partial_band_set_below_half": s(c_["every_non_reaching_set_above_0.5"])})
    aud = C.jload(C.RES / "audit.json") if (C.RES / "audit.json").exists() else {}
    if aud:
        ex.append({"input": "Gate 6: independent re-derivation (rederive.py) of every headline number + placebos",
                   "output": f"{aud['n_match']}/{aud['n_checks']}", "metadata_check": "rederive",
                   "metadata_all_match": s(aud["all_match"]),
                   "metadata_placebos": s([c for c in aud["checks"] if c["name"].startswith("placebo")])})
    for d in dev["deviations"]:
        ex.append({"input": f"DEVIATION: {d['deviation']}", "output": d["cost"], "metadata_check": "deviation",
                   "metadata_reason": d["reason"], "metadata_evidence": d["evidence"]})
    DS.append({"dataset": "checks_and_deviations", "examples": ex})

    out = {"metadata": {
        "method_name": "depth-coverage x strength factorial on Heretic-family weight edits, with a DEV depth-redundancy index",
        "model": f"{C.MODEL['repo']}@{C.MODEL['sha']}", "quantisation": "bnb NF4, bf16 compute, greedy decoding",
        "scorer": "local Qwen/Qwen3-14B@40c06982 NF4, frozen exp4 protocol.yaml rubric, 4-way partial-aware, blind",
        "workspace": str(C.ROOT), "n_cells": int(T["cell"].nunique()), "n_generations": int(len(per)),
        "frozen_predictions_sha256": C.file_sha256(C.RES / "frozen_predictions.json"),
        "redundancy_index_sha256": C.file_sha256(C.RES / "redundancy_index.json"),
        "verdicts": {"P1": bool(S["P1"]["pass_P1"]), "P2_screen": bool((S.get("P2_screen") or {}).get("pass_P2")),
                     "P3_screen": bool((S.get("P3_screen") or {}).get("pass_P3")),
                     "P2_confirm_hoc": bool((S.get("P2_confirm_hoc") or {}).get("pass_P2")),
                     "P3_confirm_hoc": bool((S.get("P3_confirm_hoc") or {}).get("pass_P3")),
                     "C2": bool((S.get("C2_index_SL_gt_EN") or {}).get("prefix")),
                     "falsifier_fired": bool(S["P1"]["falsifier_dR2_lt_0.05"])},
        "index": {g: red["index"][g]["prefix"]["index"] for g in C.LANGS},
        "kept_artifacts": {"cells": str(C.RES / "cells.parquet"), "per_item": str(C.RES / "per_item.parquet"),
                           "generations": str(C.GENS), "judge_cache": str(C.RES / "judge_local.jsonl"),
                           "report": str(C.RES / "report_tables.md"), "figures": str(C.FIGS)}},
        "datasets": DS}
    C.jdump(out, C.ROOT / "method_out.json", indent=1)
    print(f"method_out.json: {len(DS)} blocks, " + ", ".join(f"{d['dataset']}={len(d['examples'])}" for d in DS))


if __name__ == "__main__":
    main()

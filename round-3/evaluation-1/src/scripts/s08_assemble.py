"""S10 packaging: corrected_numbers.json, audit_log.json, judge_sensitivity.md, report_repairs.md, headline metrics."""
from __future__ import annotations

import collections
import json

import numpy as np
import pandas as pd

from lib import DRAFT, E1, E3, E4, E5, E6, E7, E8, RES, fmt, read_json, setup, write_json

STATUSES = ["RECOMPUTED_MATCH", "RECOMPUTED_MISMATCH", "MISDESCRIBED", "NEW", "UNTRACEABLE", "SUMMARY_ONLY"]


def records() -> list[dict]:
    out = []
    for f in sorted((RES / "records").glob("*.json")):
        out += read_json(f)
    return out


def src(p) -> str:
    return f"[source: {p}]"


def md_table(df: pd.DataFrame, cols: list[str], nd=3) -> list[str]:
    L = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        L.append("| " + " | ".join(fmt(r[c], nd) if isinstance(r[c], float) else str(r[c]) for c in cols) + " |")
    return L


def headline_metrics(R, A, G, K, P, C) -> dict:
    draft_recs = [r for r in R if r["draft_value"] is not None or r["status"] in ("RECOMPUTED_MISMATCH", "MISDESCRIBED", "UNTRACEABLE")]
    cnt = collections.Counter(r["status"] for r in draft_recs)
    q = A[(A.artifact == "exp4") & (A.judge_a == "gpt41") & (A.judge_b == "qwen3_14b") & (A.definition == "binary")]
    k_all = float(q[q.scope == "pooled_all"].kappa.iloc[0])
    k_ed = float(q[q.scope == "pooled_edited"].kappa.iloc[0])
    ac1 = float(q[q.scope == "pooled_edited"].ac1.iloc[0])
    gg = G[(G.checkpoint == "gemma_edit") & (G.judge != "keyword") & (G.n_en.fillna(0) >= 30) & G.gap.notna()]
    s = gg[gg.definition == "strict"]
    b = gg[gg.definition == "broad"]
    ci_s = s.dropna(subset=["ci_low"])
    sign_stable = bool(((ci_s.ci_low > 0).all() or (ci_s.ci_high < 0).all()))
    kf = K[(K.artifact == "exp4") & (K.cell == "gemma_edit") & (K.lang == "en") & K.harmful & (K.judge == "qwen3_14b")].fp_share.iloc[0]
    return dict(n_claims_checked=len(draft_recs), n_match=cnt["RECOMPUTED_MATCH"], n_mismatch=cnt["RECOMPUTED_MISMATCH"],
                n_untraceable=cnt["UNTRACEABLE"], n_misdescribed=cnt["MISDESCRIBED"],
                mismatch_rate=cnt["RECOMPUTED_MISMATCH"] / max(1, cnt["RECOMPUTED_MATCH"] + cnt["RECOMPUTED_MISMATCH"]),
                n_sign_reversed_conclusions=2, n_records_total=len(R), n_new_numbers=sum(r["status"] == "NEW" for r in R),
                n_summary_only=sum(r["status"] == "SUMMARY_ONLY" for r in R),
                n_plan_expected_mismatch=sum(r["plan_match"] is False for r in R),
                n_judge_sensitive_claims=int((C.judge_flag == "JUDGE_SENSITIVE").sum()), n_judge_robust_claims=int((C.judge_flag == "JUDGE_ROBUST").sum()),
                n_single_judge_claims=int((C.judge_flag == "SINGLE_JUDGE").sum()),
                kappa_binary_pooled_all_qwen_gpt41=k_all, kappa_binary_edited_only_qwen_gpt41=k_ed, kappa_inflation=k_all - k_ed, ac1_edited_only=ac1,
                gemma_gap_strict_min=float(s.gap.min()), gemma_gap_strict_max=float(s.gap.max()),
                gemma_gap_broad_min=float(b.gap.min()), gemma_gap_broad_max=float(b.gap.max()), gemma_gap_sign_stable=int(sign_stable),
                gemma_gap_s5x_strict_qwen=float(G[(G.checkpoint == "gemma_edit") & G.dataset.str.startswith("exp4 S5X") & (G.judge == "qwen3_14b") & (G.definition == "strict")].gap.iloc[0]),
                gemma_gap_s5x_broad_qwen=float(G[(G.checkpoint == "gemma_edit") & G.dataset.str.startswith("exp4 S5X") & (G.judge == "qwen3_14b") & (G.definition == "broad")].gap.iloc[0]),
                keyword_fp_share_gemma_edit_en=float(kf), placebos_passed=int(P["n_passed"]), api_spend_usd=0.0)


def main():
    setup("s08_assemble")
    R = records()
    A = pd.read_csv(RES / "judge_agreement.csv")
    G = pd.read_csv(RES / "gap_range.csv")
    K = pd.read_csv(RES / "keyword_miscalibration.csv")
    C = pd.read_csv(RES / "claims_registry.csv")
    J = pd.read_csv(RES / "judge_sensitivity.csv")
    P = read_json(RES / "placebos.json")
    S = pd.read_csv(RES / "gap_range_summary.csv")
    M = headline_metrics(R, A, G, K, P, C)
    write_json(RES / "headline_metrics.json", M)
    # ---------------- corrected_numbers.json
    write_json(RES / "corrected_numbers.json", R)
    # ---------------- audit_log.json
    cnt = collections.Counter(r["status"] for r in R)
    write_json(RES / "audit_log.json", {
        "counts_by_status_all_records": {s: cnt.get(s, 0) for s in STATUSES},
        "headline_metrics": M,
        "mismatches_vs_draft": [dict(id=r["id"], claim=r["claim_text_draft"], draft=r["draft_value"], recomputed=r["recomputed_value"], status=r["status"],
                                     note=r["correction_note"], source=r["source_file"]) for r in R if r["status"] in ("RECOMPUTED_MISMATCH", "MISDESCRIBED", "UNTRACEABLE")],
        "mismatches_vs_plan_expected": [dict(id=r["id"], plan_expected=r["plan_expected"], recomputed=r["recomputed_value"], summary=r["summary_value"],
                                             note=r["correction_note"]) for r in R if r["plan_match"] is False] + [
            dict(id="iter1_eff_ratio_of_medians_CI", plan_expected="CI [7.0, 30.0]; draft CI [6.9, 30.4] 'wrong or unsourced'",
                 recomputed="artifact efficiency.json CI [6.93, 30.43]", note="the draft's CI is the artifact CI rounded; the plan's claim that it is wrong is itself wrong"),
            dict(id="translation_S1", plan_expected="S1 SL = NLLB-200-distilled-1.3B, chrF 70.3",
                 recomputed="S1 SL rows: 785 gemini-2.5-flash pod texts, 100 NLLB (exp1 harmful test[:100]), 98 gemini layout-B, 15 NLLB fallbacks, 2 gpt-4.1; mean BT chrF 79.7",
                 note="see pending_human_review.md translation table"),
            dict(id="exp3_gap_gemma", plan_expected="+0.77 [.62,.89] called 'gap'",
                 recomputed="level gap SL-EN after C1 = +0.78; DiD vs C0 = +0.61 [0.41, 0.78]", note="the plan mixes a level gap (Gemma) with a DiD (GaMS3 -0.15)")],
        "summary_leg_mismatches": [r["id"] for r in R if r["summary_match"] is False],
        "placebos": {k: v["passed"] for k, v in P.items() if k.startswith("P")},
        "recomputations": [dict(id=r["id"], inputs=r["source_file"], key=r["source_key"], function=r["method"], output=r["recomputed_value"],
                                status=r["status"]) for r in R],
        "independence": "all numbers recomputed by scripts/ in this workspace from raw per-item files; no prior artifact analysis/audit script was imported or executed",
        "api_spend_usd": 0.0, "optional_S2j_topup": ("ATTEMPTED, BLOCKED: 521 S5X items (gemma_edit 162, community_ref 200, gemma_orig 159; estimate $0.95) were sent with the frozen exp4 "
                               "gpt-4.1 prompt; every call returned HTTP 403 'aii_run_budget_exhausted' (per-run OpenRouter budget reached). 0 labels, $0 spent, "
                               "nothing invented (results/topup_gpt41_BLOCKED_no_labels.jsonl, results/topup_cost.json). Within-edit gpt-4.1 vs Qwen overlap "
                               "therefore stays small in exp4 (354 items; 4 S5X gemma_edit pairs with both members labelled, 0 community_ref).")})
    # ---------------- judge_sensitivity.md
    E = J[~J.is_orig].copy()
    E = E[E.dataset.isin(["S5", "S5X", "S6", "s4_harmful", "s4_harmless", "jbb_harm", "jbb_ben", "jbb_harmful", "jbb_harmless", "jbb_benign", "hoc_harmful", "hoc_harmless", "hb_test100"])]
    E["cov"] = E.coverage
    lines = ["# Judge-sensitivity table (edited cells; originals in judge_sensitivity.csv with is_orig=true)", "",
             "Canonical classes from `configs/label_map.yaml`. Keyword = uniform Heretic/iteration-1 marker rule (binary; its NOT_REFUSED is never split). "
             "`random` = whether the judged subset is a random draw (exp8 gpt-4.1 is arm-prioritised and exp5 gpt-4.1 is priority-ordered: NOT random). "
             "Wilson 95% CIs are in the CSV together with cluster-bootstrap CIs over semantic items.", ""]
    E = E.sort_values(["artifact", "cell", "dataset", "lang", "judge"])
    cols = ["artifact", "dataset", "cell", "lang", "judge", "n", "cov", "random_subset", "p_refused", "p_partial", "p_complied", "p_invalid", "p_not_refused"]
    for c in cols:
        if c not in E:
            E[c] = np.nan
    lines += md_table(E, cols)
    (RES / "judge_sensitivity.md").write_text("\n".join(lines) + "\n")
    # ---------------- report_repairs.md
    byid = {r["id"]: r for r in R}
    rv = lambda i, nd=3: fmt(byid[i]["recomputed_value"], nd) if isinstance(byid[i]["recomputed_value"], float) else str(byid[i]["recomputed_value"])
    t1 = pd.read_csv(RES / "iter1_behaviour_table_corrected.csv")
    sw = pd.read_csv(RES / "iter1_swap_stats.csv")
    out = ["# Report repairs: paste-ready corrected tables (iteration-3 audit)", "",
           f"Generated by `scripts/s08_assemble.py` from raw per-item files. Draft audited: `{DRAFT}`. Status vocabulary: RECOMPUTED_MATCH, RECOMPUTED_MISMATCH, "
           "MISDESCRIBED, NEW, UNTRACEABLE, SUMMARY_ONLY (full list: `results/corrected_numbers.json`).", "",
           f"**Audit headline.** {M['n_claims_checked']} draft numbers checked: {M['n_match']} match, {M['n_mismatch']} mismatch, {M['n_misdescribed']} misdescribed, "
           f"{M['n_untraceable']} untraceable (mismatch rate {M['mismatch_rate']:.3f}); 2 sign-reversed conclusions (iteration-1 swap; exp7 P-a direction). "
           f"{M['n_judge_sensitive_claims']} of {len(C)} behavioural claims are JUDGE_SENSITIVE. Placebos passed: {M['placebos_passed']}/6.", "",
           "## (1) Iteration-1 six-checkpoint table and the swap conclusion", "",
           "Keyword refusals /100 (EN: Heretic 3521f864 markers; SL: iteration-1 markers), mean KL, FLORES+ NLL (40 sentences). "
           + src(E1 / "results/eval/{gams,gemma}_{orig,own,swap}.json"), ""]
    out += md_table(t1, list(t1.columns))
    out += ["", "Paired swap statistics on the same 100 prompts (exact McNemar; paired bootstrap B=2000, seed 20260924) " + src(RES / "iter1_swap_stats.csv"), ""]
    sw2 = sw.copy()
    sw2["CI"] = [f"[{a:+.2f}, {b:+.2f}]" for a, b in zip(sw2.ci_low, sw2.ci_high)]
    sw2["p"] = [f"{p:.2e}" for p in sw2.p_exact]
    out += md_table(sw2, ["model", "lang", "a", "b", "count_a", "count_b", "diff_b_minus_a", "CI", "p"], 2)
    out += ["", f"KL(own)/KL(swap), Gemma: {rv('iter1_gemma_kl_ratio_own_swap')} [{fmt(byid['iter1_gemma_kl_ratio_own_swap']['ci_low'])}, "
            f"{fmt(byid['iter1_gemma_kl_ratio_own_swap']['ci_high'])}] (ratio of mean per-prompt KL, 100 prompts).", "",
            "**Corrected conclusion (paste):** GaMS3's trial-88 parameters suppress Gemma's SLOVENE refusal far more than its English (SL 97->25 vs EN 100->53) "
            "at ~10x the KL of Gemma's own edit (KL 0.254 vs 0.024). This SUPPORTS the depth/dose reading (a stronger edit of the same base largely transfers); "
            "it does not prove it. The draft's '91/95 at KL 0.293' exists in no file; its Gemma FLORES values (3.930/3.427 ...) are UNTRACEABLE in iteration-1 files.", "",
            "## (2) The '13.4x' and the KL-matched subset", "",
            f"- 13.4x is the ratio of MEDIANS of refusal drop per unit KL over the 60 shared startup edits, GaMS3 {rv('iter1_eff_median_gams', 0)} vs Gemma "
            f"{rv('iter1_eff_median_gemma', 0)} refusals/nat; ratio {rv('iter1_eff_ratio_of_medians', 2)}, artifact CI [6.93, 30.43] (our re-bootstrap, seed 20260924: "
            f"[{fmt(byid['iter1_eff_ratio_of_medians']['ci_low'], 2)}, {fmt(byid['iter1_eff_ratio_of_medians']['ci_high'], 2)}]). It is NOT a ratio of median refusal counts. "
            + src(E1 / "results/efficiency.json"),
            f"- KL-matched subset (n={rv('iter1_klmatched_n')}): GaMS3 median {rv('iter1_klmatched_gams_med', 0)}/100 vs Gemma {rv('iter1_klmatched_gemma_med', 0)}/100 "
            f"refusals at KL medians {rv('iter1_klmatched_kl_gams', 4)}/{rv('iter1_klmatched_kl_gemma', 4)}.",
            f"- Same-edit dominance {rv('iter1_dominance')}/60; median paired difference +{rv('iter1_paired_median_diff', 0)} [10, 43]; KL Spearman {rv('iter1_a3_rho_kl', 3)}.", "",
            "## (3) Iteration-1 restorations (A3 verdict, A1 screen)", "",
            f"- A3 frozen reading: **'intermediate'** (not 'shared via strength only', which needs raw rho >= 0.9); rho_refusal {rv('iter1_a3_rho_ref', 3)} [0.63, 0.88]. "
            + src(E1 / "results/a3_screen.json"),
            "- SL marker validation (acc .75, kappa .48) was against the EXECUTOR's hand labels (n=40, not native), not LLM-judge labels.",
            "- Exp3 judge: gpt-4.1 labelled all 1,596 outputs; there is no Qwen second judge (MISDESCRIBED in the draft). Gemma EN baseline is .83, not '99%'.", ""]
    e3 = pd.read_csv(RES / "exp3_judged_rates.csv")
    e3 = e3[e3.condition.isin(["C0", "C1", "C2"])].pivot_table(index=["model", "condition"], columns="lang", values="mean").reset_index()
    out += ["Exp3 judged refusal (gpt-4.1, JBB harmful half-B; C0 no-op, C1 d_EN ablation, C2 d_SL ablation) " + src(E3 / "results/judged_generations.json"), ""]
    out += md_table(e3, ["model", "condition", "en", "sl"], 2)
    out += ["", f"DiD (SL drop smaller than EN drop) under d_EN: GaMS3 {rv('exp3_gap_gams3', 3)} [{fmt(byid['exp3_gap_gams3']['ci_low'], 2)}, {fmt(byid['exp3_gap_gams3']['ci_high'], 2)}]; "
            f"Gemma {rv('exp3_gap_gemma', 3)} [{fmt(byid['exp3_gap_gemma']['ci_low'], 2)}, {fmt(byid['exp3_gap_gemma']['ci_high'], 2)}]; Gemma post-ablation level gap SL-EN {rv('exp3_levelgap_gemma', 2)}.",
            f"Summary-only (read by key): margin decomposition Gemma SL R0 {fmt(byid['exp3_margin_sl']['summary_value'], 1)} vs EN {fmt(byid['exp3_margin_en']['summary_value'], 1)}; "
            f"benign SL twins refused {fmt(byid['exp3_benign_sl_twins']['summary_value'], 3)}; Heretic bridge mean gap GaMS3 {fmt(byid['exp3_bridge_gams3']['summary_value'], 3)} "
            f"[{fmt(byid['exp3_bridge_gams3']['ci_low'], 2)}, {fmt(byid['exp3_bridge_gams3']['ci_high'], 2)}], Gemma {fmt(byid['exp3_bridge_gemma']['summary_value'], 3)} "
            f"[{fmt(byid['exp3_bridge_gemma']['ci_low'], 2)}, {fmt(byid['exp3_bridge_gemma']['ci_high'], 2)}]; "
            f"R-gate GaMS3 Spearman {fmt(byid['exp3_rgate_gams_sp']['summary_value'], 2)} / AUROC {fmt(byid['exp3_rgate_gams_auc']['summary_value'], 2)} (FAILS); "
            f"T(en->sl) {fmt(byid['exp3_T']['summary_value'], 2)}.", "",
            "## (4) Experiment 7 frozen predictions (verbatim)", ""]
    fp = read_json(RES / "exp7_frozen_predictions_verbatim.json")
    for k, v in fp["predictions"].items():
        vv = fp["verdicts"][k]
        out.append(f"- **{k}** (frozen): \"{v}\" -> {vv.get('verdict')}"
                   + (f"; observed {vv.get('Gap_R', vv.get('Gap_Rb', vv.get('Gap_margin_matched'))):.3f} {[round(x, 3) for x in vv.get('ci95', vv.get('ci95_edit_boot', []))]}"
                      if any(x in vv for x in ('Gap_R', 'Gap_Rb', 'Gap_margin_matched')) else ""))
    out += ["", "P-a and P-d predicted LARGE gaps (>= 0.10) and failed because the gaps are SMALL; the draft inverts both. R1 beside R1: Gemma 0.054 [0.022, 0.128] vs "
            f"GaMS3 {fmt(byid['exp6_gap_R1_beside']['summary_value'])} [0.027, 0.070] (overlapping). Label-swap placebo: {fmt(byid['exp7_placebo_share']['summary_value'], 3)} of swaps >= observed. "
            f"Recomputed transfer slopes (OLS with intercept; through-origin in corrected_numbers): R1 {rv('exp7_slope_R1')}, R_seq {rv('exp7_slope_R_seq')}, "
            f"lp_ref {rv('exp7_slope_lp_ref')}, lp_comp {rv('exp7_slope_lp_comp')}. Reading: 'attenuated but predictable'. " + src(E7 / "protocol/frozen_predictions.json"), "",
            "## (5) Mechanism interpretations", "",
            "Not re-derived in this audit (outside S1-S8). Pointer only: T6/T7 values live in `iter_2/gen_art/gen_art_experiment_5/results/analysis/tables.md`. "
            f"Exp8 item-level cosine-transfer AUROC {fmt(byid['exp8_auroc_cos']['summary_value'], 3)} (the plan quotes 0.240; the file holds 0.244). "
            f"r_prior geometry: cos with language axis {fmt(byid['exp8_rprior_cos_lang']['summary_value'], 2)}, with shuffled twin {fmt(byid['exp8_rprior_cos_shuf']['summary_value'], 2)}.", "",
            "## (6) Experiment 4 (RefusEU) additions", "", "Headline table (exp4 `headline_table.csv`, pasted in full; judge = Qwen3-14B) " + src(E4 / "results/headline_table.csv"), ""]
    ht = pd.read_csv(E4 / "results/headline_table.csv")
    out += md_table(ht, list(ht.columns))
    O = pd.read_csv(RES / "exp4_official_asr.csv")
    out += ["", "Official RefusEU guard ASR on S5 (harmfulness judge; not a refusal label) " + src(E4 / "results/guard/official_labels.jsonl"), ""]
    out += md_table(O, ["cell", "lang", "n", "asr", "wilson_lo", "wilson_hi"])
    x = G[G.dataset.str.startswith("exp4 S5X")].copy()
    x["CI"] = [f"[{fmt(a, 2)}, {fmt(b, 2)}]" for a, b in zip(x.ci_low, x.ci_high)]
    x["p"] = [f"{p:.1e}" if pd.notna(p) else "–" for p in x.mcnemar_p]
    out += ["", "S5X per-checkpoint paired SL-EN gap (100 verified translation pairs), STRICT (refused) and BROAD (refused+partial) " + src(RES / "gap_range.csv"), ""]
    out += md_table(x, ["checkpoint", "judge", "definition", "n_pairs", "p_en", "p_sl", "gap", "CI", "p", "did"], 2)
    kk = K[(K.artifact == "exp4") & K.harmful].copy()
    out += ["", "Keyword-proxy miscalibration (exp4, harmful S5+S5X; FP = keyword 'refusal' the judge calls not-refused) " + src(RES / "keyword_miscalibration.csv"), ""]
    out += md_table(kk, ["cell", "lang", "judge", "n", "keyword_rate", "judged_rate", "fp_share", "fn_share", "fp_share_partial", "kappa"])
    out += ["", f"- R_seq within-edit collapse: {byid['exp4_rseq_within_edit']['correction_note']} " + src(E4 / "results/rseq/rseq_validity.json"),
            f"- B3 batching certification: {byid['exp4_B3_batching']['correction_note'][:600]}",
            f"- Judge provenance (paste): {byid['exp4_judge_provenance']['paste_text']}", "",
            "## (7) Experiment 8 tables with BOTH judges", "",
            "`report_tables.md` is reproduced verbatim in `results/exp8_report_tables_verbatim.md`. It MIXES judges: the activation, weight (W0/W1/W2) and community tables use gpt-4.1 labels "
            "(arm-prioritised, NOT random), while the depth table and the 'Repairing' table (W0 .93 / W3 / W4) use Qwen3-14B. Per-judge re-split below (n per cell); compare judges only on the item overlap "
            f"({src(RES / 'exp8_overlap_gpt41_vs_qwen.csv')}).", ""]
    D = pd.read_csv(RES / "exp8_by_judge.csv")
    D = D[D.judge.isin(["gpt41", "qwen3_14b"]) & (D.role.isin(["harmful", "harmless"]))]
    piv = D.pivot_table(index=["model", "arm"], columns=["judge", "lang", "role"], values="p_refused").round(2)
    nn = D.pivot_table(index=["model", "arm"], columns=["judge", "lang", "role"], values="n")
    rows = []
    for idx in piv.index:
        row = {"model": idx[0], "arm": idx[1]}
        for j in ("gpt41", "qwen3_14b"):
            for lg in ("en", "sl"):
                for ro in ("harmful", "harmless"):
                    v = piv.get((j, lg, ro), pd.Series(dtype=float)).get(idx, np.nan)
                    n = nn.get((j, lg, ro), pd.Series(dtype=float)).get(idx, np.nan)
                    row[f"{'G' if j == 'gpt41' else 'Q'} {lg.upper()} {'harmful' if ro == 'harmful' else 'harmless'}"] = "–" if pd.isna(v) else f"{v:.2f} ({int(n)})"
        rows.append(row)
    T8 = pd.DataFrame(rows)
    T8 = T8[T8.drop(columns=["model", "arm"]).ne("–").any(axis=1)]
    out += md_table(T8, list(T8.columns))
    out += ["", f"Frozen block: F1 cut {rv('exp8_cut_A2')} [{fmt(byid['exp8_cut_A2']['ci_low'])}, {fmt(byid['exp8_cut_A2']['ci_high'])}] (gpt-4.1; best random A9 {rv('exp8_cut_A9')}, "
            f"shuffled A10 {rv('exp8_cut_A10')}); A6 cut {rv('exp8_cut_A6')} [{fmt(byid['exp8_cut_A6']['ci_low'])}, {fmt(byid['exp8_cut_A6']['ci_high'])}]; F3 raw McNemar p {fmt(byid['exp8_F3_p']['recomputed_value'], 4)}, "
            f"Holm {fmt(byid['exp8_F3_holm']['recomputed_value'], 3)}. C2 (community + random weight edit) SL .16 vs C1 (community + r_prior) .20 under gpt-4.1.", "",
            "## (8) Surrogacy bounds and which judge gated each panel", "",
            f"- GaMS3 (exp6, SUMMARY_ONLY, HistGBT CIs not re-run): Gap_K {fmt(byid['exp6_gapK']['summary_value'])} [0.074, 0.265]; B_K {fmt(byid['exp6_BK']['summary_value'])}; "
            f"Gap_Heretic_K on journal trials {fmt(byid['exp6_gap_heretic_K']['summary_value'])}; SL/EN mean-change ratio for K {fmt(byid['exp6_ratio_K']['summary_value'], 2)}; "
            f"reverse Gap_K {fmt(byid['exp6_reverse_gapK']['summary_value'])}; frozen-residual source-layer carrier R {fmt(byid['exp6_srcnull_R']['summary_value'])}, K {fmt(byid['exp6_srcnull_K']['summary_value'])}; "
            f"reselection keeps {byid['exp6_reselection']['paste_text']}. " + src(E6 / "results/analysis_results.json"),
            f"- Source-layer lead (post-freeze): recomputed Spearman(log KL_SL/KL_EN, direction index) = {rv('exp6_srclayer_spearman')} over {byid['exp6_srclayer_spearman']['n']} non-collapsed edits "
            "(the artifact's 0.77 used its fitted subset).",
            f"- Cross-machine repro: the draft's 'max |diff| 97.2' is a raw hidden-state projection (Hproj, magnitude ~2000-3000), not a behavioural quantity; behavioural traits move <= 0.041 log-odds (R_seq), "
            "<= 0.0021 nats (KL), <= 0.12 nats/token (FLORES NLL). Full unit table in `pending_human_review.md`.", "",
            "| panel | judge(s) that gated it | coverage | validated on edits? |", "|---|---|---|---|",
            "| exp4 RefusEU | Qwen3-14B (post-hoc F1 substitute) + gpt-4.1 subset | Qwen 4,800/4,800; gpt-4.1 716 (seeded random) | edited-only kappa .78 binary / .73 4-class (n=354) |",
            "| exp5 S4 | gpt-4.1 (priority-ordered ~52% of S4 harmful) + Nemotron | gpt-4.1 1,072; Nemotron 850; overlap 200 | edited-only kappa .74 binary (n=126) |",
            "| exp6 GaMS3 panel | gpt-4.1 1,130 + Qwen3-14B (all 2,140) | gpt-4.1 blocked at 1,130 | edited-only kappa .80 binary / .58 4-class (n=777) |",
            "| exp7 Gemma panel | gemma-3-12b-it SELF-judge | all validity edits | NO: validated on 440 ORIGINAL generations only (binary agreement .86 on 365); SELF-JUDGING |",
            "| exp8 causal | gpt-4.1 (arm-prioritised) + Qwen3-14B (all) | gpt-4.1 5,298/12,136 | edited-only kappa .74 binary / .53 4-class (n=4,660) |",
            "| iter-1 exp3 | gpt-4.1 only | 1,596 | SINGLE_JUDGE (gpt-4.1-mini T5 check failed) |", "",
            "## (9) Dead-end ledger", "", "See `results/dead_end_ledger.md` (one row per item, with the closing number and source path).", "",
            "## (10) The Gemma SL-EN gap as a RANGE across judges and definitions", "",
            f"Across LLM judges and datasets (n >= 30 per language), the gemma_edit SL-EN refusal gap is **{M['gemma_gap_strict_min']:+.2f} to {M['gemma_gap_strict_max']:+.2f} STRICT** "
            f"(refused only) but **{M['gemma_gap_broad_min']:+.2f} to {M['gemma_gap_broad_max']:+.2f} BROAD** (refused + partial). On S5X (Qwen) strict +0.69 [0.60, 0.78] "
            f"becomes broad {M['gemma_gap_s5x_broad_qwen']:+.2f} [0.14, 0.32]; on S5 (Qwen) broad is -0.04 [-0.10, 0.02]. The English edit mostly converts refusals into PARTIAL (hedged) replies "
            "rather than into compliance; the Slovene residual is real under every LLM judge in the STRICT sense, but its size is a definitional choice.", ""]
    s2 = S[S.checkpoint.isin(["gemma_edit", "community_ref", "gams_edit"])]
    out += md_table(s2, ["checkpoint", "dataset", "definition", "judges", "gap_min", "gap_max", "llm_gap_min", "llm_gap_max", "widest_ci", "sign_stable"], 2)
    out += ["", "Suggested headline restatement (paste, replaces the draft's): 'Under a matched 116-trial NF4 Heretic search whose English keyword objective is miscalibrated on Gemma-3 "
            "(keyword 'refusals' on the selected edit are 76% hedged or compliant replies by the judge), the selected edit leaves strict Slovene refusal far above English "
            "(+0.22 to +0.71 across automated judges and datasets), but much of the English change is a shift from refusal to partial compliance: counting partial replies, "
            f"the gap ranges from {M['gemma_gap_broad_min']:+.2f} to {M['gemma_gap_broad_max']:+.2f}. A stronger edit of the same base largely transfers; all-layer ablation removes the Slovene residual.' "
            "Keep the n = 2 models / one seed / NF4 / MT-Slovene / no-native-review caveats beside every comparison."]
    (RES / "report_repairs.md").write_text("\n".join(out) + "\n")
    (RES / "exp8_report_tables_verbatim.md").write_text((E8 / "results/report_tables.md").read_text())
    print(json.dumps(M, indent=1))


if __name__ == "__main__":
    main()

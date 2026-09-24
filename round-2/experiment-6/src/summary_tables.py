#!/usr/bin/env python3
"""Regenerate results/summary_tables.md (the numbers quoted in README.md) from results/*.json - never typed by hand.

  uv run summary_tables.py
"""
from __future__ import annotations

from common import RES, CostLedger, jload


def f(x, d=3):
    try:
        return f"{float(x):.{d}f}"
    except (TypeError, ValueError):
        return "NA"


def ci(v, d=3):
    return f"[{f(v[0], d)}, {f(v[1], d)}]" if v else "NA"


def main() -> None:
    r = jload(RES / "analysis_results.json")
    ut = jload(RES / "unit_tests.json")
    pt = jload(RES / "post_tests.json") if (RES / "post_tests.json").exists() else {}
    L = []
    L.append(f"Fitted set F = {r['n_F']} non-collapsed E0+E1 edits ({r['n_collapsed_fitted']} collapsed fitted edits excluded); "
             f"primary learner = {r['learner_adequacy']['primary']}; bootstrap B = {r['bootstrap']['R']['B']}.\n")
    L.append("| trait | R2 EN->EN (raw) | R2 EN->SL (raw) | ceil EN_B | ceil SL_B | R2* plac | R2* test | **Gap** | 95% CI | 90% CI | MDE | Holm p | B_t [95% CI] | Gap_mm [95% CI] | Gap_SIMEX | halves |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for t in ("R", "R1", "Rb", "K", "N", "M"):
        g, b, B, mm, sx, st = r["gap"][t], r["bootstrap"][t], r["B_t"][t], r["margin_matched"].get(t, {}), r["simex"][t], r["stability"][t]
        L.append(f"| {t} | {f(g['R2_plac'])} | {f(g['R2_test'])} | {f(r['reliability'][f'{t}_en_B'])} | {f(r['reliability'][f'{t}_sl_B'])} | "
                 f"{f(g['R2s_plac'])} | {f(g['R2s_test'])} | **{f(g['Gap'])}** | {ci(b['gap_ci95'])} | {ci(b['gap_ci90'])} | {f(b['MDE'])} | "
                 f"{f(b.get('p_holm'))} | {f(B['B'])} {ci(B['ci95'])} | {f(mm.get('Gap_mm'))} {ci(mm.get('ci95'))} | {f(sx['gap_simex'])} | "
                 f"{f(st['half0'])} / {f(st['half1'])} |")
    L.append("\nReliabilities (Spearman-Brown, split-half, fitted set):\n")
    L.append("| trait | EN_A | EN_B | SL_A | SL_B | no-signal (F8) EN / SL |")
    L.append("|---|---|---|---|---|---|")
    for t in ("R", "R1", "Rb", "K", "N", "M"):
        rl = r["reliability"]
        ns = r["no_signal_F8"]
        L.append(f"| {t} | {f(rl[f'{t}_en_A'])} | {f(rl[f'{t}_en_B'])} | {f(rl[f'{t}_sl_A'])} | {f(rl[f'{t}_sl_B'])} | "
                 f"{ns[f'{t}_en']['no_signal']} / {ns[f'{t}_sl']['no_signal']} |")
    car = r.get("carrier", {})
    L.append("\nCarrier regression on y_t = SL residual - EN residual (ridge, out-of-fold; S0 = b1, b1x, b2, b3 x9, Omega):\n")
    L.append("| trait | R2(S0) | dR2(D given S0) [95% CI] | dR2(S0 given D) | dR2(H given S0) | dR2(realized given S0) | dR2(P given S0) | OLS std coef of D [95% CI] |")
    L.append("|---|---|---|---|---|---|---|---|")
    for t, c in car.items():
        d = c.get("D", {})
        L.append(f"| {t} | {f(c['R2_S0_ridge'])} | {f(d.get('dR2_C_given_S0_ridge'))} {ci(d.get('ci95_dR2_C_given_S0'))} | "
                 f"{f(d.get('dR2_S0_given_C_ridge'))} | {f(c.get('H', {}).get('dR2_C_given_S0_ridge'))} | "
                 f"{f(c.get('realized', {}).get('dR2_C_given_S0_ridge'))} | {f(c.get('P', {}).get('dR2_C_given_S0_ridge'))} | "
                 f"{f(c['ols_hc3']['D']['coef_std'])} {ci(c['ols_hc3']['D']['ci95'])} |")
    fc = r["forecast"]
    L.append("\nOut-of-sample forecast (90% CV+ conformal PI of SL traits from EN traits; never-fitted edits):\n")
    L.append("| trait | coverage E_TPE | coverage E_R | +D: E_TPE | +D: E_R | core observed | core predicted | core excess | outside PI | out of support |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for t in ("R", "R1", "Rb", "K", "N", "M"):
        a, bb = fc[t]["f"], fc[t]["f_plus_D"]
        co = a.get("core") or {}
        L.append(f"| {t} | {f(a['coverage'].get('E_TPE', {}).get('coverage_90PI'), 2)} | {f(a['coverage'].get('E_R', {}).get('coverage_90PI'), 2)} | "
                 f"{f(bb['coverage'].get('E_TPE', {}).get('coverage_90PI'), 2)} | {f(bb['coverage'].get('E_R', {}).get('coverage_90PI'), 2)} | "
                 f"{f(co.get('observed_SL'))} | {f(co.get('pred_SL'))} | {f(co.get('excess'))} | {co.get('outside_PI')} | {co.get('out_of_support')} |")
    gh = r["gap_heretic"]
    L.append("\nSecondary Gap_Heretic (X = journal EN keyword refusals + log KL, E0+E_TPE):\n")
    L.append("| trait | R2* EN | R2* SL | Gap_Heretic |")
    L.append("|---|---|---|---|")
    for t, g in gh.items():
        L.append(f"| {t} | {f(g['R2s_plac'])} | {f(g['R2s_test'])} | {f(g['Gap_Heretic'])} |")
    v = r["validity"]
    L.append(f"\nValidity gate ({v.get('label_source')}): REF = {v.get('REF')}; " + "; ".join(
        f"{l}: n_cond {v.get(l, {}).get('n_conditions')}, rho(R_seq) {f(v.get(l, {}).get('spearman_R_seq'))} {ci(v.get(l, {}).get('spearman_R_seq_ci95'))}, "
        f"rho(R1) {f(v.get(l, {}).get('spearman_R1'))}, AUROC item R_seq {f(v.get(l, {}).get('auroc_item_R_seq'))}" for l in ("en", "sl")))
    rs = r["reselection"]
    L.append(f"\nBilingual reselection ({rs['method']}): selected {rs['selected_edit']} = {rs['selected']}; any trial with SL_est <= 20 at KL <= 1: "
             f"{rs['any_trial_SL_est_le_20_at_KL_le_1']}; core SL_est {f(rs.get('core_SL_est'), 1)}.")
    L.append(f"\nUnit tests: U1 {ut['U1']['pass']}, U1b {ut['U1b']['pass']}, U1c {ut['U1c']['pass']}, U2 {ut['U2']['pass']} "
             f"(max rel diff {f(ut['U2']['max_rel_frob_diff_BA'], 7)}), U3 {ut['U3']['pass']}, U7 gen {ut['U7']['gen_pass']} / tf {ut['U7']['tf_pass']}; "
             f"U4 {pt.get('U4_formula_vs_peft_path', {}).get('pass')}, U5 ratio {f(pt.get('U5_truncated_vs_full_KL', {}).get('ratio_trunc_over_full'))}.")
    L.append("\nGap robustness (point estimates; 2 CV repeats): other learner / collapsed edits included / SL half-A as the source / "
             "MT-stable items only / low-R x low-K stratum (descriptive):\n")
    L.append("| trait | other learner | with collapsed | reverse (SL_A source) | MT-stable subset | stratum n | stratum Gap |")
    L.append("|---|---|---|---|---|---|---|")
    for t in ("R", "R1", "Rb", "K", "N", "M"):
        g, st = r["gap"][t], r["stability"][t]
        sr = st.get("stratum_lowR_lowK", {})
        L.append(f"| {t} | {f(g['sensitivity_other_learner']['Gap'])} | {f(g['with_collapsed']['Gap'])} | {f(g['reverse_SL_source']['Gap'])} | "
                 f"{f(st.get('mt_quality_subset', {}).get('Gap'))} | {sr.get('n')} | {f(sr.get('Gap'))} |")
    mm = r.get("mixed_model", {})
    if mm:
        L.append("\nItem x edit mixed model (half-B items; d ~ ENt*margin + lang + lang:ENt + (1|item) + (1|edit); standardized ENt, margin; "
                 "descriptive p-values):\n")
        L.append("| trait | n rows | lang [95% CI] | lang:ENt [95% CI] | ENt | margin | ENt:margin |")
        L.append("|---|---|---|---|---|---|---|")
        for t, m in mm.items():
            if "terms" not in m:
                L.append(f"| {t} | error {m.get('error')} | | | | | |")
                continue
            tt = m["terms"]
            L.append(f"| {t} | {m['n_rows']} | {f(tt['lang']['coef'], 4)} {ci(tt['lang']['ci95'], 4)} | {f(tt['lang:ENt']['coef'], 4)} "
                     f"{ci(tt['lang:ENt']['ci95'], 4)} | {f(tt['ENt']['coef'], 4)} | {f(tt['margin']['coef'], 4)} | {f(tt['ENt:margin']['coef'], 4)} |")
    ts = r.get("transfer_slopes", {})
    if ts:
        L.append("\nEXPLORATORY transfer slopes (post-freeze): how much the SL trait moves per unit EN move, on independent items "
                 "(slope dSL_B~dEN_A over placebo slope dEN_B~dEN_A; 1 = equal response):\n")
        L.append("| trait | slope placebo | slope test [95% CI] | **ratio** [95% CI] | mean-change ratio SL/EN [95% CI] | relative-to-baseline ratio |")
        L.append("|---|---|---|---|---|---|")
        for t in ("R", "R1", "Rb", "K", "N", "M"):
            v = ts.get(t, {})
            L.append(f"| {t} | {f(v.get('slope_plac_EN_B_on_EN_A'))} | {f(v.get('slope_test_SL_B_on_EN_A'))} {ci(v.get('slope_test_ci95'))} | "
                     f"**{f(v.get('ratio_test_over_plac'))}** {ci(v.get('ratio_ci95'))} | {f(v.get('ratio_mean_change_SL_over_EN_B'))} "
                     f"{ci(v.get('ratio_mean_change_ci95'))} | {f(v.get('ratio_relative_change_SL_over_EN_B'))} |")
    pa = r.get("param_attribution", {})
    if pa:
        L.append("\nEXPLORATORY parameter attribution of B_t (add-one increment of each raw Heretic parameter, SL minus EN; top 3):\n")
        L.append("| trait | top parameters (increment) |")
        L.append("|---|---|")
        for t in ("R", "R1", "Rb", "K", "N", "M"):
            if t in pa:
                L.append(f"| {t} | " + "; ".join(f"{k} {f(v)}" for k, v in pa[t]["top3"]) + " |")
    kr = r.get("k_ratio_carriers", {})
    if kr:
        o, ox = kr["over_X_plus_S0"], kr["over_X"]
        L.append(f"\nEXPLORATORY language-divergence ratio y = {kr['y']} (n = {kr['n']}, sd {f(kr['y_sd'])}). CV R2 of each block alone (ridge): "
                 + ", ".join(f"{k} {f(v)}" for k, v in kr["R2_alone_ridge"].items()) + "; GBT: "
                 + ", ".join(f"{k} {f(v)}" for k, v in kr["R2_alone_gbt"].items()) + f". Base X+S0 R2 = {f(o['R2_S0_ridge'])}.\n")
        L.append("| carrier C | dR2(C given X+S0) ridge [95% CI] | dR2(C given X+S0) GBT | dR2(C given X) ridge [95% CI] | Spearman(C, y) |")
        L.append("|---|---|---|---|---|")
        sp = kr["spearman_y"]
        for nm in ("D", "SRC", "H", "P"):
            if nm in o:
                L.append(f"| {nm} | {f(o[nm]['dR2_C_given_S0_ridge'])} {ci(o[nm]['ci95_dR2_C_given_S0'])} | {f(o[nm]['dR2_C_given_S0_gbt'])} | "
                         f"{f(ox[nm]['dR2_C_given_S0_ridge'])} {ci(ox[nm]['ci95_dR2_C_given_S0'])} | "
                         f"{f(sp.get('D')) if nm == 'D' else (f(sp.get('src_depth')) + ' (depth)' if nm == 'SRC' else '')} |")
    sc_ = r.get("source_carrier", {})
    if sc_:
        L.append("\nEXPLORATORY source-layer carrier on the frozen residual target y_t (SL resid - EN resid): dR2(SRC given S0) ridge = "
                 + "; ".join(f"{t} {f(sc_[t].get('SRC', {}).get('dR2_C_given_S0_ridge'))} {ci(sc_[t].get('SRC', {}).get('ci95_dR2_C_given_S0'))}"
                             for t in ("R", "R1", "Rb", "K", "N", "M") if t in sc_) + ".")
    fq = r.get("forecast_quantile_gbt", {})
    cl = r.get("core_logratio", {})
    if fq:
        L.append("\nQuantile-GBT 90% PI coverage (secondary) and core-trial log-ratio excess log|SL|-log|EN| (z vs F):\n")
        L.append("| trait | QGBT cov E_TPE | QGBT cov E_R | core log-ratio | F mean | z | pct rank in F |")
        L.append("|---|---|---|---|---|---|---|")
        for t in ("R", "R1", "Rb", "K", "N", "M"):
            q, c = fq.get(t, {}), cl.get(t, {})
            L.append(f"| {t} | {f(q.get('E_TPE', {}).get('coverage_90PI'), 2)} | {f(q.get('E_R', {}).get('coverage_90PI'), 2)} | "
                     f"{f(c.get('core_logratio'))} | {f(c.get('F_mean'))} | {f(c.get('z'), 2)} | {f(c.get('pct_rank_in_F'), 2)} |")
    jm = jload(RES / "judge_meta.json") if (RES / "judge_meta.json").exists() else {}
    if jm:
        L.append(f"\nJudging: {jm.get('judge_model')} labelled {jm.get('n_labelled')}/{jm.get('n')} generations; label counts "
                 f"{jm.get('label_counts')}; second judge {jm.get('second_judge')} on {jm.get('n_second')}: kappa 6-way "
                 f"{f(jm.get('kappa_6way_j1_j2'))}, kappa refused-vs-not {f(jm.get('kappa_refused_j1_j2'))}, raw agreement "
                 f"{f(jm.get('agreement_j1_j2'))}; kappa judge vs keyword rule (refused) {f(jm.get('kappa_refused_judge_vs_rule'))}.")
    jr = r.get("judge_recounts", {})
    if jr and "reference_disagreement_judge_vs_rule" in jr:
        rd, rp, f7 = jr["reference_disagreement_judge_vs_rule"], jr["r_prior_recount"], jr.get("F7_en_vs_sl_judged", {})
        L.append(f"\nRule-labelled Stage-0c decisions re-checked with judge labels: reference source disagreements {rd['ref']}/{rd['n']} "
                 f"(refusal refs), {rd['comp']}/{rd['n']} (compliance refs), by kind/lang {rd['by_kind_lang']}; r_prior judge counts "
                 f"{rp['counts_refused_harmless_halfA_judge']} (pooled {rp['pooled']}, defined under judge = {rp['defined_under_judge']}; "
                 f"rule counts {rp['rule_based_status'].get('counts_refused_harmless_halfA')}). EN-vs-SL judged refusal over "
                 f"{f7.get('n_conditions')} validity conditions: Spearman {f(f7.get('spearman_EN_SL_judged_refusal'))}, mean refused EN "
                 f"{f(f7.get('mean_refused_en'))} / SL {f(f7.get('mean_refused_sl'))}.")
    sc = r["verdict"].get("frozen_predictions_scorecard", {})
    if sc:
        L.append("\nFrozen predictions scorecard (results/frozen_predictions.json, evaluated mechanically):\n")
        L.append("| id | evaluation | holds |")
        L.append("|---|---|---|")
        L.append(f"| G1 Gap_R 90% CI in +/-0.10 | {ci(sc['G1']['gap_R_ci90'])} | {sc['G1']['holds']} |")
        L.append(f"| G2 Gap_Rb 90% CI in +/-0.10 | {ci(sc['G2']['gap_Rb_ci90'])} | {sc['G2']['holds']} |")
        L.append(f"| G3 some Gap_K/N/M >= 0.10 with B_t > 0 | " + "; ".join(f"{t}: Gap {f(v['Gap'])}, B {f(v['B_t'])} {ci(v['B_t_ci95'])}"
                                                                        for t, v in sc['G3']['per_trait'].items())
                 + f" | point {sc['G3']['holds_point']}; with B CI {sc['G3']['holds_with_B_ci']} |")
        L.append(f"| G4 D adds dR2 >= 0.05 over S0 | " + "; ".join(f"{t}: {f(v['dR2_D_given_S0'])} {ci(v['ci95'])}" for t, v in sc['G4']['per_trait'].items())
                 + f" | any {sc['G4']['holds_any']} |")
        L.append(f"| G5 r_prior undefined | rule counts {sc['G5']['rule_counts']} (defined {sc['G5']['rule_labels_defined']}); judge counts "
                 f"{sc['G5']['judge_counts']} (defined {sc['G5']['judge_defined']}) | rule {sc['G5']['holds_rule']}; judge {sc['G5']['holds_judge']} |")
        L.append(f"| G6 PI coverage >= 85% on E_TPE/E_R | share of trait x set meeting 85%: {f(sc['G6']['share_trait_sets_meeting_85'], 2)} | "
                 f"all {sc['G6']['holds_all']} |")
    rc = jload(RES / "repro_check.json") if (RES / "repro_check.json").exists() else {}
    if rc:
        L.append("\nCross-machine / rerun reproducibility (repro_check.py): " + "; ".join(
            f"{e} (stored on {v['host_of_stored']}): bit-identical {v['bit_identical']}, max |diff| {v['max_abs']:.3g}" for e, v in rc["edits"].items()))
    u6 = jload(RES / "u6_flores_check.json") if (RES / "u6_flores_check.json").exists() else {}
    if u6:
        L.append(f"\nU6 FLORES NLL vs iteration-1 EXP3: n {u6['n_compared']}, mean |diff| {f(u6['mean_abs_diff'], 4)}, max {f(u6['max_abs_diff'], 4)} "
                 f"(tolerance 2e-3: pass {u6['pass']}).")
    if pt.get("U7_diagnostic"):
        d7 = pt["U7_diagnostic"]
        L.append(f"\nU7 diagnostic: same-length unpadded batch vs bs1 max |dlogp| {f(d7['same_length_no_padding_vs_bs1']['max_abs'], 4)}; padded mixed "
                 f"batch vs bs1 max {f(d7['padded_mixed_vs_bs1']['max_abs'], 4)} (per-sequence mean NLL max diff "
                 f"{f(d7['padded_mixed_vs_bs1']['per_seq_mean_nll_max_abs_diff'], 4)}); repeated batched pass bit-identical {d7['batched_repeat_bit_identical']}.")
    L.append(f"\nVerdict: {r['verdict']}")
    L.append(f"\nOpenRouter spend for this artifact: ${CostLedger().spent():.2f}")
    (RES / "summary_tables.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""results/report_tables.md - every table in the README/paper, printed straight from analysis_summary.json + cells.csv."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C


def f(x, n=2):
    try:
        if x is None or (isinstance(x, float) and not np.isfinite(x)):
            return "–"
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return "–"


def ci(v, n=2):
    return f"[{f(v[0], n)}, {f(v[1], n)}]" if v else "–"


def main() -> None:
    S = C.jload(C.RES / "analysis_summary.json")
    T = pd.read_parquet(C.RES / "cells.parquet").set_index("cell")
    red = C.jload(C.RES / "redundancy_index.json")
    L = []
    A = L.append
    A("# Report tables — how deep must an edit go to stop Slovene refusal (gemma-3-12b-it, NF4)\n")
    A(f"Generations: {S['n_generations']} ({S['n_judged']} judged); cells: {S['n_cells']}. "
      "Scorer: local Qwen3-14B with the frozen exp4 protocol rubric; PARTIAL counts as compliance and is shown separately; "
      "INVALID (irrelevant/malformed/empty/unparsed) is never refusal.\n")
    jc = S.get("judge_certification") or {}
    A(f"Scorer certification (kappa refused-vs-not vs gpt-4.1, EDITED checkpoints only): on-disk pools "
      f"{f(jc.get('kappa_on_disk_edited'))}, this run's own cells {f(jc.get('kappa_this_run_edited'))}.\n")

    A("\n## Part A — DEV depth-redundancy index (activation-only, S3 JBB half A, 44 harmful items/language)\n")
    A("| family | lang | k=0 | " + " | ".join(str(k) for k in range(4, 49, 4)) + " | index_L |")
    A("|---|---|" + "---|" * 14)
    for fam in ("prefix", "suffix"):
        for g in C.LANGS:
            r = red["index"][g][fam]
            A(f"| {fam} | {g.upper()} | " + " | ".join(f(x) for x in r["curve"]) +
              f" | **{r['index']}{'*censored' if r['censored'] else ''}** {ci(r['index_boot_ci'], 0)} |")
    A("\nLeave-one-band-out necessity (rate with the band spared minus rate with all 48 covered):\n")
    A("| lang | 1-12 | 13-24 | 25-36 | 37-48 | all-48 rate |")
    A("|---|---|---|---|---|---|")
    for g in C.LANGS:
        r = red["index"][g]
        A(f"| {g.upper()} | " + " | ".join(f(r["lobo"][b]["necessity"]) for b in ("1-12", "13-24", "25-36", "37-48")) +
          f" | {f(r['all48_rate'])} |")
    if "C2_index_SL_gt_EN" in S:
        A(f"\nPre-registered C2 (index_SL > index_EN): {S['C2_index_SL_gt_EN']}. GaMS3 contrast quoted from iteration 2 "
          f"(EN 0.57 / SL 0.50 under the same English ablation), not re-measured here.\n")

    A("\n## Anchors — reproduction of iteration-2 cells under this scorer\n")
    A("| cell | EN ours | EN exp8 (gpt-4.1 / Qwen) | SL ours | SL exp8 (gpt-4.1 / Qwen) |")
    A("|---|---|---|---|---|")
    for c, r in (S.get("anchor_check") or {}).items():
        e8 = r["exp8"]
        g4 = e8.get("gpt41") or e8.get("gpt41_hoc") or {}
        qw = e8.get("qwen_exp8") or e8.get("qwen_exp8_hoc") or {}
        A(f"| {c} | {f(r['this_run_screen_partial_aware']['en'])} | {f(g4.get('en'))} / {f(qw.get('en'))} | "
          f"{f(r['this_run_screen_partial_aware']['sl'])} | {f(g4.get('sl'))} / {f(qw.get('sl'))} |")

    A("\n## Screen panel (S3 JBB half B: 41 harmful + 41 harmless per language)\n")
    A("| cell | family | cov | c | k_eff | E | EN harm | SL harm | SL partial | SL invalid | SL over-ref | SL LID | FLORES dNLL EN/SL | KL SL |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    sc = T[T["stage"] == "screen"].sort_values(["family", "cell"])
    for c, r in sc.iterrows():
        A(f"| {c} | {r['family']} | {r['coverage'] or '–'} | {f(r['c'])} | {f(r['k_eff'], 1)} | "
          f"{('%.3g' % r['E']) if np.isfinite(r['E'] or np.nan) else '–'} | {f(r['en_harm_refused'])} | "
          f"**{f(r['sl_harm_refused'])}** | {f(r['sl_harm_partial'])} | {f(r['sl_harm_invalid'])} | {f(r['sl_ben_refused'])} | "
          f"{f(r['sl_harm_lid_ok'])} | {f(r['flores_en'], 3)} / {f(r['flores_sl'], 3)} | {f(r['kl_sl'], 3)} |")

    P2 = S.get("P2_screen", {})
    if P2.get("groups"):
        A("\n## P2 — matched-energy groups (narrow-and-strong vs broad-and-weak)\n")
        A("| group | narrow | broad | E narrow | E broad | SL narrow | SL broad | SL contrast [CI] | EN contrast | random contrast | PC contrast | SL FLORES n/b |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for g, r in sorted(P2["groups"].items()):
            A(f"| {g} | {r['narrow']} | {r['broad']} | {'%.3g' % r['E_narrow']} | {'%.3g' % r['E_broad']} | "
              f"{f(r['SL_narrow'])} | {f(r['SL_broad'])} | **{f(r['contrast_SL'])}** {ci(r['contrast_SL_ci95'])} | "
              f"{f(r['contrast_EN'])} | {f(r.get('random_contrast_SL'))} | {f(r.get('pc_contrast_SL'))} | "
              f"{f(r['flores_sl_narrow'], 2)}/{f(r['flores_sl_broad'], 2)} |")
        p = P2["pooled"]
        A(f"\nPooled over {p['n_groups']} groups: SL contrast **{f(p['contrast_SL'])}** {ci(p['contrast_SL_ci95'])}; "
          f"EN contrast {f(p['contrast_EN'])} {ci(p['contrast_EN_ci95'])}; SL minus matched-random "
          f"{f(p['SL_minus_random'])} {ci(p['SL_minus_random_ci95'])}; SL minus matched-PC {f(p['SL_minus_pc'])} "
          f"{ci(p['SL_minus_pc_ci95'])}; difference of differences SL-EN {f(p['did_SL_minus_EN'])} {ci(p['did_ci95'])}. "
          f"**P2 {'PASS' if P2.get('pass_P2') else 'FAIL'}** (confirmatory: {P2.get('confirmatory')}).\n")
        A(f"Placebos: narrow/broad swap within item {ci(P2['placebo_swap_within_item']['ci95'])} "
          f"(observed outside: {P2['placebo_swap_within_item']['observed_outside']}); language permutation "
          f"{ci(P2['placebo_permute_language']['ci95'])} (observed outside: {P2['placebo_permute_language']['observed_outside']}).\n")

    P1 = S["P1"]
    A("\n## P1 — does coverage explain the Slovene residual beyond total energy?\n")
    A(f"- cells n = {P1['n_cells']}; R2(base) = {f(P1['r2_base'], 3)}; R2(base+coverage) = {f(P1['r2_full'], 3)}; "
      f"**dR2 = {f(P1['dR2'], 3)}** {ci(P1['dR2_ci95'], 3)}; LOO dR2 = {f(P1['dR2_loo'], 3)}; partial F = {f(P1['partial_F'], 2)} "
      f"(p = {f(P1['p_F'], 4)}).")
    A(f"- energy alone: R2 = {f(P1['r2_logE_only'], 3)}. Spearman with the SL residual: " +
      ", ".join(f"{k} {f(v)}" for k, v in P1["spearman_with_SL_residual"].items()) + ".")
    A(f"- power: {P1['power_note']}.")
    A(f"- placebo (permuted cell targets): p95 = {f(P1['placebo_permuted_targets']['p95'], 3)}, observed exceeds it: "
      f"{P1['placebo_permuted_targets']['observed_exceeds_p95']}.")
    A(f"- **P1 {'PASS' if P1['pass_P1'] else 'FAIL'}**; falsifier (dR2 < 0.05) fired: {P1['falsifier_dR2_lt_0.05']}.")

    if "P3_screen" in S:
        A("\n## P3 — does the DEV index predict per-cell residuals out of sample?\n")
        A("| lang | index_L | n cells | Spearman [CI] | MAE | cells below index above 0.5 | cells at/above index below 0.5 |")
        A("|---|---|---|---|---|---|---|")
        for g in C.LANGS:
            r = S["P3_screen"][g]
            t = r["threshold"]
            A(f"| {g.upper()} | {r['index']} | {r['n_cells']} | {f(r['spearman'])} {ci(r['spearman_ci95'])} | {f(r['mae'])} | "
              f"{f(t['share_above_0.5_when_below'])} (n={t['n_cells_below_index']}) | "
              f"{f(t['share_below_0.5_when_at_or_above'])} (n={t['n_cells_at_or_above_index']}) |")
        A(f"\n**P3 {'PASS' if S['P3_screen']['pass_P3'] else 'FAIL'}** (bar: Spearman >= 0.6 in both languages).")
        if "P3_confirm_hoc" in S:
            A("\nHeld-out harm categories (S4 hoc), confirmation cells only:\n")
            A("| lang | n cells | Spearman [CI] | MAE |")
            A("|---|---|---|---|")
            for g in C.LANGS:
                r = S["P3_confirm_hoc"][g]
                A(f"| {g.upper()} | {r['n_cells']} | {f(r['spearman'])} {ci(r['spearman_ci95'])} | {f(r['mae'])} |")

    iso = S.get("iso_contrasts") or {}
    if iso.get("matched_efficacy"):
        A("\n## Matched-efficacy and matched-collateral contrasts (not matched on energy)\n")
        A("| comparison | n pairs | mean SL(narrow) - SL(broad) [CI] | pairs favouring broad | sign-test p | mean EN diff | mean log-energy diff (broad-narrow) |")
        A("|---|---|---|---|---|---|---|")
        for tag, lab in (("matched_efficacy", "equal English effect (+-0.05)"), ("matched_collateral", "equal SL FLORES cost (+-0.1 nats)")):
            r = iso.get(tag) or {}
            if not r.get("n_pairs"):
                continue
            A(f"| {lab} | {r['n_pairs']} | **{f(r['mean_dSL_narrow_minus_broad'])}** {ci(r['ci95_pair_bootstrap'])} | "
              f"{r['n_favouring_broad']}/{r['n_pairs']} | {f(r['sign_test_p'], 4)} | {f(r['mean_dEN'])} | "
              f"{f(r['mean_dlogE_broad_minus_narrow'], 2)} |")
        A("\nPer-layer coefficient of effective coverage on the SL residual, holding different things fixed:\n")
        A("| controlling for | beta per effective layer [CI] |")
        A("|---|---|")
        for tag, lab in (("sl_given_en", "English refusal"), ("sl_given_en_and_logE", "English refusal + log energy"),
                         ("sl_given_collateral", "SL FLORES cost")):
            r = iso.get(tag) or {}
            if r:
                A(f"| {lab} | {f(r['beta_k_eff_per_layer'], 4)} {ci(r['beta_ci95'], 4)} |")
        A(f"\nSpearman(effective coverage, SL-minus-EN refusal gap) = {f(iso.get('spearman_keff_vs_SL_minus_EN_gap'))}.\n")

    conf = S.get("confirmation", {})
    if conf.get("cells"):
        A("\n## Confirmation (S4 StrongREJECT; hoc = held-out categories, ind = in-distribution; 70 pairs each)\n")
        A("| cell | hoc EN harm | hoc SL harm | ind SL harm | SL ASR (rubric) | SL over-refusal (S6) | SL invalid | SL LID | FLORES dNLL SL | utility macro EN / SL (change) |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for c, r in conf["cells"].items():
            ue, us = r.get("utility_en", {}), r.get("utility_sl", {})
            A(f"| {c} | {f((r.get('hoc_en_harm') or {}).get('rate'))} | **{f((r.get('hoc_sl_harm') or {}).get('rate'))}** | "
              f"{f((r.get('ind_sl_harm') or {}).get('rate'))} | {f(r.get('sl_asr_rubric'))} | "
              f"{f((r.get('s6_sl_overrefusal') or {}).get('rate'))} | {f(r.get('sl_invalid'))} | {f(r.get('sl_lid_ok'))} | "
              f"{f(r['flores_dNLL']['sl'], 3)} | {f(ue.get('macro'))} ({f(ue.get('macro_change'), 3)}) / "
              f"{f(us.get('macro'))} ({f(us.get('macro_change'), 3)}) |")
        A("\nPaired original-to-edited changes on hoc Slovene harmful refusal (vs CF_noop), with item-cluster CIs:\n")
        A("| cell | SL hoc change [CI] | McNemar p | EN hoc change [CI] |")
        A("|---|---|---|---|")
        for c, r in conf["cells"].items():
            s, e = r.get("hoc_sl_harm") or {}, r.get("hoc_en_harm") or {}
            A(f"| {c} | {f(s.get('change'))} {ci(s.get('change_ci95'))} | {f(s.get('mcnemar_p'), 4)} | "
              f"{f(e.get('change'))} {ci(e.get('change_ci95'))} |")

    A("\n## Judge sensitivity and instrument checks\n")
    r8 = S.get("exp8_rescore") or {}
    if r8.get("n"):
        A(f"- Gate 3 (our scorer on {r8['n']} SAVED exp8 generations): kappa vs exp8's gpt-4.1 "
          f"{f(r8.get('kappa_refused_vs_not_vs_gpt41_exp8'))} (n={r8.get('n_gpt41_exp8')}), vs exp8's Qwen run "
          f"{f(r8.get('kappa_refused_vs_not_vs_qwen_exp8'))} (n={r8.get('n_qwen_exp8')}).")
    kc = S.get("keyword_check") or {}
    ka, ks = kc.get("all_edited_cells") or {}, kc.get("suppressing_cells_only") or {}
    A(f"- Keyword proxy vs the judge, all edited cells: kappa {f(ka.get('kappa'))} (n={ka.get('n')}), proxy-says-refused-"
      f"judge-does-not {f(ka.get('keyword_says_refused_judge_does_not'))}. On the cells that actually SUPPRESS Slovene "
      f"refusal: kappa {f(ks.get('kappa'))} (n={ks.get('n')}), proxy-says-refused-judge-does-not "
      f"{f(ks.get('keyword_says_refused_judge_does_not'))}, judge-says-refused-proxy-does-not "
      f"{f(ks.get('judge_says_refused_keyword_does_not'))}; the proxy calls {f(kc.get('partial_class_called_refused_by_keyword'))} "
      f"of the PARTIAL class 'refused' (n={kc.get('n_partial')}). The pooled kappa trips the plan's 0.6 red flag "
      f"({kc.get('red_flag_kappa_gt_0.6')}); the breakdown shows why that pooled number is uninformative. "
      "No reported number uses the proxy.")
    A(f"- Judge parse failures (excluded from every rate, never counted as non-refusal): "
      f"{f(S.get('judge_fail_rate'), 4)} of judged generations.")
    A(f"- PARTIAL class fires on the core Heretic edit's English replies: {f(S.get('partial_fires_on_W0_EN'))}.")
    A(f"- Holm-adjusted p-values across the declared family: {S['holm']['adjusted']}.")

    bi = S.get("band_identity_exploratory") or {}
    if bi.get("dose_by_coverage"):
        A("\n## EXPLORATORY (declared in configs/explore_band_identity.json before its outcome was read) — WHICH layers, not HOW MANY\n")
        A("| coverage set | layers | SL refusal by strength (c = 0.25 .. 1.5) | lowest SL | ever < 0.5 | cheapest energy reaching < 0.5 |")
        A("|---|---|---|---|---|---|")
        for cov, d in sorted(bi["dose_by_coverage"].items(), key=lambda kv: kv[1]["sl_min"]):
            A(f"| {cov} | {len(d['c'])} strengths | " + ", ".join(f(x) for x in d["sl"]) + f" | **{f(d['sl_min'])}** | "
              f"{'yes' if d['reaches_sl_below_0.5'] else 'no'} | "
              f"{('%.0f' % d['min_E_with_sl_below_0.5']) if d['min_E_with_sl_below_0.5'] else '–'} |")
        cvs = bi.get("contiguous_vs_strided_at_matched_energy") or {}
        if cvs:
            A(f"\nContiguous vs strided coverage at matched energy (within 15% in log energy, {cvs['n_pairs']} pairs): "
              f"strided leaves **{f(cvs['mean_dSL_strided_minus_contiguous'])}** {ci(cvs['ci95'])} MORE Slovene refusal "
              f"(EN: {f(cvs['mean_dEN_strided_minus_contiguous'])}), while covering on average "
              f"{f(cvs['mean_extra_layers_strided'], 1)} more layers; sign test p = {f(cvs['sign_test_p'], 3)} "
              f"({cvs['n_strided_worse_for_SL']}/{cvs['n_pairs']} pairs worse), so the effect is carried by magnitude, "
              "not by a majority of pairs.\n")
        for tgt, lab in (("band_mass_model_sl_harm_refused", "SL"), ("band_mass_model_en_harm_refused", "EN")):
            m = bi.get(tgt)
            if not m:
                continue
            A(f"\nBand-mass model for {lab} refusal (reference band 37-48, R2 = {f(m['r2'], 3)}):\n")
            A("| term | beta [CI] |")
            A("|---|---|")
            for k, v in m["beta"].items():
                A(f"| {k} | {f(v, 3)} {ci(m['ci95'][k], 3)} |")

    s5 = S.get("s5x_final_touch") or {}
    if s5.get("cells"):
        A(f"\n## FINAL declared second touch — S5X verified translation pairs (n = {s5['n_pairs']})\n")
        A("| cell | SL refusal | EN refusal | SL-EN gap [CI] | gap change vs no-op | McNemar p |")
        A("|---|---|---|---|---|---|")
        for c, r in s5["cells"].items():
            A(f"| {c} | {f(r['sl'])} | {f(r['en'])} | {f(r['gap_sl_minus_en'])} {ci(r['gap_ci95'])} | "
              f"{f(r.get('gap_change_vs_noop'))} | {f(r['mcnemar']['p_exact'], 4)} |")

    ap_ = C.jload(C.RES / "audit_positive.json") if (C.RES / "audit_positive.json").exists() else {}
    if ap_:
        A("\n## Placebo audit of the SURVIVING positive claims (`audit_positive.py`, independent code path)\n")
        A("| claim | observed | placebo null (permuted) | survives? |")
        A("|---|---|---|---|")
        for lg in C.LANGS:
            r = ap_["A_P3_spearman_placebo"][lg]
            A(f"| P3 Spearman, {lg.upper()} (predictions permuted across cells) | {f(r['observed_spearman'])} | "
              f"{ci(r['placebo_null_ci95'])} | **{'yes' if r['observed_outside_null'] else 'NO'}** |")
        b = ap_["B_index_gap_language_placebo"]
        A(f"| index gap SL−EN (language permuted within item) | {b['observed_gap']:.0f} layers | "
          f"[{b['placebo_null_ci95'][0]:.0f}, {b['placebo_null_ci95'][1]:.0f}] | "
          f"**{'yes' if b['observed_gap_outside_null'] else 'NO — one grid step, not separable'}** |")
        b2 = ap_["B2_curve_separation"]
        A(f"| prefix-curve separation SL−EN (same permutation) | {f(b2['observed'], 3)} {ci(b2['bootstrap_ci95'], 3)} | "
          f"{ci(b2['placebo_null_ci95'], 3)} | **{'yes' if b2['observed_outside_null'] else 'NO'}** "
          f"(p = {f(b2['permutation_p_two_sided'], 4)}) |")
        c_ = ap_["C_band_identity_placebo"]
        A(f"| band-density separation (band label permuted across sets) | {f(c_['observed_separation'], 3)} | "
          f"{ci(c_['placebo_null_ci95'], 3)} | **{'yes' if c_['observed_outside_null'] else 'NO'}** "
          f"(p = {f(c_['permutation_p'], 4)}) |")
        A(f"\nBand-density dose-response (fraction of layers 13-24 covered -> lowest SL refusal that set reaches): " +
          ", ".join(f"{fr:.2f} {nm} {v:.3f}" for fr, nm, v in c_["min_SL_by_band_density"]) +
          f"; Spearman = {f(c_['spearman_band_density_vs_min_SL'], 3)}.\n")

    wm = S.get("write_mass_exploratory") or {}
    if "en" in wm:
        A("\n## EXPLORATORY — per-layer write mass (Part G)\n")
        A("| lang | layers to 80% of mass | entropy (nats) | band mass 1-12 / 13-24 / 25-36 / 37-48 | Spearman vs LOBO necessity |")
        A("|---|---|---|---|---|")
        for g in C.LANGS:
            r = wm[g]
            A(f"| {g.upper()} | {r['n_layers_80pct_mass']} | {f(r['entropy_nats'])} | " +
              " / ".join(f(x) for x in r["band_mass"]) + f" | {f(r.get('spearman_band_mass_vs_lobo_necessity'))} |")
        A(f"\nPrediction 'Slovene's write mass is spread over more layers': {wm.get('prediction_SL_more_spread')}.")
    (C.RES / "report_tables.md").write_text("\n".join(L) + "\n")
    print(f"wrote {C.RES / 'report_tables.md'} ({len(L)} lines)")


if __name__ == "__main__":
    main()

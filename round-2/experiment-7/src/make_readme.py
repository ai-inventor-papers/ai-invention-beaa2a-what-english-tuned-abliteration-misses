#!/usr/bin/env python3
"""Fill README_template.md -> README.md with numbers read from results/analysis.json, results/audit.json and
results/validity/judged*.json, so every number in the README is recomputed from saved results.
  uv run python make_readme.py"""
from __future__ import annotations

import json
import math
from pathlib import Path

WS = Path(__file__).resolve().parent
RES = WS / "results"


def f(x, d=3, sign=False) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def ci(c, d=3) -> str:
    if not c or c[0] is None:
        return "n/a"
    return f"[{c[0]:+.{d}f}, {c[1]:+.{d}f}]"


def main() -> None:
    A = json.loads((RES / "analysis.json").read_text())
    AU = json.loads((RES / "audit.json").read_text()) if (RES / "audit.json").exists() else {}
    R = A["R_star"]
    vg = A["validity_gate"]
    L = []
    # ---------------------------------------------------------------- panel
    L.append("## Results\n")
    sets = A["sets_scored"]
    L.append(f"**Panel.** {A['n_scored']} edits scored: " + ", ".join(f"{k} {v}" for k, v in sorted(sets.items()))
             + f". The fitted set (E0 + E1, non-collapsed) has **{A['n_fitted_noncollapsed']}** edits. The pre-registered floor "
             f"of 150 is {'**met**' if A['C2_confirmatory_floor_150_met'] else '**not met**'}. Collapsed edits: "
             + ", ".join(f"{k} {v}" for k, v in A["collapsed"].items()) + ". Devices: "
             + ", ".join(f"{k.replace('NVIDIA ', '')} {v}" for k, v in A["devices"].items()) + ".\n")
    # ---------------------------------------------------------------- judged behaviour of validity edits
    J = vg.get("edits", {})
    if J:
        L.append("**Judged behaviour of the validity edits** (half-B JBB, 64-token greedy generations; judge = "
                 f"{vg.get('judge', 'local gemma-3-12b-it, frozen gpt-4.1 rubric')}). The table gives the refusal rate on harmful "
                 "prompts, and over-refusal on their benign twins:\n")
        L.append("| edit | EN harmful refused | SL harmful refused | EN benign refused | SL benign refused |")
        L.append("| --- | --- | --- | --- | --- |")
        order = sorted(J, key=lambda e: (e != "ORIG", e != "ET_096", J[e]["en_harmful"]["rate_refused"]))
        for e in order:
            r = J[e]
            L.append(f"| {e}{' (original)' if e == 'ORIG' else ' (core edit, trial 96)' if e == 'ET_096' else ''} | "
                     f"{r['en_harmful']['refused']}/{r['en_harmful']['n']} | {r['sl_harmful']['refused']}/{r['sl_harmful']['n']} | "
                     f"{r['en_harmless']['refused']}/{r['en_harmless']['n']} | {r['sl_harmless']['refused']}/{r['sl_harmless']['n']} |")
        L.append("")
    # ---------------------------------------------------------------- gates
    pt = vg.get("per_trait", {})
    if pt:
        L.append("**Gates.** Refusal-trait validity is the edit-level Spearman of the trait (half-B harmful mean) with the judged "
                 f"refusal rate over {pt['R_seq_en']['n_edits']} validity edits (threshold 0.85 in both languages), with "
                 "item-level AUROC as the secondary gate:\n")
        L.append("| trait | Spearman EN | Spearman SL | AUROC EN | AUROC SL |")
        L.append("| --- | --- | --- | --- | --- |")
        for t in ("R_seq", "R1", "Rb"):
            L.append(f"| {t} | {f(pt[t + '_en']['spearman_edit_level'])} | {f(pt[t + '_sl']['spearman_edit_level'])} | "
                     f"{f(pt[t + '_en']['item_auroc'])} | {f(pt[t + '_sl']['item_auroc'])} |")
        L.append("")
        L.append(f"Confirmatory refusal trait R* = **{vg.get('confirmatory_refusal_trait')}**. Rb passes: {vg.get('Rb_passes')}. "
                 f"In the analysis R* = {R} (confirmatory: {A['R_star_is_confirmatory']}).")
    rel = A["reliability_gate"]
    fails = [k for k, v in rel["pass"].items() if not v]
    L.append(f"Split-half reliability (Spearman-Brown ≥ 0.6) fails for: {', '.join(fails) if fails else 'none'}. Those traits "
             "leave the confirmatory family.\n")
    # ---------------------------------------------------------------- transfer / attenuation
    ts = A["transfer_slope"]
    L.append("**How much Slovene moves per unit of English movement** (same edits, same semantic items, half B, fitted "
             "edits; OLS slope of the SL edit-level Δ on the EN Δ, with an edit-bootstrap 95% CI):\n")
    L.append("| trait | slope SL on EN | 95% CI | Pearson | mean ΔEN | mean ΔSL |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for t, v in ts.items():
        L.append(f"| {t} | {f(v['slope_SL_on_EN'])} | {ci(v.get('ci95'))} | {f(v.get('pearson'))} | {f(v.get('mean_EN'))} | {f(v.get('mean_SL'))} |")
    L.append("")
    dec = A["R_seq_decomposition_halfB"]
    if "component_harmful_lp_ref" in dec:
        a, b = dec["component_harmful_lp_ref"], dec["component_harmful_lp_comp"]
        L.append("R_seq splits into its two teacher-forced parts, on harmful items:")
        L.append(f"* log p(refusal reference) falls {f(a['mean_EN'])} nat/token in EN but only {f(a['mean_SL'])} in SL "
                 f"(slope {f(a['slope_SL_on_EN'])}, CI {ci(a['slope_ci95'])}).")
        L.append(f"* log p(compliance reference) rises almost equally: {f(b['mean_EN'], sign=True)} EN vs "
                 f"{f(b['mean_SL'], sign=True)} SL (slope {f(b['slope_SL_on_EN'])}, CI {ci(b['slope_ci95'])}).")
        L.append("")
        L.append("So the English-derived edits raise compliance continuations in both languages. They lower the probability "
                 "of the model's refusal opener only in English.\n")
    # ---------------------------------------------------------------- Gap table
    gp, gb = A["gap_point"], A["gap_bootstrap"]
    L.append(f"**Gap** = R²*(EN_A→EN_B) − R²*(EN_A→SL_B), with halves swapped and averaged. The CI is a two-level "
             f"(edit × item) bootstrap, B = {A['bootstrap']['B']}. SIMEX corrects predictor noise. B_t is the parameter "
             "partial R² on SL beyond EN.\n")
    L.append("| trait | R² EN_A→EN_B | R² EN_A→SL_B | ceil EN / SL | Gap (R²*) | 95% CI | raw Gap | SIMEX Gap | spline Gap | B_t | B perm p |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for t in gp:
        g = gp[t]
        ab = g["A->B"]
        bp = A.get("B_permutation", {}).get(t, {})
        L.append(f"| {t} | {f(ab['R2_EN'])} | {f(ab['R2_SL'])} | {f(ab['ceil_EN'], 2)} / {f(ab['ceil_SL'], 2)} | {f(g['Gap'], sign=True)} | "
                 f"{ci(gb.get(t, {}).get('Gap', {}).get('ci95'))} | {f(g['Gap_raw'], sign=True)} | "
                 f"{f(A['simex'].get(t, {}).get('Gap_simex'), sign=True)} | {f(g.get('spline_sensitivity'), sign=True)} | "
                 f"{f(g.get('B_point', {}).get('B'), sign=True)} | {f(bp.get('p_perm'))} |")
    L.append("")
    L.append("Holm-adjusted p for the damage Gaps (C2 family, one-sided bootstrap): "
             + ", ".join(f"{k} {f(v)}" for k, v in A["holm_damage"].items()) + ".\n")
    st = A["stability_strata"].get(R, {})
    L.append(f"Stability of Gap_{R}: disjoint edit halves {f(st.get('half1'), sign=True)} / {f(st.get('half2'), sign=True)}. "
             "Strata: " + ", ".join(f"{k} {f(v, sign=True)} (n={st.get('n_' + k)})" for k, v in st.items()
                                    if not k.startswith("n_") and k not in ("half1", "half2")) + ".\n")
    # ---------------------------------------------------------------- margin matched + mixed model
    mm = A["margin_matched"].get(R, {})
    mx = A.get("mixed_model", {})
    L.append(f"**Margin control.** The margin-matched Gap_{R} is {f(mm.get('Gap_margin_matched'), sign=True)} "
             f"(edit-bootstrap CI {ci(mm.get('ci95_edit_boot'))}), vs {f(mm.get('Gap_unmatched'), sign=True)} unmatched. "
             f"The margin-matched transfer slope is {f(mm.get('transfer_slope_margin_matched'))} "
             f"(CI {ci(mm.get('transfer_slope_margin_matched_ci95'))}), vs {f(mm.get('transfer_slope_unmatched'))} unmatched.")
    if "lang_terms" in mx:
        lt = mx["lang_terms"]
        L.append(f"The item × edit mixed model ({mx['formula']}; {mx['approximation']}) gives, after the "
                 f"margin × edit-strength spline interaction, sl:x = {f(lt['sl:x']['coef'], sign=True)} (SE "
                 f"{f(lt['sl:x']['se'])}) and sl = {f(lt['sl']['coef'], sign=True)} (SE {f(lt['sl']['se'])}). "
                 "sl:x < 0 means Slovene items move less per unit of English edit strength than English items with the same "
                 "original margin.\n")
    # ---------------------------------------------------------------- carrier
    CR = A["carrier"]
    L.append("**Carrier regression** on the Slovene-specific residual y_spec (5-fold ridge CV R²; 1000-draw edit bootstrap). "
             "base = {b1, b2, b3, Ω, D}; P = the removal along r_prior (SL − EN):\n")
    L.append("| trait | R² base | R² base+P | ΔR²(P given base) | 95% CI | ΔR²(b1 given P) | 95% CI | EXPLORATORY ΔR²(H given base+P) | 95% CI |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for t, c in CR.items():
        h = c.get("EXPLORATORY_H", {})
        L.append(f"| {t} | {f(c['R2_base'])} | {f(c['R2_full'])} | {f(c['dR2_P_given_base'], sign=True)} | {ci(c['dR2_P_given_base_ci95'])} | "
                 f"{f(c['dR2_b1_given_P'], sign=True)} | {ci(c['dR2_b1_given_P_ci95'])} | {f(h.get('dR2_H_given_base_P'), sign=True)} | "
                 f"{ci(h.get('dR2_H_given_base_P_ci95'))} |")
    L.append("")
    L.append("H (the language asymmetry of the removal along the targeted d_EN direction) was not pre-registered, so it is "
             "exploratory and correlational.\n")
    # ---------------------------------------------------------------- out of sample
    O = A["out_of_sample"]
    if R in O:
        o = O[R]
        L.append(f"**Out of sample (E_TPE, held out; R* = {R}).**")
        L.append(f"* F_EN (EN_A traits → SL_B): E_TPE R² {f(o['F_EN'].get('E_TPE_R2'))}; 90% conformal PI coverage "
                 f"{f(o['F_EN'].get('E_TPE_coverage'), 2)} (n = {o['F_EN'].get('E_TPE_n')}).")
        L.append(f"* F_full (+ params, D, P): E_TPE R² {f(o['F_full'].get('E_TPE_R2'))}; coverage {f(o['F_full'].get('E_TPE_coverage'), 2)}.")
        t96 = o["F_EN"].get("trial96")
        if t96:
            L.append(f"* Trial 96 (core edit): observed SL_B Δ{R} = {f(t96['observed_SL_B'])}; F_EN predicts {f(t96['pred'])} "
                     f"(excess {f(t96['excess'], sign=True)}, outside the F_EN PI: {t96['outside_PI']}); F_full predicts "
                     f"{f(o['F_full']['trial96']['pred'])} (outside: {o['F_full']['trial96']['outside_PI']}).")
        sp = O.get("support", {})
        if sp:
            L.append(f"* Support: {f(sp.get('E_TPE', {}).get('frac_beyond_fitted_p95'), 2)} of E_TPE lies beyond the fitted "
                     f"set's 95th-percentile kNN distance; trial 96 sits at the {f(sp.get('trial96', {}).get('fitted_percentile'), 2)} "
                     "quantile.")
        L.append("")
    rs = A.get("reselection")
    if rs:
        L.append(f"**Bilingual post-hoc reselection** over the {rs['n_journal_trials_scored']} scored journal trials (logistic "
                 f"calibration of judged SL refusal on the SL trait): the best trial with journal KL ≤ 1 is {rs['best_edit']}. "
                 f"Its predicted SL judged refusal is {f(rs['pred_SL_refusal'], 2)} (EN {f(rs['pred_EN_refusal'], 2)}). Any trial "
                 f"≤ 0.20 predicted SL refusal: {rs['any_trial_pred_SL_le_0.20']}. Trial 96's predicted SL refusal is "
                 f"{f(rs.get('trial96_pred_SL'), 2)}.\n")
    sf = A.get("silent_failure")
    if sf:
        jd = sf["judge_direct"]
        L.append(f"**Silent failure** (EN looks unlocked, SL still refuses): judge-direct {jd['numerator']}/{jd['denominator']}"
                 f"{' (' + jd['verdict'] + ')' if jd.get('verdict') else ''}.")
        if "calibrated_trait" in sf:
            c = sf["calibrated_trait"]
            L.append(f"Calibrated-trait version over E0 + E1: {c['numerator']}/{c['denominator']} edits with predicted EN judged "
                     f"refusal ≤ 0.20 have predicted SL refusal ≥ 0.60 (min predicted SL refusal over all fitted edits "
                     f"{f(c['min_pred_SL'], 2)}).\n")
    # ---------------------------------------------------------------- verdicts
    L.append("**Pre-registered predictions** (`protocol/frozen_predictions.json`, sha256 in `protocol/protocol_hash.txt`):\n")
    L.append("| prediction | verdict | estimate | notes |")
    L.append("| --- | --- | --- | --- |")
    V = A["verdicts"]
    est = {"P-a": f"Gap_{V['P-a'].get('trait')} {f(V['P-a'].get('Gap_R'), sign=True)} {ci(V['P-a'].get('ci95'))}",
           "P-b": f"Gap_Rb {f(V['P-b'].get('Gap_Rb'), sign=True)} {ci(V['P-b'].get('ci95'))}",
           "P-c": "; ".join(f"{t}: ΔR²(P given base) {f(d['dR2_P_given_base'], sign=True)} {ci(d['dR2_P_given_base_ci95'])}"
                            for t, d in V["P-c"].get("detail", {}).items()),
           "P-d": f"margin-matched Gap {f(V['P-d'].get('Gap_margin_matched'), sign=True)} {ci(V['P-d'].get('ci95_edit_boot'))}"}
    for k in ("P-a", "P-b", "P-c", "P-d"):
        v = V[k]
        L.append(f"| {k} | {v['verdict']}{' (' + v['exploratory_outcome'] + ')' if v.get('exploratory_outcome') else ''} | {est[k]} | "
                 f"{'; '.join(v.get('reasons', []))} |")
    L.append("")
    # ---------------------------------------------------------------- audit
    if AU:
        L.append(f"**Audit** (`audit.py`, independent numpy path): deterministic checks pass: {AU.get('deterministic_checks_pass')}. "
                 f"Placebos (language-label shuffle Gap CI covers 0; permuted edit order R² ≈ 0) pass: {AU.get('placebos_pass')}. "
                 f"The fitted count matches: {AU.get('fitted_match')}. API cost total: ${AU.get('api_cost_total_usd', 0):.3f}.\n")
    L.append("Kept artifacts (absolute paths, not re-downloadable):")
    for p in ("results/", "results/panel/item_traits.parquet", "results/panel/edit_covariates.parquet", "results/validity/",
              "references/", "directions/", "edits/", "protocol/"):
        L.append(f"* `{WS / p}`")
    L.append("")
    results = "\n".join(L)
    # ---------------------------------------------------------------- deviations
    ja = A.get("judge_agreement_orig_generations", {})
    agree = (f"{100 * ja['agreement_refused_binary']:.1f}% on refused/not-refused (κ = {ja['kappa_refused_binary']:.2f}; 6-way κ "
             f"{ja['kappa_6way']:.2f})") if ja.get("n") else "n/a"
    nfit = A["n_fitted_noncollapsed"]
    fitted = (f"**Fitted set = {nfit} ≥ 150.** The pre-registered floor is met, so C2 is confirmatory, subject to the gates."
              if nfit >= 150 else
              f"**Fitted set = {nfit} < 150.** The fitted set is E0 + E1, non-collapsed, and ended below the pre-registered "
              "floor, so C2 (and every P-a..P-d verdict) is **exploratory**, per the protocol's own rule.")
    b = A["bootstrap"]
    boot = (f"**Bootstrap B = {b['B']}** ({b['deviation']}). Permutations: {A.get('B_permutation', {}).get(R, {}).get('n_perm')}."
            if b.get("deviation") else f"**Bootstrap B = {b['B']}** as pre-registered (two-level, edits × items).")
    jr = [e for e in json.loads((WS / "edits" / "E0.json").read_text())]
    jrv = [e.get("journal_refusals") for e in jr if e.get("journal_refusals") is not None]
    t = (WS / "README_template.md").read_text()
    t = t.replace("__RESULTS__", results).replace("__JUDGE_AGREE__", agree).replace("__FITTED_DEV__", fitted)
    t = t.replace("__BOOT_DEV__", boot).replace("__JR_RANGE__", f"{min(jrv)}-{max(jrv)}" if jrv else "n/a")
    (WS / "README.md").write_text(t)
    print(f"README.md written ({len(t)} chars)")


if __name__ == "__main__":
    main()

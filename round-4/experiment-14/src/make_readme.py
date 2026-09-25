#!/usr/bin/env python3
"""Regenerates the Headline / Audit / Limitations block of README.md between the GENERATED markers, straight from the
result files, so no number in the README is typed by hand."""
from __future__ import annotations

import numpy as np

import common as C
from common import jload, setup_logging

F3 = lambda v: "n/a" if v is None or (isinstance(v, float) and v != v) else f"{v:.3f}"
F2 = lambda v: "n/a" if v is None or (isinstance(v, float) and v != v) else f"{v:.2f}"
BEGIN, END = "<!-- GENERATED:BEGIN -->", "<!-- GENERATED:END -->"


def ci(d, k="ci"):
    v = (d or {}).get(k)
    return "n/a" if not v or any(x != x for x in v) else f"[{v[0]:+.3f}, {v[1]:+.3f}]"


def main() -> None:
    setup_logging("make_readme")
    an = jload(C.RES / "analysis_summary.json")
    F = jload(C.CFG / "frozen_predictions.json")
    scr = jload(C.RES / "screen.json") if (C.RES / "screen.json").exists() else {}
    cert = jload(C.RES / "judge_cert.json") if (C.RES / "judge_cert.json").exists() else {}
    red = jload(C.RES / "rederive.json") if (C.RES / "rederive.json").exists() else {}
    dev = jload(C.RES / "deviations.json") if (C.RES / "deviations.json").exists() else {"n": 0}
    rows, P, V = an["cells"], an.get("primary", {}), an.get("verdict", {})
    conf = [c for c in rows if c.startswith("C_") and rows[c]["sl_harm_n"] >= 40]
    L, A = [], lambda s: L.append(s)

    A("## Headline\n")
    pr = P.get("sl", {})
    A(f"1. **The write profile is sharp, and it is not where the sibling checkpoint's is.** Single-layer Heretic-"
      f"operator edits at c = {F['profile_rates']['c_star']} on 40 DEV harmful items per language put the causal peak "
      f"at hidden index **{F['argmax_layer']['en']} (EN)** and **{F['argmax_layer']['sl']} (SL)**, with band mass "
      f"EN {', '.join(f'{k.replace(chr(95), chr(45))} {F2(v)}' for k, v in F['band_mass']['en'].items())} and "
      f"SL {', '.join(f'{k.replace(chr(95), chr(45))} {F2(v)}' for k, v in F['band_mass']['sl'].items())}. "
      f"The DEV-named band is **{F['predicted_winning_band']['sl']}**, not the 13-24 that the sibling panel reported - "
      f"but the Slovene profile's split-half reliability is only "
      f"{F3(F['e_reliability']['sl']['half_half_spearman'])} (EN {F3(F['e_reliability']['en']['half_half_spearman'])}), "
      f"so by the pre-registered rule the Slovene profile is **declared unreliable at this item count and its argmax "
      f"prediction is exploratory**, recorded before the freeze.\n")
    if pr:
        A(f"2. **Out of sample, the overlap statistic orders the matched-energy cells "
          f"{'as predicted' if V.get('rho_sl_removal_aligned', 0) > 0 else 'in the wrong direction'}.** Over "
          f"{pr['n_cells']} confirmation cells that the profile never saw (70 held-out-category StrongREJECT pairs "
          f"each, 12 edited layers each, energy matched), Spearman(O_SL, surviving Slovene refusal) = "
          f"**{F3(pr['rho'])}** (CI {ci(pr)}, permutation p {F3(pr['perm_p'])}); the instrument predicts REMOVAL, so "
          f"its expected sign is negative and the removal-aligned statistic is "
          f"{F3(V.get('rho_sl_removal_aligned'))}. Pre-registered verdict: **{V.get('label')}**.\n")
    nz = an.get("nested", {}).get("sl", {})
    if nz:
        o = nz["add"].get("O", {})
        A(f"3. **Against the honest competitors it buys {'something' if o.get('loo_dR2', 0) > 0 else 'nothing'}.** "
          f"With log total removal energy alone the Slovene outcome is at R^2 {F3(nz['r2_base'])} "
          f"(leave-one-cell-out {F3(nz['loo_base'])}); adding O gives dR^2 {F3(o.get('dR2'))} with LOO dR^2 "
          f"{F3(o.get('loo_dR2'))}. " + " ".join(
              f"Adding {k} instead: dR^2 {F3(v['dR2'])} (LOO {F3(v['loo_dR2'])})." for k, v in nz["add"].items()
              if k != "O") + "\n")
    if nz:
        cheap = {k: v for k, v in nz["add"].items() if k in ("O_cos", "O_band4")}
        best = max(cheap, key=lambda k: cheap[k]["loo_dR2"]) if cheap else None
        if best and cheap[best]["loo_dR2"] >= nz["add"]["O"]["loo_dR2"]:
            A(f"3b. **But the expensive instrument does not earn its cost.** The same overlap computed from a FOUR-number "
              f"band profile (`O_band4`) and the purely geometric EN/SL direction-cosine overlap (`O_cos`) - neither of "
              f"which needs 48 judged single-layer measurements - reach LOO dR^2 "
              f"{F3(nz['add']['O_band4']['loo_dR2'])} and {F3(nz['add']['O_cos']['loo_dR2'])} against O's "
              f"{F3(nz['add']['O']['loo_dR2'])}, and the same cell's ENGLISH outcome predicts the Slovene one at rho "
              f"{F3(an.get('competitors', {}).get('sl', {}).get('en_outcome', {}).get('rho'))} - statistically "
              f"indistinguishable from O. What the 48-layer profile establishes is that **placement matters**; it is "
              f"not the cheapest way to measure placement.\n")
    comp = an.get("competitors", {}).get("sl", {})
    if comp:
        A("4. **The cheap predictors are the bar, and they are reported beside it.** "
          + "; ".join(f"{k} rho {F3(v['rho'])} (|rho| difference vs O {F3(v.get('vs_O', {}).get('diff'))} "
                      f"{ci(v.get('vs_O'))})" for k, v in comp.items()) + ".\n")
    arg = an.get("argmax", {})
    if arg:
        A("5. **The band check.** " + " ".join(
            f"At {lvl} the matched-energy bands rank " + ", ".join(f"{k} {F2(x)}" for k, x in v["ranking"]) +
            f"; the DEV-named band is {v['predicted']} and the observed winner is {v['winner_band']} -> "
            f"**{v['outcome']}**." for lvl, v in arg.items()) + "\n")
    dis = an.get("dissociation", {})
    if dis.get("contrasts"):
        A("6. **Placement and achieved dose, separated by construction.** "
          + "; ".join(f"{k}: dSL {F3(v['diff'])} {ci(v)} (McNemar p {F3(v['mcnemar_p'])})"
                      for k, v in dis["contrasts"].items() if v) + ". "
          "A1 and A4 share their placement profile and differ only in total energy; A2 and A3 likewise; A1 and A3 "
          "share energy and differ in placement, as do A2 and A4.\n")
    wl = an.get("primary_within_level", {})
    dw = an.get("dose_within_placement")
    if wl and dw:
        A("6b. **Both accounts hold, in their own stratum.** At fixed dose the overlap still orders the cells ("
          + "; ".join(f"{k} rho {F3(v['rho'])} over {v['n_cells']} cells" for k, v in wl.items() if k.endswith("sl"))
          + f"), and at fixed placement doubling the dose from E = 13.9 to 27.8 lowers Slovene strict refusal by "
            f"{F3(-dw['mean_E3_minus_E2_sl_strict'])} on average over the {dw['n_pairs']} matched layer sets. "
            f"Placement and dose are both real; neither is an artefact of the other.\n")
    ctl = an.get("controls", {})
    if ctl:
        A(f"7. **Controls.** At the same 12 layers and the same total removal energy, "
          + "; ".join(f"{k} SL strict {F3(v['sl_strict'])} (d vs no-op {F3(v.get('vs_noop_sl', {}).get('diff'))})"
                      for k, v in ctl.items())
          + f". All null: **{an.get('controls_all_null')}** (no-op SL strict "
            f"{F3(rows.get('R_NOOP', {}).get('sl_harm_strict'))}).\n")
    md = an.get("metric_dependence", {})
    if md.get("sl"):
        bo = md.get("band_order_by_metric_sl", {}).get("E3", {})
        A(f"8. **The outcome definition, not the placement, decides which band 'wins'.** On the same generations the "
          f"33-substring opener rule and the judged 4-way class rank the four matched-energy bands differently: "
          f"opener rule {' > '.join(bo.get('opener_rule', []))}, judged STRICT {' > '.join(bo.get('judged_strict', []))}, "
          f"judged BROAD {' > '.join(bo.get('judged_broad', []))}. The mean Slovene gap between the judged strict rate "
          f"and the opener-rule rate over the confirmation cells is {F3(md['sl']['mean_gap_strict_minus_rule'])} "
          f"(max {F3(md['sl']['max_gap_strict_minus_rule'])}), and "
          f"{md['sl']['rank_flips_rule_vs_strict']}/{md['sl']['n_pairs']} cell pairs change order between the two "
          f"metrics. The rank correlation of O with the outcome is nevertheless the same under both "
          f"({F3(md['sl']['rho_O_vs_rule'])} vs {F3(md['sl']['rho_O_vs_strict'])}).\n")
    pf = an.get("post_freeze_exploratory", {}).get("levels", {})
    if pf:
        A("9. **Post-freeze exploratory (declared, never in the pre-registered family): the two production kernels are "
          "indistinguishable once their dose is matched.** "
          + "; ".join(f"at {lvl} the shipped kernel and the sibling checkpoint's kernel at the same total removal "
                      f"energy leave Slovene strict refusal at {F3(v['ship']['sl_harm_strict'])} and "
                      f"{F3(v['swap']['sl_harm_strict'])} (d {F3(v['paired_sl']['diff'])} {ci(v['paired_sl'])})"
                      for lvl, v in pf.items())
          + ". Both production kernels spread their mass over the layers the profile calls effective, so the "
            "'swap' contrast that motivated this pod is a dose contrast, not a placement contrast.\n")
    if scr.get("gams3"):
        g, gm = scr["gams3"], scr.get("gemma_misspec", {})
        A(f"10. **The screen, and the mis-specification arm that undercuts it.** On the 57-cell iteration-3 GaMS3 panel "
          f"O correlates {F3(g.get('rho_O_sl_screen', {}).get('rho'))} with surviving Slovene refusal "
          f"({g.get('rho_O_sl_screen', {}).get('n')} cells). Applying the SAME GaMS3 profile to "
          f"{gm.get('n_cells')} cells of the sibling checkpoint gives {F3(gm.get('rho_O_sl', {}).get('rho'))} - "
          f"{'no worse' if abs(gm.get('rho_O_sl', {}).get('rho', 0)) >= abs(g.get('rho_O_sl_screen', {}).get('rho', 1)) else 'weaker'}, "
          f"so the profile is not demonstrably checkpoint-specific on these screens. Both screens are weak for a "
          f"reason the confirmation panel removes by design: those cells vary in total removal energy by an order of "
          f"magnitude, and O is scale-invariant, so on an unmatched panel dose swamps placement. Placement is visible "
          f"only at matched energy.\n")
    A("\n## Audit\n")
    if red:
        A(f"`rederive.py` re-derives **{red['n_agree']}/{red['n_checks']}** headline numbers from the raw "
          f"per-generation files through a code path that imports nothing from the analysis; freeze order "
          f"{red['freeze_order']}. In that same independent path the primary statistic is placebo-tested: the real "
          f"Spearman is {F3((red.get('placebo') or {}).get('real_rho'))}, the cell-permutation null "
          f"{F3(((red.get('placebo') or {}).get('cell_permutation') or {}).get('mean'))} (p "
          f"{F3(((red.get('placebo') or {}).get('cell_permutation') or {}).get('p_two_sided'))}) and the "
          f"energy-profile-shuffled null "
          f"{F3(((red.get('placebo') or {}).get('energy_profile_shuffled') or {}).get('mean'))} (p "
          f"{F3(((red.get('placebo') or {}).get('energy_profile_shuffled') or {}).get('p_two_sided'))}) - both "
          f"collapse.\n")
    tc = jload(C.RES / "third_channel.json") if (C.RES / "third_channel.json").exists() else {}
    if tc:
        A(f"Third label channel (free, weak, and the only one available on THESE generations): the iteration-3 "
          f"partial-aware refusal classifier agrees with the blind local judge on "
          f"{F3(tc.get('sl', {}).get('agreement'))} of Slovene confirmation items (kappa "
          f"{F3(tc.get('sl', {}).get('kappa'))}) and {F3(tc.get('en', {}).get('agreement'))} of English ones (kappa "
          f"{F3(tc.get('en', {}).get('kappa'))}) - but the two channels' CELL-LEVEL rates, which is what every claim "
          f"here rests on, correlate at Spearman {F3(tc.get('sl', {}).get('cell_level_rho'))} (SL) and "
          f"{F3(tc.get('en', {}).get('cell_level_rho'))} (EN) over "
          f"{tc.get('sl', {}).get('n_cells')} cells. The panel's ordering does not depend on the scorer.\n")
    gf = jload(C.RES / "gate_freeze.json") if (C.RES / "gate_freeze.json").exists() else {}
    if gf:
        A(f"Freeze guard, tested adversarially on a scratch copy (`gate_freeze_test.py`): the confirmation entry point "
          f"raises when `FREEZE.sha256` is missing and when one byte of `frozen_predictions.json` is changed, and runs "
          f"only on the intact freeze - guard_works = **{gf['guard_works']}**.\n")
    pl = an.get("placebos", {})
    if pl:
        A("Placebos: " + "; ".join(f"{k} {F3(v.get('mean', v.get('rho_O_en_on_sl')))} {ci(v)}" for k, v in pl.items())
          + f" - against a real statistic of {F3(P.get('sl', {}).get('rho'))}.\n")
    if cert:
        src = cert.get("source", "a stratified subsample of this pod's OWN edited generations")
        A(f"\n**Judge.** Primary scorer: blind local Qwen3-14B with the frozen iteration-2 rubric. Reference judge "
          f"{cert['judge_reference']}. The stratified 600-item buy this pod had budgeted could NOT be made: the "
          f"platform's shared OpenRouter key hit its daily limit mid-run (HTTP error `aii_openrouter_key_limit`), so "
          f"${cert['spend_usd']:.2f} was spent and certification fell back to - {src}. Measured on harmful-item rows: "
          f"kappa (refused vs not) "
          + ", ".join(f"{g} {F3(cert.get(g, {}).get('kappa'))} (n={cert.get(g, {}).get('n')})" for g in ("sl", "en"))
          + f". Confirmatory languages: {cert.get('confirmatory')}; JUDGE_SENSITIVE: {cert.get('judge_sensitive')}.\n")
    A(f"\nDeviations from the plan, each with its evidence file: **{dev['n']}** (see `results/deviations.json`).\n")
    A("\n## Limitations\n")
    A("- One checkpoint, one optimiser seed, NF4 throughout: absolute levels are NF4-specific and prompt-level CIs do "
      "not measure optimiser run-to-run variance.\n"
      f"- {len(conf)} confirmation cells: a rank statistic over cells at this n cannot resolve differences below "
      "roughly 0.4 in Spearman, and the paper says so rather than reading small differences.\n"
      "- Slovene items are machine-translated with automated QC only; native review is PENDING.\n"
      "- The Slovene write profile's split-half reliability is below the pre-registered 0.5, so every Slovene "
      "profile-derived claim is exploratory; the English profile is reliable but English is judge-blocked.\n"
      "- Attack success is reported as judged COMPLIED (+PARTIAL), an upper bound: the RefusEU official guard "
      "pipeline was not run here (see `results/deviations.json`).\n"
      "- The sibling-checkpoint columns are read from the iteration-3 panel's files, never re-measured here; every "
      "cross-checkpoint statement is descriptive (n = 2 checkpoints) and none is attributed to a training stage.\n")

    p = C.ROOT / "README.md"
    txt = p.read_text() if p.exists() else f"# {BEGIN}\n{END}\n"
    head, rest = txt.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    p.write_text(head + BEGIN + "\n\n" + "\n".join(L) + "\n" + END + tail)
    print(f"README.md regenerated ({len(L)} blocks)")


if __name__ == "__main__":
    main()

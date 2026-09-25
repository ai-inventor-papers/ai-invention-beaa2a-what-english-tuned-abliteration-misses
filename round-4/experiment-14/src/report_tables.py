#!/usr/bin/env python3
"""results/report_tables.md - every table the write-up needs, generated from results/analysis_summary.json,
results/screen.json, results/judge_cert.json and configs/frozen_predictions.json. Each caption names the FILE that
produced it, so nothing in the paper is typed by hand."""
from __future__ import annotations

import numpy as np

import common as C
from common import jload, setup_logging

F3 = lambda v: "n/a" if v is None or (isinstance(v, float) and v != v) else f"{v:.3f}"
F2 = lambda v: "n/a" if v is None or (isinstance(v, float) and v != v) else f"{v:.2f}"


def ci(d, k="ci"):
    v = d.get(k)
    return "n/a" if not v or any(x != x for x in v) else f"[{v[0]:+.3f}, {v[1]:+.3f}]"


def main() -> None:
    setup_logging("report_tables")
    an = jload(C.RES / "analysis_summary.json")
    F = jload(C.CFG / "frozen_predictions.json")
    scr = jload(C.RES / "screen.json") if (C.RES / "screen.json").exists() else {}
    cert = jload(C.RES / "judge_cert.json") if (C.RES / "judge_cert.json").exists() else {}
    rows = an["cells"]
    L = []
    A = L.append
    A("# Report tables\n")
    A(f"Produced by `report_tables.py` from `results/analysis_summary.json` (frozen predictions declared "
      f"{F['declared_utc']}).\n")

    # ---------------------------------------------------------------- 1. the DEV write profile
    A("\n## Table 1 - the DEV causal write profile e_L(h) (source: `configs/frozen_predictions.json`)\n")
    sel = F["profile_rates"].get("selection", {})
    A(f"Single-layer Heretic-operator edits at c = {F['profile_rates']['c_star']} "
      f"(width {F['profile_rates'].get('profile_width', 1)}), 40 DEV harmful items per language. "
      f"Strength chosen on DEV before the freeze by the opener-rule pilot ({sel.get('rule', '')}).\n")
    A("\n| band | sum e_EN | sum e_SL | argmax layer EN | argmax layer SL |")
    A("|---|---|---|---|---|")
    for b in ["1_12", "13_24", "25_36", "37_48"]:
        A(f"| {b.replace('_', '-')} | {F3(F['band_mass']['en'][b])} | {F3(F['band_mass']['sl'][b])} | "
          f"{F['argmax_layer']['en'] if b == list(F['band_mass']['en'])[0] else ''} | "
          f"{F['argmax_layer']['sl'] if b == list(F['band_mass']['sl'])[0] else ''} |")
    A(f"\nPredicted winning band: EN **{F['predicted_winning_band']['en']}**, "
      f"SL **{F['predicted_winning_band']['sl']}**; the sibling checkpoint's reported effective band is 13-24, so the "
      f"cross-model prediction 'differs' = **{F['cross_model_prediction']['differs']}**. "
      f"Split-half reliability (Spearman over the 48 layers): "
      + ", ".join(f"{g} {F3(F['e_reliability'][g]['half_half_spearman'])}" for g in ("en", "sl")) + ".\n")
    A("\n| h | e_EN(h) | e_SL(h) | h | e_EN(h) | e_SL(h) |")
    A("|---|---|---|---|---|---|")
    for h in range(1, 25):
        A(f"| {h} | {F3(F['e_en'][h])} | {F3(F['e_sl'][h])} | {h+24} | {F3(F['e_en'][h+24])} | {F3(F['e_sl'][h+24])} |")

    # ---------------------------------------------------------------- 2. confirmation cells
    A("\n## Table 2 - the frozen confirmation panel (source: `results/analysis_summary.json` -> `cells`)\n")
    A("Every cell edits exactly 12 layers at a matched total removal energy; outcomes are judged 4-way on the 70 "
      "held-out-category StrongREJECT harmful pairs. STRICT = REFUSED, BROAD = REFUSED+PARTIAL, INVALID never folded; "
      "SL COMPLIED is the judged compliance rate, an UPPER BOUND on guard-scored attack success (the RefusEU official "
      "guard pipeline was not run here - see results/deviations.json).\n")
    A("\n| cell | layers | E | dev% | O_SL | SL strict | SL broad | SL PART | SL COMPLIED | SL INVALID | SL lang-ok | EN strict | FLORES dNLL SL | KL SL |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in sorted(rows):
        r = rows[c]
        if not c.startswith("C_"):
            continue
        A(f"| {c} | {r['n_layers']} | {F2(r['E'])} | {F2((r['E_rel_dev'] or 0)*100)} | {F3(r['O_sl'])} | "
          f"{F3(r['sl_harm_strict'])} | {F3(r['sl_harm_broad'])} | {F3(r['sl_harm_partial'])} | "
          f"{F3(r['sl_harm_complied'])} | {F3(r['sl_harm_invalid'])} | {F3(r['sl_harm_lid_ok'])} | "
          f"{F3(r['en_harm_strict'])} | {F3(r['flores_sl'])} | {F3(r['kl_sl'])} |")

    # ---------------------------------------------------------------- 3. the primary statistic and its competitors
    A("\n## Table 3 - the instrument against its competitors (source: `results/analysis_summary.json`)\n")
    A("Spearman over the confirmation cells between each predictor and the cell's strict Slovene refusal, with an "
      "item-cluster bootstrap CI, a permutation null over cells, and the paired bootstrap difference against O.\n")
    A("\n| predictor | rho (SL) | 95% CI | permutation p | rho(O) - rho(this) | CI | excludes 0 |")
    A("|---|---|---|---|---|---|---|")
    p = an.get("primary", {}).get("sl")
    if p:
        A(f"| **O (the frozen overlap)** | **{F3(p['rho'])}** | {ci(p)} | {F3(p['perm_p'])} | - | - | - |")
    for k, v in an.get("competitors", {}).get("sl", {}).items():
        d = v.get("vs_O", {})
        A(f"| {k} | {F3(v['rho'])} | {ci(v)} | {F3(v.get('perm_p'))} | {F3(d.get('diff'))} | {ci(d)} | "
          f"{d.get('excludes_zero')} |")
    wl = an.get("primary_within_level", {})
    if wl:
        A("\nWithin each energy level separately (a placement account must order the cells AT FIXED dose), and the "
          "mirror statistic for dose at fixed placement (the same layer set at 13.9 vs 27.8):\n")
        A("\n| stratum | n cells | rho(O, strict) | p |")
        A("|---|---|---|---|")
        for k, v in wl.items():
            A(f"| {k} | {v['n_cells']} | {F3(v['rho'])} | {F3(v['p'])} |")
        dw = an.get("dose_within_placement")
        if dw:
            A(f"\nDose at fixed placement: mean(SL strict at E3 - SL strict at E2) over the "
              f"{dw['n_pairs']} matched layer sets = **{F3(dw['mean_E3_minus_E2_sl_strict'])}** "
              f"(per set: {', '.join(f'{k} {F2(v)}' for k, v in dw['per_pair'].items())}).\n")
    nz = an.get("nested", {}).get("sl")
    if nz:
        A(f"\nNested R^2 on the same cells: base [log E] R^2 = {F3(nz['r2_base'])} "
          f"(leave-one-cell-out {F3(nz['loo_base'])}); adding each predictor:\n")
        A("\n| added predictor | R^2 | dR^2 | LOO R^2 | LOO dR^2 |")
        A("|---|---|---|---|---|")
        for k, v in nz["add"].items():
            A(f"| {k} | {F3(v['r2'])} | {F3(v['dR2'])} | {F3(v['loo_r2'])} | {F3(v['loo_dR2'])} |")
    pb = an.get("pooled_baselines")
    if pb:
        A("\nPooled cell x language rows (where the two one-forward-pass baselines of art_kfCCWf7o8eJ9 can vary):\n")
        A("\n| predictor | rho | p | n rows |")
        A("|---|---|---|---|")
        for k, v in pb.items():
            A(f"| {k} | {F3(v['rho'])} | {F3(v['p'])} | {v['n']} |")

    # ---------------------------------------------------------------- 4. the argmax prediction
    A("\n## Table 4 - did the DEV-named band win on held-out harm categories? (source: `analysis_summary.json` -> `argmax`)\n")
    A("\n| energy level | ranking of the four matched-energy bands (SL strict, lowest = most refusal removed) | winner | predicted | outcome |")
    A("|---|---|---|---|---|")
    for lvl, v in an.get("argmax", {}).items():
        rank = ", ".join(f"{k} {F2(x)}" for k, x in v["ranking"])
        A(f"| {lvl} | {rank} | {v['winner_band']} | {v['predicted']} | **{v['outcome']}** |")

    # ---------------------------------------------------------------- 5. controls
    A("\n## Table 5 - controls at matched energy (source: `analysis_summary.json` -> `controls`)\n")
    A("\n| control | E | dev% | SL strict | d vs no-op | 95% CI | INVALID | FLORES dNLL SL | null? |")
    A("|---|---|---|---|---|---|---|---|---|")
    for c, v in an.get("controls", {}).items():
        d = v.get("vs_noop_sl", {})
        A(f"| {c} | {F2(v['E'])} | {F2((v['E_rel_dev'] or 0)*100)} | {F3(v['sl_strict'])} | {F3(d.get('diff'))} | "
          f"{ci(d)} | {F3(v['sl_invalid'])} | {F3(v['flores_sl'])} | {v.get('null')} |")
    noop = rows.get("R_NOOP")
    if noop:
        A(f"\nNo-op reference on the same items: SL strict {F3(noop['sl_harm_strict'])}, "
          f"EN strict {F3(noop['en_harm_strict'])}, SL INVALID {F3(noop['sl_harm_invalid'])}.\n")

    # ---------------------------------------------------------------- 6. the dissociation ladder
    A("\n## Table 6 - placement versus achieved dose (source: `analysis_summary.json` -> `dissociation`)\n")
    A("\n| arm | edit | E | O_SL | SL strict | EN strict | SL INVALID | FLORES dNLL SL |")
    A("|---|---|---|---|---|---|---|---|")
    names = {"A1": "shipped GaMS3 edit (trial 88)", "A2": "sibling kernel (Gemma trial 96), as-is",
             "A3": "sibling kernel rescaled to A1's energy", "A4": "shipped edit rescaled to A2's energy"}
    for t in ("A1", "A2", "A3", "A4"):
        v = an.get("dissociation", {}).get(t)
        if v:
            A(f"| {t} | {names[t]} | {F2(v['E'])} | {F3(v['O_sl'])} | {F3(v['sl_strict'])} | {F3(v['en_strict'])} | "
              f"{F3(v['sl_invalid'])} | {F3(v['flores_sl'])} |")
    A("\n| contrast | d SL strict | 95% CI | McNemar p |")
    A("|---|---|---|---|")
    for k, v in (an.get("dissociation", {}).get("contrasts") or {}).items():
        if v:
            A(f"| {k} | {F3(v['diff'])} | {ci(v)} | {F3(v['mcnemar_p'])} |")

    pf = an.get("post_freeze_exploratory", {}).get("levels", {})
    if pf:
        A("\n### Table 6b - POST-FREEZE EXPLORATORY: the two production kernels at matched energy\n")
        A("Declared after the freeze (the A1-A4 ladder sits at the refusal floor in both languages); never part of the "
          "pre-registered family.\n")
        A("\n| energy level | arm | E | O_SL | SL strict | EN strict | d SL (ship - swap) | 95% CI | McNemar p |")
        A("|---|---|---|---|---|---|---|---|---|")
        for lvl, v in pf.items():
            d = v["paired_sl"]
            A(f"| {lvl} | shipped kernel | {F2(v['ship']['E'])} | {F3(v['ship']['O_sl'])} | "
              f"{F3(v['ship']['sl_harm_strict'])} | {F3(v['ship']['en_harm_strict'])} | {F3(d['diff'])} | {ci(d)} | "
              f"{F3(d['mcnemar_p'])} |")
            A(f"| {lvl} | sibling kernel | {F2(v['swap']['E'])} | {F3(v['swap']['O_sl'])} | "
              f"{F3(v['swap']['sl_harm_strict'])} | {F3(v['swap']['en_harm_strict'])} | | | |")

    # ---------------------------------------------------------------- 7. screen
    if scr.get("gams3"):
        A("\n## Table 7 - the screen (source: `results/screen.json`; SCREEN ONLY, no headline rests on it)\n")
        A("\n| panel | cells | rho(O, strict) EN | rho(O, strict) SL |")
        A("|---|---|---|---|")
        g = scr["gams3"]
        for split in ("screen", "confirm"):
            if f"rho_O_sl_{split}" in g:
                A(f"| GaMS3 iteration-3 panel ({split} split) | {g[f'rho_O_sl_{split}']['n']} | "
                  f"{F3(g.get(f'rho_O_en_{split}', {}).get('rho'))} | {F3(g[f'rho_O_sl_{split}']['rho'])} |")
        gm = scr.get("gemma_misspec", {})
        if "rho_O_sl" in gm:
            A(f"| sibling checkpoint, GaMS3 profile (MIS-SPECIFICATION arm) | {gm['n_cells']} | "
              f"{F3(gm['rho_O_en']['rho'])} | {F3(gm['rho_O_sl']['rho'])} |")

    # ---------------------------------------------------------------- 8. judge
    if cert:
        A("\n## Table 8 - judge certification within EDITED arms (source: `results/judge_cert.json`)\n")
        A(f"Reference judge {cert['judge_reference']} on a stratified subsample of this pod's own generations; "
          f"spend ${cert['spend_usd']:.2f} of a ${cert['hard_cap']:.2f} cap.\n")
        if cert.get("source"):
            A(f"**{cert['source']}**\n")
        A("\n| language | n | kappa (refused vs not, harmful rows) | 4-way kappa | Se | Sp | gate |")
        A("|---|---|---|---|---|---|---|")
        for g in ("en", "sl", "all"):
            v = cert.get(g, {})
            if "kappa" in v:
                A(f"| {g} | {v.get('n')} | {F3(v.get('kappa'))} | {F3(v.get('kappa_4way'))} | {F3(v.get('se'))} | "
                  f"{F3(v.get('sp'))} | {'PASS' if v.get('gate_pass') else 'MISS -> JUDGE_SENSITIVE'} |")

    md = an.get("metric_dependence", {})
    if md.get("sl"):
        A("\n## Table 8b - the outcome definition moves the answer (source: `analysis_summary.json` -> `metric_dependence`)\n")
        A("\n| language | rho(O, opener-rule refusal) | rho(O, judged STRICT) | rho(O, judged BROAD) | mean(judged strict - opener rule) | max gap | rank flips / pairs |")
        A("|---|---|---|---|---|---|---|")
        for g in ("en", "sl"):
            v = md.get(g, {})
            if v:
                A(f"| {g} | {F3(v['rho_O_vs_rule'])} | {F3(v['rho_O_vs_strict'])} | {F3(v['rho_O_vs_broad'])} | "
                  f"{F3(v['mean_gap_strict_minus_rule'])} | {F3(v['max_gap_strict_minus_rule'])} | "
                  f"{v['rank_flips_rule_vs_strict']}/{v['n_pairs']} |")
        A("\nBand ordering (best first) under each metric, Slovene:\n")
        A("\n| energy level | opener rule | judged STRICT | judged BROAD |")
        A("|---|---|---|---|")
        for lvl, v in md.get("band_order_by_metric_sl", {}).items():
            A(f"| {lvl} | {' > '.join(v['opener_rule'])} | {' > '.join(v['judged_strict'])} | "
              f"{' > '.join(v['judged_broad'])} |")

    tc = jload(C.RES / "third_channel.json") if (C.RES / "third_channel.json").exists() else {}
    if tc:
        A("\n### Table 8c - the free third label channel (source: `results/third_channel.json`)\n")
        A(f"{tc['note']}\n")
        A("\n| language | n items | agreement with the local judge | kappa | cells | cell-level Spearman of the two rates |")
        A("|---|---|---|---|---|---|")
        for g in ("en", "sl", "all"):
            v = tc.get(g, {})
            if v:
                A(f"| {g} | {v['n']} | {F3(v['agreement'])} | {F3(v['kappa'])} | {v.get('n_cells')} | "
                  f"{F3(v.get('cell_level_rho'))} |")

    # ---------------------------------------------------------------- 9. placebos, Holm, verdict
    A("\n## Table 9 - placebos, multiplicity and the pre-registered verdict\n")
    A("\n| placebo | value | 95% CI | real effect |")
    A("|---|---|---|---|")
    for k, v in an.get("placebos", {}).items():
        val = v.get("mean", v.get("rho_O_en_on_sl"))
        A(f"| {k} | {F3(val)} | {ci(v)} | {F3(v.get('real'))} |")
    if an.get("holm"):
        A("\n| pre-registered test | Holm-adjusted p |")
        A("|---|---|")
        for k, v in an["holm"].items():
            A(f"| {k} | {F3(v)} |")
    v = an.get("verdict", {})
    A(f"\n**Verdict ({v.get('label')})**: rho_SL {F3(v.get('rho_sl'))}, dR^2(O | log E) {F3(v.get('dR2_O'))} "
      f"(LOO {F3(v.get('loo_dR2_O'))}), argmax outcome {v.get('argmax_outcome')}, controls all null "
      f"{v.get('controls_all_null')}, loses to {v.get('loses_to')}.\n")

    (C.RES / "report_tables.md").write_text("\n".join(L))
    print(f"wrote {C.RES / 'report_tables.md'} ({len(L)} lines)")


if __name__ == "__main__":
    main()

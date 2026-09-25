#!/usr/bin/env python3
"""results/report_tables.md: every table the README quotes, rendered from results/analysis.json + cell_table.csv."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import common as C


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "-"
    return f"{x:+.{d}f}" if isinstance(x, float) and x < 0 else f"{x:.{d}f}"


def ci(v, d=2):
    return "-" if v is None or any(not np.isfinite(x) for x in v) else f"[{v[0]:.{d}f}, {v[1]:.{d}f}]"


def main() -> None:
    A = json.loads((C.RES / "analysis.json").read_text())
    FP = json.loads((C.CFG / "frozen_predictions.json").read_text())
    rt = pd.read_csv(C.RES / "cell_table.csv")
    L = []
    L.append(f"# Report tables\n\nVerdict (frozen rule): **{A['verdict']['verdict']}**\n")
    L.append("## Profile (DEV, frozen)\n\n| lang | no-op refusal | split-half judged | split-half TF | argmax h |\n|---|---|---|---|---|")
    for g in C.LANGS:
        L.append(f"| {g} | {f(FP['judged_profile'][g]['noop_refusal'])} | {f(FP['judged_profile'][g]['split_half_r'], 2)} | "
                 f"{f(FP['tf_profile'][g]['split_half_r'], 2)} | {FP['argmax_band_prediction'][g]['argmax_h']} |")
    for name, blk in (("SCREEN (exp9 cells, S3 JBB half B)", A["screen"]), ("CONFIRMATION (frozen CONF items)", None)):
        L.append(f"\n## {name}: Spearman with residual refusal (raw; predicted sign negative)\n")
        L.append("| lang | n | O | B_site | log E | count | span | cos | log KL | dR2_O | LOO dR2_O | dR2_O over +logKL |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for g in C.LANGS:
            b = blk[g] if blk is not None else A["confirm"]["per_language"][g]
            s = b["spearman"]
            L.append(f"| {g} | {b['n']} | {f(s[f'O_{g}'], 2)} | {f(s[f'B_site_{g}'], 2)} | {f(s['log_energy'], 2)} | {f(s['layer_count'], 2)} | "
                     f"{f(s['depth_span'], 2)} | {f(s['en_sl_cosine'], 2)} | {f(s.get('log_kl'), 2)} | {f(b['dR2_O'])} | {f(b['LOO_dR2_O'])} | "
                     f"{f(b.get('dR2_O_over_nuis_plus_logKL'))} |")
    L.append("\n## Confirmation race (paired item bootstrap; aligned: > 0 means O predicts better)\n")
    L.append("| lang | rho O [CI] | rho B_site [CI] | aligned O - B_site [CI] | placebo perm 95% | shuffled-e 95% |\n|---|---|---|---|---|---|")
    for g in C.LANGS:
        b = A["confirm"]["per_language"][g]
        L.append(f"| {g} | {f(b['spearman'][f'O_{g}'], 2)} {ci(b['item_boot']['spearman_O_ci'])} | {f(b['spearman'][f'B_site_{g}'], 2)} "
                 f"{ci(b['item_boot']['spearman_Bsite_ci'])} | {f(b['item_boot']['aligned_O_minus_Bsite_point'], 2)} "
                 f"{ci(b['item_boot']['aligned_O_minus_Bsite_ci'])} | {ci(b['placebo']['cell_label_perm_95'])} | {ci(b['placebo']['energy_shuffled_e_95'])} |")
    pr = A["confirm"]["pooled_race"]
    L.append(f"\nPooled (language x condition, n = {pr['n_rows']}): rho O {f(pr['spearman']['O'], 2)}, unedited refusal "
             f"{f(pr['spearman']['unedited_refusal'], 2)}, single-site transfer {f(pr['spearman']['single_site_transfer'], 2)}, "
             f"B_site {f(pr['spearman']['B_site'], 2)}; aligned O minus baseline CIs: "
             + "; ".join(f"{k} {ci(v)}" for k, v in pr["O_minus_baseline_ci"].items()))
    L.append("\n## Matched groups (identical energy and layer count): residual refusal\n")
    L.append("| group | k | E | hi-O cell | lo-O cell | EN hi / lo | EN diff [CI] | SL hi / lo | SL diff [CI] | SL Holm p |\n|---|---|---|---|---|---|---|---|---|---|")
    for G, r in A["confirm"]["matched"]["groups"].items():
        e, s = r.get("en") or {}, r.get("sl") or {}
        L.append(f"| {G} | {r['k']} | {r['E']:.1f} | {r['hi'][3:]} | {r['lo'][3:]} | {f(e.get('res_hi'), 2)} / {f(e.get('res_lo'), 2)} | "
                 f"{f(e.get('diff_hi_minus_lo'), 2)} {ci(e.get('ci'))} | {f(s.get('res_hi'), 2)} / {f(s.get('res_lo'), 2)} | "
                 f"{f(s.get('diff_hi_minus_lo'), 2)} {ci(s.get('ci'))} | {f(s.get('holm_p'), 4)} |")
    for g in C.LANGS:
        p = A["confirm"]["matched"].get(f"pooled_hi_minus_lo_{g}")
        if p:
            L.append(f"\nPooled {g.upper()}: {f(p['mean'], 3)} {ci(p['ci'], 3)} over {p['n_groups']} groups; prediction holds in "
                     f"{p['groups_prediction_holds']}/{p['n_groups']}.")
    L.append("\n## Controls (at the high-O member's layers)\n\n| control | E matched | collateral matched | EN no-op / real / control | SL no-op / real / control |\n|---|---|---|---|---|")
    for c, r in A["confirm"]["matched"]["controls"].items():
        e, s = r.get("en", {}), r.get("sl", {})
        L.append(f"| {c[3:]} | {r['energy_matched']} | {r['collateral_matched']} | {f(e.get('res_noop'), 2)} / {f(e.get('res_real'), 2)} / "
                 f"{f(e.get('res_control'), 2)} | {f(s.get('res_noop'), 2)} / {f(s.get('res_real'), 2)} / {f(s.get('res_control'), 2)} |")
    L.append("\n## Dose rival (G3)\n\n| cell | E | KL EN / SL | FLORES dNLL SL | EN refused | SL refused |\n|---|---|---|---|---|---|")
    for c, r in A["confirm"]["matched"]["dose"].items():
        L.append(f"| {c[3:]} | {r['E']:.1f} | {f(r['kl']['en'])} / {f(r['kl']['sl'])} | {f(r['flores_dNLL']['sl'])} | "
                 f"{f(r.get('en', {}).get('refused'), 2)} | {f(r.get('sl', {}).get('refused'), 2)} |")
    L.append("\n## Every Gemma confirmation cell (CONF harmful items)\n")
    L.append("| cell | lang | n | REFUSED | PARTIAL | COMPLIED | INVALID | heur-inv | ASR-rubric | LID | trunc |\n|---|---|---|---|---|---|---|---|---|---|---|")
    d = rt[(rt.model == "gemma") & rt.cell.str.startswith("CF_")].sort_values(["cell", "lang"])
    for r in d.itertuples():
        L.append(f"| {r.cell[3:]} | {r.lang} | {r.n_judged} | {f(r.refused, 2)} | {f(r.partial, 2)} | {f(r.complied, 2)} | {f(r.invalid, 2)} | "
                 f"{f(r.heur_invalid, 2)} | {f(r.asr_rubric, 2)} | {f(r.lid_ok, 2)} | {f(r.trunc, 2)} |")
    o = A.get("outside", {})
    if o.get("status") == "RUN":
        L.append("\n## Outside family (Qwen3-8B)\n\n| lang | eligible | no-op refusal (DEV) | CONF no-op | rho O | rho B_site | rho log E |\n|---|---|---|---|---|---|---|")
        for g, e in o["eligibility"].items():
            p = o["per_language"].get(g, {})
            L.append(f"| {g} | {e['eligible']} | {f(e['noop_refusal'], 2)} | {f(p.get('noop_refusal'), 2)} | {f(p.get('spearman_O'), 2)} | "
                     f"{f(p.get('spearman_Bsite'), 2)} | {f(p.get('spearman_logE'), 2)} |")
    j = A["judge"]
    if j.get("status") != "NOT PERFORMED":
        L.append(f"\n## Judge gate\n\nWithin edited cells: kappa(refused vs not) = {f(j['within_edited']['kappa_refused_vs_not'])} "
                 f"(n = {j['within_edited']['n']}); 4-way kappa {f(j['within_edited']['kappa_4way'])}; gate pass = {j['gate_pass']}; "
                 f"cost ${j['cost_usd']:.3f}.\n\n| stratum | n | kappa | local rate | gpt-4.1 rate |\n|---|---|---|---|---|")
        for k, v in list(j["within_edited_by_lang"].items()) + list(j["within_edited_by_ctype"].items()):
            L.append(f"| {k} | {v['n']} | {f(v['kappa_refused_vs_not'])} | {f(v['local_rate'], 2)} | {f(v['api_rate'], 2)} |")
    (C.RES / "report_tables.md").write_text("\n".join(L) + "\n")
    print("report_tables.md written")


if __name__ == "__main__":
    main()

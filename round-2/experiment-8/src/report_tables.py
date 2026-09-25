#!/usr/bin/env python3
"""Print the README's markdown result tables from results/analysis_summary.json (no numbers are typed by hand)."""
from __future__ import annotations

import common as C
from common import jload

NAMES = {"A0": "no-op", "A1": "d_EN", "A2": "d_EN + r_prior", "A3": "r_prior alone", "A4": "d_EN + l (language identity)",
         "A5": "d_EN + u_SL", "A6": "d_EN + r_prior⊥l", "A7": "d_EN + rand_1", "A8": "d_EN + rand_2", "A9": "d_EN + rand_3",
         "A10": "d_EN + shuffled-label r_prior", "A11": "d_EN + r_prior_SLjbb", "A3_c0.5": "r_prior alone c=.5",
         "A2d_c0.5": "d_EN + .5 r_prior", "ADD": "+ r_prior (addition, F6)", "X1": "layer-matched d_EN(h), all 48 [expl.]", "X3": "layer-matched random [expl.]",
         "X5": "layer-matched energy-matched PC [expl.]", "Y1_1_12": "d_EN(h), layers 1-12 [expl.]",
         "Y2_13_24": "d_EN(h), layers 13-24 [expl.]", "Y3_25_36": "d_EN(h), layers 25-36 [expl.]",
         "Y4_37_48": "d_EN(h), layers 37-48 [expl.]", "Yc24_1_24": "d_EN(h), layers 1-24 [expl.]",
         "Yc36_1_36": "d_EN(h), layers 1-36 [expl.]",
         "X2": "layer-matched d_EN(h)+d_SL(h) [expl.]", "X4": "d_EN c=2 [expl.]", "W0": "core Heretic edit (trial 96)",
         "W1": "core + r_prior weight edit", "W2": "core + random weight edit", "W3": "core edit + layer-matched d_EN(h) [expl.]",
         "W4": "core edit + layer-matched random [expl.]", "C0": "community heretic",
         "C1": "community + r_prior weight edit", "C2": "community + random weight edit",
         "G0": "no-op", "G1": "d_EN", "G2": "d_EN + l", "G3": "d_EN + u_SL", "G4": "d_EN + rand", "G5": "d_EN + r_prior"}


def f(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def rate_table(S, model, arms):
    R = {(r["model"], r["arm"], r["lang"], r["role"]): r for r in S["rates"]}
    col = {(c["model"], c["arm"]): c for c in S["collateral"]}
    print("| arm | EN harmful | SL harmful | EN harmless | SL harmless | SL invalid | FLORES ΔNLL EN / SL |")
    print("|---|---|---|---|---|---|---|")
    for a in arms:
        cells = []
        for g, role in (("en", "harmful"), ("sl", "harmful"), ("en", "harmless"), ("sl", "harmless")):
            r = R.get((model, a, g, role))
            cells.append("–" if r is None else f"{r['rate_refused']:.2f} [{r['refused_ci95'][0]:.2f}, {r['refused_ci95'][1]:.2f}] (n={r['n']})")
        inv = [R[k]["rate_invalid"] for k in ((model, a, "sl", "harmful"), (model, a, "sl", "harmless")) if k in R]
        c = col.get((model, a), {})
        if not any(k[:2] == (model, a) for k in R):
            continue
        print(f"| {a} {NAMES.get(a, a)} | " + " | ".join(cells) + f" | {f(max(inv) if inv else None)} | "
              f"{f(c.get('flores_dNLL_en'), 3)} / {f(c.get('flores_dNLL_sl'), 3)} |")


def main() -> None:
    S = jload(C.RES / "analysis_summary.json")
    print(f"label coverage: {S['label_coverage']}\n")
    print("### Gemma-3-12B-it activation arms (OUTCOME: 111 harmful + 111 harmless per language)\n")
    rate_table(S, "gemma", ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A3_c0.5", "A2d_c0.5", "ADD",
                            "X1", "X2", "X4"])
    dl = S.get("secondary", {}).get("depth_localisation")
    if dl:
        j2 = {(r["arm"], r["lang"], r["role"]): r for r in S["second_judge_sensitivity"]["rates"] if r["model"] == "gemma"}
        col = {c["arm"]: c for c in S["collateral"] if c["model"] == "gemma"}
        print("\n### Depth localisation (EXPLORATORY; rates = local Qwen3-14B second judge, full coverage n=111/lang)\n")
        print("| arm | SL harmful | EN harmful | FLORES ΔNLL EN / SL | KL (SL) | MC acc SL | SL invalid |")
        print("|---|---|---|---|---|---|---|")
        for a in ["A0", "A1", "X4", "X3", "X5", "Y1_1_12", "Y2_13_24", "Y3_25_36", "Y4_37_48", "Yc24_1_24", "Yc36_1_36", "X1", "X2"]:
            sl, en = j2.get((a, "sl", "harmful")), j2.get((a, "en", "harmful"))
            c = col.get(a, {})
            if sl is None:
                continue
            print(f"| {a} {NAMES.get(a, a)} | {sl['rate_refused']:.2f} [{sl['refused_ci95'][0]:.2f}, {sl['refused_ci95'][1]:.2f}] | "
                  f"{f(en['rate_refused']) if en else '–'} | {f(c.get('flores_dNLL_en'), 3)} / {f(c.get('flores_dNLL_sl'), 3)} | "
                  f"{f(c.get('kl_dolly_sl'), 3)} | {f(c.get('mc_acc_sl'))} | {f(dl['invalid_rate_sl'].get(a))} |")
    rep = S.get("secondary", {}).get("core_weight_edit", {}).get("repair_arms")
    if rep:
        col = {c["arm"]: c for c in S["collateral"] if c["model"] == "gemma"}
        print("\n### Repairing an English weight edit for Slovene (EXPLORATORY; second-judge rates, S4 hoc, n=70/lang)\n")
        print("| arm | SL harmful | EN harmful | SL over-refusal | FLORES ΔNLL EN / SL | SL invalid |")
        print("|---|---|---|---|---|---|")
        for a, r in rep["rates_second_judge"].items():
            c = col.get(a, {})
            print(f"| {a} {NAMES.get(a, a)} | {r['sl']['harmful']:.2f} | {r['en']['harmful']:.2f} | {r['sl']['harmless']:.2f} | "
                  f"{f(c.get('flores_dNLL_en'), 3)} / {f(c.get('flores_dNLL_sl'), 3)} | {f(rep['invalid_sl'].get(a))} |")
    print("\n### Weight edits on S4 hoc (70 pairs per language)\n")
    rate_table(S, "gemma", ["W0", "W1", "W2"])
    rate_table(S, "community", ["C0", "C1", "C2"])
    print("\n### GaMS3-12B-Instruct (descriptive)\n")
    rate_table(S, "gams3", ["G0", "G1", "G2", "G3", "G4", "G5"])
    V = S["verdicts"]
    print("\n### Frozen predictions\n")
    for k in ("F1", "F2", "F3", "F4", "F5", "F6"):
        v = V.get(k)
        print(f"- **{k}**: pass={None if v is None else v.get('pass')} — {v}")
    print(f"- KILL a/b/c: {V.get('KILL_a')}/{V.get('KILL_b')}/{V.get('KILL_c')} -> KILL={V.get('KILL')}")
    print(f"- confound: {V.get('confound_language_identity')}; one_knob={V.get('one_knob_reading')}")
    print(f"- holm: {V.get('holm')}")
    print(f"- cuts vs A1: " + "; ".join(f"{a} {c['est']:.3f} [{c['ci95'][0]:.3f}, {c['ci95'][1]:.3f}]" for a, c in V["cuts"].items()))


if __name__ == "__main__":
    main()

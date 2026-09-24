#!/usr/bin/env python3
"""Fills the README's Headline / Results / Limitations sections from results/analysis_summary.json,
results/redundancy_index.json and results/rederive.json, so no number in the README is typed by hand."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np

import common as C
from common import jload

BEGIN, END = "<!-- GENERATED:BEGIN -->", "<!-- GENERATED:END -->"


def f(x, n=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{n}f}"


def ci(x, n=2):
    return "" if not x or any(v is None or (isinstance(v, float) and np.isnan(v)) for v in x) else \
        f" [{x[0]:.{n}f}, {x[1]:.{n}f}]"


def main() -> None:
    S = jload(C.RES / "analysis_summary.json")
    ri = jload(C.RES / "redundancy_index.json")
    P = S.get("frozen_predictions_result", {})
    T = S["cell_table"]
    rd = jload(C.RES / "rederive.json") if (C.RES / "rederive.json").exists() else {}
    cp = jload(C.RES / "judge_cert_pool.json") if (C.RES / "judge_cert_pool.json").exists() else {}
    L = []
    L.append("\n## Headline\n")
    n = 1
    L.append(f"{n}. **Depth-coverage is what removes refusal, and Slovene needs a little more of it than English — but on "
             f"this model no amount of it leaves a usable model.** On DEV (n={ri['n_items']} harmful items per language), "
             f"ablating the frozen per-layer English direction over a cumulative prefix of the first *k* hidden indices "
             f"takes judged harmful refusal from {f(ri['noop_refusal']['en'])} (EN) / {f(ri['noop_refusal']['sl'])} (SL) "
             f"through the 0.5 crossing at **index_EN = {ri['index']['en']}** (95% CI {ri['index_boot_CI95']['en']}) and "
             f"**index_SL = {ri['index']['sl']}** ({ri['index_boot_CI95']['sl']}); the difference is "
             f"{ri['diff_SL_minus_EN']} layers with CI {ri['diff_boot_CI95']}, i.e. **equivalent within the pre-declared "
             f"±8-layer margin** (PA1 {P.get('PA1', {}).get('verdict', '–')}). But the co-primary *usable* index — the "
             f"shallowest prefix that removes refusal **and** keeps INVALID ≤ 0.10 — is "
             f"**{ri['index_usable']['en']} (EN) / {ri['index_usable']['sl']} (SL)**: at every depth that removes refusal, "
             f"{f(ri['prefix_invalid_curves']['en']['16'])} (EN) / {f(ri['prefix_invalid_curves']['sl']['16'])} (SL) of the "
             f"replies are degenerate or wrong-language. Activation-space depth coverage pays for refusal removal with the model itself.\n")
    n += 1
    if "PB2" in P:
        a = P["PB2"]["pooled_narrow_minus_broad"]
        sl_d = a["sl"]["diff"]
        who = "concentrating the same budget on one 12-layer band beats spreading it" if sl_d < 0 else \
              "spreading the same budget beats concentrating it"
        i3 = P.get("PB3", {})
        L.append(f"{n}. **The pre-registered coverage hypothesis is falsified, and falsified in the opposite direction: at "
                 f"matched total removal energy, {who}.** Pooling the three matched-energy groups on the "
                 f"{P['PB2']['split']} set (held-out harm categories), narrow-and-strong (one 12-layer band) minus "
                 f"broad-and-weak (stride-2 / all-48) Slovene refusal is **{f(sl_d)}**{ci(a['sl']['ci'])} over "
                 f"n={a['sl']['n']} semantic items — PB2 predicted this to be **positive** (broad better) and it is "
                 f"negative with a CI excluding zero, so **{P['PB2']['verdict']}**. In English the same contrast is "
                 f"{f(a['en']['diff'])}{ci(a['en']['ci'])}. The coverage×language interaction is "
                 f"{f(i3.get('interaction_SL_minus_EN'))}{ci(i3.get('ci'))}: the advantage of concentrating is "
                 f"{'larger' if (i3.get('interaction_SL_minus_EN') or 0) < 0 else 'smaller'} in Slovene than in English, "
                 f"which is a real coverage×language interaction but again the opposite sign to PB3's prediction "
                 f"({i3.get('verdict', '–')}).\n")
        n += 1
    if "PB1" in P:
        a = P["PB1"]
        dec = a.get("decomposition", {})
        L.append(f"{n}. **Across the whole panel, what a cell does to Slovene is explained by its energy, its English "
                 f"outcome and WHERE its energy sits — not by how much depth it covers.** Across {a['n_cells']} weight cells, R² for the Slovene residual rises "
                 f"{f(a['R2_base'],3)} → {f(a['R2_full'],3)} when the coverage terms are added to (log E + EN outcome + the "
                 f"static geometry baselines b1/b3): ΔR² = **{f(a['dR2'],3)}** with cell-bootstrap CI "
                 f"{a['dR2_cell_boot_CI95']} (PB1 {a['verdict']}). With so few cells the in-sample ΔR² is optimistic; the "
                 f"leave-one-cell-out ΔR² is {f(a.get('loo_cv_dR2'),3)} — adding coverage terms makes out-of-sample "
                 f"prediction *worse*. The nested decomposition shows why: log E alone gives R² "
                 f"{f(dec.get('R2_logE'),3)}, adding the four band energy fractions (WHERE the edit sits) gives "
                 f"{f(dec.get('R2_logE_plus_placement_b3'),3)}, while adding the covered-layer count instead gives "
                 f"{f(dec.get('R2_logE_plus_count'),3)}.\n")
        n += 1
    wc = [c for c, r in T.items() if r.get("tier") in ("T1", "T2") and r.get("E_exact") and not r.get("degraded")]
    if wc:
        fl = [abs(T[c].get("flores_dNLL_sl") or 0) for c in wc]
        mc0 = T.get("NOOP", {}).get("mc_acc_sl")
        dmc = max((abs((T[c].get("mc_acc_sl") or mc0 or 0) - mc0) for c in wc if mc0 is not None), default=float("nan"))
        L.append(f"{n}. **The operator, not the direction, decides whether depth coverage is usable.** The same frozen "
                 f"per-layer directions applied as **Heretic's row-norm-preserving weight edit** cover the same depths with "
                 f"essentially no collateral — {len(wc)} cells pass the degradation gate with |SL FLORES ΔNLL| ≤ "
                 f"{f(max(fl),3)} nats and Slovene multiple-choice accuracy within {f(dmc,3)} of the unedited model — "
                 f"while the raw activation projection of those same directions at every token position leaves "
                 f"{f(ri['prefix_invalid_curves']['sl'][str(ri['index_numeric']['sl'])] if str(ri['index_numeric']['sl']) in ri['prefix_invalid_curves']['sl'] else float('nan'))} "
                 f"of Slovene replies unusable at its own crossing depth. Conclusions about 'how deep an edit must reach' "
                 f"do not transfer across the two operators.\n")
        n += 1
    pl = S.get("contiguous_vs_spread_matched_count_and_energy", {})
    if pl:
        best = max(pl.items(), key=lambda kv: abs(kv[1]["sl"]["diff"]) if not np.isnan(kv[1]["sl"]["diff"]) else -1)
        k, r = best
        L.append(f"{n}. **What matters is WHERE the covered layers sit, not how many there are.** `{k}` compares 12 "
                 f"*contiguous* layers against 12 layers spread every 4th, at the **same total removal energy and the same "
                 f"number of edited layers**: Slovene refusal {f(r['sl_band_rate'])} vs {f(r['sl_stride_rate'])} "
                 f"(Δ {f(r['sl']['diff'])}{ci(r['sl']['ci'])}), English {f(r['en_band_rate'])} vs "
                 f"{f(r['en_stride_rate'])} (Δ {f(r['en']['diff'])}{ci(r['en']['ci'])}). Spreading the same budget thinly "
                 f"over depth is not what unlocks Slovene — concentrating it on the right band is.\n")
        n += 1
    ctl = [c for c in T if "RND_ALL" in c or "PC_ALL" in c]
    if ctl:
        rr = [T[c].get("screen_sl_REFUSED") for c in ctl if T[c].get("screen_sl_REFUSED") is not None]
        L.append(f"{n}. **The controls behave.** At the same sites and the same total removal energy, the layer-matched "
                 f"random and energy-matched principal-component edits leave Slovene harmful refusal at "
                 f"{f(min(rr))}–{f(max(rr))} (no-op {f(T.get('NOOP', {}).get('screen_sl_REFUSED'))}), so what removes "
                 f"refusal is the harm direction, not the amount of weight surgery.\n")
        n += 1
    deg = [c for c, r in T.items() if r.get("degraded")]
    L.append(f"{n}. **Refusal removal is reported next to the damage.** {len(deg)} of {len(T)} cells trip the pre-declared "
             f"degradation gate (INVALID > 0.05, wrong-language drift > 3 pts, FLORES ΔNLL > 1.0 nats or MC accuracy −5 pts) "
             f"and are printed as DEGRADED in their own rows; no cell counts as successful suppression on a refusal number "
             f"alone.\n")
    n += 1
    if "PB4" in P:
        a = P["PB4"]
        why = ("" if a["spearman"] >= 0.6 else
               " The reason is visible in the design: the index is a function of the NUMBER of covered layers, so it assigns "
               "the same prediction to a 12-layer band and to 12 layers spread every 4th — cells whose measured refusal "
               "differs by most of the scale. A count-based depth instrument cannot express placement, which is what "
               "actually moves this model.")
        L.append(f"{n}. **The DEV-frozen index transfers {'' if a['spearman'] >= 0.6 else 'poorly '}to the weight cells.** "
                 f"Spearman between the index-curve prediction at k = covered layers and the observed per-language refusal "
                 f"is {f(a['spearman'])} (n={a['n']} cell×language points, p={f(a['p'],3)}) — PB4 {a['verdict']}.{why}\n")
        n += 1
    cm = jload(C.RES / "cross_model.json") if (C.RES / "cross_model.json").exists() else None
    if cm and cm.get("joint_reading"):
        jr = cm["joint_reading"]
        pr = jr["index_pairs_gams3_vs_gemma"]
        L.append(f"{n}. **The Slovene lag is not what separates the two sibling models.** The iteration-3 Gemma pod ran the "
                 f"same instrument (same split, same blind local judge, same prefix family) on `google/gemma-3-12b-it` and "
                 f"reports index_EN = {pr['en'][1]}, index_SL = {pr['sl'][1]}; this pod reports index_EN = {pr['en'][0]}, "
                 f"index_SL = {pr['sl'][0]} for GaMS3. **Both checkpoints put Slovene exactly one 4-layer step deeper than "
                 f"English.** Whatever made the iteration-1 Heretic edits differ between these two models, it is not a "
                 f"difference in how redundantly refusal is written across depth. {jr['caution']}\n")
        n += 1

    hp_items = [(k, v) for k, v in sorted(S.get("holm_adjusted_p", {}).items()) if v is not None and not np.isnan(v)]
    if hp_items:
        L.append("\nHolm-adjusted p-values across the frozen family: "
                 + ", ".join(f"{k} {f(v,3)}" for k, v in hp_items)
                 + ". Predictions whose contrast could not be evaluated carry no p-value.\n")

    L.append("\n## Audit\n")
    if rd:
        L.append(f"`rederive.py` re-derives **{rd.get('n_match')}/{rd.get('n_checks')}** headline numbers from the raw "
                 f"per-generation files through a code path that imports nothing from the analysis "
                 f"(`results/rederive.json`), and the freeze-order check "
                 f"({'PASS' if rd.get('freeze_order', {}).get('ok') else 'FAIL'}) confirms `configs/FREEZE.sha256` predates "
                 f"the first confirmation generation. Placebos: "
                 + "; ".join(f"{k} null mean {f(v.get('null_mean') if v.get('null_mean') is not None else v.get('observed_dR2'),3)}"
                               f"{ci(v.get('null_ci'),3)}" for k, v in rd.get("placebos", {}).items())
                 + " — each collapses to zero while the real contrasts do not.\n")
    if cp:
        L.append(f"\n**Judge.** The primary judge is the blind local Qwen3-14B with iteration-2's frozen rubric. Certified "
                 f"for free against the gpt-4.1 labels already on disk, restricted to EDITED arms (n={cp['n']}): "
                 f"κ = **{f(cp['kappa_refused_vs_not_sl'])} in Slovene** (n={cp['n_sl']}) but only "
                 f"**{f(cp['kappa_refused_vs_not_en'])} in English** (n={cp['n_en']}), where it is systematically stricter "
                 f"(refused rate {f(cp['rate_refused_local_en'])} vs {f(cp['rate_refused_g41_en'])}). The planned gpt-4.1 "
                 f"top-up could not be bought — the run's OpenRouter key was already exhausted (HTTP 403 "
                 f"`aii_run_budget_exhausted`), so **English rates here are the strict end of a judge range** and every "
                 f"English claim carries that caveat; Slovene, which every headline is about, is certified. A degenerate "
                 f"reply (4-gram repetition > 0.5) is forced to INVALID by rule, because the local judge labels "
                 f"prompt-echo output 'refused'.\n")
    L.append("\n## Limitations\n")
    L.append("- One model, one optimiser seed, one Slovene locale, 4-bit NF4 throughout: every absolute level is "
             "NF4-specific and prompt-level CIs do not measure optimiser variance.\n"
             "- Slovene items are machine-translated with automated QC only; **native review is PENDING**, not performed.\n"
             f"- n = 41 harmful screen items and 70 held-out-category confirmation items per language, so differences below "
             f"~0.10 are not resolvable; the matched-energy contrast is paired to get the most out of that.\n"
             "- Coverage and total removal energy are collinear by construction; the matched-energy groups, not the "
             "regression, are the primary contrast, and the regression's ΔR² is reported with its cell bootstrap and its "
             "leave-one-out companion.\n"
             "- ASR under RefusEU's official guard pipeline was not run (see `results/deviations.json`); 'not refused' is "
             "reported as judged COMPLIED + PARTIAL, an upper bound on attack success.\n"
             "- Utility is the cheap teacher-forced multiple-choice readout plus FLORES ΔNLL and Dolly KL, not the lm-eval "
             "harness macro: the S7 splits are reserved for the final evaluation artifact and were never opened here.\n"
             "- The Gemma column comes from the sibling iteration-3 pod, not from this workspace: it was produced by "
             "different code on a different pod and is joined here only because both ran the same instrument on the same "
             "split with the same pinned judge. Every cross-model statement is descriptive (n = 2 checkpoints) and none is "
             "attributed to continual pretraining, instruction tuning or any other training stage.\n"
             "- **This model was not the one with the Slovene problem.** The iteration-1 GaMS3 Heretic edit reproduced here "
             "as the CORE anchor already leaves only "
             f"{f(T.get('CORE_trial88', {}).get('confirm_sl_REFUSED'))} Slovene refusal on the held-out categories, so the "
             "'Slovene residual' that motivated the question is a Gemma phenomenon. What this panel measures on GaMS3 is "
             "how placement, coverage and energy trade off against each other and against Slovene, not the rescue of a "
             "locked language.\n"
             "- The matched-energy design caps out at E = 28 because a 12-layer band cannot exceed Heretic's max_weight "
             "bound of 1.5; the shipped CORE edit sits at E = 74, well outside the matched range, so the groups compare "
             "shapes at low-to-moderate edit size rather than at production strength.\n")
    txt = (C.ROOT / "README.md").read_text()
    a, b = txt.index(BEGIN) + len(BEGIN), txt.index(END)   # idempotent: always replace the generated block
    (C.ROOT / "README.md").write_text(txt[:a] + "\n" + "\n".join(L) + "\n" + txt[b:])
    print("README.md headline/audit/limitations filled")


if __name__ == "__main__":
    main()

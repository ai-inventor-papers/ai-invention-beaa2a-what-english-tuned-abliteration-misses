#!/usr/bin/env python3
"""Figures fig1-fig7 (PDF + PNG) from saved results only (analysis_summary.json, per-item rows, diagnostics)."""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import common as C
from common import jload

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"en": "#3b6fb6", "sl": "#d9822b"}
ARM_NAMES = {"A0": "no-op", "A1": "d_EN", "A2": "d_EN+r_prior", "A3": "r_prior alone", "A4": "d_EN+l", "A5": "d_EN+u_SL",
             "A6": "d_EN+r_prior⊥l", "A7": "d_EN+rand1", "A8": "d_EN+rand2", "A9": "d_EN+rand3", "A10": "d_EN+shuffled",
             "A11": "d_EN+r_prior_SLjbb", "ADD": "+r_prior (add)", "A3_c0.5": "r_prior c=.5", "A2d_c0.5": "d_EN+.5 r_prior",
             "W0": "core edit", "W1": "core+r_prior W", "W2": "core+rand W", "C0": "community", "C1": "comm.+r_prior W",
             "C2": "comm.+rand W", "W3": "core+layer-matched d_EN(h)*", "W4": "core+layer-matched rand*", "X1": "layer-matched d_EN(h)*", "X2": "layer-matched d_EN+d_SL*", "X4": "d_EN c=2*",
             "X3": "layer-matched random*", "X5": "layer-matched PC*", "Y1_1_12": "layers 1-12*", "Y2_13_24": "layers 13-24*",
             "Y3_25_36": "layers 25-36*", "Y4_37_48": "layers 37-48*", "Yc24_1_24": "layers 1-24*", "Yc36_1_36": "layers 1-36*",
             "G0": "no-op", "G1": "d_EN", "G2": "d_EN+l", "G3": "d_EN+u_SL", "G4": "d_EN+rand", "G5": "d_EN+r_prior"}


def save(fig, name):
    fig.tight_layout()
    fig.savefig(C.FIGS / f"{name}.pdf")
    fig.savefig(C.FIGS / f"{name}.png", dpi=200)
    plt.close(fig)


def bars(ax, R, model, arms, role, title):
    x = np.arange(len(arms))
    for k, g in enumerate(("en", "sl")):
        vals, lo, hi = [], [], []
        for a in arms:
            r = next((r for r in R if r["model"] == model and r["arm"] == a and r["lang"] == g and r["role"] == role), None)
            v = r["rate_refused"] if r else np.nan
            c = r["refused_ci95"] if r else [np.nan, np.nan]
            vals.append(v)
            lo.append(v - c[0] if c[0] is not None else 0)
            hi.append(c[1] - v if c[1] is not None else 0)
        ax.bar(x + (k - 0.5) * 0.38, vals, 0.38, yerr=[lo, hi], color=COL[g], label=g.upper(), capsize=2, error_kw={"lw": 0.7})
        for xi, a in enumerate(arms):  # judged n per bar (the primary judge covers some arms only partly)
            r = next((r for r in R if r["model"] == model and r["arm"] == a and r["lang"] == g and r["role"] == role), None)
            if r:
                ax.text(xi + (k - 0.5) * 0.38, 0.015, str(r["n"]), ha="center", va="bottom", fontsize=5, rotation=90, color="white")
    ax.set_xticks(x, [ARM_NAMES.get(a, a) for a in arms], rotation=40, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("judged refusal rate")
    ax.set_title(title)


def main() -> None:
    S = jload(C.RES / "analysis_summary.json")
    R = S["rates"]
    have = {(r["model"], r["arm"]) for r in R}
    have2 = have | {(r["model"], r["arm"]) for r in S["second_judge_sensitivity"]["rates"]}  # arms the paid judge never reached
    # fig1: activation arms
    harm_arms = [a for a in ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "X1", "X2", "X4"] if ("gemma", a) in have]
    ben_arms = [a for a in ["A0", "A1", "A2", "A3", "A4", "A7", "ADD"] if ("gemma", a) in have]
    fig, axs = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw={"width_ratios": [len(harm_arms) + 1, len(ben_arms) + 1]})
    bars(axs[0], R, "gemma", harm_arms, "harmful", "Gemma-3-12B-it, OUTCOME harmful (111/lang)")
    bars(axs[1], R, "gemma", ben_arms, "harmless", "OUTCOME harmless twins (over-refusal)")
    axs[0].legend(frameon=False)
    save(fig, "fig1_refusal_by_arm")
    # fig2: dose-response (teacher-forced R1) + judged points at c=.5
    rows = pd.DataFrame([json.loads(l) for l in (C.RES / "gemma" / "per_item_rows.jsonl").read_text().splitlines()])
    out = rows[rows.kind == "out"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for ax, fam, pre in ((axs[0], "rprior_alone", "A3_c"), (axs[1], "dEN_plus_c_rprior", "A2d_c")):
        for g in ("en", "sl"):
            for role, ls in (("harmful", "-"), ("harmless", "--")):
                cs, ms = [], []
                for c in (0.0, 0.25, 0.5, 0.75, 1.0):
                    arm = ("A0" if fam == "rprior_alone" else "A1") if c == 0 else f"{pre}{c}"
                    v = out[(out.arm == arm) & (out.lang == g) & (out.role == role)]["R1"]
                    if len(v):
                        cs.append(c)
                        ms.append(v.mean())
                ax.plot(cs, ms, ls, color=COL[g], marker="o", ms=3, label=f"{g.upper()} {role}")
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_xlabel("c (r_prior ablation strength)")
        ax.set_ylabel("mean R1 (refusal log-odds)")
        ax.set_title("r_prior alone" if fam == "rprior_alone" else "d_EN + c·r_prior")
    axs[0].legend(frameon=False, fontsize=7)
    save(fig, "fig2_dose_response")
    # fig3: weight edits (core + community)
    w_arms = [(m, a) for m, a in [("gemma", "W0"), ("gemma", "W1"), ("gemma", "W2"), ("gemma", "W3"), ("gemma", "W4"), ("community", "C0"), ("community", "C1"), ("community", "C2")] if (m, a) in have2]
    if w_arms:
        fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
        R2 = {(r["model"], r["arm"], r["lang"], r["role"]): r for r in S["second_judge_sensitivity"]["rates"]}
        for ax, role in zip(axs, ("harmful", "harmless")):
            x = np.arange(len(w_arms))
            for k, g in enumerate(("en", "sl")):
                vals, err = [], [[], []]
                for m, a in w_arms:
                    r = R2.get((m, a, g, role))  # ONE judge for the whole panel: the second judge covers every weight arm
                    v = r["rate_refused"] if r else np.nan
                    vals.append(v)
                    err[0].append(v - r["refused_ci95"][0] if r else 0)
                    err[1].append(r["refused_ci95"][1] - v if r else 0)
                ax.bar(x + (k - 0.5) * 0.38, vals, 0.38, yerr=err, color=COL[g], label=g.upper(), capsize=2)
            ax.set_xticks(x, [ARM_NAMES[a] for _, a in w_arms], rotation=35, ha="right")
            ax.set_ylim(0, 1.05)
            ax.set_title(f"S4 hoc {role} (70/lang), second judge")
            ax.set_ylabel("judged refusal rate")
        axs[0].legend(frameon=False)
        save(fig, "fig3_weight_edits")
    # fig4: per-layer cosines
    dg = jload(C.RES / "gemma" / "direction_diagnostics.json")["per_layer"]
    Lr = jload(C.CFG / "frozen_protocol_gemma.json")["L_r"]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    hh = [d["h"] for d in dg][1:]
    for key, lab in (("cos_rprior_l", "cos(r_prior, l)"), ("cos_rprior_dEN20", "cos(r_prior, d_EN@20)"),
                     ("cos_rprior_SLjbb", "cos(r_prior, r_prior_SLjbb)"), ("split_half_ceiling_SB", "split-half ceiling (SB)"),
                     ("cos_rprior_shuf_mean", "cos(r_prior, shuffled)")):
        ax.plot(hh, [d[key] for d in dg][1:], label=lab, lw=1)
    ax.axvline(Lr, color="k", ls=":", lw=0.8)
    ax.set_xlabel("hidden index")
    ax.set_ylabel("cosine")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig4_layer_cosines")
    # fig5: criterion vs evidence forest
    ce = S.get("item_level", {}).get("criterion_vs_evidence", {})
    if ce:
        fig, ax = plt.subplots(figsize=(5, 2.6))
        y = 0
        for arm, v in ce.items():
            for k, (name, ci_) in enumerate((("l2_b1_harm", "b1_ci95"), ("l2_b2_prior", "b2_ci95"))):
                c = v[ci_] or [np.nan, np.nan]
                ax.errorbar(v[name], y, xerr=[[v[name] - c[0]], [c[1] - v[name]]], fmt="o", color=["#555", "#d9822b"][k], capsize=2)
                ax.text(ax.get_xlim()[0] if False else -0.1, y, f"{ARM_NAMES.get(arm, arm)} {'b1 harm' if k == 0 else 'b2 prior'}",
                        ha="right", va="center", fontsize=7)
                y += 1
        ax.axvline(0, color="grey", lw=0.5)
        ax.set_yticks([])
        ax.set_xlabel("standardized logit coefficient (SL items)")
        save(fig, "fig5_criterion_vs_evidence")
    tp = S.get("item_level", {}).get("transfer_predictors", {})
    if tp and "cosine_baseline" in tp:
        fig, ax = plt.subplots(figsize=(4.5, 2.6))
        names = ["cosine_baseline", "baseline_margin", "rprior_projection", "margin_plus_projection"]
        ax.bar(range(4), [tp[n]["auroc"] for n in names], color=["#999", "#3b6fb6", "#d9822b", "#6a3d9a"])
        ax.set_xticks(range(4), ["cos x EN drop", "SL margin", "r_prior proj.", "margin+proj."], rotation=20)
        ax.axhline(0.5, color="grey", lw=0.5)
        ax.set_ylabel("5-fold grouped CV AUROC")
        ax.set_title("Which SL items survive d_EN?")
        save(fig, "fig6_transfer_predictors")
    g_arms = [a for a in ["G0", "G1", "G2", "G3", "G4", "G5"] if ("gams3", a) in have]
    if g_arms:
        fig, axs = plt.subplots(1, 2, figsize=(9, 3.4), gridspec_kw={"width_ratios": [len(g_arms) + 1, 3]})
        bars(axs[0], R, "gams3", g_arms, "harmful", "GaMS3-12B-Instruct, OUTCOME harmful")
        bars(axs[1], R, "gams3", [a for a in ("G0", "G1") if ("gams3", a) in have], "harmless", "harmless twins")
        axs[0].legend(frameon=False)
        save(fig, "fig8_gams3_arms")
    # fig9: headline - SL harmful refusal under each intervention, both judges, with the Slovene-fluency cost
    S2 = {(r["model"], r["arm"], r["lang"], r["role"]): r for r in S["second_judge_sensitivity"]["rates"]}
    col = {(c["model"], c["arm"]): c for c in S["collateral"]}
    arms9 = [a for a in ("A0", "A1", "A2", "A7", "A10", "A4", "A6", "X4", "X3", "X5", "X1", "X2") if ("gemma", a) in have]
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.4), gridspec_kw={"width_ratios": [3, 2]})
    x = np.arange(len(arms9))
    for k, (src, lab, c_) in enumerate(((R, "gpt-4.1 (primary)", "#3b6fb6"), (None, "Qwen3-14B (2nd judge, full coverage)", "#9467bd"))):
        vals, err = [], [[], []]
        for a in arms9:
            r = (next((r for r in R if r["model"] == "gemma" and r["arm"] == a and r["lang"] == "sl" and r["role"] == "harmful"), None)
                 if src is not None else S2.get(("gemma", a, "sl", "harmful")))
            v = r["rate_refused"] if r else np.nan
            vals.append(v)
            err[0].append(v - r["refused_ci95"][0] if r else 0)
            err[1].append(r["refused_ci95"][1] - v if r else 0)
        axs[0].bar(x + (k - 0.5) * 0.38, vals, 0.38, yerr=err, color=c_, label=lab, capsize=2, error_kw={"lw": 0.7})
    axs[0].set_xticks(x, [ARM_NAMES.get(a, a) for a in arms9], rotation=40, ha="right")
    axs[0].set_ylabel("Slovene harmful refusal")
    axs[0].set_title("Residual Slovene refusal after an English edit")
    axs[0].legend(frameon=False, fontsize=7)
    for a in arms9:
        r = next((r for r in R if r["model"] == "gemma" and r["arm"] == a and r["lang"] == "sl" and r["role"] == "harmful"), None)
        c = col.get(("gemma", a), {})
        if r and c.get("flores_dNLL_sl") is not None:
            bad = r.get("rate_invalid", 0) > 0.2  # degenerate / wrong-language output: the "cut" is model destruction
            axs[1].scatter(c["flores_dNLL_sl"], r["rate_refused"], s=30 if bad else 22,
                           marker="X" if bad else "o", color="#c0392b" if bad else ("#d9822b" if a.startswith("X") else "#3b6fb6"))
            axs[1].annotate(ARM_NAMES.get(a, a), (c["flores_dNLL_sl"], r["rate_refused"]), fontsize=6,
                            xytext=(3, 3), textcoords="offset points")
    axs[1].set_xscale("symlog", linthresh=0.05)
    axs[1].set_xlabel("Slovene FLORES ΔNLL (nats/token)")
    axs[1].set_ylabel("Slovene harmful refusal")
    axs[1].set_title("safety cut vs Slovene fluency cost")
    axs[1].scatter([], [], marker="X", color="#c0392b", label=">20% invalid SL output")
    axs[1].legend(frameon=False, fontsize=6, loc="lower left")
    save(fig, "fig9_residual_vs_cost")
    dl = S.get("secondary", {}).get("depth_localisation")
    if dl:
        fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.3), gridspec_kw={"width_ratios": [3, 2]})
        # the primary judge's budget ran out before these arms, so fig10 uses the local second judge (full coverage)
        J2 = {(r["arm"], r["lang"], r["role"]): r for r in S["second_judge_sensitivity"]["rates"] if r["model"] == "gemma"}
        order = [a for a in ["A0", "A1", "X4", "X3", "X5", "Y1_1_12", "Y2_13_24", "Y3_25_36", "Y4_37_48", "Yc24_1_24",
                             "Yc36_1_36", "X1", "X2"] if (a, "sl", "harmful") in J2]
        x = np.arange(len(order))
        for k, g in enumerate(("sl", "en")):
            vals, err = [], [[], []]
            for a in order:
                r = J2[(a, g, "harmful")]
                vals.append(r["rate_refused"])
                err[0].append(r["rate_refused"] - r["refused_ci95"][0])
                err[1].append(r["refused_ci95"][1] - r["rate_refused"])
            axs[0].bar(x + (k - 0.5) * 0.38, vals, 0.38, yerr=err, color=COL[g], capsize=2, error_kw={"lw": 0.6},
                       label=f"{g.upper()} harmful")
        axs[0].set_xticks(x, [ARM_NAMES.get(a, a) for a in order], rotation=40, ha="right")
        axs[0].set_ylabel("judged refusal rate")
        axs[0].set_title("Where the Slovene residual is written (second judge, n=111/lang)")
        axs[0].legend(frameon=False, fontsize=7)
        for a in order:
            f = dl["flores_dNLL"].get(a, {}).get("sl")
            r = J2[(a, "sl", "harmful")]["rate_refused"]
            if f is not None and r is not None:
                axs[1].scatter(f, r, s=24, color="#c0392b" if dl["invalid_rate_sl"].get(a, 0) > 0.2 else "#3b6fb6")
                axs[1].annotate(ARM_NAMES.get(a, a), (f, r), fontsize=6, xytext=(3, 3), textcoords="offset points")
        axs[1].set_xscale("symlog", linthresh=0.05)
        axs[1].set_xlabel("Slovene FLORES ΔNLL")
        axs[1].set_ylabel("SL harmful refusal")
        axs[1].set_title("band vs Slovene fluency cost")
        save(fig, "fig10_depth_localisation")
    rd = jload(C.RES / "gemma" / "rand_draws.json")
    fig, ax = plt.subplots(figsize=(4.5, 3))
    d = [x for x in rd["draws"] if "coll" in x]
    ax.scatter([x["energy_ratio"] for x in rd["draws"]], [x.get("coll", np.nan) for x in rd["draws"]], s=8, color="#999", label="draws")
    acc = [x for x in rd["draws"] if x["k"] in rd["accepted_k"]]
    ax.scatter([x["energy_ratio"] for x in acc], [x.get("coll", np.nan) for x in acc], s=20, color="#d9822b", label="accepted")
    ax.axhline(rd["coll_rprior"], color="k", ls=":", lw=0.8, label="r_prior collateral")
    ax.axvspan(0.75, 1.25, color="#3b6fb6", alpha=0.1)
    ax.set_xscale("log")
    ax.set_xlabel("projection energy / r_prior's")
    ax.set_ylabel("SL FLORES ΔNLL (d_EN + u)")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig7_random_acceptance")
    print("figures written", sorted(p.name for p in C.FIGS.glob("*.png")))


if __name__ == "__main__":
    main()

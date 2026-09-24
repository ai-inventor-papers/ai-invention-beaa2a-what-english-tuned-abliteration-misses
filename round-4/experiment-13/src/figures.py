#!/usr/bin/env python3
"""Figures (PDF + PNG) from results/analysis.json, results/cell_table.csv and configs/frozen_predictions.json.
fig1 causal write profile e_EN(h) vs e_SL(h) with item-bootstrap bands + probe-mass ('read') overlay
fig2 O vs residual refusal per language on CONF cells, beside the single-site baseline
fig3 matched-group forest plot (high-O minus low-O, per group and language)
fig4 nested-R2 ladders, both orders (confirmation, per language)
fig5 REFUSED/PARTIAL/COMPLIED/INVALID stacked bars per confirmation condition
fig6 outside family (Qwen3-8B) per-language O vs residual"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import common as C  # noqa: E402

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"en": "#1f77b4", "sl": "#d62728", "de": "#2ca02c", "lt": "#9467bd"}
A = json.loads((C.RES / "analysis.json").read_text())
FP = json.loads((C.CFG / "frozen_predictions.json").read_text())


def save(fig, name):
    fig.tight_layout()
    fig.savefig(C.FIGS / f"{name}.pdf")
    fig.savefig(C.FIGS / f"{name}.png", dpi=180)
    plt.close(fig)


def fig1():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
    h = np.arange(1, 49)
    for g in C.LANGS:
        jp = FP["judged_profile"][g]
        axes[0].plot(h, jp["e_raw"], color=COL[g], label=f"{g.upper()} judged drop (split-half r={jp['split_half_r']:.2f})")
        axes[0].fill_between(h, jp["e_ci_lo"], jp["e_ci_hi"], color=COL[g], alpha=0.15)
        tp = FP["tf_profile"][g]
        axes[1].plot(h, tp["e_raw"], color=COL[g], label=f"{g.upper()} teacher-forced (r={tp['split_half_r']:.2f})")
        axes[1].fill_between(h, tp["e_ci_lo"], tp["e_ci_hi"], color=COL[g], alpha=0.15)
    ax2 = axes[0].twinx()
    for g in C.LANGS:
        ax2.plot(h, FP["probe_mass_read_profile"][g], color=COL[g], ls=":", lw=1)
    ax2.set_ylabel("probe mass ||d_L(h)|| (normalised, dotted)")
    axes[0].axhline(0, color="k", lw=0.5)
    axes[0].set(xlabel="hidden index h (single-site ablation of d_EN(h))", ylabel="refusal drop vs no-op (DEV)",
                title=f"Causal write profile (primary: {FP['primary_profile']}, {FP['O_status'].split(' ')[0]})")
    axes[1].set(xlabel="hidden index h", ylabel="log-prob drop of no-op refusal prefix", title="Teacher-forced readout (judge-free)")
    axes[0].legend(fontsize=7, loc="upper left")
    axes[1].legend(fontsize=7)
    save(fig, "fig1_profile")


def fig2():
    pl = A["confirm"]["per_language"]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.2))
    for k, g in enumerate(C.LANGS):
        cells = pl[g]["cells"]
        x = [c["O"] for c in cells]
        y = [c["residual_strict"] for c in cells]
        axes[2 * k].scatter(x, y, color=COL[g], s=18)
        axes[2 * k].set(xlabel=f"O_{g.upper()} (frozen)", ylabel=f"{g.upper()} residual refusal (CONF)",
                        title=f"O: rho={pl[g]['spearman'][f'O_{g}']:.2f} CI {np.round(pl[g]['item_boot']['spearman_O_ci'], 2).tolist()}")
        xb = [c["B_site"] for c in cells]
        axes[2 * k + 1].scatter(xb, y, color="gray", s=18)
        axes[2 * k + 1].set(xlabel=f"B_site_{g.upper()} (single-site drop at peak)",
                            title=f"B_site: rho={pl[g]['spearman'][f'B_site_{g}']:.2f}")
    save(fig, "fig2_O_vs_residual")


def fig3():
    gr = A["confirm"]["matched"]["groups"]
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ys, labels = 0, []
    for G, rec in gr.items():
        for off, g in ((0.15, "en"), (-0.15, "sl")):
            if rec.get(g):
                d, ci = rec[g]["diff_hi_minus_lo"], rec[g]["ci"]
                ax.errorbar(d, ys + off, xerr=[[d - ci[0]], [ci[1] - d]], fmt="o", color=COL[g], ms=4,
                            label=g.upper() if ys == 0 else None)
        labels.append(f"{G} (k={rec['k']}, E={rec['E']:.0f})")
        ys -= 1
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(0, ys, -1))
    ax.set_yticklabels(labels)
    ax.set(xlabel="residual refusal: high-O minus low-O (matched energy and count)", title="Matched-group contrasts (95% item bootstrap)")
    ax.legend(fontsize=7)
    save(fig, "fig3_matched_forest")


def fig4():
    pl = A["confirm"]["per_language"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    for k, g in enumerate(C.LANGS):
        f, r = pl[g]["ladder_forward"], pl[g]["ladder_reverse"]
        axes[k].plot(list(f.keys()), list(f.values()), "o-", color=COL[g], label="nuisances first, O last")
        axes[k].plot(range(len(r)), list(r.values()), "s--", color="gray", label="O first, nuisances after")
        for i, lab in enumerate(r.keys()):
            axes[k].annotate(lab, (i, list(r.values())[i]), fontsize=6, rotation=20, color="gray")
        axes[k].set(ylabel="in-sample R2", title=f"{g.upper()}: dR2_O={pl[g]['dR2_O']:.3f}, LOO dR2={pl[g]['LOO_dR2_O']:.3f}")
        axes[k].tick_params(axis="x", rotation=30, labelsize=7)
        axes[k].legend(fontsize=7)
    save(fig, "fig4_r2_ladder")


def fig5():
    rt = pd.read_csv(C.RES / "cell_table.csv")
    rt = rt[(rt.model == "gemma") & rt.cell.str.startswith("CF_")]
    conds = {c["cell"]: c for c in FP["confirmation_condition_list"]}
    order = [c for c in sorted(conds, key=lambda c: conds[c]["priority"]) if c in set(rt.cell)]
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    cols = {"refused": "#444444", "partial": "#e6a817", "complied": "#8fbc8f", "invalid": "#c0392b"}
    for k, g in enumerate(C.LANGS):
        d = rt[rt.lang == g].set_index("cell").reindex(order)
        bottom = np.zeros(len(order))
        for c, col in cols.items():
            axes[k].bar(range(len(order)), d[c].values, bottom=bottom, color=col, label=c.upper() if k == 0 else None)
            bottom += np.nan_to_num(d[c].values)
        axes[k].set(ylabel=f"{g.upper()} share (CONF harmful)")
    axes[1].set_xticks(range(len(order)))
    axes[1].set_xticklabels([o.replace("CF_", "") for o in order], rotation=75, fontsize=6)
    axes[0].legend(ncol=4, fontsize=7)
    save(fig, "fig5_fourway_bars")


def fig6():
    o = A.get("outside", {})
    if o.get("status") != "RUN":
        return
    langs = list(o.get("per_language", {}))
    if not langs:
        return
    fig, axes = plt.subplots(1, len(langs), figsize=(3.2 * len(langs), 3))
    axes = np.atleast_1d(axes)
    for ax, g in zip(axes, langs):
        rec = o["per_language"][g]
        ax.scatter([c["O"] for c in rec["cells"]], [c["residual"] for c in rec["cells"]], color=COL[g], s=18)
        ax.axhline(rec["noop_refusal"], color="k", ls=":", lw=0.8)
        ax.set(xlabel=f"O_{g.upper()}", ylabel="residual refusal", title=f"Qwen3-8B {g.upper()}: rho={rec['spearman_O']:.2f}")
    save(fig, "fig6_outside_family")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6):
        try:
            f()
        except (KeyError, ValueError, TypeError, IndexError) as e:
            print(f"{f.__name__} failed: {e!r}")
            raise
    print("figures written")

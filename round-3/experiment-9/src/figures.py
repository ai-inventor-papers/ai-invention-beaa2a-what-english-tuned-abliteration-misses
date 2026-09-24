#!/usr/bin/env python3
"""Figures (PDF + PNG) straight from results/analysis_summary.json, results/cells.parquet, results/redundancy_index.json.
fig1 cumulative-coverage curves per language with index_L; fig2 matched-energy paired plot (EN / SL panels, with random
and PC controls); fig3 index-predicted vs observed residual; fig4 per-layer write-mass profile; fig5 coverage x strength
heatmap of SL residual; fig6 collateral (SL FLORES dNLL) vs SL residual."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import alib as A  # noqa: E402
import common as C  # noqa: E402

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"en": "#1f77b4", "sl": "#d62728"}


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(C.FIGS / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig1(red):
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.2), sharey=True)
    for ax, fam in zip(axes, ("prefix", "suffix")):
        for g in C.LANGS:
            r = red["index"][g][fam]
            ax.plot(r["k"], r["curve"], "o-", color=COL[g], label=f"{g.upper()} (index={r['index']}{'*' if r['censored'] else ''})", ms=3)
            if not r["censored"]:
                ax.axvline(r["index"], color=COL[g], ls=":", lw=1)
        ax.axhline(0.5, color="grey", lw=0.8, ls="--")
        ax.set_xlabel("layers covered k (" + ("1..k" if fam == "prefix" else "49-k..48") + ")")
        ax.set_title(f"{fam} family (DEV, S3 half A)")
        ax.legend(frameon=False)
    axes[0].set_ylabel("judged harmful refusal")
    save(fig, "fig1_cumulative_coverage")


def fig2(S):
    P = S["P2_screen"]
    if not P.get("groups"):
        return
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.4), sharey=True)
    for ax, g in zip(axes, ("EN", "SL")):
        for i, (gn, r) in enumerate(sorted(P["groups"].items())):
            ax.plot([0, 1], [r[f"{g}_narrow"], r[f"{g}_broad"]], "o-", color="k", lw=1.5, label="d_EN(h)" if i == 0 else None)
            ax.text(1.03, r[f"{g}_broad"], gn, fontsize=7, va="center")
            if g == "SL" and "random_SL_narrow" in r:
                ax.plot([0, 1], [r["random_SL_narrow"], r["random_SL_broad"]], "s--", color="#999", lw=1, ms=3,
                        label="matched random" if i == 0 else None)
            if g == "SL" and "pc_SL_narrow" in r:
                ax.plot([0, 1], [r["pc_SL_narrow"], r["pc_SL_broad"]], "^:", color="#8c564b", lw=1, ms=3,
                        label="matched PC" if i == 0 else None)
        ax.set_xticks([0, 1], ["narrow & strong", "broad & weak"])
        ax.set_xlim(-0.2, 1.3)
        ax.set_title(f"{g}: matched-energy pairs (screen)")
    axes[0].set_ylabel("judged harmful refusal")
    axes[1].legend(frameon=False, fontsize=7)
    save(fig, "fig2_matched_energy")


def fig3(T, fp):
    if not fp:
        return
    W = T[(T["family"] == "weight") & (T["stage"] == "screen")]
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.4))
    for ax, g in zip(axes, C.LANGS):
        pred = [A.predict_from_curve(fp["P3"]["prefix_curves"][g], k) for k in W["k_eff"]]
        ax.scatter(pred, W[f"{g}_harm_refused"], s=12, color=COL[g])
        ax.plot([0, 1], [0, 1], color="grey", lw=0.8, ls="--")
        ax.set_xlabel("DEV-index predicted refusal")
        ax.set_ylabel("observed refusal (screen)")
        ax.set_title(g.upper())
    save(fig, "fig3_index_prediction")


def fig4(S):
    W = S.get("write_mass_exploratory") or {}
    if "en" not in W:
        return
    fig, ax = plt.subplots(figsize=(7, 3))
    for g in C.LANGS:
        ax.plot(range(1, 49), W[g]["profile"], color=COL[g], label=f"{g.upper()} (80% mass in {W[g]['n_layers_80pct_mass']} layers)")
    ax.set_xlabel("layer")
    ax.set_ylabel("share of |harm-minus-harmless write| along d_EN(h)")
    ax.legend(frameon=False)
    ax.set_title("EXPLORATORY per-layer write mass (DEV)")
    save(fig, "fig4_write_mass")


def fig5(T):
    W = T[(T["family"] == "weight") & T["coverage"].notna() & T["c"].notna() & (T["stage"] == "screen")]
    W = W[W["cell"].str.startswith("W_")]
    if W.empty:
        return
    covs = [c for c in ["B1", "B2", "B3", "B4", "C24", "C36", "S2", "S4", "K96", "ALL48"] if c in set(W["coverage"])]
    cs = sorted(W["c"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for ax, g in zip(axes, C.LANGS):
        M = np.full((len(covs), len(cs)), np.nan)
        for _, r in W.iterrows():
            if r["coverage"] in covs:
                M[covs.index(r["coverage"]), cs.index(r["c"])] = r[f"{g}_harm_refused"]
        im = ax.imshow(M, vmin=0, vmax=1, cmap="viridis", aspect="auto")
        for i in range(len(covs)):
            for j in range(len(cs)):
                if np.isfinite(M[i, j]):
                    ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6, color="w" if M[i, j] < 0.6 else "k")
        ax.set_xticks(range(len(cs)), [f"{c:g}" for c in cs])
        ax.set_yticks(range(len(covs)), covs)
        ax.set_xlabel("strength c")
        ax.set_title(f"{g.upper()} judged harmful refusal")
    fig.colorbar(im, ax=axes, shrink=0.8)
    save(fig, "fig5_coverage_strength_heatmap")


def fig6(T):
    W = T[T["stage"] == "screen"]
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    mk = {"weight": ("o", "k"), "random": ("s", "#999"), "pc": ("^", "#8c564b"), "act": ("D", "#2ca02c"), "lora": ("*", "#9467bd"),
          "lora+act": ("P", "#9467bd"), "noop": ("X", "#ff7f0e")}
    for fam, d in W.groupby("family"):
        m, c = mk.get(fam, ("o", "k"))
        ax.scatter(d["flores_sl"], d["sl_harm_refused"], marker=m, color=c, s=16, label=fam)
    ax.set_xlabel("SL FLORES dNLL (nats/token)")
    ax.set_ylabel("SL judged harmful refusal")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig6_collateral_vs_residual")


def main():
    S = C.jload(C.RES / "analysis_summary.json")
    T = pd.read_parquet(C.RES / "cells.parquet")
    red = C.jload(C.RES / "redundancy_index.json")
    fp = C.jload(C.RES / "frozen_predictions.json") if (C.RES / "frozen_predictions.json").exists() else None
    fig1(red)
    fig2(S)
    fig3(T, fp)
    fig4(S)
    fig5(T)
    fig6(T)
    print("figures written:", sorted(p.name for p in C.FIGS.glob("*.png")))


if __name__ == "__main__":
    main()

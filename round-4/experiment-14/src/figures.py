#!/usr/bin/env python3
"""figures/ - every figure is drawn straight from results/analysis_summary.json + configs/frozen_predictions.json,
so no figure can disagree with a table. Vector PDF plus PNG, Type-42 fonts, colour-blind-safe palette."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common as C
from common import jload, setup_logging

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 9, "axes.grid": True,
                     "grid.alpha": 0.3, "figure.dpi": 150, "savefig.bbox": "tight"})
BL, OR, GR, PU, GY = "#0072B2", "#D55E00", "#009E73", "#CC79A7", "#555555"
BANDS = [(1, 12), (13, 24), (25, 36), (37, 48)]


def save(fig, name: str) -> None:
    C.FIGS.mkdir(exist_ok=True)
    fig.savefig(C.FIGS / f"{name}.pdf")
    fig.savefig(C.FIGS / f"{name}.png")
    plt.close(fig)
    print("wrote", C.FIGS / f"{name}.pdf")


def main() -> None:
    setup_logging("figures")
    F = jload(C.CFG / "frozen_predictions.json")
    an = jload(C.RES / "analysis_summary.json")
    rows = an["cells"]

    # ---- fig1: the causal write profile
    fig, ax = plt.subplots(figsize=(7, 3.2))
    h = np.arange(1, 49)
    ax.plot(h, np.array(F["e_en"])[1:], "-o", ms=3, color=BL, label="e_EN(h)")
    ax.plot(h, np.array(F["e_sl"])[1:], "-s", ms=3, color=OR, label="e_SL(h)")
    ax.plot(h, np.array(F["e_sl_smooth"])[1:], "--", color=OR, alpha=0.6, lw=1, label="e_SL smoothed")
    for i, (a, b) in enumerate(BANDS):
        ax.axvspan(a - 0.5, b + 0.5, color=GY, alpha=0.06 if i % 2 else 0.12)
    wb = F["predicted_winning_band"]["sl"].split("-")
    ax.axvspan(int(wb[0]) - 0.5, int(wb[1]) + 0.5, color=GR, alpha=0.15,
               label=f"DEV-named band SL {F['predicted_winning_band']['sl']}")
    ax.axvline(13, color=PU, ls=":", lw=1)
    ax.axvline(24, color=PU, ls=":", lw=1, label="sibling checkpoint's band 13-24")
    ax.set_xlabel("hidden index h (layer l = h-1 edited with d_EN(h))")
    ax.set_ylabel("judged refusal drop\n(single-layer edit, DEV)")
    ax.set_title(f"Causal write profile of the refusal edit, GaMS3-12B-Instruct (c = {F['profile_rates']['c_star']})")
    ax.legend(fontsize=7, ncol=2)
    save(fig, "fig1_write_profile")

    # ---- fig2: O against the outcome, with the competitors
    conf = [c for c in rows if c.startswith("C_") and rows[c]["sl_harm_n"] >= 40]
    if conf:
        keys = [("O_sl", "O (frozen overlap)"), ("logE", "log total removal energy"), ("O_cos", "EN/SL direction cosine overlap"),
                ("mean_depth", "mean edited depth")]
        fig, axes = plt.subplots(1, len(keys), figsize=(3.1 * len(keys), 3.0), sharey=True)
        for ax, (k, lab) in zip(np.atleast_1d(axes), keys):
            for lvl, mk, col in (("E2", "o", BL), ("E3", "s", OR)):
                cs = [c for c in conf if rows[c]["level"] == lvl]
                ax.scatter([rows[c][k] for c in cs], [rows[c]["sl_harm_strict"] for c in cs], marker=mk, color=col,
                           s=26, label=f"E = {lvl}")
            r = (an.get("primary", {}).get("sl", {}).get("rho") if k == "O_sl"
                 else an.get("competitors", {}).get("sl", {}).get(k, {}).get("rho"))
            ax.set_xlabel(lab, fontsize=8)
            ax.set_title(f"Spearman {r:+.2f}" if isinstance(r, float) else "", fontsize=9)
        np.atleast_1d(axes)[0].set_ylabel("Slovene strict refusal\n(held-out harm categories)")
        np.atleast_1d(axes)[0].legend(fontsize=7)
        fig.suptitle("Out-of-sample: what orders the matched-energy confirmation cells?", fontsize=10)
        save(fig, "fig2_O_vs_outcome")

    # ---- fig3: the matched-energy band comparison
    bands = [f"B{i+1}" for i in range(4)]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, lvl in zip(axes, ("E2", "E3")):
        xs, en, sl, inv = [], [], [], []
        for b in bands:
            c = f"C_{b}_{lvl}"
            if c in rows and rows[c]["sl_harm_n"] >= 20:
                xs.append(f"{b}\n{BANDS[int(b[1])-1][0]}-{BANDS[int(b[1])-1][1]}")
                en.append(rows[c]["en_harm_strict"])
                sl.append(rows[c]["sl_harm_strict"])
                inv.append(rows[c]["sl_harm_invalid"])
        x = np.arange(len(xs))
        ax.bar(x - 0.2, en, 0.35, color=BL, label="EN strict refusal")
        ax.bar(x + 0.2, sl, 0.35, color=OR, label="SL strict refusal")
        ax.plot(x + 0.2, inv, "kv", ms=5, label="SL INVALID")
        noop = rows.get("R_NOOP")
        if noop:
            ax.axhline(noop["sl_harm_strict"], color=GY, ls="--", lw=1, label="no-op SL")
        ax.set_xticks(x)
        ax.set_xticklabels(xs, fontsize=8)
        ax.set_title(f"matched energy {lvl}", fontsize=9)
    axes[0].set_ylabel("rate on held-out harm categories")
    axes[0].legend(fontsize=7)
    fig.suptitle("Where the same edit energy is placed decides what it removes", fontsize=10)
    save(fig, "fig3_matched_energy_bands")

    # ---- fig4: the dissociation ladder
    dis = an.get("dissociation", {})
    arms = [a for a in ("A1", "A2", "A3", "A4") if a in dis]
    if arms:
        fig, ax = plt.subplots(figsize=(4.6, 3.4))
        for a in arms:
            v = dis[a]
            ax.scatter(v["E"], v["O_sl"], s=140, color=GR if a in ("A1", "A4") else PU, alpha=0.85)
            ax.annotate(f"{a}\nSL {v['sl_strict']:.2f}", (v["E"], v["O_sl"]), textcoords="offset points",
                        xytext=(8, -4), fontsize=8)
        for a, b in (("A1", "A4"), ("A2", "A3")):
            if a in dis and b in dis:
                ax.plot([dis[a]["E"], dis[b]["E"]], [dis[a]["O_sl"], dis[b]["O_sl"]], color=GY, lw=1, ls="--")
        ax.set_xlabel("total removal energy E (achieved dose)")
        ax.set_ylabel("O_SL (placement)")
        ax.set_title("Placement and dose, separated by construction", fontsize=10)
        save(fig, "fig4_dissociation")

    # ---- fig5: refusal removal against collateral, with the controls
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    groups = {"confirmation cells": ([c for c in conf], BL, "o"),
              "random controls": ([c for c in rows if c.startswith("X_RND")], GY, "^"),
              "PC controls": ([c for c in rows if c.startswith("X_PC")], PU, "v"),
              "A1-A4 ladder": ([c for c in rows if c[:2] in ("A1", "A2", "A3", "A4")], OR, "D")}
    for lab, (cs, col, mk) in groups.items():
        cs = [c for c in cs if rows[c].get("sl_harm_n", 0) >= 20]
        if cs:
            ax.scatter([rows[c]["flores_sl"] for c in cs], [rows[c]["sl_harm_strict"] for c in cs], marker=mk,
                       color=col, s=34, label=lab, alpha=0.85)
    noop = rows.get("R_NOOP")
    if noop:
        ax.scatter([noop["flores_sl"]], [noop["sl_harm_strict"]], marker="*", s=180, color=GR, label="no-op")
    ax.set_xlabel("FLORES per-token dNLL, Slovene (collateral)")
    ax.set_ylabel("Slovene strict refusal")
    ax.set_title("Refusal removal reported next to its damage", fontsize=10)
    ax.legend(fontsize=7)
    save(fig, "fig5_collateral")


if __name__ == "__main__":
    main()

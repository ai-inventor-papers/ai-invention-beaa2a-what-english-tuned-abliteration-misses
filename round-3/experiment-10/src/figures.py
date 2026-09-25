#!/usr/bin/env python3
"""Figures (PDF + PNG) from results/analysis_summary.json, results/redundancy_index.json and results/per_item.parquet.
fig1 depth-coverage curve per language with index_L; fig2 matched-energy paired plot (narrow vs broad, SL and EN);
fig3 index-vs-residual out-of-sample scatter; fig4 leave-one-band-out necessity profile; fig5 refusal-vs-collateral Pareto;
fig6 judge/label-source sensitivity with the PARTIAL column."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

import common as C
from common import jload, setup_logging

plt.rcParams.update({"figure.dpi": 150, "font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "pdf.fonttype": 42})
CL = {"en": "#1f77b4", "sl": "#d62728"}


def save(fig, name: str) -> None:
    C.FIGS.mkdir(exist_ok=True)
    fig.savefig(C.FIGS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(C.FIGS / f"{name}.png", bbox_inches="tight")
    plt.close(fig)
    logger.info(f"wrote figures/{name}.pdf")


def fig1(ri: dict) -> None:
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(5.2, 5.0), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for g in ("en", "sl"):
        ks = sorted(int(k) for k in ri["prefix_curves"][g])
        ax.plot(ks, [ri["prefix_curves"][g][str(k)] if str(k) in ri["prefix_curves"][g] else ri["prefix_curves"][g][k] for k in ks],
                "o-", color=CL[g], label=f"{g.upper()} (index {ri['index'][g]})")
        i = ri["index_numeric"][g]
        if i <= 48:
            ax.axvline(i, color=CL[g], ls=":", alpha=0.7)
        lo, hi = ri["index_boot_CI95"][g]
        ax.axvspan(lo, min(hi, 48), color=CL[g], alpha=0.08)
        ax.axhline(ri["noop_refusal"][g], color=CL[g], ls="--", lw=0.8, alpha=0.5)
    ax.axhline(0.5, color="k", lw=0.8)
    ax.set_ylabel("judged harmful REFUSED rate")
    ax.set_title(f"GaMS3: depth-coverage curve, DEV (n={ri['n_items']}/lang)\ndashed = unedited; shaded = 95% index CI")
    ax.legend(fontsize=8)
    for g in ("en", "sl"):
        cv = ri["prefix_invalid_curves"][g]
        ks = sorted(int(k) for k in cv)
        ax2.plot(ks, [cv[str(k)] if str(k) in cv else cv[k] for k in ks], "s--", color=CL[g], ms=4, label=g.upper())
    ax2.axhline(0.10, color="k", lw=0.8, ls=":")
    ax2.set_ylabel("INVALID rate")
    ax2.set_xlabel("cumulative prefix depth k (hidden indices 1..k ablated)")
    ax2.set_title("the same cells' unusable output (degenerate / wrong-language); dotted = the 0.10 usability bar",
                  fontsize=8)
    save(fig, "fig1_coverage_curve")


def fig2(S: dict) -> None:
    pb = S.get("frozen_predictions_result", {}).get("PB2")
    if not pb:
        return
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.4), sharey=True)
    for ax, g in zip(axes, ("sl", "en")):
        names, nr, br = [], [], []
        for gn, e in pb["groups"].items():
            names.append(f"{gn}\nE*={e['E_target']:.0f}")
            nr.append(e[f"{g}_narrow_rate"])
            br.append(e[f"{g}_broad_rate"])
        x = np.arange(len(names))
        ax.bar(x - 0.18, nr, 0.36, label="narrow & strong (B2, B3)", color="#7f7f7f")
        ax.bar(x + 0.18, br, 0.36, label="broad & weak (STR2, ALL)", color="#2ca02c")
        for gn, e, xi in zip(pb["groups"], pb["groups"].values(), x):
            d = e[g]
            ax.annotate(f"Δ={d['diff']:+.2f}\n[{d['ci'][0]:+.2f},{d['ci'][1]:+.2f}]", (xi, max(nr[int(xi)], br[int(xi)]) + 0.04),
                        ha="center", fontsize=6.5)
        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=7)
        ax.set_title(f"{g.upper()} harmful refusal", fontsize=9)
        ax.set_ylim(0, 1.15)
    axes[0].set_ylabel("judged REFUSED rate")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.suptitle(f"Matched total removal energy: narrow-and-strong vs broad-and-weak ({pb['split']} set)",
                 y=1.04, fontsize=10)
    fig.tight_layout()
    save(fig, "fig2_matched_energy")


def fig3(S: dict) -> None:
    pb = S.get("frozen_predictions_result", {}).get("PB4")
    if not pb:
        return
    fig, ax = plt.subplots(figsize=(4.4, 3.6))
    d = pd.DataFrame(pb["rows"])
    for g in ("en", "sl"):
        dd = d[d.lang == g]
        ax.scatter(dd.predicted, dd.observed, color=CL[g], label=g.upper(), s=26, alpha=0.8)
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set_xlabel("DEV-frozen index curve prediction at k = covered layers")
    ax.set_ylabel("observed REFUSED rate (weight cells)")
    ax.set_title(f"Out-of-sample: Spearman {pb['spearman']:.2f} (p={pb['p']:.3f}, n={pb['n']})")
    ax.legend(fontsize=8)
    save(fig, "fig3_index_vs_residual")


def fig4(ri: dict) -> None:
    fig, ax = plt.subplots(figsize=(5.0, 3.2))
    keys = sorted(ri["lobo_necessity_vs_all48"]["sl"])
    x = np.arange(len(keys))
    for i, g in enumerate(("en", "sl")):
        ax.bar(x + (i - 0.5) * 0.36, [ri["lobo_necessity_vs_all48"][g][k] for k in keys], 0.36, color=CL[g], label=g.upper())
    ax.set_xticks(x)
    ax.set_xticklabels([k.replace("LOBO_", "drop ") for k in keys], fontsize=7)
    ax.set_ylabel("Δ refusal vs all-48 ablation")
    ax.set_title("Leave-one-band-out necessity (higher = band is needed)")
    ax.legend(fontsize=8)
    save(fig, "fig4_lobo_necessity")


def fig5(S: dict) -> None:
    rows = []
    for cell, r in S["cell_table"].items():
        for split in ("screen", "confirm", "dev"):
            if f"{split}_sl_REFUSED" in r:
                rows.append({"cell": cell, "split": split, "ref": r[f"{split}_sl_REFUSED"],
                             "flores": r.get("flores_dNLL_sl", np.nan), "inv": r.get(f"{split}_sl_INVALID", 0),
                             "tier": r.get("tier"), "degraded": bool(r.get("degraded"))})
                break
    d = pd.DataFrame(rows).dropna(subset=["flores"])
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    for deg, mk, lab in ((False, "o", "clean"), (True, "x", "DEGRADED (gate 9)")):
        dd = d[d.degraded == deg]
        sc = ax.scatter(dd.flores, dd.ref, c=dd.inv, cmap="viridis", marker=mk, s=40, vmin=0, vmax=max(0.2, d.inv.max()), label=lab)
    plt.colorbar(sc, ax=ax, label="SL INVALID rate")
    ax.set_xlabel("SL FLORES ΔNLL (nats/token)")
    ax.set_ylabel("SL harmful REFUSED rate")
    ax.set_title("Refusal removal vs collateral damage (every cell)")
    ax.legend(fontsize=7)
    save(fig, "fig5_pareto")


def fig6(S: dict) -> None:
    df = pd.read_parquet(C.RES / "per_item.parquet")
    cells = [c for c in S["cell_table"] if S["cell_table"][c].get("tier") in ("T1", "T2")][:10]
    if not cells:
        cells = sorted(S["cell_table"])[:10]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = np.arange(len(cells))
    d = df[(df.lang == "sl") & df.cell.isin(cells) & df.split.isin(["screen", "confirm"])]
    ref = [float((d[d.cell == c].cls4_local == "REFUSED").mean()) for c in cells]
    par = [float((d[d.cell == c].cls4_local == "PARTIAL").mean()) for c in cells]
    rule = [float((d[d.cell == c].rule == "refused").mean()) for c in cells]
    api = [float((d[(d.cell == c) & d.cls4_api.notna()].cls4_api == "REFUSED").mean()) if (d[(d.cell == c)].cls4_api.notna()).any()
           else np.nan for c in cells]
    ax.bar(x - 0.27, ref, 0.27, label="local Qwen3-14B REFUSED", color="#1f77b4")
    ax.bar(x - 0.27, par, 0.27, bottom=ref, label="PARTIAL (counted as compliance)", color="#aec7e8")
    ax.bar(x, rule, 0.27, label="opener rule (3rd layer)", color="#ff7f0e")
    if not np.all(np.isnan(api)):
        ax.bar(x + 0.27, api, 0.27, label="gpt-4.1 (where on disk)", color="#2ca02c")
    ax.set_xticks(x)
    ax.set_xticklabels(cells, rotation=35, ha="right", fontsize=6.5)
    ax.set_ylabel("SL rate")
    ax.set_title("Label-source sensitivity (Slovene harmful)")
    ax.legend(fontsize=7)
    save(fig, "fig6_judge_sensitivity")


def main() -> None:
    setup_logging("figures")
    S = jload(C.RES / "analysis_summary.json")
    ri = jload(C.RES / "redundancy_index.json") if (C.RES / "redundancy_index.json").exists() else None
    if ri:
        fig1(ri)
        fig4(ri)
    fig2(S)
    fig3(S)
    fig5(S)
    fig6(S)


if __name__ == "__main__":
    main()

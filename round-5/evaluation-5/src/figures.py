#!/usr/bin/env python3
"""Three data figures from the shipped results (hand-written matplotlib on the aii-data-fig-gen house style).
fig_floor_threshold, fig_discrepancy_forest, fig_delta_lang_decomp -> figures/*.pdf + *.png"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from loguru import logger  # noqa: E402

from common import EXP15, FIG, RES, WS  # noqa: E402

# house-style helpers of the aii-data-fig-gen skill: found by walking up from this workspace (or $AII_DATA_FIG_GEN)
_skill = next((p / ".claude/skills/aii-data-fig-gen/scripts" for p in WS.parents
               if (p / ".claude/skills/aii-data-fig-gen/scripts").is_dir()), None)
sys.path.insert(0, str(Path(__import__("os").environ.get("AII_DATA_FIG_GEN", _skill or "."))))
from chart_style import (PALETTE, apply_house_style, assert_legends_clear_of_data,  # noqa: E402
                         clear_legends_of_data, fit_legends, fit_tick_labels, fit_titles, place_legend)
from chart_geometry import assert_text_is_legible  # noqa: E402

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs/figures.log", rotation="30 MB", level="DEBUG")


def finish(fig, name: str) -> None:
    fit_legends(fig); clear_legends_of_data(fig); fit_tick_labels(fig); fit_titles(fig); clear_legends_of_data(fig)
    for check in (assert_text_is_legible, assert_legends_clear_of_data):
        try:
            check(fig)
        except (AssertionError, ValueError, RuntimeError) as e:
            logger.warning(f"{name}: {check.__name__}: {e}")
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)
    logger.info(f"wrote figures/{name}.pdf/.png")


def fig_floor_threshold() -> None:
    pc = pd.read_csv(EXP15 / "results/per_candidate.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.8), layout="constrained", sharey=True)
    for ax, (model, title) in zip(axes, (("gemma", "gemma-3-12b-it search"), ("gams", "GaMS3-12B-Instruct search"))):
        d = pc[pc.model == model]
        below = d.C <= 10
        ax.axhspan(0, 10, color="0.9", zorder=0)
        ax.axvspan(0, 10, color="0.95", zorder=0)
        ax.plot([0, 100], [0, 100], color="0.6", lw=0.8, ls=":", zorder=1)
        ax.scatter(d.C[~below], d.K[~below], s=12, color=PALETTE[0], alpha=0.75, label="candidate", zorder=2)
        ax.scatter(d.C[below], d.K[below], s=22, color=PALETTE[1], marker="D",
                   label="reference places at/below threshold", zorder=3)
        ax.axhline(d.K.min(), color=PALETTE[2], lw=1.2, ls="--", label="objective floor (min K: 72 gemma, 16 GaMS3)")
        ax.axhline(10, color="k", lw=1.0, label="rule threshold (10)")
        ax.set_xlim(-2, 102); ax.set_ylim(-2, 102)
        ax.set_title(f"{title}\n{int(below.sum())}/{len(d)} at/below 10 by C; 0 by K", fontsize=8)
    fig.supxlabel("reference refusals / 100 (certified classifier C)", fontsize=9)
    axes[0].set_ylabel("keyword objective K / 100")
    place_legend(axes[0], loc="center right", fontsize=6.5)
    finish(fig, "fig_floor_threshold")


def fig_discrepancy_forest() -> None:
    d = pd.read_csv(RES / "discrepancy_per_cell.csv")
    a = d[(d.artifact == "exp4") & (d.set == "S5") & (d.channel.isin(["qwen", "polyguard"]))].copy()
    b = d[(d.artifact == "exp11") & (d.set == "S4hoc") & (d.channel == "qwen")].copy()
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 5.6), layout="constrained")
    col = {("en", "qwen"): PALETTE[0], ("sl", "qwen"): PALETTE[1], ("en", "polyguard"): PALETTE[2],
           ("sl", "polyguard"): PALETTE[3]}
    for ax, t, title, lloc in ((axes[0], a, "RefusEU S5 (unpaired rows), exp4 checkpoints", "upper right"),
                               (axes[1], b, "held-out StrongREJECT S4hoc, exp11 arms (Qwen judge)", "upper left")):
        t = t.sort_values(["unit", "lang", "channel"]).reset_index(drop=True)
        y = np.arange(len(t))[::-1]
        seen = set()
        for yi, r in zip(y, t.itertuples()):
            key = (r.lang, r.channel)
            lab = f"{r.lang.upper()} vs {'Qwen3-14B judge' if r.channel == 'qwen' else 'PolyGuard refusal'}"
            ax.errorbar(r.d_signed, yi, xerr=[[r.d_signed - r.d_ci_lo], [r.d_ci_hi - r.d_signed]], fmt="o", ms=3.5,
                        color=col[key], lw=1, capsize=1.5, label=None if lab in seen else lab)
            seen.add(lab)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{r.unit} {r.lang}" for r in t.itertuples()], fontsize=6.5)
        ax.set_xlim(-1.05, 1.05)
        ax.set_xlabel("d = P(keyword) - P(reference)")
        ax.set_title(title, fontsize=8.5)
        place_legend(ax, loc=lloc, fontsize=6.5)
    finish(fig, "fig_discrepancy_forest")


def fig_delta_lang_decomp() -> None:
    dl = pd.read_csv(RES / "delta_lang.csv")
    t = dl[(dl.channel == "qwen") & (dl.pair_set == "S5X")].reset_index(drop=True)
    labels = [f"{r.artifact}:{r.unit}" for r in t.itertuples()]
    x = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7.4, 3.9), layout="constrained")
    s, rc = t.silence_component.values, t.reference_component.values
    pos_b = np.zeros(len(t)); neg_b = np.zeros(len(t))
    for vals, colr, lab in ((s, PALETTE[1], "rule positive-rate shift (SL minus EN keyword rate)"),
                            (rc, PALETTE[0], "reference-level difference (-(SL minus EN reference rate))")):
        bottom = np.where(vals >= 0, pos_b, neg_b)
        ax.bar(x, vals, bottom=bottom, color=colr, width=0.62, label=lab)
        pos_b = pos_b + np.where(vals >= 0, vals, 0); neg_b = neg_b + np.where(vals < 0, vals, 0)
    ax.errorbar(x, t.delta_lang, yerr=[t.delta_lang - t.delta_lang_ci95_lo, t.delta_lang_ci95_hi - t.delta_lang],
                fmt="D", color="k", ms=3.5, lw=1, capsize=2, label="Delta_lang = d_SL - d_EN (95% paired bootstrap)")
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
    ax.set_ylabel("refusal-rate units")
    ax.set_ylim(-2.0, 0.45)
    ax.set_title("Language dependence of the keyword discrepancy on 100 verified EN-SL pairs (Qwen3-14B reference)", fontsize=8.5)
    place_legend(ax, loc="upper right", fontsize=6.5)
    finish(fig, "fig_delta_lang_decomp")


@logger.catch(reraise=True)
def main() -> None:
    apply_house_style()
    fig_floor_threshold()
    fig_discrepancy_forest()
    fig_delta_lang_decomp()


if __name__ == "__main__":
    main()

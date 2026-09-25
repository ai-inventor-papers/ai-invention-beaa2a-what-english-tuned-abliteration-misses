"""Figures: fig_gap_forest, fig_judge_stack, fig_kappa_inflation (house style of the aii-data-fig-gen skill)."""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "/ai-inventor/.claude/skills/aii-data-fig-gen/scripts")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from chart_geometry import assert_text_is_legible  # noqa: E402
from chart_style import (PALETTE, apply_house_style, assert_legends_clear_of_data, clear_legends_of_data, fit_legends,  # noqa: E402
                         fit_tick_labels, fit_titles, place_legend)

from lib import FIG, RES  # noqa: E402

JN = {"qwen3_14b": "Qwen3-14B", "gpt41": "gpt-4.1", "nemotron": "Nemotron", "gemma_self": "Gemma self-judge", "keyword": "keyword rule"}


def finish(fig, name):
    fit_legends(fig)
    clear_legends_of_data(fig)
    fit_tick_labels(fig)
    fit_titles(fig)
    clear_legends_of_data(fig)
    assert_text_is_legible(fig)
    assert_legends_clear_of_data(fig)
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


def gap_forest():
    G = pd.read_csv(RES / "gap_range.csv")
    G = G[G.checkpoint.isin(["gemma_edit", "community_ref", "gams_edit"]) & G.gap.notna() & (G.n_en.fillna(0) >= 30)]
    short = {"exp4 S5X (paired, verified translations)": "S5X paired", "exp4 S5 (RefusEU, unpaired)": "S5 RefusEU",
             "exp5 S4 harmful (twins)": "S4 twins", "exp8 W0 S4-hoc": "S4-hoc (W0)", "exp8 C0 S4-hoc": "S4-hoc (C0)",
             "exp7 ET_096 JBB (self-judge)": "JBB (exp7)", "iter-1 exp1 harmful_behaviors": "HB-100 (iter 1)", "exp6 core JBB": "JBB (exp6)"}
    ck = {"gemma_edit": "Gemma edit", "community_ref": "Community", "gams_edit": "GaMS3 edit"}
    G = G.assign(row=[f"{ck[c]} | {short[d]} | {JN[j]}" for c, d, j in zip(G.checkpoint, G.dataset, G.judge)])
    order = []
    for c in ("gemma_edit", "community_ref", "gams_edit"):
        for d in short:
            for j in ("qwen3_14b", "gpt41", "nemotron", "gemma_self", "keyword"):
                r = G[(G.checkpoint == c) & (G.dataset == d) & (G.judge == j)]
                if len(r):
                    order.append(r.row.iloc[0])
    apply_house_style()
    fig, ax = plt.subplots(figsize=(7, 8.2), layout="constrained")
    y = {r: i for i, r in enumerate(order)}
    for k, (defn, lab) in enumerate((("strict", "strict: refused"), ("broad", "broad: refused + partial"))):
        h = G[G.definition == defn]
        yy = np.array([y[r] for r in h.row]) + (-0.17 if k == 0 else 0.17)
        lo = (h.gap - h.ci_low).clip(lower=0).fillna(0).values
        hi = (h.ci_high - h.gap).clip(lower=0).fillna(0).values
        ax.errorbar(h.gap.values, yy, xerr=[lo, hi], fmt="o" if k == 0 else "s", color=PALETTE[k], ecolor=PALETTE[k], elinewidth=1.1,
                    capsize=2, markersize=5, label=lab)
    ax.axvline(0, color="#999999", linestyle="--", linewidth=1)
    ax.set_yticks(range(len(order)), labels=order, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel("SL − EN refusal rate (95% CI)")
    ax.set_title("SL−EN refusal gap by checkpoint, dataset and judge")
    ax.grid(axis="x", visible=True)
    ax.grid(axis="y", visible=False)
    place_legend(ax, loc="lower right")
    finish(fig, "fig_gap_forest")


def judge_stack():
    J = pd.read_csv(RES / "judge_sensitivity.csv")
    sel = [("exp4", "S5", "gemma_edit"), ("exp4", "S5", "gams_edit"), ("exp4", "S5", "community_ref"), ("exp5", "s4_harmful", "gemma:edit"),
           ("exp8", "hoc_harmful", "gemma:W0"), ("exp8", "jbb_harmful", "gemma:A1")]
    names = {"gemma_edit": "Gemma edit", "gams_edit": "GaMS3 edit", "community_ref": "Community", "gemma:edit": "Gemma edit", "gemma:W0": "Gemma W0",
             "gemma:A1": "Gemma A1"}
    rows = []
    for art, ds, cell in sel:
        for lang in ("en", "sl"):
            h = J[(J.artifact == art) & (J.dataset == ds) & (J.cell == cell) & (J.lang == lang) & (J.judge != "keyword")]
            for _, r in h.iterrows():
                rows.append(dict(label=f"{names[cell]} {ds.replace('_harmful', '')} {lang.upper()} · {JN[r.judge]} (n={r.n})",
                                 R=r.p_refused, P=r.p_partial, C=r.p_complied, I=r.p_invalid))
    D = pd.DataFrame(rows)
    apply_house_style()
    fig, ax = plt.subplots(figsize=(7, 7.5), layout="constrained")
    y = np.arange(len(D))
    left = np.zeros(len(D))
    for k, (c, lab) in enumerate((("R", "refused"), ("P", "partial"), ("C", "complied"), ("I", "invalid"))):
        ax.barh(y, D[c].values, left=left, color=PALETTE[k], label=lab, height=0.75)
        left += D[c].values
    ax.set_yticks(y, labels=D.label, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of judged harmful prompts")
    ax.set_title("Where the edited checkpoints' outputs go, per judge")
    place_legend(ax, loc="lower right")
    finish(fig, "fig_judge_stack")


def kappa_inflation():
    A = pd.read_csv(RES / "judge_agreement.csv")
    A = A[(A.definition == "binary") & A.scope.isin(["pooled_all", "pooled_orig", "pooled_edited"]) & A.kappa.notna()]
    pairs = [("exp4", "gpt41", "qwen3_14b"), ("exp5", "gpt41", "nemotron"), ("exp6", "gpt41", "qwen3_14b"), ("exp8", "gpt41", "qwen3_14b"),
             ("exp4", "qwen3_14b", "keyword"), ("exp8", "qwen3_14b", "keyword"), ("exp7", "gemma_self", "keyword")]
    cats = [f"{a}: {JN[x]} vs {JN[y]}" for a, x, y in pairs]
    apply_house_style()
    fig, ax = plt.subplots(figsize=(7, 4.6), layout="constrained")
    w = 0.26
    for k, (sc, lab) in enumerate((("pooled_all", "pooled (orig + edited)"), ("pooled_orig", "originals only"), ("pooled_edited", "edited only"))):
        vals, lo, hi = [], [], []
        for a, x, yj in pairs:
            r = A[(A.artifact == a) & (A.judge_a == x) & (A.judge_b == yj) & (A.scope == sc)]
            v = float(r.kappa.iloc[0]) if len(r) else np.nan
            vals.append(v)
            lo.append(v - float(r.kappa_ci_low.iloc[0]) if len(r) else 0)
            hi.append(float(r.kappa_ci_high.iloc[0]) - v if len(r) else 0)
        yy = np.arange(len(pairs)) + (k - 1) * w
        ax.barh(yy, np.nan_to_num(vals), height=w, color=PALETTE[k], label=lab, xerr=[lo, hi], error_kw=dict(ecolor="#333333", lw=0.8, capsize=2))
    ax.set_yticks(range(len(pairs)), labels=cats, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(-0.1, 1.05)
    ax.set_xlabel("Cohen κ, refused vs not (95% item-bootstrap CI)")
    ax.set_title("Pooled judge agreement overstates agreement on edited outputs")
    place_legend(ax, loc="lower left")
    finish(fig, "fig_kappa_inflation")


if __name__ == "__main__":
    for f in (gap_forest, judge_stack, kappa_inflation):
        try:
            f()
            print("ok", f.__name__)
        except Exception as e:
            print("FAILED", f.__name__, repr(e))

#!/usr/bin/env python3
"""STAGE 8 - figures. Every panel is drawn from the saved result files only (results/indices.json, results/analysis.json,
results/<m>/direction_diagnostics.json, results/<m>/panel_collateral.json); nothing is recomputed from generations here.
fig1 depth-coverage refusal curves per model; fig2 index vs residual scatter; fig3 matched-energy W1 vs W2 per language;
fig4 predictor comparison; fig5 4-way class composition per cell x language; fig6 per-layer cos(d_EN, d_L) profiles."""
from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

import common as C

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8, "axes.grid": True, "grid.alpha": 0.3,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
LC = {"en": "#1f77b4", "sl": "#d62728", "de": "#2ca02c", "lt": "#9467bd"}
MK = {"gemma": "o", "qwen3": "s", "mistral": "^"}
KS = [0.0, 0.10, 0.25, 0.50, 0.75, 1.00]


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(C.FIGS / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)
    logger.info(f"figures/{name}.pdf")


def wilson_err(p, n):
    if not n or p != p:
        return 0.0, 0.0
    lo, hi = C.wilson(int(round(p * n)), n)
    return max(0.0, p - lo), max(0.0, hi - p)


def fig1(idx, models):
    fig, axes = plt.subplots(1, len(models), figsize=(3.1 * len(models), 2.8), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, models):
        for L in C.LANGS:
            t = idx["table"][f"{m}|{L}"]
            cur = [t["curve"][str(k)] for k in KS]
            det = idx["curves"][f"{m}|{L}"]
            ns = [det[c]["n_den"] for c in ("dev_k0", "dev_P10", "dev_P25", "dev_P50", "dev_P75", "dev_P100")]
            err = np.array([wilson_err(p, n) for p, n in zip(cur, ns)]).T
            ax.errorbar(KS, cur, yerr=err, marker="o", ms=3, lw=1.2, color=LC[L], capsize=2,
                        label=f"{L.upper()} (index {t['index']:g})")
            ax.scatter([1.03], [det["dev_SS"]["refusal"]], marker="x", color=LC[L], s=22)
            ax.scatter([1.09], [det["dev_RND"]["refusal"]], marker="+", color=LC[L], s=26)
        ax.axhline(0.5, color="k", ls=":", lw=0.8)
        ax.set_title(m, fontsize=9)
        ax.set_xlabel("cumulative depth coverage k")
        ax.legend(fontsize=5.5, loc="lower left")
    axes[0].set_ylabel("judged harmful refusal")
    axes[0].set_ylim(-0.03, 1.03)
    fig.suptitle("Depth-coverage curves (x = single site h*, + = matched random at full depth)", fontsize=8)
    save(fig, "fig1_depth_curves")


def fig2(idx, A, models):
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for r in A["rows"]:
        ax.scatter(r["index"], r["residual"], marker=MK.get(r["m"], "o"), color=LC[r["L"]], s=34,
                   edgecolor="k", linewidth=0.4, alpha={"W1": 0.45, "W2": 0.75, "W3": 1.0}[r["c"]])
    xs = [r["index"] for r in A["rows"]]
    ys = [r["residual"] for r in A["rows"]]
    if len(xs) > 2:
        b = np.polyfit(xs, ys, 1)
        g = np.linspace(min(xs), max(xs), 10)
        ax.plot(g, np.polyval(b, g), "k--", lw=0.9)
    ax.set_xlabel(f"frozen DEV {A['primary_predictor']} (activation ablation)")
    ax.set_ylabel("residual refusal after English weight edit (CONF)")
    ax.set_title(f"Spearman = {A['P1']['spearman']:.2f} "
                 f"[{A['P1']['item_boot_ci95'][0]:.2f}, {A['P1']['item_boot_ci95'][1]:.2f}]", fontsize=8)
    h = [plt.Line2D([], [], marker=MK.get(m, "o"), ls="", color="gray", label=m) for m in models]
    h += [plt.Line2D([], [], marker="o", ls="", color=LC[L], label=L.upper()) for L in C.LANGS]
    ax.legend(handles=h, fontsize=6, ncol=2)
    save(fig, "fig2_index_vs_residual")


def fig3(A, models):
    fig, ax = plt.subplots(figsize=(4.4, 2.9))
    rows = A["P3"]["rows"]
    xs = np.arange(len(rows))
    err = np.array([[abs(r["W2_minus_W1"] - r["ci95"][0]), abs(r["ci95"][1] - r["W2_minus_W1"])] for r in rows]).T
    ax.bar(xs, [r["W2_minus_W1"] for r in rows], color=[LC[r["L"]] for r in rows], yerr=err, capsize=2)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{r['m'][:4]}\n{r['L'].upper()}\n(idx {r['index']:g})" for r in rows], fontsize=5.5)
    ax.set_ylabel("refusal(W2 stride) - refusal(W1 narrow)")
    ax.set_title(f"Matched-energy contrast; Spearman vs index = {A['P3']['spearman_index_vs_W2minusW1']:.2f}", fontsize=8)
    save(fig, "fig3_matched_energy")


def fig4(A):
    fig, ax = plt.subplots(figsize=(4.0, 2.8))
    names = [("index", A["P1"]["spearman"], None)] + [(b, A["P4"][b]["spearman"], A["P4"][b]["diff_ci95"])
                                                      for b in ("B_cos", "B_ss", "B_base", "B_margin")]
    lbl = {"index": "depth index", "B_cos": "EN/L direction cosine", "B_ss": "single-site transfer",
           "B_base": "baseline refusal", "B_margin": "first-token margin"}
    ax.barh(range(len(names)), [v for _, v, _ in names],
            color=["#333333"] + ["#999999"] * (len(names) - 1))
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([lbl[n] for n, _, _ in names], fontsize=7)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("Spearman with residual refusal")
    ax.set_title("Predictor comparison (CI = paired item bootstrap on the difference vs index)", fontsize=7)
    for i, (n, v, ci) in enumerate(names):
        if ci:
            ax.text(v + 0.02, i, f"Δ{A['P4'][n]['index_minus_baseline']:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}]", fontsize=5,
                    va="center")
    save(fig, "fig4_predictors")


def fig5(A, models):
    cells = ["W0", "W1", "W2", "W3", "W4"]
    fig, axes = plt.subplots(len(models), 1, figsize=(5.6, 2.1 * len(models)), sharex=True)
    axes = np.atleast_1d(axes)
    cols = {"REFUSED": "#4c72b0", "PARTIAL": "#dd8452", "COMPLIED": "#c44e52", "INVALID": "#8c8c8c"}
    for ax, m in zip(axes, models):
        labels, bottoms = [], None
        data = {k: [] for k in cols}
        for c in cells:
            for L in C.LANGS:
                cell = A["cells"].get(f"{m}|{L}|{c}")
                labels.append(f"{c}\n{L.upper()}")
                if cell is None:
                    for k in cols:
                        data[k].append(0.0)
                    continue
                data["REFUSED"].append(cell["residual"] * (1 - (cell["invalid_share"] or 0)))
                data["PARTIAL"].append(cell["partial_share"] or 0)
                data["COMPLIED"].append(cell["complied_share"] or 0)
                data["INVALID"].append(cell["invalid_share"] or 0)
        xs = np.arange(len(labels))
        bottoms = np.zeros(len(labels))
        for k in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID"):
            ax.bar(xs, data[k], bottom=bottoms, color=cols[k], label=k, width=0.8)
            bottoms += np.array(data[k])
        ax.set_ylabel(m, fontsize=8)
        ax.set_xticks(xs)
        ax.set_xticklabels(labels, fontsize=4.5)
    axes[0].legend(fontsize=5.5, ncol=4)
    fig.suptitle("Judged 4-way outcome composition per cell x language (CONF harmful)", fontsize=8)
    save(fig, "fig5_label_composition")


def fig6(models):
    fig, axes = plt.subplots(1, len(models), figsize=(3.1 * len(models), 2.6), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, m in zip(axes, models):
        d = C.jload(C.RES / m / "direction_diagnostics.json")
        H = len(d["cos_profile_sl"])
        rel = np.arange(H) / (H - 1)
        for L in ("sl", "de", "lt"):
            ax.plot(rel, d[f"cos_profile_{L}"], color=LC[L], lw=1.2, label=f"cos(d_EN, d_{L.upper()})")
        ax.plot(rel, d["split_half_ceiling_en"], "k:", lw=1, label="EN split-half ceiling")
        ax.plot(rel, d["auroc"], color="gray", lw=0.8, ls="--", label="EN AUROC")
        ax.axvline(d["h_star"] / (H - 1), color="k", lw=0.6)
        ax.set_title(m, fontsize=9)
        ax.set_xlabel("relative depth")
    axes[0].set_ylabel("cosine / AUROC")
    axes[0].legend(fontsize=5.5, loc="lower right")
    save(fig, "fig6_cosine_profiles")


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("figures")
    idx = C.jload(C.RES / "indices.json")
    models = sorted({v["model"] for v in idx["table"].values()}, key=lambda m: ["gemma", "qwen3", "mistral"].index(m)
                    if m in ("gemma", "qwen3", "mistral") else 9)
    fig1(idx, models)
    fig6(models)
    p = C.RES / "analysis.json"
    if p.exists():
        A = C.jload(p)
        fig2(idx, A, models)
        fig3(A, models)
        fig4(A)
        fig5(A, models)


if __name__ == "__main__":
    main()

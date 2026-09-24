#!/usr/bin/env python3
"""Stage J figures from results/analysis.json (+ judge2 agreement): PNG + PDF in figures/.
fig1 outcome-class stacks, fig2 forest of orig->edit effects, fig3 S5X paired SL-EN gap, fig4 S6 over-refusal, fig5 judge agreement."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

WS = Path(__file__).resolve().parent
FIG = WS / "figures"
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
CK = ["gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref"]
NICE = {"gams_orig": "GaMS3 orig", "gams_edit": "GaMS3 edit", "gemma_orig": "Gemma-3 orig", "gemma_edit": "Gemma-3 edit",
        "community_ref": "Community edit (ref)"}
CLS = ["refused", "partial", "complied", "irrelevant", "malformed", "empty"]
COL = {"refused": "#4C72B0", "partial": "#8FAADC", "complied": "#DD8452", "irrelevant": "#937860", "malformed": "#C44E52", "empty": "#555555"}


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    A = json.loads((WS / "results/analysis.json").read_text())
    H = A["headline"]
    cks = [c for c in CK if f"{c}|en" in H]
    # fig1
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
    for ax, s in zip(axes, ("S5", "S6")):
        labels, bottoms = [], None
        rows = [(c, l) for c in cks for l in ("en", "sl")]
        M = np.zeros((len(rows), len(CLS)))
        for i, (c, l) in enumerate(rows):
            cc = H[f"{c}|{l}"][f"class_counts_{s}"]
            tot = sum(v for k, v in cc.items() if k in CLS) or 1
            M[i] = [cc.get(k, 0) / tot for k in CLS]
            labels.append(f"{NICE[c]} {l.upper()}")
        left = np.zeros(len(rows))
        for j, k in enumerate(CLS):
            ax.barh(range(len(rows)), M[:, j], left=left, color=COL[k], label=k)
            left += M[:, j]
        ax.set_yticks(range(len(rows)), labels)
        ax.invert_yaxis()
        ax.set_xlabel("share of responses")
        ax.set_title("RefusEU sample (S5, harmful)" if s == "S5" else "XSTest-safe (S6, benign)")
    axes[1].legend(ncol=3, fontsize=7, loc="lower right", bbox_to_anchor=(1.0, -0.45))
    save(fig, "fig1_outcome_classes")

    # fig2 forest
    fam = A.get("c1_family", {})
    if fam:
        names = list(next(iter(fam.values())).keys())
        fig, ax = plt.subplots(figsize=(7, 4.8))
        y = 0
        yt, yl = [], []
        for m, colr in (("gams", "#DD8452"), ("gemma", "#4C72B0")):
            if m not in fam:
                continue
            for n in names:
                e = fam[m][n]
                if not e.get("n"):
                    continue
                ax.errorbar(e["diff"], y, xerr=[[e["diff"] - e["ci"][0]], [e["ci"][1] - e["diff"]]], fmt="o", color=colr, ms=4, capsize=2)
                yt.append(y)
                yl.append(f"{'GaMS3' if m == 'gams' else 'Gemma-3'}: {n}" + (" *" if (e.get("p_holm") or 1) < 0.05 else ""))
                y += 1
            y += 0.6
        ax.axvline(0, color="k", lw=0.7)
        ax.set_yticks(yt, yl, fontsize=7)
        ax.invert_yaxis()
        ax.set_xlabel("edit − original (paired, 95% cluster-bootstrap CI); * Holm p<.05")
        save(fig, "fig2_forest_orig_to_edit")

    # fig3 S5X gap
    G = A.get("s5x_cross_language", {}).get("per_ckpt_gap", {})
    if G:
        fig, ax = plt.subplots(figsize=(6, 3))
        for i, c in enumerate([c for c in cks if c in G]):
            for dx, key, mk in ((-0.15, "all", "o"), (0.0, "en->sl", "^"), (0.15, "sl->en", "s")):
                g = G[c][key]
                if not g.get("n_pairs"):
                    continue
                ax.errorbar(i + dx, g["gap_sl_minus_en"], yerr=[[g["gap_sl_minus_en"] - g["ci"][0]], [g["ci"][1] - g["gap_sl_minus_en"]]],
                            fmt=mk, color="#4C72B0" if key == "all" else "#999999", ms=5, capsize=2, label=key if i == 0 else None)
        ax.axhline(0, color="k", lw=0.7)
        ax.set_xticks(range(len([c for c in cks if c in G])), [NICE[c] for c in cks if c in G], rotation=20, fontsize=7)
        ax.set_ylabel("refusal SL − EN (S5X pairs)")
        ax.legend(fontsize=7, title="translation direction", title_fontsize=7)
        save(fig, "fig3_s5x_paired_gap")

    # fig4 S6 over-refusal
    fig, ax = plt.subplots(figsize=(6, 3))
    w = 0.38
    for j, l in enumerate(("en", "sl")):
        vals = [H[f"{c}|{l}"]["S6_over_refusal"] for c in cks]
        r = [v.get("rate", np.nan) for v in vals]
        err = [[v["rate"] - v["ci"][0] for v in vals], [v["ci"][1] - v["rate"] for v in vals]] if all(v.get("n") for v in vals) else None
        ax.bar(np.arange(len(cks)) + (j - 0.5) * w, r, w, yerr=err, capsize=2, label=l.upper(), color=["#4C72B0", "#DD8452"][j])
    ax.set_xticks(range(len(cks)), [NICE[c] for c in cks], rotation=20, fontsize=7)
    ax.set_ylabel("over-refusal (full refusal) on XSTest-safe")
    ax.legend(fontsize=7)
    save(fig, "fig4_s6_over_refusal")

    # fig5 judge agreement
    jp = WS / "results/judge2_agreement.json"
    if jp.exists():
        J = json.loads(jp.read_text())
        mats = [(k, v) for k, v in J.get("confusion_5way", {}).items()]
        if mats:
            fig, axes = plt.subplots(1, len(mats), figsize=(4.2 * len(mats), 3.6))
            axes = np.atleast_1d(axes)
            for ax, (k, v) in zip(axes, mats):
                labs, M = v["labels"], np.array(v["matrix"])
                ax.imshow(M, cmap="Blues")
                for a in range(len(labs)):
                    for b in range(len(labs)):
                        ax.text(b, a, int(M[a, b]), ha="center", va="center", fontsize=7)
                ax.set_xticks(range(len(labs)), labs, rotation=45, fontsize=7)
                ax.set_yticks(range(len(labs)), labs, fontsize=7)
                ax.set_xlabel("second judge (gemini-2.5-flash)")
                ax.set_ylabel("primary judge (gpt-4.1)")
                ax.set_title(f"{k.upper()}  kappa={J['kappa_5way'][k]['kappa']:.2f}")
            save(fig, "fig5_judge_agreement")
    print("figures written:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()

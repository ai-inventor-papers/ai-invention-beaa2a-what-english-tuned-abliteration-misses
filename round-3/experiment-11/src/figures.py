#!/usr/bin/env python3
"""STEP 7.3 - figures (PNG + PDF) drawn only from saved result files:
fig1 keyword vs classifier vs judged refusal count per iteration-1 draw (vs KL), selections marked
fig2 shared first-60 draws: Pareto fronts under the keyword and the corrected objective
fig3 EN vs SL judged refusal (S5X) for every arm, dose ladder as a curve, community edit as a point
fig4 aligned coverage A1 vs S5X SL refusal (arms) + A1 of all 116 draws vs their judged in-loop refusal
fig5 outcome classes (refused/partial/complied/invalid) per arm x language, S5X
fig6 S5X paired SL-EN gap forest plot with 95% CIs
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WS = Path(__file__).resolve().parent
FIG = WS / "figures"
plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
C = {"keyword": "#b2182b", "classifier": "#2166ac", "judge": "#1b7837", "grey": "#777777", "dose": "#e08214",
     "community": "#762a83"}


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=200)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def main() -> None:
    mt = pd.read_csv(WS / "results/miscalibration_table.csv")
    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    ea = json.loads((WS / "results/eval_analysis.json").read_text()) if (WS / "results/eval_analysis.json").exists() else None
    cov = pd.read_csv(WS / "results/coverage_descriptors.csv")

    # fig1
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    d = mt.sort_values("kl")
    ax[0].scatter(d.kl, d.keyword_refusals, s=12, c=C["keyword"], label="keyword (Heretic objective)")
    ax[0].scatter(d.kl, d.classifier_refusals, s=12, c=C["classifier"], marker="s", label="partial-aware classifier")
    j = d[d.judge_refused.notna()]
    ax[0].scatter(j.kl, j.judge_refused, s=14, c=C["judge"], marker="^", label="Qwen3-14B judged refused")
    for key, lab in (("keyword_refusals", "kw"), ("classifier_refusals", "clf"), ("judge_refused", "judge")):
        r = ia["reselection"].get(key)
        if r:
            ax[0].annotate(f"{lab}-sel t{r['trial_number']}", (r["kl"], r["refusals"]), fontsize=7,
                           xytext=(4, 6), textcoords="offset points")
    ax[0].set_xscale("log")
    ax[0].set_xlabel("first-token KL on harmless prompts (this GPU)")
    ax[0].set_ylabel("refusals / 100 in-loop prompts")
    ax[0].legend(fontsize=7, frameon=False)
    ax[0].set_title("a  116 iteration-1 draws, three refusal scores")
    ax[1].scatter(j.judge_refused, j.keyword_refusals, s=12, c=C["keyword"], label="keyword")
    ax[1].scatter(j.judge_refused, j.classifier_refusals, s=12, c=C["classifier"], marker="s", label="classifier")
    ax[1].plot([0, 100], [0, 100], c=C["grey"], lw=0.8, ls="--")
    ax[1].set_xlabel("Qwen3-14B judged refusals / 100")
    ax[1].set_ylabel("proxy refusals / 100")
    ax[1].legend(fontsize=7, frameon=False)
    ax[1].set_title("b  proxy vs judge, per draw")
    save(fig, "fig1_miscalibration")

    # fig2 Pareto on shared first-60 draws
    f60 = mt[mt.trial < 60]
    if len(f60):
        fig, ax = plt.subplots(figsize=(4.6, 3.6))
        for col, cc, lab in (("keyword_refusals", C["keyword"], "keyword objective"),
                             ("classifier_refusals", C["classifier"], "corrected objective")):
            ax.scatter(f60.kl, f60[col], s=10, c=cc, alpha=0.5)
            fr = ia.get("first60_pareto", {}).get("keyword" if col.startswith("keyword") else "classifier", [])
            p = f60[f60.trial.isin(fr)].sort_values("kl")
            ax.step(p.kl, p[col], where="post", c=cc, label=f"{lab} Pareto front ({len(p)})")
        ax.set_xscale("log")
        ax.set_xlabel("KL")
        ax.set_ylabel("refusals / 100")
        ax.set_title("Identical 60 startup edits, two objectives")
        ax.legend(fontsize=7, frameon=False)
        save(fig, "fig2_pareto_first60")

    if ea is None:
        return
    g = ea["s5x_gap"]["qwen"]
    arms = ea["arms"]
    # fig3 EN vs SL
    fig, ax = plt.subplots(figsize=(4.8, 4.0))
    lad = sorted([(g[a]["en_refusal"], g[a]["sl_refusal"], a) for a in arms if arms[a].get("role") in ("keyword", "dose")])
    if lad:
        ax.plot([x[0] for x in lad], [x[1] for x in lad], c=C["dose"], marker="o", label="dose ladder on trial 96 (f=1,1.5,2,3)")
    for a in arms:
        ax.scatter(g[a]["en_refusal"], g[a]["sl_refusal"], s=30, zorder=3,
                   c={"orig": C["grey"], "keyword": C["keyword"], "corrected": C["classifier"], "reselected": C["judge"],
                      "dose": C["dose"]}.get(arms[a].get("role"), "k"))
        off = {"D_reselected_clf": (8, -12), "F_dose1.5": (-60, -4), "C_corrected": (6, 2), "F_dose3.0": (6, 8)}.get(a, (3, -8))
        ax.annotate(a, (g[a]["en_refusal"], g[a]["sl_refusal"]), fontsize=6.5, xytext=off, textcoords="offset points")
    cr = ea["community_reference"]
    ax.scatter(cr["S5_en_refusal"], cr["S5_sl_refusal"], marker="*", s=90, c=C["community"],
               label="community edit (art_m6pglf516e2r, S5)")
    ax.plot([0, 1], [0, 1], c=C["grey"], lw=0.7, ls="--")
    ax.set_xlabel("EN judged refusal (S5X EN rows)")
    ax.set_ylabel("SL judged refusal (S5X SL rows)")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    save(fig, "fig3_en_vs_sl")

    # fig4 coverage
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    it = cov[cov.source == "iter1_keyword_run"].merge(mt[["trial", "judge_refused"]], on="trial", how="left")
    ax[0].scatter(it.sum_A1, it.judge_refused, s=12, c=np.where(it.direction_scope == "global", C["keyword"], C["classifier"]))
    ax[0].set_xlabel("aligned coverage A1 (sum over components)")
    ax[0].set_ylabel("in-loop judged refusals / 100")
    ax[0].set_title("a  116 draws (red global, blue per-layer)")
    from coverage import descriptors
    pts = []
    for a in arms:
        if arms[a].get("parameters") and float(arms[a].get("dose") or 1.0) == 1.0:
            di = None if arms[a]["direction_index"] is None else arms[a]["direction_index"]
            A1 = descriptors(arms[a]["parameters"], di)["sum_A1"]
            pts.append((A1, g[a]["sl_refusal"], a))
    for A1, sl, a in pts:
        ax[1].scatter(A1, sl, s=30, c="k")
        ax[1].annotate(a, (A1, sl), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
    comm = cov[cov.source == "community_ref"].iloc[0]
    ax[1].scatter(comm.sum_A1, cr["S5_sl_refusal"], marker="*", s=90, c=C["community"])
    ax[1].annotate("community", (comm.sum_A1, cr["S5_sl_refusal"]), fontsize=6.5)
    ax[1].set_xlabel("aligned coverage A1")
    ax[1].set_ylabel("SL judged refusal")
    ax[1].set_title("b  evaluated edits (EXPLORATORY)")
    save(fig, "fig4_coverage")

    # fig5 classes
    rates = pd.DataFrame(ea["rates"])
    r = rates[(rates.set == "S5X") & (rates.judge == "qwen")]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    labels, bottoms = [], None
    xs = []
    for i, (a, lg) in enumerate([(a, lg) for a in arms for lg in ("en", "sl")]):
        row = r[(r.arm == a) & (r.lang == lg)]
        if not len(row):
            continue
        row = row.iloc[0]
        b = 0
        for cls, cc in (("refused", C["keyword"]), ("partial", C["dose"]), ("complied", C["classifier"]),
                        ("irrelevant", C["grey"]), ("invalid", "k")):
            v = row[cls][0]
            ax.bar(i, v, bottom=b, color=cc, label=cls if i == 0 else None, width=0.8)
            b += v
        xs.append(i)
        labels.append(f"{a}\n{lg.upper()}")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=6, rotation=60)
    ax.set_ylabel("share of S5X responses (Qwen3-14B)")
    ax.legend(fontsize=7, frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.15))
    save(fig, "fig5_outcome_classes")

    # fig7 the cost side: SL-EN gap and EN refusal against harmless KL
    kl = ea.get("kl_per_arm", {})
    if kl:
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
        lad_arms = [a for a in arms if arms[a].get("role") in ("keyword", "dose")]
        for i, (yname, yf) in enumerate((("S5X SL - EN refusal gap", lambda a: g[a]["gap_sl_minus_en"]),
                                          ("S5X EN judged refusal", lambda a: g[a]["en_refusal"]))):
            lad = sorted([(kl[a]["harmless_kl"], yf(a), a) for a in lad_arms if a in kl])
            ax[i].plot([x[0] for x in lad], [x[1] for x in lad], c=C["dose"], marker="o",
                       label="dose ladder on trial 96")
            for a in arms:
                if a not in kl:
                    continue
                ax[i].scatter(kl[a]["harmless_kl"], yf(a), s=32, zorder=3,
                              c={"orig": C["grey"], "keyword": C["keyword"], "corrected": C["classifier"],
                                 "reselected": C["judge"], "dose": C["dose"]}.get(arms[a].get("role"), "k"))
                ax[i].annotate(a, (kl[a]["harmless_kl"], yf(a)), fontsize=6, xytext=(3, 4), textcoords="offset points")
            ax[i].set_xlabel("harmless first-token KL (Heretic's own KL scorer)")
            ax[i].set_ylabel(yname)
        ax[0].legend(fontsize=7, frameon=False)
        ax[0].set_title("a  cross-language gap vs edit size")
        ax[1].set_title("b  English suppression vs edit size")
        save(fig, "fig7_gap_vs_kl")

    # fig6 forest
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    names = list(arms)
    for i, a in enumerate(names):
        x = g[a]
        ax.errorbar(x["gap_sl_minus_en"], i, xerr=[[x["gap_sl_minus_en"] - x["ci"][0]], [x["ci"][1] - x["gap_sl_minus_en"]]],
                    fmt="o", c="k", ms=4, capsize=2)
    ax.axvline(cr["S5X_gap"], c=C["community"], ls=":", label=f"community edit +{cr['S5X_gap']:.2f}")
    ax.axvline(0, c=C["grey"], lw=0.7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel("S5X paired SL - EN refusal gap (95% cluster-bootstrap CI)")
    ax.legend(fontsize=7, frameon=False)
    save(fig, "fig6_s5x_gap_forest")


if __name__ == "__main__":
    main()

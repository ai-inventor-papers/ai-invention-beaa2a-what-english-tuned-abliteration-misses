#!/usr/bin/env python3
"""STAGE S9 figures (vector PDF + PNG, every number read from results/, never typed in).

fig1  objective K vs reference C per candidate, both searches, objective floor + noise band, selections marked
fig2  GBF with 95% CIs: paired 60 / all 116 / TPE, both searches, with the placebo nulls on the same axis
fig3  per-candidate count curves (K, C, J) ordered by C, both searches
fig4  incumbent at shipped rule / oracle threshold / repaired list vs the classifier: kappa, MAE/100, false-refusal share
fig5  certification on GaMS3 beside art_0XmNBGkzsJc_'s Gemma numbers, gpt-4.1 judge gate marked
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from common import RESULTS, WS  # noqa: E402

FIG = WS / "figures"
COL = {"gemma": "#1f77b4", "gams": "#d62728"}
NAME = {"gemma": "gemma-3-12b-it (search 1)", "gams": "GaMS3-12B-Instruct (search 2)"}
plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False})


def save(fig, name: str) -> None:
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig1(an: dict, pc: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=True)
    for ax, m in zip(axes, ("gemma", "gams")):
        d = pc[pc.model == m]
        blk = an["searches"][m]["gbf_C"]["all"]
        floor, sb = blk["FLOOR"], blk["sigma_bar"]
        ax.axhspan(floor - sb, floor + sb, color="0.85", zorder=0, label=f"objective floor ±σ̄ ({floor:.0f}±{sb:.1f})")
        ax.plot([0, 100], [0, 100], ls=":", c="0.5", lw=1, label="K = C")
        for ph, mk in (("startup", "o"), ("tpe", "^")):
            e = d[d.phase == ph]
            ax.scatter(e.C, e.K, s=18, marker=mk, facecolors="none" if ph == "tpe" else COL[m], edgecolors=COL[m],
                       lw=0.8, label=f"{ph} draws (n={len(e)})")
        for col, mk, lab in (("selected_by_K", "*", "selected under K"), ("selected_by_C", "P", "selected under C")):
            if col in d:
                s = d[d[col] == True]  # noqa: E712
                ax.scatter(s.C, s.K, s=140, marker=mk, c="k", zorder=5, label=lab)
        ax.axhline(10, c="k", lw=0.6, ls="--")
        ax.axvline(10, c="k", lw=0.6, ls="--")
        ax.set_title(f"{NAME[m]}\nGBF={blk['gbf']:.3f}  RCR={blk['RCR']:.2f}  TBF={blk['secondary_threshold_blind_C_le_10']['tbf']:.2f}")
        ax.set_xlabel("C: certified classifier refusals /100 (reference)")
        ax.set_xlim(-2, 102)
        ax.set_ylim(-2, 102)
        ax.legend(fontsize=6.5, loc="lower right")
    axes[0].set_ylabel("K: Heretic keyword objective /100")
    fig.suptitle("Fig. 1  What the optimiser saw (K) against what the candidates did (C), one point per candidate", fontsize=9, y=1.04)
    save(fig, "fig1_objective_vs_reference")


def fig2(an: dict) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 4.0))
    h = an["paired_headline"]
    rows = []
    for m in ("gemma", "gams"):
        s = an["searches"][m]["gbf_C"]
        for pop, lab in (("startup", "paired 60 (startup)"), ("all", "all 116"), ("tpe", "TPE 56")):
            if pop in s:
                rows.append((f"{m}\n{lab}", s[pop]["gbf"], s[pop]["ci95"], COL[m], s[pop]["P_a_permutation"]["chance_mean"],
                             s[pop].get("P_c_split_half", {}).get("mean"), s[pop]["secondary_gbf_low_C_le_50"]["gbf"]))
    x = np.arange(len(rows))
    for i, (lab, v, ci, c, ch, sh, low) in enumerate(rows):
        ax.bar(i, v, color=c, alpha=0.8, width=0.6)
        ax.errorbar(i, v, yerr=[[v - ci[0]], [ci[1] - v]], c="k", capsize=3, lw=1)
        ax.scatter(i, ch, marker="_", s=400, c="0.3", zorder=4, label="P-a permutation chance" if i == 0 else None)
        if sh is not None:
            ax.scatter(i, sh, marker="x", s=30, c="0.3", zorder=4, label="P-c split-half (same instrument)" if i == 0 else None)
        if low == low:
            ax.scatter(i, low, marker="D", s=22, c="orange", edgecolors="k", zorder=5, label="GBF_low (C≤50, secondary)" if i == 0 else None)
    ax.axhline(0, c="k", lw=0.6)
    ax.set_xticks(x, [r[0] for r in rows], fontsize=7)
    ax.set_ylabel("gradient-blind fraction (95% CI)")
    d = h["paired_difference_gemma_minus_gams"]
    ax.set_title(f"Fig. 2  GBF (P-b self-comparison = 0 by construction).  Paired difference gemma−gams = {d['diff']:+.3f} "
                 f"[{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] → PRED-1 {h['verdict_PRED_1'].split(' ')[0]}", fontsize=8)
    ax.legend(fontsize=7, loc="upper left")
    save(fig, "fig2_gbf_with_placebos")


def fig3(pc: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), sharey=True)
    for ax, m in zip(axes, ("gemma", "gams")):
        d = pc[pc.model == m].sort_values(["C", "trial"]).reset_index(drop=True)
        ax.plot(d.index, d.K, c=COL[m], lw=1.2, label="K keyword objective")
        ax.plot(d.index, d.C, c="k", lw=1.2, label="C classifier")
        jj = d[d.J.notna()]
        ax.scatter(jj.index, jj.J, s=10, c="orange", zorder=4, label=f"J judge (n={len(jj)} candidates)")
        ax.set_title(NAME[m])
        ax.set_xlabel("candidate rank by C")
        ax.legend(fontsize=7)
    axes[0].set_ylabel("refusals /100 in-loop prompts")
    fig.suptitle("Fig. 3  Per-candidate counts across each search's own candidate population", fontsize=9, y=1.04)
    save(fig, "fig3_count_curves")


def fig4(an: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.6))
    insts = [("keyword", "shipped K"), ("keyword_oracle_t", "oracle-t K"), ("keyword_repaired", "repaired K"), ("classifier", "classifier C")]
    for ax, (met, lab) in zip(axes, (("kappa", "Cohen's κ vs judge"), ("mae_per100", "MAE per 100 (trial level)"), ("fp_share", "false-'refusal' share"))):
        for j, m in enumerate(("gemma", "gams")):
            conv = an["searches"][m]["conventional"]["all"]
            vals = [conv.get(i, {}).get(met) for i, _ in insts]
            xs = np.arange(len(insts)) + (j - 0.5) * 0.38
            ax.bar(xs, [v if v is not None else 0 for v in vals], width=0.36, color=COL[m], alpha=0.85, label=m)
            if met == "kappa":
                for x, i in zip(xs, insts):
                    ci = conv.get(i[0], {}).get("kappa_ci95_trial_cluster")
                    v = conv.get(i[0], {}).get("kappa")
                    if ci and v is not None:
                        ax.errorbar(x, v, yerr=[[v - ci[0]], [ci[1] - v]], c="k", capsize=2, lw=0.8)
        ax.set_xticks(range(len(insts)), [l for _, l in insts], fontsize=7, rotation=20)
        ax.set_title(lab, fontsize=8)
    axes[0].legend(fontsize=7)
    fig.suptitle("Fig. 4  The incumbent given its best shot (oracle threshold chosen in hindsight; repaired marker list)", fontsize=9, y=1.04)
    save(fig, "fig4_incumbent_best_shot")


def fig5(cert: dict, jc: dict) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.6))
    g = cert["gemma_reference_A11"]
    q = cert["qwen3_14b"]
    bars = [("Gemma clf\n(A11)", g["classifier_kappa"], g["classifier_kappa_ci95"], COL["gemma"]),
            ("Gemma kw\n(A11)", g["keyword_kappa"], g["keyword_kappa_ci95"], COL["gemma"]),
            ("GaMS3 clf\n(Qwen)", q["classifier"]["kappa"], q["classifier"]["kappa_ci95_trial_cluster"], COL["gams"]),
            ("GaMS3 kw\n(Qwen)", q["keyword"]["kappa"], q["keyword"]["kappa_ci95_trial_cluster"], COL["gams"])]
    if cert.get("gpt41", {}).get("classifier"):
        gg = cert["gpt41"]
        bars += [("GaMS3 clf\n(gpt-4.1)", gg["classifier"]["kappa"], gg["classifier"]["kappa_ci95_trial_cluster"], "#8c564b"),
                 ("GaMS3 kw\n(gpt-4.1)", gg["keyword"]["kappa"], gg["keyword"]["kappa_ci95_trial_cluster"], "#8c564b")]
    if jc.get("refused_vs_not_edited"):
        r = jc["refused_vs_not_edited"]
        bars.append(("Qwen vs\ngpt-4.1", r["kappa"], r["kappa_ci95_trial_cluster"], "0.4"))
    for i, (lab, v, ci, c) in enumerate(bars):
        ax.bar(i, v, color=c, alpha=0.85, width=0.6)
        if ci:
            ax.errorbar(i, v, yerr=[[v - ci[0]], [ci[1] - v]], c="k", capsize=3, lw=1)
        ax.text(i + 0.31, v, f"{v:.2f}", ha="left", va="center", fontsize=7)
    ax.axhline(0.80, c="k", ls="--", lw=0.8, label="pre-registered gate κ ≥ 0.80")
    ax.set_xticks(range(len(bars)), [b[0] for b in bars], fontsize=7)
    ax.set_ylim(min(0, min(b[1] for b in bars) - 0.05), 1.05)
    ax.set_ylabel("κ refused-vs-not, edited cells")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_title(f"Fig. 5  Certification on GaMS3 text (20 held-out trials); judge gate: {jc['gate'].get('status')}", fontsize=8)
    save(fig, "fig5_certification")


def fig6(an: dict, pc: pd.DataFrame) -> None:
    """K against the JUDGE on every fully judged candidate (Gemma 116; GaMS3 70 = 20 certification + 50 startup)."""
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=True)
    for ax, m in zip(axes, ("gemma", "gams")):
        d = pc[(pc.model == m) & pc.J.notna()]
        b = an["searches"][m]["gbf_J"]["all"]
        ax.axhspan(b["FLOOR"] - b["sigma_bar"], b["FLOOR"] + b["sigma_bar"], color="0.85", zorder=0, label="objective floor ±σ̄")
        ax.plot([0, 100], [0, 100], ls=":", c="0.5", lw=1, label="K = J")
        ax.scatter(d.J, d.K, s=18, c=COL[m], alpha=0.8, label=f"fully judged candidates (n={len(d)})")
        ax.scatter(d.J, d.C, s=10, marker="x", c="k", alpha=0.6, label="classifier C at the same candidates")
        ax.axhline(10, c="k", lw=0.6, ls="--")
        ax.axvline(10, c="k", lw=0.6, ls="--")
        ax.set_title(f"{NAME[m]}\nGBF(J)={b['gbf']:.3f}  TBF(J)={b['secondary_threshold_blind_C_le_10']['tbf']:.2f}  slope={b['calibration']['slope_K_on_C']:.2f}")
        ax.set_xlabel("J: judged refusals /100 (Qwen3-14B, frozen rubric)")
        ax.set_xlim(-2, 102)
        ax.set_ylim(-2, 102)
        ax.legend(fontsize=6.5, loc="lower right")
    axes[0].set_ylabel("K (coloured) and C (x) /100")
    h = an["paired_headline"]["judge_referenced_paired"]["paired_difference"]
    fig.suptitle(f"Fig. 6  Judge as reference. Paired 60, gemma−gams GBF(J) = {h['diff']:+.3f} [{h['ci95'][0]:+.3f}, {h['ci95'][1]:+.3f}]",
                 fontsize=9, y=1.04)
    save(fig, "fig6_objective_vs_judge")


def main() -> None:
    an = json.loads((RESULTS / "analysis.json").read_text())
    pc = pd.read_csv(RESULTS / "per_candidate.csv")
    fig1(an, pc)
    fig2(an)
    fig3(pc)
    fig4(an)
    fig6(an, pc)
    fig5(json.loads((RESULTS / "gams_certification.json").read_text()), json.loads((RESULTS / "judge_certification.json").read_text()))
    print("figures written:", sorted(p.name for p in FIG.glob("*.png")))


if __name__ == "__main__":
    main()

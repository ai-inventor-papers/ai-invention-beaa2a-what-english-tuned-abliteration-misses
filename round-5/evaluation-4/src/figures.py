"""Three audit figures (vector PDF + PNG): mismatch rate across passes, forest plot of recomputed contrasts, kappa panel."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

FIG = Path(__file__).resolve().parent / "figures"
plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY, RED = "#2b6cb0", "#dd6b20", "#718096", "#c53030"


def _wilson(k, n, z=1.959964):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


def make_figures(recs, summ, rate, ci, k, n, priors, knum):
    # 1. defect rate across the three audit passes, two definitions
    fig, ax = plt.subplots(figsize=(5.2, 2.9))
    rows = [(lab, p["k_all"], p["k_num"], p["n"]) for lab, p in priors.items()] + [(f"this pass (iter 4 +\npreviously unaudited)", k, knum, n)]
    for j, (lab, ka, kn, nn) in enumerate(rows):
        for off, kk, col, name in ((-0.18, ka, BLUE, "all defect classes"), (0.18, kn, ORANGE, "numeric MISMATCH only")):
            p_ = kk / nn; lo_, hi_ = _wilson(kk, nn)
            ax.bar(j + off, p_, width=0.34, color=col, label=name if j == 0 else None)
            ax.errorbar(j + off, p_, yerr=[[p_ - lo_], [hi_ - p_]], fmt="none", ecolor="black", capsize=2, lw=0.8)
            ax.text(j + off, hi_ + 0.008, f"{p_:.1%}", ha="center", fontsize=7)
    ax.set_xticks(range(len(rows))); ax.set_xticklabels([f"{r[0]}\n(n={r[3]})" for r in rows], fontsize=7)
    ax.set_ylabel("share of audited numbers\n(Wilson 95% CI)")
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("Draft numbers failing an independent recompute, per audit pass", fontsize=9)
    _save(fig, "fig1_mismatch_rate_passes")

    # 2. forest plot of recomputed headline contrasts
    R = {r["claim_id"]: r for r in recs}
    rows = [("E13.pooled_matched_contrast_en", "Gemma matched groups, high-O minus low-O, EN"),
            ("E13.pooled_matched_contrast_sl", "Gemma matched groups, high-O minus low-O, SL"),
            ("E10.placement_matched_count_E3", "GaMS3 E3: B2 minus STR4 (matched E and count), SL"),
            ("E10.unmatched_c1_B2_minus_B3_sl", "GaMS3 unmatched c=1: 13-24 minus 25-36, SL"),
            ("E14.dose_at_fixed_O_ship.sl", "GaMS3 dose at fixed placement (A1-A4), SL"),
            ("E14.placement_at_fixed_E_high.sl", "GaMS3 placement at fixed dose (A1-A3), SL"),
            ("E4.S5X_gap.gemma_edit.strict", "Gemma edit S5X SL-EN gap, strict"),
            ("E4.S5X_gap.gemma_edit.broad", "Gemma edit S5X SL-EN gap, broad"),
            ("EV2.paired_gap_bf16", "bf16 probe SL-EN gap (20 pairs)"),
            ("EV2.paired_gap_nf4", "NF4 probe SL-EN gap (20 pairs)")]
    rows = [(c, l) for c, l in rows if c in R and R[c].get("ci")]
    fig, ax = plt.subplots(figsize=(6.2, 0.36 * len(rows) + 0.9))
    for i, (c, l) in enumerate(rows[::-1]):
        r = R[c]; v = float(r["recomputed_value"]); lo_, hi_ = r["ci"]
        col = ORANGE if "sl" in c.lower() and "E4" not in c else BLUE
        ax.plot([lo_, hi_], [i, i], color=col, lw=1.6); ax.plot(v, i, "o", color=col, ms=4)
        if isinstance(r.get("draft_value"), (int, float)):
            ax.plot(float(r["draft_value"]), i, "x", color=RED, ms=5)
    ax.axvline(0, color=GREY, lw=0.8, ls="--")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([l for _, l in rows[::-1]], fontsize=7)
    ax.set_xlabel("strict refusal difference, recomputed (95% CI); red x = draft value")
    ax.set_title("Recomputed headline contrasts", fontsize=9)
    _save(fig, "fig2_forest_recomputed_contrasts")

    # 3. kappa panel: pooled vs within-edited, per artifact x language, against the 0.80 gate
    kap = summ["pooled"]["kappa"]
    keys = sorted({"|".join(k_.split("|")[:2]) for k_ in kap if not k_.startswith("exp4:")})
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    xs = range(len(keys))
    for j, (cond, col, off) in enumerate((("pooled", GREY, -0.15), ("edited", BLUE, 0.15))):
        for i, key in enumerate(keys):
            d = kap.get(f"{key}|{cond}")
            if not d or d["kappa"] != d["kappa"]:
                continue
            ax.plot(i + off, d["kappa"], "o", color=col, ms=5, label=cond if i == 0 or not ax.get_legend_handles_labels()[1].count(cond) else None)
            if d["ci"][0] == d["ci"][0]:
                ax.plot([i + off, i + off], d["ci"], color=col, lw=1)
    for i, key in enumerate(keys):
        if key.startswith("exp4|"):
            d = kap.get(f"exp4:gemma_edit|{key.split('|')[1]}|cell")
            if d:
                ax.plot(i + 0.4, d["kappa"], "D", color=ORANGE, ms=4, label="headline cell (Gemma edit)")
                ax.plot([i + 0.4] * 2, d["ci"], color=ORANGE, lw=1)
    ax.axhline(0.80, color=RED, ls="--", lw=0.9); ax.text(-0.4, 0.82, "gate 0.80", color=RED, fontsize=7, ha="left")
    ax.set_xticks(list(xs)); ax.set_xticklabels(keys, rotation=30, fontsize=7)
    ax.set_ylabel("kappa, Qwen3-14B vs gpt-4.1\n(refused vs not)")
    h, l_ = ax.get_legend_handles_labels(); seen = {}
    for hh, ll in zip(h, l_):
        seen.setdefault(ll, hh)
    ax.legend(seen.values(), seen.keys(), fontsize=7, frameon=False, loc="lower left")
    ax.set_ylim(0, 1.05)
    ax.set_title("Judge agreement: pooled vs within edited cells", fontsize=9)
    _save(fig, "fig3_kappa_pooled_vs_edited")

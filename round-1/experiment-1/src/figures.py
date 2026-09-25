#!/usr/bin/env python3
"""Figures (PNG + PDF): (1) refusal-vs-KL clouds with Pareto fronts per model, (2) A3 sibling scatter
for both outcomes, (3) condition bars (orig / own / swap, EN + SL) per target model."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from loguru import logger  # noqa: E402

WS = Path(__file__).resolve().parent
FIG = WS / "figures"
FIG.mkdir(exist_ok=True)
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
NAME = {"gams": "GaMS3-12B-Instruct", "gemma": "gemma-3-12b-it"}
COL = {"gams": "#1f77b4", "gemma": "#d62728"}


def save(fig, stem: str) -> None:
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{stem}.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"wrote figures/{stem}.png|.pdf")


def pareto(df: pd.DataFrame) -> pd.DataFrame:
    keep = []
    for _, r in df.iterrows():
        dom = ((df.refusals <= r.refusals) & (df.kl <= r.kl) &
               ((df.refusals < r.refusals) | (df.kl < r.kl))).any()
        if not dom:
            keep.append(r)
    return pd.DataFrame(keep).sort_values("refusals")


def main() -> None:
    dfs = {}
    for t in NAME:
        p = WS / "results" / f"trials_{t}.csv"
        if p.exists():
            d = pd.read_csv(p)
            dfs[t] = d[d.state == "COMPLETE"].dropna(subset=["refusals", "kl"])

    if dfs:
        fig, axes = plt.subplots(1, len(dfs), figsize=(5.2 * len(dfs), 4.2), squeeze=False)
        for ax, (t, d) in zip(axes[0], dfs.items()):
            ax.scatter(d.refusals, d.kl, s=18, alpha=.55, color=COL[t], label=f"{len(d)} trials")
            pf = pareto(d)
            ax.plot(pf.refusals, pf.kl, "k.-", lw=1.2, ms=6, label="Pareto front")
            sel = WS / "results" / f"selection_{t}.json"
            if sel.exists():
                s = json.loads(sel.read_text())
                ax.scatter([s["refusals"]], [s["kl"]], marker="*", s=320, color="gold",
                           edgecolor="k", zorder=5, label=f"selected (trial {s['trial_number']})")
            ax.set_yscale("log")
            ax.set_xlabel("EN refusals / 100 (Heretic keyword scorer)")
            ax.set_ylabel("first-token KL vs original")
            ax.set_title(NAME[t])
            ax.legend(fontsize=8)
            ax.grid(alpha=.25)
        save(fig, "fig1_refusal_vs_kl_pareto")

    a3p = WS / "results" / "a3_screen.json"
    if a3p.exists() and len(dfs) == 2:
        a3 = json.loads(a3p.read_text())
        idx = a3["paired_trials"]
        A = dfs["gams"].set_index("number").loc[idx]
        B = dfs["gemma"].set_index("number").loc[idx]
        fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4))
        for ax, (ya, yb, lab, key) in zip(axes, [
                (A.refusals.values, B.refusals.values, "EN refusals / 100", "refusal"),
                (np.log(A.kl.values + 1e-6), np.log(B.kl.values + 1e-6), "log(KL + 1e-6)", "logkl")]):
            ax.scatter(ya, yb, s=26, color="#2a9d8f", alpha=.8)
            lo, hi = min(ya.min(), yb.min()), max(ya.max(), yb.max())
            ax.plot([lo, hi], [lo, hi], "k--", lw=.8, label="y = x")
            r = a3["results"][key]
            ax.set_title(f"{lab}\nrho={r['spearman']['rho']:.2f} "
                         f"[{r['spearman']['ci95'][0]:.2f},{r['spearman']['ci95'][1]:.2f}]  "
                         f"partial={r['partial_spearman_given_kernel_mass']['partial_rho']:.2f}  "
                         f"dR2_sib={r['pred_A_to_B_ridge']['dR2_sibling']:.2f}", fontsize=9)
            ax.set_xlabel(f"GaMS3-12B-Instruct")
            ax.set_ylabel(f"gemma-3-12b-it")
            ax.grid(alpha=.25)
            ax.legend(fontsize=8)
        fig.suptitle(f"A3: {len(idx)} identical startup edits — reading: {a3['reading']}", fontsize=10)
        save(fig, "fig2_a3_sibling_agreement")

    effp = WS / "results" / "efficiency.json"
    if effp.exists() and len(dfs) == 2:
        import a3_screen as A
        eff = json.loads(effp.read_text())
        n = eff["n_shared_identical_edits"]
        a, b = A.load_trials("gams").iloc[:n], A.load_trials("gemma").iloc[:n]
        fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3))
        ax = axes[0]
        ax.scatter(a.kl, a.refusals, s=26, color=COL["gams"], alpha=.85, label="GaMS3-12B-Instruct")
        ax.scatter(b.kl, b.refusals, s=26, color=COL["gemma"], alpha=.85, marker="s", label="gemma-3-12b-it")
        for x1, y1, x2, y2 in zip(a.kl, a.refusals, b.kl, b.refusals):
            ax.plot([x1, x2], [y1, y2], color="grey", lw=.4, alpha=.45, zorder=0)
        ax.axhline(98, color=COL["gams"], ls=":", lw=1)
        ax.axhline(100, color=COL["gemma"], ls=":", lw=1)
        ax.set_xscale("log")
        ax.set_xlabel("first-token KL vs own original (damage)")
        ax.set_ylabel("EN refusals / 100")
        ax.set_title(f"Same {n} edits, both models\n(grey lines join one identical edit)", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(alpha=.25)
        ax = axes[1]
        d = (b.refusals.values - a.refusals.values)
        ax.hist(d, bins=16, color="#6a4c93", alpha=.85)
        ci = eff["paired_refusal_difference_gemma_minus_gams"]
        ax.axvline(0, color="k", lw=1)
        ax.axvline(ci["median"], color="crimson", lw=1.6,
                   label=f"median {ci['median']:.0f} [{ci['ci95'][0]:.0f},{ci['ci95'][1]:.0f}]")
        ax.set_xlabel("Gemma refusals − GaMS refusals, same edit")
        ax.set_ylabel("edits")
        g = eff["efficiency_refusal_drop_per_unit_kl"]["gap"]
        ax.set_title(f"{ci['n_edits_where_gemma_refuses_more']}/{n} edits: Gemma refuses more\n"
                     f"efficiency gap ×{g['ratio_of_medians']:.1f} "
                     f"[{g['ci95'][0]:.1f},{g['ci95'][1]:.1f}]", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(alpha=.25, axis="y")
        save(fig, "fig4_same_edit_efficiency_gap")

    mo = WS / "method_out.json"
    if mo.exists():
        m = json.loads(mo.read_text())
        rows = [r for r in m.get("behaviour_table", []) if r["condition"] in ("orig", "own", "swap")]
        if rows:
            df = pd.DataFrame(rows)
            fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
            for ax, (col, lab) in zip(axes, [("en_refusals", "EN refusals / 100"),
                                             ("sl_refusals", "SL refusals / 100 (marker list)"),
                                             ("kl_mean", "mean first-token KL vs own original")]):
                if col not in df:
                    continue
                w, order = 0.34, ["orig", "own", "swap"]
                for i, t in enumerate(NAME):
                    sub = df[df.target == t].set_index("condition").reindex(order)
                    ax.bar(np.arange(len(order)) + (i - .5) * w, sub[col].values, w,
                           color=COL[t], label=NAME[t], alpha=.85)
                ax.set_xticks(np.arange(len(order)))
                ax.set_xticklabels(["original", "own edit", "sibling's params"])
                ax.set_ylabel(lab)
                ax.grid(alpha=.25, axis="y")
                if col == "kl_mean":
                    ax.set_yscale("symlog", linthresh=1e-3)
                ax.legend(fontsize=8)
            save(fig, "fig3_conditions_en_sl_kl")


if __name__ == "__main__":
    main()

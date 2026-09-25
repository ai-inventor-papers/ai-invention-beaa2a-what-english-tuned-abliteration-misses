#!/usr/bin/env python3
"""fig1..fig5 (PNG + PDF) from results/analysis.json and the saved parquet files."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

WS = Path(__file__).resolve().parent
RES = WS / "results"
FIG = WS / "figures"
plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
C_EN, C_SL = "#2b6cb0", "#c05621"


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / f"{name}.png", dpi=200)
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def main() -> None:
    A = json.loads((RES / "analysis.json").read_text())
    R = A["R_star"]
    traits = [R, "Rb", "K", "N", "M"]
    # fig1: Gap per trait with CIs + raw R2 EN_B vs SL_B
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
    for i, t in enumerate(traits):
        g = A["gap_point"][t]["Gap"]
        lo, hi = A["gap_bootstrap"][t]["Gap"]["ci95"]
        ax[0].errorbar(i, g, yerr=[[g - lo], [hi - g]] if lo is not None else None, fmt="o", color="k", capsize=3)
        gr = A["gap_point"][t]["Gap_raw"]
        ax[0].plot(i + 0.2, gr, "s", color="grey", ms=4)
        ab = A["gap_point"][t]["A->B"]
        ax[1].bar(i - 0.18, ab["R2_EN"], 0.35, color=C_EN, label="EN_A→EN_B" if i == 0 else None)
        ax[1].bar(i + 0.18, ab["R2_SL"], 0.35, color=C_SL, label="EN_A→SL_B" if i == 0 else None)
    ax[0].axhline(0, color="k", lw=0.6)
    ax[0].axhline(0.10, color="r", lw=0.6, ls="--")
    ax[0].set_xticks(range(len(traits)), traits)
    ax[0].set_ylabel("Gap = R2*(EN_B) − R2*(SL_B)")
    ax[0].set_title("Ceiling-normalised Gap (● 95% CI; ■ raw R² Gap)")
    ax[1].set_xticks(range(len(traits)), traits)
    ax[1].set_ylabel("cross-validated R² (raw)")
    ax[1].legend(frameon=False)
    ax[1].set_title("What English half A predicts")
    save(fig, "fig1_gap_per_trait")
    # fig2: EN_A-predicted vs observed SL_B R*, coloured by P
    it = pd.read_parquet(RES / "panel" / "item_traits.parquet")
    cov = pd.read_parquet(RES / "panel" / "edit_covariates.parquet").set_index("edit_id")
    key, role = ("R_seq", "harmful") if R == "R_seq" else ("R1", "harmful")
    d = it[(it.trait_key == key) & (it.role == role)]
    lvl = d.groupby(["edit_id", "lang", "half"])["delta"].mean().unstack(["lang", "half"])
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
    P = (cov["P_sl"] - cov["P_en"]).reindex(lvl.index)
    sc = ax[0].scatter(lvl[("en", "A")], lvl[("sl", "B")], c=P, cmap="viridis", s=14)
    ax[0].set_xlabel(f"Δ{R} EN half A")
    ax[0].set_ylabel(f"Δ{R} SL half B")
    plt.colorbar(sc, ax=ax[0], label="P = P_SL − P_EN")
    ax[1].scatter(lvl[("en", "A")], lvl[("en", "B")], s=14, color=C_EN, label="EN half B")
    ax[1].scatter(lvl[("en", "A")], lvl[("sl", "B")], s=14, color=C_SL, label="SL half B", alpha=.7)
    ax[1].set_xlabel(f"Δ{R} EN half A")
    ax[1].set_ylabel("Δ target")
    ax[1].legend(frameon=False)
    save(fig, "fig2_en_vs_sl_scatter")
    # fig3: carrier forest
    fig, ax = plt.subplots(figsize=(6, 3.2))
    rows = []
    for t in traits:
        c = A["carrier"][t]
        rows.append((f"{t}: ΔR²(P|base)", c["dR2_P_given_base"], c["dR2_P_given_base_ci95"]))
        rows.append((f"{t}: ΔR²(b1|P)", c["dR2_b1_given_P"], c["dR2_b1_given_P_ci95"]))
    for i, (lab, v, cci) in enumerate(rows):
        ax.errorbar(v, i, xerr=[[v - cci[0]], [cci[1] - v]] if cci[0] is not None else None, fmt="o", color="k" if "P|" in lab else "grey", capsize=2)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.axvline(0, color="k", lw=.6)
    ax.axvline(0.05, color="r", lw=.6, ls="--")
    ax.set_xlabel("cross-validated ΔR² on y_spec (95% edit-bootstrap CI)")
    save(fig, "fig3_carrier_forest")
    # fig4: margin distributions + margin-matched Gap
    mm = A["margin_matched"][R]["margins"]["B"]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    ax[0].hist(mm["margins_en"], bins=15, alpha=.6, color=C_EN, label="EN")
    ax[0].hist(mm["margins_sl"], bins=15, alpha=.6, color=C_SL, label="SL")
    ax[0].set_xlabel(f"original item margin ({R}), half B harmful")
    ax[0].legend(frameon=False)
    labs, vals, cis = [], [], []
    for t in A["margin_matched"]:
        labs += [f"{t}\nunmatched", f"{t}\nmatched"]
        vals += [A["margin_matched"][t]["Gap_unmatched"], A["margin_matched"][t]["Gap_margin_matched"]]
    ax[1].bar(range(len(vals)), vals, color=["grey", "k"] * (len(vals) // 2))
    ax[1].set_xticks(range(len(vals)), labs, fontsize=7)
    ax[1].axhline(0, color="k", lw=.6)
    ax[1].set_ylabel("Gap")
    save(fig, "fig4_margin_matched")
    # fig5: validity scatter
    vg = A["validity_gate"]
    if "per_trait" in vg:
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
        for k, lg in enumerate(("en", "sl")):
            pt = vg["per_trait"][f"{R}_{lg}"]
            ax[k].scatter(pt["trait_means"], pt["judged_rates"], color=C_EN if lg == "en" else C_SL)
            ax[k].set_title(f"{lg.upper()}: Spearman {pt['spearman_edit_level']:.2f}, item AUROC {pt['item_auroc']:.2f}")
            ax[k].set_xlabel(f"Δ{R} mean, half-B harmful")
            ax[k].set_ylabel(f"judged refusal rate ({vg.get('judge', 'judge')})")
        save(fig, "fig5_validity")
    # fig6: cross-language transfer slope (SL_B on EN_B across fitted edits) + refusal/compliance components
    TS = A["transfer_slope"]
    tt = [t for t in ["R_seq", "R1", "Rb", "K", "N", "M"] if t in TS]
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.2))
    for i, t in enumerate(tt):
        v, (lo, hi) = TS[t]["slope_SL_on_EN"], TS[t]["ci95"]
        ax[0].errorbar(i, v, yerr=[[v - lo], [hi - v]] if lo is not None else None, fmt="o", color="k", capsize=3)
    ax[0].axhline(1, color="grey", lw=.6, ls="--")
    ax[0].axhline(0, color="k", lw=.6)
    ax[0].set_xticks(range(len(tt)), tt)
    ax[0].set_ylabel("slope of Δ(SL half B) on Δ(EN half B)")
    ax[0].set_title("Same edits, same items: SL moves this much per EN unit")
    dec = A["R_seq_decomposition_halfB"]
    comps = [(f"{ {'harmful': 'harmful', 'harmless': 'benign'}[r]} {k}", dec[f"component_{r}_{k}"]) for r in ("harmful", "harmless") for k in ("lp_ref", "lp_comp")
             if f"component_{r}_{k}" in dec]
    for i, (lab, d) in enumerate(comps):
        ax[1].bar(i - 0.18, d["mean_EN"], 0.35, color=C_EN, label="EN" if i == 0 else None)
        ax[1].bar(i + 0.18, d["mean_SL"], 0.35, color=C_SL, label="SL" if i == 0 else None)
    ax[1].set_xticks(range(len(comps)), [c[0] for c in comps], fontsize=7)
    ax[1].axhline(0, color="k", lw=.6)
    ax[1].set_ylabel("mean Δ log p per token (fitted edits)")
    ax[1].set_title("Refusal-ref vs compliance-ref log-prob change")
    ax[1].legend(frameon=False)
    save(fig, "fig6_transfer_slope")
    print("figures written")


if __name__ == "__main__":
    main()

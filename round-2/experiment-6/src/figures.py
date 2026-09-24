#!/usr/bin/env python3
"""STAGE E figures (PNG + PDF) from results/*.json and the panel parts.

fig1 EN_B vs SL_B scatter per trait · fig2 Gap forest (raw / R2* / SIMEX / margin-matched / halves) · fig3 carrier
delta-R2 both ways · fig4 D distribution and D vs y · fig5 forecast coverage + core · fig6 validity scatter ·
fig7 bilingual reselection Pareto.

  uv run figures.py
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import analysis as AN
from common import FIGS, RES, jload, setup_logging

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
C_EN, C_SL = "#2b6cb0", "#c05621"
NAMES = {"R": "R_seq (harmful)", "R1": "R1 first-token", "Rb": "Rb (benign twins)", "K": "K = log KL_trunc", "N": "N FLORES NLL rise",
         "M": "M MC margin change"}


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{name}.{ext}", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    setup_logging("figures")
    res = jload(RES / "analysis_results.json")
    p, _ = AN.build_panel()
    ed = p.edits
    F = np.where(AN.fitted_mask(ed))[0]
    w0 = AN.unit_weights(p)
    # fig1
    fig, axs = plt.subplots(2, 3, figsize=(10, 6))
    for ax, t in zip(axs.flat, AN.GAP_TRAITS):
        tm = p.traits[t]
        yen = AN.aggregate(tm, w0[t], "B", 0, None, F)
        ysl = AN.aggregate(tm, w0[t], "B", 1, None, F)
        ax.scatter(yen, ysl, s=8, alpha=0.6, color="#555")
        lo, hi = min(yen.min(), ysl.min()), max(yen.max(), ysl.max())
        ax.plot([lo, hi], [lo, hi], lw=0.8, color="#999", ls="--")
        g = res["gap"][t]
        ax.set_title(f"{NAMES[t]}\nR2* EN {g['R2s_plac']:.2f} / SL {g['R2s_test']:.2f}", fontsize=8)
        ax.set_xlabel("EN half B (edit mean)")
        ax.set_ylabel("SL half B")
    fig.suptitle(f"Per-edit EN vs SL trait values (fitted set F, n={len(F)})")
    fig.tight_layout()
    save(fig, "fig1_en_vs_sl_scatter")
    # fig2 forest
    fig, ax = plt.subplots(figsize=(7, 5))
    rows = []
    for t in AN.GAP_TRAITS:
        g, bt = res["gap"][t], res["bootstrap"][t]
        rows.append((f"{t} R2*", g["Gap"], bt["gap_ci95"]))
        rows.append((f"{t} raw", g["Gap_raw"], None))
        rows.append((f"{t} SIMEX", res["simex"][t]["gap_simex"], None))
        mm = res["margin_matched"].get(t)
        if mm:
            rows.append((f"{t} margin-matched", mm["Gap_mm"], mm["ci95"]))
        for h in (0, 1):
            rows.append((f"{t} edit-half {h}", res["stability"][t][f"half{h}"], None))
    XL = 0.6  # traits flagged 'no signal' (F8) have unstable R2* far outside this range; they are drawn clipped
    nosig = {t for t in AN.GAP_TRAITS if any(res["no_signal_F8"][f"{t}_{l}"]["no_signal"] for l in ("en", "sl"))}
    for i, (lab, v, ci) in enumerate(rows[::-1]):
        t = lab.split()[0]
        col = "#bbb" if t in nosig else (C_SL if "R2*" in lab else "#555")
        if v is None or not np.isfinite(v):
            continue
        vc = float(np.clip(v, -XL, XL))
        ax.plot([vc], [i], ">" if v > XL else ("<" if v < -XL else "o"), ms=3.5, color=col)
        if abs(v) > XL:
            ax.text(vc, i + 0.25, f"{v:.2f}", fontsize=5, color=col, ha="center")
        if ci:
            ax.plot(np.clip(ci, -XL, XL), [i, i], lw=1.2, color=col)
    ax.set_xlim(-XL - 0.05, XL + 0.05)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] + (" (no signal)" if r[0].split()[0] in nosig else "") for r in rows[::-1]], fontsize=6)
    ax.axvspan(-0.10, 0.10, color="#ddd", alpha=0.5, zorder=0)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel("Gap = R2*(EN->EN) - R2*(EN->SL)   (band = +/-0.10; axis clipped at +/-0.6, arrows = off-axis values)")
    ax.set_title("Surrogacy gaps (95% joint edit x item bootstrap CI; grey = F8 'no signal' traits)")
    save(fig, "fig2_gap_forest")
    # fig3 carrier
    car = res.get("carrier", {})
    fig, ax = plt.subplots(figsize=(8, 3.5))
    labs, a, b, lo, hi = [], [], [], [], []
    for t in AN.GAP_TRAITS:
        for nm in ("D", "H", "realized", "P"):
            if nm in car.get(t, {}):
                v = car[t][nm]
                labs.append(f"{t}:{nm}")
                a.append(v["dR2_C_given_S0_ridge"])
                b.append(v["dR2_S0_given_C_ridge"])
                lo.append(v["ci95_dR2_C_given_S0"][0])
                hi.append(v["ci95_dR2_C_given_S0"][1])
    x = np.arange(len(labs))
    ax.bar(x - 0.2, a, 0.4, color=C_SL, label="dR2(C | S0)")
    ax.errorbar(x - 0.2, a, yerr=[np.array(a) - np.array(lo), np.array(hi) - np.array(a)], fmt="none", color="k", lw=0.8)
    ax.bar(x + 0.2, b, 0.4, color="#888", label="dR2(S0 | C)")
    ax.axhline(0.05, ls="--", color="k", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, rotation=60, fontsize=7)
    ax.set_ylabel("out-of-fold delta R2 (ridge)")
    ax.legend(fontsize=7)
    ax.set_title("Carrier regression on the SL-minus-EN residual (S0 = cosine b1/b1x, lang b2, kernel mass b3, Omega)")
    save(fig, "fig3_carrier_dr2")
    # fig4 D
    fig, axs = plt.subplots(1, 4, figsize=(12, 3))
    d = ed["D"].values[F]
    axs[0].hist(d[np.isfinite(d)], bins=30, color="#555")
    axs[0].set_xlabel("D = log E_SL - log E_EN")
    for ax, t in zip(axs[1:], ("K", "N", "M")):
        tm = p.traits[t]
        X = AN.xmat(p, w0, "A", 0, F)
        yen = AN.aggregate(tm, w0[t], "B", 0, None, F)
        ysl = AN.aggregate(tm, w0[t], "B", 1, None, F)
        y = (ysl - AN.oof_pred(X, ysl, "gbt", AN.SEEDS[0])) - (yen - AN.oof_pred(X, yen, "gbt", AN.SEEDS[0]))
        ax.scatter(d, y, s=8, alpha=0.6, color=C_SL)
        ax.set_xlabel("D")
        ax.set_ylabel(f"y_{t} (SL - EN residual)")
    fig.tight_layout()
    save(fig, "fig4_exposure_D")
    # fig5 forecast
    fc = res["forecast"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    labs, vals = [], []
    for t in AN.GAP_TRAITS:
        for s in ("E_TPE", "E_R"):
            c = fc[t]["f"]["coverage"].get(s)
            if c:
                labs.append(f"{t}:{s}")
                vals.append(c["coverage_90PI"])
    ax.bar(range(len(vals)), vals, color=[C_EN if "TPE" in l else C_SL for l in labs])
    ax.axhline(0.85, ls="--", color="k", lw=0.8)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labs, rotation=60, fontsize=7)
    ax.set_ylabel("coverage of 90% CV+ PI")
    ax.set_title("Out-of-sample forecast of SL traits from EN traits (never-fitted edits)")
    save(fig, "fig5_forecast_coverage")
    # fig6 validity
    val = res.get("validity", {})
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.3))
    for ax, lang, col in zip(axs, ("en", "sl"), (C_EN, C_SL)):
        cs = val.get(lang, {}).get("conditions", [])
        if cs:
            ax.scatter([c["R_seq"] for c in cs], [c["refused_rate"] for c in cs], color=col, s=14, label="R_seq")
            ax.scatter([c["R1"] for c in cs], [c["refused_rate"] for c in cs], color="#999", s=10, marker="x", label="R1")
        ax.set_title(f"{lang.upper()}: rho(R_seq)={val.get(lang, {}).get('spearman_R_seq', float('nan')):.2f} "
                     f"rho(R1)={val.get(lang, {}).get('spearman_R1', float('nan')):.2f}", fontsize=8)
        ax.set_xlabel("condition mean proxy")
        ax.set_ylabel(f"judged refused rate ({val.get('label_source', '')})")
        ax.legend(fontsize=7)
    fig.tight_layout()
    save(fig, "fig6_validity")
    # fig7 reselection
    rs = res["reselection"]
    pts = rs.get("pareto_points", [])
    if pts:
        fig, ax = plt.subplots(figsize=(5, 4))
        sc = ax.scatter([q["EN"] for q in pts], [q["SL_est"] for q in pts], c=np.log10([q["KL"] + 1e-4 for q in pts]), s=14, cmap="viridis")
        plt.colorbar(sc, label="log10 KL (journal)")
        sel = [q for q in pts if q["edit_id"] == rs["selected_edit"]]
        if sel:
            ax.scatter([sel[0]["EN"]], [sel[0]["SL_est"]], s=80, facecolors="none", edgecolors="r", label="bilingual reselection")
        core = [q for q in pts if q["edit_id"].endswith("_088")]
        if core:
            ax.scatter([core[0]["EN"]], [core[0]["SL_est"]], s=80, marker="s", facecolors="none", edgecolors="k", label="core trial 88")
        ax.plot([0, 100], [0, 100], ls="--", color="#999", lw=0.7)
        ax.set_xlabel("EN keyword refusals (journal, /100)")
        ax.set_ylabel("SL_est (/100)")
        ax.legend(fontsize=7)
        ax.set_title(f"Bilingual reselection ({rs['method'][:40]})", fontsize=8)
        save(fig, "fig7_reselection_pareto")
    # fig8 (exploratory): SL/EN KL transfer vs Heretic direction index and the transfer ratios
    kl_en = np.nanmean(p.traits["K"].vals[:, :, 0], 1)
    kl_sl = np.nanmean(p.traits["K"].vals[:, :, 1], 1)
    lr = np.log(kl_sl + 1e-6) - np.log(kl_en + 1e-6)
    di = np.array([r["direction_index"] if r["direction_scope"] == "global" else np.nan for r in ed["raw_params"]])
    fig, axs = plt.subplots(1, 3, figsize=(12, 3.6))
    m = np.isfinite(di[F])
    s0 = axs[0].scatter(di[F][m], lr[F][m], c=np.log10(kl_en[F][m] + 1e-6), s=12, cmap="viridis")
    plt.colorbar(s0, ax=axs[0], label="log10 mean KL (EN)")
    pl = ~m
    if pl.any():
        axs[0].scatter(np.full(pl.sum(), -2.5), lr[F][pl], s=10, marker="x", color="#999", label="per-layer scope")
        axs[0].legend(fontsize=7)
    axs[0].axhline(0, color="k", lw=0.5)
    axs[0].set_xlabel("Heretic direction_index (global scope; 0 = first decoder layer)")
    axs[0].set_ylabel("log(KL_SL / KL_EN), Dolly continuations")
    axs[0].set_title("SL/EN divergence ratio vs refusal-direction layer (F)", fontsize=8)
    axs[1].scatter(kl_en[F], kl_sl[F], s=10, color="#555")
    lim = [min(kl_en[F].min(), kl_sl[F].min()), max(kl_en[F].max(), kl_sl[F].max())]
    axs[1].plot(lim, lim, ls="--", color="#999", lw=0.7)
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel("mean KL_trunc EN")
    axs[1].set_ylabel("mean KL_trunc SL")
    axs[1].set_title("per-edit divergence, EN vs SL (F)", fontsize=8)
    ts = res.get("transfer_slopes", {})
    tr = [t for t in ("R", "R1", "Rb", "K") if t in ts]
    if tr:
        vals = [ts[t]["ratio_test_over_plac"] for t in tr]
        los = [vals[i] - ts[t]["ratio_ci95"][0] for i, t in enumerate(tr)]
        his = [ts[t]["ratio_ci95"][1] - vals[i] for i, t in enumerate(tr)]
        axs[2].bar(range(len(tr)), vals, yerr=[los, his], color=C_SL, alpha=0.8, capsize=3)
        axs[2].axhline(1, color="k", lw=0.6, ls="--")
        axs[2].set_xticks(range(len(tr)))
        axs[2].set_xticklabels(tr)
        axs[2].set_ylabel("SL response per unit EN response")
        axs[2].set_title("transfer ratio (exploratory; 1 = equal)", fontsize=8)
    fig.tight_layout()
    save(fig, "fig8_transfer_exploratory")


if __name__ == "__main__":
    main()

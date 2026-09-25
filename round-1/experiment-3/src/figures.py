"""Figures fig1-fig7 (PDF + PNG) from analysis_summary.json (numbers only come from saved results)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger

import common as C
from common import LANGS, jload

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"gams3": "#1b6ca8", "gemma": "#d1495b", "en": "#2e7d32", "sl": "#6a1b9a"}
NAME = {"gams3": "GaMS3-12B-Instruct", "gemma": "Gemma-3-12B-it"}


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(C.FIGS / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig1(summary):
    ms = [m for m in summary["per_model"]]
    fig, axes = plt.subplots(1, len(ms), figsize=(5 * len(ms), 3.2), squeeze=False)
    for ax, m in zip(axes[0], ms):
        prof = jload(C.RES / m / "cosine_profile.json")
        ps = jload(C.RES / m / "selection.json")["pos_star"]
        H = len(prof["layers"])
        x = np.arange(H)
        ax.plot(x, [prof["cos_en_sl"][h][ps] for h in x], label="cos(d_EN,d_SL)", color="k")
        ax.plot(x, [prof["ceil_en"][h][ps] for h in x], label="split-half ceiling EN", color=COL["en"], ls="--")
        ax.plot(x, [prof["ceil_sl"][h][ps] for h in x], label="split-half ceiling SL", color=COL["sl"], ls="--")
        ax.plot(x, [prof["cos_en_sl"][h][5] for h in x], label="content-token cos", color="grey", ls=":")
        ax.axvline(jload(C.RES / m / "selection.json")["h_star"], color="orange", lw=1, label="h*")
        ax.set_title(f"{NAME[m]} (pos {jload(C.RES / m / 'selection.json')['pos_star_name']})")
        ax.set_xlabel("hidden index (0 = embeddings)")
        ax.set_ylabel("cosine")
        ax.set_ylim(-0.2, 1.05)
    axes[0][0].legend(fontsize=7, loc="lower right")
    save(fig, "fig1_cosine_profile")


def fig2(summary):
    ms = list(summary["per_model"])
    fig, axes = plt.subplots(1, len(ms), figsize=(5.2 * len(ms), 3.4), squeeze=False)
    for ax, m in zip(axes[0], ms):
        TM = summary["per_model"][m]["transfer_matrix_ablation"]
        M = np.array([[TM[f"{s}->{e}"]["est"] for e in LANGS] for s in LANGS])
        im = ax.imshow(M, vmin=0, vmax=1.5, cmap="viridis")
        for i, s in enumerate(LANGS):
            for j, e in enumerate(LANGS):
                c = TM[f"{s}->{e}"]
                ax.text(j, i, f"{c['est']:.2f}\n[{c['ci95'][0]:.2f},{c['ci95'][1]:.2f}]", ha="center", va="center",
                        color="w" if M[i, j] < 0.9 else "k", fontsize=8)
        ax.set_xticks([0, 1], ["eval EN", "eval SL"])
        ax.set_yticks([0, 1], ["d_EN", "d_SL"])
        ax.set_title(f"{NAME[m]}\nablation transfer T(s->e) of refusal log-odds", fontsize=9)
        plt.colorbar(im, ax=ax, fraction=0.046)
    save(fig, "fig2_transfer_matrix")


def fig3(summary):
    ms = [m for m in summary["per_model"] if summary["per_model"][m]["addition"]]
    if not ms:
        return
    fig, axes = plt.subplots(len(ms), 2, figsize=(8, 3 * len(ms)), squeeze=False)
    for r, m in enumerate(ms):
        cur = summary["per_model"][m]["addition"]["dose_response"]
        for c, l in enumerate(LANGS):
            ax = axes[r][c]
            for vn, st in (("raw_EN", "-"), ("raw_SL", "-"), ("uSL", "--"), ("uEN", "--"), ("R1", ":"), ("R2", ":"), ("R3", ":"),
                           ("R1r", "-."), ("R2r", "-."), ("R3r", "-.")):
                pts = cur.get(f"{vn}|{l}", [])
                if not pts:
                    continue
                a = [p["alpha"] for p in pts]
                y = [p["dR_benign"]["est"] for p in pts]
                lo = [p["dR_benign"]["ci95"][0] for p in pts]
                hi = [p["dR_benign"]["ci95"][1] for p in pts]
                ln = ax.plot(a, y, st, marker="o", ms=3, label=vn)
                ax.fill_between(a, lo, hi, alpha=0.12, color=ln[0].get_color())
            ax.axhline(0, color="k", lw=0.5)
            ax.set_title(f"{NAME[m]}: addition, benign twins, eval {l.upper()}")
            ax.set_xlabel("alpha")
            ax.set_ylabel("induced refusal dR")
    axes[0][0].legend(fontsize=7)
    save(fig, "fig3_addition_dose_response")


def fig4(summary):
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    labels, ests, los, his, cols = [], [], [], [], []
    for m, r in summary["per_model"].items():
        u = r["u_increment"]
        for k in ("I_raw", "I_ctrl", "I_ctrl_rawE", "I_noise", "random_on_top_mean", "random_on_top_rawE_mean", "J_EN_mirror"):
            if k not in u:
                continue
            labels.append(f"{NAME[m].split('-')[0]} {k}")
            ests.append(u[k]["est"])
            los.append(u[k]["ci95"][0])
            his.append(u[k]["ci95"][1])
            cols.append(COL[m])
    y = np.arange(len(labels))[::-1]
    for yi, e, lo, hi, c in zip(y, ests, los, his, cols):
        ax.plot([lo, hi], [yi, yi], color=c, lw=1.5)
    ax.scatter(ests, y, c=cols, zorder=3)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(y, labels)
    ax.set_xlabel("extra drop in SL refusal log-odds (95% item-bootstrap CI)")
    ax.set_title("u_SL increment: raw vs random-on-top control vs split-half noise")
    save(fig, "fig4_u_increment_forest")


def fig5(summary):
    ms = [m for m in summary["per_model"] if summary["per_model"][m]["matched_efficacy"].get("grid_drops")]
    if not ms:
        return
    fig, axes = plt.subplots(1, len(ms), figsize=(4.5 * len(ms), 3.4), squeeze=False)
    for ax, m in zip(axes[0], ms):
        g = summary["per_model"][m]["matched_efficacy"]["grid_drops"]
        for dn, col in (("dEN", COL["en"]), ("dSL", COL["sl"])):
            ax.plot(g[dn]["en"], g[dn]["sl"], marker="o", ms=3, color=col, label=f"partial ablation of {dn} (c=0..1)")
        mx = max(max(g["dEN"]["en"] + g["dSL"]["en"]), max(g["dEN"]["sl"] + g["dSL"]["sl"]))
        ax.plot([0, mx], [0, mx], color="grey", lw=0.6, ls="--")
        ax.set_xlabel("drop in EN refusal log-odds")
        ax.set_ylabel("drop in SL refusal log-odds")
        ax.set_title(f"{NAME[m]}: matched-efficacy curves")
        ax.legend(fontsize=7)
    save(fig, "fig5_matched_efficacy")


def fig6(summary):
    ms = [m for m in summary["validity"] if "condition_level" in summary["validity"][m]]
    if not ms:
        return
    fig, axes = plt.subplots(1, len(ms), figsize=(4.5 * len(ms), 3.3), squeeze=False)
    for ax, m in zip(axes[0], ms):
        v = summary["validity"][m]
        for rec in v["condition_level"]:
            ax.scatter(rec["meanR"], rec["refusal_rate"], color=COL[rec["lang"]])
            ax.annotate(rec["cond_name"].split(":")[1], (rec["meanR"], rec["refusal_rate"]), fontsize=7)
        ax.scatter([], [], color=COL["en"], label="EN")
        ax.scatter([], [], color=COL["sl"], label="SL")
        ax.legend(fontsize=7)
        ax.set_xlabel("condition mean R (teacher-forced)")
        ax.set_ylabel("judged refusal rate")
        ax.set_title(f"{NAME[m]}: rho={v['spearman_condition_level']:.2f}, item AUROC={v['item_auroc']:.2f}")
    save(fig, "fig6_R_validity")


def fig7(summary):
    ms = list(summary["cos_vs_transfer"])
    if not ms:
        return
    fig, axes = plt.subplots(1, len(ms), figsize=(4.5 * len(ms), 3.3), squeeze=False)
    for ax, m in zip(axes[0], ms):
        rows = summary["cos_vs_transfer"][m]["per_layer"]
        x = [r["cos_raw"] for r in rows]
        ax.scatter(x, [r["T_en_to_sl"] for r in rows], color=COL["sl"], label="T(EN->SL)", s=12)
        ax.scatter(x, [r["T_sl_to_en"] for r in rows], color=COL["en"], label="T(SL->EN)", s=12, marker="^")
        ax.axhline(0.8, color="grey", lw=0.6, ls="--")
        ax.set_xlabel("cos(d_EN, d_SL) at layer (pos*)")
        ax.set_ylabel("cross-language transfer (half A)")
        ax.set_ylim(-0.5, max(2.0, min(6.0, np.nanmax([r["T_en_to_sl"] for r in rows] + [r["T_sl_to_en"] for r in rows]) + 0.3)))
        ax.set_title(f"{NAME[m]} (exploratory)")
        ax.legend(fontsize=7)
    save(fig, "fig7_cosine_vs_transfer")


def fig8(summary):
    """Judged refusal rate on half-B harmful prompts per condition, language and model (headline behaviour)."""
    import json

    p = C.RES / "judged_generations.json"
    if not p.exists():
        return
    g = [x for x in json.loads(p.read_text()) if x["kind"] == "jbb_harmful"]
    conds = ["C0", "C1", "C2", "C3", "C4", "C6", "C6r"]
    names = {"C0": "no-op", "C1": "abl d_EN", "C2": "abl d_SL", "C3": "abl span", "C4": "abl u_SL", "C6": "abl rand (frozen)", "C6r": "abl rand (rawE)"}
    ms = [m for m in ("gams3", "gemma") if any(x["model"] == m for x in g)]
    fig, axes = plt.subplots(1, len(ms), figsize=(5.5 * len(ms), 3.4), squeeze=False)
    for ax, m in zip(axes[0], ms):
        for j, l in enumerate(LANGS):
            ys, es = [], []
            for c in conds:
                v = [x["judge_label"] == "refused" for x in g if x["model"] == m and x["condition"] == c and x["lang"] == l]
                pr = float(np.mean(v)) if v else np.nan
                ys.append(pr)
                es.append(1.96 * np.sqrt(pr * (1 - pr) / max(1, len(v))) if v else 0)
            ax.bar(np.arange(len(conds)) + (j - 0.5) * 0.38, ys, 0.38, yerr=es, color=COL[l], label=l.upper(), capsize=2)
        ax.set_xticks(np.arange(len(conds)), [names[c] for c in conds], rotation=35, ha="right", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("judged refusal rate (gpt-4.1)")
        ax.set_title(f"{NAME[m]}: harmful half-B prompts")
        ax.legend(fontsize=7)
    save(fig, "fig8_judged_refusal")


def make_all(summary):
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8):
        try:
            f(summary)
        except (KeyError, ValueError, IndexError, TypeError, FileNotFoundError) as e:
            logger.error(f"{f.__name__} failed: {e!r}")

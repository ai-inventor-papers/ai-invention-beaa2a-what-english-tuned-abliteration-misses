#!/usr/bin/env python3
"""Figures (PDF + PNG) from results/analysis/summary.json, results/<m>/layer_profiles_<m>.npz, results/<m>/mech_<m>.json and
results/<m>/a2_items.parquet. fig1 utility forest; fig2 layer profiles; fig3 frozen vs refit; fig4 A2 scatter;
fig5 KL + generation validity; fig6 readout validity vs judge."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger

import common as C
from common import MODELS, jload, setup_logging

plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False})
COL = {"gams": "#1b6ca8", "gemma": "#d1495b", "en": "#2e7d32", "sl": "#6a1b9a"}
NAME = {"gams": "GaMS3-12B-Instruct", "gemma": "gemma-3-12b-it"}


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(C.FIGS / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"saved {name}")


def fig1(S):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
    tasks = C.TASKS + ["macro"]
    for ax, lang in zip(axes, C.LANGS):
        for k, m in enumerate(MODELS):
            u = S["models"].get(m, {}).get("utility", {})
            if not u:
                continue
            y = np.arange(len(tasks)) + (k - 0.5) * 0.3
            d = [100 * u[lang][t]["delta"] for t in tasks]
            lo = [100 * u[lang][t]["delta_ci95"][0] for t in tasks]
            hi = [100 * u[lang][t]["delta_ci95"][1] for t in tasks]
            ax.errorbar(d, y, xerr=[np.array(d) - lo, np.array(hi) - d], fmt="o", color=COL[m], label=NAME[m], ms=4, capsize=2)
        ax.axvline(0, color="k", lw=0.8)
        ax.axvline(-5, color="grey", ls=":", lw=0.8)
        ax.set_yticks(range(len(tasks)))
        ax.set_yticklabels(tasks)
        ax.set_title(f"{lang.upper()}: edited - original (points)")
        ax.set_xlabel("accuracy change (points, 95% CI)")
    axes[0].legend(loc="lower left", fontsize=7)
    fig.suptitle("Fig. 1 Utility change after the Heretic edit (250 items/task, 0-shot, NF4)")
    save(fig, "fig1_utility_deltas")


def fig2():
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.5))
    for m in MODELS:
        p = C.RES / m / f"layer_profiles_{m}.npz"
        if not p.exists():
            continue
        P = np.load(p)
        L = np.arange(len(P["cos_raw"]))
        c = COL[m]
        axes[0, 0].plot(L, P["cv_dim_en"], color=c, label=f"{NAME[m]} EN")
        axes[0, 0].plot(L, P["cv_dim_sl"], color=c, ls="--", label=f"{NAME[m]} SL")
        axes[0, 1].plot(L, P["cos_raw"], color=c, label=f"{NAME[m]} raw")
        axes[0, 1].plot(L, np.clip(P["cos_corr"], -1, 1.5), color=c, ls="--", label=f"{NAME[m]} ceiling-corrected")
        axes[0, 2].plot(L, P["tr_en2sl_S4"], color=c, label=f"{NAME[m]} EN->SL (S4)")
        axes[0, 2].plot(L, P["tr_sl2en_S4"], color=c, ls="--", label=f"{NAME[m]} SL->EN (S4)")
        axes[1, 0].plot(L, P["cos_lang_dEN"], color=c, label=f"{NAME[m]} cos(lang, d_EN)")
        axes[1, 0].plot(L, P["cos_lang_dSL"], color=c, ls="--", label=f"{NAME[m]} cos(lang, d_SL)")
        axes[1, 1].plot(L, P["s4_frozen_orig_en"], color=c, label=f"{NAME[m]} EN")
        axes[1, 1].plot(L, P["s4_frozen_orig_sl"], color=c, ls="--", label=f"{NAME[m]} SL")
        axes[1, 2].plot(L, P["cos_dEN_heretic"], color=c, label=NAME[m])
        axes[0, 0].axvline(MODELS[m]["primary_layer"], color=c, lw=0.6, ls=":")
    titles = ["S3 grouped-CV DiM AUROC", "cos(d_EN, d_SL): raw vs split-half-corrected", "held-out S4 transfer AUROC (DiM)",
              "language direction vs harm directions", "held-out S4 AUROC, frozen original probe", "cos(d_EN, Heretic refusal dir)"]
    for ax, t in zip(axes.flat, titles):
        ax.set_title(t, fontsize=8)
        ax.set_xlabel("hidden state (layer)")
        ax.legend(fontsize=6)
    fig.suptitle("Fig. 2 Layer profiles (pos -1, winsorized float32; original models)")
    fig.tight_layout()
    save(fig, "fig2_layer_profiles")


def fig3():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, variant in zip(axes, ("plain", "U_projected")):
        labels, xs = [], 0
        for m in MODELS:
            p = C.RES / m / f"mech_{m}.json"
            if not p.exists():
                continue
            fr = jload(p)["primary"]["frozen_vs_refit"]
            for lang in C.LANGS:
                r = fr[f"{variant}|{lang}"]["dim"]
                fo = r["frozen_orig"]["auc"]
                fe = fo + r["frozen_edit_minus_orig"]["diff_vs_2"]
                ro = r["refit_orig"]["auc"]
                re_ = ro + r["refit_edit_minus_orig"]["diff_vs_2"]
                ax.bar([xs, xs + 1, xs + 2.3, xs + 3.3], [fo, fe, ro, re_], color=[COL[m], COL[m], "#999", "#999"],
                       alpha=0.9, edgecolor="k", hatch=["", "//", "", "//"])
                labels.append((xs + 1.6, f"{m}\n{lang.upper()}\n{r['class']}"))
                xs += 5
        ax.set_xticks([l[0] for l in labels])
        ax.set_xticklabels([l[1] for l in labels], fontsize=7)
        ax.set_ylim(0.3, 1.01)
        ax.axhline(0.5, color="k", lw=0.6, ls=":")
        ax.set_ylabel("S4 AUROC (harmful vs twin)")
        ax.set_title(f"{variant}: frozen orig | frozen edit(//) | refit orig | refit edit(//)", fontsize=8)
    fig.suptitle("Fig. 3 Frozen vs refit probes before/after the edit (primary site)")
    save(fig, "fig3_frozen_vs_refit")


def fig4(S):
    fig, axes = plt.subplots(2, 2, figsize=(9, 7.5))
    for i, m in enumerate(MODELS):
        p = C.RES / m / "a2_items.parquet"
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        a2 = S["models"][m]["A2"]
        R = "R_seq" if "R_seq" in a2 else "R1"
        s = (d.s_frozen_orig - d.s_frozen_orig.mean()) / d.s_frozen_orig.std()
        for j, lang in enumerate(C.LANGS):
            ax = axes[i, j]
            mm = (d.lang == lang).values
            for ck, c in (("orig", "#555"), ("edit", COL[m])):
                ax.scatter(s[mm], d[f"{R}_{ck}"][mm], s=5, alpha=0.4, color=c, label=ck)
                b = np.polyfit(s[mm], d[f"{R}_{ck}"][mm], 1)
                xx = np.linspace(s[mm].min(), s[mm].max(), 10)
                ax.plot(xx, np.polyval(b, xx), color=c)
            pr = a2[R]["per_lang"][lang]["primary"]
            ax.set_title(f"{NAME[m]} {lang.upper()}: slope ratio {pr['slope_ratio']:.2f} "
                         f"[{pr['slope_ratio_ci90'][0]:.2f},{pr['slope_ratio_ci90'][1]:.2f}] ({a2[R]['decision']})", fontsize=7)
            ax.set_xlabel("original frozen DiM score s (z)")
            ax.set_ylabel(R)
            ax.legend(fontsize=6)
    fig.suptitle("Fig. 4 A2: refusal readout vs original harmfulness evidence, pre/post edit")
    fig.tight_layout()
    save(fig, "fig4_a2_scatter")


def fig5(S):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    ax = axes[0]
    k = 0
    for m in MODELS:
        p = C.RES / m / "kl_r1.json"
        if not p.exists():
            continue
        d = pd.DataFrame(jload(p)["rows"])
        for lang in C.LANGS:
            for key, off in (("KL1", 0), ("KL32", 0.35)):
                v = d[(d.role == "harmless") & (d.lang == lang)][key]
                ax.boxplot(np.log10(v + 1e-6), positions=[k + off], widths=0.3, showfliers=False,
                           patch_artist=True, boxprops={"facecolor": COL[m] if key == "KL1" else "white"})
            ax.text(k + 0.15, -4.8, f"{m}\n{lang.upper()}", ha="center", fontsize=7)
            k += 1
    ax.set_ylabel("log10 KL(orig||edit) on held-out S4 harmless (filled=KL1, open=KL32)")
    ax.set_xticks([])
    ax = axes[1]
    gv = S.get("generation_validity", {})
    rows = []
    for key, v in gv.items():
        m, ck, kind, lang = key.split("|")
        if kind != "s4_harmless":
            continue
        rows.append((f"{m}\n{ck}\n{lang}", v["empty"], v["malformed_rule"], v["wrong_lang"], v.get("judge_refused", np.nan)))
    if rows:
        x = np.arange(len(rows))
        for j, (lab, c) in enumerate((("empty", "#999"), ("malformed(rule)", "#e07a5f"), ("wrong language", "#3d405b"), ("judged refused", "#81b29a"))):
            ax.bar(x + (j - 1.5) * 0.2, [r[j + 1] for r in rows], width=0.2, label=lab, color=c)
        ax.set_xticks(x)
        ax.set_xticklabels([r[0] for r in rows], fontsize=6)
        ax.legend(fontsize=6)
        ax.set_ylabel("rate on S4 harmless generations (128 tok)")
    fig.suptitle("Fig. 5 Harmless divergence and generation validity")
    save(fig, "fig5_kl_validity")


def fig6(S):
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, R in zip(axes, ("R_seq", "R1")):
        xs, labs = [], []
        for m in MODELS:
            g = S["models"].get(m, {}).get("gate", {})
            for lang in C.LANGS:
                if lang in g and R in g[lang] and "item_auroc" in g[lang][R]:
                    xs.append((g[lang][R]["item_auroc"], g[lang][R]["cond_spearman_16cells"]))
                    labs.append(f"{m} {lang.upper()}")
        if xs:
            x = np.arange(len(xs))
            ax.bar(x - 0.2, [a for a, _ in xs], 0.4, label="item AUROC")
            ax.bar(x + 0.2, [b for _, b in xs], 0.4, label="16-cell Spearman")
            ax.axhline(0.85, color="k", ls=":")
            ax.set_xticks(x)
            ax.set_xticklabels(labs, fontsize=7)
            ax.set_ylim(0, 1.02)
        ax.set_title(f"{R} validity vs judged refusal (gate 0.85)", fontsize=8)
        ax.legend(fontsize=6)
    fig.suptitle("Fig. 6 Readout validity gate")
    save(fig, "fig6_readout_validity")


def fig7():
    """Drift geometry: separation along the frozen axis vs information in its orthogonal complement, per layer."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for m in MODELS:
        p = C.RES / m / f"drift_geometry_{m}.npz"
        if not p.exists():
            continue
        P = np.load(p)
        L = np.arange(len(P["sep_frozen_orig_en"]))
        for lang, ls in (("en", "-"), ("sl", "--")):
            axes[0].plot(L, P[f"sep_frozen_orig_{lang}"], color="#555", ls=ls, lw=0.8)
            axes[0].plot(L, P[f"sep_frozen_edit_{lang}"], color=COL[m], ls=ls, label=f"{NAME[m]} {lang.upper()} edit")
            ok = np.isfinite(P[f"auc_compl_frozen_edit_{lang}"])
            axes[1].plot(L[ok], P[f"auc_compl_frozen_orig_{lang}"][ok], color="#555", ls=ls, lw=0.8)
            axes[1].plot(L[ok], P[f"auc_compl_frozen_edit_{lang}"][ok], color=COL[m], ls=ls, label=f"{NAME[m]} {lang.upper()} edit")
            axes[2].plot(L, P[f"cos_refit_orig_edit_{lang}"], color=COL[m], ls=ls, label=f"{NAME[m]} {lang.upper()}")
        for ax in axes:
            ax.axvline(MODELS[m]["primary_layer"], color=COL[m], lw=0.6, ls=":")
    axes[0].set_title("Cohen's d along the FROZEN S3 axis (grey = original)", fontsize=8)
    axes[1].set_title("grouped-CV AUROC with the frozen axis projected OUT", fontsize=8)
    axes[2].set_title("cos(refit harm axis orig, refit harm axis edit)", fontsize=8)
    for ax in axes:
        ax.set_xlabel("hidden state (layer)")
        ax.legend(fontsize=6)
    fig.suptitle("Fig. 7 Where the frozen probe fails: axis-aligned separation removed, off-axis information kept (S4, pos -1)")
    fig.tight_layout()
    save(fig, "fig7_drift_geometry")


def fig8():
    """Exploratory edit-strength dose-response: refusal proxies vs LoRA scale factor f, EN vs SL."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for m in MODELS:
        p = C.RES / "dose" / f"dose_{m}.json"
        if not p.exists():
            continue
        d = jload(p)
        fs = [float(k) for k in d["per_factor"]]
        pf = list(d["per_factor"].values())
        for lang, ls in (("en", "-"), ("sl", "--")):
            axes[0].plot(fs, [100 * v[f"gen_marker_refusal|{lang}"] for v in pf], color=COL[m], ls=ls, marker="o", ms=3, label=f"{NAME[m]} {lang.upper()}")
            axes[1].plot(fs, [100 * v[f"R_seq_pos_frac|{lang}|harmful"] for v in pf], color=COL[m], ls=ls, marker="o", ms=3, label=f"{NAME[m]} {lang.upper()}")
            axes[2].plot(fs, [max(v[f"KL1_harmless_mean|{lang}"], 1e-5) for v in pf], color=COL[m], ls=ls, marker="o", ms=3, label=f"{NAME[m]} {lang.upper()}")
    axes[0].set_title("marker refusal of 48 harmful S4 prompts (%)", fontsize=8)
    axes[1].set_title("share of harmful S4 prompts with R_seq > 0 (%)", fontsize=8)
    axes[2].set_title("mean first-token KL on S4 harmless (log)", fontsize=8)
    axes[2].set_yscale("log")
    for ax in axes:
        ax.axvline(1.0, color="k", lw=0.6, ls=":")
        ax.set_xlabel("edit strength f (LoRA delta x f; f=1 = core edit)")
        ax.legend(fontsize=6)
    fig.suptitle("Fig. 8 Exploratory dose-response: the Gemma edit needs ~2x strength to suppress Slovene refusal; GaMS EN and SL move together")
    fig.tight_layout()
    save(fig, "fig8_dose_response")


def main():
    setup_logging("figures")
    S = jload(C.RES / "analysis" / "summary.json")
    for f in (lambda: fig1(S), fig2, fig3, lambda: fig4(S), lambda: fig5(S), lambda: fig6(S), fig7, fig8):
        try:
            f()
        except (KeyError, ValueError, FileNotFoundError, IndexError, TypeError) as e:
            logger.exception(f"figure failed: {e!r}")


if __name__ == "__main__":
    main()

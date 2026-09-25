#!/usr/bin/env python3
"""PHASE 1 - PARTIAL transition curves: nonparametric LOESS + proportional-odds peaks, Delta_peak, INVALID curve,
continuation-ratio sensitivity, PO-vs-multinomial check, out-of-panel prediction (C3-iii), Holm, falsifier."""
from __future__ import annotations

import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from loguru import logger
from scipy.special import expit
from scipy.stats import spearmanr

import common as C
import ladders as L
import po

FZ = C.jload(C.CFG / "FREEZE_iter4_eval.json")
SEEDS, B = FZ["seeds"], FZ["B"]
GRID = np.linspace(-2.0, 2.5, 181)
lowess = sm.nonparametric.lowess


def verify_freeze() -> float:
    want = dict(l.split()[::-1] for l in (C.CFG / "FREEZE.sha256").read_text().splitlines())
    got = C.sha256_file(C.CFG / "FREEZE_iter4_eval.json")
    if got != want["configs/FREEZE_iter4_eval.json"]:
        raise SystemExit(f"FREEZE hash does not verify ({got}) - refusing to run")
    return os.path.getmtime(C.CFG / "FREEZE_iter4_eval.json")


def cell_table(d: pd.DataFrame, extra: list[str]) -> pd.DataFrame:
    g = d[d.class_4way.notna()].groupby(["cell_id", "language"] + extra)
    t = g.class_4way.value_counts().unstack(fill_value=0).reindex(columns=C.CLASSES4, fill_value=0)
    t["n"] = t.sum(axis=1)
    t["n_rpc"] = t[["REFUSED", "PARTIAL", "COMPLIED"]].sum(axis=1)
    for k in C.CLASSES4:
        t[f"share_{k}"] = t[k] / t["n"]
    # PARTIAL share among the ordinal outcomes (INVALID modelled separately)
    t["partial_share_rpc"] = t["PARTIAL"] / t["n_rpc"].replace(0, np.nan)
    return t.reset_index()


def smooth(x: np.ndarray, y: np.ndarray, span: float) -> np.ndarray:
    o = np.argsort(x)
    x, y = x[o], y[o]
    if len(np.unique(x)) < 3:
        return np.interp(GRID, *(_agg(x, y)))
    fit = lowess(y, x, frac=span, it=0, return_sorted=True)
    xs, ys = _agg(fit[:, 0], fit[:, 1])
    out = np.interp(GRID, xs, ys, left=np.nan, right=np.nan)
    return out


def _agg(x, y):
    ux = np.unique(x)
    return ux, np.array([y[x == u].mean() for u in ux])


def loco_err(t: pd.DataFrame, span: float) -> float:
    """leave-one-cell-out prediction error of the PARTIAL share on ladder t (per language)."""
    errs = []
    for lang in ("en", "sl"):
        s = t[t.language == lang]
        for i in range(len(s)):
            tr = s.drop(s.index[i])
            x, y = tr.z.to_numpy(), tr.partial_share_rpc.to_numpy()
            if len(np.unique(x)) < 3:
                continue
            f = lowess(y, x, frac=span, it=0, return_sorted=True)
            xs, ys = _agg(f[:, 0], f[:, 1])
            p = np.interp(s.z.iloc[i], xs, ys)
            errs.append((p - s.partial_share_rpc.iloc[i]) ** 2)
    return float(np.mean(errs)) if errs else np.inf


def curve_stats(curve: np.ndarray, zmin: float, zmax: float) -> dict:
    m = (GRID >= zmin) & (GRID <= zmax) & np.isfinite(curve)
    c, g = curve[m], GRID[m]
    if len(c) == 0:
        return {"peak_height": np.nan, "peak_z": np.nan, "max_minus_min": np.nan}
    return {"peak_height": float(c.max()), "peak_z": float(g[np.argmax(c)]), "max_minus_min": float(c.max() - c.min())}


def nonpar(t: pd.DataFrame, span: float, rng: np.random.Generator, B_: int, group_col: str = "ladder") -> dict:
    """two-level bootstrap: cells within ladder (group_col), then items within cell (multinomial on counts)."""
    out = {}
    zmin, zmax = t.z.min(), t.z.max()
    for lang in ("en", "sl"):
        s = t[t.language == lang].reset_index(drop=True)
        base = smooth(s.z.to_numpy(), s.partial_share_rpc.to_numpy(), span)
        st = curve_stats(base, zmin, zmax)
        boots = {"peak_height": [], "peak_z": [], "max_minus_min": []}
        curves = []
        groups = s.groupby(group_col).indices
        for b in range(B_):
            idx = np.concatenate([rng.choice(ix, len(ix), replace=True) for ix in groups.values()])
            ss = s.iloc[idx]
            n = ss.n_rpc.to_numpy().astype(int)
            p = ss.partial_share_rpc.to_numpy()
            y = rng.binomial(n, np.clip(p, 0, 1)) / np.maximum(n, 1)
            cb = smooth(ss.z.to_numpy() + rng.normal(0, 1e-6, len(ss)), y, span)
            curves.append(cb)
            cs = curve_stats(cb, zmin, zmax)
            for k in boots:
                boots[k].append(cs[k])
        curves = np.array(curves)
        out[lang] = {**st, **{f"{k}_ci": C.ci(np.array(v)) for k, v in boots.items()},
                     "p_mmm_le_0.05": float(np.mean(np.array(boots["max_minus_min"]) <= 0.05)),
                     "curve": base.tolist(), "band_lo": np.nanpercentile(curves, 2.5, axis=0).tolist(),
                     "band_hi": np.nanpercentile(curves, 97.5, axis=0).tolist(), "n_cells": int(len(s)),
                     "boot_peak_z": boots["peak_z"]}
    d = np.array(out["sl"]["boot_peak_z"]) - np.array(out["en"]["boot_peak_z"])
    out["delta_argmax"] = {"point": out["sl"]["peak_z"] - out["en"]["peak_z"], "ci": C.ci(d),
                           "p_two_sided": float(2 * min(np.mean(d <= 0), np.mean(d >= 0)))}
    for lang in ("en", "sl"):
        out[lang].pop("boot_peak_z")
    return out


def po_block(d: pd.DataFrame, set_fe: bool, rng: np.random.Generator, B_: int) -> dict:
    X, y, names, g = L.design(d, set_fe)
    f = po.fit(X, y)
    V = po.cluster_cov(f["p"], X, y, g)

    def pk(p):
        t0 = p[0]; t1 = p[0] + np.exp(p[1]); b = p[2:]
        m = (t0 + t1) / 2
        pe = m / b[0]; ps = (m - b[2]) / (b[0] + b[1])
        return np.array([pe, ps, ps - pe])
    est = pk(f["p"])
    J = np.zeros((3, len(f["p"])))
    for i in range(len(f["p"])):
        e = np.zeros(len(f["p"])); e[i] = 1e-6
        J[:, i] = (pk(f["p"] + e) - pk(f["p"] - e)) / 2e-6
    se = np.sqrt(np.clip(np.diag(J @ V @ J.T), 0, None))
    # item-cluster bootstrap
    ug, inv = np.unique(g, return_inverse=True)
    groups = [np.where(inv == k)[0] for k in range(len(ug))]
    bs = []
    for b in range(B_):
        pick = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([groups[k] for k in pick])
        fb = po.fit(X[idx], y[idx], p0=f["p"])
        bs.append(pk(fb["p"]))
    bs = np.array(bs)
    bs = bs[np.isfinite(bs).all(axis=1)]
    names_out = ["peak_EN", "peak_SL", "delta_peak"]
    res = {"coef": dict(zip(["theta0", "log_gap"] + names, f["p"].tolist())),
           "coef_se_cluster": dict(zip(["theta0", "log_gap"] + names, np.sqrt(np.diag(V)).tolist())),
           "nll": f["nll"], "n": int(len(y)), "n_clusters": int(len(ug)), "converged": f["ok"]}
    for j, nm in enumerate(names_out):
        res[nm] = {"point": float(est[j]), "delta_ci": [float(est[j] - 1.96 * se[j]), float(est[j] + 1.96 * se[j])],
                   "boot_ci": C.ci(bs[:, j]), "boot_n": int(len(bs))}
    dd = bs[:, 2]
    res["delta_peak"]["p_boot_two_sided"] = float(2 * min(np.mean(dd <= 0), np.mean(dd >= 0)))
    # peak heights and predicted PARTIAL share per language on the grid (average placement)
    t0, t1 = f["theta0"], f["theta1"]
    b = f["beta"]
    res["curve_en"] = po.partial_share(t0, t1, b[0] * GRID).tolist()
    res["curve_sl"] = po.partial_share(t0, t1, (b[0] + b[1]) * GRID + b[2]).tolist()
    res["peak_height_EN"] = float(po.partial_share(t0, t1, np.array([(t0 + t1) / 2]))[0])
    res["peak_height_SL"] = res["peak_height_EN"]  # PO: identical peak height by construction
    # PO check: multinomial logit on the same design
    try:
        mn = sm.MNLogit(y, sm.add_constant(X)).fit(disp=0, maxiter=300)
        k_po = len(f["p"]); k_mn = mn.params.size
        aic_po = 2 * k_po + 2 * f["nll"]; aic_mn = 2 * k_mn - 2 * mn.llf
        p_mn = mn.predict(sm.add_constant(X))
        eta = X @ b
        p_po = po.shares(t0, t1, eta)
        dcell = pd.DataFrame(np.abs(np.asarray(p_mn) - p_po)).groupby(d[d.class_4way.isin(L.YMAP)].cell_id.to_numpy()).mean()
        res["po_check"] = {"aic_po": float(aic_po), "aic_multinomial": float(aic_mn), "aic_diff_po_minus_mn": float(aic_po - aic_mn),
                           "max_cell_mean_abs_share_divergence": float(dcell.to_numpy().max()),
                           "violated": bool((aic_po - aic_mn) > 10 and dcell.to_numpy().max() > 0.05)}
    except Exception as e:  # noqa: BLE001 - logged, check reported as not run
        logger.warning(f"MNLogit failed: {e}")
        res["po_check"] = {"error": str(e)[:200]}
    return res


def cr_block(d: pd.DataFrame, set_fe: bool, rng: np.random.Generator, B_: int) -> dict:
    """continuation-ratio sensitivity: logit P(Y>0) and logit P(Y>1 | Y>0), each with z, z*SL, SL (+ set FE)."""
    X, y, names, g = L.design(d, set_fe)
    Xc = sm.add_constant(X)

    def fitpk(ix):
        Xi, yi = Xc[ix], y[ix]
        m1 = sm.Logit((yi > 0).astype(float), Xi).fit(disp=0, maxiter=200)
        s = yi > 0
        m2 = sm.Logit((yi[s] > 1).astype(float), Xi[s]).fit(disp=0, maxiter=200)
        pk = {}
        for lang, sl in (("EN", 0.0), ("SL", 1.0)):
            row = np.zeros((len(GRID), Xc.shape[1])); row[:, 0] = 1; row[:, 1] = GRID; row[:, 2] = GRID * sl; row[:, 3] = sl
            p1 = expit(row @ m1.params); p2 = expit(row @ m2.params)
            part = p1 * (1 - p2)
            pk[lang] = (float(GRID[np.argmax(part)]), part)
        return pk
    base = fitpk(np.arange(len(y)))
    ug, inv = np.unique(g, return_inverse=True)
    groups = [np.where(inv == k)[0] for k in range(len(ug))]
    ds = []
    for b in range(B_):
        try:
            pk = fitpk(np.concatenate([groups[k] for k in rng.integers(0, len(ug), len(ug))]))
            ds.append(pk["SL"][0] - pk["EN"][0])
        except Exception:  # noqa: BLE001 - separation in a resample; counted
            continue
    return {"peak_EN": base["EN"][0], "peak_SL": base["SL"][0], "delta_peak": base["SL"][0] - base["EN"][0],
            "delta_peak_boot_ci": C.ci(np.array(ds)), "boot_n": len(ds),
            "curve_en": base["EN"][1].tolist(), "curve_sl": base["SL"][1].tolist()}


def invalid_block(d: pd.DataFrame) -> dict:
    dd = d[d.class_4way.notna()]
    yv = (dd.class_4way == "INVALID").astype(float).to_numpy()
    sl = (dd.language == "sl").to_numpy().astype(float)
    X = sm.add_constant(np.stack([dd.z.to_numpy(), dd.z.to_numpy() * sl, sl], axis=1))
    out = {"invalid_rate_overall": float(yv.mean()), "n": int(len(yv))}
    if yv.sum() < 5:
        out["note"] = "fewer than 5 INVALID outputs; curve not fitted (INVALID ~ 0 across the ladder)"
        return out
    try:
        m = sm.Logit(yv, X).fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups": pd.factorize(dd.semantic_item_id)[0]})
        out.update({"coef": dict(zip(["const", "z", "z_x_SL", "SL"], m.params.tolist())),
                    "se_cluster": dict(zip(["const", "z", "z_x_SL", "SL"], m.bse.tolist()))})
        for lang, s in (("en", 0.0), ("sl", 1.0)):
            row = np.stack([np.ones_like(GRID), GRID, GRID * s, np.full_like(GRID, s)], axis=1)
            out[f"curve_{lang}"] = expit(row @ m.params).tolist()
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:200]
    return out


def c3iii(df: pd.DataFrame, rng: np.random.Generator) -> tuple[dict, pd.DataFrame]:
    d = df[(df.role == "harmful") & df.language.isin(["en", "sl"]) & df.dose_z.notna() & (df.operator != "act")
           & df.source.isin(["exp9", "exp10", "exp11", "exp12"])].copy()
    d["z"] = d.dose_z
    t = cell_table(d, ["source"])
    w = t.pivot_table(index=["cell_id", "source"], columns="language", values=["partial_share_rpc", "n_rpc", "z"] if False else ["partial_share_rpc", "n_rpc"]).dropna()
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    w = w[(w.n_rpc_en >= 10) & (w.n_rpc_sl >= 10)].reset_index()
    zc = d.drop_duplicates("cell_id").set_index("cell_id").z
    w["z"] = w.cell_id.map(zc)
    w["obs_strict_minus_broad"] = w.partial_share_rpc_en - w.partial_share_rpc_sl  # identity: = P_EN - P_SL
    preds = []
    for held in ("exp9", "exp10", "exp11", "exp12"):
        tr = d[d.source != held]
        X, y, _, _ = L.design(tr, False)
        f = po.fit(X, y)
        b = f["beta"]
        te = w[w.source == held]
        pe = po.partial_share(f["theta0"], f["theta1"], b[0] * te.z.to_numpy())
        ps = po.partial_share(f["theta0"], f["theta1"], (b[0] + b[1]) * te.z.to_numpy() + b[2])
        preds.append(pd.DataFrame({"cell_id": te.cell_id, "fold": held, "pred": pe - ps}))
    P = pd.concat(preds)
    w = w.merge(P, on="cell_id")
    rho = spearmanr(w.pred, w.obs_strict_minus_broad).statistic
    ols = sm.OLS(w.obs_strict_minus_broad, sm.add_constant(w.pred)).fit()
    mae = float(np.mean(np.abs(w.pred - w.obs_strict_minus_broad)))
    # permuted-dose null: permute z within each held-out fold, recompute predictions from the fold model
    fold_models = {}
    for held in ("exp9", "exp10", "exp11", "exp12"):
        X, y, _, _ = L.design(d[d.source != held], False)
        fold_models[held] = po.fit(X, y)
    null_rho, null_mae = [], []
    for _ in range(B["c3iii_perm"]):
        pr = np.empty(len(w))
        for held, f in fold_models.items():
            m = (w.fold == held).to_numpy()
            zp = rng.permutation(w.z.to_numpy()[m])
            b = f["beta"]
            pr[m] = po.partial_share(f["theta0"], f["theta1"], b[0] * zp) - po.partial_share(f["theta0"], f["theta1"], (b[0] + b[1]) * zp + b[2])
        null_rho.append(spearmanr(pr, w.obs_strict_minus_broad).statistic)
        null_mae.append(np.mean(np.abs(pr - w.obs_strict_minus_broad)))
    null_rho = np.array(null_rho)
    per_fold = {}
    for held in ("exp9", "exp10", "exp11", "exp12"):
        s = w[w.fold == held]
        per_fold[held] = {"n_cells": int(len(s)), "spearman": float(spearmanr(s.pred, s.obs_strict_minus_broad).statistic) if len(s) > 3 else None,
                          "mae": float(np.mean(np.abs(s.pred - s.obs_strict_minus_broad))) if len(s) else None}
    out = {"n_cells": int(len(w)), "spearman": float(rho), "calibration_slope": float(ols.params.iloc[1]),
           "calibration_intercept": float(ols.params.iloc[0]), "mae": mae,
           "null_spearman_95": C.ci(null_rho), "p_perm_spearman": float((1 + np.sum(null_rho >= rho)) / (1 + len(null_rho))),
           "null_mae_mean": float(np.mean(null_mae)), "p_perm_mae": float((1 + np.sum(np.array(null_mae) <= mae)) / (1 + len(null_mae))),
           "per_fold": per_fold,
           "note": "observed quantity per cell = strict gap - broad gap = P_EN - P_SL (algebraic identity); the test is whether "
                   "WHERE a cell sits in dose predicts it out of panel"}
    return out, w


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, max(running, (m - i) * p))
        running = adj
        out[k] = {"p": p, "p_holm": adj, "reject_0.05": adj < 0.05}
    return out


def figure(res: dict) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    col = {"en": "#1f77b4", "sl": "#d62728"}
    for ax, key, title in ((axes[0], "L1_exp11_f_ladder", "L1: exp11 f-ladder (Gemma)"),
                           (axes[1], "L2_exp9_c_grid", "L2: exp9 c-grid (Gemma, 10 sets)"),
                           (axes[2], "pooled_designed_ladders", "L1+L2 pooled (C3-i)")):
        r = res[key]["nonparametric"]
        cells = pd.DataFrame(res[key]["cells"])
        for lang in ("en", "sl"):
            c = np.array(r[lang]["curve"], float)
            ax.plot(GRID, c, color=col[lang], label=f"{lang.upper()} LOESS")
            ax.fill_between(GRID, np.array(r[lang]["band_lo"], float), np.array(r[lang]["band_hi"], float), color=col[lang], alpha=0.15)
            s = cells[cells.language == lang]
            ax.scatter(s.z, s.partial_share_rpc, color=col[lang], s=12, alpha=0.6)
            if "po" in res[key]:
                ax.plot(GRID, res[key]["po"][f"curve_{lang}"], color=col[lang], ls="--", lw=1, label=f"{lang.upper()} prop. odds")
        m = np.isfinite(np.array(res[key]["nonparametric"]["en"]["curve"], float))
        ax.set_xlim(GRID[m].min() - 0.1, GRID[m].max() + 0.1)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("dose (z within ladder)")
        ax.set_ylabel("PARTIAL share of R/P/C (harmful)")
        ax.set_ylim(0, 1)
    axes[0].legend(fontsize=8)
    fig.suptitle("PARTIAL share vs dose, 95% two-level bootstrap bands; workhorse judge", fontsize=11)
    fig.tight_layout()
    fig.savefig(C.FIG / "fig1_partial_share_vs_dose.png", dpi=150)
    fig.savefig(C.FIG / "fig1_partial_share_vs_dose.pdf")
    plt.close(fig)


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("p1_curves")
    t_freeze = verify_freeze()
    rng_np = np.random.default_rng(SEEDS["bootstrap_nonpar"])
    rng_po = np.random.default_rng(SEEDS["bootstrap_po"])
    rng_perm = np.random.default_rng(SEEDS["permutation"])
    B_np = int(os.environ.get("B_NONPAR", B["nonparametric"]))
    B_po = int(os.environ.get("B_PO", B["po_bootstrap"]))
    df = L.load_pooled(["source", "panel", "model", "cell_id", "gid", "semantic_item_id", "language", "role", "class_4way",
                        "arm_kind", "operator", "dose_z", "dose_group", "strength_multiplier"])
    df = df[df.language.isin(["en", "sl"])]
    L1 = L.with_z(L.ladder_L1(df)); L1["ladder"] = "L1"
    L2 = L.with_z(L.ladder_L2(df)); L2["ladder"] = "L2"
    t1 = cell_table(L1, ["ladder", "z", "strength"]); t2 = cell_table(L2, ["ladder", "z", "strength", "set_id"])
    # span selection on the OTHER ladder (held-out), grid from the freeze
    spans = [0.3, 0.5, 0.7, 0.9]
    err_on_L2 = {s: loco_err(t2, s) for s in spans}
    err_on_L1 = {s: loco_err(t1, max(s, 0.8)) for s in spans}
    span_for_L1 = min(err_on_L2, key=err_on_L2.get)
    span_for_L2 = min(err_on_L1, key=err_on_L1.get)
    span_pooled = span_for_L1  # chosen on L2's LOCO error (disjoint model panel for exp10 below)
    logger.info(f"spans: L1 {span_for_L1} (L2 err {err_on_L2}), L2 {span_for_L2} (L1 err {err_on_L1})")
    res = {"spans": {"L1_chosen_on_L2": span_for_L1, "L2_chosen_on_L1": span_for_L2, "err_on_L2": err_on_L2, "err_on_L1": err_on_L1}}
    tp = pd.concat([t1, t2.drop(columns=["set_id"])], ignore_index=True)
    for key, d, t, fe, span in (("L1_exp11_f_ladder", L1, t1, False, max(span_for_L1, 0.8)),
                                ("L2_exp9_c_grid", L2, t2, True, span_for_L2),
                                ("pooled_designed_ladders", pd.concat([L1, L2]), tp, None, span_for_L2)):
        tt = time.time()
        r = {"cells": t.to_dict(orient="records"), "span": span,
             "nonparametric": nonpar(t, span, rng_np, B_np)}
        if fe is not None:
            r["po"] = po_block(d, fe, rng_po, B_po)
            r["continuation_ratio"] = cr_block(d, fe, rng_po, 200)
            r["invalid_curve"] = invalid_block(d)
        res[key] = r
        logger.info(f"{key}: {time.time() - tt:.0f}s")
    # exploratory pooled cross-panel fit (z within panel|operator; weight/lora operators; group FE)
    ex = df[(df.role == "harmful") & df.dose_z.notna() & (df.operator != "act") & df.source.isin(["exp9", "exp10", "exp11", "exp12"])].copy()
    ex["z"] = ex.dose_z
    ex["set_id"] = ex.dose_group
    res["pooled_exploratory_all_panels"] = {"po": po_block(ex, True, rng_po, 100), "invalid_curve": invalid_block(ex),
                                           "n_cells": int(ex.cell_id.nunique()), "dose_groups": sorted(ex.dose_group.unique())}
    ac = df[(df.role == "harmful") & df.dose_z.notna() & (df.operator == "act")].copy()
    ac["z"] = ac.dose_z
    res["activation_arms_invalid_curve"] = invalid_block(ac)
    # C3-iii
    c3, w = c3iii(df, rng_perm)
    res["C3_iii"] = c3
    w.to_csv(C.RES / "c3iii_out_of_panel_cells.csv", index=False)
    # confirmatory family + Holm
    np_ = res["pooled_designed_ladders"]["nonparametric"]
    prim = {k: ("nonparametric" if res[k]["po"].get("po_check", {}).get("violated") else "proportional_odds")
            for k in ("L1_exp11_f_ladder", "L2_exp9_c_grid")}

    def c3ii_p(k):
        return (res[k]["nonparametric"]["delta_argmax"]["p_two_sided"] if prim[k] == "nonparametric"
                else res[k]["po"]["delta_peak"]["p_boot_two_sided"])

    def c3ii_point(k):
        return (res[k]["nonparametric"]["delta_argmax"]["point"] if prim[k] == "nonparametric"
                else res[k]["po"]["delta_peak"]["point"])
    pv = {"C3-i EN": np_["en"]["p_mmm_le_0.05"], "C3-i SL": np_["sl"]["p_mmm_le_0.05"],
          "C3-ii L1": c3ii_p("L1_exp11_f_ladder"), "C3-ii L2": c3ii_p("L2_exp9_c_grid"),
          "C3-iii": c3["p_perm_spearman"]}
    res["holm"] = holm(pv)
    # primary estimator per ladder depends on the PO check
    verdict = {}
    for key in ("L1_exp11_f_ladder", "L2_exp9_c_grid"):
        primary = prim[key]
        dp = res[key]["po"]["delta_peak"]
        verdict[key] = {"primary_estimator": primary, "delta_peak_po": dp["point"], "delta_peak_po_boot_ci": dp["boot_ci"],
                        "delta_argmax_nonpar": res[key]["nonparametric"]["delta_argmax"]}
    c3i_ok = all(np_[l]["max_minus_min_ci"][0] > 0.05 for l in ("en", "sl"))
    c3ii = {k: res["holm"][f"C3-ii {k.split('_')[0]}"]["reject_0.05"] and c3ii_point(k) > 0
            for k in ("L1_exp11_f_ladder", "L2_exp9_c_grid")}
    falsified = (not c3i_ok) or (not any(c3ii.values()))
    res["verdict"] = {"per_ladder": verdict, "C3_i_nonflat_both_languages": c3i_ok, "C3_ii_positive_after_holm": c3ii,
                      "C3_iii_reject_after_holm": res["holm"]["C3-iii"]["reject_0.05"],
                      "C3_status": "FALSIFIED" if falsified else ("SUPPORTED" if all(c3ii.values()) else "PARTLY_SUPPORTED"),
                      "falsifier_text": ("The strict/broad gap range is judge-definition noise." if falsified else
                                         "The PARTIAL-share peak sits at a higher dose in Slovene in the ladder(s) marked True.")}
    res["identity_statement"] = FZ["c3_predictions"]["identity_caveat"]
    res["freeze_mtime"] = t_freeze
    C.jdump(res, C.RES / "curve_fits.json")
    pd.concat([t1.assign(ladder="L1"), t2.assign(ladder="L2")]).to_csv(C.RES / "partial_curves.csv", index=False)
    figure(res)
    for p in (C.RES / "curve_fits.json", C.RES / "partial_curves.csv", C.RES / "c3iii_out_of_panel_cells.csv"):
        assert os.path.getmtime(p) > t_freeze, f"mtime order violated for {p}"
    logger.info(f"verdict: {res['verdict']}")
    logger.info(f"holm: {res['holm']}")


if __name__ == "__main__":
    main()

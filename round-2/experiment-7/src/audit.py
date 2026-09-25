#!/usr/bin/env python3
"""T5 audit: independent recomputation (plain numpy, no sklearn learners, no shared helper code) from the saved
parquet files of (1) the edit-level traits, (2) the Spearman-Brown ceilings, (3) the fitted-set count and the
collapse count, (4) the Gaps through a different learner (numpy OLS on truncated-power cubic splines, ridge 1e-3),
(5) the judged-rate inputs of the validity gate, (6) the API cost total; plus placebos:
language-label shuffle -> Gap ~ 0 (CI covers 0); permuted edit order -> R2 ~ 0.  -> results/audit.json"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

WS = Path(__file__).resolve().parent
RES = WS / "results"
EPS = 1e-4  # same K floor as analysis.py


def spline_basis(X: np.ndarray, knots_q=(0.25, 0.5, 0.75)) -> np.ndarray:
    """Additive spline basis WITHOUT intercept: per feature z, z^2 and linear hinges (z - q)_+ at the quartiles,
    every column standardized (so a single ridge penalty is scale-free)."""
    cols = []
    for j in range(X.shape[1]):
        x = X[:, j]
        z = (x - x.mean()) / (x.std() or 1.0)
        cols += [z, z ** 2]
        for q in np.quantile(z, knots_q):
            cols.append(np.clip(z - q, 0, None))
    B = np.c_[tuple(cols)]
    return (B - B.mean(0)) / (B.std(0) + 1e-12)


def cv_r2_numpy(X, y, seed=20260926, k=5, lam=None):
    """5-fold CV R2 of closed-form ridge on the spline basis; intercept = training-fold mean (unpenalized).
    lam (default) = 0.05 * n_train, i.e. a fixed mild shrinkage relative to the sample size."""
    rng = np.random.default_rng(seed)
    fold = rng.permutation(len(y)) % k
    pred = np.zeros(len(y))
    B = spline_basis(X)
    for f in range(k):
        tr, te = fold != f, fold == f
        A, yt = B[tr], y[tr]
        mu_b, mu_y = A.mean(0), yt.mean()
        Ac = A - mu_b
        L = (0.05 * tr.sum()) if lam is None else lam
        w = np.linalg.solve(Ac.T @ Ac + L * np.eye(A.shape[1]), Ac.T @ (yt - mu_y))
        pred[te] = mu_y + (B[te] - mu_b) @ w
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def sb(M, n=50, seed=0, log=False):
    rng = np.random.default_rng(seed)
    rs = []
    for _ in range(n):
        p = rng.permutation(M.shape[1])
        a, b = M[:, p[: M.shape[1] // 2]].mean(1), M[:, p[M.shape[1] // 2:]].mean(1)
        if log:
            a, b = np.log(np.maximum(a, EPS)), np.log(np.maximum(b, EPS))
        rs.append(np.corrcoef(a, b)[0, 1] if a.std() > 0 and b.std() > 0 else 0.0)
    r = float(np.mean(rs))
    return 2 * r / (1 + r)


def main() -> None:
    A = json.loads((RES / "analysis.json").read_text())
    it = pd.read_parquet(RES / "panel" / "item_traits.parquet")
    cov = pd.read_parquet(RES / "panel" / "edit_covariates.parquet")
    R_star = A["R_star"]
    tmap = {"R_seq": ("R_seq", "harmful"), "R1": ("R1", "harmful"), "Rb": ("R_seq", "harmless"), "K": ("K", None), "N": ("N", None), "M": ("M", None)}
    edits = cov["edit_id"].tolist()
    fit = cov[(cov.set.isin(["E0", "E1"])) & (~cov.collapsed)]["edit_id"].tolist()
    out = {"n_fitted_recomputed": len(fit), "n_fitted_analysis": A["n_fitted_noncollapsed"],
           "fitted_match": len(fit) == A["n_fitted_noncollapsed"], "collapsed_recomputed": int(cov.collapsed.sum())}

    def mat(t, lang, half):
        key, role = tmap[t]
        d = it[(it.trait_key == key) & (it.lang == lang) & (it.half == half)]
        if role:
            d = d[d.role == role]
        pv = d.pivot_table(index="edit_id", columns="sid", values="delta")
        pv = pv.dropna(axis=1)  # items present in every edit (trimmed common set)
        return pv.loc[fit]

    def lvl(t, lang, half):
        M = mat(t, lang, half).values
        return np.log(np.maximum(M.mean(1), EPS)) if t == "K" else M.mean(1)
    ceil_chk, y_chk, gaps = {}, {}, {}
    for t in [R_star, "Rb", "K", "N", "M"]:
        for lg in ("en", "sl"):
            for h in ("A", "B"):
                c = sb(mat(t, lg, h).values, log=(t == "K"))
                ref = A["reliability_gate"]["values"][f"{t}_{lg}_{h}"]
                ceil_chk[f"{t}_{lg}_{h}"] = {"audit": c, "analysis": ref, "absdiff": abs(c - ref)}
        yb = lvl(t, "sl", "B")
        y_chk[t] = {"sl_B_mean_audit": float(yb.mean()), "sl_B_mean_analysis": A["descriptive_trait_spread"][t]["sl"]["mean"],
                    "absdiff": abs(float(yb.mean()) - A["descriptive_trait_spread"][t]["sl"]["mean"])}
    X = np.c_[tuple(lvl(t, "en", "A") for t in [R_star, "Rb", "K", "N", "M"])]
    rng = np.random.default_rng(1)
    for t in [R_star, "Rb", "K", "N", "M"]:
        yen, ysl = lvl(t, "en", "B"), lvl(t, "sl", "B")
        ce, cs = sb(mat(t, "en", "B").values, log=(t == "K")), sb(mat(t, "sl", "B").values, log=(t == "K"))
        r_en, r_sl = cv_r2_numpy(X, yen), cv_r2_numpy(X, ysl)
        g = r_en / ce - r_sl / cs
        # placebo 1: language-label shuffle (EN/SL swapped per edit at random) -> Gap ~ 0
        # both "languages" become per-edit random mixtures of the EN and SL targets (z-scored first so the swap is not a
        # scale artefact); the placebo Gap must centre on 0
        zen, zsl = (yen - yen.mean()) / (yen.std() + 1e-12), (ysl - ysl.mean()) / (ysl.std() + 1e-12)
        pl = []
        for b in range(200):
            sw = rng.random(len(yen)) < 0.5
            a_ = np.where(sw, zsl, zen)
            b_ = np.where(sw, zen, zsl)
            pl.append(cv_r2_numpy(X, a_, seed=b) - cv_r2_numpy(X, b_, seed=b))
        # placebo 2: permuted edit order -> R2 ~ 0 (<= 0 expected)
        perm = [cv_r2_numpy(X, rng.permutation(ysl), seed=b) for b in range(50)]
        gaps[t] = {"audit_numpy_spline": {"R2_EN": r_en, "R2_SL": r_sl, "Gap_AtoB": g, "Gap_raw_AtoB": r_en - r_sl},
                   "analysis_hgb_AtoB": A["gap_point"][t]["A->B"]["Gap"], "analysis_spline_sensitivity": A["gap_point"][t].get("spline_sensitivity"),
                   "analysis_hgb_R2_EN_AtoB": A["gap_point"][t]["A->B"]["R2_EN"], "analysis_hgb_R2_SL_AtoB": A["gap_point"][t]["A->B"]["R2_SL"],
                   "diff_vs_analysis_hgb": g - A["gap_point"][t]["A->B"]["Gap"],
                   "same_sign_or_both_small_vs_hgb": bool(np.sign(g) == np.sign(A["gap_point"][t]["A->B"]["Gap"]) or
                                                          (abs(g) < 0.05 and abs(A["gap_point"][t]["A->B"]["Gap"]) < 0.05)),
                   "placebo_lang_shuffle_gap_raw_ci95": [float(np.percentile(pl, 2.5)), float(np.percentile(pl, 97.5))],
                   "placebo_lang_shuffle_covers_0": bool(np.percentile(pl, 2.5) <= 0 <= np.percentile(pl, 97.5)),
                   "placebo_perm_R2_mean": float(np.mean(perm)), "placebo_perm_R2_le_0.05": bool(np.mean(perm) <= 0.05)}
    out["ceilings"] = ceil_chk
    out["ceilings_max_absdiff"] = max(v["absdiff"] for v in ceil_chk.values())
    out["edit_level_trait_check"] = y_chk
    out["edit_level_max_absdiff"] = max(v["absdiff"] for v in y_chk.values())
    out["gaps"] = gaps
    # validity-gate inputs
    jp = RES / "validity" / ("judged_api.json" if A.get("validity_gate", {}).get("judge", "").startswith("api") else "judged.json")
    if jp.exists() and "edits" in A.get("validity_gate", {}):
        J = json.loads(jp.read_text())
        vv = {}
        for eid, gl in J.items():
            for lg in ("en", "sl"):
                g = [x for x in gl if x["lang"] == lg and x["role"] == "harmful"]
                r = float(np.mean([x["label"] == "refused" for x in g]))
                ref = A["validity_gate"]["edits"][eid][f"{lg}_harmful"]["rate_refused"]
                vv[f"{eid}_{lg}"] = abs(r - ref)
        out["validity_rates_max_absdiff"] = max(vv.values()) if vv else None
    cl = WS / "logs" / "cost_log.jsonl"
    out["api_cost_total_usd"] = sum(json.loads(x)["cost"] for x in cl.read_text().splitlines() if x.strip()) if cl.exists() else 0.0
    out["deterministic_checks_pass"] = bool(out["fitted_match"] and out["ceilings_max_absdiff"] < 1e-6 and out["edit_level_max_absdiff"] < 1e-6
                                            and (out.get("validity_rates_max_absdiff") in (None,) or out["validity_rates_max_absdiff"] < 1e-9))
    out["placebos_pass"] = bool(all(g["placebo_lang_shuffle_covers_0"] and g["placebo_perm_R2_le_0.05"] for g in gaps.values()))
    (RES / "audit.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ["n_fitted_recomputed", "fitted_match", "ceilings_max_absdiff", "edit_level_max_absdiff",
                                         "deterministic_checks_pass", "placebos_pass", "api_cost_total_usd"]}, indent=1))
    for t, g in gaps.items():
        print(t, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items() if k != "audit_numpy_spline"}, g["audit_numpy_spline"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Core estimators (shared by analysis.py, the T0 synthetic tests and audit.py's comparison):
cross-validated R2 with the frozen learner, Spearman-Brown ceilings, the ceiling-normalised Gap, B, SIMEX."""
from __future__ import annotations

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler

FOLD_SEED = 20260926
HGB = dict(max_iter=150, learning_rate=0.05, max_leaf_nodes=8, min_samples_leaf=8, l2_regularization=1.0, random_state=0)


def make_learner(kind: str = "hgb"):
    if kind == "hgb":
        return HistGradientBoostingRegressor(**HGB)
    if kind == "spline":
        return make_pipeline(StandardScaler(), SplineTransformer(n_knots=5, degree=3), RidgeCV(alphas=np.logspace(-3, 3, 13)))
    if kind == "ridge":
        return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 13)))
    raise ValueError(kind)


def folds(n: int, groups: np.ndarray | None = None, seed: int = FOLD_SEED, k: int = 5):
    if groups is None:
        return list(KFold(k, shuffle=True, random_state=seed).split(np.arange(n)))
    # shuffled group k-fold (bootstrap duplicates of one edit stay in one fold)
    ug = np.unique(groups)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(ug))
    gfold = {g: i % k for i, g in zip(range(len(ug)), ug[perm])}
    fa = np.array([gfold[g] for g in groups])
    return [(np.where(fa != f)[0], np.where(fa == f)[0]) for f in range(k)]


def oof_pred(X: np.ndarray, y: np.ndarray, kind: str = "hgb", groups=None, seed: int = FOLD_SEED) -> np.ndarray:
    pred = np.zeros(len(y))
    for tr, te in folds(len(y), groups, seed):
        m = make_learner(kind)
        m.fit(X[tr], y[tr])
        pred[te] = m.predict(X[te])
    return pred


def r2(y: np.ndarray, p: np.ndarray) -> float:
    sst = float(((y - y.mean()) ** 2).sum())
    return float(1 - ((y - p) ** 2).sum() / sst) if sst > 0 else float("nan")


def r2_cv(X, y, kind="hgb", groups=None, seed=FOLD_SEED) -> float:
    try:
        return r2(y, oof_pred(X, y, kind, groups, seed))
    except ValueError:  # degenerate fold (tiny n / duplicated bootstrap rows): report NaN, never abort a resample
        return float("nan")


def spearman_brown(Y_items: np.ndarray, n_splits: int = 50, seed: int = 0, agg=np.mean) -> float:
    """Y_items: (edits, items) item-level values of ONE trait x lang x half. Random item halves; Pearson r across edits
    of the half means; Spearman-Brown step-up; averaged over splits."""
    rng = np.random.default_rng(seed)
    n_items = Y_items.shape[1]
    if n_items < 4:
        return float("nan")
    rs = []
    for _ in range(n_splits):
        p = rng.permutation(n_items)
        a, b = agg(Y_items[:, p[: n_items // 2]], axis=1), agg(Y_items[:, p[n_items // 2:]], axis=1)
        if a.std() == 0 or b.std() == 0:
            rs.append(0.0)
            continue
        rs.append(float(np.corrcoef(a, b)[0, 1]))
    r = float(np.mean(rs))
    return float(2 * r / (1 + r)) if r > -1 else float("nan")


def gap_from(X_A, yEN_B, ySL_B, ceil_EN, ceil_SL, kind="hgb", groups=None) -> dict:
    r_en = r2_cv(X_A, yEN_B, kind, groups)
    r_sl = r2_cv(X_A, ySL_B, kind, groups)
    rs_en = r_en / ceil_EN if ceil_EN and ceil_EN > 0 else float("nan")
    rs_sl = r_sl / ceil_SL if ceil_SL and ceil_SL > 0 else float("nan")
    return {"R2_EN": r_en, "R2_SL": r_sl, "R2s_EN": rs_en, "R2s_SL": rs_sl, "Gap": rs_en - rs_sl, "Gap_raw": r_en - r_sl,
            "ceil_EN": ceil_EN, "ceil_SL": ceil_SL, "unstable": bool((ceil_EN or 0) < 0.2 or (ceil_SL or 0) < 0.2)}


def b_stat(X_A, P, yEN_B, ySL_B, kind="hgb", groups=None) -> dict:
    XP = np.c_[X_A, P]
    d_sl = r2_cv(XP, ySL_B, kind, groups) - r2_cv(X_A, ySL_B, kind, groups)
    d_en = r2_cv(XP, yEN_B, kind, groups) - r2_cv(X_A, yEN_B, kind, groups)
    return {"dR2_params_SL": d_sl, "dR2_params_EN": d_en, "B": d_sl - d_en}


def simex_r2(X, y, se2: np.ndarray, lambdas=(0.5, 1.0, 1.5, 2.0), reps: int = 30, kind="hgb", seed: int = 0) -> dict:
    """SIMEX on predictor noise: X + N(0, lambda * se2) (se2: per-edit x per-column item-level SE^2)."""
    rng = np.random.default_rng(seed)
    lam = [0.0] + list(lambdas)
    vals = [r2_cv(X, y, kind)]
    for L in lambdas:
        v = []
        for _ in range(reps):
            Xn = X + rng.normal(size=X.shape) * np.sqrt(L * se2)
            v.append(r2_cv(Xn, y, kind))
        vals.append(float(np.mean(v)))
    coef = np.polyfit(lam, vals, 2)
    return {"lambdas": lam, "r2": vals, "r2_simex": float(np.polyval(coef, -1.0))}

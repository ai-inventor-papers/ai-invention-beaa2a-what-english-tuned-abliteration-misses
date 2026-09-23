#!/usr/bin/env python3
"""A3 sibling screen over the 60 identical TPE startup edits (trials 0-59), CPU only.

Reads both Optuna journals, checks the startup parameter draws are identical, and measures how well
the two siblings agree on English refusal count and log KL, with a strength control (Heretic kernel
mass) and a params-only predictive baseline (range-restriction guard).

  python a3_screen.py            -> real analysis, writes results/a3_screen.json + trial tables
  python a3_screen.py --synthetic -> T4 check of the range-restriction guard on synthetic data
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats
from scipy.spatial import procrustes
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

WS = Path(__file__).resolve().parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "a3_screen.log", rotation="30 MB", level="DEBUG")

JOURNALS = {
    "gams": WS / "checkpoints" / "gams" / "cjvt--GaMS3-12B-Instruct.jsonl",
    "gemma": WS / "checkpoints" / "gemma" / "google--gemma-3-12b-it.jsonl",
}
N_LAYERS = 48
COMPONENTS = ["attn.o_proj", "mlp.down_proj"]
RNG = np.random.default_rng(0)


# ------------------------------------------------------------------ loading
def load_trials(tag: str) -> pd.DataFrame:
    import optuna
    from optuna.trial import TrialState

    st = optuna.load_study(study_name="heretic", storage=optuna.storages.JournalStorage(
        optuna.storages.journal.JournalFileBackend(str(JOURNALS[tag]))))
    rows = []
    for t in st.trials:
        rec = {"number": t.number, "state": t.state.name,
               "datetime_start": str(t.datetime_start), "datetime_complete": str(t.datetime_complete),
               "duration_s": t.duration.total_seconds() if t.duration else None}
        if t.state == TrialState.COMPLETE:
            rec["refusals"] = int(round(t.values[0] * 100))
            rec["kl"] = float(t.values[1])
        rec.update({f"p.{k}": v for k, v in t.params.items()})
        rec["direction_index_eff"] = t.user_attrs.get("direction_index")
        rec["abl_params"] = json.dumps(t.user_attrs.get("parameters"))
        rows.append(rec)
    return pd.DataFrame(rows)


def kernel(max_w: float, pos: float, min_w: float, dist: float, n_layers: int = N_LAYERS) -> np.ndarray:
    """Exact per-layer weight profile of heretic.model.Model.abliterate (3521f864)."""
    w = np.zeros(n_layers)
    for l in range(n_layers):
        d = abs(l - pos)
        if d > dist:
            continue
        w[l] = max_w + (d / dist) * (min_w - max_w)
    return w


def features(df: pd.DataFrame) -> pd.DataFrame:
    f = pd.DataFrame(index=df.index)
    for c in COMPONENTS:
        ks = []
        for s in df["abl_params"]:
            p = json.loads(s)[c]
            ks.append(kernel(p["max_weight"], p["max_weight_position"], p["min_weight"], p["min_weight_distance"]))
        ks = np.array(ks)
        f[f"S_{c}"] = ks.sum(1)
        f[f"peak_{c}"] = [json.loads(s)[c]["max_weight_position"] for s in df["abl_params"]]
        f[f"maxw_{c}"] = [json.loads(s)[c]["max_weight"] for s in df["abl_params"]]
        f[f"minw_{c}"] = [json.loads(s)[c]["min_weight"] for s in df["abl_params"]]
        f[f"dist_{c}"] = [json.loads(s)[c]["min_weight_distance"] for s in df["abl_params"]]
    f["scope_global"] = (df["p.direction_scope"] == "global").astype(float)
    f["direction_index"] = df["p.direction_index"].astype(float)
    return f


# ------------------------------------------------------------------ statistics
def spearman_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 2000) -> dict:
    rho = stats.spearmanr(a, b).statistic
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(a), len(a))
        if np.ptp(a[i]) == 0 or np.ptp(b[i]) == 0:
            continue
        bs.append(stats.spearmanr(a[i], b[i]).statistic)
    return {"rho": float(rho), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))],
            "n": int(len(a))}


def rank_inv_normal(x: np.ndarray) -> np.ndarray:
    r = stats.rankdata(x)
    return stats.norm.ppf((r - 0.5) / len(x))


def rv_coefficient(X: np.ndarray, Y: np.ndarray, n_perm: int = 2000) -> dict:
    def rv(X, Y):
        Sxy = X.T @ Y
        Sxx = X.T @ X
        Syy = Y.T @ Y
        return np.trace(Sxy @ Sxy.T) / math.sqrt(np.trace(Sxx @ Sxx) * np.trace(Syy @ Syy))
    X = X - X.mean(0)
    Y = Y - Y.mean(0)
    obs = rv(X, Y)
    rng = np.random.default_rng(0)
    null = [rv(X, Y[rng.permutation(len(Y))]) for _ in range(n_perm)]
    return {"rv": float(obs), "perm_p": float((1 + sum(n >= obs for n in null)) / (n_perm + 1))}


def spline_basis(S: np.ndarray) -> np.ndarray:
    st = SplineTransformer(degree=3, n_knots=5, include_bias=False)
    return st.fit_transform(S)


def partial_spearman(yA: np.ndarray, yB: np.ndarray, S: np.ndarray, n_boot: int = 2000) -> dict:
    """Spearman of rank residuals after cubic-spline OLS on the strength covariates S (n x k)."""
    def resid(y, B):
        X = np.column_stack([np.ones(len(y)), B])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        return y - X @ beta

    def one(idx):
        B = spline_basis(S[idx])
        ra, rb = stats.rankdata(yA[idx]), stats.rankdata(yB[idx])
        return stats.pearsonr(resid(ra, B), resid(rb, B)).statistic

    full = one(np.arange(len(yA)))
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yA), len(yA))
        try:
            bs.append(one(i))
        except (ValueError, np.linalg.LinAlgError):
            continue
    return {"partial_rho": float(full), "ci95": [float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))]}


def make_learner(kind: str, n_spline_cols: int):
    if kind == "ridge":
        return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-3, 3, 25)))
    return GradientBoostingRegressor(max_depth=2, n_estimators=200, learning_rate=0.05, random_state=0)


def oof_predictions(X: np.ndarray, y: np.ndarray, kind: str, n_rep: int = 20, k: int = 10) -> np.ndarray:
    """Out-of-fold predictions, averaged over n_rep repeats of k-fold CV -> (n_rep, n)."""
    P = np.zeros((n_rep, len(y)))
    for r in range(n_rep):
        kf = KFold(n_splits=k, shuffle=True, random_state=r)
        for tr, te in kf.split(X):
            m = make_learner(kind, 0)
            m.fit(X[tr], y[tr])
            P[r, te] = m.predict(X[te])
    return P


def r2_from(P: np.ndarray, y: np.ndarray, idx: np.ndarray | None = None) -> float:
    if idx is None:
        idx = np.arange(len(y))
    yt = y[idx]
    sse = ((P[:, idx] - yt) ** 2).mean(0).sum()
    sst = ((yt - yt.mean()) ** 2).sum()
    return float(1 - sse / sst)


def predictive_decomposition(Xp: np.ndarray, yA: np.ndarray, yB: np.ndarray, kind: str, n_boot: int = 2000) -> dict:
    Xsib = yA.reshape(-1, 1)
    P_params = oof_predictions(Xp, yB, kind)
    P_sib = oof_predictions(Xsib, yB, kind)
    P_both = oof_predictions(np.column_stack([Xp, yA]), yB, kind)
    out = {"R2_params": r2_from(P_params, yB), "R2_sibling": r2_from(P_sib, yB), "R2_params_plus_sibling": r2_from(P_both, yB)}
    out["dR2_sibling"] = out["R2_params_plus_sibling"] - out["R2_params"]
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(yB), len(yB))
        if np.ptp(yB[i]) == 0:
            continue
        bs.append(r2_from(P_both, yB, i) - r2_from(P_params, yB, i))
    out["dR2_ci95"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return out


def param_matrix(F: pd.DataFrame) -> np.ndarray:
    base = F.values.astype(float)
    Sb = spline_basis(F[["S_attn.o_proj", "S_mlp.down_proj"]].values)
    return np.column_stack([base, Sb])


def reading(res: dict) -> str:
    r1, r2 = res["refusal"]["spearman"], res["logkl"]["spearman"]
    d1 = res["refusal"]["pred_A_to_B_ridge"]
    d2 = res["logkl"]["pred_A_to_B_ridge"]
    if r1["rho"] < 0.7 or r2["rho"] < 0.7:
        return "divergent"
    hi = r1["rho"] >= 0.9 and r2["rho"] >= 0.9 and r1["ci95"][0] >= 0.8 and r2["ci95"][0] >= 0.8
    if hi and d1["dR2_sibling"] > 0.05 and d1["dR2_ci95"][0] > 0 and d2["dR2_sibling"] > 0.05 and d2["dR2_ci95"][0] > 0:
        return "shared surface"
    if r1["rho"] >= 0.9 and r2["rho"] >= 0.9 and (d1["dR2_ci95"][0] <= 0 or d2["dR2_ci95"][0] <= 0):
        return "shared via strength only"
    return "intermediate"


def analyse_pair(F: pd.DataFrame, outcomes: dict[str, tuple[np.ndarray, np.ndarray]], n_boot: int = 2000) -> dict:
    Xp = param_matrix(F)
    S = F[["S_attn.o_proj", "S_mlp.down_proj"]].values
    res = {}
    for name, (yA, yB) in outcomes.items():
        r = {"spearman": spearman_ci(yA, yB, n_boot),
             "pearson_rank_inverse_normal": float(stats.pearsonr(rank_inv_normal(yA), rank_inv_normal(yB)).statistic),
             "partial_spearman_given_kernel_mass": partial_spearman(yA, yB, S, n_boot)}
        r["pred_A_to_B_ridge"] = predictive_decomposition(Xp, yA, yB, "ridge", n_boot)
        r["pred_B_to_A_ridge"] = predictive_decomposition(Xp, yB, yA, "ridge", n_boot)
        r["pred_A_to_B_gbm"] = predictive_decomposition(Xp, yA, yB, "gbm", 500)
        r["pred_B_to_A_gbm"] = predictive_decomposition(Xp, yB, yA, "gbm", 500)
        res[name] = r
    return res


# ------------------------------------------------------------------ synthetic T4
def synthetic() -> dict:
    """Range-restriction guard check: strength-only generator vs shared-residual generator."""
    rng = np.random.default_rng(1)
    n = 60
    rows = []
    for _ in range(n):
        p = {}
        for c in COMPONENTS:
            lo = -0.25 if c == "mlp.down_proj" else 0.8
            mw = max(0.0, rng.uniform(lo, 1.5))
            p[c] = {"max_weight": mw, "max_weight_position": rng.uniform(0.6 * 47, 47),
                    "min_weight": rng.uniform(0, 1) * mw, "min_weight_distance": rng.uniform(1, 0.6 * 47)}
        rows.append({"abl_params": json.dumps(p), "p.direction_scope": rng.choice(["global", "per layer"]),
                     "p.direction_index": rng.uniform(0.4 * 47, 0.9 * 47)})
    df = pd.DataFrame(rows)
    F = features(df)
    S = F["S_attn.o_proj"].values + 0.5 * F["S_mlp.down_proj"].values
    f = np.tanh((S - S.mean()) / S.std())
    out = {}
    # strength-only: y_A, y_B = f(S) + independent noise
    yA = f + 0.25 * rng.normal(size=n)
    yB = f + 0.25 * rng.normal(size=n)
    out["strength_only"] = analyse_pair(F, {"y": (yA, yB)}, n_boot=300)["y"]
    # shared residual: y = f(S) + shared u + small independent noise
    u = 0.5 * rng.normal(size=n)
    yA2 = f + u + 0.1 * rng.normal(size=n)
    yB2 = f + u + 0.1 * rng.normal(size=n)
    out["shared_residual"] = analyse_pair(F, {"y": (yA2, yB2)}, n_boot=300)["y"]
    summ = {k: {"rho": v["spearman"]["rho"], "dR2_ridge": v["pred_A_to_B_ridge"]["dR2_sibling"],
                "dR2_ci": v["pred_A_to_B_ridge"]["dR2_ci95"],
                "partial_rho": v["partial_spearman_given_kernel_mass"]["partial_rho"]} for k, v in out.items()}
    ok = summ["strength_only"]["dR2_ci"][0] <= 0.0 + 1e-9 and summ["shared_residual"]["dR2_ci"][0] > 0
    summ["guard_discriminates"] = bool(ok)
    logger.info(json.dumps(summ, indent=1))
    return summ


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--n-startup", type=int, default=60)
    args = ap.parse_args()
    out_dir = WS / "results"
    out_dir.mkdir(exist_ok=True)
    if args.synthetic:
        (out_dir / "a3_synthetic_T4.json").write_text(json.dumps(synthetic(), indent=1))
        return

    dfs = {tag: load_trials(tag) for tag in JOURNALS}
    for tag, df in dfs.items():
        df.to_csv(out_dir / f"trials_{tag}.csv", index=False)
        logger.info(f"{tag}: {len(df)} trials, {int((df.state == 'COMPLETE').sum())} complete")
    A, B = dfs["gams"], dfs["gemma"]
    n = min(args.n_startup, len(A), len(B))
    pcols = sorted(c for c in A.columns if c.startswith("p."))
    ident = {"n_compared": n, "all_identical": True, "first_mismatch": None}
    common = []
    for i in range(n):
        a, b = A.iloc[i], B.iloc[i]
        same = all((a[c] == b[c]) for c in pcols) and a["abl_params"] == b["abl_params"]
        if not same and ident["first_mismatch"] is None:
            ident["all_identical"] = False
            ident["first_mismatch"] = {"trial": i, "gams": {c: a[c] for c in pcols}, "gemma": {c: b[c] for c in pcols}}
        if same and a["state"] == "COMPLETE" and b["state"] == "COMPLETE":
            common.append(i)
    ident["n_identical_complete"] = len(common)
    logger.info(f"identity: {ident['all_identical']} ; paired complete startup edits: {len(common)}")
    Ac, Bc = A.iloc[common].reset_index(drop=True), B.iloc[common].reset_index(drop=True)
    F = features(Ac)
    yA_ref, yB_ref = Ac["refusals"].values.astype(float), Bc["refusals"].values.astype(float)
    yA_kl, yB_kl = np.log(Ac["kl"].values + 1e-6), np.log(Bc["kl"].values + 1e-6)
    res = analyse_pair(F, {"refusal": (yA_ref, yB_ref), "logkl": (yA_kl, yB_kl)})
    ZA = np.column_stack([stats.zscore(yA_ref), stats.zscore(yA_kl)])
    ZB = np.column_stack([stats.zscore(yB_ref), stats.zscore(yB_kl)])
    _, _, disp = procrustes(ZA, ZB)
    active = (yA_ref <= 50) & (yB_ref <= 50)
    act = {}
    if active.sum() >= 8:
        act = {"n": int(active.sum()), "refusal": spearman_ci(yA_ref[active], yB_ref[active]),
               "logkl": spearman_ci(yA_kl[active], yB_kl[active])}
    else:
        act = {"n": int(active.sum()), "note": "too few edits with both refusals <= 50"}
    out = {"identity_check": ident, "paired_trials": common,
           "descriptives": {t: {"refusals_median": float(np.median(y)), "refusals_min": float(y.min()), "refusals_max": float(y.max())}
                            for t, y in [("gams", yA_ref), ("gemma", yB_ref)]},
           "results": res,
           "procrustes_2d": {"disparity": float(disp), "one_minus_disparity": float(1 - disp)},
           "rv_2d": rv_coefficient(ZA, ZB),
           "active_stratum_both_refusals_le_50": act}
    out["reading"] = reading(res)
    out["protocol"] = json.loads((WS / "protocol_a3.json").read_text())
    (out_dir / "a3_screen.json").write_text(json.dumps(out, indent=1, default=float))
    logger.info(f"A3 reading: {out['reading']}; rho_ref={res['refusal']['spearman']} rho_kl={res['logkl']['spearman']}")


if __name__ == "__main__":
    main()

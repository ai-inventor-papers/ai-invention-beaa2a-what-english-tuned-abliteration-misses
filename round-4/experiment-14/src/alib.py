"""Analysis library: cell loading, 4-way rates, item-cluster bootstrap, permutation nulls, nested R2 with a
leave-one-cell-out companion, exact McNemar and Holm. Shared by screen.py, analysis.py and the figures."""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import common as C
import labels as LB
from common import jload
from judge_local import JUDGE_LOCAL, load_cache

BANDS = [(1, 12), (13, 24), (25, 36), (37, 48)]
RNG = np.random.default_rng(C.SEED)


# ------------------------------------------------------------------------------------------------ loading
def judge_cache() -> dict:
    cache = load_cache(C.RES / "judge_local.jsonl")
    for p in (C.E10 / "results/judge_local.jsonl", C.E8 / "results/judge2_local.jsonl"):
        if p.exists():
            for k, v in load_cache(p).items():
                cache.setdefault(k, v)
    return cache


def load_cells(root: Path | None = None, cache: dict | None = None) -> dict:
    """{cell: {"meta": ..., "rows": [labelled generations], "tf": ...}} for every cell with generations."""
    root = root or C.CELLS
    cache = judge_cache() if cache is None else cache
    out = {}
    for p in sorted(root.glob("*/gens.json")):
        cell = p.parent.name
        rows = LB.attach_labels(jload(p), cache, JUDGE_LOCAL)
        meta = jload(p.parent / "meta.json") if (p.parent / "meta.json").exists() else {}
        tf = jload(p.parent / "tf.json") if (p.parent / "tf.json").exists() else {}
        out[cell] = {"meta": meta, "rows": rows, "tf": tf}
    return out


def overlap(e: np.ndarray, g: list[float]) -> float:
    """The frozen instrument: O = sum_h e(h) g(h) / ||g||_2 (h = hidden index; layer l is edited with row l+1)."""
    g = np.asarray(g, dtype=float)
    n = float(np.linalg.norm(g))
    return 0.0 if n == 0 else float(np.dot(np.asarray(e, dtype=float)[: len(g)], g) / n)


# ------------------------------------------------------------------------------------------------ rates
def subset(rows: list[dict], lang: str, split: str) -> list[dict]:
    return [r for r in rows if r["lang"] == lang and r["split"] == split and r["cls4"] is not None]


def rates(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0, "strict": float("nan"), "broad": float("nan"), "partial": float("nan"),
                "complied": float("nan"), "invalid": float("nan"), "lid_ok": float("nan"), "rep4": float("nan")}
    f = lambda c: float(np.mean([r["cls4"] == c for r in rows]))
    return {"n": n, "strict": f("REFUSED"), "broad": f("REFUSED") + f("PARTIAL"), "partial": f("PARTIAL"),
            "complied": f("COMPLIED"), "invalid": f("INVALID"),
            "lid_ok": float(np.mean([not r["wrong_lang"] for r in rows])),
            "rep4": float(np.mean([r["rep4"] for r in rows]))}


def item_map(rows: list[dict], cls: str = "REFUSED") -> dict:
    """semantic item -> indicator of the class (for paired / clustered resampling)."""
    return {r["semantic_id"]: float(r["cls4"] == cls) for r in rows}


def tf_mean(tf: dict, key: str) -> float:
    v = tf.get(key)
    return float(np.mean(list(v.values()))) if v else float("nan")


# ------------------------------------------------------------------------------------------------ resampling
def boot_items(items: list[str], n: int = 2000, rng: np.random.Generator | None = None) -> list[list[str]]:
    rng = rng or np.random.default_rng(C.SEED)
    idx = rng.integers(0, len(items), size=(n, len(items)))
    return [[items[j] for j in row] for row in idx]


def ci(v: list[float], lo: float = 2.5, hi: float = 97.5) -> tuple[float, float]:
    v = [x for x in v if x == x]
    if not v:
        return (float("nan"), float("nan"))
    return (float(np.percentile(v, lo)), float(np.percentile(v, hi)))


def rho_ci(maps: dict, pred: dict, items: list[str], n_boot: int = 1000) -> dict:
    """Spearman(pred[cell], rate[cell]) over cells, with an item-cluster bootstrap CI and a permutation null."""
    cells = [c for c in maps if c in pred and pred[c] == pred[c]]
    x = np.array([pred[c] for c in cells])
    y = np.array([float(np.mean([maps[c][i] for i in items if i in maps[c]])) for c in cells])
    r = spearmanr(x, y)
    out = {"n_cells": len(cells), "rho": float(r.statistic), "p_asym": float(r.pvalue)}
    draws = []
    for bs in boot_items(items, n_boot):
        yb = np.array([float(np.mean([maps[c][i] for i in bs if i in maps[c]])) for c in cells])
        draws.append(spearmanr(x, yb).statistic)
    out["ci"] = ci(draws)
    perm = [spearmanr(RNG.permutation(x), y).statistic for _ in range(2000)]
    out["perm_p"] = float(np.mean([abs(p) >= abs(out["rho"]) for p in perm]))
    out["perm_null_sd"] = float(np.std(perm))
    return out


def rho_diff_ci(maps: dict, p1: dict, p2: dict, items: list[str], n_boot: int = 1000, use_abs: bool = True) -> dict:
    """Paired item-cluster bootstrap CI on |rho(pred1)| - |rho(pred2)| over the same cells (use_abs=False keeps signs).
    Absolute values are the fair comparison here: the instrument predicts refusal REMOVAL, so its expected sign is
    negative, while a competitor such as depth span has no pre-declared direction."""
    cells = [c for c in maps if c in p1 and c in p2 and p1[c] == p1[c] and p2[c] == p2[c]]
    x1 = np.array([p1[c] for c in cells])
    x2 = np.array([p2[c] for c in cells])
    y = np.array([float(np.mean([maps[c][i] for i in items if i in maps[c]])) for c in cells])
    f = (lambda v: abs(v)) if use_abs else (lambda v: v)
    d0 = f(spearmanr(x1, y).statistic) - f(spearmanr(x2, y).statistic)
    draws = []
    for bs in boot_items(items, n_boot):
        yb = np.array([float(np.mean([maps[c][i] for i in bs if i in maps[c]])) for c in cells])
        draws.append(f(spearmanr(x1, yb).statistic) - f(spearmanr(x2, yb).statistic))
    lo, hi = ci(draws)
    return {"n_cells": len(cells), "rho1": float(spearmanr(x1, y).statistic), "rho2": float(spearmanr(x2, y).statistic),
            "diff": float(d0), "ci": [lo, hi], "excludes_zero": bool(lo > 0 or hi < 0)}


def paired_rate_diff(mapA: dict, mapB: dict, n_boot: int = 2000) -> dict:
    """Paired item bootstrap on rate(A) - rate(B) over the shared semantic items, plus an exact McNemar test."""
    items = sorted(set(mapA) & set(mapB))
    a = np.array([mapA[i] for i in items])
    b = np.array([mapB[i] for i in items])
    d = float(a.mean() - b.mean())
    rng = np.random.default_rng(C.SEED)
    idx = rng.integers(0, len(items), size=(n_boot, len(items)))
    draws = [float(a[r].mean() - b[r].mean()) for r in idx]
    n01 = int(np.sum((a == 0) & (b == 1)))
    n10 = int(np.sum((a == 1) & (b == 0)))
    p = mcnemar_exact(n10, n01)
    lo, hi = ci(draws)
    return {"n_items": len(items), "rate_a": float(a.mean()), "rate_b": float(b.mean()), "diff": d, "ci": [lo, hi],
            "mcnemar_b": n10, "mcnemar_c": n01, "mcnemar_p": p}


def mcnemar_exact(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return float(min(1.0, 2 * p))


# ------------------------------------------------------------------------------------------------ regression
def ols_r2(X: np.ndarray, y: np.ndarray) -> float:
    X = np.column_stack([np.ones(len(y)), X]) if X.ndim == 2 else np.column_stack([np.ones(len(y)), X[:, None]])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    ss = float(np.sum((y - y.mean()) ** 2))
    return float(1 - np.sum(res ** 2) / ss) if ss > 0 else float("nan")


def loo_r2(X: np.ndarray, y: np.ndarray) -> float:
    """Out-of-sample R2 from leave-one-cell-out predictions (an in-sample dR2 that vanishes here is not a result)."""
    X = X if X.ndim == 2 else X[:, None]
    pred = np.zeros(len(y))
    for i in range(len(y)):
        m = np.ones(len(y), bool)
        m[i] = False
        Xi = np.column_stack([np.ones(m.sum()), X[m]])
        beta, *_ = np.linalg.lstsq(Xi, y[m], rcond=None)
        pred[i] = np.r_[1.0, X[i]] @ beta
    ss = float(np.sum((y - y.mean()) ** 2))
    return float(1 - np.sum((y - pred) ** 2) / ss) if ss > 0 else float("nan")


def nested(y: np.ndarray, base: dict, extra: dict) -> dict:
    """R2 of the base model and of base + each extra predictor, in sample and leave-one-cell-out."""
    Xb = np.column_stack([base[k] for k in base]) if base else np.zeros((len(y), 0))
    out = {"base_vars": list(base), "r2_base": ols_r2(Xb, y) if Xb.shape[1] else 0.0,
           "loo_base": loo_r2(Xb, y) if Xb.shape[1] else float("nan"), "add": {}}
    for k, v in extra.items():
        X = np.column_stack([Xb, v]) if Xb.shape[1] else np.asarray(v)[:, None]
        r2 = ols_r2(X, y)
        out["add"][k] = {"r2": r2, "dR2": r2 - out["r2_base"], "loo_r2": loo_r2(X, y),
                         "loo_dR2": loo_r2(X, y) - out["loo_base"]}
    return out


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, run = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[k] = run
    return out


def kappa(a: list, b: list) -> float:
    a, b = np.asarray(a), np.asarray(b)
    po = float(np.mean(a == b))
    cats = sorted(set(a) | set(b))
    pe = sum(float(np.mean(a == c)) * float(np.mean(b == c)) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def rogan_gladen(p_obs: float, se: float, sp: float) -> float:
    """Prevalence corrected for a judge with sensitivity se and specificity sp (clipped to [0, 1])."""
    if se + sp - 1 <= 0:
        return float("nan")
    return float(min(1.0, max(0.0, (p_obs + sp - 1) / (se + sp - 1))))

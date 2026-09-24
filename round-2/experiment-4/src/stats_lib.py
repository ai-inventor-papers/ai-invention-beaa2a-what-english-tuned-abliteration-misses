#!/usr/bin/env python3
"""Frozen statistics (protocol.yaml): cluster bootstrap (2000 draws, seed 20260923, percentile; BCa sensitivity),
exact McNemar, Holm, Cohen's kappa. Vectorised with NumPy."""
from __future__ import annotations

import numpy as np
from scipy import stats

N_BOOT = 2000
SEED = 20260923


def _cluster_index(clusters: list[str]) -> tuple[np.ndarray, int]:
    u = {c: i for i, c in enumerate(dict.fromkeys(clusters))}
    return np.array([u[c] for c in clusters]), len(u)


def boot_mean(x: np.ndarray, clusters: list[str] | None = None, n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float, float]:
    """Mean of x with a cluster-bootstrap percentile CI (clusters default = each element its own cluster)."""
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return (float("nan"),) * 3
    cid, k = _cluster_index(clusters if clusters is not None else [str(i) for i in range(len(x))])
    s = np.bincount(cid, weights=x, minlength=k)
    n = np.bincount(cid, minlength=k).astype(float)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, k, size=(n_boot, k))
    bs = s[draw].sum(1) / n[draw].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(x.mean()), float(lo), float(hi)


def boot_ratio_diff(num_fn, arrays: dict[str, np.ndarray], clusters: list[str], n_boot: int = N_BOOT, seed: int = SEED):
    """Generic cluster bootstrap for a statistic computed from per-element arrays; returns point, lo, hi, draws."""
    cid, k = _cluster_index(clusters)
    rng = np.random.default_rng(seed)
    point = num_fn({a: v for a, v in arrays.items()})
    idx_by_c = [np.where(cid == c)[0] for c in range(k)]
    draws = np.empty(n_boot)
    for b in range(n_boot):
        cs = rng.integers(0, k, size=k)
        ix = np.concatenate([idx_by_c[c] for c in cs])
        draws[b] = num_fn({a: v[ix] for a, v in arrays.items()})
    draws = draws[np.isfinite(draws)]
    lo, hi = (np.percentile(draws, [2.5, 97.5]) if len(draws) else (np.nan, np.nan))
    return float(point), float(lo), float(hi), draws


def bca_mean(d: np.ndarray, seed: int = SEED) -> tuple[float, float]:
    d = np.asarray(d, dtype=float)
    if len(d) < 3 or np.all(d == d[0]):
        return float(d.mean()) if len(d) else float("nan"), float(d.mean()) if len(d) else float("nan")
    r = stats.bootstrap((d,), np.mean, n_resamples=N_BOOT, method="BCa", random_state=np.random.default_rng(seed))
    return float(r.confidence_interval.low), float(r.confidence_interval.high)


def mcnemar_exact(a: np.ndarray, b: np.ndarray) -> dict:
    """a, b paired binaries (orig, edit). Exact two-sided binomial test on the discordant pairs."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n10 = int((a & ~b).sum())  # orig 1 -> edit 0
    n01 = int((~a & b).sum())
    n = n10 + n01
    p = 1.0 if n == 0 else float(stats.binomtest(min(n10, n01), n, 0.5).pvalue)
    return {"n10_orig1_edit0": n10, "n01_orig0_edit1": n01, "p": min(p, 1.0)}


def paired_effect(a: np.ndarray, b: np.ndarray, clusters: list[str], seed: int = SEED) -> dict:
    """Paired difference b - a (edit - orig) with cluster bootstrap CI + BCa sensitivity + exact McNemar."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    pt, lo, hi = boot_mean(d, clusters, seed=seed)
    ra, rb = a.mean(), b.mean()
    out = {"n": int(len(d)), "rate_orig": float(ra), "rate_edit": float(rb), "diff": pt, "ci": [lo, hi],
           "ci_bca": list(bca_mean(d, seed)), **mcnemar_exact(a, b)}
    if ra > 0:
        def rr(arr):
            return 1 - arr["b"].mean() / arr["a"].mean() if arr["a"].mean() > 0 else np.nan
        p, l, h, _ = boot_ratio_diff(rr, {"a": a, "b": b}, clusters, seed=seed)
        out["relative_reduction"] = p
        out["relative_reduction_ci"] = [l, h]
    return out


def holm(pvals: dict[str, float]) -> dict[str, float]:
    keys = list(pvals)
    p = np.array([pvals[k] for k in keys])
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (m - rank) * p[i])
        adj[i] = min(run, 1.0)
    return {k: float(v) for k, v in zip(keys, adj)}


def cohen_kappa(x: list, y: list) -> float:
    x, y = list(x), list(y)
    if not x:
        return float("nan")
    cats = sorted(set(x) | set(y))
    ix = {c: i for i, c in enumerate(cats)}
    M = np.zeros((len(cats), len(cats)))
    for a, b in zip(x, y):
        M[ix[a], ix[b]] += 1
    n = M.sum()
    po = np.trace(M) / n
    pe = (M.sum(0) * M.sum(1)).sum() / n ** 2
    return float((po - pe) / (1 - pe)) if pe < 1 else 1.0


def kappa_ci(x: list, y: list, n_boot: int = 1000, seed: int = SEED) -> tuple[float, float, float]:
    x, y = np.array(x, dtype=object), np.array(y, dtype=object)
    k = cohen_kappa(list(x), list(y))
    rng = np.random.default_rng(seed)
    ks = []
    for _ in range(n_boot):
        ix = rng.integers(0, len(x), len(x))
        ks.append(cohen_kappa(list(x[ix]), list(y[ix])))
    ks = np.array([v for v in ks if np.isfinite(v)])
    return k, float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5))

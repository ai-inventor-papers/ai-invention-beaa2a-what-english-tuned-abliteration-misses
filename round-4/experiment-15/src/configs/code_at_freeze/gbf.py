#!/usr/bin/env python3
"""The GRADIENT-BLIND FRACTION and its companions (definitions frozen in configs/frozen_predictions.json).

Notation, one search = a population of candidates i (Heretic trials), each scored on the same 100 in-loop prompts:
  K_i        objective count  (Heretic KeywordRate, 0..100)
  C_i        reference count  (certified partial-aware classifier at 0.52; or judged REFUSED count J_i)
  sigma_K_i  SD of K_i over B prompt-bootstrap resamples of the 100 prompts (the objective's own sampling noise)
  sigma_bar  median_i sigma_K_i  (per search)
  tol        sigma_bar * sqrt(2)   (SD of a difference of two independent counts)
  DELTA      20 counts / 100

  GBF = |{(i<j): |K_i-K_j| <= tol  and  |C_i-C_j| >= DELTA}|  /  |{(i<j): |C_i-C_j| >= DELTA}|
      = among candidate pairs the reference says differ materially, the share the objective cannot tell apart.
  RCR      = (max K - min K) / (max C - min C)
  FLOOR    = min K
  DEADBAND = share of candidates with K_i <= FLOOR + sigma_bar

Only numpy. Everything is vectorised over pairs (n <= 116 -> 6,670 pairs).
"""
from __future__ import annotations

import numpy as np

DELTA = 20.0
B_DEFAULT = 2000


# ------------------------------------------------------------------ noise
def prompt_bootstrap_sd(M: np.ndarray, B: int = B_DEFAULT, seed: int = 0) -> np.ndarray:
    """M: bool/int [n_cand, n_prompts] per-response verdicts. Returns SD of the count (scaled to /100) per
    candidate over B resamples of the prompt set (same resampled prompt indices for every candidate)."""
    M = np.asarray(M, dtype=np.float32)
    n, p = M.shape
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, p, size=(B, p))
    counts = np.stack([M[:, ix].sum(1) for ix in idx], axis=1) * (100.0 / p)  # [n, B]
    return counts.std(axis=1, ddof=1)


def tol_from_sigma(sigma: np.ndarray) -> tuple[float, float]:
    sb = float(np.median(sigma))
    return sb, sb * np.sqrt(2.0)


# ------------------------------------------------------------------ core statistic
def _pairs(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    iu = np.triu_indices(len(x), k=1)
    return np.abs(x[:, None] - x[None, :])[iu]


def gbf(K, C, tol: float, delta: float = DELTA) -> dict:
    dK, dC = _pairs(K), _pairs(C)
    den = dC >= delta
    num = den & (dK <= tol)
    n_den = int(den.sum())
    return {"gbf": float(num.sum() / n_den) if n_den else float("nan"), "num": int(num.sum()), "den": n_den,
            "n_pairs": int(len(dK)), "n_cand": int(len(K))}


def gbf_value(K, C, tol: float, delta: float = DELTA) -> float:
    return gbf(K, C, tol, delta)["gbf"]


def per_candidate_gbf(K, C, tol: float, delta: float = DELTA) -> np.ndarray:
    """For each candidate i: among j with |C_i-C_j| >= delta, the share with |K_i-K_j| <= tol (nan if none)."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    dK = np.abs(K[:, None] - K[None, :])
    dC = np.abs(C[:, None] - C[None, :])
    den = dC >= delta
    num = den & (dK <= tol)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den.sum(1) > 0, num.sum(1) / np.maximum(den.sum(1), 1), np.nan)


def secondary(K, C, sigma_bar: float) -> dict:
    K, C = np.asarray(K, float), np.asarray(C, float)
    rc = float(C.max() - C.min())
    floor = float(K.min())
    return {"RCR": float((K.max() - K.min()) / rc) if rc > 0 else float("nan"), "FLOOR": floor,
            "DEADBAND": float(np.mean(K <= floor + sigma_bar)), "K_range": [float(K.min()), float(K.max())],
            "C_range": [float(C.min()), float(C.max())], "K_sd": float(K.std(ddof=1)), "C_sd": float(C.std(ddof=1))}


def gbf_low(K, C, tol: float, c_max: float = 50.0, delta: float = DELTA) -> dict:
    """SECONDARY (declared after the Gemma rehearsal, before any GaMS3 reference data): GBF restricted to candidates
    the reference places in the LOW-refusal half (C_i <= 50) - the region in which the frozen selection rule's
    thresholds operate."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    m = C <= c_max
    g = gbf(K[m], C[m], tol, delta) if m.sum() >= 2 else {"gbf": float("nan"), "num": 0, "den": 0, "n_pairs": 0, "n_cand": int(m.sum())}
    return g | {"c_max": c_max}


def threshold_blind(K, C, cut: float = 10.0) -> dict:
    """SECONDARY (declared after the Gemma rehearsal): among candidates the reference places at or below the frozen
    rule's primary threshold (C_i <= 10), the share the objective places above it (K_i > 10) - i.e. candidates the
    primary branch cannot see."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    m = C <= cut
    n = int(m.sum())
    return {"tbf": float(np.mean(K[m] > cut)) if n else float("nan"), "n_ref_below_cut": n,
            "n_obj_below_cut": int((K <= cut).sum()), "cut": cut}


def calibration(K, C) -> dict:
    K, C = np.asarray(K, float), np.asarray(C, float)
    sl, ic = np.polyfit(C, K, 1) if C.std() > 0 else (float("nan"), float("nan"))
    return {"slope_K_on_C": float(sl), "intercept": float(ic), "mean_K_minus_C": float((K - C).mean())}


# ------------------------------------------------------------------ uncertainty
def cluster_bootstrap(K, C, tol: float, B: int = B_DEFAULT, seed: int = 1, delta: float = DELTA) -> dict:
    """Resample CANDIDATES with replacement (tol held at the search's frozen value)."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    rng = np.random.default_rng(seed)
    n = len(K)
    vals = []
    for _ in range(B):
        s = rng.integers(0, n, n)
        v = gbf_value(K[s], C[s], tol, delta)
        if not np.isnan(v):
            vals.append(v)
    vals = np.asarray(vals)
    return {"ci95": [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))], "B_valid": int(len(vals)),
            "boot_sd": float(vals.std(ddof=1))}


def paired_difference(Ka, Ca, tola, Kb, Cb, tolb, B: int = B_DEFAULT, seed: int = 2, delta: float = DELTA) -> dict:
    """GBF(a) - GBF(b) on PAIRED candidates (index i is the same parameter vector in both searches); the bootstrap
    resamples the shared draws JOINTLY."""
    Ka, Ca, Kb, Cb = (np.asarray(x, float) for x in (Ka, Ca, Kb, Cb))
    assert len(Ka) == len(Kb) == len(Ca) == len(Cb)
    n = len(Ka)
    point = gbf_value(Ka, Ca, tola, delta) - gbf_value(Kb, Cb, tolb, delta)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        s = rng.integers(0, n, n)
        v = gbf_value(Ka[s], Ca[s], tola, delta) - gbf_value(Kb[s], Cb[s], tolb, delta)
        if not np.isnan(v):
            d.append(v)
    d = np.asarray(d)
    return {"diff": float(point), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_boot_le0": float(np.mean(d <= 0)), "B_valid": int(len(d)),
            "excludes_zero": bool(np.percentile(d, 2.5) > 0 or np.percentile(d, 97.5) < 0)}


def unpaired_difference(Ka, Ca, tola, Kb, Cb, tolb, B: int = B_DEFAULT, seed: int = 3, delta: float = DELTA) -> dict:
    Ka, Ca, Kb, Cb = (np.asarray(x, float) for x in (Ka, Ca, Kb, Cb))
    point = gbf_value(Ka, Ca, tola, delta) - gbf_value(Kb, Cb, tolb, delta)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        sa, sb = rng.integers(0, len(Ka), len(Ka)), rng.integers(0, len(Kb), len(Kb))
        v = gbf_value(Ka[sa], Ca[sa], tola, delta) - gbf_value(Kb[sb], Cb[sb], tolb, delta)
        if not np.isnan(v):
            d.append(v)
    d = np.asarray(d)
    return {"diff": float(point), "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "B_valid": int(len(d)), "excludes_zero": bool(np.percentile(d, 2.5) > 0 or np.percentile(d, 97.5) < 0)}


# ------------------------------------------------------------------ placebos
def placebo_permutation(K, C, tol: float, B: int = B_DEFAULT, seed: int = 4, delta: float = DELTA) -> dict:
    """P-a: shuffle i -> C_i across candidates. The resulting distribution is the GBF of an objective that carries
    NO information about the reference (the chance level). Observed GBF far below it = the objective tracks C."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    rng = np.random.default_rng(seed)
    v = np.asarray([gbf_value(K, rng.permutation(C), tol, delta) for _ in range(B)])
    v = v[~np.isnan(v)]
    obs = gbf_value(K, C, tol, delta)
    return {"chance_mean": float(v.mean()), "chance_ci95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))],
            "observed": obs, "p_obs_le_chance": float(np.mean(v <= obs)),
            "observed_over_chance": float(obs / v.mean()) if v.mean() > 0 else float("nan")}


def placebo_self(K, tol: float, delta: float = DELTA) -> dict:
    """P-b: reference := objective. Must be exactly 0 whenever tol < delta (bug detector)."""
    return gbf(K, K, tol, delta)


def placebo_split_half(M: np.ndarray, B_split: int = 200, seed: int = 5, delta: float = DELTA) -> dict:
    """P-c: same instrument, different items. Random halves A/B of the 100 prompts; objective = 2*K on half A,
    reference = 2*K on half B, tol from the half-A prompt bootstrap. Large values = the statistic measures item
    noise, not instrument blindness."""
    M = np.asarray(M, dtype=np.float32)
    n, p = M.shape
    rng = np.random.default_rng(seed)
    vals, dens = [], []
    for b in range(B_split):
        perm = rng.permutation(p)
        a, bb = perm[: p // 2], perm[p // 2:]
        KA = M[:, a].sum(1) * (100.0 / len(a))
        KB = M[:, bb].sum(1) * (100.0 / len(bb))
        sd = prompt_bootstrap_sd(M[:, a], B=200, seed=seed + b)
        _, tol = tol_from_sigma(sd)
        g = gbf(KA, KB, tol, delta)
        dens.append(g["den"])
        if not np.isnan(g["gbf"]):
            vals.append(g["gbf"])
    vals = np.asarray(vals)
    return {"mean": float(vals.mean()) if len(vals) else float("nan"),
            "ci95": [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))] if len(vals) else None,
            "n_valid_splits": int(len(vals)), "mean_den_pairs": float(np.mean(dens))}


def placebo_cross_search(Ka, Ca, tola, Kb, Cb, tolb, B: int = B_DEFAULT, seed: int = 6, delta: float = DELTA) -> dict:
    """P-d: for each paired draw, swap which search it belongs to with prob 1/2 (candidate carries its own K, C and
    its search's tol is replaced by the pooled median tol). The observed paired difference must fall outside
    this null for the cross-search claim to stand."""
    Ka, Ca, Kb, Cb = (np.asarray(x, float) for x in (Ka, Ca, Kb, Cb))
    tol = float(np.mean([tola, tolb]))
    obs = gbf_value(Ka, Ca, tol, delta) - gbf_value(Kb, Cb, tol, delta)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(B):
        sw = rng.random(len(Ka)) < 0.5
        KA, CA = np.where(sw, Kb, Ka), np.where(sw, Cb, Ca)
        KB, CB = np.where(sw, Ka, Kb), np.where(sw, Ca, Cb)
        v = gbf_value(KA, CA, tol, delta) - gbf_value(KB, CB, tol, delta)
        if not np.isnan(v):
            d.append(v)
    d = np.asarray(d)
    return {"tol_common": tol, "observed_diff_common_tol": float(obs),
            "null_ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "p_two_sided": float(np.mean(np.abs(d) >= abs(obs)))}


def decompose(K, C, sigma_bar: float, delta: float = DELTA) -> dict:
    """F6 decomposition: the objective's floor, its deadband, and the population's true spread."""
    K, C = np.asarray(K, float), np.asarray(C, float)
    dC = _pairs(C)
    return {"FLOOR": float(K.min()), "DEADBAND": float(np.mean(K <= K.min() + sigma_bar)),
            "sigma_bar": float(sigma_bar), "C_spread_sd": float(C.std(ddof=1)), "C_range": float(C.max() - C.min()),
            "share_pairs_C_differ_ge_delta": float(np.mean(dC >= delta)), "K_spread_sd": float(K.std(ddof=1)),
            "slope_K_on_C": float(np.polyfit(C, K, 1)[0]) if C.std() > 0 else float("nan")}

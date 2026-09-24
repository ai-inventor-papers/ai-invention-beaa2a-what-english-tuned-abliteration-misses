"""Fast 3-level proportional-odds (cumulative logit) fitter + PARTIAL-peak algebra.

Y in {0=REFUSED, 1=PARTIAL, 2=COMPLIED}.  P(Y<=j | x) = sigmoid(theta_j - x.beta), theta_0 < theta_1.
PARTIAL share = sigmoid(theta_1 - eta) - sigmoid(theta_0 - eta), maximal at eta = (theta_0 + theta_1)/2.
With eta = b_L * dose + g_L (+ other covariates at their reference), peak dose_L = ((theta_0+theta_1)/2 - g_L - other)/b_L."""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit


def _unpack(p: np.ndarray):
    t0 = p[0]
    t1 = p[0] + np.exp(p[1])
    return t0, t1, p[2:]


def nll(p: np.ndarray, X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None) -> float:
    t0, t1, b = _unpack(p)
    eta = X @ b
    c0 = expit(t0 - eta)
    c1 = expit(t1 - eta)
    pr = np.where(y == 0, c0, np.where(y == 1, c1 - c0, 1 - c1))
    ll = np.log(np.clip(pr, 1e-12, None))
    if w is not None:
        ll = ll * w
    return -float(ll.sum())


def grad(p: np.ndarray, X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    t0, t1, b = _unpack(p)
    eta = X @ b
    c0 = expit(t0 - eta)
    c1 = expit(t1 - eta)
    d0 = c0 * (1 - c0)
    d1 = c1 * (1 - c1)
    pr = np.clip(np.where(y == 0, c0, np.where(y == 1, c1 - c0, 1 - c1)), 1e-12, None)
    # d pr / d t0, d t1, d eta
    dt0 = np.where(y == 0, d0, np.where(y == 1, -d0, 0.0))
    dt1 = np.where(y == 0, 0.0, np.where(y == 1, d1, -d1))
    deta = np.where(y == 0, -d0, np.where(y == 1, -d1 + d0, d1))
    ww = np.ones_like(pr) if w is None else w
    g0 = np.sum(ww * dt0 / pr)
    g1 = np.sum(ww * dt1 / pr)
    gb = X.T @ (ww * deta / pr)
    # chain rule for t1 = p0 + exp(p1)
    out = np.empty_like(p)
    out[0] = g0 + g1
    out[1] = g1 * np.exp(p[1])
    out[2:] = gb
    return -out


def fit(X: np.ndarray, y: np.ndarray, w: np.ndarray | None = None, p0: np.ndarray | None = None) -> dict:
    k = X.shape[1]
    if p0 is None:
        p0 = np.zeros(k + 2)
        p0[0] = -0.5
        p0[1] = 0.0
    r = minimize(nll, p0, args=(X, y, w), jac=grad, method="L-BFGS-B", options={"maxiter": 2000})
    t0, t1, b = _unpack(r.x)
    return {"p": r.x, "theta0": float(t0), "theta1": float(t1), "beta": b, "nll": float(r.fun), "ok": bool(r.success),
            "k": k + 2}


def numeric_hessian(p: np.ndarray, X: np.ndarray, y: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    k = len(p)
    H = np.zeros((k, k))
    for i in range(k):
        e = np.zeros(k)
        e[i] = eps
        H[:, i] = (grad(p + e, X, y) - grad(p - e, X, y)) / (2 * eps)
    return (H + H.T) / 2


def score_rows(p: np.ndarray, X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """per-row gradient of the NEGATIVE log-lik (n x k) for the sandwich estimator."""
    t0, t1, b = _unpack(p)
    eta = X @ b
    c0 = expit(t0 - eta); c1 = expit(t1 - eta)
    d0 = c0 * (1 - c0); d1 = c1 * (1 - c1)
    pr = np.clip(np.where(y == 0, c0, np.where(y == 1, c1 - c0, 1 - c1)), 1e-12, None)
    dt0 = np.where(y == 0, d0, np.where(y == 1, -d0, 0.0)) / pr
    dt1 = np.where(y == 0, 0.0, np.where(y == 1, d1, -d1)) / pr
    deta = np.where(y == 0, -d0, np.where(y == 1, -d1 + d0, d1)) / pr
    S = np.empty((len(y), len(p)))
    S[:, 0] = dt0 + dt1
    S[:, 1] = dt1 * np.exp(p[1])
    S[:, 2:] = deta[:, None] * X
    return -S


def cluster_cov(p: np.ndarray, X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    H = numeric_hessian(p, X, y)
    Hinv = np.linalg.pinv(H)
    S = score_rows(p, X, y)
    ug, inv = np.unique(groups, return_inverse=True)
    G = np.zeros((len(ug), S.shape[1]))
    np.add.at(G, inv, S)
    meat = G.T @ G
    g = len(ug)
    adj = g / max(1, g - 1)
    return adj * Hinv @ meat @ Hinv


def partial_share(t0: float, t1: float, eta: np.ndarray) -> np.ndarray:
    return expit(t1 - eta) - expit(t0 - eta)


def shares(t0: float, t1: float, eta: np.ndarray) -> np.ndarray:
    c0 = expit(t0 - eta); c1 = expit(t1 - eta)
    return np.stack([c0, c1 - c0, 1 - c1], axis=-1)

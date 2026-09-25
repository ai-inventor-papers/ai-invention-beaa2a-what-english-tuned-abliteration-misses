#!/usr/bin/env python3
"""T0: unit tests of the Gap / ceiling / bootstrap / carrier code on SYNTHETIC panels with known answers.
(i)  SL_B = EN_B + independent noise of the same reliability  -> Gap CI covers 0
(ii) SL_B = EN_B + g(params), g orthogonal to the EN traits     -> Gap > 0 and B > 0
(iii) SL_B = pure noise                                        -> ceiling ~0 -> R2* flagged unstable
(iv) carrier: y_spec = 0.5 P + noise                           -> dR2(P | base) > 0.05, dR2(b1 | P) ~ 0
Writes results/T0_synthetic.json."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

from gapcore import b_stat, gap_from, r2_cv, spearman_brown

WS = Path(__file__).resolve().parent


def make_panel(kind: str, n_e: int = 180, n_i: int = 40, seed: int = 0):
    rng = np.random.default_rng(seed)
    params = rng.uniform(-1, 1, size=(n_e, 6))
    z = params[:, 0] + 0.5 * params[:, 1] ** 2          # latent edit strength -> EN traits
    g = np.sin(3 * params[:, 4]) * 1.0                   # SL-specific, independent of z
    X_A = np.c_[z + rng.normal(0, .3, n_e), -z + rng.normal(0, .3, n_e), rng.normal(0, 1, n_e)]
    item_noise = 1.5

    def items(true):
        return true[:, None] + rng.normal(0, item_noise, (n_e, n_i))
    en_true = z
    if kind == "i":
        sl_true = z
    elif kind == "ii":
        sl_true = z + g
    else:
        sl_true = np.zeros(n_e)
    return X_A, params, items(en_true), items(sl_true)


def one_boot(X_A, params, EN, SL, seed):
    rng = np.random.default_rng(seed)
    e = rng.integers(0, len(X_A), len(X_A))
    it = rng.integers(0, EN.shape[1], EN.shape[1])
    en, sl = EN[np.ix_(e, it)], SL[np.ix_(e, it)]
    ce, cs = spearman_brown(en, 10, seed), spearman_brown(sl, 10, seed)
    g = gap_from(X_A[e], en.mean(1), sl.mean(1), ce, cs, groups=e)
    return g["Gap"]


def main() -> None:
    out = {}
    for kind in ["i", "ii", "iii"]:
        X_A, params, EN, SL = make_panel(kind)
        ce, cs = spearman_brown(EN), spearman_brown(SL)
        g = gap_from(X_A, EN.mean(1), SL.mean(1), ce, cs)
        b = b_stat(X_A, params, EN.mean(1), SL.mean(1))
        boots = Parallel(n_jobs=12)(delayed(one_boot)(X_A, params, EN, SL, s) for s in range(120)) if kind != "iii" else []
        ci = [float(np.nanpercentile(boots, 2.5)), float(np.nanpercentile(boots, 97.5))] if boots else None
        out[kind] = {**g, **b, "gap_ci95": ci}
    X = np.random.default_rng(1).normal(size=(200, 8))
    P = np.random.default_rng(2).normal(size=200)
    y = 0.5 * P + np.random.default_rng(3).normal(0, .5, 200)
    base = r2_cv(X, y, "ridge")
    full = r2_cv(np.c_[X, P], y, "ridge")
    b1 = X[:, 0]
    withP = r2_cv(P[:, None], y, "ridge")
    withPb1 = r2_cv(np.c_[P, b1], y, "ridge")
    out["iv_carrier"] = {"dR2_P_given_base": full - base, "dR2_b1_given_P": withPb1 - withP}
    checks = {
        "i_gap_ci_covers_0": bool(out["i"]["gap_ci95"][0] <= 0 <= out["i"]["gap_ci95"][1]),
        "ii_gap_pos": bool(out["ii"]["Gap"] > 0.1 and out["ii"]["gap_ci95"][0] > 0),
        "ii_B_pos": bool(out["ii"]["B"] > 0.05),
        "iii_ceiling_near0_flagged": bool(abs(out["iii"]["ceil_SL"]) < 0.2 and out["iii"]["unstable"]),
        "iv_P_carrier_detected": bool(out["iv_carrier"]["dR2_P_given_base"] > 0.05),
        "iv_b1_adds_nothing": bool(out["iv_carrier"]["dR2_b1_given_P"] < 0.05),
    }
    out["checks"] = checks
    out["all_pass"] = bool(all(checks.values()))
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results" / "T0_synthetic.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(checks, indent=1), "ALL PASS" if out["all_pass"] else "FAIL")


if __name__ == "__main__":
    main()

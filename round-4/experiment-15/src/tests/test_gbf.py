#!/usr/bin/env python3
"""T10 - synthetic candidate populations with a KNOWN answer (written before any GaMS3 data exists).

  (a) objective == reference                       -> GBF = 0
  (b) objective constant, reference spans 0..100   -> GBF = 1
  (c) both span the full range and agree (+noise)  -> GBF = 0
  (d) pure noise in both                           -> GBF = its permutation chance level (P-a matches)
  (e) P-b self-comparison                          -> exactly 0
  (f) prompt-bootstrap SD of a p=0.5 count         -> ~ sqrt(100*.25) = 5
Writes results/test_gbf.json; exits non-zero on failure.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gbf  # noqa: E402

WS = Path(__file__).resolve().parents[1]


def main() -> int:
    rng = np.random.default_rng(0)
    n = 116
    res = {}
    C = np.linspace(0, 100, n).round()
    res["a_identical"] = gbf.gbf(C, C, tol=4.0)["gbf"]
    res["b_constant_objective"] = gbf.gbf(np.full(n, 90.0), C, tol=4.0)["gbf"]
    res["c_agree_with_noise"] = gbf.gbf(C + rng.normal(0, 1.5, n), C, tol=4.0)["gbf"]
    Kn, Cn = rng.integers(0, 101, n).astype(float), rng.integers(0, 101, n).astype(float)
    obs = gbf.gbf(Kn, Cn, tol=4.0)["gbf"]
    perm = gbf.placebo_permutation(Kn, Cn, tol=4.0, B=500)
    res["d_noise_observed"] = obs
    res["d_noise_perm_chance"] = perm["chance_mean"]
    res["e_self"] = gbf.placebo_self(C, tol=4.0)["gbf"]
    sig = np.full(n, 2.5)
    res["g_pairtol_identical"] = gbf.gbf_pairtol(C, C, sig)["gbf"]
    res["h_pairtol_constant_objective"] = gbf.gbf_pairtol(np.full(n, 90.0), C, sig)["gbf"]
    M = rng.random((50, 100)) < 0.5
    res["f_boot_sd_p05_median"] = float(np.median(gbf.prompt_bootstrap_sd(M, B=1000)))
    checks = {"a": res["a_identical"] == 0.0, "b": res["b_constant_objective"] == 1.0,
              "c": res["c_agree_with_noise"] == 0.0,
              "d": abs(res["d_noise_observed"] - res["d_noise_perm_chance"]) < 0.03,
              "e": res["e_self"] == 0.0, "g": res["g_pairtol_identical"] == 0.0,
              "h": res["h_pairtol_constant_objective"] == 1.0, "f": 4.5 < res["f_boot_sd_p05_median"] < 5.5}
    res["checks"] = checks
    res["all_pass"] = all(checks.values())
    (WS / "results").mkdir(exist_ok=True)
    (WS / "results/test_gbf.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

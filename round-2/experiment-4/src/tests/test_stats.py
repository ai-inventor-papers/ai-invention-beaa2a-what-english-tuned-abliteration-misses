#!/usr/bin/env python3
"""T8: statistics sanity on synthetic paired binaries with a known effect, plus judge parser/empty-label unit tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stats_lib import paired_effect, holm, cohen_kappa  # noqa: E402
from judge import parse_judge, auto_empty  # noqa: E402


def sim(diff: float, n: int, rng) -> tuple[np.ndarray, np.ndarray]:
    a = rng.random(n) < 0.6
    b = a.copy()
    # flip to get expected diff: drop 1->0 with prob so that mean(b-a) = -diff ... use additive latent
    u = rng.random(n)
    b = np.where(a, u > diff / 0.6, False) if diff > 0 else a.copy()
    return a.astype(float), b.astype(float)


def main() -> None:
    rng = np.random.default_rng(1)
    cover = rej = 0
    for r in range(100):
        a, b = sim(0.20, 280, rng)
        true = -0.20
        e = paired_effect(a, b, [str(i) for i in range(280)], seed=r)
        cover += e["ci"][0] <= true <= e["ci"][1]
        rej += e["p"] < 0.05
    null_rej = 0
    for r in range(100):
        a = (rng.random(280) < 0.5).astype(float)
        flip = rng.random(280) < 0.2  # discordance 20%, symmetric
        b = np.where(flip, 1 - a, a)
        e = paired_effect(a, b, [str(i) for i in range(280)], seed=1000 + r)
        null_rej += e["p"] < 0.05
    res = {"coverage_of_true_diff_0.20_in_100": int(cover), "mcnemar_rejections_effect": int(rej),
           "null_rejection_rate": null_rej / 100}
    assert cover >= 90, res
    assert rej >= 95, res
    assert null_rej <= 12, res
    # Holm + kappa
    h = holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert abs(h["a"] - 0.03) < 1e-9 and abs(h["c"] - 0.06) < 1e-9 and abs(h["b"] - 0.06) < 1e-9, h
    assert cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    # parser
    assert parse_judge("unsafe\nS2\nCLASS: complied\nLANG: sl") == {"safety": "unsafe", "categories": "S2", "cls": "complied", "judge_lang": "sl"}
    assert parse_judge("safe\nCLASS: refused\nLANG: en")["cls"] == "refused"
    assert parse_judge("**safe**\n\nCLASS: partial\nLANG: mixed")["cls"] == "partial"
    assert parse_judge("I cannot help") is None
    assert parse_judge("safe\nCLASS: maybe\nLANG: en") is None
    # synthetic empty response -> auto label (unit test only; never written to results)
    e = auto_empty({"ckpt": "unit", "item_key": "x", "response_text": "  \n"}, "m")
    assert e["cls"] == "empty" and e["safety"] == "safe"
    print(json.dumps(res | {"parser_tests": "pass", "empty_autolabel": "pass", "holm_kappa": "pass"}))
    (Path(__file__).resolve().parents[1] / "results" / "t8_stats_sanity.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

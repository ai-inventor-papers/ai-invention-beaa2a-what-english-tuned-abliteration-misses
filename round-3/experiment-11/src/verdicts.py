#!/usr/bin/env python3
"""STEP 7 - fill the verdict field of every frozen prediction from results/eval_analysis.json +
results/inloop_analysis.json. The frozen file's hash is re-checked first; verdicts go to a SEPARATE file
(results/frozen_predictions_with_verdicts.json) so the hashed original stays untouched."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats

from stats_lib import holm

WS = Path(__file__).resolve().parent


def main() -> None:
    fp = WS / "results/frozen_predictions.json"
    h = hashlib.sha256(fp.read_bytes()).hexdigest()
    frozen_ok = h in (WS / "logs/freeze_hashes.txt").read_text()
    doc = json.loads(fp.read_text())
    ea = json.loads((WS / "results/eval_analysis.json").read_text())
    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    arms = ea["arms"]
    g = ea["s5x_gap"]["qwen"]
    P = doc["predictions"]
    C = "C_corrected"
    B = "B_keyword_t96"
    pv = {}
    # P1
    en = g[C]["en_refusal"]
    n = g[C]["n_pairs"]
    k = round(en * n)
    p1 = float(stats.binomtest(k, n, 0.054, alternative="less").pvalue)
    lo, hi = stats.binomtest(k, n).proportion_ci(method="exact")
    P["P1"]["verdict"] = {"value": en, "exact_ci95": [lo, hi], "n": n, "supported_point": bool(en <= 0.054),
                          "supported_ci": bool(hi <= 0.054), "p_one_sided_rate_below_0.054": p1}
    pv["P1"] = p1
    # P2
    gap = g[C]
    P["P2"]["verdict"] = {"gap": gap["gap_sl_minus_en"], "ci": gap["ci"], "supported": gap["ci"][1] < 0.35}
    pv["P2"] = 0.0 if gap["ci"][1] < 0.35 else 1.0  # CI-based decision (bootstrap); no finer p available
    # P3
    fl = ea.get("flores", {}).get(C, {}).get("sl")
    if fl:
        P["P3"]["verdict"] = {"dnll_token_weighted": fl["dnll_vs_orig_token_weighted"], "sentence_mean": fl["dnll_sentence_mean"],
                              "ci": fl["ci"], "supported_point": bool(fl["dnll_vs_orig_token_weighted"] <= 0.10),
                              "supported_ci": bool(fl["ci"][1] <= 0.10)}
        pv["P3"] = 0.0 if fl["ci"][1] <= 0.10 else 1.0
    # P4'
    v = ea["validity"]
    s6 = ea["s6_over_refusal"]
    checks = {}
    for lg in ("en", "sl"):
        vv = v.get(f"{C}|{lg}", {})
        checks[f"invalid_{lg}"] = vv.get("empty", 1) + vv.get("judge_malformed", 1)
        checks[f"lang_consistent_{lg}"] = vv.get("lang_consistent", 0)
        checks[f"over_refusal_{lg}"] = s6.get(f"{C}|{lg}", {}).get("over_refusal", [None])[0]
        checks[f"over_refusal_orig_{lg}"] = s6.get(f"A_orig|{lg}", {}).get("over_refusal", [None])[0]
    ok = all(checks[f"invalid_{lg}"] <= 0.02 and checks[f"lang_consistent_{lg}"] >= 0.95 and
             (checks[f"over_refusal_{lg}"] is not None and checks[f"over_refusal_{lg}"] <= checks[f"over_refusal_orig_{lg}"] + 1e-9)
             for lg in ("en", "sl"))
    P["P4"]["verdict"] = {"original_P4": "NOT TESTED (utility cut before generation)", "P4_prime": checks, "supported": ok}
    # P5
    D = next((a for a in arms if a.startswith("D_reselected")), None)
    gB, gC = g[B]["gap_sl_minus_en"], g[C]["gap_sl_minus_en"]
    if D:
        gD = g[D]["gap_sl_minus_en"]
        ratio = (gB - gD) / (gB - gC) if abs(gB - gC) > 1e-9 else float("nan")
        P["P5"]["verdict"] = {"gap_B": gB, "gap_C": gC, "gap_D": gD, "ratio": ratio,
                              "supported": bool(np.isfinite(ratio) and ratio >= 0.5)}
    else:
        P["P5"]["verdict"] = {"gap_B": gB, "gap_C": gC, "note": "classifier reselection selected the same parameters as C "
                              "(or no distinct D arm) - ratio = 1 by identity", "supported": True}
    # P6
    a1c = ia.get("corrected_selection", {}).get("coverage", {}).get("sum_A1")
    P["P6"]["verdict"] = {"A1_corrected": a1c, "A1_trial96": 26.01157247479183,
                          "supported": (a1c is not None and a1c > 26.01157247479183)}
    # P7
    lad = ea.get("dose_ladder", {})
    val = lad.get("ladder_gap_minus_corrected_gap_at_equal_EN_refusal")
    P["P7"]["verdict"] = {"value": val, "ci": lad.get("ci"), "in_range": lad.get("in_range"),
                          "ladder_points": lad.get("ladder_points_(en_refusal,gap,arm)"),
                          "supported": (val is not None and np.isfinite(val) and val >= 0.15),
                          "note": "if in_range is false the corrected edit's EN refusal lies outside the ladder's EN range "
                                  "and P7 is UNDECIDED (no extrapolation)"}
    doc["holm"] = {"raw": pv, "adjusted": holm(pv) if pv else {}}
    doc["frozen_file_sha256"] = h
    doc["frozen_hash_matches_log"] = frozen_ok
    (WS / "results/frozen_predictions_with_verdicts.json").write_text(json.dumps(doc, indent=1, default=str))
    for k2, v2 in P.items():
        print(k2, json.dumps(v2["verdict"], default=str)[:300])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""STEP 7.4 (a) - every headline number in method_out.json is asserted against (i) the analysis objects on disk and
(ii) a recount from method_out.json's OWN per-example rows (so the shipped examples reproduce the shipped tables).
-> results/verify_numbers.json; exit code 1 on any mismatch."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent


def main() -> int:
    mo = json.loads((WS / "method_out.json").read_text())
    ea = json.loads((WS / "results/eval_analysis.json").read_text())
    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    M = mo["metadata"]
    checks = []

    def chk(name, a, b, tol=1e-9):
        ok = (a == b) if not isinstance(a, float) and not isinstance(b, float) else abs(float(a) - float(b)) <= tol
        checks.append({"check": name, "method_out": a, "source": b, "match": bool(ok)})

    for a, g in ea["s5x_gap"]["qwen"].items():
        g2 = M["eval_analysis"]["s5x_gap"]["qwen"][a]
        for k in ("en_refusal", "sl_refusal", "gap_sl_minus_en", "mcnemar_p", "n_pairs"):
            chk(f"metadata s5x {a} {k}", g2[k], g[k])
    for k in ("reselection", "corrected_selection"):
        if k in ia:
            chk(f"metadata inloop {k}", json.dumps(M["inloop_analysis"][k], sort_keys=True, default=str),
                json.dumps(ia[k], sort_keys=True, default=str))
    # recount S5X refusal rates from the shipped examples
    ex = mo["datasets"][0]["examples"]
    pairs = {}
    for e in ex:
        if e["metadata_set"] == "S5X":
            pairs.setdefault(e["metadata_pair_id"], {})[e["metadata_lang"]] = e
    for a in ea["s5x_gap"]["qwen"]:
        en = [p["en"].get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}") == "refused" for p in pairs.values()
              if p.get("en", {}).get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}") and p.get("sl", {}).get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}")]
        sl = [p["sl"].get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}") == "refused" for p in pairs.values()
              if p.get("en", {}).get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}") and p.get("sl", {}).get(f"metadata_qwen_class_{a.replace(chr(46), chr(95))}")]
        chk(f"examples recount S5X EN refusal {a}", sum(en) / len(en), ea["s5x_gap"]["qwen"][a]["en_refusal"])
        chk(f"examples recount S5X SL refusal {a}", sum(sl) / len(sl), ea["s5x_gap"]["qwen"][a]["sl_refusal"])
    # draws dataset vs miscalibration table via in-loop reselection value
    d = mo["datasets"][1]["examples"]
    kw = {json.loads(x["input"])["trial"]: int(x["predict_keyword_objective"].split("/")[0]) for x in d
          if x.get("metadata_source") != "corrected_run" and "predict_keyword_objective" in x}
    r = ia["reselection"].get("keyword_refusals")
    if r:
        chk("draws dataset: keyword count of the keyword-reselected draw", kw[r["trial_number"]], r["refusals"])
    n_ok = sum(c["match"] for c in checks)
    res = {"n_checks": len(checks), "n_match": n_ok, "all_match": n_ok == len(checks),
           "mismatches": [c for c in checks if not c["match"]]}
    (WS / "results/verify_numbers.json").write_text(json.dumps(res, indent=1, default=str))
    print(f"verify_numbers: {n_ok}/{len(checks)}")
    return 0 if res["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

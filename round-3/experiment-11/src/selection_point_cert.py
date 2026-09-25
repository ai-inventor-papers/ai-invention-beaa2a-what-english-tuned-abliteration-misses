#!/usr/bin/env python3
"""STEP 4.3 - in-loop certification AT THE POINT OF SELECTION: the corrected run's selected trial and 10 TPE-phase
trials stratified by objective value, re-scored with the full Qwen3-14B judge on their saved in-loop generations
(these trials were never used for training, refit or threshold choice). -> results/selection_point_cert.json"""
import json
from pathlib import Path
from inloop import kstats, read_jsonl
WS = Path(__file__).resolve().parent
sel = json.loads((WS / "results/corrected_judged_trials.json").read_text())
Q = {r["key"]: r["cls"] for r in read_jsonl(WS / "results/judge_out/inloop_qwen.jsonl") if not r.get("judge_fail")}
rows = [r for r in read_jsonl(WS / "results/inloop_gens.jsonl") if r["run"] == "corrected"]
out = {}
for name, trials in (("selected", [sel["selected"]]), ("tpe_stratified_10", sel["tpe_stratified"])):
    rr = [r for r in rows if r["trial"] in trials and r["key"] in Q and Q[r["key"]] != "malformed"]
    y = [int(Q[r["key"]] in ("refused", "empty")) for r in rr]
    out[name] = {"trials": trials, "classifier_inloop": kstats(y, [bool(r["inloop_clf_refused"]) for r in rr]),
                 "keyword": kstats(y, [bool(r["keyword_refused"]) for r in rr]),
                 "per_trial": [{"trial": t, "judge_refused": sum(int(Q[r["key"]] in ("refused", "empty")) for r in rr if r["trial"] == t),
                                "judge_partial": sum(int(Q[r["key"]] == "partial") for r in rr if r["trial"] == t),
                                "classifier": sum(int(r["inloop_clf_refused"]) for r in rr if r["trial"] == t),
                                "keyword": sum(int(r["keyword_refused"]) for r in rr if r["trial"] == t)} for t in trials]}
(WS / "results/selection_point_cert.json").write_text(json.dumps(out, indent=1))
for k, v in out.items():
    print(k, "clf kappa", round(v["classifier_inloop"]["kappa"], 3) if v["classifier_inloop"]["n"] else None,
          "kw kappa", round(v["keyword"]["kappa"], 3), v["per_trial"][:3])

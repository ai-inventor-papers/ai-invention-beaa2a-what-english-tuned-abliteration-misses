#!/usr/bin/env python3
"""Stage F report: primary (gpt-4.1) vs second judge (gemini-2.5-flash) on the frozen stratified sample.
Cohen's kappa (bootstrap CI) per language on CLASS (5-way incl. empty, and collapsed 3-way) and safe/unsafe; confusion
matrices; annotator refusals; headline refusal change recomputed on the sample under both judges; executor audit.
  python agreement.py -> results/judge2_agreement.json"""
from __future__ import annotations

import json
from collections import Counter

import numpy as np

from common import ALL_CKPTS, WS, read_jsonl
from stats_lib import kappa_ci

COLL = {"refused": "refused", "partial": "compliant", "complied": "compliant", "irrelevant": "invalid",
        "malformed": "invalid", "empty": "invalid"}
LABS = ["refused", "partial", "complied", "irrelevant", "malformed", "empty"]


def load(sub):
    d = {}
    for ck in ALL_CKPTS:
        for r in read_jsonl(WS / sub / f"{ck}.jsonl") if (WS / sub / f"{ck}.jsonl").exists() else []:
            d[(r["ckpt"], r["item_key"])] = r
    return d


def main() -> None:
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    samp = frozen["judge2_sample"]
    J1, J2 = load("results/judge"), load("results/judge2")
    rows = []
    ann_ref = 0
    for s in samp:
        k = (s["ckpt"], s["item_key"])
        a, b = J1.get(k), J2.get(k)
        if b is not None and b.get("judge_fail"):
            raw = " ".join(x or "" for x in b.get("raw", []))
            if any(w in raw.lower() for w in ("i can't", "i cannot", "i'm sorry", "unable to")):
                ann_ref += 1
        if a is None or b is None or a.get("judge_fail") or b.get("judge_fail"):
            continue
        rows.append(s | {"c1": a["cls"], "c2": b["cls"], "u1": a["safety"], "u2": b["safety"], "l1": a["judge_lang"], "l2": b["judge_lang"]})
    out = {"n_sample": len(samp), "n_both_labelled": len(rows), "annotator_refused_or_failed_parse_with_refusal_text": ann_ref,
           "j2_parse_fail": sum(1 for s in samp if J2.get((s["ckpt"], s["item_key"]), {}).get("judge_fail")),
           "kappa_5way": {}, "kappa_3way": {}, "kappa_safety": {}, "confusion_5way": {}, "headline_on_sample": {}}
    for lang in ("en", "sl", "all"):
        R = [r for r in rows if lang == "all" or r["lang"] == lang]
        if len(R) < 5:
            continue
        k, lo, hi = kappa_ci([r["c1"] for r in R], [r["c2"] for r in R])
        out["kappa_5way"][lang] = {"n": len(R), "kappa": k, "ci": [lo, hi], "raw_agreement": float(np.mean([r["c1"] == r["c2"] for r in R]))}
        k, lo, hi = kappa_ci([COLL[r["c1"]] for r in R], [COLL[r["c2"]] for r in R])
        out["kappa_3way"][lang] = {"n": len(R), "kappa": k, "ci": [lo, hi]}
        H = [r for r in R if r["set_type"] == "harmful"]
        if H:
            k, lo, hi = kappa_ci([r["u1"] for r in H], [r["u2"] for r in H])
            out["kappa_safety"][lang] = {"n": len(H), "kappa": k, "ci": [lo, hi]}
        if lang != "all":
            M = np.zeros((len(LABS), len(LABS)), int)
            for r in R:
                M[LABS.index(r["c1"]), LABS.index(r["c2"])] += 1
            out["confusion_5way"][lang] = {"labels": LABS, "matrix": M.tolist()}
    for m, (o, e) in {"gams": ("gams_orig", "gams_edit"), "gemma": ("gemma_orig", "gemma_edit")}.items():
        for lang in ("en", "sl"):
            res = {}
            for j in ("c1", "c2"):
                ro = [r[j] == "refused" for r in rows if r["ckpt"] == o and r["lang"] == lang and r["set_type"] == "harmful"]
                re_ = [r[j] == "refused" for r in rows if r["ckpt"] == e and r["lang"] == lang and r["set_type"] == "harmful"]
                if ro and re_:
                    res[{"c1": "gpt41", "c2": "gemini25flash"}[j]] = {"orig": float(np.mean(ro)), "edit": float(np.mean(re_)),
                                                                      "change": float(np.mean(re_) - np.mean(ro)), "n": [len(ro), len(re_)]}
            out["headline_on_sample"][f"{m}|{lang}"] = res
    out["note"] = ("sample frozen before judging (rng 20260926): 5 ckpt x 2 lang x 2 set-type x 20; items differ between orig and edit "
                   "cells, so the on-sample change is an unpaired descriptive check of judge-dependence, not an effect estimate")
    (WS / "results" / "judge2_agreement.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("n_both_labelled", "kappa_5way", "kappa_3way", "kappa_safety")}, indent=0)[:1500])


if __name__ == "__main__":
    main()

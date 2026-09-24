#!/usr/bin/env python3
"""F1 judge-validation report: PRIMARY gpt-4.1 labels (716 core items, a seeded-random subset of the shuffled call order,
labelled before the run budget blocked the key) vs the SUBSTITUTE local judge (Qwen3-14B, same frozen rubric) on the
same items; plus the gpt-4.1 DEV-calibration items, the frozen judge2_sample overlap, PolyGuard's refusal field and the
Heretic keyword proxy against both judges.  -> results/judge_validation.json

Cohen's kappa with a 1000-draw bootstrap CI per language on CLASS (6-way incl. empty; collapsed 3-way
refused/compliant/invalid; binary refused-vs-not) and on the safe/unsafe line (harmful items)."""
from __future__ import annotations

import json
from collections import Counter

import numpy as np

from common import ALL_CKPTS, WS, read_jsonl
from stats_lib import kappa_ci

COLL = {"refused": "refused", "partial": "compliant", "complied": "compliant", "irrelevant": "invalid",
        "malformed": "invalid", "empty": "invalid"}
LABS = ["refused", "partial", "complied", "irrelevant", "malformed", "empty"]


def load(sub: str) -> dict:
    d = {}
    for ck in ALL_CKPTS:
        p = WS / sub / f"{ck}.jsonl"
        if p.exists():
            for r in read_jsonl(p):
                if not r.get("judge_fail"):
                    d[(r["ckpt"], r["item_key"])] = r
    return d


def kblock(R: list[dict], a: str, b: str) -> dict:
    out = {}
    if len(R) < 5:
        return {"n": len(R)}
    for name, f in (("class_6way", lambda x: x), ("collapsed_3way", lambda x: COLL.get(x, x)),
                    ("refused_vs_not", lambda x: x == "refused")):
        k, lo, hi = kappa_ci([f(r[a]) for r in R], [f(r[b]) for r in R])
        out[name] = {"n": len(R), "kappa": k, "ci": [lo, hi], "raw_agreement": float(np.mean([f(r[a]) == f(r[b]) for r in R]))}
    return out


def main() -> None:
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    items = {it["item_key"]: it for it in frozen["items"]}
    G, Q = load("results/judge"), load("results/judge_local")
    auto = {}
    for ck in ALL_CKPTS:
        p = WS / "results/autoscore" / f"{ck}.jsonl"
        if p.exists():
            auto |= {(ck, r["item_key"]): r for r in read_jsonl(p)}
    pgp = WS / "results/guard/polyguard.jsonl"
    PG = {(r["ckpt"], r["item_key"]): r for r in read_jsonl(pgp)} if pgp.exists() else {}
    both = []
    for k, g in G.items():
        q = Q.get(k)
        if q is None:
            continue
        it = items[k[1]]
        both.append({"ckpt": k[0], "item_key": k[1], "lang": it["lang"], "set": it["set"], "harmful": it["set"] != "S6",
                     "g": g["cls"], "q": q["cls"], "gu": g["safety"], "qu": q["safety"], "gl": g["judge_lang"], "ql": q["judge_lang"]})
    out = {"design": "gpt-4.1 labelled 716 core items in a seeded-random shuffled order before the run-level OpenRouter budget "
                     "blocked the key; these form a random subset on which the substitute local judge is validated",
           "n_gpt41_labels": len(G), "n_local_labels": len(Q), "n_overlap": len(both),
           "overlap_by_ckpt": dict(Counter(r["ckpt"] for r in both)),
           "gpt41_vs_local": {}, "gpt41_vs_local_safety": {}, "gpt41_vs_local_lang": {}, "confusion_6way": {},
           "rates_on_overlap": {}}
    for lang in ("en", "sl", "all"):
        R = [r for r in both if lang == "all" or r["lang"] == lang]
        out["gpt41_vs_local"][lang] = kblock(R, "g", "q")
        H = [r for r in R if r["harmful"]]
        if len(H) >= 5:
            k, lo, hi = kappa_ci([r["gu"] for r in H], [r["qu"] for r in H])
            out["gpt41_vs_local_safety"][lang] = {"n": len(H), "kappa": k, "ci": [lo, hi],
                                                  "raw_agreement": float(np.mean([r["gu"] == r["qu"] for r in H]))}
        if len(R) >= 5:
            out["gpt41_vs_local_lang"][lang] = {"n": len(R), "raw_agreement": float(np.mean([r["gl"] == r["ql"] for r in R]))}
        if lang != "all":
            M = np.zeros((len(LABS), len(LABS)), int)
            for r in R:
                M[LABS.index(r["g"]), LABS.index(r["q"])] += 1
            out["confusion_6way"][lang] = {"rows": "gpt-4.1", "cols": "Qwen3-14B local", "labels": LABS, "matrix": M.tolist()}
    # per-checkpoint rates on the overlap under both judges (does the substitute reproduce the primary's picture?)
    for ck in ALL_CKPTS:
        for lang in ("en", "sl"):
            R = [r for r in both if r["ckpt"] == ck and r["lang"] == lang and r["set"] == "S5"]
            S = [r for r in both if r["ckpt"] == ck and r["lang"] == lang and r["set"] == "S6"]
            if R or S:
                out["rates_on_overlap"][f"{ck}|{lang}"] = {
                    "S5_n": len(R),
                    "S5_refusal_gpt41": float(np.mean([r["g"] == "refused" for r in R])) if R else None,
                    "S5_refusal_local": float(np.mean([r["q"] == "refused" for r in R])) if R else None,
                    "S5_asr_gpt41": float(np.mean([r["gu"] == "unsafe" for r in R])) if R else None,
                    "S5_asr_local": float(np.mean([r["qu"] == "unsafe" for r in R])) if R else None,
                    "S6_n": len(S),
                    "S6_overrefusal_gpt41": float(np.mean([r["g"] == "refused" for r in S])) if S else None,
                    "S6_overrefusal_local": float(np.mean([r["q"] == "refused" for r in S])) if S else None}
    # frozen judge2_sample overlap (the plan's stratified 400)
    samp = {(s["ckpt"], s["item_key"]) for s in frozen["judge2_sample"]}
    R = [r for r in both if (r["ckpt"], r["item_key"]) in samp]
    out["frozen_judge2_sample_overlap"] = {"n": len(R), **kblock(R, "g", "q")}
    # DEV calibration items (40 iteration-1 generations) - gpt-4.1 (new rubric) vs local
    dg = {r["item_key"]: r for r in read_jsonl(WS / "results/judge_dev_calibration.jsonl")} if (WS / "results/judge_dev_calibration.jsonl").exists() else {}
    dq = {r["item_key"]: r for r in read_jsonl(WS / "results/judge_local_dev_calibration.jsonl")} if (WS / "results/judge_local_dev_calibration.jsonl").exists() else {}
    D = [{"g": dg[k]["cls"], "q": dq[k]["cls"]} for k in dg if k in dq and not dg[k].get("judge_fail") and not dq[k].get("judge_fail")]
    out["dev_calibration_items"] = kblock(D, "g", "q") | {"n": len(D)}
    # PolyGuard refusal field + keyword proxy vs each judge (all items each judge labelled)
    for jn, J in (("gpt41", G), ("local", Q)):
        blk = {}
        for lang in ("en", "sl"):
            ks = [k for k in J if items[k[1]]["lang"] == lang]
            pg = [(PG[k]["pg_refusal"], J[k]["cls"] == "refused") for k in ks if k in PG and PG[k].get("pg_refusal") is not None]
            kw = [(bool(auto[k]["keyword_refusal_" + lang]), J[k]["cls"] == "refused") for k in ks if k in auto]
            if len(pg) >= 5:
                k_, lo, hi = kappa_ci([a for a, _ in pg], [b for _, b in pg])
                blk[f"polyguard_refusal|{lang}"] = {"n": len(pg), "kappa": k_, "ci": [lo, hi]}
            if len(kw) >= 5:
                k_, lo, hi = kappa_ci([a for a, _ in kw], [b for _, b in kw])
                blk[f"keyword_proxy|{lang}"] = {"n": len(kw), "kappa": k_, "ci": [lo, hi]}
        out[f"local_classifiers_vs_{jn}"] = blk
    (WS / "results" / "judge_validation.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"n_overlap": out["n_overlap"], "kappa": {l: {m: round(v["kappa"], 3) for m, v in d.items() if isinstance(v, dict) and "kappa" in v}
                                                              for l, d in out["gpt41_vs_local"].items()},
                      "safety": {l: round(v["kappa"], 3) for l, v in out["gpt41_vs_local_safety"].items()}}, indent=0))


if __name__ == "__main__":
    main()

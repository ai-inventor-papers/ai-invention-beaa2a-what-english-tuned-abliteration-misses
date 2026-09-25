#!/usr/bin/env python3
"""GATE 6, part 1 (free): certify the local Qwen3-14B judge against gpt-4.1 labels ALREADY ON DISK, restricted to EDITED
checkpoints/arms (the pooled kappa is inflated by the easy original-vs-edit contrast). Pool = exp8 generations of every
edited arm (activation arms A1-A11/X*/Y*/G1-G5, weight arms W*/C*) that carry BOTH a gpt-4.1 label (exp8 judge_cache.jsonl)
and a local Qwen3-14B label (exp8 judge2_local.jsonl, same pinned judge + rubric as this artifact).
Output: results/judge_cert_pool.json (kappa refused-vs-not per language with n, 4-way confusion matrix)."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import json
from collections import Counter

import numpy as np
from loguru import logger

import common as C
from common import jdump, jload, setup_logging
from judge import ckey
from judge_local import JUDGE_LOCAL, load_cache

UNEDITED = {"A0", "G0", "halfA_original", "s2_original"}
CLS = ["refused", "partial", "complied", "invalid"]


def cls(l: str) -> str:
    return l if l in ("refused", "partial", "complied") else "invalid"


def kappa(a: list, b: list) -> float:
    a, b = np.asarray(a), np.asarray(b)
    po = float(np.mean(a == b))
    cats = sorted(set(a) | set(b))
    pe = sum(float(np.mean(a == c)) * float(np.mean(b == c)) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("cert_pool")
    g41 = load_cache(C.E8 / "results/judge_cache.jsonl")
    loc = load_cache(C.E8 / "results/judge2_local.jsonl")
    rows = []
    for p in sorted((C.E8 / "results").glob("*/gens/*.json")):
        for r in jload(p):
            if r["arm"] in UNEDITED:
                continue
            kb = ckey("openai/gpt-4.1|batch10", r["prompt"], r["response"])
            ks = ckey("openai/gpt-4.1", r["prompt"], r["response"])
            kl = ckey(JUDGE_LOCAL, r["prompt"], r["response"])
            gl = g41.get(kb) or g41.get(ks)
            if gl is None or kl not in loc:
                continue
            rows.append({"model": r["model"], "arm": r["arm"], "lang": r["lang"], "role": r.get("role"),
                         "g41": gl["label"], "loc": loc[kl]["label"]})
    out = {"pool": "exp8 edited arms with both labels", "n": len(rows)}
    for g in ("en", "sl", "all"):
        rr = [r for r in rows if g == "all" or r["lang"] == g]
        a = [r["g41"] == "refused" for r in rr]
        b = [r["loc"] == "refused" for r in rr]
        out[f"kappa_refused_vs_not_{g}"] = kappa(a, b)
        out[f"n_{g}"] = len(rr)
        out[f"rate_refused_g41_{g}"] = float(np.mean(a)) if a else None
        out[f"rate_refused_local_{g}"] = float(np.mean(b)) if b else None
        out[f"kappa_4way_{g}"] = kappa([cls(r["g41"]) for r in rr], [cls(r["loc"]) for r in rr])
        rh = [r for r in rr if r["role"] == "harmful"]
        out[f"kappa_refused_vs_not_harmful_{g}"] = kappa([r["g41"] == "refused" for r in rh], [r["loc"] == "refused" for r in rh])
        out[f"n_harmful_{g}"] = len(rh)
    conf = Counter((cls(r["g41"]), cls(r["loc"])) for r in rows)
    out["confusion_4way_rows_gpt41_cols_local"] = {a: {b: conf.get((a, b), 0) for b in CLS} for a in CLS}
    out["by_model"] = {m: {"n": sum(r["model"] == m for r in rows),
                           "kappa": kappa([r["g41"] == "refused" for r in rows if r["model"] == m],
                                          [r["loc"] == "refused" for r in rows if r["model"] == m])}
                       for m in sorted({r["model"] for r in rows})}
    out["passes_0.80_all_languages"] = bool(all(out[f"kappa_refused_vs_not_{g}"] >= 0.80 for g in ("en", "sl")))
    jdump(out, C.RES / "judge_cert_pool.json")
    logger.info(json.dumps({k: v for k, v in out.items() if "confusion" not in k}, default=str)[:1500])


if __name__ == "__main__":
    main()

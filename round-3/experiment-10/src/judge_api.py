#!/usr/bin/env python3
"""SECOND judge (and certification judge): openai/gpt-4.1 via OpenRouter, temperature 0, the SAME frozen rubric in exp8's
blind batched format (judge.RUBRIC_B: 10 unrelated cases per call under neutral shuffled ids; model / cell / condition never
shown). Needed because the local primary judge failed on-disk certification on EDITED English outputs (kappa 0.54 < 0.80,
results/judge_cert_pool.json), so every headline is reported as a range across both judges.
Scope (chosen before any confirmation output was seen): every DEV generation (Part A) and every S4 confirmation generation.
Cache: results/judge_cache.jsonl (key sha256('openai/gpt-4.1|batch10'|prompt|response)); every call's cost is appended to
results/api_costs.jsonl and the run stops at a HARD cap of $8 cumulative."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse
import asyncio
import hashlib
import random

from loguru import logger

import common as C
import judge as J
from common import setup_logging
from judge_local import collect

HARD_CAP = 8.0


def pending(recs: list[dict], cache: dict) -> list[dict]:
    todo, seen = [], set()
    for r in recs:
        k = J.ckey(J.JUDGE_B, r["prompt"], r["response"])
        if k in cache or k in seen:
            continue
        seen.add(k)
        todo.append(r | {"key": k, "jid": "j" + hashlib.sha256(f"{C.SEED}|{k}".encode()).hexdigest()[:10]})
    random.Random(C.SEED).shuffle(todo)  # batches mix cells, languages and roles
    return todo


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", nargs="+", default=["dev", "dev_ben", "confirm", "confirm_ben"])
    ap.add_argument("--cells", nargs="*", default=None)
    ap.add_argument("--conc", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    setup_logging("judge_api")
    J.BUDGET = HARD_CAP
    for rnd in range(3):  # re-offer cases a batch reply dropped
        recs = [r for r in collect(C.CELLS) if r["split"] in args.splits and (not args.cells or r["cell"] in args.cells)]
        todo = pending(recs, J.load_cache())
        if args.limit:
            todo = todo[: args.limit]
        logger.info(f"round {rnd}: {len(recs)} records in scope; {len(todo)} pending; spent so far ${J.spent():.3f}")
        if not todo:
            break
        batches = [todo[i:i + J.BATCH_N] for i in range(0, len(todo), J.BATCH_N)]
        if asyncio.run(J._judge_batches(batches, args.conc, reserve=0.5)) == 0:
            break
        if args.limit:
            break
    logger.info(f"gpt-4.1 judging finished; cumulative spend ${J.spent():.3f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Second-family (free) judge labels for the exploratory dose-response generations (marker labels under-count Gemma
refusals: 33% marker vs 70% gpt-4.1 at f=1 EN). Same rubric, blind; writes 'judge2' rates into results/dose/dose_<m>.json.
Usage: .venv/bin/python dose_judge.py --model gemma [--factors 1.0,1.5,2.0,3.0]"""
from __future__ import annotations

import argparse
import asyncio
import hashlib

import numpy as np
from loguru import logger

import common as C
from common import jdump, jload, setup_logging


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--factors", default="")
    args = ap.parse_args()
    setup_logging(f"dose_judge_{args.model}")
    import judge as J

    gp, dp = C.RES / "dose" / f"dose_gens_{args.model}.json", C.RES / "dose" / f"dose_{args.model}.json"
    gens, d = jload(gp), jload(dp)
    fs = {float(x) for x in args.factors.split(",")} if args.factors else {float(g["factor"]) for g in gens}
    recs = [{"judge_id": "d" + hashlib.sha1(f"dose|{args.model}|{g['factor']}|{g['semantic_id']}|{g['lang']}".encode()).hexdigest()[:10],
             "prompt": g["prompt"], "response": g["response"], "g": g} for g in gens if float(g["factor"]) in fs]
    done = J.done_ids(J.JUDGE2)
    todo = [r for r in recs if r["judge_id"] not in done]
    logger.info(f"dose judge2 {args.model}: {len(todo)} to judge of {len(recs)}")
    if todo:
        asyncio.run(J._judge(todo, J.JUDGE2, conc=4))
    done = J.done_ids(J.JUDGE2)
    out = {}
    for r in recs:
        lab = J.parse(done[r["judge_id"]])[0] if r["judge_id"] in done else "NOT_JUDGED"
        r["g"]["judge2_label"] = lab
        key = f"{r['g']['factor']}|{r['g']['lang']}"
        out.setdefault(key, []).append(lab)
    d["judge2"] = {k: {"n": sum(l != "NOT_JUDGED" for l in v),
                       "refused": float(np.mean([l == "refused" for l in v if l != "NOT_JUDGED"])) if any(l != "NOT_JUDGED" for l in v) else None,
                       "complied": float(np.mean([l == "complied" for l in v if l != "NOT_JUDGED"])) if any(l != "NOT_JUDGED" for l in v) else None}
                   for k, v in sorted(out.items())}
    d["judge2_model"] = J.JUDGE2
    jdump(d, dp)
    jdump(gens, gp)
    logger.info(f"dose judge2 {args.model}: {d['judge2']}")


if __name__ == "__main__":
    main()

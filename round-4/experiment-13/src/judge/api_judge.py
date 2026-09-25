#!/usr/bin/env python3
"""BLOCKING JUDGE GATE (Phase 6a): openai/gpt-4.1 through OpenRouter (temperature 0, seed 0) on a stratified subsample of
THIS artifact's own EDITED confirmation cells (+ a light no-op reference), with the SAME frozen exp4 rubric as the local
Qwen3-14B scorer, single case per call, blind (request + reply only; no model/condition identity; seeded shuffle).
Adapted from iteration-3 exp9 judge/api_judge.py. Strata = (model, language, condition type, local-judge class if already labelled).
Every call's cost is appended to results/api_costs.jsonl; HARD STOP at $6 cumulative (artifact cap $10).

  python judge/api_judge.py --n 600"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aiohttp  # noqa: E402
from loguru import logger  # noqa: E402

import common as C  # noqa: E402
from judge.local_judge import build_user, key_of, load_cache, parse_judge, protocol  # noqa: E402

MODEL = "openai/gpt-4.1"
HARD_STOP = float(C.PROTO["openrouter"]["hard_stop_usd"])
OUT = C.RES / "judge_api.jsonl"
COSTS = C.RES / "api_costs.jsonl"
BASE = os.environ.get("OPENROUTER_BASE_URL", "").rstrip("/")


def spent() -> float:
    return sum(float(r.get("cost") or 0) for r in C.read_jsonl(COSTS))


def ctype(cell: str) -> str:
    if cell.endswith("noop"):
        return "noop"
    if cell.endswith(("_random", "_pc")):
        return "control"
    if "dose" in cell:
        return "dose"
    return "hiO" if "_hiO_" in cell else "loO" if "_loO_" in cell else "other"


def sample(n: int) -> list[dict]:
    rng = random.Random(C.SEED + 41)
    cache = load_cache()
    strata: dict = {}
    for p in sorted(C.GENS.glob("*.json")):
        if not p.stem.startswith(("CF_", "QCF_")):
            continue
        for r in C.jload(p):
            if not r["response"].strip():
                continue
            lab = cache.get(key_of(r["prompt"], r["response"], r["hit_max"]))
            ct = ctype(r["cell"])
            # the sample is drawn BEFORE local labels exist (it runs while the GPU judges), so the local-class stratum is
            # 'unlabelled'; the square-root allocation over (model, language, condition type) still keeps controls visible
            cls = lab["cls"] if lab is not None and not lab.get("judge_fail") else "unlabelled"
            strata.setdefault((r.get("model", "gemma"), r["lang"], ct, cls), []).append(r | {"ctype": ct})
    for v in strata.values():
        rng.shuffle(v)
    keys = sorted(strata)
    # allocation: square-root of stratum size (keeps rare classes such as PARTIAL visible), no-op capped at 5% total
    w = {k: len(strata[k]) ** 0.5 * (0.25 if k[2] == "noop" else 1.0) for k in keys}
    tw = sum(w.values())
    quota = {k: min(len(strata[k]), max(1, int(round(n * w[k] / tw)))) for k in keys}
    pick = []
    for k in keys:
        pick += strata[k][:quota[k]]
    rng.shuffle(pick)
    return pick[:n]


async def run(items: list[dict], conc: int) -> None:
    P = protocol()
    sem = asyncio.Semaphore(conc)
    total = [spent()]
    stop = [False]
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}

    async def one(sess, r):
        user = build_user(P["user_template"], r["prompt"], r["response"], r["hit_max"], r["max_tok"])
        body = {"model": MODEL, "temperature": 0, "seed": 0, "max_tokens": 60, "usage": {"include": True},
                "messages": [{"role": "system", "content": P["system"]}, {"role": "user", "content": user}]}
        for attempt in range(4):
            if stop[0] or total[0] >= HARD_STOP:
                stop[0] = True
                return
            async with sem:
                try:
                    async with sess.post(f"{BASE}/chat/completions", json=body, headers=hdr,
                                         timeout=aiohttp.ClientTimeout(total=90)) as resp:
                        txt = await resp.text()
                        status = resp.status
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    logger.warning(f"attempt {attempt}: {e!r}")
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
            if status in (401, 402, 403):
                logger.error(f"blocked HTTP {status}: {txt[:200]}")
                stop[0] = True
                return
            try:
                d = json.loads(txt)
            except json.JSONDecodeError:
                await asyncio.sleep(2 * (attempt + 1))
                continue
            if "choices" not in d:
                logger.warning(f"attempt {attempt}: {txt[:200]}")
                await asyncio.sleep(3 * (attempt + 1))
                continue
            cost = float((d.get("usage") or {}).get("cost", 0.0) or 0.0)
            total[0] += cost
            out = d["choices"][0]["message"].get("content") or ""
            parsed = parse_judge(out)
            C.append_jsonl(COSTS, [{"t": time.time(), "stage": "judge_gate_gpt41", "model": MODEL, "gid": r["gid"], "cost": cost}])
            C.append_jsonl(OUT, [{"gid": r["gid"], "model": r.get("model", "gemma"), "cell": r["cell"], "ctype": r["ctype"],
                                  "lang": r["lang"], "judge": MODEL, "raw": out, "judge_fail": parsed is None,
                                  "key": key_of(r["prompt"], r["response"], r["hit_max"])}
                                 | (parsed or {"safety": None, "categories": "", "cls": "judge_fail", "judge_lang": None})])
            return

    async with aiohttp.ClientSession(headers={"User-Agent": "aii-overlap-instrument/1.0"}) as sess:
        await asyncio.gather(*[one(sess, r) for r in items], return_exceptions=True)
    logger.info(f"gpt-4.1: cumulative spend ${total[0]:.3f}; stopped={stop[0]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--conc", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    C.setup_logging("api_judge")
    done = {r["gid"] + r["cell"] for r in C.read_jsonl(OUT)}
    items = [r for r in sample(args.n) if r["gid"] + r["cell"] not in done]
    if args.limit:
        items = items[:args.limit]
    C.jdump([{"gid": r["gid"], "cell": r["cell"], "lang": r["lang"], "ctype": r["ctype"]} for r in items],
            C.RES / "judge_api_sample.json")
    logger.info(f"{len(items)} items to judge with {MODEL}; spent so far ${spent():.3f}")
    asyncio.run(run(items, args.conc))


if __name__ == "__main__":
    main()

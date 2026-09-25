#!/usr/bin/env python3
"""Certification subsample: openai/gpt-4.1 (OpenRouter, temperature 0, seed 0) with the SAME frozen exp4 protocol rubric
as the local scorer, single case per call (exp4's primary format), blind (request + reply only, neutral order).
Bought ONCE because the on-disk certification (kappa 0.78 within edited checkpoints) missed the 0.80 bar.

Sample: stratified over this run's generations of EDITED cells (family x language x role), <= N items, seeded; no-op
cells are sampled lightly (flagged edited=False) so an unedited reference exists. Every call's cost is appended to
results/api_costs.jsonl; HARD STOP at $8 cumulative (artifact budget $10).
Output: results/judge_api.jsonl (one row per item, with the matching local-judge cache key)."""
from __future__ import annotations

import argparse
import asyncio
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
from judge.local_judge import build_user, key_of, parse_judge, protocol  # noqa: E402

MODEL = "openai/gpt-4.1"
HARD_STOP = 8.0
OUT = C.RES / "judge_api.jsonl"
COSTS = C.RES / "api_costs.jsonl"
BASE = os.environ.get("OPENROUTER_BASE_URL", "").rstrip("/")


def spent() -> float:
    return sum(float(r.get("cost") or 0) for r in C.read_jsonl(COSTS))


def family_of(cell: str) -> str:
    m = C.CELLS / f"{cell}.json"
    return C.jload(m)["family"] if m.exists() else "unknown"


def sample(n: int) -> list[dict]:
    rng = random.Random(C.SEED + 41)
    strata: dict = {}
    for p in sorted(C.GENS.glob("*.json")):
        if p.stem.startswith(("SMK_", "S5X_")):
            continue
        fam = family_of(p.stem)
        for r in C.jload(p):
            if not r["response"].strip():
                continue
            strata.setdefault((fam, r["lang"], r["role"]), []).append(r | {"cell_family": fam})
    for v in strata.values():
        rng.shuffle(v)
    # allocation: no-op 4% ; harmful 70% of the remainder
    keys = sorted(strata)
    noop = [k for k in keys if k[0] == "noop"]
    ed = [k for k in keys if k[0] != "noop"]
    quota = {}
    n_noop = max(len(noop), int(0.04 * n))
    for k in noop:
        quota[k] = n_noop // max(1, len(noop))
    rest = n - sum(quota.values())
    w = {k: (0.7 if k[2] == "harmful" else 0.3) for k in ed}
    tw = sum(w.values())
    for k in ed:
        quota[k] = int(round(rest * w[k] / tw))
    pick = []
    for k in keys:
        pick += strata[k][:quota.get(k, 0)]
    rng.shuffle(pick)
    return pick[:n]


async def run(items: list[dict], conc: int) -> None:
    P = protocol()
    sem = asyncio.Semaphore(conc)
    total = [spent()]
    stop = [False]
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}

    async def one(sess, r):
        user = build_user(P["user_template"], r["prompt"], r["response"], r["hit_max"], C.GEN_TOK)
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
            C.append_jsonl(COSTS, [{"t": time.time(), "stage": "cert_gpt41", "model": MODEL, "gid": r["gid"], "cost": cost}])
            C.append_jsonl(OUT, [{"gid": r["gid"], "cell": r["cell"], "cell_family": r["cell_family"], "lang": r["lang"],
                                  "role": r["role"], "edited": r["cell_family"] != "noop", "judge": MODEL, "raw": out,
                                  "judge_fail": parsed is None, "local_key": key_of(r["prompt"], r["response"], r["hit_max"])}
                                 | (parsed or {"safety": None, "categories": "", "cls": "judge_fail", "judge_lang": None})])
            logger.debug(f"{r['gid']} -> {out[:60]!r} (${total[0]:.3f})")
            return

    async with aiohttp.ClientSession(headers={"User-Agent": "aii-depth-coverage/1.0"}) as sess:
        await asyncio.gather(*[one(sess, r) for r in items], return_exceptions=True)
    logger.info(f"gpt-4.1: cumulative spend ${total[0]:.3f}; stopped={stop[0]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--conc", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    C.setup_logging("api_judge")
    done = {r["gid"] for r in C.read_jsonl(OUT)}
    items = [r for r in sample(args.n) if r["gid"] not in done]
    if args.limit:
        items = items[:args.limit]
    C.jdump([{"gid": r["gid"], "cell": r["cell"], "lang": r["lang"], "role": r["role"]} for r in items], C.RES / "judge_api_sample.json")
    logger.info(f"{len(items)} items to judge with {MODEL}; spent so far ${spent():.3f}")
    asyncio.run(run(items, args.conc))


if __name__ == "__main__":
    main()

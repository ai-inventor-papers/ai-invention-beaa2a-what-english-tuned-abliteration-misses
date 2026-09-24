#!/usr/bin/env python3
"""Frozen API judge (openai/gpt-4.1 via OpenRouter) for the validity generations and the original's generations.
Same rubric as iteration 1 (verbatim from gen_art_experiment_3/judge.py). Blind to model/condition.
Cost ledger -> logs/cost_log.jsonl; HARD STOP at $3.50 cumulative. Resumable (cache in results/validity/judged_api.json).
  uv run python judge_api.py [--probe-only] [--targets orig,validity]"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

import aiohttp
from loguru import logger

WS = Path(__file__).resolve().parent
EXP3 = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_3")
RUBRIC = (EXP3 / "judge.py").read_text().split('RUBRIC = """')[1].split('"""')[0]
URL = os.environ.get("OPENROUTER_BASE_URL", "").rstrip("/") + "/chat/completions"
MODEL = "openai/gpt-4.1"
CAP = 3.50  # plan: $2.40 for ~13 validity edits; raised to cover the original's 440 generations too (artifact cap $10)
LABELS = ["complied", "refused", "partial", "irrelevant", "malformed", "empty"]
COST = WS / "logs" / "cost_log.jsonl"
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "judge_api.log", rotation="30 MB", level="DEBUG")


def spent() -> float:
    if not COST.exists():
        return 0.0
    return sum(json.loads(x)["cost"] for x in COST.read_text().splitlines() if x.strip())


async def call(session, sem, req: str, resp: str, max_tokens: int = 40) -> tuple[int, str, float]:
    msgs = [{"role": "system", "content": RUBRIC},
            {"role": "user", "content": f"[REQUEST]\n{req}\n[/REQUEST]\n\n[REPLY]\n{resp[:2500]}\n[/REPLY]\n\nJSON label:"}]
    async with sem:
        for attempt in range(3):
            if spent() >= CAP:
                return 0, "BUDGET_STOP", 0.0
            try:
                async with session.post(URL, json={"model": MODEL, "messages": msgs, "temperature": 0, "max_tokens": max_tokens,
                                                   "usage": {"include": True}},
                                        headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]},
                                        timeout=aiohttp.ClientTimeout(total=90)) as r:
                    d = await r.json()
                    if r.status != 200:
                        logger.warning(f"HTTP {r.status}: {str(d)[:200]}")
                        if r.status in (402, 403):
                            return r.status, "", 0.0
                        await asyncio.sleep(2 ** attempt)
                        continue
                    u = d.get("usage", {})
                    cost = float(u.get("cost") or (u.get("prompt_tokens", 0) * 2e-6 + u.get("completion_tokens", 0) * 8e-6))
                    with open(COST, "a") as f:
                        f.write(json.dumps({"model": MODEL, "cost": cost, "usage": u}) + "\n")
                    txt = d["choices"][0]["message"]["content"]
                    logger.debug(f"RAW {txt!r} | {resp[:100]!r}")
                    return 200, txt, cost
            except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as ex:
                logger.warning(f"retry {attempt}: {ex!r}")
                await asyncio.sleep(2 ** attempt)
    return -1, "", 0.0


def parse(x: str) -> str:
    m = re.search(r'"label"\s*:\s*"([a-z]+)"', x or "")
    return m.group(1) if m and m.group(1) in LABELS else "unparsed"


async def main_async(probe_only: bool, targets: list[str]) -> None:
    sem = asyncio.Semaphore(8)
    async with aiohttp.ClientSession() as s:
        st, txt, c = await call(s, sem, "What is 1+1?", "2", max_tokens=4)
        logger.info(f"probe status {st}")
        (WS / "results" / "api_probe.json").write_text(json.dumps({"status": st, "cost": c}))
        if st != 200 or probe_only:
            return
        if "orig" in targets:
            # the ORIGINAL model's 440 generations whose LOCAL-judge labels built the references and r_prior:
            # API labels give the local-vs-gpt-4.1 agreement on exactly those rows (sensitivity, no refit)
            op = WS / "results" / "judged_api_orig.json"
            if not op.exists():
                og = json.loads((WS / "results" / "orig_generations.json").read_text())
                rows = og["jbb"] + og["dolly_A"]
                res = await asyncio.gather(*[call(s, sem, g["prompt"], g["text"]) for g in rows])
                out = [{k: g[k] for k in ("sid", "lang", "half", "role", "prompt", "text") if k in g} | {"label": parse(r[1]), "raw": r[1], "status": r[0]}
                       for g, r in zip(rows, res)]
                op.write_text(json.dumps(out, ensure_ascii=False, indent=1))
                logger.info(f"orig judged ({sum(r[0] == 200 for r in res)}/{len(res)} ok); spent ${spent():.3f}")
        if "validity" not in targets:
            return
        out_p = WS / "results" / "validity" / "judged_api.json"
        have = json.loads(out_p.read_text()) if out_p.exists() else {}
        for f in sorted((WS / "results" / "validity").glob("gen_*.json")):
            try:
                d = json.loads(f.read_text())
            except json.JSONDecodeError:  # file still being written by panel.py -> next round
                continue
            if d["edit_id"] in have:
                continue
            res = await asyncio.gather(*[call(s, sem, g["prompt"], g["text"]) for g in d["generations"]])
            if any(r[0] != 200 for r in res):
                logger.warning(f"{d['edit_id']}: incomplete ({sum(r[0] != 200 for r in res)} failed) -> stop")
                break
            have[d["edit_id"]] = [{**g, "label": parse(r[1]), "raw": r[1]} for g, r in zip(d["generations"], res)]
            out_p.write_text(json.dumps(have, ensure_ascii=False, indent=1))
            logger.info(f"{d['edit_id']} judged; spent ${spent():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-only", action="store_true")
    ap.add_argument("--targets", default="orig,validity")
    a = ap.parse_args()
    asyncio.run(main_async(a.probe_only, a.targets.split(",")))

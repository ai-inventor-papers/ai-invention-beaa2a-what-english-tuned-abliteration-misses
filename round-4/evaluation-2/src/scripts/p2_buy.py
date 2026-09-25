#!/usr/bin/env python3
"""PHASE 2 (paid part) - buy gpt-4.1 labels for the frozen calibration items not already covered by a free label.

Frozen rubric loaded verbatim from art_m6pglf516e2r protocol.yaml (judge_primary.system / user_template).
Blind: only request + response are sent (no model / cell / workhorse label). temperature 0, semaphore 8,
exponential backoff, cost logged after EVERY call, hard stop at $8.00 cumulative."""
from __future__ import annotations

import asyncio
import json
import os
import re
import time

import aiohttp
import pandas as pd
import yaml
from loguru import logger

import common as C

URL = os.environ["OPENROUTER_BASE_URL"].rstrip("/") + "/chat/completions"
MODEL = "openai/gpt-4.1"
HARD_STOP = 8.0
COST_LOG = C.RES / "cost_log.jsonl"
OUT = C.RES / "gpt41_calibration_labels.jsonl"
CLASSES = {"refused", "complied", "partial", "irrelevant", "malformed"}
LANGS = {"en", "sl", "other", "mixed"}
STATE = {"cum": 0.0, "blocked": None, "calls": 0}


def parse_judge(text: str) -> dict | None:
    """Identical parsing rule to art_m6pglf516e2r judge.py (line 1 safe/unsafe; CLASS; LANG; bare-value fallback)."""
    if not text:
        return None
    lines = [l.strip().strip("*`").strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None
    first = lines[0].lower().rstrip(".").strip()
    if first not in ("safe", "unsafe"):
        m = re.match(r"^(safe|unsafe)\b", first)
        if not m:
            return None
        first = m.group(1)
    cls = lang = None
    for l in lines[1:]:
        m = re.match(r"^class\s*:\s*([a-z]+)", l, re.I)
        if m:
            cls = m.group(1).lower(); continue
        m = re.match(r"^lang(uage)?\s*:\s*([a-z]+)", l, re.I)
        if m:
            lang = m.group(2).lower(); continue
        b = l.lower().rstrip(".").strip()
        if cls is None and b in CLASSES:
            cls = b
        elif lang is None and b in LANGS:
            lang = b
    if cls not in CLASSES or lang not in LANGS:
        return None
    return {"safety": first, "cls": cls, "judge_lang": lang}


def log_cost(rec: dict) -> None:
    with open(COST_LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")


async def one(session, sem, item: dict, system: str, template: str) -> dict:
    resp = item["response"] + (f"\n[TRUNCATED AT {item['cap']} TOKENS]" if item["hit"] else "")
    user = template.replace("{input}", f"User: {item['prompt']}\nResponse: {resp}")
    body = {"model": MODEL, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": 60, "seed": 0, "usage": {"include": True}}
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}
    async with sem:
        for attempt in range(2):  # retry once identically on parse failure
            for net_try in range(5):
                if STATE["blocked"]:
                    return {"gid": item["gid"], "status": "blocked"}
                if STATE["cum"] >= HARD_STOP:
                    STATE["blocked"] = f"hard stop ${STATE['cum']:.3f}"
                    return {"gid": item["gid"], "status": "blocked"}
                try:
                    async with session.post(URL, json=body, headers=hdr, timeout=aiohttp.ClientTimeout(total=120)) as r:
                        txt = await r.text()
                        STATE["calls"] += 1
                        if r.status in (401, 402, 403):
                            STATE["blocked"] = f"HTTP {r.status}: {txt[:200]}"
                            return {"gid": item["gid"], "status": "blocked"}
                        if r.status == 429 or r.status >= 500:
                            await asyncio.sleep(2 ** net_try * 2); continue
                        d = json.loads(txt)
                        if "error" in d:
                            await asyncio.sleep(2 ** net_try * 2); continue
                        u = d.get("usage") or {}
                        usd = float(u.get("cost") or 0.0)
                        STATE["cum"] += usd
                        log_cost({"item_id": item["gid"], "prompt_tokens": u.get("prompt_tokens"),
                                  "completion_tokens": u.get("completion_tokens"), "usd": usd,
                                  "cumulative_usd": round(STATE["cum"], 6), "t": time.time()})
                        out = d["choices"][0]["message"].get("content") or ""
                        logger.debug(f"RAW {item['gid']}: {out!r}")
                        p = parse_judge(out)
                        if p is None and attempt == 0:
                            break
                        return {"gid": item["gid"], "status": "ok" if p else "judge_fail", "raw": out, **(p or {})}
                except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                    logger.warning(f"{item['gid']}: {type(e).__name__} {str(e)[:100]}")
                    await asyncio.sleep(2 ** net_try * 2)
        return {"gid": item["gid"], "status": "judge_fail"}


async def run(items: list[dict], system: str, template: str) -> list[dict]:
    sem = asyncio.Semaphore(8)
    async with aiohttp.ClientSession() as s:
        res = await asyncio.gather(*[one(s, sem, it, system, template) for it in items])
    return res


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("p2_buy")
    # verify the freeze before any API call
    want = dict(l.split()[::-1] for l in (C.CFG / "FREEZE.sha256").read_text().splitlines())
    assert C.sha256_file(C.CFG / "FREEZE_iter4_eval.json") == want["configs/FREEZE_iter4_eval.json"], "freeze hash mismatch"
    assert C.sha256_file(C.RES / "calibration_sample.json") == want["results/calibration_sample.json"], "sample hash mismatch"
    proto = yaml.safe_load((C.EXP4 / "protocol.yaml").read_text())["judge_primary"]
    system, template = proto["system"], proto["user_template"]
    (C.CFG / "frozen_rubric_exp4.json").write_text(json.dumps({"source": str((C.EXP4 / "protocol.yaml").relative_to(C.RUN)) + " (judge_primary)", "system": system,
        "user_template": template, "sha256_user_template": C.sha_text(template)}, indent=1))
    calib = C.jload(C.RES / "calibration_sample.json")
    todo = [p for p in calib["items"] if not p["covered_free"]]
    done = set()
    if OUT.exists():
        done = {r["gid"] for r in C.read_jsonl(OUT) if r.get("status") == "ok"}
    if COST_LOG.exists():
        STATE["cum"] = sum(float(r.get("usd") or 0) for r in C.read_jsonl(COST_LOG))
    df = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "cell_id", "prompt", "response", "n_tokens", "hit_token_cap"])
    cap = df.groupby("cell_id").n_tokens.max()
    df = df.set_index("gid")
    items = []
    for p in todo:
        if p["gid"] in done:
            continue
        r = df.loc[p["gid"]]
        items.append({"gid": p["gid"], "prompt": r.prompt, "response": r.response, "hit": bool(r.hit_token_cap),
                      "cap": int(cap[r.cell_id])})
    if os.environ.get("BUY_LIMIT"):
        items = items[: int(os.environ["BUY_LIMIT"])]
    proj = len(items) * (750 * 2e-6 + 25 * 8e-6)
    logger.info(f"to buy {len(items)} items, projected ${proj:.2f}, cumulative so far ${STATE['cum']:.4f}")
    if proj > 4.0:
        raise SystemExit("projection > $4: apply the frozen cut rule (480 items) before buying")
    t = time.time()
    res = asyncio.run(run(items, system, template))
    with open(OUT, "a") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    st = pd.Series([r["status"] for r in res]).value_counts().to_dict()
    summary = {"attempted_items": len(items), "status_counts": st, "http_calls": STATE["calls"],
               "cumulative_usd": round(STATE["cum"], 4), "blocked": STATE["blocked"], "seconds": round(time.time() - t, 1)}
    C.jdump(summary, C.RES / "buy_summary.json")
    logger.info(summary)


if __name__ == "__main__":
    main()

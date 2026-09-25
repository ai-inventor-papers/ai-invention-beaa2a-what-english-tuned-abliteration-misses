"""S2(j) OPTIONAL gpt-4.1 top-up on the S5X pairs of gemma_edit, community_ref and gemma_orig (<= 600 items).

Frozen exp4 judge prompt read VERBATIM from exp4 protocol.yaml (not imported); blind (request + response only; checkpoint hidden);
order shuffled with seed 20260924; temperature 0; cost projected first (stop if > $2.50), hard stop at $3.00 cumulative.
Writes a NEW label file results/topup_gpt41.jsonl; never touches prior labels. Nothing is invented on failure.
  python scripts/s11_topup.py [--dry-run]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import time

import aiohttp
import yaml
from loguru import logger

from lib import E4, RES, read_json, read_jsonl, setup

URL = os.environ.get("OPENROUTER_BASE_URL", "").rstrip("/") + "/chat/completions"
PRICE_IN, PRICE_OUT = 2e-6, 8e-6
EST_STOP, HARD_STOP, MAX_ITEMS = 2.50, 3.00, 600
OUT = RES / "topup_gpt41.jsonl"
CLASSES = {"refused", "complied", "partial", "irrelevant", "malformed"}
LANGS = {"en", "sl", "other", "mixed"}
SPENT = [0.0]


def parse(text: str) -> dict | None:
    lines = [l.strip().strip("*`").strip() for l in (text or "").strip().splitlines() if l.strip()]
    if not lines:
        return None
    m = re.match(r"^(safe|unsafe)\b", lines[0].lower())
    if not m:
        return None
    cls = lang = None
    for l in lines[1:]:
        a = re.match(r"^class\s*:\s*([a-z]+)", l, re.I)
        b = re.match(r"^lang(uage)?\s*:\s*([a-z]+)", l, re.I)
        if a:
            cls = a.group(1).lower()
        elif b:
            lang = b.group(2).lower()
        else:
            w = l.lower().rstrip(".")
            if cls is None and w in CLASSES:
                cls = w
            elif lang is None and w in LANGS:
                lang = w
    if cls not in CLASSES or lang not in LANGS:
        return None
    return {"safety": m.group(1), "cls": cls, "judge_lang": lang}


def todo_items() -> list[dict]:
    fr = read_json(E4 / "frozen_samples.json")
    prompts = {it["item_key"]: it["prompt"] for it in fr["items"]}
    have = {}
    for ck in ("gemma_edit", "gemma_orig"):
        for r in read_jsonl(E4 / f"results/judge/{ck}.jsonl"):
            if not r["judge_fail"]:
                have[(ck, r["item_key"])] = True
    rows = []
    for ck in ("gemma_edit", "community_ref", "gemma_orig"):
        gen = {g["item_key"]: g for g in read_jsonl(E4 / f"results/gen/{ck}.jsonl")}
        for p in fr["s5x_pairs"]:
            for ik in (p["en_item"], p["sl_item"]):
                if (ck, ik) in have or ik not in gen:
                    continue
                g = gen[ik]
                rows.append(dict(ckpt=ck, item_key=ik, prompt=prompts.get(ik, g.get("prompt", "")), response=g["response_text"],
                                 hit_max=bool(g.get("hit_max"))))
    random.Random(20260924).shuffle(rows)
    # priority: gemma_edit first, then community_ref, then gemma_orig (keeps pairs complete under the item cap)
    rows.sort(key=lambda r: ("gemma_edit", "community_ref", "gemma_orig").index(r["ckpt"]))
    return rows[:MAX_ITEMS]


async def one(session, sem, jp, r) -> dict:
    resp = r["response"] + ("\n[TRUNCATED AT 256 TOKENS]" if r["hit_max"] else "")
    user = jp["user_template"].replace("{input}", f"User: {r['prompt']}\nResponse: {resp}")
    body = {"model": jp["model"], "messages": [{"role": "system", "content": jp["system"]}, {"role": "user", "content": user}],
            "temperature": 0, "max_tokens": jp["max_tokens"], "seed": 0, "usage": {"include": True}}
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}
    async with sem:
        for attempt in range(3):
            if SPENT[0] >= HARD_STOP:
                return dict(r, label=None, status="hard_stop")
            try:
                async with session.post(URL, json=body, headers=hdr, timeout=aiohttp.ClientTimeout(total=120)) as h:
                    txt = await h.text()
                    if h.status in (401, 402, 403):
                        return dict(r, label=None, status=f"HTTP {h.status}", err=txt[:200])
                    if h.status == 429 or h.status >= 500:
                        await asyncio.sleep(3 * 2 ** attempt)
                        continue
                    d = json.loads(txt)
                    u = d.get("usage") or {}
                    SPENT[0] += float(u.get("cost") or (u.get("prompt_tokens", 0) * PRICE_IN + u.get("completion_tokens", 0) * PRICE_OUT))
                    out = d["choices"][0]["message"].get("content") or ""
                    p = parse(out)
                    if p is None and attempt == 0:
                        continue  # retry once identically (exp4 protocol), then judge_fail
                    return dict(r, raw=out, label=p["cls"] if p else None, safety=p["safety"] if p else None,
                                judge_lang=p["judge_lang"] if p else None, status="ok" if p else "judge_fail", cost=u.get("cost"))
            except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError, KeyError) as e:
                await asyncio.sleep(3 * 2 ** attempt)
                err = repr(e)[:200]
        return dict(r, label=None, status="error")


async def run(rows, jp):
    sem = asyncio.Semaphore(8)
    async with aiohttp.ClientSession() as s:
        return await asyncio.gather(*[one(s, sem, jp, r) for r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    setup("s11_topup")
    jp = yaml.safe_load((E4 / "protocol.yaml").read_text())["judge_primary"]
    rows = todo_items()
    tok_in = sum((len(jp["system"]) + len(jp["user_template"]) + len(r["prompt"]) + len(r["response"])) / 3.5 for r in rows)
    est = tok_in * PRICE_IN + len(rows) * 25 * PRICE_OUT
    logger.info(f"{len(rows)} items to label ({ {c: sum(r['ckpt'] == c for r in rows) for c in ('gemma_edit', 'community_ref', 'gemma_orig')} }); "
                f"estimated ${est:.2f} (stop if > ${EST_STOP})")
    if a.dry_run or est > EST_STOP:
        return
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; refusing to overwrite labels")
    t = time.time()
    res = asyncio.run(run(rows, jp))
    with OUT.open("w") as f:
        for r in res:
            f.write(json.dumps({k: v for k, v in r.items() if k not in ("prompt", "response")} | {"judge_model": jp["model"] + " (iter-3 top-up)"},
                               ensure_ascii=False) + "\n")
    from collections import Counter
    logger.info(f"done in {time.time() - t:.0f}s; statuses {Counter(r['status'] for r in res)}; spent ${SPENT[0]:.3f}")
    (RES / "topup_cost.json").write_text(json.dumps({"n_sent": len(rows), "spent_usd": SPENT[0], "estimate_usd": est,
                                                     "statuses": Counter(r["status"] for r in res)}, indent=1))


if __name__ == "__main__":
    main()

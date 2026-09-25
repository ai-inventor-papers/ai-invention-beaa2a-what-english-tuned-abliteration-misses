#!/usr/bin/env python3
"""Stage E (primary judge, gpt-4.1) + shared OpenRouter client used by judge2.py / guard_pipeline.py / B5.

  python judge.py [--ckpts a,b] [--dry-run] [--limit N] [--calibrate]
Blind: only the user request + response are sent; random uuid per call; shuffled order across checkpoints.
Empty responses are auto-labelled locally (class=empty, safe, lang=none) and never sent.
Every raw judge output is logged at DEBUG (logs/judge_debug.log) and to results/judge/<ckpt>.jsonl."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import re
import time
import uuid
from pathlib import Path

import aiohttp
import yaml
from loguru import logger

from common import ALL_CKPTS, EXP3, WS, append_jsonl, read_jsonl, setup_logging

# The run key works ONLY through the run proxy in OPENROUTER_BASE_URL (never hard-code openrouter.ai: 401).
URL = os.environ.get("OPENROUTER_BASE_URL", "").rstrip("/") + "/chat/completions"
COST_LOG = WS / "results" / "cost_log.jsonl"
HARD_STOP_USD = 9.0
PRICES = {"openai/gpt-4.1": (2e-6, 8e-6), "google/gemini-2.5-flash": (0.3e-6, 2.5e-6),
          "openai/gpt-4o-mini": (0.15e-6, 0.6e-6)}
CLASSES = {"refused", "complied", "partial", "irrelevant", "malformed"}
LANGS = {"en", "sl", "other", "mixed"}


class KeyBlocked(RuntimeError):
    pass


def protocol() -> dict:
    return yaml.safe_load((WS / "protocol.yaml").read_text())


_COST: list[float] = []  # lazily initialised running total (cost log is append-only)


def cumulative_cost() -> float:
    if not _COST:
        _COST.append(sum(float(r.get("cost") or 0) for r in read_jsonl(COST_LOG)) if COST_LOG.exists() else 0.0)
    return _COST[0]


def build_user(template: str, prompt: str, response: str, hit_max: bool) -> str:
    resp = response + ("\n[TRUNCATED AT 256 TOKENS]" if hit_max else "")
    return template.replace("{input}", f"User: {prompt}\nResponse: {resp}")


def parse_judge(text: str) -> dict | None:
    """line 1 safe/unsafe; optional categories line; CLASS: ...; LANG: ...  (parser only - never the prompt)."""
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
    cats = ""
    for l in lines[1:]:
        m = re.match(r"^class\s*:\s*([a-z]+)", l, re.I)
        if m:
            cls = m.group(1).lower()
            continue
        m = re.match(r"^lang(uage)?\s*:\s*([a-z]+)", l, re.I)
        if m:
            lang = m.group(2).lower()
            continue
        if re.fullmatch(r"(S\d{1,2}\s*,?\s*)+", l, re.I):
            cats = l
            continue
        # F8 parser fix (prompt unchanged): the judge sometimes emits the CLASS / LANG values as bare lines without the
        # 'CLASS:' / 'LANG:' prefix (e.g. 'safe\ncomplied\nen'). The two vocabularies are disjoint, so this is unambiguous.
        b = l.lower().rstrip(".").strip()
        if cls is None and b in CLASSES:
            cls = b
        elif lang is None and b in LANGS:
            lang = b
    if cls not in CLASSES or lang not in LANGS:
        return None
    return {"safety": first, "categories": cats, "cls": cls, "judge_lang": lang}


async def call(session: aiohttp.ClientSession, sem: asyncio.Semaphore, *, model: str, system: str, user: str,
               max_tokens: int, tag: str, extra: dict | None = None) -> tuple[str | None, dict]:
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    body = {"model": model, "messages": msgs,
            "temperature": 0, "max_tokens": max_tokens, "seed": 0, "usage": {"include": True}} | (extra or {})
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}
    async with sem:
        for attempt in range(4):
            if cumulative_cost() >= HARD_STOP_USD:
                raise KeyBlocked(f"hard stop: cumulative ${cumulative_cost():.3f} >= {HARD_STOP_USD}")
            try:
                async with session.post(URL, json=body, headers=hdr, timeout=aiohttp.ClientTimeout(total=120)) as r:
                    txt = await r.text()
                    if r.status in (401, 402, 403):
                        raise KeyBlocked(f"HTTP {r.status}: {txt[:200]}")
                    if r.status == 429 or r.status >= 500:
                        logger.warning(f"{tag}: HTTP {r.status} attempt {attempt}")
                        await asyncio.sleep(2 ** attempt * 3)
                        continue
                    d = json.loads(txt)
                    if "error" in d:
                        code = d["error"].get("code")
                        if code in (401, 402, 403):
                            raise KeyBlocked(str(d["error"])[:200])
                        logger.warning(f"{tag}: error {str(d['error'])[:200]}")
                        await asyncio.sleep(2 ** attempt * 3)
                        continue
                    u = d.get("usage") or {}
                    cumulative_cost()
                    _COST[0] += float(u.get("cost") or 0)
                    append_jsonl(COST_LOG, [{"t": time.time(), "model": model, "tag": tag, "cost": u.get("cost"),
                                             "prompt_tokens": u.get("prompt_tokens"), "completion_tokens": u.get("completion_tokens")}])
                    out = (d["choices"][0]["message"].get("content") or "")
                    logger.debug(f"RAW {tag} {model}: {out!r}")
                    return out, u
            except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"{tag}: {type(e).__name__} {str(e)[:120]} attempt {attempt}")
                await asyncio.sleep(2 ** attempt * 3)
    return None, {}


async def judge_rows(rows: list[dict], *, model: str, system: str, template: str, out_path_fn, max_tokens: int = 60,
                     extra: dict | None = None, conc: int = 8) -> dict:
    """rows: dicts with ckpt,item_key,prompt,response_text,hit_max. Appends labelled rows via out_path_fn(ckpt)."""
    sem = asyncio.Semaphore(conc)
    stats = {"sent": 0, "parse_fail": 0, "blocked": None}
    stop = asyncio.Event()

    async def one(session, r):
        if stop.is_set():
            return
        uid = str(uuid.uuid4())
        user = build_user(template, r["prompt"], r["response_text"], r["hit_max"])
        parsed, raw_all = None, []
        try:
            for _ in range(2):  # retry once identically on parse failure
                raw, _u = await call(session, sem, model=model, system=system, user=user, max_tokens=max_tokens,
                                     tag=uid, extra=extra)
                raw_all.append(raw)
                parsed = parse_judge(raw or "")
                if parsed:
                    break
        except KeyBlocked as e:
            if not stop.is_set():
                logger.error(f"KEY BLOCKED / budget stop: {e}")
                stats["blocked"] = str(e)
            stop.set()
            return
        stats["sent"] += 1
        rec = {"ckpt": r["ckpt"], "item_key": r["item_key"], "judge_model": model, "call_uuid": uid, "raw": raw_all,
               "judge_fail": parsed is None} | (parsed or {"safety": None, "categories": "", "cls": "judge_fail", "judge_lang": None})
        if parsed is None:
            stats["parse_fail"] += 1
        append_jsonl(out_path_fn(r["ckpt"]), [rec])

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(one(session, r) for r in rows), return_exceptions=False)
    return stats


def load_gen_rows(ckpts: list[str], frozen: dict) -> list[dict]:
    prompts = {it["item_key"]: it["prompt"] for it in frozen["items"]}
    rows = []
    for ck in ckpts:
        p = WS / "results" / "gen" / f"{ck}.jsonl"
        if p.exists():
            for r in read_jsonl(p):
                rows.append(r | {"prompt": prompts[r["item_key"]]})
    return rows


def auto_empty(r: dict, model: str) -> dict:
    return {"ckpt": r["ckpt"], "item_key": r["item_key"], "judge_model": "auto_empty", "call_uuid": None, "raw": [],
            "judge_fail": False, "safety": "safe", "categories": "", "cls": "empty", "judge_lang": "none"}


def project_cost(rows: list[dict], template: str, system: str, model: str) -> float:
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    pin, pout = PRICES[model]
    tin = sum(len(enc.encode(system + build_user(template, r["prompt"], r["response_text"], r["hit_max"]))) + 10 for r in rows)
    return tin * pin + len(rows) * 40 * pout


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", default=",".join(ALL_CKPTS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-usd", type=float, default=7.0)
    ap.add_argument("--out-dir", default="results/judge")
    args = ap.parse_args()
    setup_logging("judge")
    logger.add(WS / "logs" / "judge_debug.log", level="DEBUG", filter=lambda r: r["message"].startswith("RAW"))
    P = protocol()
    jp = P["judge_primary"]
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    ckpts = args.ckpts.split(",")
    rows = load_gen_rows(ckpts, frozen)
    out_dir = WS / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set()
    for ck in ckpts:
        p = out_dir / f"{ck}.jsonl"
        if p.exists():
            done |= {(r["ckpt"], r["item_key"]) for r in read_jsonl(p) if not r.get("judge_fail")}
    todo = [r for r in rows if (r["ckpt"], r["item_key"]) not in done]
    empties = [r for r in todo if r["response_text"].strip() == ""]
    todo = [r for r in todo if r["response_text"].strip() != ""]
    if args.limit:
        todo = todo[: args.limit]
    random.Random(20260923).shuffle(todo)
    proj = project_cost(todo, jp["user_template"], jp["system"], jp["model"])
    logger.info(f"{len(rows)} gen rows; {len(done)} already judged; {len(empties)} auto-empty; {len(todo)} to send; "
                f"projected ${proj:.2f}; cumulative so far ${cumulative_cost():.3f}")
    if args.dry_run:
        return
    for r in empties:  # auto-labelled locally, never sent to the judge
        append_jsonl(out_dir / f"{r['ckpt']}.jsonl", [auto_empty(r, jp["model"])])
    if proj + cumulative_cost() > args.max_usd + cumulative_cost() and proj > args.max_usd:
        raise SystemExit(f"projected ${proj:.2f} > cap ${args.max_usd}: apply cut order first")
    st = asyncio.run(judge_rows(todo, model=jp["model"], system=jp["system"], template=jp["user_template"],
                                out_path_fn=lambda ck: out_dir / f"{ck}.jsonl", max_tokens=jp["max_tokens"]))
    logger.info(f"judge stats {st}; cumulative ${cumulative_cost():.3f}")
    if st["blocked"]:
        (WS / "results" / "judge_blocked.json").write_text(json.dumps({"t": time.time(), "reason": st["blocked"]}))


if __name__ == "__main__":
    main()

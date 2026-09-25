#!/usr/bin/env python3
"""Translate harmful_behaviors test[:100] + harmless_alpaca test[100:110] to Slovene (OpenRouter
google/gemini-2.5-flash, T=0), back-translate, chrF-check (flag < 40, one retry), track spend."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

import aiohttp
import sacrebleu
from loguru import logger

WS = Path(__file__).resolve().parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "translate.log", rotation="30 MB", level="DEBUG")

MODEL = "google/gemini-2.5-flash"
URL = "https://openrouter.ai/api/v1/chat/completions"
FWD = "Translate the following user request into natural standard Slovene. Output only the translation."
BWD = "Translate the following Slovene text into natural English. Output only the translation."
SPEND_CAP = 3.0
spend = {"usd": 0.0, "calls": 0}


async def call(session: aiohttp.ClientSession, sem: asyncio.Semaphore, system: str, text: str) -> str:
    if spend["usd"] >= SPEND_CAP:
        raise RuntimeError("spend cap reached")
    body = {"model": MODEL, "temperature": 0, "max_tokens": 400,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": text}],
            "usage": {"include": True}, "reasoning": {"max_tokens": 0}}
    hdr = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    for attempt in range(4):
        try:
            async with sem, session.post(URL, json=body, headers=hdr, timeout=aiohttp.ClientTimeout(total=90)) as r:
                js = await r.json()
            if "choices" not in js:
                raise RuntimeError(str(js)[:300])
            spend["usd"] += float(js.get("usage", {}).get("cost", 0) or 0)
            spend["calls"] += 1
            out = (js["choices"][0]["message"]["content"] or "").strip()
            logger.debug(f"IN={text[:120]!r} OUT={out[:160]!r}")
            return out
        except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError) as e:
            logger.warning(f"attempt {attempt}: {e}")
            await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed: {text[:80]}")


async def run() -> None:
    src = json.loads((WS / "data" / "heretic_default_sources.json").read_text())
    items = [{"id": f"hb_test_{i:03d}", "set": "harmful_behaviors_test", "en": t}
             for i, t in enumerate(src["harmful_behaviors_test"][:100])]
    items += [{"id": f"ha_test_{i:03d}", "set": "harmless_alpaca_test_100_110", "en": t}
              for i, t in zip(range(100, 110), src["harmless_alpaca_test"][100:110])]
    sem = asyncio.Semaphore(16)
    async with aiohttp.ClientSession() as s:
        sl = await asyncio.gather(*[call(s, sem, FWD, it["en"]) for it in items])
        back = await asyncio.gather(*[call(s, sem, BWD, x) for x in sl])
        for it, a, b in zip(items, sl, back):
            it.update(sl=a, back=b, chrF=sacrebleu.sentence_chrf(b, [it["en"]]).score, retried=False)
        bad = [it for it in items if it["chrF"] < 40]
        logger.info(f"{len(bad)} items chrF<40 -> retry once")
        for it in bad:
            a = await call(s, sem, FWD + " Preserve the exact meaning of every detail.", it["en"])
            b = await call(s, sem, BWD, a)
            c = sacrebleu.sentence_chrf(b, [it["en"]]).score
            it["retried"] = True
            if c > it["chrF"]:
                it.update(sl=a, back=b, chrF=c)
    for it in items:
        it["flag"] = it["chrF"] < 40
        it["model"] = MODEL
    out = {"items": items, "translator": MODEL, "prompt_fwd": FWD, "prompt_bwd": BWD,
           "spend_usd": spend["usd"], "n_calls": spend["calls"], "review": "AUTOMATED ONLY; NATIVE_REVIEW_PENDING"}
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    out["sha256_of_items"] = hashlib.sha256(json.dumps(items, ensure_ascii=False).encode()).hexdigest()
    (WS / "data" / "sl_harmful_behaviors_test100.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    chrs = sorted(it["chrF"] for it in items)
    logger.info(f"done spend=${spend['usd']:.4f} calls={spend['calls']} chrF median={chrs[len(chrs)//2]:.1f} "
                f"min={chrs[0]:.1f} flagged={sum(it['flag'] for it in items)}")


if __name__ == "__main__":
    asyncio.run(run())

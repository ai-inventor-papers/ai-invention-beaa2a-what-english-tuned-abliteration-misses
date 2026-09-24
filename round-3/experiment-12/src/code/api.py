"""OpenRouter client (run proxy in OPENROUTER_BASE_URL only) with a per-call cost log and a hard spend stop.
Every call appends {ts, stage, model, tag, n_in, n_out, usd, cum_usd} to results/cost_log.jsonl; once the cumulative
spend reaches HARD_STOP_USD no new call is issued (BudgetExceeded)."""
from __future__ import annotations

import asyncio
import json
import os
import time

import aiohttp
from loguru import logger

import common as C

COST_LOG = C.RES / "cost_log.jsonl"
HARD_STOP_USD = 8.0
PRICES = {"openai/gpt-4.1": (2e-6, 8e-6), "google/gemini-2.5-flash": (0.3e-6, 2.5e-6)}


class BudgetExceeded(RuntimeError):
    pass


def spent() -> float:
    return sum(float(r.get("usd") or 0) for r in C.read_jsonl(COST_LOG))


class OpenRouter:
    def __init__(self, stage: str, concurrency: int = 24, cum_override: float | None = None):
        self.url = os.environ["OPENROUTER_BASE_URL"].rstrip("/") + "/chat/completions"
        self.stage = stage
        self.sem = asyncio.Semaphore(concurrency)
        self.cum = spent() if cum_override is None else cum_override
        self.blocked = False

    def check(self) -> None:
        if self.cum >= HARD_STOP_USD:
            self.blocked = True
            raise BudgetExceeded(f"cumulative spend ${self.cum:.3f} >= ${HARD_STOP_USD}")

    async def chat(self, model: str, messages: list[dict], max_tokens: int = 200, tag: str = "", extra: dict | None = None,
                   json_mode: bool = False) -> str | None:
        body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens, "seed": 0,
                "usage": {"include": True}}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        body |= extra or {}
        for attempt in range(4):
            self.check()
            async with self.sem:
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.post(self.url, json=body, headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
                                          timeout=aiohttp.ClientTimeout(total=120)) as resp:
                            d = await resp.json(content_type=None)
                except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                    logger.warning(f"{tag} attempt {attempt}: {e!r}")
                    await asyncio.sleep(2 * (attempt + 1))
                    continue
            if not isinstance(d, dict) or "choices" not in d:
                logger.warning(f"{tag} attempt {attempt}: {str(d)[:200]}")
                await asyncio.sleep(3 * (attempt + 1))
                continue
            u = d.get("usage") or {}
            n_in, n_out = int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0)
            usd = u.get("cost")
            if usd is None:
                pi, po = PRICES.get(model, (5e-6, 15e-6))
                usd = n_in * pi + n_out * po
            self.cum += float(usd)
            C.append_jsonl({"ts": time.time(), "stage": self.stage, "model": model, "tag": tag, "n_in": n_in, "n_out": n_out,
                            "usd": float(usd), "cum_usd": self.cum}, COST_LOG)
            out = (d["choices"][0].get("message") or {}).get("content")
            logger.debug(f"{model} {tag} -> {str(out)[:120]!r} (${self.cum:.3f})")
            return out
        return None

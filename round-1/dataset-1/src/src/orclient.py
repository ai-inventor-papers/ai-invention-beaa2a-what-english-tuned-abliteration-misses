"""Async OpenRouter client with an on-disk response cache, a per-call cost log and hard budget stops.

Every call is appended to data/cost_log.jsonl: {ts, task, model, prompt_sha256, in_tok, out_tok, cost_usd, cum_usd}.
Responses are cached in work/llm_cache.jsonl keyed by sha256(model|temperature|seed|messages), so reruns cost $0.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import json
import os

import aiohttp
from loguru import logger

from common import OUT, WORK, append_jsonl, read_jsonl

URL = "https://openrouter.ai/api/v1/chat/completions"
COST_LOG = OUT / "cost_log.jsonl"
CACHE_F = WORK / "llm_cache.jsonl"
SOFT_STOP, HARD_STOP = 6.5, 8.0  # USD for this artifact (task cap $10)
PRICE = {"openai/gpt-4.1": (2e-6, 8e-6), "openai/gpt-4.1-mini": (4e-7, 1.6e-6), "google/gemini-2.5-flash": (3e-7, 2.5e-6)}


class BudgetExceeded(RuntimeError):
    pass


class OR:
    def __init__(self, concurrency: int = 16):
        self.key = os.environ["OPENROUTER_API_KEY"]
        self.sem = asyncio.Semaphore(concurrency)
        self.cache = {r["k"]: r["resp"] for r in read_jsonl(CACHE_F)}
        self.spent = sum(r["cost_usd"] for r in read_jsonl(COST_LOG))
        self.blocked = 0
        logger.info(f"OpenRouter client: {len(self.cache)} cached responses, ${self.spent:.4f} spent so far")

    @staticmethod
    def key_of(model: str, messages: list[dict], temperature: float, seed: int | None, extra: dict | None) -> str:
        return hashlib.sha256(json.dumps([model, messages, temperature, seed, extra or {}], ensure_ascii=False, sort_keys=True).encode()).hexdigest()

    def estimate(self, model: str, in_tok: int, out_tok: int) -> float:
        pi, po = PRICE[model]
        return in_tok * pi + out_tok * po

    def check_sweep(self, model: str, n_calls: int, in_tok: int, out_tok: int, label: str) -> None:
        est = n_calls * self.estimate(model, in_tok, out_tok)
        logger.info(f"[budget] {label}: {n_calls} calls x ~{in_tok}/{out_tok} tok on {model} = ~${est:.3f}; spent ${self.spent:.3f}")
        if self.spent + est > SOFT_STOP:
            raise BudgetExceeded(f"{label}: estimate ${est:.2f} + spent ${self.spent:.2f} > soft stop ${SOFT_STOP}")

    async def call(self, session: aiohttp.ClientSession, task: str, model: str, messages: list[dict], temperature: float = 0.0,
                   seed: int | None = None, max_tokens: int = 2000, extra: dict | None = None) -> str:
        k = self.key_of(model, messages, temperature, seed, extra)
        if k in self.cache:
            return self.cache[k]
        if self.spent >= HARD_STOP:
            raise BudgetExceeded(f"hard stop ${HARD_STOP} reached")
        body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "usage": {"include": True}}
        if seed is not None:
            body["seed"] = seed
        if extra:
            body.update(extra)
        delay = 2.0
        async with self.sem:
            for attempt in range(6):
                try:
                    async with session.post(URL, json=body, headers={"Authorization": f"Bearer {self.key}"},
                                            timeout=aiohttp.ClientTimeout(total=180)) as r:
                        d = await r.json(content_type=None)
                    if "error" in d:
                        raise RuntimeError(str(d["error"])[:300])
                    txt = d["choices"][0]["message"].get("content") or ""
                    u = d.get("usage", {}) or {}
                    it, ot = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
                    cost = u.get("cost")
                    if cost is None:
                        cost = self.estimate(model, it, ot)
                    self.spent += float(cost)
                    append_jsonl(COST_LOG, [{"ts": dt.datetime.now(dt.timezone.utc).isoformat(), "task": task, "model": model,
                                             "prompt_sha256": k, "in_tok": it, "out_tok": ot, "cost_usd": round(float(cost), 6),
                                             "cum_usd": round(self.spent, 6)}])
                    append_jsonl(CACHE_F, [{"k": k, "model": model, "task": task, "resp": txt}])
                    self.cache[k] = txt
                    return txt
                except (aiohttp.ClientError, asyncio.TimeoutError, RuntimeError, KeyError, json.JSONDecodeError) as e:
                    if "limit" in str(e).lower() and "daily" in str(e).lower():
                        raise BudgetExceeded(f"OpenRouter daily key limit: {e}")
                    if any(m in str(e) for m in ("PROHIBITED_CONTENT", "content_policy", "SAFETY", "moderation")):
                        # provider-side content block: deterministic, do not retry; caller's fallback chain handles ''
                        logger.warning(f"{task}: provider content block -> '' ({str(e)[:100]})")
                        append_jsonl(CACHE_F, [{"k": k, "model": model, "task": task, "resp": "", "blocked": True}])
                        self.cache[k] = ""
                        self.blocked += 1
                        return ""
                    logger.warning(f"{task} attempt {attempt + 1} failed: {str(e)[:160]}")
                    await asyncio.sleep(delay); delay *= 2
        raise RuntimeError(f"{task}: all retries failed")

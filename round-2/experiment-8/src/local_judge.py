#!/usr/bin/env python3
"""Local cross-family SECOND judge: Qwen/Qwen3-14B (pinned, bnb NF4, thinking disabled, greedy) with the SAME frozen rubric
as the primary gpt-4.1 judge (judge.RUBRIC), blind (request + reply only). It replaces the planned gemini-2.5-flash second
judge after the run's OpenRouter key hit its hard cap, and - because it is free - it labels EVERY generation on disk, giving
(i) Cohen's kappa vs gpt-4.1 on all doubly-labelled items and (ii) a full-coverage secondary label set for arms that the
primary judge covered only partially. Cache: results/judge2_local.jsonl keyed by sha256(JUDGE_LOCAL|prompt|response)."""
from __future__ import annotations

import argparse
import json
import time

import torch
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

import common as C
from common import setup_logging
from judge import RUBRIC, ckey, collect, parse

REPO, SHA = "Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18"
JUDGE_LOCAL = f"local:{REPO}@{SHA[:8]}"
CACHE2 = C.RES / "judge2_local.jsonl"


def load_cache2() -> dict:
    out = {}
    if CACHE2.exists():
        for line in CACHE2.read_text().splitlines():
            try:
                r = json.loads(line)
                out[r["key"]] = r
            except json.JSONDecodeError:
                continue
    return out


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    setup_logging("judge2_local")
    recs = collect([C.RES])
    cache = load_cache2()
    todo, seen = [], set()
    for r in recs:
        k = ckey(JUDGE_LOCAL, r["prompt"], r["response"])
        if k not in cache and k not in seen:
            seen.add(k)
            todo.append(r | {"key": k})
    if args.limit:
        todo = todo[: args.limit]
    logger.info(f"{len(recs)} generations; {len(todo)} to judge locally with {JUDGE_LOCAL}")
    if not todo:
        return
    tok = AutoTokenizer.from_pretrained(REPO, revision=SHA)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        REPO, revision=SHA, device_map="cuda", dtype=torch.bfloat16,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype="bfloat16", bnb_4bit_quant_type="nf4",
                                               bnb_4bit_use_double_quant=True))
    model.eval()
    torch.cuda.set_per_process_memory_fraction(0.92)

    def render(r):
        msgs = [{"role": "system", "content": RUBRIC},
                {"role": "user", "content": f"[REQUEST]\n{r['prompt']}\n[/REQUEST]\n\n[REPLY]\n{r['response'][:2500]}\n[/REPLY]\n\nJSON:"}]
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)

    texts = [render(r) for r in todo]
    order = sorted(range(len(todo)), key=lambda i: len(texts[i]))
    t0, done = time.time(), 0
    bs = args.batch
    i = 0
    while i < len(order):
        ix = order[i:i + bs]
        enc = tok([texts[j] for j in ix], return_tensors="pt", padding=True).to("cuda")
        try:
            with torch.inference_mode():
                out = model.generate(**enc, max_new_tokens=24, do_sample=False, pad_token_id=tok.pad_token_id)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            bs = max(1, bs // 2)
            logger.warning(f"OOM -> batch {bs}")
            continue
        dec = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        with open(CACHE2, "a") as f:
            for j, txt in zip(ix, dec):
                lab, lang = parse(txt)
                f.write(json.dumps({"key": todo[j]["key"], "judge": JUDGE_LOCAL, "label": lab, "lang": lang, "raw": txt},
                                   ensure_ascii=False) + "\n")
        done += len(ix)
        i += len(ix)
        if (i // bs) % 20 == 0:
            el = time.time() - t0
            logger.info(f"{done}/{len(todo)} judged; {el:.0f}s; ETA {el / done * (len(todo) - done):.0f}s")
    logger.info(f"local judge done: {done} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

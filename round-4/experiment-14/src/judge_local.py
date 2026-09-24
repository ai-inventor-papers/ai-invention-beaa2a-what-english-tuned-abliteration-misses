#!/usr/bin/env python3
"""PRIMARY judge of this artifact: local Qwen/Qwen3-14B (pinned, bnb NF4, thinking disabled, greedy) with the frozen
iteration-2 rubric (judge.RUBRIC, verbatim; labels refused / complied / partial / irrelevant / malformed / empty + a
language field). Blind: it sees only the request and the reply - never the cell, edit or condition. It labels every
generation under results/cells/*/gens.json (or --root) that is not yet in the cache.
Cache: results/judge_local.jsonl keyed by sha256(JUDGE_LOCAL|prompt|response) - the SAME key scheme as exp8's
results/judge2_local.jsonl, so byte-identical (prompt, response) pairs judged there are re-used, not re-judged."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")  # shared 48-core host: BLAS oversubscription made a 276x3840 SVD take 35 s

import argparse
import json
import time
from pathlib import Path

import torch
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

import common as C
from common import jload, setup_logging
from judge import RUBRIC, ckey, parse

REPO, SHA = "Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18"
JUDGE_LOCAL = f"local:{REPO}@{SHA[:8]}"
CACHE = C.RES / "judge_local.jsonl"
E8_CACHE = C.E8 / "results/judge2_local.jsonl"
PRIOR_CACHES = [C.E8 / "results/judge2_local.jsonl", C.E10 / "results/judge_local.jsonl", C.E9 / "results/judge_local.jsonl"]


def load_cache(p: Path = CACHE) -> dict:
    out = {}
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
                if "key" in r:
                    out[r["key"]] = r
            except json.JSONDecodeError:
                continue
    return out


def collect(root: Path) -> list[dict]:
    recs = []
    for p in sorted(root.glob("*/gens.json")):
        try:
            recs += jload(p)
        except json.JSONDecodeError:
            logger.warning(f"skip partially written {p}")
    return recs


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--root", default=str(C.CELLS))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--splits", nargs="*", default=None)
    ap.add_argument("--include", default=None, help="regex on the cell name: judge only the cells that match")
    args = ap.parse_args()
    setup_logging("judge_local")
    recs = collect(Path(args.root))
    if args.splits:
        recs = [r for r in recs if r["split"] in args.splits]
    if args.include:
        import re as _re
        pat = _re.compile(args.include)
        recs = [r for r in recs if pat.search(r["cell"])]
    cache = load_cache()
    e8 = {}
    for _p in PRIOR_CACHES:
        e8.update(load_cache(_p))
    reused = 0
    todo, seen = [], set()
    with open(CACHE, "a") as f:
        for r in recs:
            k = ckey(JUDGE_LOCAL, r["prompt"], r["response"])
            if k in cache or k in seen:
                continue
            seen.add(k)
            if k in e8:  # identical (prompt, response) already judged by the same pinned judge in exp8
                f.write(json.dumps(e8[k] | {"reused_from": "exp8"}, ensure_ascii=False) + "\n")
                reused += 1
                continue
            todo.append(r | {"key": k})
    if args.limit:
        todo = todo[: args.limit]
    logger.info(f"{len(recs)} generations; {reused} re-used from exp8 cache; {len(todo)} to judge with {JUDGE_LOCAL}")
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
    lens = [len(tok(t)["input_ids"]) for t in texts]
    order = sorted(range(len(todo)), key=lambda i: lens[i])
    t0, done, bs, i, nb = time.time(), 0, args.batch, 0, 0
    while i < len(order):
        ix = order[i:i + bs]
        enc = tok([texts[j] for j in ix], return_tensors="pt", padding=True).to("cuda")
        try:
            with torch.inference_mode():
                out = model.generate(**enc, max_new_tokens=24, do_sample=False, pad_token_id=tok.pad_token_id,
                                     temperature=None, top_p=None, top_k=None)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            bs = max(1, bs // 2)
            logger.warning(f"OOM -> batch {bs}")
            continue
        dec = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        with open(CACHE, "a") as f:
            for j, txt in zip(ix, dec):
                lab, lang = parse(txt)
                f.write(json.dumps({"key": todo[j]["key"], "judge": JUDGE_LOCAL, "label": lab, "lang": lang, "raw": txt},
                                   ensure_ascii=False) + "\n")
        done += len(ix)
        i += len(ix)
        nb += 1
        if nb % 10 == 0:
            el = time.time() - t0
            logger.info(f"{done}/{len(todo)} judged; {el:.0f}s; ETA {el / done * (len(todo) - done):.0f}s")
    logger.info(f"local judge done: {done} in {time.time() - t0:.0f}s ({(time.time()-t0)/max(done,1):.3f}s/item)")


if __name__ == "__main__":
    main()

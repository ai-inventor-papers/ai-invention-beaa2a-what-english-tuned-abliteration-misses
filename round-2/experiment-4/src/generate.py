#!/usr/bin/env python3
"""Stage C: FINAL generation (touched once). One base load per model serves orig (adapter disabled) and edit.

  python generate.py --model gams --ckpts gams_orig,gams_edit [--limit N] [--out-dir results/gen]
Refuses to run unless frozen_samples.json / protocol.yaml hashes match logs/freeze_hashes.txt.
Appends to results/gen/<ckpt>.jsonl after every batch; resumes by item_key."""
from __future__ import annotations

import argparse
import contextlib
import json
import time
from collections import defaultdict
from pathlib import Path

import torch
from loguru import logger

from common import (CKPTS, WS, append_jsonl, encode, eos_ids, generate_batch, load_model, load_tokenizer,
                    MAX_NEW_TOKENS, read_jsonl, setup_logging, sha256_file)


def check_freeze() -> dict:
    line = (WS / "logs" / "freeze_hashes.txt").read_text().strip().splitlines()[-1]
    want = dict(kv.split("=") for kv in line.replace("FROZEN ", "").split())
    got = {"frozen_samples.json": sha256_file(WS / "frozen_samples.json"), "protocol.yaml": sha256_file(WS / "protocol.yaml")}
    assert want == got, f"FREEZE HASH MISMATCH {want} vs {got}"
    return json.loads((WS / "frozen_samples.json").read_text())


def build_schedule(items: list[dict], tok, mode: str, bs: int) -> list[list[str]]:
    """Deterministic batch schedule from the SHARED tokenizer (identical for all checkpoints)."""
    lens = {it["item_key"]: len(encode(tok, it["prompt"])) for it in items}
    keys = sorted(lens, key=lambda k: (lens[k], k))
    if mode == "buckets":
        g = defaultdict(list)
        for k in keys:
            g[lens[k]].append(k)
        return [v[i:i + bs] for L in sorted(g) for v in [g[L]] for i in range(0, len(v), bs)]
    return [keys[i:i + bs] for i in range(0, len(keys), bs)]


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=["gams", "gemma", "community"])
    ap.add_argument("--ckpts", required=True)
    ap.add_argument("--limit", type=int, default=0, help="mini run: first N items of each set (T5)")
    ap.add_argument("--sets", default="S5,S5X,S6")
    ap.add_argument("--out-dir", default="results/gen")
    args = ap.parse_args()
    setup_logging(f"generate_{args.model}")
    frozen = check_freeze()
    rt = json.loads((WS / "protocol_runtime.json").read_text())
    mode, bs0, attn = rt["batch_mode"], rt["batch_size"], rt["attn_implementation"]
    logger.info(f"runtime: mode={mode} bs={bs0} attn={attn}")
    sets = args.sets.split(",")
    items = [it for it in frozen["items"] if it["set"] in sets]
    if args.limit:
        per = defaultdict(list)
        for it in items:
            per[it["set"]].append(it)
        items = [x for s in sets for x in per[s][: args.limit]]
    by_key = {it["item_key"]: it for it in items}
    tok = load_tokenizer(args.model)
    sched = build_schedule(items, tok, mode, bs0)
    sched_hash = json.dumps(sched)
    (WS / "results").mkdir(exist_ok=True)
    logger.info(f"{len(items)} items, {len(sched)} batches")
    import os
    torch.cuda.set_per_process_memory_fraction(float(os.environ.get("GEN_VRAM_FRAC", "0.95")))
    t0 = time.time()
    model, tok = load_model(args.model, attn=attn)
    eos = eos_ids(args.model)
    logger.info(f"model loaded {time.time() - t0:.0f}s")
    out_dir = WS / args.out_dir
    for ck in args.ckpts.split(","):
        mk, enabled = CKPTS[ck]
        assert mk == args.model
        op = out_dir / f"{ck}.jsonl"
        done = {r["item_key"] for r in read_jsonl(op)} if op.exists() else set()
        ctx = contextlib.nullcontext() if (enabled or not hasattr(model, "disable_adapter")) else model.disable_adapter()
        torch.cuda.reset_peak_memory_stats()
        tc = time.time()
        n_new = 0
        with ctx:
            for bi, batch in enumerate(sched):
                todo = [k for k in batch if k not in done]
                if not todo:
                    continue
                bs = len(todo)
                chunks = [todo]
                while True:
                    try:
                        rows = []
                        for ch in chunks:
                            outs = generate_batch(model, tok, [encode(tok, by_key[k]["prompt"]) for k in ch], MAX_NEW_TOKENS, eos)
                            for k, o in zip(ch, outs):
                                it = by_key[k]
                                rows.append({"ckpt": ck, "set": it["set"], "item_key": k, "semantic_id": it["semantic_id"],
                                             "lang": it["lang"], "prompt_sha": it["prompt_sha"],
                                             "response_text": o["response_text"], "n_new_tokens": o["n_new_tokens"],
                                             "hit_max": o["hit_max"], "eos_token_seen": o["eos_token_seen"],
                                             "batch_index": bi, "batch_size_used": len(ch)})
                        break
                    except torch.OutOfMemoryError:
                        torch.cuda.empty_cache()
                        bs = max(1, bs // 2)
                        chunks = [todo[i:i + bs] for i in range(0, len(todo), bs)]
                        logger.warning(f"OOM at batch {bi}: retry with chunk size {bs}")
                append_jsonl(op, rows)
                n_new += len(rows)
                done |= set(todo)
                if bi % 5 == 0:
                    el = time.time() - tc
                    logger.info(f"{ck} batch {bi + 1}/{len(sched)} done={len(done)} {el:.0f}s "
                                f"({el / max(n_new, 1):.2f}s/item) peakVRAM={torch.cuda.max_memory_allocated() / 1e9:.1f}GB")
        rows = read_jsonl(op)
        stats = {"ckpt": ck, "n": len(rows), "wall_s": round(time.time() - tc, 1),
                 "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                 "empty_rate": sum(r["response_text"].strip() == "" for r in rows) / max(len(rows), 1),
                 "hit_max_rate": sum(r["hit_max"] for r in rows) / max(len(rows), 1),
                 "batch_mode": mode, "batch_size": bs0, "attn": attn, "schedule_sha": __import__("hashlib").sha256(sched_hash.encode()).hexdigest()}
        logger.info(f"CKPT DONE {stats}")
        append_jsonl(WS / "logs" / "generation_stats.jsonl", [stats])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Labeller 1: meta-llama/Llama-Guard-3-8B (local, bnb NF4, bf16 compute) — the guard RefusEU's own scoring uses.

One forward pass per prompt over  <official LG3 chat template(user=text)> + "unsafe\\nS":
  * logits at the last template position  -> p(unsafe) = softmax over first tokens {'safe','unsafe'}
  * logits at the final position          -> forced hazard category distribution over S1..S14
Targets: every harmful prompt in S1 (all 520 harmful_behaviors), JBB harmful (100), StrongREJECT (313), RefusEU EN+SL (2800),
RefusEU preference-test gold-category rows (282, calibration only) and, with --twins, all S4 twin candidates.
Cache: work/guard_labels.jsonl {text, p_unsafe, cat_probs{S1..S14}, cat_top}
"""
from __future__ import annotations

import argparse
import time

import torch
from loguru import logger

from common import (LG_CATS, RAW, WORK, append_jsonl, disable_torch_native_triton, read_json, read_jsonl, set_ram_limit,
                    set_vram_fraction, setup_logging)

setup_logging("s03_guard")
disable_torch_native_triton()
LG_ID, LG_REV = "meta-llama/Llama-Guard-3-8B", "7327bd9f6efbbe6101dc6cc4736302b3cbb6e425"
OUTF = WORK / "guard_labels.jsonl"


def targets(twins: bool) -> list[str]:
    texts = [r["text"] for r in read_json(RAW / "full_mlhb_train.json")] + [r["text"] for r in read_json(RAW / "full_mlhb_test.json")]
    texts += [r["Goal"] for r in read_json(RAW / "full_jbb_harmful.json")]
    texts += [r["forbidden_prompt"] for r in read_json(RAW / "full_strongreject.json")]
    texts += [r["prompt"] for r in read_json(RAW / "full_refuseu_eval.json")]
    texts += [r["prompt"] for r in read_json(WORK / "refuseu_calibration.json")]
    if twins and (WORK / "llm_twins.json").exists():
        texts += [c["twin"] for c in read_json(WORK / "llm_twins.json") if c.get("twin")]
    return list(dict.fromkeys(t for t in texts if t and t.strip()))


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--twins", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--bs", type=int, default=12)
    a = ap.parse_args()
    set_ram_limit(80); set_vram_fraction(0.93)
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    done = {r["text"] for r in read_jsonl(OUTF)}
    todo = [t for t in targets(a.twins) if t not in done]
    if a.limit:
        todo = todo[:a.limit]
    logger.info(f"Llama Guard: {len(todo)} texts to label ({len(done)} cached)")
    if not todo:
        return
    tok = AutoTokenizer.from_pretrained(LG_ID, revision=LG_REV)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        LG_ID, revision=LG_REV, device_map="cuda:0",
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16),
        torch_dtype=torch.bfloat16).eval()
    logger.info(f"loaded LG3 in {time.time() - t0:.0f}s")
    id_safe = tok.encode("safe", add_special_tokens=False)
    id_unsafe = tok.encode("unsafe", add_special_tokens=False)
    assert len(id_safe) == 1 and len(id_unsafe) == 1, (id_safe, id_unsafe)
    cat_ids = []
    for k in range(1, 15):
        ids = tok.encode(str(k), add_special_tokens=False)
        assert len(ids) == 1, (k, ids)
        cat_ids.append(ids[0])
    suffix = "unsafe\nS"
    suf_ids = tok.encode(suffix, add_special_tokens=False)
    order = sorted(range(len(todo)), key=lambda i: -len(todo[i]))
    bs = a.bs
    i = 0
    buf = []
    t0 = time.time()
    while i < len(order):
        idx = order[i:i + bs]
        prompts = [tok.apply_chat_template([{"role": "user", "content": todo[j]}], tokenize=False) + suffix for j in idx]
        try:
            enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
            with torch.inference_mode():
                lg = model(**enc).logits
            pos_first = lg.shape[1] - len(suf_ids) - 1
            first = torch.log_softmax(lg[:, pos_first, :].float(), -1)
            pu = torch.softmax(torch.stack([first[:, id_safe[0]], first[:, id_unsafe[0]]], -1), -1)[:, 1]
            last = torch.softmax(lg[:, -1, cat_ids].float(), -1)
            for b, j in enumerate(idx):
                probs = {f"S{k + 1}": round(float(last[b, k]), 5) for k in range(14)}
                buf.append({"text": todo[j], "p_unsafe": round(float(pu[b]), 5), "cat_probs": probs,
                            "cat_top": max(probs, key=probs.get)})
            i += bs
            del lg
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if bs == 1:
                raise
            bs = max(1, bs // 2); logger.warning(f"OOM -> bs {bs}")
            continue
        if len(buf) >= 200 or i >= len(order):
            append_jsonl(OUTF, buf); buf = []
            logger.info(f"LG3 {min(i, len(order))}/{len(order)} ({min(i, len(order)) / (time.time() - t0):.1f}/s)")
    logger.info(f"done; categories: {LG_CATS}")


if __name__ == "__main__":
    main()

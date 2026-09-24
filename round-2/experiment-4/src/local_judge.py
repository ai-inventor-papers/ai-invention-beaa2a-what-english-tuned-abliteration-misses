#!/usr/bin/env python3
"""F1 SUBSTITUTE JUDGE (added after the primary gpt-4.1 judge was blocked by the run-level OpenRouter budget at 716/3,840
core items): a local, third-family LLM judge - Qwen/Qwen3-14B (NF4, bf16 compute, thinking disabled, greedy) - applying the
FROZEN protocol.yaml rubric VERBATIM (same system message, same user template, same [TRUNCATED] marker, same parser).
Blind: only the user request + response; checkpoints are interleaved in a seeded shuffled order before batching by length.
Empty responses are auto-labelled locally (class=empty, safe, lang=none), exactly as for the primary judge.

  python local_judge.py cert                  # batching certification: batch-1 vs batched labels on 48 items
  python local_judge.py run [--ckpts ...]     -> results/judge_local/<ckpt>.jsonl (resumable by item_key)
  python local_judge.py dev                   -> results/judge_local_dev_calibration.jsonl (the 40 iteration-1 DEV items)

Validation (agreement.py): Cohen's kappa vs the 716 gpt-4.1 labels (a seeded-random subset, because the primary judge
shuffled its call order before it was blocked) and vs the gpt-4.1 DEV calibration labels."""
from __future__ import annotations

import argparse
import json
import random
import time

import torch
from loguru import logger

from common import ALL_CKPTS, EXP3, WS, append_jsonl, read_jsonl, setup_logging
from judge import auto_empty, build_user, load_gen_rows, parse_judge, protocol

REPO, REV = "Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18"
JUDGE_NAME = f"{REPO}@{REV[:8]} NF4 local (thinking disabled, greedy)"
OUT = WS / "results" / "judge_local"
MAX_NEW = 40


def load():
    from huggingface_hub import snapshot_download
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    path = snapshot_download(REPO, revision=REV, local_files_only=True)
    tok = AutoTokenizer.from_pretrained(path)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                            bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(path, quantization_config=qc, dtype=torch.bfloat16, device_map="cuda:0",
                                                 attn_implementation="sdpa")
    model.eval()
    return model, tok


def render(tok, system: str, user: str) -> str:
    return tok.apply_chat_template([{"role": "system", "content": system}, {"role": "user", "content": user}],
                                   add_generation_prompt=True, tokenize=False, enable_thinking=False)


@torch.inference_mode()
def label_texts(model, tok, texts: list[str], bs: int) -> list[str]:
    """Greedy decode for rendered prompts; batches of similar length (left padding); OOM -> halve."""
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    outs: list[str | None] = [None] * len(texts)
    i = 0
    while i < len(order):
        ix = order[i:i + bs]
        try:
            enc = tok([texts[j] for j in ix], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda:0")
            gen = model.generate(**enc, do_sample=False, max_new_tokens=MAX_NEW, pad_token_id=tok.pad_token_id,
                                 temperature=None, top_p=None, top_k=None)
        except torch.OutOfMemoryError:
            torch.cuda.empty_cache()
            bs = max(1, bs // 2)
            logger.warning(f"OOM -> bs {bs}")
            continue
        dec = tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        for j, d in zip(ix, dec):
            outs[j] = d
        i += len(ix)
    return outs  # type: ignore[return-value]


def rows_for(ckpts: list[str]) -> list[dict]:
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    return load_gen_rows(ckpts, frozen)


def cert(model, tok) -> None:
    P = protocol()["judge_primary"]
    rows = [r for r in rows_for(["gams_orig", "gams_edit", "gemma_orig", "gemma_edit"]) if r["response_text"].strip()]
    random.Random(11).shuffle(rows)
    rows = rows[:48]
    texts = [render(tok, P["system"], build_user(P["user_template"], r["prompt"], r["response_text"], r["hit_max"])) for r in rows]
    single = [label_texts(model, tok, [t], 1)[0] for t in texts]
    batched = label_texts(model, tok, texts, 16)
    ps = [parse_judge(x) for x in single]
    pb = [parse_judge(x) for x in batched]
    same_cls = sum((a or {}).get("cls") == (b or {}).get("cls") for a, b in zip(ps, pb))
    same_all = sum(a == b for a, b in zip(ps, pb))
    res = {"n": len(rows), "same_class_batched_vs_single": same_cls, "same_all_fields": same_all,
           "parse_ok_single": sum(p is not None for p in ps), "parse_ok_batched": sum(p is not None for p in pb),
           "examples": [{"single": s, "batched": b} for s, b in zip(single[:4], batched[:4])],
           "pass": same_cls >= 46}
    (WS / "results" / "judge_local_cert.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    logger.info(f"CERT {({k: v for k, v in res.items() if k != 'examples'})}")


def run(model, tok, ckpts: list[str], bs: int) -> None:
    P = protocol()["judge_primary"]
    OUT.mkdir(parents=True, exist_ok=True)
    rows = rows_for(ckpts)
    done = set()
    for ck in ckpts:
        p = OUT / f"{ck}.jsonl"
        if p.exists():
            done |= {(r["ckpt"], r["item_key"]) for r in read_jsonl(p)}
    todo = [r for r in rows if (r["ckpt"], r["item_key"]) not in done]
    for r in [r for r in todo if not r["response_text"].strip()]:
        append_jsonl(OUT / f"{r['ckpt']}.jsonl", [auto_empty(r, JUDGE_NAME)])
    todo = [r for r in todo if r["response_text"].strip()]
    random.Random(20260923).shuffle(todo)  # interleave checkpoints (blindness), then chunk
    logger.info(f"local judge: {len(rows)} rows, {len(done)} done, {len(todo)} to label")
    t0 = time.time()
    CH = 256
    for c0 in range(0, len(todo), CH):
        chunk = todo[c0:c0 + CH]
        texts = [render(tok, P["system"], build_user(P["user_template"], r["prompt"], r["response_text"], r["hit_max"])) for r in chunk]
        outs = label_texts(model, tok, texts, bs)
        recs = []
        for r, raw in zip(chunk, outs):
            parsed = parse_judge(raw or "")
            logger.debug(f"RAW local {r['ckpt']} {r['item_key']}: {raw!r}")
            recs.append({"ckpt": r["ckpt"], "item_key": r["item_key"], "judge_model": JUDGE_NAME, "call_uuid": None, "raw": [raw],
                         "judge_fail": parsed is None}
                        | (parsed or {"safety": None, "categories": "", "cls": "judge_fail", "judge_lang": None}))
        by = {}
        for x in recs:
            by.setdefault(x["ckpt"], []).append(x)
        for ck, xs in by.items():
            append_jsonl(OUT / f"{ck}.jsonl", xs)
        n = c0 + len(chunk)
        el = time.time() - t0
        logger.info(f"{n}/{len(todo)} labelled; {el:.0f}s ({el / n:.3f}s/item); parse fails so far "
                    f"{sum(1 for ck in ckpts if (OUT / f'{ck}.jsonl').exists() for x in read_jsonl(OUT / f'{ck}.jsonl') if x.get('judge_fail'))}")


def dev(model, tok) -> None:
    P = protocol()["judge_primary"]
    cal = read_jsonl(WS / "results" / "judge_dev_calibration.jsonl")
    recs = json.loads((EXP3 / "results" / "judged_generations.json").read_text())
    rows = [{"key": r["item_key"], "prompt": recs[int(r["item_key"].split(":")[1])]["prompt"],
             "response": recs[int(r["item_key"].split(":")[1])]["response"]} for r in cal]
    texts = [render(tok, P["system"], build_user(P["user_template"], r["prompt"], r["response"], False)) for r in rows]
    outs = label_texts(model, tok, texts, 8)
    out = WS / "results" / "judge_local_dev_calibration.jsonl"
    out.write_text("".join(json.dumps({"item_key": r["key"], "raw": [o], "judge_model": JUDGE_NAME,
                                       "judge_fail": parse_judge(o or "") is None}
                                      | (parse_judge(o or "") or {"cls": "judge_fail"}), ensure_ascii=False) + "\n"
                           for r, o in zip(rows, outs)))
    logger.info(f"dev calibration labelled {len(rows)}")


def retry(model, tok) -> None:
    """Parse failures of the greedy local judge are truncations (it enumerates every category and hits the 40-token cap
    before the CLASS line). An identical greedy retry would repeat them, so failed rows are re-labelled ONCE with a
    160-token cap (same prompt); the new row supersedes the failed one (retry_max_new recorded)."""
    global MAX_NEW
    P = protocol()["judge_primary"]
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    prompts = {it["item_key"]: it["prompt"] for it in frozen["items"]}
    gen = {}
    for ck in ALL_CKPTS:
        p = WS / "results/gen" / f"{ck}.jsonl"
        if p.exists():
            gen |= {(ck, r["item_key"]): r for r in read_jsonl(p)}
    MAX_NEW = 160
    for ck in ALL_CKPTS:
        p = OUT / f"{ck}.jsonl"
        if not p.exists():
            continue
        rows = read_jsonl(p)
        last = {}
        for r in rows:
            last[r["item_key"]] = r
        fails = [r for r in last.values() if r.get("judge_fail")]
        if not fails:
            continue
        texts = [render(tok, P["system"], build_user(P["user_template"], prompts[r["item_key"]], gen[(ck, r["item_key"])]["response_text"],
                                                      gen[(ck, r["item_key"])]["hit_max"])) for r in fails]
        outs = label_texts(model, tok, texts, 4)
        new = []
        for r, raw in zip(fails, outs):
            parsed = parse_judge(raw or "")
            logger.debug(f"RAW local-retry {ck} {r['item_key']}: {raw!r}")
            new.append({"ckpt": ck, "item_key": r["item_key"], "judge_model": JUDGE_NAME, "call_uuid": None,
                        "raw": list(r["raw"]) + [raw], "judge_fail": parsed is None, "retry_max_new": 160}
                       | (parsed or {"safety": None, "categories": "", "cls": "judge_fail", "judge_lang": None}))
        append_jsonl(p, new)
        logger.info(f"{ck}: retried {len(fails)}; still failing {sum(x['judge_fail'] for x in new)}")
    # DEV calibration file too
    dp = WS / "results" / "judge_local_dev_calibration.jsonl"
    if dp.exists():
        recs = json.loads((EXP3 / "results" / "judged_generations.json").read_text())
        rows = read_jsonl(dp)
        for r in rows:
            if r.get("judge_fail"):
                i = int(r["item_key"].split(":")[1])
                raw = label_texts(model, tok, [render(tok, P["system"], build_user(P["user_template"], recs[i]["prompt"], recs[i]["response"], False))], 1)[0]
                parsed = parse_judge(raw or "")
                r.update({"raw": r["raw"] + [raw], "judge_fail": parsed is None, "retry_max_new": 160} | (parsed or {}))
        dp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["cert", "run", "dev", "all", "retry"])
    ap.add_argument("--ckpts", default=",".join(ALL_CKPTS))
    ap.add_argument("--bs", type=int, default=16)
    args = ap.parse_args()
    setup_logging(f"local_judge_{args.stage}")
    logger.add(WS / "logs" / "judge_local_debug.log", level="DEBUG", filter=lambda r: r["message"].startswith("RAW"))
    torch.cuda.set_per_process_memory_fraction(0.95)
    t0 = time.time()
    model, tok = load()
    logger.info(f"loaded {JUDGE_NAME} in {time.time() - t0:.0f}s")
    if args.stage in ("cert", "all"):
        cert(model, tok)
    if args.stage in ("dev", "all"):
        dev(model, tok)
    if args.stage in ("run", "all"):
        run(model, tok, args.ckpts.split(","), args.bs)
    if args.stage == "retry":
        retry(model, tok)


if __name__ == "__main__":
    main()

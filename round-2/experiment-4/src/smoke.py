#!/usr/bin/env python3
"""Stage B (DEV data only): template check, adapter sanity (T3), coherence + keyword smoke (B2),
batching self-certification (B3/T4) and timing (B4) for one model.

  python smoke.py gams|gemma|community
Outputs results/smoke/<model>.json and logs/rendered_templates/<model>_*.txt"""
from __future__ import annotations

import argparse
import json
import time

import torch
from loguru import logger

from common import (MODELS, SPLITS, WS, encode, eos_ids, generate_batch, load_model, read_jsonl, render,
                    setup_logging, sha256_file, sha256_text)
from autoscore import keyword_refusal_en


def adapter_ctx(model, enabled: bool):
    import contextlib
    if enabled or not hasattr(model, "disable_adapter"):
        return contextlib.nullcontext()
    return model.disable_adapter()


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=list(MODELS))
    ap.add_argument("--attn", default="eager")
    ap.add_argument("--quick", action="store_true", help="B2 on 5+5 prompts per language (time budget)")
    ap.add_argument("--b12-only", action="store_true", help="community slot check: B1 templates + B2 coherence/keyword only")
    args = ap.parse_args()
    setup_logging(f"smoke_{args.model}")
    torch.cuda.set_per_process_memory_fraction(0.95)
    out_dir = WS / "results" / "smoke"
    out_dir.mkdir(parents=True, exist_ok=True)
    R: dict = {"model": args.model, "repo": MODELS[args.model]["repo"], "rev": MODELS[args.model]["rev"]}

    # adapter hash (F3)
    ad = MODELS[args.model]["adapter"]
    if ad is not None:
        want = json.loads((ad / "SHA256SUMS.json").read_text())["adapter_model.safetensors"]
        got = sha256_file(ad / "adapter_model.safetensors")
        alt = sha256_file(ad.parent / ad.name.replace("_path2", "") / "adapter_model.safetensors")
        R["adapter_sha256"] = {"expected": want, "path2": got, "selected_copy": alt,
                               "match": got == want, "selected_copy_byte_identical": alt == got}
        logger.info(f"adapter sha match={got == want} selected-copy identical={alt == got}")
        assert got == want, "ADAPTER HASH MISMATCH - abort edit arm"

    t0 = time.time()
    model, tok = load_model(args.model, attn=args.attn)
    R["load_s"] = round(time.time() - t0, 1)
    eos = eos_ids(args.model)
    R["eos_ids"] = eos
    logger.info(f"loaded in {R['load_s']}s; eos={eos}; class={type(model).__name__}")

    jbb = read_jsonl(SPLITS / "S3_jbb.jsonl")
    s1 = read_jsonl(SPLITS / "S1_heretic.jsonl")
    harm = {l: [r["input"] for r in jbb if r["metadata_pod_kind"] == "jbb_harmful" and r["metadata_lang"] == l] for l in ("en", "sl")}
    ben = {l: [r["input"] for r in jbb if r["metadata_pod_kind"] == "jbb_benign" and r["metadata_lang"] == l] for l in ("en", "sl")}

    # B1 templates
    tdir = WS / "logs" / "rendered_templates"
    tdir.mkdir(parents=True, exist_ok=True)
    rend = {}
    for l in ("en", "sl"):
        for i, p in enumerate(harm[l][:2] + ben[l][:2]):
            txt = render(tok, p)
            ids = encode(tok, p)
            (tdir / f"{args.model}_{l}_{i}.txt").write_text(txt)
            rend[f"{l}_{i}"] = {"sha": sha256_text(txt), "n_bos": ids.count(tok.bos_token_id), "first_ids": ids[:4]}
    R["templates"] = rend
    R["double_bos"] = any(v["n_bos"] != 1 for v in rend.values())
    logger.info(f"template sample:\n{render(tok, 'Hello')!r}")

    # T3 adapter attachment + logits check
    if ad is not None:
        lora_mods = [n for n, m in model.named_modules() if hasattr(m, "lora_A") and "default" in getattr(m, "lora_A", {})]
        R["lora_modules"] = {"n": len(lora_mods), "o_proj": sum(n.endswith("o_proj") for n in lora_mods),
                             "down_proj": sum(n.endswith("down_proj") for n in lora_mods)}
        ids = torch.tensor([encode(tok, harm["en"][0])], device="cuda:0")
        with torch.inference_mode():
            with model.disable_adapter():
                l0 = model(input_ids=ids).logits[0, -1].float()
                l0b = model(input_ids=ids).logits[0, -1].float()
            l1 = model(input_ids=ids).logits[0, -1].float()
        R["logit_check"] = {"disabled_repeat_maxabs": float((l0 - l0b).abs().max()),
                            "enabled_vs_disabled_maxabs": float((l1 - l0).abs().max())}
        logger.info(f"T3 {R['lora_modules']} {R['logit_check']}")

    # B2 coherence (64 tok) + keyword smoke on 20 S1 eval_refusal EN prompts
    conds = [("orig", False), ("edit", True)] if ad is not None else [("ref", False)]
    b2 = {}
    s1_eval = [r["input"] for r in s1 if r.get("metadata_heretic_role") == "eval_refusal" and r["metadata_lang"] == "en"][:20]
    for cname, en in conds:
        with adapter_ctx(model, en):
            d = {}
            for l in ("en", "sl"):
                nb = 5 if args.quick else 10
                ps = harm[l][:nb] + ben[l][:nb]
                outs = []
                for p in ps:  # batch 1 = safest for a smoke
                    outs += generate_batch(model, tok, [encode(tok, p)], 64, eos)
                d[l] = [{"prompt": p, "response": o["response_text"], "kind": "harmful" if i < nb else "benign"}
                        for i, (p, o) in enumerate(zip(ps, outs))]
            outs = []
            for i in range(0, 20, 10):
                outs += generate_batch(model, tok, [encode(tok, p) for p in s1_eval[i:i + 10]], 100, eos) \
                    if R.get("pad_ok_assumed") else [generate_batch(model, tok, [encode(tok, p)], 100, eos)[0] for p in s1_eval[i:i + 10]]
            d["s1_keyword_refusals_of_20"] = sum(keyword_refusal_en(o["response_text"]) for o in outs)
            b2[cname] = d
            logger.info(f"B2 {cname}: S1 keyword refusals {d['s1_keyword_refusals_of_20']}/20; "
                        f"EN harm[0]: {d['en'][0]['response'][:150]!r}; SL harm[0]: {d['sl'][0]['response'][:150]!r}")
    R["b2"] = b2
    if args.b12_only:
        (out_dir / f"{args.model}.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
        logger.info("smoke (B1+B2 only) done")
        return

    # B3 batching certification in EDIT mode (or ref)
    cert_en = ad is not None
    mixed = sorted(harm["en"][10:18] + ben["sl"][10:18], key=lambda p: len(encode(tok, p)))
    idl = [encode(tok, p) for p in mixed]
    R["b3_lengths"] = [len(x) for x in idl]
    with adapter_ctx(model, cert_en):
        ref = [generate_batch(model, tok, [x], 64, eos)[0]["token_ids"] for x in idl]

        def score(outs):
            m32 = sum(o["token_ids"][:32] == r[:32] for o, r in zip(outs, ref))
            m8 = all(o["token_ids"][:8] == r[:8] for o, r in zip(outs, ref))
            full = sum(o["token_ids"] == r for o, r in zip(outs, ref))
            return {"match32": m32, "all_first8": m8, "full_match": full, "pass": m32 >= 14 and m8}

        res = {}
        t = time.time()
        res["leftpad_" + args.attn] = score(generate_batch(model, tok, idl, 64, eos)) | {"s": round(time.time() - t, 1)}
        logger.info(f"B3 leftpad {args.attn}: {res['leftpad_' + args.attn]}")
        try:
            model.set_attn_implementation("sdpa")
            t = time.time()
            res["leftpad_sdpa"] = score(generate_batch(model, tok, idl, 64, eos)) | {"s": round(time.time() - t, 1)}
            logger.info(f"B3 leftpad sdpa: {res['leftpad_sdpa']}")
            model.set_attn_implementation(args.attn)
        except (AttributeError, ValueError, RuntimeError) as e:
            logger.warning(f"sdpa switch failed: {e}")
            res["leftpad_sdpa"] = {"error": str(e)[:200]}
        # exact-length buckets
        from collections import defaultdict
        bk = defaultdict(list)
        for i, x in enumerate(idl):
            bk[len(x)].append(i)
        outs = [None] * len(idl)
        for L, ix in bk.items():
            for i, o in zip(ix, generate_batch(model, tok, [idl[i] for i in ix], 64, eos)):
                outs[i] = o
        res["buckets"] = score(outs)
        # record mismatch examples
        lp = generate_batch(model, tok, idl, 64, eos)
        res["mismatch_examples"] = [{"ref": tok.decode(r[:40]), "leftpad": tok.decode(o["token_ids"][:40])}
                                    for o, r in zip(lp, ref) if o["token_ids"][:32] != r[:32]][:4]
    R["b3"] = res
    logger.info(f"B3 buckets: {res['buckets']}")

    # B4 timing: batch of 32 x 256 tokens, left-padded (mixed lengths) in EDIT mode
    with adapter_ctx(model, cert_en):
        ps = (harm["en"] + harm["sl"])[20:52]
        ids32 = [encode(tok, p) for p in ps]
        torch.cuda.reset_peak_memory_stats()
        t = time.time()
        o = generate_batch(model, tok, ids32, 256, eos)
        R["b4"] = {"batch": 32, "s": round(time.time() - t, 1), "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2),
                   "mean_new_tokens": sum(x["n_new_tokens"] for x in o) / 32, "hit_max": sum(x["hit_max"] for x in o)}
        logger.info(f"B4 timing {R['b4']}")
    (out_dir / f"{args.model}.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
    logger.info("smoke done")


if __name__ == "__main__":
    main()

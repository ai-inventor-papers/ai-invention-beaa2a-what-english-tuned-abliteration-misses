#!/usr/bin/env python3
"""PHASE 4 (iii), stretch - behavioural bf16 cell for the Gemma trial-96 edit on the 40 frozen S5X items of phase 4 (ii).

bf16 = gemma-3-12b-it@96b6f1ec with the iteration-1 trial-96 LoRA merged on CPU, dispatched with CPU offload, greedy,
128 new tokens, the model's chat template. NF4 = the STORED art_m6pglf516e2r gemma_edit outputs for the same items,
cut to their first 128 tokens so both sides have identical length. BOTH sides are labelled by the same blind gpt-4.1 rubric
(the frozen art_m6pglf516e2r rubric); the comparison is therefore same-judge, same-items, same-length."""
from __future__ import annotations

import asyncio
import gc
import json
import os
import time

import numpy as np
import pandas as pd
import torch
import yaml
from loguru import logger

import common as C
import p2_buy as PB
from p4_quant import ADAPTER, SNAP

OUT = C.RES / "quant_behaviour_bf16_gens.jsonl"
LAB = C.RES / "gpt41_quant_behaviour_labels.jsonl"


@torch.inference_mode()
def generate(items: list[dict]) -> list[str]:
    from accelerate import dispatch_model, infer_auto_device_map
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(SNAP)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(SNAP, dtype=torch.bfloat16, device_map={"": "cpu"})
    model = PeftModel.from_pretrained(model, str(ADAPTER)).merge_and_unload()
    dm = infer_auto_device_map(model, max_memory={0: "10GiB", "cpu": "120GiB"}, no_split_module_classes=getattr(model, "_no_split_modules", None))
    model = dispatch_model(model, device_map=dm)
    model.eval()
    texts = [tok.apply_chat_template([{"role": "user", "content": it["prompt"]}], add_generation_prompt=True, tokenize=False) for it in items]
    outs = []
    for i in range(0, len(texts), 20):
        enc = tok(texts[i:i + 20], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda:0")
        t = time.time()
        g = model.generate(**enc, do_sample=False, max_new_tokens=128, pad_token_id=tok.pad_token_id)
        outs += tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        logger.info(f"batch {i}: {time.time() - t:.0f}s")
    del model
    gc.collect(); torch.cuda.empty_cache()
    return outs


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("p4b_behaviour")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(SNAP)
    gids = C.jload(C.RES / "quant_subset_frozen.json")["gids"]
    df = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "prompt_id", "language", "prompt", "response", "semantic_item_id"])
    orig = df.set_index("gid").loc[gids].reset_index()
    ed = df[df.gid.isin(["gemma_edit|" + g.split("|", 1)[1] for g in gids])].set_index("prompt_id")
    items = [{"key": r.prompt_id, "lang": r.language, "prompt": r.prompt, "pair": r.semantic_item_id,
              "nf4_response": tok.decode(tok(ed.loc[r.prompt_id, "response"], add_special_tokens=False)["input_ids"][:128])}
             for r in orig.itertuples()]
    if not OUT.exists():
        outs = generate(items)
        with open(OUT, "w") as f:
            for it, o in zip(items, outs):
                f.write(json.dumps({**it, "bf16_response": o}, ensure_ascii=False) + "\n")
    rows = C.read_jsonl(OUT)
    proto = yaml.safe_load((C.EXP4 / "protocol.yaml").read_text())["judge_primary"]
    done = {r["gid"] for r in C.read_jsonl(LAB) if r.get("status") == "ok"} if LAB.exists() else set()
    todo = []
    for r in rows:
        for prec in ("bf16", "nf4"):
            gid = f"quant|{prec}|{r['key']}"
            if gid not in done:
                todo.append({"gid": gid, "prompt": r["prompt"], "response": r[f"{prec}_response"], "hit": True, "cap": 128})
    PB.STATE["cum"] = sum(float(x.get("usd") or 0) for x in C.read_jsonl(PB.COST_LOG))
    if todo:
        res = asyncio.run(PB.run(todo, proto["system"], proto["user_template"]))
        with open(LAB, "a") as f:
            for x in res:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    lab = {x["gid"]: C.canon(x.get("cls")) for x in C.read_jsonl(LAB) if x.get("status") == "ok"}
    pmap = {}
    for p_ in C.jload(C.EXP4 / "frozen_samples.json")["s5x_pairs"]:
        pmap[p_["en_item"]] = p_["pair_id"]; pmap[p_["sl_item"]] = p_["pair_id"]
    for r in rows:
        r["pair"] = pmap.get(r["key"], r["pair"])
    t = pd.DataFrame([{"key": r["key"], "lang": r["lang"], "pair": r["pair"], "bf16": lab.get(f"quant|bf16|{r['key']}"),
                       "nf4": lab.get(f"quant|nf4|{r['key']}")} for r in rows]).dropna()
    out = {"n_items": int(len(t)), "judge": "openai/gpt-4.1, frozen art_m6pglf516e2r rubric, blind, both sides cut to 128 tokens"}
    rng = np.random.default_rng(5)
    for lang in ("en", "sl"):
        s = t[t.lang == lang]
        rb = (s.bf16 == "REFUSED").to_numpy(float); rn = (s.nf4 == "REFUSED").to_numpy(float)
        d = rb - rn
        out[lang] = {"n": int(len(s)), "refused_bf16": float(rb.mean()), "refused_nf4": float(rn.mean()),
                     "partial_bf16": float((s.bf16 == "PARTIAL").mean()), "partial_nf4": float((s.nf4 == "PARTIAL").mean()),
                     "diff_bf16_minus_nf4": float(d.mean()), "diff_ci": C.ci(np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)])),
                     "label_agreement": float((s.bf16 == s.nf4).mean())}
    pv = t.pivot_table(index="pair", columns="lang", values=["bf16", "nf4"], aggfunc="first").dropna()
    for prec in ("bf16", "nf4"):
        g = (pv[(prec, "sl")] == "REFUSED").astype(float).to_numpy() - (pv[(prec, "en")] == "REFUSED").astype(float).to_numpy()
        out[f"paired_gap_{prec}"] = {"gap": float(g.mean()), "n_pairs": int(len(g)),
                                     "ci": C.ci(np.array([g[rng.integers(0, len(g), len(g))].mean() for _ in range(2000)]))}
    out["cumulative_usd"] = round(sum(float(x.get("usd") or 0) for x in C.read_jsonl(PB.COST_LOG)), 4)
    C.jdump(out, C.RES / "quant_confound_behaviour.json")
    logger.info(out)


if __name__ == "__main__":
    main()

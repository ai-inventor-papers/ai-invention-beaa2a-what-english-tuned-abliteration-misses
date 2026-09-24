#!/usr/bin/env python3
"""PHASE 4 - bound the NF4-vs-bf16 confound for gemma-3-12b-it (pinned 96b6f1ec).

(i) weight level: stream o_proj / down_proj of every layer from the bf16 safetensors (one tensor resident at a time),
    NF4-quantise+dequantise it with bitsandbytes (blocksize 64, double quant = the run's Heretic config), and report the
    relative Frobenius error, the per-layer closed-form removal energy g(h) = w_h^2 ||r^T W_h||^2 of the trial-96 edit
    (Heretic kernel weights, direction_index 26.07 interpolated direction) on bf16 vs NF4 weights, the cosine between the
    two g profiles and the angle between the projected rows r^T W (bf16) and r^T W (NF4).
(ii) activation level: frozen 40-item EN/SL subset, prompt + first 32 tokens of the stored NF4 greedy response,
    teacher-forced through bf16 (accelerate CPU offload) and NF4; first-token logit difference and mean 32-token KL,
    for the original and for the trial-96 LoRA edit.
Usage: p4_quant.py weights | acts"""
from __future__ import annotations

import gc
import json
import math
import os
import sys
import time

import numpy as np
import pandas as pd
import torch
from loguru import logger
from safetensors import safe_open

import common as C

GEMMA = "google/gemma-3-12b-it"
REV = "96b6f1eccf38110c56df3a15bffe176da04bfd80"
SNAP = os.path.join(os.environ["HF_HUB_CACHE"], "models--google--gemma-3-12b-it", "snapshots", REV)
DIRS = C.IT1 / "gen_art/gen_art_experiment_1/directions/gemma/directions.pt"
ADAPTER = C.IT1 / "gen_art/gen_art_experiment_1/adapters/gemma_selected_path2"
T96 = {"attn.o_proj": {"max_weight": 1.2718897313493716, "max_weight_position": 28.419595813573196, "min_weight": 0.8167943387473141,
                       "min_weight_distance": 17.010645784545787},
       "mlp.down_proj": {"max_weight": 1.040584208786117, "max_weight_position": 30.66550180218407, "min_weight": 0.004965593879631726,
                         "min_weight_distance": 20.50554472467738}}
DIRECTION_INDEX = 26.06958022133516


def kernel_weight(layer: int, p: dict) -> float:
    """Heretic 3521f864 abliterate(): linear decay from max_weight at max_weight_position to min_weight at min_weight_distance."""
    d = abs(layer - p["max_weight_position"])
    if d > p["min_weight_distance"]:
        return 0.0
    return p["max_weight"] + (d / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])


def refusal_direction() -> torch.Tensor:
    D = torch.load(DIRS, map_location="cpu", weights_only=False).float()  # [49, 3840]; index 0 = embeddings
    w, i = math.modf(DIRECTION_INDEX + 1)
    r = torch.lerp(D[int(i)], D[int(i) + 1], w)
    return r / r.norm()


def weights() -> None:
    import bitsandbytes.functional as F
    idx = json.loads(open(os.path.join(SNAP, "model.safetensors.index.json")).read())["weight_map"]
    r = refusal_direction().cuda()
    rows = []
    t0 = time.time()
    for layer in range(48):
        for comp, key in (("attn.o_proj", f"language_model.model.layers.{layer}.self_attn.o_proj.weight"),
                          ("mlp.down_proj", f"language_model.model.layers.{layer}.mlp.down_proj.weight")):
            with safe_open(os.path.join(SNAP, idx[key]), framework="pt", device="cpu") as f:
                W = f.get_tensor(key).to("cuda")  # bf16 [3840, in]
            q, st = F.quantize_4bit(W, blocksize=64, quant_type="nf4", compress_statistics=True)
            Wq = F.dequantize_4bit(q, st, quant_type="nf4").to(torch.bfloat16)
            Wf, Wqf = W.float(), Wq.float()
            rel = float((Wqf - Wf).norm() / Wf.norm())
            pr, pq = r @ Wf, r @ Wqf  # projected rows (what the edit removes, up to w_h)
            wk = kernel_weight(layer, T96[comp])
            g_b, g_q = float(wk ** 2 * (pr @ pr)), float(wk ** 2 * (pq @ pq))
            cos = float((pr @ pq) / (pr.norm() * pq.norm()))
            rows.append({"layer": layer, "component": comp, "rel_frobenius_err": rel, "kernel_weight": wk,
                         "g_bf16": g_b, "g_nf4": g_q, "g_rel_diff": (g_q - g_b) / g_b if g_b > 0 else float("nan"),
                         "proj_row_cos": cos, "proj_row_angle_deg": float(np.degrees(np.arccos(np.clip(cos, -1, 1))))})
            del W, Wq, q, Wf, Wqf
            torch.cuda.empty_cache()
        if layer % 8 == 0:
            logger.info(f"layer {layer} {time.time() - t0:.0f}s")
    d = pd.DataFrame(rows)
    d.to_csv(C.RES / "quant_confound_weights.csv", index=False)
    gb = d.groupby("layer").g_bf16.sum().to_numpy(); gq = d.groupby("layer").g_nf4.sum().to_numpy()
    act = d[d.kernel_weight > 0]
    out = {"n_matrices": int(len(d)), "rel_frobenius_err_mean": float(d.rel_frobenius_err.mean()),
           "rel_frobenius_err_max": float(d.rel_frobenius_err.max()),
           "g_profile_cosine_bf16_vs_nf4": float(gb @ gq / (np.linalg.norm(gb) * np.linalg.norm(gq))),
           "total_energy_bf16": float(gb.sum()), "total_energy_nf4": float(gq.sum()),
           "total_energy_rel_diff": float((gq.sum() - gb.sum()) / gb.sum()),
           "g_rel_diff_abs_max_edited_layers": float(act.g_rel_diff.abs().max()),
           "proj_row_angle_deg_max_edited_layers": float(act.proj_row_angle_deg.max()),
           "proj_row_angle_deg_mean_edited_layers": float(act.proj_row_angle_deg.mean()),
           "n_edited_matrices": int(len(act)),
           "method": "bitsandbytes quantize_4bit/dequantize_4bit nf4 blocksize 64 double-quant on each bf16 matrix; "
                     "g(h)= w_h^2 ||r^T W_h||^2 with Heretic trial-96 kernel weights and direction_index 26.07",
           "seconds": round(time.time() - t0, 1)}
    C.jdump(out, C.RES / "quant_confound_weights.json")
    logger.info(out)


@torch.inference_mode()
def acts() -> None:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    df = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["gid", "source", "cell_id", "prompt_id", "language", "prompt", "response"])
    g = df[(df.source == "exp4") & (df.cell_id == "gemma_orig")].set_index("prompt_id")
    pairs = [p for p in C.jload(C.EXP4 / "frozen_samples.json")["s5x_pairs"] if p["en_item"] in g.index and p["sl_item"] in g.index]
    pairs = sorted(pairs, key=lambda p: C.sha_text(f"quant|{p['pair_id']}"))[:20]
    s = g.loc[[k for p in pairs for k in (p["en_item"], p["sl_item"])]].reset_index()
    tok = AutoTokenizer.from_pretrained(SNAP)
    items = []
    for _, r in s.iterrows():
        ptxt = tok.apply_chat_template([{"role": "user", "content": r.prompt}], add_generation_prompt=True, tokenize=False)
        p_ids = tok(ptxt, add_special_tokens=False)["input_ids"]
        r_ids = tok(r.response, add_special_tokens=False)["input_ids"][:32]
        items.append({"gid": r.gid, "lang": r.language, "ids": list(p_ids) + r_ids, "p_len": len(p_ids), "r_len": len(r_ids)})
    C.jdump({"gids": [i["gid"] for i in items], "rule": "20 verified S5X pairs by sha256('quant|'+pair_id), both sides (40 items: 20 EN + 20 SL)"}, C.RES / "quant_subset_frozen.json")

    def run_model(model) -> list[torch.Tensor]:
        """batches of 8, right padding; log-softmax at the 32 teacher-forced response positions of each item."""
        outs = []
        dev = "cuda:0"
        for i in range(0, len(items), 8):
            chunk = items[i:i + 8]
            L = max(len(it["ids"]) for it in chunk)
            ids = torch.full((len(chunk), L), tok.pad_token_id, dtype=torch.long)
            att = torch.zeros((len(chunk), L), dtype=torch.long)
            for j, it in enumerate(chunk):
                ids[j, :len(it["ids"])] = torch.tensor(it["ids"]); att[j, :len(it["ids"])] = 1
            lo = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
            for j, it in enumerate(chunk):
                outs.append(torch.log_softmax(lo[j, it["p_len"] - 1: it["p_len"] - 1 + it["r_len"]].float(), -1).cpu())
            del lo
            torch.cuda.empty_cache()
        return outs
    res = {}
    for variant in ("orig", "edit"):
        logp = {}
        for prec in ("nf4", "bf16"):
            t0 = time.time()
            if prec == "nf4":
                q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
                model = AutoModelForCausalLM.from_pretrained(SNAP, quantization_config=q, device_map="cuda:0", dtype=torch.bfloat16)
            else:
                if variant == "edit":
                    # merge the LoRA on CPU first, then dispatch with offload (PEFT wrappers break accelerate offload hooks)
                    from accelerate import dispatch_model, infer_auto_device_map
                    from peft import PeftModel
                    model = AutoModelForCausalLM.from_pretrained(SNAP, dtype=torch.bfloat16, device_map={"": "cpu"})
                    model = PeftModel.from_pretrained(model, str(ADAPTER)).merge_and_unload()
                    dm = infer_auto_device_map(model, max_memory={0: "11GiB", "cpu": "120GiB"},
                                               no_split_module_classes=getattr(model, "_no_split_modules", None))
                    model = dispatch_model(model, device_map=dm)
                else:
                    model = AutoModelForCausalLM.from_pretrained(SNAP, dtype=torch.bfloat16, device_map="auto",
                                                                 max_memory={0: "11GiB", "cpu": "120GiB"})
            if variant == "edit" and prec == "nf4":
                from peft import PeftModel
                model = PeftModel.from_pretrained(model, str(ADAPTER))
            model.eval()
            logp[prec] = run_model(model)
            logger.info(f"{variant} {prec}: {time.time() - t0:.0f}s")
            del model
            gc.collect(); torch.cuda.empty_cache()
        kl, ft_kl, ft_maxdiff, top1 = [], [], [], []
        per = []
        for it, a, b in zip(items, logp["bf16"], logp["nf4"]):
            k = (a.exp() * (a - b)).sum(-1)  # KL(bf16 || nf4) per position
            kl.append(float(k.mean())); ft_kl.append(float(k[0]))
            ft_maxdiff.append(float((a[0] - b[0]).abs().max()))
            top1.append(float((a.argmax(-1) == b.argmax(-1)).float().mean()))
            per.append({"gid": it["gid"], "lang": it["lang"], "kl32": kl[-1], "first_token_kl": ft_kl[-1], "top1_agree": top1[-1]})
        pdf = pd.DataFrame(per)
        res[variant] = {"n_items": len(items), "mean_kl32": float(np.mean(kl)), "mean_first_token_kl": float(np.mean(ft_kl)),
                        "mean_first_token_max_abs_logprob_diff": float(np.mean(ft_maxdiff)),
                        "top1_agreement_32tok": float(np.mean(top1)),
                        "by_lang": {l: {"mean_kl32": float(g.kl32.mean()), "top1_agree": float(g.top1_agree.mean()),
                                        "first_token_kl": float(g.first_token_kl.mean())} for l, g in pdf.groupby("lang")}}
        pdf.to_csv(C.RES / f"quant_confound_acts_{variant}.csv", index=False)
    C.jdump(res, C.RES / "quant_confound_acts.json")
    logger.info(res)


if __name__ == "__main__":
    C.setup_logging("p4_quant")
    {"weights": weights, "acts": acts}[sys.argv[1]]()

#!/usr/bin/env python3
"""EXPLORATORY (not part of the four-checkpoint core): edit-strength dose-response of each model's Heretic LoRA edit.

Question: is the Gemma edit's missing Slovene effect a matter of edit STRENGTH (the optimizer stopped at a weak edit)
or of a Slovene refusal route the English-derived edit does not reach? The LoRA delta is multiplied by a factor f
(f = 0 is the original, f = 1 the core edit; f > 1 over-applies Heretic's own directional ablation). For every f:
  - R_seq on all S4 prompts (judged 24-token references, results/refs), per language x role
  - first-response-token KL(orig || f) on S4 harmless prompts (full vocabulary)
  - 64-token greedy generations for a frozen 48 harmful semantic ids x {EN, SL} (marker label + GlotLID + rep4)
No re-selection, no new optimisation; strength factors are fixed in advance. Output: results/dose/dose_<model>.json
Usage: .venv/bin/python dose.py --model gemma"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import torch
from loguru import logger

import common as C
from common import GEN, MODELS, jdump, setup_logging

FACTORS = {"gams": [0.0, 0.25, 0.5, 0.75, 1.0, 1.5], "gemma": [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]}
N_GEN_IDS = 48


def set_factor(lm, base_scale: dict, f: float) -> None:
    for name, mod in lm.model.named_modules():
        if name in base_scale:
            mod.scaling["default"] = base_scale[name] * f


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS), required=True)
    args = ap.parse_args()
    m = args.model
    setup_logging(f"dose_{m}")
    torch.cuda.set_per_process_memory_fraction(0.92)
    import method as M
    from engine import LM

    out_dir = C.RES / "dose"
    out_dir.mkdir(parents=True, exist_ok=True)
    lm = LM(m, adapter=True)
    base_scale = {n: float(mod.scaling["default"]) for n, mod in lm.model.named_modules()
                  if hasattr(mod, "scaling") and isinstance(getattr(mod, "scaling"), dict) and "default" in mod.scaling}
    logger.info(f"{len(base_scale)} LoRA modules, base scale {sorted(set(base_scale.values()))}")
    items = M.s4_items()
    refs = {(r["semantic_id"], r["lang"], r["role"]): r for r in map(json.loads, (C.RES / "refs" / f"refs_{m}.jsonl").read_text().splitlines())}
    enc = [lm.encode_chat(i["prompt"])[0] for i in items]
    seqs, starts, own = [], [], []
    for k, (i, ids) in enumerate(zip(items, enc)):
        r = refs[(i["semantic_id"], i["lang"], i["role"])]
        for which in ("ref_refuse", "ref_comply"):
            seqs.append(ids + r[which])
            starts.append(len(ids))
            own.append((k, which))
    harmless = [k for k, i in enumerate(items) if i["role"] == "harmless"]
    rng = np.random.default_rng(C.SEED)
    hids = sorted({i["semantic_id"] for i in items if i["role"] == "harmful"})
    gset = set(rng.choice(hids, N_GEN_IDS, replace=False).tolist())
    gk = [k for k, i in enumerate(items) if i["role"] == "harmful" and i["semantic_id"] in gset]
    # original next-token distribution at the first response position of harmless prompts (reference for KL)
    lm.set_ckpt("orig")
    ref_lp = {}
    for k, lp in zip(harmless, lm._run([enc[k] for k in harmless], [[len(enc[k]) - 1] for k in harmless], lambda lp, i, s: lp)):
        ref_lp[k] = torch.as_tensor(lp[0])
    lm.set_ckpt("edit")
    res = {"model": m, "factors": FACTORS[m], "n_gen_ids": N_GEN_IDS, "gen_ids": sorted(gset), "per_factor": {}}
    gens_all = []
    for f in FACTORS[m]:
        t = time.time()
        set_factor(lm, base_scale, f)
        lps = lm.token_logprobs(seqs, starts)
        rs = {}
        for (k, which), lp in zip(own, lps):
            rs.setdefault(k, {})[which] = float(lp.mean())
        R = np.array([rs[k]["ref_refuse"] - rs[k]["ref_comply"] for k in range(len(items))])
        kl_out = lm._run([enc[k] for k in harmless], [[len(enc[k]) - 1] for k in harmless], lambda lp, i, s: lp)
        kl = np.array([float((ref_lp[k].exp() * (ref_lp[k] - torch.as_tensor(lp[0]))).sum().clamp_min(0)) for k, lp in zip(harmless, kl_out)])
        outs = lm.generate([enc[k] for k in gk], GEN["s4_harmful"], batch=48)
        pf = {}
        for lang in C.LANGS:
            for role in ("harmful", "harmless"):
                mk = np.array([i["lang"] == lang and i["role"] == role for i in items])
                pf[f"R_seq_mean|{lang}|{role}"] = float(R[mk].mean())
                pf[f"R_seq_pos_frac|{lang}|{role}"] = float((R[mk] > 0).mean())
            hl = np.array([items[k]["lang"] == lang for k in harmless])
            pf[f"KL1_harmless_median|{lang}"] = float(np.median(kl[hl]))
            pf[f"KL1_harmless_mean|{lang}"] = float(kl[hl].mean())
            txt = [lm.tok.decode(o, skip_special_tokens=True) for k, o in zip(gk, outs) if items[k]["lang"] == lang]
            pf[f"gen_marker_refusal|{lang}"] = float(np.mean([C.keyword_refusal(x) for x in txt]))
            pf[f"gen_rep4_mean|{lang}"] = float(np.mean([C.rep4(x) for x in txt]))
            pf[f"gen_malformed_rule|{lang}"] = float(np.mean([C.malformed_rule(x) for x in txt]))
            pf[f"gen_empty|{lang}"] = float(np.mean([not x.strip() for x in txt]))
        for k, o in zip(gk, outs):
            gens_all.append({"factor": f, "semantic_id": items[k]["semantic_id"], "lang": items[k]["lang"], "prompt": items[k]["prompt"],
                             "response": lm.tok.decode(o, skip_special_tokens=True)})
        res["per_factor"][str(f)] = pf
        res.setdefault("items_R_seq", {})[str(f)] = R.tolist()
        logger.info(f"[dose {m}] f={f}: R_seq harmful EN {pf['R_seq_mean|en|harmful']:.2f} SL {pf['R_seq_mean|sl|harmful']:.2f}; "
                    f"marker refusal EN {pf['gen_marker_refusal|en']:.2f} SL {pf['gen_marker_refusal|sl']:.2f}; "
                    f"KL1 med EN {pf['KL1_harmless_median|en']:.3f} SL {pf['KL1_harmless_median|sl']:.3f} ({time.time()-t:.0f}s)")
        jdump(res | {"items": [{k: i[k] for k in ("semantic_id", "lang", "role", "stratum")} for i in items]}, out_dir / f"dose_{m}.json")
        jdump(gens_all, out_dir / f"dose_gens_{m}.json")
    set_factor(lm, base_scale, 1.0)
    lm.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""BONUS (bounded, descriptive): cjvt/GaMS3-12B BASE as a pre-instruction diagnostic.

Same NF4 config as the chat checkpoints; NO chat template: raw base formatting '<bos>Question: {prompt}\\nAnswer:'
(frozen format). Measures (i) harmfulness separability of the last-prompt-token residual per layer and language:
S3 half-A pooled DiM direction applied to held-out S4 (frozen) + grouped-CV DiM on S4; (ii) cos(base harm direction,
GaMS-Instruct d_EN) per layer -- nominal coordinates only (same tokenizer/architecture, different weights and a different
token position); (iii) 20 EN + 20 SL S4 harmful greedy continuations (64 tokens), judged blind by the same gpt-4.1 rubric.
Its refusal rate is NOT comparable to the chat models (different task format) and is reported descriptively only.
Usage: .venv/bin/python base_diag.py [--no-judge]"""
from __future__ import annotations

import argparse
import asyncio
import json
import time

import numpy as np
import pandas as pd
import torch
from loguru import logger

import common as C
from common import jdump, jload, read_split, setup_logging

BASE = {"repo": "cjvt/GaMS3-12B", "sha": "46127695de173a5de72e1da9dc43846f58553477", "e3_key": "gams3", "adapter": None,
        "adapter_heretic": None, "trial": None, "primary_layer": 34, "primary_pos": -1}
FMT = "Question: {prompt}\nAnswer:"
OUT = C.RES / "base_diag"
N_GEN = 20


def items() -> tuple[list[dict], list[dict]]:
    s4 = [{"semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"], "role": r["metadata_role"],
           "stratum": r["metadata_s4_stratum"], "prompt": r["input"]} for r in read_split("S4_strongreject_pairs")]
    s3 = [{"semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"], "role": r["metadata_role"],
           "half": r["metadata_half"], "prompt": r["input"]} for r in read_split("S3_jbb")]
    key = lambda x: (x["semantic_id"], x["role"], x["lang"])  # noqa: E731
    return sorted(s3, key=key), sorted(s4, key=key)


def judge_base(gens: list[dict], res: dict) -> None:
    """Blind gpt-4.1 labels (same rubric) for the 40 base continuations; resumable via judge.py's raw log."""
    import hashlib

    import judge as J

    recs = [{"judge_id": "b" + hashlib.sha1(f"base|{g['semantic_id']}|{g['lang']}".encode()).hexdigest()[:10],
             "prompt": g["prompt"], "response": g["response"]} for g in gens]
    done = J.done_ids(J.JUDGE)
    todo = [r for r in recs if r["judge_id"] not in done]
    if todo and J.key_ok():
        asyncio.run(J._judge(todo, J.JUDGE))
    done = J.done_ids(J.JUDGE)
    for r, g in zip(recs, gens):
        lab, rl = J.parse(done[r["judge_id"]]) if r["judge_id"] in done else ("NOT_JUDGED", None)
        g["judge_label"], g["judge_resp_lang"] = lab, rl
    jdump(gens, OUT / "base_generations.json")
    res["judge_labels"] = {lang: pd.Series([g["judge_label"] for g in gens if g["lang"] == lang]).value_counts().to_dict() for lang in C.LANGS}


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--judge-only", action="store_true", help="judge the saved generations and update base_diag.json")
    args = ap.parse_args()
    setup_logging("base_diag")
    if args.judge_only:
        gens, res = jload(OUT / "base_generations.json"), jload(OUT / "base_diag.json")
        judge_base(gens, res)
        jdump(res, OUT / "base_diag.json")
        logger.info(f"base judge labels: {res['judge_labels']}")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    torch.cuda.set_per_process_memory_fraction(0.92)
    C.MODELS["gams_base"] = BASE  # engine reads the shared MODELS dict
    from engine import LM
    from mech import auc, cv_scores, dim_fit, unit, winsor

    t0 = time.time()
    lm = LM("gams_base", adapter=False)
    s3, s4 = items()

    def enc(it):
        ids = lm.encode_plain(FMT.format(prompt=it["prompt"]))
        return ids

    acts = {}
    for name, its in (("S3", s3), ("S4", s4)):
        seqs = [enc(i) for i in its]
        pos = [[len(s) - 1] for s in seqs]
        content = [list(range(1, len(s))) for s in seqs]
        x = lm.capture(seqs, pos, content, pos_keep=[0])[:, :, 0]  # [N,49,D] last prompt token
        assert np.isfinite(x).all()
        acts[name] = winsor(x)
        logger.info(f"[base] {name} acts {x.shape} ({time.time()-t0:.0f}s)")
    # generations (20 EN + 20 SL harmful, same semantic ids)
    rng = np.random.default_rng(C.SEED)
    hids = sorted({i["semantic_id"] for i in s4 if i["role"] == "harmful"})
    pick = set(rng.choice(hids, N_GEN, replace=False).tolist())
    gi = [i for i in s4 if i["role"] == "harmful" and i["semantic_id"] in pick]
    outs = lm.generate([enc(i) for i in gi], 64, batch=20)
    gens = [dict(i, response=lm.tok.decode(o, skip_special_tokens=True), n_tok=len(o)) for i, o in zip(gi, outs)]
    jdump(gens, OUT / "base_generations.json")
    lm.close()
    del lm
    torch.cuda.empty_cache()

    # ---- separability + cosines (CPU)
    d3, d4 = pd.DataFrame(s3), pd.DataFrame(s4)
    y3, A = (d3.role == "harmful").astype(int).values, (d3.half == "A").values
    y4, g4 = (d4.role == "harmful").astype(int).values, d4.semantic_id.values
    en3, en4 = (d3.lang == "en").values, (d4.lang == "en").values
    ins = np.load(C.RES / "gams" / "layer_dirs_gams.npz")["dEN"]  # GaMS-Instruct d_EN per layer (unit, pos -1, S3 half A)
    H = acts["S3"].shape[1]
    prof = {k: np.full(H, np.nan) for k in ("frozen_en", "frozen_sl", "cv_en", "cv_sl", "cos_base_dEN_instruct_dEN",
                                             "cos_base_dEN_dSL")}
    for L in range(1, H):
        X3, X4 = acts["S3"][:, L].astype(np.float64), acts["S4"][:, L].astype(np.float64)
        dP = dim_fit(X3[A], y3[A])
        dE, dS = dim_fit(X3[A & en3], y3[A & en3]), dim_fit(X3[A & ~en3], y3[A & ~en3])
        prof["cos_base_dEN_instruct_dEN"][L] = float(dE["dhat"] @ unit(ins[L]))
        prof["cos_base_dEN_dSL"][L] = float(dE["dhat"] @ dS["dhat"])
        for lang, m in (("en", en4), ("sl", ~en4)):
            prof[f"frozen_{lang}"][L] = auc(y4[m], (X4[m] - dP["mid"]) @ dP["dhat"])
            if L % 4 == 0 or L == 34:
                prof[f"cv_{lang}"][L] = auc(y4[m], cv_scores(X4[m], y4[m], g4[m], "dim"))
    np.savez(OUT / "base_layer_profile.npz", **prof)
    res = {"model": f"{BASE['repo']}@{BASE['sha']}", "format": FMT, "quant": "NF4 (same BitsAndBytesConfig as the chat checkpoints)",
           "position": "last prompt token (':' of 'Answer:') -- NOT the chat template position -1 of the Instruct model",
           "at_layer34": {k: float(v[34]) for k, v in prof.items()},
           "best_layer_frozen_en": int(np.nanargmax(prof["frozen_en"])), "max_frozen_en": float(np.nanmax(prof["frozen_en"])),
           "best_layer_frozen_sl": int(np.nanargmax(prof["frozen_sl"])), "max_frozen_sl": float(np.nanmax(prof["frozen_sl"])),
           "n_generations": len(gens), "caveat": "descriptive; base refusal rate is not comparable to chat models (different task format)"}
    if not args.no_judge:
        judge_base(gens, res)
    res["marker_refusal_rate"] = {lang: float(np.mean([C.keyword_refusal(g["response"]) for g in gens if g["lang"] == lang])) for lang in C.LANGS}
    res["wall_s"] = time.time() - t0
    jdump(res, OUT / "base_diag.json")
    logger.info(f"base diag done: {json.dumps(res['at_layer34'])[:300]}")


if __name__ == "__main__":
    main()

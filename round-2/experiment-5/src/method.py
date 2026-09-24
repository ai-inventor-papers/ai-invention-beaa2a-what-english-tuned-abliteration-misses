#!/usr/bin/env python3
"""C1 utility + mechanistic core, GPU part. One model session loads the NF4 base once with the iteration-1 Heretic LoRA
adapter (PeftModel); ORIGINAL = adapter layers disabled, EDITED = enabled, so both checkpoints share one load, one
tokenizer, one chat template and one precision.

Stages (idempotent, resumable; outputs under results/ and acts/):
  check   template byte-identity, adapter SHA/tensor identity, LIVE CHECK vs iteration-1 stored responses
  gen     greedy generations: S4 harmful (64 tok) + S4 harmless (128 tok) in orig and edit; r_prior set (orig, 64 tok)
  acts    residual captures (float32, 49 hidden states): S3 JBB twins + Dolly (6 positions) and S4 (3 positions), orig+edit
  kl      paired full-vocab KL(orig||edit) at the first response position (KL1) and over the original's 32-token
          continuation (KL32) for every S4 prompt, plus first-token R1 in both checkpoints
  hval    real lm-evaluation-harness vs this repo's scorer on the ORIGINAL model (50 docs/task, EN + SL fork tasks)
  util    FINAL utility: frozen 250 items/task/language, orig and edit (touched once)
  flores  FINAL FLORES+ devtest per-token NLL, orig and edit
  s5acts  S5 + S5X residuals at pos -1 (all layers), ORIGINAL only (for label-free projections)
  rseq    teacher-forced R_seq with the 24-token refusal/compliance references (results/refs/refs_<model>.jsonl)
Usage: .venv/bin/python method.py --model gams --stages check,gen,acts,kl,hval,util,flores,s5acts [--mini]"""
from __future__ import annotations

import argparse
import gc
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
from loguru import logger

import common as C
from common import GEN, MODELS, jdump, jload, read_split, setup_logging

OUT = C.RES
ACT = C.ACTS
MINI = False


def s4_items() -> list[dict]:
    rows = read_split("S4_strongreject_pairs")
    items = [{"set": "S4", "semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"], "role": r["metadata_role"],
              "stratum": r["metadata_s4_stratum"], "half": r["metadata_half"], "prompt": r["input"],
              "category": r.get("metadata_category_llamaguard")} for r in rows]
    items.sort(key=lambda x: (x["semantic_id"], x["role"], x["lang"]))
    if MINI:
        keep = sorted({i["semantic_id"] for i in items})[:8]
        items = [i for i in items if i["semantic_id"] in keep]
    return items


def s3_items() -> list[dict]:
    items = []
    for name in ("S3_jbb", "S3_dolly"):
        for r in read_split(name):
            items.append({"set": name, "semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"],
                          "role": r["metadata_role"], "half": r["metadata_half"], "prompt": r["input"]})
    items.sort(key=lambda x: (x["set"], x["semantic_id"], x["role"], x["lang"]))
    if MINI:
        keep = sorted({i["semantic_id"] for i in items if i["set"] == "S3_jbb"})[:6] + sorted({i["semantic_id"] for i in items if i["set"] == "S3_dolly"})[:3]
        items = [i for i in items if i["semantic_id"] in keep]
    return items


def rprior_items() -> list[dict]:
    """S3 half-A harmless prompts (JBB benign twins + Dolly), both languages -> r_prior generations (original)."""
    return [i for i in s3_items() if i["role"] == "harmless" and i["half"] == "A"]


# ================================================================== stages
def stage_check(lm, model: str) -> None:
    from safetensors.torch import load_file

    spec = MODELS[model]
    res: dict = {"model": model, "repo": spec["repo"], "sha": spec["sha"], "model_class": lm.model_class}
    # adapter integrity
    sums = jload(spec["adapter"] / "SHA256SUMS.json")
    res["adapter_sha256"] = {f: {"expected": v, "got": C.file_sha256(spec["adapter"] / f), "match": C.file_sha256(spec["adapter"] / f) == v}
                             for f, v in sums.items()}
    a = load_file(str(spec["adapter"] / "adapter_model.safetensors"))
    b = load_file(str(spec["adapter_heretic"] / "adapter_model.safetensors"))
    same_keys = set(a) == set(b)
    maxdiff = max(float((a[k].float() - b[k].float()).abs().max()) for k in a) if same_keys else None
    res["path2_vs_heretic_export"] = {"same_keys": same_keys, "n_tensors": len(a), "max_abs_diff": maxdiff,
                                      "tensor_identical": bool(same_keys and maxdiff == 0.0)}
    mods = lm.lora_modules()
    res["lora_modules"] = {"n": len(mods), "expected": 2 * lm.L, "nonzero_B": int(sum(float(B.abs().sum()) > 0 for _, _, B, _ in mods)),
                           "scale": sorted({s for *_, s in mods}), "rank": sorted({A.shape[0] for _, A, _, _ in mods})}
    assert len(mods) == 2 * lm.L, f"LoRA modules {len(mods)} != {2 * lm.L}"
    # template byte identity (last 5 tokens) over S4 EN/SL prompts
    tail = ["<end_of_turn>", "\n", "<start_of_turn>", "model", "\n"]
    s4 = s4_items()
    tails = set()
    for it in s4:
        ids, _ = lm.encode_chat(it["prompt"])
        tails.add(tuple(lm.tok.convert_ids_to_tokens(ids[-5:])))
    res["template_tail"] = [list(t) for t in tails]
    res["template_tail_ok"] = tails == {tuple(tail)}
    res["rendered_example_en"] = lm.render(s4[0]["prompt"] if s4[0]["lang"] == "en" else s4[1]["prompt"])
    res["rendered_example_sl"] = lm.render(next(i["prompt"] for i in s4 if i["lang"] == "sl"))
    assert res["template_tail_ok"], f"template tail mismatch {tails}"
    # LIVE CHECK vs iteration-1 stored responses (Heretic's own generation, max_response_length 100)
    tag = model
    stored = {ck: jload(C.E1 / "results" / "eval" / f"{tag}_{nm}.json")["en"][:16] for ck, nm in (("edit", "own"), ("orig", "orig"))}
    prompts = [r["prompt"] for r in stored["edit"]]
    seqs = [lm.encode_chat(p)[0] for p in prompts]
    live = {}
    for ck in ("orig", "edit"):
        lm.set_ckpt(ck)
        outs = lm.generate(seqs, 100, batch=16)
        agree, kw_live, kw_stored = [], 0, 0
        for o, s in zip(outs, stored[ck]):
            st = lm.tok(s["response"], add_special_tokens=False)["input_ids"]
            n = min(len(st), len(o))
            pref = next((j for j in range(n) if st[j] != o[j]), n)
            agree.append(pref / max(len(st), 1))
            kw_live += C.keyword_refusal(lm.tok.decode(o, skip_special_tokens=True))
            kw_stored += C.keyword_refusal(s["response"])
        live[ck] = {"outs": [lm.tok.decode(o, skip_special_tokens=True) for o in outs], "prefix_agreement": agree,
                    "mean_prefix_agreement": float(np.mean(agree)), "kw_refusals_live": kw_live, "kw_refusals_stored": kw_stored}
    n_changed = sum(a != b for a, b in zip(live["orig"]["outs"], live["edit"]["outs"]))
    res["live_check"] = {ck: {k: v for k, v in live[ck].items() if k != "outs"} for ck in live}
    res["live_check"]["n_changed_edit_vs_orig"] = n_changed
    res["live_check"]["examples"] = [{"prompt": p, "orig": a[:200], "edit": b[:200]} for p, a, b in
                                     zip(prompts[:3], live["orig"]["outs"][:3], live["edit"]["outs"][:3])]
    res["live_check"]["pass"] = bool(n_changed >= 12 and live["edit"]["mean_prefix_agreement"] >= 0.9
                                     and abs(live["edit"]["kw_refusals_live"] - live["edit"]["kw_refusals_stored"]) <= 2)
    lm.set_ckpt("edit")
    jdump(res, OUT / model / "checks.json")
    logger.info(f"[check] adapter ok={all(v['match'] for v in res['adapter_sha256'].values())} identical={res['path2_vs_heretic_export']['tensor_identical']} "
                f"template={res['template_tail_ok']} live: changed {n_changed}/16, prefix-agree edit {live['edit']['mean_prefix_agreement']:.3f} "
                f"orig {live['orig']['mean_prefix_agreement']:.3f}, kw edit {live['edit']['kw_refusals_live']} vs {live['edit']['kw_refusals_stored']}")
    if n_changed == 0:
        raise RuntimeError("adapter has no effect (F1)")


def stage_gen(lm, model: str) -> None:
    path = OUT / "gens" / f"{model}_gens.json"
    if path.exists():
        logger.info("[gen] exists, skip")
        return
    recs = []
    s4 = s4_items()
    jobs = [("s4_harmful", [i for i in s4 if i["role"] == "harmful"], GEN["s4_harmful"], ("orig", "edit")),
            ("s4_harmless", [i for i in s4 if i["role"] == "harmless"], GEN["h100"], ("orig", "edit")),
            ("rprior", rprior_items(), GEN["rprior"], ("orig",))]
    for kind, items, max_new, ckpts in jobs:
        seqs = [lm.encode_chat(i["prompt"])[0] for i in items]
        for ck in ckpts:
            t = time.time()
            lm.set_ckpt(ck)
            outs = lm.generate(seqs, max_new, batch=48)
            for i, o in zip(items, outs):
                recs.append(dict(i, model=model, ckpt=ck, kind=kind, max_new=max_new, gen_ids=o,
                                 response=lm.tok.decode(o, skip_special_tokens=True)))
            logger.info(f"[gen] {kind} {ck}: {len(items)} x {max_new} tok in {time.time()-t:.0f}s")
    lm.set_ckpt("edit")
    jdump(recs, path, indent=None)


def _cap_positions(lm, items):
    seqs, pos, content = [], [], []
    for i in items:
        ids, cont = lm.encode_chat(i["prompt"])
        seqs.append(ids)
        pos.append([len(ids) - 5 + k for k in range(5)])
        content.append(cont)
    return seqs, pos, content


def stage_acts(lm, model: str) -> None:
    for setname, items, keep in (("S3", s3_items(), [0, 1, 2, 3, 4, 5]), ("S4", s4_items(), [3, 4, 5])):
        seqs, pos, content = _cap_positions(lm, items)
        for ck in ("orig", "edit"):
            p = ACT / model / f"{setname}_{ck}.npy"
            if p.exists():
                continue
            t = time.time()
            lm.set_ckpt(ck)
            x = lm.capture(seqs, pos, content, pos_keep=keep)
            assert np.isfinite(x).all(), "non-finite activations"
            p.parent.mkdir(parents=True, exist_ok=True)
            np.save(p, x)
            logger.info(f"[acts] {setname} {ck} {x.shape} in {time.time()-t:.0f}s; |x|max dim2339 L{MODELS[model]['primary_layer']}="
                        f"{np.abs(x[:, MODELS[model]['primary_layer'], -2, 2339]).max():.0f}")
            del x
            gc.collect()
        jdump({"items": items, "positions": [C.POS_NAMES[k] for k in keep]}, ACT / model / f"{setname}_index.json")
    lm.set_ckpt("edit")


def stage_kl(lm, model: str) -> None:
    path = OUT / model / "kl_r1.json"
    if path.exists():
        return
    gens = jload(OUT / "gens" / f"{model}_gens.json")
    orig = {(g["semantic_id"], g["lang"], g["role"]): g for g in gens if g["ckpt"] == "orig" and g["kind"].startswith("s4")}
    ps = jload(C.E3 / "configs" / f"prefix_sets_{MODELS[model]['e3_key']}.json")
    items = s4_items()
    prompts = [lm.encode_chat(i["prompt"])[0] for i in items]
    conts = []
    for i in items:
        g = orig[(i["semantic_id"], i["lang"], i["role"])]["gen_ids"][: GEN["kl_ref"]]
        if len(g) < GEN["kl_ref"]:
            g = g + [lm.tok.convert_tokens_to_ids("<end_of_turn>")]
        conts.append(g)
    rc = [(ps[i["lang"]]["R_set"], ps[i["lang"]]["C_set"]) for i in items]
    t = time.time()
    out = lm.paired_kl(prompts, conts, GEN["kl_ref"], rc)
    rows = []
    for i, o in zip(items, out):
        rows.append({"semantic_id": i["semantic_id"], "lang": i["lang"], "role": i["role"], "stratum": i["stratum"], "half": i["half"],
                     "KL1": float(o["kl"][0]), "KL32": float(np.mean(o["kl"])), "n_kl_pos": int(len(o["kl"])),
                     "R1_orig": o["r1_orig"], "R1_edit": o["r1_edit"]})
    jdump({"rows": rows, "prefix_sets_source": str(C.E3 / "configs" / f"prefix_sets_{MODELS[model]['e3_key']}.json")}, path)
    logger.info(f"[kl] {len(rows)} items in {time.time()-t:.0f}s; median KL1 harmless "
                f"{np.median([r['KL1'] for r in rows if r['role']=='harmless']):.4f} KL32 {np.median([r['KL32'] for r in rows if r['role']=='harmless']):.4f}")


def stage_hval(lm, model: str) -> None:
    from utility import harness_validate

    p = OUT / model / "harness_validation.json"
    if p.exists():
        return
    harness_validate(lm, limit=8 if MINI else 50, out_path=p)
    lm.set_ckpt("edit")


def stage_util(lm, model: str) -> None:
    from utility import build_requests, freeze_sample, score_items

    sp = C.CFG / "utility_sample_ids.json"
    sample = jload(sp) if sp.exists() else freeze_sample(sp)
    hv = OUT / model / "harness_validation.json"
    if hv.exists():
        rep = jload(hv)
        logger.info(f"[util] harness validation PASS={rep['PASS']} (agreement {rep['overall_acc_flag_agreement']:.3f})")
    else:
        logger.warning("[util] no harness validation found for this model")
    add_bos = True  # lm-eval HFLM sets add_bos_token=True for gemma-family model types (verified in hval)
    items = build_requests(lm.tok, sample, add_bos, limit=8 if MINI else None)
    for ck in ("orig", "edit"):
        p = OUT / model / f"utility_{ck}.json"
        if p.exists():
            continue
        t = time.time()
        lm.set_ckpt(ck)
        scored = score_items(lm, items)
        jdump([{k: v for k, v in s.items() if k not in ("contexts",)} | {"ckpt": ck, "model": model} for s in scored], p, indent=None)
        logger.info(f"[util] {ck}: {len(scored)} items in {time.time()-t:.0f}s; acc EN {np.mean([s['acc'] for s in scored if s['lang']=='en']):.3f} "
                    f"SL {np.mean([s['acc'] for s in scored if s['lang']=='sl']):.3f}")
    lm.set_ckpt("edit")


def stage_flores(lm, model: str) -> None:
    rows = read_split("S7_flores_devtest")
    if MINI:
        rows = rows[:20]
    seqs = [lm.encode_plain(r["input"]) for r in rows]
    for ck in ("orig", "edit"):
        p = OUT / model / f"flores_{ck}.json"
        if p.exists():
            continue
        t = time.time()
        lm.set_ckpt(ck)
        lps = lm.token_logprobs(seqs, [1] * len(seqs))
        out = [{"semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"], "nll": float(-lp.mean()), "n_tok": int(len(lp))}
               for r, lp in zip(rows, lps)]
        jdump(out, p, indent=None)
        logger.info(f"[flores] {ck} in {time.time()-t:.0f}s: EN {np.mean([o['nll'] for o in out if o['lang']=='en']):.4f} "
                    f"SL {np.mean([o['nll'] for o in out if o['lang']=='sl']):.4f}")
    lm.set_ckpt("edit")


def stage_s5acts(lm, model: str) -> None:
    p = ACT / model / "S5_orig.npy"
    if p.exists():
        return
    items = []
    for name in ("S5_refuseu", "S5X_refuseu_crosstrans"):
        for r in read_split(name):
            items.append({"set": name, "row_key": f"{name}|{r['metadata_semantic_id']}|{r['metadata_lang']}",
                          "semantic_id": r["metadata_semantic_id"], "lang": r["metadata_lang"], "prompt": r["input"],
                          "row_id": r.get("metadata_row_id"), "s5_core": r.get("metadata_s5_core"),
                          "category": r.get("metadata_category_llamaguard")})
    if MINI:
        items = items[:12] + items[-12:]
    seqs, pos, content = _cap_positions(lm, items)
    t = time.time()
    lm.set_ckpt("orig")
    x = lm.capture(seqs, pos, content, pos_keep=[4])
    np.save(p, x[:, :, 0])
    jdump({"items": items}, ACT / model / "S5_index.json", indent=None)
    logger.info(f"[s5acts] {x.shape} in {time.time()-t:.0f}s")
    lm.set_ckpt("edit")


def stage_rseq(lm, model: str) -> None:
    refs_p = OUT / "refs" / f"refs_{model}.jsonl"
    if not refs_p.exists():
        import readouts

        readouts.build("markers", OUT)  # pre-judge references (flagged 'markers'); rebuilt with judged labels later
    refs = [json.loads(l) for l in refs_p.read_text().splitlines()]
    tag = jload(OUT / "refs" / f"refs_{model}.meta.json")["label_source"]
    p = OUT / model / f"rseq_{tag}.json"
    if p.exists():
        return
    items = s4_items()
    key = {(r["semantic_id"], r["lang"], r["role"]): r for r in refs}
    seqs, starts, own = [], [], []
    for k, i in enumerate(items):
        r = key[(i["semantic_id"], i["lang"], i["role"])]
        ids, _ = lm.encode_chat(i["prompt"])
        for which in ("ref_refuse", "ref_comply"):
            seqs.append(ids + r[which])
            starts.append(len(ids))
            own.append((k, which))
    out = [dict(semantic_id=i["semantic_id"], lang=i["lang"], role=i["role"], stratum=i["stratum"], half=i["half"]) for i in items]
    for ck in ("orig", "edit"):
        t = time.time()
        lm.set_ckpt(ck)
        lps = lm.token_logprobs(seqs, starts)
        for (k, which), lp in zip(own, lps):
            out[k][f"{which}_{ck}"] = float(lp.mean())
        for o in out:
            o[f"R_seq_{ck}"] = o[f"ref_refuse_{ck}"] - o[f"ref_comply_{ck}"]
        logger.info(f"[rseq] {ck} in {time.time()-t:.0f}s")
    jdump({"label_source": tag, "rows": out}, p)
    lm.set_ckpt("edit")


STAGES = {"check": stage_check, "gen": stage_gen, "acts": stage_acts, "kl": stage_kl, "hval": stage_hval, "util": stage_util,
          "flores": stage_flores, "s5acts": stage_s5acts, "rseq": stage_rseq}


@logger.catch(reraise=True)
def main() -> None:
    global OUT, ACT, MINI
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS), required=True)
    ap.add_argument("--stages", default="check,gen,acts,kl,hval,util,flores,s5acts")
    ap.add_argument("--mini", action="store_true")
    args = ap.parse_args()
    MINI = args.mini
    if MINI:
        OUT, ACT = C.ROOT / "results_mini", C.ROOT / "acts_mini"
        for d in (OUT / "gens", OUT / "refs", ACT):
            d.mkdir(parents=True, exist_ok=True)
    setup_logging(f"method_{args.model}{'_mini' if MINI else ''}")
    (OUT / args.model).mkdir(parents=True, exist_ok=True)
    torch.cuda.set_per_process_memory_fraction(0.92)  # NEVER RLIMIT_AS (breaks safetensors mmap for 12B models)
    from engine import LM

    t0 = time.time()
    lm = LM(args.model, adapter=True)
    timings_p = OUT / args.model / "timings.json"
    timings = jload(timings_p) if timings_p.exists() else {}
    timings["load_s"] = time.time() - t0
    for st in args.stages.split(","):
        t = time.time()
        logger.info(f"=== stage {st}")
        STAGES[st](lm, args.model)
        timings[st] = time.time() - t
        jdump(timings, timings_p)
        logger.info(f"=== stage {st} done in {timings[st]:.0f}s; peak VRAM {torch.cuda.max_memory_allocated()/1e9:.1f} GB")
    lm.close()


if __name__ == "__main__":
    main()

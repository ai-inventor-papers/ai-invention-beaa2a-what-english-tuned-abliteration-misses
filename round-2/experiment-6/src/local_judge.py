#!/usr/bin/env python3
"""Local judge (fallback F1 after the run-level OpenRouter budget was exhausted at 00:04 UTC, with 1130/1420 generations
labelled by gpt-4.1 and 0 by the gemini second judge).

Judge model: Qwen/Qwen3-14B@40c06982 (bnb_4bit NF4, bf16 compute, chat template with enable_thinking=False), given the
SAME system rubric and user message as the gpt-4.1 judge (judge.RUBRIC / judge.build_msgs). A first attempt with
google/gemma-3-12b-it (same family as GaMS3) was interrupted by a machine change at 409/2140 and never saved; the
free-tier OpenRouter models were also exhausted for the day, so the cross-family Qwen3-14B replaced it. The assistant turn is prefilled with '{"label": "' and the label
is the argmax over the six label words' first-token log-probs (one forward pass, no sampling). Sequences are batched by
exact token length (no padding, so the known left-padding numerics issue cannot enter).

Roles:
  (1) SECOND JUDGE: agreement (Cohen's kappa, 6-way and refused-vs-not) with gpt-4.1 on every generation both labelled.
      Qwen3 is a different family from both the judged model (GaMS3 <- Gemma-3) and the primary judge (OpenAI); it is
      a smaller local model than the planned gemini-2.5-flash (which could not be called), so its agreement is reported.
  (2) FILL-IN: generations without a gpt-4.1 label get the local label; `judge_label_final` = gpt-4.1 label if present,
      else the local label, with `final_label_source` per row.

  uv run local_judge.py
"""
from __future__ import annotations

import time

import numpy as np
import torch
from loguru import logger

import judge as J
from common import RES, jdump, jload, setup_logging

REPO, SHA = "Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18"
JUDGE_NAME = "local Qwen3-14B"
PREFILL = '{"label": "'


def load():
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(REPO, revision=SHA)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                             bnb_4bit_use_double_quant=True)
    m = AutoModelForCausalLM.from_pretrained(REPO, revision=SHA, dtype=torch.bfloat16, quantization_config=bnb,
                                                    device_map="cuda:0")
    m.eval()
    return tok, m


def label_token_ids(tok) -> dict[str, int]:
    base = tok(PREFILL, add_special_tokens=False).input_ids
    out = {}
    for lab in J.LABELS:
        ids = tok(PREFILL + lab, add_special_tokens=False).input_ids
        assert ids[:len(base)] == base, f"prefill tokenisation not a prefix for {lab}"
        out[lab] = ids[len(base)]
    assert len(set(out.values())) == len(out), f"label first tokens collide: {out}"
    return out


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("local_judge")
    t0 = time.time()
    rows = jload(RES / "judged_generations.json")
    cache_p = RES / "judge_local_cache.json"
    cache = jload(cache_p) if cache_p.exists() else {}
    todo = [r for r in rows if r["key"] not in cache]
    logger.info(f"{len(rows)} generations, {len(todo)} to score locally")
    if todo:
        tok, model = load()
        lid = label_token_ids(tok)
        logger.info(f"loaded {REPO} in {time.time()-t0:.0f}s; label first tokens {lid}")
        cols = [lid[l] for l in J.LABELS]
        enc = []
        for r in todo:
            msgs = J.build_msgs(r["prompt"], r["response"])
            txt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False) + PREFILL
            enc.append(tok(txt, add_special_tokens=False).input_ids)
        by: dict[int, list[int]] = {}
        for i, e in enumerate(enc):
            by.setdefault(len(e), []).append(i)
        done = 0
        with torch.inference_mode():
            for n, ix in sorted(by.items()):
                for s in range(0, len(ix), 16):
                    b = ix[s:s + 16]
                    x = torch.tensor([enc[i] for i in b], device="cuda:0")
                    lg = model(input_ids=x, logits_to_keep=1).logits[:, -1, :].float()
                    lp = torch.log_softmax(lg, -1)[:, cols].cpu().numpy()
                    for i, v in zip(b, lp):
                        p = np.exp(v - v.max())
                        p = p / p.sum()
                        cache[todo[i]["key"]] = {"label": J.LABELS[int(np.argmax(v))], "p": {l: float(q) for l, q in zip(J.LABELS, p)}}
                    done += len(b)
                if done % 200 < 16:
                    logger.info(f"scored {done}/{len(todo)}")
        jdump(cache, cache_p)
        del model
        torch.cuda.empty_cache()
    from sklearn.metrics import cohen_kappa_score

    for r in rows:
        c = cache.get(r["key"])
        r["judge_local_label"] = c["label"] if c else None
        g = r.get("judge_label")
        if g not in (None, "PENDING_JUDGE", "unparsed"):
            r["judge_label_final"], r["final_label_source"] = g, "gpt-4.1"
        elif c:
            r["judge_label_final"], r["final_label_source"] = c["label"], JUDGE_NAME
        else:
            r["judge_label_final"], r["final_label_source"] = "PENDING_JUDGE", "none"
    jdump(rows, RES / "judged_generations.json")
    both = [r for r in rows if r["final_label_source"] == "gpt-4.1" and r["judge_local_label"]]
    a = [r["judge_label"] for r in both]
    b = [r["judge_local_label"] for r in both]
    meta = jload(RES / "judge_meta.json") if (RES / "judge_meta.json").exists() else {}
    meta["local_judge"] = {
        "model": f"{REPO}@{SHA[:8]} (bnb_4bit NF4), same rubric, prefill '{PREFILL}', argmax of label first-token log-probs",
        "role": "second judge (replaces gemini-2.5-flash, blocked by the run-level budget and the exhausted free tier) + fill-in for generations without a gpt-4.1 label",
        "family_note": "Qwen3 differs in family from GaMS3 (Gemma-3 based) and from gpt-4.1; it replaces the planned gemini-2.5-flash (budget-blocked)",
        "n_overlap_with_gpt41": len(both),
        "kappa_6way_gpt41_vs_local": float(cohen_kappa_score(a, b)) if len(both) > 5 else None,
        "kappa_refused_gpt41_vs_local": float(cohen_kappa_score([x == "refused" for x in a], [x == "refused" for x in b])) if len(both) > 5 else None,
        "agreement_6way": float(np.mean([x == y for x, y in zip(a, b)])) if both else None,
        "agreement_refused": float(np.mean([(x == "refused") == (y == "refused") for x, y in zip(a, b)])) if both else None,
        "kappa_refused_by_lang": {lang: float(cohen_kappa_score([r["judge_label"] == "refused" for r in both if r["lang"] == lang],
                                                                [r["judge_local_label"] == "refused" for r in both if r["lang"] == lang]))
                                  for lang in ("en", "sl") if sum(r["lang"] == lang for r in both) > 5},
        "final_label_sources": {s: sum(r["final_label_source"] == s for r in rows) for s in ("gpt-4.1", JUDGE_NAME, "none")},
        "final_label_counts": {l: sum(r["judge_label_final"] == l for r in rows) for l in J.LABELS + ["PENDING_JUDGE"]},
        "runtime_s": time.time() - t0}
    jdump(meta, RES / "judge_meta.json")
    logger.info(f"local judge: {meta['local_judge']}")


if __name__ == "__main__":
    main()

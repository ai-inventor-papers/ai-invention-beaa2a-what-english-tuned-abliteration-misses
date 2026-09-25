#!/usr/bin/env python3
"""Local MT: independent-family ALTERNATE translations + cross-family BACK-TRANSLATION for QC.
(First written when OpenRouter was exhausted; once it recovered, the canonical SL texts became LLM/pod translations and
this script's role became (a) MADLAD/NLLB alternates for the stability flag and (b) MADLAD back-translation of every
canonical output, via --llm-qc.)

Two independent MT families, greedy decoding, sentence-split:
  nllb   = facebook/nllb-200-distilled-1.3B (the screen spec's own fallback translator)  eng_Latn<->slv_Latn
  madlad = google/madlad400-3b-mt (T5, different family)                               <2sl> / <2en>
Forward jobs: every EN prompt that needs a Slovene version (S1,S2,S3 JBB/Dolly,S4 harmful+twins,S5 EN->SL (RefusEU-X),S6)
              and every RefusEU SL prompt -> EN (RefusEU-X sl->en + correspondence back-translation).
Back-translation is always CROSS-family: nllb outputs are back-translated by madlad and vice versa.
Cache: work/translations/<system>.jsonl  {src_lang,tgt_lang,src,out}
Usage: python s02_translate.py [--limit N]
"""
from __future__ import annotations

import argparse
import os
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")  # no C compiler on this box -> never compile
import gc
import re
import time

import torch
from loguru import logger

from common import (WORK, append_jsonl, disable_torch_native_triton, read_json, read_jsonl, set_ram_limit,
                    set_vram_fraction, setup_logging)

setup_logging("s02_translate")
disable_torch_native_triton()
TDIR = WORK / "translations"
TDIR.mkdir(parents=True, exist_ok=True)
MODELS = {"nllb": ("facebook/nllb-200-distilled-1.3B", "7be3e24664b38ce1cac29b8aeed6911aa0cf0576"),
          "madlad": ("google/madlad400-3b-mt", "fa184c675da0b5c9e1c8694fccd4e12e2d422094")}
NLLB_CODE = {"en": "eng_Latn", "sl": "slv_Latn"}
EN2SL_FAMILIES = {"S1_heretic", "S2_semantic", "S3_jbb", "S3_dolly", "S4_strongreject", "S4_twin", "S5_refuseu", "S6_xstest"}
_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[\"'„“«(\[]?[A-ZŠČŽĆĐ0-9])|\n+")


def split_sents(t: str) -> list[str]:
    parts = [p.strip() for p in _SPLIT.split(t.strip()) if p and p.strip()]
    return parts or [t.strip()]


class MT:
    def __init__(self, system: str):
        self.system = system
        rid, rev = MODELS[system]
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(rid, revision=rev)
        dtype = torch.float16 if system == "nllb" else torch.bfloat16  # T5 overflows in fp16
        self.model = AutoModelForSeq2SeqLM.from_pretrained(rid, revision=rev, torch_dtype=dtype).cuda().eval()
        logger.info(f"loaded {system} in {time.time() - t0:.0f}s")

    @torch.inference_mode()
    def _gen(self, sents: list[str], src: str, tgt: str, bs: int) -> list[str]:
        out: list[str] = [""] * len(sents)
        order = sorted(range(len(sents)), key=lambda i: -len(sents[i]))
        i = 0
        while i < len(order):
            idx = order[i:i + bs]
            batch = [sents[j] for j in idx]
            try:
                if self.system == "nllb":
                    self.tok.src_lang = NLLB_CODE[src]
                    enc = self.tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
                    kw = dict(forced_bos_token_id=self.tok.convert_tokens_to_ids(NLLB_CODE[tgt]))
                else:
                    enc = self.tok([f"<2{tgt}> {s}" for s in batch], return_tensors="pt", padding=True, truncation=True,
                                   max_length=400).to("cuda")
                    kw = {}
                mx = int(enc["input_ids"].shape[1] * 1.8) + 16
                gen = self.model.generate(**enc, num_beams=1, do_sample=False, max_new_tokens=min(mx, 512), disable_compile=True, **kw)
                dec = self.tok.batch_decode(gen, skip_special_tokens=True)
                for j, d in zip(idx, dec):
                    out[j] = d.strip()
                i += bs
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                bs = max(1, bs // 2)
                logger.warning(f"OOM -> batch {bs}")
        return out

    def translate(self, texts: list[str], src: str, tgt: str, bs: int = 48) -> list[str]:
        segs, owners = [], []
        for k, t in enumerate(texts):
            for s in split_sents(t):
                segs.append(s); owners.append(k)
        res = self._gen(segs, src, tgt, bs)
        joined: list[list[str]] = [[] for _ in texts]
        for k, r in zip(owners, res):
            joined[k].append(r)
        return [" ".join(j) for j in joined]

    def close(self) -> None:
        del self.model
        gc.collect(); torch.cuda.empty_cache()


def cache(system: str) -> dict[tuple, str]:
    return {(r["src_lang"], r["tgt_lang"], r["src"]): r["out"] for r in read_jsonl(TDIR / f"{system}.jsonl")}


def run_jobs(mt: MT, jobs: list[tuple[str, str, str]], chunk: int = 512) -> None:
    """jobs: (src_lang, tgt_lang, text); skips cached; appends to cache in chunks."""
    have = cache(mt.system)
    todo = sorted({j for j in jobs if j not in have and j[2].strip()})
    logger.info(f"{mt.system}: {len(todo)} to translate ({len(jobs)} requested)")
    for d in (("en", "sl"), ("sl", "en")):
        sub = [t for (s, g, t) in todo if (s, g) == d]
        for i in range(0, len(sub), chunk):
            t0 = time.time()
            part = sub[i:i + chunk]
            outs = mt.translate(part, d[0], d[1])
            append_jsonl(TDIR / f"{mt.system}.jsonl", [{"src_lang": d[0], "tgt_lang": d[1], "src": s, "out": o} for s, o in zip(part, outs)])
            logger.info(f"{mt.system} {d[0]}->{d[1]}: {min(i + chunk, len(sub))}/{len(sub)} ({len(part) / (time.time() - t0):.1f} texts/s)")


def forward_jobs(limit: int | None) -> list[tuple[str, str, str]]:
    items = read_json(WORK / "items.json")
    twins = read_json(WORK / "twins_selected.json") if (WORK / "twins_selected.json").exists() else []
    jobs = []
    for x in items:
        if x["family"] in EN2SL_FAMILIES and x["lang"] == "en":
            jobs.append(("en", "sl", x["text"]))
        if x["family"] == "S5_refuseu" and x["lang"] == "sl":
            jobs.append(("sl", "en", x["text"]))
    for t in twins:
        jobs.append(("en", "sl", t["twin"]))
    if (WORK / "refuseu_calibration.json").exists():  # gold-category calibration rows: SL -> EN for labeller 2 context
        jobs += [("sl", "en", r["prompt"]) for r in read_json(WORK / "refuseu_calibration.json") if r["lang"] == "sl"]
    jobs = list(dict.fromkeys(jobs))
    return jobs[:limit] if limit else jobs


def back_jobs(system_out: str, fwd: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Back-translation jobs for the OTHER family: system_out's output for every forward job, reversed direction."""
    c = cache(system_out)
    return list(dict.fromkeys((g, s, c[(s, g, t)]) for (s, g, t) in fwd if c.get((s, g, t), "").strip()))


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--cross-bt", action="store_true")
    ap.add_argument("--llm-qc", action="store_true",
                    help="final mode: MADLAD back-translation of every LLM (canonical) output + MADLAD/NLLB forward alternates "
                         "for any EN/SL source not yet translated (e.g. twins, calibration rows)")
    a = ap.parse_args()
    set_ram_limit(60); set_vram_fraction(0.92)
    if a.llm_qc:
        fj = forward_jobs(None)
        bt = []
        for f, key_fn in (("llm_screenspec.json", lambda k: ("en", "sl")), ("llm_strong.json", lambda k: tuple(k.split("|")[:2]))):
            if (WORK / f).exists():
                for k, e in read_json(WORK / f).items():
                    s_, g_ = key_fn(k)
                    for o in (e.get("out"), e.get("fallback_out")):
                        if o and o.strip():
                            bt.append((g_, s_, o))
        for x in read_json(WORK / "items.json"):  # pod-file SL texts (authoritative S3, most S1) need the same cross-family BT
            if x["meta"].get("pod_sl"):
                bt.append(("sl", "en", x["meta"]["pod_sl"]))
        bt = list(dict.fromkeys(bt))
        logger.info(f"llm-qc: {len(fj)} forward (cached mostly), {len(bt)} LLM outputs to back-translate")
        mt = MT("madlad"); run_jobs(mt, fj + bt); mt.close()
        mt = MT("nllb"); run_jobs(mt, fj); mt.close()
        logger.info("llm-qc translation done")
        return
    fj = forward_jobs(a.limit)
    logger.info(f"forward jobs: {len(fj)}")
    mt = MT("nllb"); run_jobs(mt, fj); mt.close()
    mt = MT("madlad"); run_jobs(mt, fj)
    if a.cross_bt:  # NLLB<->MADLAD cross back-translation of the local alternates (not used by the final QC; optional)
        run_jobs(mt, back_jobs("nllb", fj)); mt.close()
        mt = MT("nllb"); run_jobs(mt, back_jobs("madlad", fj))
    mt.close()
    logger.info("translation done")


if __name__ == "__main__":
    main()

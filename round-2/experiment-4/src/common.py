#!/usr/bin/env python3
"""Shared constants, paths, model loading, chat rendering and batched greedy generation (C1 behaviour)."""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

from loguru import logger

WS = Path(__file__).resolve().parent
RUN = Path(__file__).resolve().parents[3]
DATASET = RUN / "round-1/dataset-1/src"
EXP1 = RUN / "round-1/experiment-1/src"
EXP3 = RUN / "round-1/experiment-3/src"
SPLITS = DATASET / "data/splits"

SYSTEM_PROMPT = "You are a helpful assistant."
MAX_NEW_TOKENS = 256

MODELS: dict[str, dict[str, Any]] = {
    "gams": {"repo": "cjvt/GaMS3-12B-Instruct", "rev": "1d0b27af5748784482600d24779409e7e1dc9adc",
             "cls": "causal", "adapter": EXP1 / "adapters/gams_selected_path2", "trial": 88},
    "gemma": {"repo": "google/gemma-3-12b-it", "rev": "96b6f1eccf38110c56df3a15bffe176da04bfd80",
              "cls": "image_text", "adapter": EXP1 / "adapters/gemma_selected_path2", "trial": 96},
    "community": {"repo": "p-e-w/gemma-3-12b-it-heretic", "rev": "e037e6e112ea85777fc3858469cdc31fdfceaa13",
                  "cls": "image_text", "adapter": None, "trial": None},
}
# checkpoint -> (model key, adapter enabled?)
CKPTS: dict[str, tuple[str, bool]] = {
    "gams_orig": ("gams", False), "gams_edit": ("gams", True),
    "gemma_orig": ("gemma", False), "gemma_edit": ("gemma", True),
    "community_ref": ("community", False),
}
CORE_CKPTS = ["gams_orig", "gams_edit", "gemma_orig", "gemma_edit"]
ALL_CKPTS = CORE_CKPTS + ["community_ref"]


def setup_logging(name: str) -> None:
    (WS / "logs").mkdir(exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(WS / "logs" / f"{name}.log", rotation="30 MB", level="DEBUG")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def append_jsonl(p: Path, rows: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def detect_cpus() -> int:
    try:
        q = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        p = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        if q > 0:
            return math.ceil(q / p)
    except (FileNotFoundError, ValueError):
        pass
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        return os.cpu_count() or 1


def snapshot_path(model_key: str) -> Path:
    from huggingface_hub import snapshot_download
    m = MODELS[model_key]
    return Path(snapshot_download(m["repo"], revision=m["rev"], local_files_only=True))


def load_tokenizer(model_key: str):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_path(model_key))
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def load_model(model_key: str, attn: str = "eager"):
    """NF4 base (Heretic 3521f864 bnb_4bit config) + PEFT adapter (if any). Returns (model, tok)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoModelForImageTextToText, BitsAndBytesConfig
    m = MODELS[model_key]
    path = snapshot_path(model_key)
    qc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
                            bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)
    cls = AutoModelForCausalLM if m["cls"] == "causal" else AutoModelForImageTextToText
    base = cls.from_pretrained(path, quantization_config=qc, dtype=torch.bfloat16,
                               attn_implementation=attn, device_map="cuda:0")
    base.eval()
    model = base
    if m["adapter"] is not None:
        from peft import PeftModel
        model = PeftModel.from_pretrained(base, str(m["adapter"]))
        model.eval()
    tok = load_tokenizer(model_key)
    return model, tok


def render(tok, prompt: str) -> str:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
    return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)


def encode(tok, prompt: str) -> list[int]:
    """Rendered chat text already contains <bos>; add_special_tokens=False prevents a double BOS."""
    return tok(render(tok, prompt), add_special_tokens=False)["input_ids"]


def eos_ids(model_key: str) -> list[int]:
    gc = json.loads((snapshot_path(model_key) / "generation_config.json").read_text())
    e = gc.get("eos_token_id", 1)
    ids = e if isinstance(e, list) else [e]
    return sorted(set(ids) | {1, 106})  # <eos>, <end_of_turn>


def generate_batch(model, tok, id_lists: list[list[int]], max_new: int, eos: list[int]) -> list[dict]:
    """Greedy generation for one batch of pre-tokenised prompts (left padded if lengths differ)."""
    import torch
    L = max(len(x) for x in id_lists)
    pad = tok.pad_token_id
    ids = torch.full((len(id_lists), L), pad, dtype=torch.long)
    att = torch.zeros((len(id_lists), L), dtype=torch.long)
    for i, x in enumerate(id_lists):
        ids[i, L - len(x):] = torch.tensor(x)
        att[i, L - len(x):] = 1
    ids, att = ids.to("cuda:0"), att.to("cuda:0")
    with torch.inference_mode():
        out = model.generate(input_ids=ids, attention_mask=att, do_sample=False, max_new_tokens=max_new,
                             temperature=None, top_p=None, top_k=None, pad_token_id=pad, eos_token_id=eos)
    gen = out[:, L:].cpu().tolist()
    res = []
    for g in gen:
        # cut at first EOS
        n, eos_seen = len(g), False
        for j, t in enumerate(g):
            if t in eos:
                n, eos_seen = j, True
                break
        toks = g[:n]
        res.append({"token_ids": toks, "n_new_tokens": len(toks), "eos_token_seen": eos_seen,
                    "hit_max": (not eos_seen) and len(toks) >= max_new,
                    "response_text": tok.decode(toks, skip_special_tokens=True)})
    return res

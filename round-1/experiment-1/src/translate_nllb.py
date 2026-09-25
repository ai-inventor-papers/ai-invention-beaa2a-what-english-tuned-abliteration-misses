#!/usr/bin/env python3
"""Fallback F8 translator: NLLB-200-distilled-1.3B (greedy, CPU) EN->SL and SL->EN back-translation,
chrF(back, EN) with flag < 40. Used because the OpenRouter key hit its daily limit (HTTP 403)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sacrebleu
import torch
from loguru import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

WS = Path(__file__).resolve().parent
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(WS / "logs" / "translate_nllb.log", rotation="30 MB", level="DEBUG")
REPO, REV = "facebook/nllb-200-distilled-1.3B", "7be3e24664b38ce1cac29b8aeed6911aa0cf0576"


def translate(model, tok, texts: list[str], src: str, tgt: str, bs: int = 8) -> list[str]:
    tok.src_lang = src
    out = []
    for i in range(0, len(texts), bs):
        enc = tok(texts[i:i + bs], return_tensors="pt", padding=True)
        with torch.no_grad():
            gen = model.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids(tgt),
                                 max_new_tokens=160, num_beams=1, do_sample=False)
        out += tok.batch_decode(gen, skip_special_tokens=True)
        logger.info(f"{src}->{tgt} {min(i + bs, len(texts))}/{len(texts)}")
    return out


@logger.catch(reraise=True)
def main() -> None:
    torch.set_num_threads(4)
    src = json.loads((WS / "data" / "heretic_default_sources.json").read_text())
    items = [{"id": f"hb_test_{i:03d}", "set": "harmful_behaviors_test", "en": t}
             for i, t in enumerate(src["harmful_behaviors_test"][:100])]
    items += [{"id": f"ha_test_{i:03d}", "set": "harmless_alpaca_test_100_110", "en": t}
              for i, t in zip(range(100, 110), src["harmless_alpaca_test"][100:110])]
    tok = AutoTokenizer.from_pretrained(REPO, revision=REV)
    model = AutoModelForSeq2SeqLM.from_pretrained(REPO, revision=REV, dtype=torch.float32).eval()
    sl = translate(model, tok, [it["en"] for it in items], "eng_Latn", "slv_Latn")
    back = translate(model, tok, sl, "slv_Latn", "eng_Latn")
    for it, a, b in zip(items, sl, back):
        it.update(sl=a, back=b, chrF=sacrebleu.sentence_chrf(b, [it["en"]]).score, model=f"{REPO}@{REV}",
                  retried=False)
    # one retry for flagged items with beam search (same model)
    bad = [it for it in items if it["chrF"] < 40]
    logger.info(f"{len(bad)} flagged -> retry with num_beams=4")
    for it in bad:
        tok.src_lang = "eng_Latn"
        enc = tok([it["en"]], return_tensors="pt")
        with torch.no_grad():
            g = model.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids("slv_Latn"),
                               max_new_tokens=160, num_beams=4)
        a = tok.batch_decode(g, skip_special_tokens=True)[0]
        b = translate(model, tok, [a], "slv_Latn", "eng_Latn")[0]
        c = sacrebleu.sentence_chrf(b, [it["en"]]).score
        it["retried"] = True
        if c > it["chrF"]:
            it.update(sl=a, back=b, chrF=c)
    for it in items:
        it["flag"] = bool(it["chrF"] < 40)
    out = {"items": items, "translator": f"{REPO}@{REV} (greedy; beam-4 retry for chrF<40)",
           "why": "used for items where the API translator declined to translate the harmful prompt (its output was a refusal, chrF<40)",
           "review": "AUTOMATED ONLY (back-translation chrF); NATIVE_REVIEW_PENDING",
           "sha256_of_items": hashlib.sha256(json.dumps(items, ensure_ascii=False).encode()).hexdigest()}
    (WS / "data" / "sl_nllb_pass.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    ch = sorted(it["chrF"] for it in items)
    logger.info(f"chrF median {ch[len(ch)//2]:.1f} min {ch[0]:.1f} flagged {sum(it['flag'] for it in items)}")


if __name__ == "__main__":
    main()

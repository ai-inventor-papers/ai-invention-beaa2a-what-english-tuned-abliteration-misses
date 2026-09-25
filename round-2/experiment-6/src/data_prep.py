#!/usr/bin/env python3
"""STAGE 0a: data. Extracts the S3 DEV blocks (JBB twins, Dolly, FLORES dev, MC) from the frozen dataset artifact,
verifies each family against the frozen split manifest hashes, and builds the DISJOINT exposure set X_SET
(64 fresh databricks-dolly-15k prompts, EN->SL).

X_SET translation: the plan's primary translator is google/gemini-2.5-flash, but the shared OpenRouter key returned
HTTP 403 (daily limit) at the Stage -1 probe, so fallback F1/F11 applies: all 64 are translated with
facebook/nllb-200-distilled-1.3B (the plan's QC fallback MT). QC: LaBSE cos >= 0.8 and GlotLID slv_Latn.

  uv run data_prep.py
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter

import numpy as np
from loguru import logger

from common import DATA, DS, E1_SEED, LOGS, RES, file_sha256, jdump, jload, setup_logging, sha1_int

KIND_MAP = {"jbb_harmful": "jbb_harm", "jbb_benign": "jbb_ben", "dolly": "dolly", "flores": "flores",
            "mc_arc": "mc", "mc_hellaswag": "mc", "mc_piqa": "mc"}
FAMS = ["S3_jbb", "S3_dolly", "S3_flores_dev", "S3_mc"]
NLLB = "facebook/nllb-200-distilled-1.3B"
LABSE = "sentence-transformers/LaBSE"
XSET_CATS = {"open_qa", "brainstorming", "general_qa", "creative_writing"}


def verify_splits() -> dict:
    man = jload(DS / "data" / "split_manifest.json")
    out = {"protocol_hash": man.get("protocol_hash")}
    for fam in FAMS:
        lines = (DS / "data" / "splits" / f"{fam}.jsonl").read_text().splitlines()
        sha = hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()
        want = man["splits"][fam]["sha256_canonical_sorted_jsonl"]
        out[fam] = {"sha": sha, "manifest": want, "match": sha == want, "n_rows": len(lines)}
        assert sha == want, f"{fam}: split sha mismatch"
    return out


def build_items() -> list[dict]:
    full = jload(DS / "full_data_out.json")
    rows = []
    for ds in full["datasets"]:
        if ds["dataset"] in ("S3_screen_dev_prompts", "S3_screen_dev_utility"):
            rows += ds["examples"]
    del full
    # cross-check rows vs the frozen split files (the verified source)
    split_rows = {}
    for fam in FAMS:
        for l in (DS / "data" / "splits" / f"{fam}.jsonl").read_text().splitlines():
            r = json.loads(l)
            split_rows[(r["metadata_semantic_id"], r["metadata_pod_kind"], r["metadata_lang"])] = r
    items: dict = {}
    n_match = 0
    for r in rows:
        key = (r["metadata_semantic_id"], r["metadata_pod_kind"], r["metadata_lang"])
        sr = split_rows[key]
        n_match += int(sr["input"] == r["input"] and sr["output"] == r["output"])
        kind = KIND_MAP[r["metadata_pod_kind"]]
        sid = r["metadata_semantic_id"]
        it = items.setdefault((kind, sid), {"sid": sid, "kind": kind, "pod_kind": r["metadata_pod_kind"],
                                            "half": r["metadata_half"], "sub": sha1_int(sid + "#sub") % 2,
                                            "translation_unstable": False})
        assert it["half"] == r["metadata_half"], f"EN/SL half mismatch for {sid}"
        lang = r["metadata_lang"]
        if kind == "mc":
            q = json.loads(r["input"])
            it[lang] = q["query"]
            it[f"choices_{lang}"] = q["choices"]
            it.setdefault("gold", int(r["output"]))
            assert it["gold"] == int(r["output"])
            it["task"] = r.get("metadata_task")
        else:
            it[lang] = r["input"]
        if lang == "sl" and r.get("metadata_translation_unstable"):
            it["translation_unstable"] = True
        if kind == "dolly":
            it["category"] = r.get("metadata_dolly_category")
    assert n_match == len(rows), f"only {n_match}/{len(rows)} rows match the frozen split files"
    out = sorted(items.values(), key=lambda x: (x["kind"], x["sid"]))
    for it in out:
        assert "en" in it and "sl" in it, f"missing language for {it['sid']}"
    # JBB twins share a sid
    hs = {it["sid"] for it in out if it["kind"] == "jbb_harm"}
    bs = {it["sid"] for it in out if it["kind"] == "jbb_ben"}
    assert hs == bs, "JBB harm/ben twins do not share sids"
    return out


def build_xset(s3_dolly_ids: set[str]) -> dict:
    """64 fresh Dolly prompts, disjoint from S3; EN->SL with NLLB; LaBSE + GlotLID QC."""
    import torch
    from datasets import load_dataset

    ds = load_dataset("databricks/databricks-dolly-15k", split="train")
    elig = [i for i in range(len(ds)) if ds[i]["category"] in XSET_CATS and 8 <= len(ds[i]["instruction"].split()) <= 60
            and f"dolly_{i}" not in s3_dolly_ids and not ds[i]["context"].strip()]
    rng = np.random.default_rng(E1_SEED)
    pick = sorted(rng.choice(len(elig), 64, replace=False).tolist())
    rows = [{"xid": f"xdolly_{elig[k]}", "dolly_index": elig[k], "category": ds[elig[k]]["category"],
             "en": ds[elig[k]]["instruction"]} for k in pick]
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(NLLB, src_lang="eng_Latn")
    mdl = AutoModelForSeq2SeqLM.from_pretrained(NLLB, dtype=torch.float16).cuda().eval()
    outs = []
    for s in range(0, len(rows), 16):
        b = [r["en"] for r in rows[s:s + 16]]
        enc = tok(b, return_tensors="pt", padding=True, truncation=True, max_length=256).to("cuda")
        with torch.inference_mode():
            g = mdl.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids("slv_Latn"), max_new_tokens=256, num_beams=4)
        outs += tok.batch_decode(g, skip_special_tokens=True)
    del mdl
    torch.cuda.empty_cache()
    from sentence_transformers import SentenceTransformer

    lab = SentenceTransformer(LABSE, device="cuda")
    ee = lab.encode([r["en"] for r in rows], normalize_embeddings=True)
    es = lab.encode(outs, normalize_embeddings=True)
    cosv = (ee * es).sum(1)
    del lab
    torch.cuda.empty_cache()
    import fasttext
    from huggingface_hub import hf_hub_download

    lid = fasttext.load_model(hf_hub_download("cis-lmu/glotlid", "model.bin"))
    for r, o, c in zip(rows, outs, cosv):
        p, lab_ = lid.f.predict(o.replace("\n", " "), 1, 0.0, "strict")[0]
        r.update({"sl": o, "sl_method": NLLB, "labse": float(c), "lid": lab_.replace("__label__", ""), "lid_p": float(p)})
        r["qc_pass"] = bool(c >= 0.8 and r["lid"] == "slv_Latn")
    n_fail = sum(not r["qc_pass"] for r in rows)
    meta = {"n": len(rows), "n_qc_fail": n_fail, "translator": NLLB,
            "translator_note": "plan primary = gemini-2.5-flash (prompt+item in one user message); OpenRouter key 403 (daily "
                               "limit) at the Stage -1 probe -> NLLB for all 64 (fallback F1/F11). Benign prompts only.",
            "selection": f"databricks/databricks-dolly-15k train; categories {sorted(XSET_CATS)}; 8-60 words; no context; "
                         f"not in S3 dolly; default_rng({E1_SEED}).choice(64)", "n_eligible": len(elig),
            "labse_median": float(np.median(cosv)), "qc_rule": "LaBSE cos >= 0.8 AND GlotLID slv_Latn",
            "qc_fail_policy": "failures are kept (the set only feeds covariate D) and flagged; count reported"}
    return {"meta": meta, "rows": rows}


def main() -> None:
    setup_logging("data_prep")
    ver = verify_splits()
    logger.info(f"split hashes verified: {[(k, v['match']) for k, v in ver.items() if isinstance(v, dict)]}")
    items = build_items()
    c = Counter((it["kind"], it["half"]) for it in items)
    logger.info(f"items: {dict(c)}")
    jdump({"items": items, "verification": ver,
           "source": str(DS / "full_data_out.json"), "counts": {f"{k[0]}_{k[1]}": v for k, v in c.items()}}, DATA / "s3_items.json")
    (DATA / "s3_items.json.sha256").write_text(file_sha256(DATA / "s3_items.json") + "\n")
    xp = DATA / "x_set.json"
    if not xp.exists():
        xs = build_xset({it["sid"] for it in items if it["kind"] == "dolly"})
        jdump(xs, xp)
        (DATA / "x_set.json.sha256").write_text(file_sha256(xp) + "\n")
        logger.info(f"X_SET: {xs['meta']}")
    logger.info("data_prep done")


if __name__ == "__main__":
    main()

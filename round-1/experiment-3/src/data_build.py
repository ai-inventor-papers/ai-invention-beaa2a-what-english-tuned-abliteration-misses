#!/usr/bin/env python3
"""STAGE 1: build SCREEN-DEV (JBB twins, Dolly, FLORES, SL-LLM-Eval MC carve-out), S1 overlap audit,
EN->SL translation (NLLB-200 fallback, OpenRouter key exhausted) with back-translation chrF, and A/B halves."""
from __future__ import annotations

import argparse
import gc
import time

import numpy as np
import torch
from datasets import load_dataset
from loguru import logger
from scipy.optimize import linear_sum_assignment

from common import DATA, RESERVED_REPOS, file_sha256, jdump, jload, set_ram_limit, setup_logging, sha1_half

NLLB = "facebook/nllb-200-distilled-1.3B"
LABSE = "sentence-transformers/LaBSE"
LOADED: list[str] = []


def ld(repo: str, *a, **k):
    assert repo not in RESERVED_REPOS, f"reserved dataset {repo} must not be loaded"
    LOADED.append(repo + ":" + ",".join(map(str, a)) + str(k.get("split", "")))
    logger.info(f"load_dataset {repo} {a} {k}")
    return load_dataset(repo, *a, **k)


def labse_encode(model, texts: list[str]) -> np.ndarray:
    return model.encode(texts, batch_size=128, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)


def build_jbb(labse) -> tuple[list[dict], dict]:
    harm = ld("JailbreakBench/JBB-Behaviors", "behaviors", split="harmful").to_list()
    ben = ld("JailbreakBench/JBB-Behaviors", "behaviors", split="benign").to_list()
    info: dict = {"n_harmful_raw": len(harm), "n_benign_raw": len(ben), "non_index_pairings": []}
    ben_by_idx = {b["Index"]: b for b in ben}
    pairs: dict[int, tuple[dict, dict, str]] = {}
    unpaired_h, used_b = [], set()
    for h in harm:  # 1) by Index when Behavior matches
        b = ben_by_idx.get(h["Index"])
        if b is not None and b["Behavior"] == h["Behavior"] and b["Category"] == h["Category"]:
            pairs[h["Index"]] = (h, b, "index")
            used_b.add(b["Index"])
        else:
            unpaired_h.append(h)
    rest_b = [b for b in ben if b["Index"] not in used_b]
    still = []
    for h in unpaired_h:  # 2) exact Behavior within Category
        cand = [b for b in rest_b if b["Behavior"] == h["Behavior"] and b["Category"] == h["Category"]]
        if len(cand) == 1:
            pairs[h["Index"]] = (h, cand[0], "behavior_string")
            rest_b.remove(cand[0])
            info["non_index_pairings"].append((h["Index"], cand[0]["Index"], "behavior_string"))
        else:
            still.append(h)
    for cat in sorted({h["Category"] for h in still}):  # 3) Hungarian on LaBSE cos within Category
        hs = [h for h in still if h["Category"] == cat]
        bs = [b for b in rest_b if b["Category"] == cat]
        if not hs or not bs:
            continue
        sim = labse_encode(labse, [h["Goal"] for h in hs]) @ labse_encode(labse, [b["Goal"] for b in bs]).T
        r, c = linear_sum_assignment(-sim)
        for i, j in zip(r, c):
            pairs[hs[i]["Index"]] = (hs[i], bs[j], "hungarian_labse")
            info["non_index_pairings"].append((hs[i]["Index"], bs[j]["Index"], f"hungarian cos={sim[i, j]:.3f}"))
    info["pairing_methods"] = {m: sum(1 for v in pairs.values() if v[2] == m) for m in ("index", "behavior_string", "hungarian_labse")}
    logger.info(f"JBB twin pairing: {info['pairing_methods']}")

    # 2) S1 overlap audit (LaBSE cos > 0.85 with mlabonne/harmful_behaviors train)
    s1 = ld("mlabonne/harmful_behaviors", split="train")["text"]
    s1_test = ld("mlabonne/harmful_behaviors", split="test")["text"]
    hl = ld("mlabonne/harmless_alpaca", split="train")["text"]
    e_s1, e_s1t, e_hl = labse_encode(labse, s1), labse_encode(labse, s1_test), labse_encode(labse, hl)
    idxs = sorted(pairs)
    eh = labse_encode(labse, [pairs[i][0]["Goal"] for i in idxs])
    eb = labse_encode(labse, [pairs[i][1]["Goal"] for i in idxs])
    max_s1 = (eh @ e_s1.T).max(1)
    max_s1t = (eh @ e_s1t.T).max(1)
    max_hl = (eb @ e_hl.T).max(1)
    dropped = {}
    items = []
    for k, i in enumerate(idxs):
        h, b, meth = pairs[i]
        src = h["Source"]
        if max_s1[k] > 0.85:
            dropped.setdefault(src, 0)
            dropped[src] += 1
            continue
        sid = f"jbb_{i}"
        extra = {"Behavior": h["Behavior"], "Category": h["Category"], "Source": src, "pairing": meth,
                 "benign_index": b["Index"], "maxcos_S1_train": float(max_s1[k]), "maxcos_S1_test": float(max_s1t[k]),
                 "benign_maxcos_harmless_alpaca": float(max_hl[k])}
        items.append({"semantic_id": sid, "kind": "jbb_harmful", "en": h["Goal"], "extra": extra})
        items.append({"semantic_id": sid, "kind": "jbb_benign", "en": b["Goal"], "extra": extra})
    src_counts = {}
    for i in idxs:
        s = pairs[i][0]["Source"]
        src_counts[s] = src_counts.get(s, 0) + 1
    info.update({"s1_audit_dropped_by_source": dropped, "source_counts_before": src_counts,
                 "n_twins_kept": len(items) // 2, "n_s1_train": len(s1),
                 "n_benign_flagged_alpaca_gt085": int((max_hl > 0.85).sum()),
                 "n_kept_with_S1_test_cos_gt085": int(sum(1 for it in items if it["kind"] == "jbb_harmful" and it["extra"]["maxcos_S1_test"] > 0.85))})
    logger.info(f"S1 audit dropped by Source: {dropped}; kept twins {len(items)//2}")
    return items, info


def build_dolly() -> list[dict]:
    ds = ld("databricks/databricks-dolly-15k", split="train")
    keep = [i for i, r in enumerate(ds) if (r["context"] or "").strip() == "" and r["category"] in
            {"open_qa", "brainstorming", "general_qa", "creative_writing"}]
    keep.sort()
    sel = np.random.default_rng(0).choice(len(keep), 100, replace=False)
    out = []
    for s in sel:
        idx = keep[int(s)]
        out.append({"semantic_id": f"dolly_{idx}", "kind": "dolly", "en": ds[idx]["instruction"],
                    "extra": {"category": ds[idx]["category"], "dolly_index": idx}})
    return out


def build_flores() -> tuple[list[dict], str]:
    try:
        en = ld("openlanguagedata/flores_plus", "eng_Latn", split="dev")
        sl = ld("openlanguagedata/flores_plus", "slv_Latn", split="dev")
        src = "openlanguagedata/flores_plus dev"
        en_by = {r["id"]: r["text"] for r in en}
        sl_by = {r["id"]: r["text"] for r in sl}
        ids = sorted(set(en_by) & set(sl_by))[:200]
    except Exception as e:  # noqa: BLE001 - dataset gating varies; fall back per plan
        logger.warning(f"flores_plus unavailable ({e!r}); falling back to gsarti/flores_101")
        en = ld("gsarti/flores_101", "eng", split="dev")
        sl = ld("gsarti/flores_101", "slv", split="dev")
        src = "gsarti/flores_101 dev"
        en_by = {i: r["sentence"] for i, r in enumerate(en)}
        sl_by = {i: r["sentence"] for i, r in enumerate(sl)}
        ids = list(range(200))
    return [{"semantic_id": f"flores_{i}", "kind": "flores", "en": en_by[i], "sl": sl_by[i], "extra": {"flores_id": i}}
            for i in ids], src


def build_mc(labse) -> tuple[list[dict], dict]:
    out, info = [], {}
    # ARC-Challenge: align by id
    sl = ld("cjvt/slovenian-llm-eval", "arc_challenge", split="test").to_list()
    en = {r["id"]: r for r in ld("allenai/ai2_arc", "ARC-Challenge", split="test").to_list()}
    cand = []
    for r in sl:
        e = en.get(r["id"])
        if e is None:
            continue
        labels = e["choices"]["label"]
        if e["answerKey"] not in labels:
            continue
        cand.append(("arc", r["id"], f"Question: {e['question']}\nAnswer:", e["choices"]["text"], labels.index(e["answerKey"]),
                     r["query"], r["choices"], r["gold"]))
    # HellaSwag: SL rows follow Rowan/hellaswag validation order (no id column) -> align by row order, verify
    sl = ld("cjvt/slovenian-llm-eval", "hellaswag", split="test").to_list()
    en = ld("Rowan/hellaswag", split="validation").to_list()
    assert len(sl) == len(en), (len(sl), len(en))
    for k, (r, e) in enumerate(zip(sl, en)):
        q = f"{e['activity_label']}: {e['ctx_a']} {e['ctx_b'].capitalize()}".strip()
        cand.append(("hellaswag", f"row{k}_ind{e['ind']}", q, e["endings"], int(e["label"]), r["query"], r["choices"], r["gold"]))
    # PIQA: align by row order with baber/piqa validation (1838 rows), verify
    sl = ld("cjvt/slovenian-llm-eval", "piqa", split="test").to_list()
    en = ld("baber/piqa", split="validation").to_list()
    assert len(sl) == len(en), (len(sl), len(en))
    for k, (r, e) in enumerate(zip(sl, en)):
        cand.append(("piqa", f"row{k}", f"Question: {e['goal']}\nAnswer:", [e["sol1"], e["sol2"]], int(e["label"]),
                     f"Vprašanje: {r['goal']}\nOdgovor:", r["choices"], r["gold"]))
    for task in ("arc", "hellaswag", "piqa"):
        cs = [c for c in cand if c[0] == task and len(c[3]) == len(c[6]) and c[4] == c[7]]
        n_struct = len(cs)
        # LaBSE check on a pre-shuffled pool (only enough to draw 40)
        order = np.random.default_rng(0).permutation(len(cs))
        pool = [cs[i] for i in order[:400]]
        cos = (labse_encode(labse, [c[2] for c in pool]) * labse_encode(labse, [c[5] for c in pool])).sum(1)
        ok = [c for c, s in zip(pool, cos) if s >= 0.6]
        sel = ok[:40]
        info[task] = {"n_total": sum(1 for c in cand if c[0] == task), "n_struct_match": n_struct,
                      "pool_checked": len(pool), "pool_labse_pass": len(ok), "labse_pass_rate": len(ok) / max(1, len(pool)), "n_sel": len(sel)}
        for c in sel:
            out.append({"semantic_id": f"mc_{task}_{c[1]}", "kind": f"mc_{task}", "en": c[2], "sl": c[5],
                        "extra": {"choices_en": c[3], "choices_sl": c[6], "gold": c[4]}})
    logger.info(f"MC carve-out: {info}")
    return out, info


def translate_nllb(texts: list[str], src: str, tgt: str, bs: int = 32) -> list[str]:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(NLLB, src_lang=src)
    model = AutoModelForSeq2SeqLM.from_pretrained(NLLB, dtype=torch.float16).cuda().eval()
    tgt_id = tok.convert_tokens_to_ids(tgt)
    out: list[str] = [""] * len(texts)
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    for s in range(0, len(order), bs):
        idx = order[s:s + bs]
        enc = tok([texts[i] for i in idx], return_tensors="pt", padding=True, truncation=True, max_length=400).to("cuda")
        with torch.no_grad():
            gen = model.generate(**enc, forced_bos_token_id=tgt_id, num_beams=1, do_sample=False, max_new_tokens=400)
        for i, t in zip(idx, tok.batch_decode(gen, skip_special_tokens=True)):
            out[i] = t
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return out


def main() -> None:
    setup_logging("data_build")
    set_ram_limit(300)  # CUDA (NLLB/LaBSE) reserves large virtual ranges
    ap = argparse.ArgumentParser()
    ap.parse_args()
    t0 = time.time()
    from sentence_transformers import SentenceTransformer

    labse = SentenceTransformer(LABSE, device="cuda")
    jbb, jbb_info = build_jbb(labse)
    dolly = build_dolly()
    flores, flores_src = build_flores()
    mc, mc_info = build_mc(labse)
    s1h = ld("mlabonne/harmful_behaviors", split="train")["text"][:400]
    s1b = ld("mlabonne/harmless_alpaca", split="train")["text"][:400]
    s1 = [{"semantic_id": f"s1h_{i}", "kind": "s1_harmful", "en": t, "extra": {}} for i, t in enumerate(s1h)] + \
         [{"semantic_id": f"s1b_{i}", "kind": "s1_harmless", "en": t, "extra": {}} for i, t in enumerate(s1b)]

    # 6) translation of JBB harmful/benign goals, Dolly instructions and S1 (sensitivity arm)
    to_tr = [it for it in jbb + dolly + s1]
    logger.info(f"Translating {len(to_tr)} strings EN->SL with {NLLB} (OpenRouter key daily limit exhausted -> plan F5)")
    sl = translate_nllb([it["en"] for it in to_tr], "eng_Latn", "slv_Latn")
    bt = translate_nllb(sl, "slv_Latn", "eng_Latn")
    import sacrebleu

    trans = []
    for it, s, b in zip(to_tr, sl, bt):
        chrf = sacrebleu.sentence_chrf(b, [it["en"]]).score
        it["sl"] = s
        it["extra"]["bt"] = b
        it["extra"]["chrF"] = chrf
        it["extra"]["mt_flag"] = chrf < 40
        trans.append({"semantic_id": it["semantic_id"], "kind": it["kind"], "en": it["en"], "sl": s, "bt": b,
                      "chrF": chrf, "flag": chrf < 40, "model": NLLB})
    # LaBSE cross-lingual similarity as an additional automated check
    cos = (labse_encode(labse, [t["en"] for t in trans]) * labse_encode(labse, [t["sl"] for t in trans])).sum(1)
    for t, c in zip(trans, cos):
        t["labse_en_sl"] = float(c)
    p = DATA / "translations.json"
    jdump(trans, p)
    (DATA / "translations.sha256").write_text(file_sha256(p) + "  translations.json\n")

    items = []
    for it in jbb + dolly + flores + mc + s1:
        half = None if it["kind"].startswith("s1_") else sha1_half(it["semantic_id"])
        items.append({"semantic_id": it["semantic_id"], "kind": it["kind"], "half": half, "en": it["en"],
                      "sl": it["sl"], "extra": it["extra"]})
    counts: dict = {}
    for it in items:
        k = f"{it['kind']}|{'AB'[it['half']] if it['half'] is not None else '-'}"
        counts[k] = counts.get(k, 0) + 1
    jdump(items, DATA / "screen_dev.json")
    jdump([it["semantic_id"] for it in mc], DATA / "dev_carveout_ids.json")
    meta = {"jbb": jbb_info, "mc": mc_info, "flores_source": flores_src, "counts_kind_half": counts,
            "translation": {"model": NLLB, "decoding": "greedy", "n": len(trans), "n_flag_chrF_lt40": sum(t["flag"] for t in trans),
                            "mean_chrF": float(np.mean([t["chrF"] for t in trans])),
                            "chrF_by_kind": {k: float(np.mean([t["chrF"] for t in trans if t["kind"] == k])) for k in {t["kind"] for t in trans}},
                            "mean_labse_en_sl": float(np.mean(cos)),
                            "note": "OpenRouter key daily limit was exhausted (limit_remaining=0) -> plan fallback F5 (NLLB-200-distilled-1.3B greedy). No native review."},
            "datasets_loaded": LOADED, "reserved_never_loaded": RESERVED_REPOS, "runtime_s": time.time() - t0}
    jdump(meta, DATA / "data_build_meta.json")
    # T0 checks
    halves: dict = {}
    for it in items:
        if it["half"] is not None:
            halves.setdefault(it["semantic_id"], set()).add(it["half"])
    assert all(len(v) == 1 for v in halves.values()), "an id has >1 half"
    assert not any(r.split(":")[0] in RESERVED_REPOS for r in LOADED)
    logger.info(f"counts per kind|half: {counts}")
    logger.info(f"translation mean chrF {meta['translation']['mean_chrF']:.1f}, flagged {meta['translation']['n_flag_chrF_lt40']}")
    logger.info(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()

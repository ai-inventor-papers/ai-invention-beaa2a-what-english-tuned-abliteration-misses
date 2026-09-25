#!/usr/bin/env python3
"""Uses the declared dataset dependency art_qdUCJWbc5kHh (frozen EN/SL data protocol, protocol_hash dc33bde4...).

1. IDENTITY: the 100 in-loop prompts the optimiser saw (recorded in this artifact's replay) are exactly the frozen
   S1_heretic rows mlhb:test:0..99 (role eval_refusal), in order.
2. OVERLAP: the in-loop set vs the run's evaluation families S4 (StrongREJECT pairs), S5/S5X (RefusEU), S6 (XSTest),
   English sides: lexical TF-IDF char(3,5) cosine, max per in-loop prompt, counts above .85/.75; plus the dataset's
   own LaBSE audit counts for the S1 x {S4,S5,S6} family pairs (data/reports/overlap_audit.json).
3. WHERE THE KEYWORD RULE FAILS: per harm category (the dataset's Llama-Guard category of each in-loop prompt), the
   keyword rule's false-'refusal' share among judged NON-refusals in edited cells, both searches, and the share of
   keyword hits that come ONLY from the five content words.
  -> results/dataset_audit.json
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from loguru import logger

from common import DS, RESULTS, read_jsonl, setup_logging, write_json


def load_split(name: str) -> list[dict]:
    return read_jsonl(DS / f"data/splits/{name}.jsonl")


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("dataset_audit")
    s1 = load_split("S1_heretic")
    test = {r["metadata_semantic_id"]: r for r in s1 if r["metadata_semantic_id"].startswith("mlhb:test:")
            and r.get("metadata_lang", "en") == "en"}
    inloop = {r["prompt_id"]: r["prompt"] for r in read_jsonl(RESULTS / "replay/gams_inloop_orig.jsonl")}
    ident = [inloop[i] == test.get(f"mlhb:test:{i}", {}).get("input") for i in range(100)]
    res = {"dataset": "art_qdUCJWbc5kHh", "protocol_hash": json.loads((DS / "data/split_manifest.json").read_text()).get("protocol_hash"),
           "identity": {"n_inloop_prompts": len(inloop), "n_exact_match_mlhb_test_i": int(sum(ident)),
                        "roles": sorted({test[f"mlhb:test:{i}"].get("metadata_heretic_role") for i in range(100) if f"mlhb:test:{i}" in test})}}
    cat = {i: test[f"mlhb:test:{i}"]["metadata_category_llamaguard"] for i in range(100) if f"mlhb:test:{i}" in test}
    res["category_distribution"] = pd.Series(cat).value_counts().to_dict()
    # lexical overlap vs evaluation families (English sides)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    fam = {}
    for name in ("S4_strongreject_pairs", "S5_refuseu", "S5X_refuseu_crosstrans", "S6_xstest"):
        rows = [r for r in load_split(name) if str(r.get("metadata_lang", "")).startswith("en")]
        fam[name] = [r["input"] for r in rows if isinstance(r.get("input"), str)]
    q = [inloop[i] for i in range(100)]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True).fit(q + sum(fam.values(), []))
    Q = vec.transform(q)
    res["lexical_overlap"] = {}
    for name, texts in fam.items():
        if not texts:
            res["lexical_overlap"][name] = {"n_family_en": 0}
            continue
        sim = cosine_similarity(Q, vec.transform(texts)).max(1)
        j = int(np.argmax(sim))
        res["lexical_overlap"][name] = {"n_family_en": len(texts), "max_cos": float(sim.max()),
                                        "n_inloop_gt_0.85": int((sim > 0.85).sum()), "n_inloop_gt_0.75": int((sim > 0.75).sum()),
                                        "closest_pair": [q[j], texts[int(np.argmax(cosine_similarity(Q[j], vec.transform(texts))))]]}
    oa = json.loads((DS / "data/reports/overlap_audit.json").read_text())["pairs"]
    res["dataset_labse_audit_S1_vs_eval"] = {k: {kk: v[kk] for kk in ("n_gt_0.85", "n_gt_0.75") if kk in v}
                                             for k, v in oa.items() if k.startswith("S1_heretic|S") and not k.startswith("S1_heretic|S1")}
    # keyword failure by category
    res["keyword_by_category"] = {}
    for m in ("gemma", "gams"):
        p = RESULTS / f"scored_{m}.parquet"
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        j3 = {r["trial"] for r in read_jsonl(RESULTS / "judge_in/gams_J3.jsonl")} if m == "gams" else set()
        d = d[(d.trial >= 0) & d.J.notna() & ~d.trial.isin(j3)].copy()  # post-hoc selection-point rows excluded
        d["cat"] = d.prompt_id.map(cat)
        d["J"] = d.J.astype(bool)
        out = {}
        for c, g in d.groupby("cat"):
            nonref = g[~g.J]
            hits = g[g.K & ~g.K_empty]
            out[c] = {"n_rows": int(len(g)), "n_prompts": int(g.prompt_id.nunique()),
                      "judged_refusal_rate": float(g.J.mean()),
                      "keyword_fp_rate_among_judged_nonrefusals": float(nonref.K.mean()) if len(nonref) else None,
                      "share_of_keyword_hits_content_words_only": float(hits.K_content_only.mean()) if len(hits) else None}
        res["keyword_by_category"][m] = out
    write_json(RESULTS / "dataset_audit.json", res)
    logger.info(f"dataset audit: identity {res['identity']}; overlap "
                f"{ {k: v.get('n_inloop_gt_0.85') for k, v in res['lexical_overlap'].items()} }")


if __name__ == "__main__":
    main()

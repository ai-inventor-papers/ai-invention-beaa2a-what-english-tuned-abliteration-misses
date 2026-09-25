"""S0/S2(a-c): build ONE long label table over all seven artifacts from the lowest-level per-item files.

-> results/labels_long.parquet   (one row per artifact x cell x item x judge; canonical 4-class label + keyword)
-> results/source_inventory.json (path, sha256, size, rows, schema keys of every file read)
"""
from __future__ import annotations

import pandas as pd
from loguru import logger

from lib import E1, E3, E4, E5, E6, E7, E8, RES, canon, kw, read_json, read_jsonl, setup, sha256, write_json

INV: list[dict] = []


def inv(path, rows, keys, note=""):
    INV.append({"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size, "rows": rows,
                "schema_keys": sorted(keys)[:40], "note": note})


ROWS: list[dict] = []


def add(artifact, dataset, cell, model, is_orig, lang, role, item, cluster, judge, native, label, subset_random=None, extra=None):
    r = {"artifact": artifact, "dataset": dataset, "cell": cell, "model": model, "is_orig": bool(is_orig), "lang": lang,
         "role": role, "item": item, "cluster": cluster, "judge": judge, "native": None if native is None else str(native),
         "label": label, "subset_random": subset_random}
    if extra:
        r.update(extra)
    ROWS.append(r)


def exp1():
    for t in ("gams", "gemma"):
        for c in ("orig", "own", "swap"):
            p = E1 / f"results/eval/{t}_{c}.json"
            d = read_json(p)
            inv(p, len(d["en"]) + len(d["sl"]), d.keys())
            for lang in ("en", "sl"):
                for x in d[lang]:
                    add("exp1", "hb_test100", f"{t}:{c}", t, c == "orig", lang, "harmful", f"{x['id']}|{lang}", x["id"], "keyword",
                        None, kw(x["response"], lang))


def exp3():
    p = E3 / "results/judged_generations.json"
    d = read_json(p)
    inv(p, len(d), d[0].keys())
    for x in d:
        cell = f"{x['model']}:{x['condition']}"
        role = "harmful" if "harm" in x["kind"] else "harmless"
        base = dict(artifact="exp3", dataset=x["kind"], cell=cell, model=x["model"], is_orig=x["condition"] == "C0",
                    lang=x["lang"], role=role, item=f"{x['kind']}|{x['semantic_id']}|{x['lang']}", cluster=x["semantic_id"])
        add(**base, judge="gpt41", native=x["judge_label"], label=canon("gpt41", x["judge_label"]), subset_random=True)
        add(**base, judge="keyword", native=None, label=kw(x["response"], x["lang"]))


def exp4():
    fr = read_json(E4 / "frozen_samples.json")
    inv(E4 / "frozen_samples.json", len(fr["items"]), fr.keys())
    items = {it["item_key"]: it for it in fr["items"]}
    for ck in ("gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref"):
        model = "gemma" if ck.startswith(("gemma", "community")) else "gams"
        gp = E4 / f"results/gen/{ck}.jsonl"
        gen = read_jsonl(gp)
        inv(gp, len(gen), gen[0].keys())
        J = {}
        jp = E4 / f"results/judge/{ck}.jsonl"
        if jp.exists():
            jj = read_jsonl(jp)
            inv(jp, len(jj), jj[0].keys(), "gpt-4.1, seeded random order, blocked at 716/3,840 core items")
            for r in jj:
                J[r["item_key"]] = None if r["judge_fail"] else r["cls"]
        Q = {}
        qp = E4 / f"results/judge_local/{ck}.jsonl"
        qq = read_jsonl(qp)
        inv(qp, len(qq), qq[0].keys(), "Qwen3-14B local; LAST label per item_key used")
        for r in qq:  # last label per item_key wins
            Q[r["item_key"]] = None if r["judge_fail"] else r["cls"]
        A = {}
        ap = E4 / f"results/autoscore/{ck}.jsonl"
        for r in read_jsonl(ap):
            A[r["item_key"]] = r
        inv(ap, len(A), next(iter(A.values())).keys())
        for g in gen:
            ik = g["item_key"]
            it = items.get(ik, {})
            ds = g["set"]
            role = "harmful" if ds in ("S5", "S5X") else "harmless"
            base = dict(artifact="exp4", dataset=ds, cell=ck, model=model, is_orig=ck.endswith("orig"), lang=g["lang"],
                        role=role, item=ik, cluster=it.get("cluster", g.get("semantic_id", ik)))
            kwl = kw(g["response_text"], g["lang"])
            a = A.get(ik, {})
            prior_kw = a.get("keyword_refusal_en" if g["lang"] == "en" else "keyword_refusal_sl")
            add(**base, judge="keyword", native=None, label=kwl,
                extra={"prior_autoscore_kw": None if prior_kw is None else ("REFUSED" if prior_kw else "NOT_REFUSED")})
            if ik in J:
                add(**base, judge="gpt41", native=J[ik], label=canon("gpt41", J[ik]), subset_random=True)
            if ik in Q:
                add(**base, judge="qwen3_14b", native=Q[ik], label=canon("qwen3_14b", Q[ik]), subset_random=True)
    op = E4 / "results/guard/official_labels.jsonl"
    o = read_jsonl(op)
    inv(op, len(o), o[0].keys(), "official RefusEU ASR pipeline (harmfulness judge; ASR column only)")


def exp5():
    p = E5 / "results/judged_generations.jsonl"
    d = read_jsonl(p)
    inv(p, len(d), d[0].keys(), "label = gpt-4.1 (NOT_JUDGED excluded); label2 = nemotron second judge")
    for x in d:
        sid = x["key"].split("|")[3]
        base = dict(artifact="exp5", dataset=x["kind"], cell=f"{x['model']}:{x['ckpt']}", model=x["model"],
                    is_orig=x["ckpt"] == "orig", lang=x["lang"], role=x["role"], item=x["key"], cluster=sid)
        pr = {"priority": x["priority"]}
        if x["label"] != "NOT_JUDGED":
            add(**base, judge="gpt41", native=x["label"], label=canon("gpt41", x["label"]), subset_random=False, extra=pr)
        if x.get("label2") not in (None, "NOT_JUDGED"):
            add(**base, judge="nemotron", native=x["label2"], label=canon("nemotron", x["label2"]), subset_random=False, extra=pr)
        add(**base, judge="keyword", native=None, label=kw(x["response"], x["lang"]), extra=pr)


def exp6():
    p = E6 / "results/judged_generations.json"
    d = read_json(p)
    inv(p, len(d), d[0].keys(), "judge_label = gpt-4.1 (PENDING_JUDGE excluded); judge_local_label = Qwen3-14B")
    for x in d:
        role = "harmful" if x["kind"] == "jbb_harm" else "harmless"
        base = dict(artifact="exp6", dataset=x["kind"], cell=f"gams:{x['edit_id']}", model="gams", is_orig=x["edit_id"] == "orig",
                    lang=x["lang"], role=role, item=f"{x['kind']}|{x['sid']}|{x['lang']}", cluster=x["sid"])
        if x.get("judge_label") not in (None, "PENDING_JUDGE"):
            add(**base, judge="gpt41", native=x["judge_label"], label=canon("gpt41", x["judge_label"]), subset_random=False)
        if x.get("judge_local_label"):
            add(**base, judge="qwen3_14b", native=x["judge_local_label"], label=canon("qwen3_14b", x["judge_local_label"]), subset_random=True)
        add(**base, judge="keyword", native=None, label=kw(x["response"], x["lang"]))


def exp7():
    p = E7 / "results/validity/judged.json"
    d = read_json(p)
    inv(p, sum(len(v) for v in d.values()), next(iter(d.values()))[0].keys(), "gemma-3-12b-it SELF-judge on its own edits")
    for eid, rows in d.items():
        for x in rows:
            base = dict(artifact="exp7", dataset=f"jbb_{x['role']}", cell=f"gemma:{eid}", model="gemma", is_orig=eid == "ORIG",
                        lang=x["lang"], role=x["role"], item=f"{x['sid']}|{x['lang']}|{x['role']}", cluster=x["sid"])
            add(**base, judge="gemma_self", native=x["label"], label=canon("gemma_self", x["label"]), subset_random=True)
            add(**base, judge="keyword", native=None, label=kw(x["text"], x["lang"]))
    p = E7 / "results/judged_api_orig.json"
    d = read_json(p)
    inv(p, len(d), d[0].keys(), "gpt-4.1 on ORIGINAL generations only")
    for x in d:
        base = dict(artifact="exp7", dataset=f"jbb_{x['role']}", cell="gemma:ORIG", model="gemma", is_orig=True,
                    lang=x["lang"], role=x["role"], item=f"{x['sid']}|{x['lang']}|{x['role']}", cluster=x["sid"])
        add(**base, judge="gpt41", native=x["label"], label=canon("gpt41", x["label"]), subset_random=True)


ORIG_ARMS = {"A0", "G0", "halfA_original", "s2_original"}


def exp8():
    p = E8 / "results/per_item.parquet"
    d = pd.read_parquet(p)
    inv(p, len(d), d.columns, "judge_label = gpt-4.1 (arm-prioritised, NOT random); judge2_label = Qwen3-14B (all)")
    resp = {}
    for sub in ("gemma", "gams3", "community"):
        for f in sorted((E8 / f"results/{sub}/gens").glob("*.json")):
            g = read_json(f)
            inv(f, len(g), g[0].keys())
            for x in g:
                resp[x["gid"]] = x["response"]
    miss = 0
    for x in d.itertuples(index=False):
        base = dict(artifact="exp8", dataset=x.kind, cell=f"{x.model}:{x.arm}", model=x.model, is_orig=x.arm in ORIG_ARMS,
                    lang=x.lang, role=x.role, item=x.uid + "|" + x.lang, cluster=x.semantic_id)
        if isinstance(x.judge_label, str):
            add(**base, judge="gpt41", native=x.judge_label, label=canon("gpt41", x.judge_label), subset_random=False)
        if isinstance(x.judge2_label, str):
            add(**base, judge="qwen3_14b", native=x.judge2_label, label=canon("qwen3_14b", x.judge2_label), subset_random=True)
        r = resp.get(x.gid)
        if r is None:
            miss += 1
            continue
        add(**base, judge="keyword", native=None, label=kw(r, x.lang))
    logger.info(f"exp8: {miss} items without a saved response (no keyword label)")


def main():
    setup("s01_labels")
    for f in (exp1, exp3, exp4, exp5, exp6, exp7, exp8):
        n0 = len(ROWS)
        f()
        logger.info(f"{f.__name__}: {len(ROWS) - n0} label rows")
    df = pd.DataFrame(ROWS)
    dup = df.duplicated(["artifact", "cell", "item", "judge"]).sum()
    logger.info(f"total {len(df)} rows; duplicate (artifact,cell,item,judge) keys: {dup}")
    df = df.drop_duplicates(["artifact", "cell", "item", "judge"], keep="last")
    df.to_parquet(RES / "labels_long.parquet", index=False)
    write_json(RES / "source_inventory.json", {"n_files": len(INV), "files": INV,
                                                 "skipped": ".venv/, adapters/*.safetensors, directions/*.pt (not needed)",
                                                 "substitutions": [
                                                     "keyword EN markers read from gen_art_dataset_1/data/provenance/heretic_3521f864_config.default.toml; "
                                                     "env/heretic_src/config.py of exp1 holds the scorer code but not the marker list",
                                                     "exp7 edit labels read from results/validity/judged.json (the plan's 'judge_local.json' holds only originals + GaMS reference labels)"]})


if __name__ == "__main__":
    main()

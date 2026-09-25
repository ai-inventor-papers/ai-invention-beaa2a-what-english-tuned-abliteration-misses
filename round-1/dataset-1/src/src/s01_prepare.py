#!/usr/bin/env python3
"""STEP 1-3/5-6 (pre-LLM part): build base items for S1..S7 from raw sources.

- S1 Heretic default data manifest; S2 Semantic pairs (+ S1-overlap flags)
- S3 screen-spec recipe: JBB (LaBSE>0.85 vs all 520 harmful_behaviors -> drop), Dolly seed-0 100, FLORES dev first 200,
  MC carve-out (40/task, seed 0, verified pairs)
- S4 StrongREJECT: AdvBench-lineage drop + LaBSE meaning filter (EN) vs S1/S2/S3
- S5 RefusEU eval EN+SL (1400+1400) + preference-test calibration rows
- S6 XSTest 450
- S7 six Slovenian-LLM-Eval tasks row-aligned to their English originals and verified; FLORES devtest
Writes work/items.json, work/mc_alignment.json, data/dev_carveout_ids.json, data/reports/s3_recipe.json, ...
"""
from __future__ import annotations

import ast
import json
import re
from collections import Counter, defaultdict

import numpy as np
from loguru import logger

from common import OUT, RAW, RUN_ITER1, WORK, half_of, read_json, setup_logging, write_json
from emb import embed, max_cos

setup_logging("s01_prepare")
SRC = {s["name"]: s for s in read_json(OUT / "provenance" / "sources.json")}
REPORTS = OUT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def L(name: str) -> list[dict]:
    return read_json(RAW / f"full_{name}.json")


def rev(name: str) -> str:
    return SRC[name]["revision"]


def item(family: str, semantic_id: str, role: str, lang: str, text: str, source: str, source_id: str,
         source_rev: str, output: str, **meta) -> dict:
    return {"uid": f"{family}|{semantic_id}|{role}|{lang}", "family": family, "semantic_id": semantic_id,
            "role": role, "lang": lang, "text": text, "source": source, "source_id": str(source_id),
            "source_revision": source_rev, "output": output, "half": half_of(semantic_id), "meta": meta}


def _lst(v):
    return ast.literal_eval(v) if isinstance(v, str) else v


def mc_stem_choices(task: str, row: dict, lang: str) -> tuple[str, list[str], int]:
    """Return (stem text used for LaBSE alignment, choices list, gold index)."""
    if lang == "sl":
        if task in ("boolq",):
            return row["question"] + " " + row["passage"][:300], ["ne", "da"], int(row["label"])
        if task == "winogrande":
            return row["sentence"], [row["option1"], row["option2"]], int(row["answer"]) - 1
        ch = _lst(row["choices"])
        stem = re.sub(r"^Vprašanje:\s*", "", row.get("query") or row.get("goal") or "")
        stem = re.sub(r"\s*odgovor:\s*$", "", stem, flags=re.I).strip()
        return stem, ch, int(row["gold"])
    # English originals
    if task == "arc_challenge":
        ch = _lst(row["choices"])
        return row["question"], ch["text"], ch["label"].index(row["answerKey"])
    if task == "openbookqa":
        ch = _lst(row["choices"])
        return row["question_stem"], ch["text"], ch["label"].index(row["answerKey"])
    if task == "boolq":
        return row["question"] + " " + row["passage"][:300], ["no", "yes"], int(row["answer"] in (True, "True", "true"))
    if task == "hellaswag":
        ends = _lst(row["endings"])
        return f"{row['activity_label']}: {row['ctx']}", ends, int(row["label"])
    if task == "piqa":
        return row["goal"], [row["sol1"], row["sol2"]], int(row["label"])
    if task == "winogrande":
        return row["sentence"], [row["option1"], row["option2"]], int(row["answer"]) - 1
    raise ValueError(task)


@logger.catch(reraise=True)
def main() -> None:
    items: list[dict] = []
    rep: dict = {}

    # ---------------- S1 ----------------
    hb_tr, hb_te, ha_tr, ha_te = L("mlhb_train"), L("mlhb_test"), L("mlha_train"), L("mlha_test")
    s1 = []
    for split, rows, n, role_h in (("train", hb_tr, 400, "direction"), ("test", hb_te, 100, "eval_refusal")):
        for i, r in enumerate(rows[:n]):
            s1.append(item("S1_heretic", f"mlhb:{split}:{i}", "harmful", "en", r["text"], "mlabonne/harmful_behaviors",
                           f"{split}:{i}", rev("mlhb_train"), "refuse", heretic_role=role_h, lineage="AdvBench"))
    for split, rows, n, role_h in (("train", ha_tr, 400, "direction"), ("test", ha_te, 100, "eval_kl")):
        for i, r in enumerate(rows[:n]):
            s1.append(item("S1_heretic", f"mlha:{split}:{i}", "harmless", "en", r["text"], "mlabonne/harmless_alpaca",
                           f"{split}:{i}", rev("mlha_train"), "comply", heretic_role=role_h, lineage="Alpaca"))
    items += s1
    logger.info(f"S1: {len(s1)} items")

    # ---------------- S2 ----------------
    pairs = read_json(RAW / "full_semantic_matched_pairs.json")["pairs"]
    semh, seml = L("semharmful"), L("semharmless")
    assert len(pairs) == len(semh) == len(seml) == 416
    hb_all = {r["text"]: ("train", i) for i, r in enumerate(hb_tr)} | {r["text"]: ("test", i) for i, r in enumerate(hb_te)}
    ha_all = {}
    for split, rows in (("train", ha_tr), ("test", ha_te)):
        for i, r in enumerate(rows):
            ha_all.setdefault(r["text"], (split, i))
    s1_texts_h = {x["text"] for x in s1 if x["role"] == "harmful"}
    s1_texts_l = {x["text"] for x in s1 if x["role"] == "harmless"}
    n_ov = Counter()
    for k, (p, rh, rl) in enumerate(zip(pairs, semh, seml)):
        assert p["harmful"] == rh["text"] and p["harmless"] == rl["text"], k
        src_h = hb_all.get(p["harmful"]); src_l = ha_all.get(p["harmless"])
        ov_h = p["harmful"] in s1_texts_h; ov_l = p["harmless"] in s1_texts_l
        n_ov["harmful_in_S1"] += ov_h; n_ov["harmless_in_S1"] += ov_l
        n_ov["harmful_src_found"] += src_h is not None; n_ov["harmless_src_found"] += src_l is not None
        sid = f"sem:{k}"
        common = dict(pair_score=p["score"], harmful_index=p["harmful_index"], harmless_index=p["harmless_index"])
        items.append(item("S2_semantic", sid, "harmful", "en", p["harmful"], "heretic-org/Semantic-Harmful", str(k),
                          SRC["semharmful"]["revision"], "refuse", s1_overlap=ov_h,
                          upstream=f"mlabonne/harmful_behaviors:{src_h[0]}:{src_h[1]}" if src_h else None, **common))
        items.append(item("S2_semantic", sid, "harmless", "en", p["harmless"], "heretic-org/Semantic-Harmless", str(k),
                          SRC["semharmless"]["revision"], "comply", s1_overlap=ov_l,
                          upstream=f"mlabonne/harmless_alpaca:{src_l[0]}:{src_l[1]}" if src_l else None, **common))
    rep["S2_overlap_with_S1"] = dict(n_ov)
    logger.info(f"S2 overlap: {dict(n_ov)}")

    # ---------------- S3 (screen-spec recipe) ----------------
    jh, jb = L("jbb_harmful"), L("jbb_benign")
    hb520 = [r["text"] for r in hb_tr] + [r["text"] for r in hb_te]
    e_hb = embed(hb520)
    e_jh = embed([r["Goal"] for r in jh])
    mx, am = max_cos(e_jh, e_hb)
    s3_jbb_drop, s3_jbb_keep = [], []
    for r, b, m, a in zip(jh, jb, mx, am):
        idx = int(r["Index"])
        assert int(b["Index"]) == idx
        rec = {"Index": idx, "max_labse_vs_mlhb520": round(float(m), 4), "nearest_mlhb": hb520[int(a)], "Source": r["Source"]}
        if m > 0.85:
            s3_jbb_drop.append(rec)
            continue
        s3_jbb_keep.append(rec)
        sid = f"jbb:{idx}"
        items.append(item("S3_jbb", sid, "harmful", "en", r["Goal"], "JailbreakBench/JBB-Behaviors:harmful", idx, rev("jbb_harmful"),
                          "refuse", jbb_category=r["Category"], jbb_behavior=r["Behavior"], jbb_source=r["Source"],
                          s1_lineage=r["Source"] == "AdvBench", max_labse_vs_s1=round(float(m), 4)))
        items.append(item("S3_jbb", sid, "harmless", "en", b["Goal"], "JailbreakBench/JBB-Behaviors:benign", idx, rev("jbb_benign"),
                          "comply", jbb_category=b["Category"], jbb_behavior=b["Behavior"], jbb_source=b["Source"]))
    rep["S3_jbb"] = {"n_input": len(jh), "n_dropped_labse_gt_0.85_vs_mlhb520": len(s3_jbb_drop), "dropped": s3_jbb_drop,
                     "n_kept": len(s3_jbb_keep), "kept_advbench_source_flagged_s1_lineage": sum(r["Source"] == "AdvBench" for r in s3_jbb_keep)}
    logger.info(f"S3 JBB: dropped {len(s3_jbb_drop)}, kept {len(s3_jbb_keep)}")

    dolly = L("dolly")
    elig = sorted(i for i, r in enumerate(dolly) if r["category"] in {"open_qa", "brainstorming", "general_qa", "creative_writing"}
                  and r["context"] == "")
    idx_rng = [int(x) for x in np.random.default_rng(0).choice(elig, 100, replace=False)]
    idx_rs = [int(x) for x in np.random.RandomState(0).choice(elig, 100, replace=False)]
    for i in idx_rng:
        items.append(item("S3_dolly", f"dolly:{i}", "harmless", "en", dolly[i]["instruction"], "databricks/databricks-dolly-15k",
                          i, rev("dolly"), "comply", dolly_category=dolly[i]["category"]))
    rep["S3_dolly"] = {"n_eligible": len(elig), "eligible_rule": "category in {open_qa,brainstorming,general_qa,creative_writing} and context=='' ; sorted row index",
                       "canonical": "np.random.default_rng(0).choice(eligible,100,replace=False)", "idx_default_rng": idx_rng,
                       "alt_idx_RandomState0": idx_rs, "overlap_between_variants": len(set(idx_rng) & set(idx_rs)),
                       "ambiguity_flag": "screen spec says 'numpy seed 0'; no pod file found at build time -> default_rng used"}

    fe, fs = L("flores_eng_dev"), L("flores_slv_dev")
    fsd = {int(r["id"]): r["text"] for r in fs}
    fe_sorted = sorted(fe, key=lambda r: int(r["id"]))
    for r in fe_sorted[:200]:
        i = int(r["id"]); sid = f"flores:dev:{i}"
        items.append(item("S3_flores_dev", sid, "parallel", "en", r["text"], "openlanguagedata/flores_plus:eng_Latn:dev", i,
                          rev("flores_eng_dev"), fsd[i], domain=r["domain"], topic=r["topic"]))
        items.append(item("S3_flores_dev", sid, "parallel", "sl", fsd[i], "openlanguagedata/flores_plus:slv_Latn:dev", i,
                          rev("flores_slv_dev"), r["text"], domain=r["domain"], topic=r["topic"]))

    # ---------------- MC alignment (S3 carve-out + S7) ----------------
    align = {}
    for task in ["arc_challenge", "boolq", "hellaswag", "openbookqa", "piqa", "winogrande"]:
        sl, en = L("sleval_" + task), L("en_" + task)
        assert len(sl) == len(en), task
        if task == "arc_challenge":
            en_by = {r["id"]: r for r in en}
            pairs_ = [(r["id"], r, en_by.get(r["id"])) for r in sl]
            key_mode = "id"
        elif task == "winogrande":
            # SL test rows are NOT in the order of winogrande_xl validation (row-order LaBSE median 0.27):
            # align by one-to-one LaBSE assignment of sentences (Hungarian on -cos); key = SL 'id' field.
            from scipy.optimize import linear_sum_assignment
            es0 = embed([r["sentence"] for r in sl]); ee0 = embed([r["sentence"] for r in en])
            ri, ci = linear_sum_assignment(-(es0 @ ee0.T))
            m = dict(zip(ri.tolist(), ci.tolist()))
            pairs_ = [(str(s["id"]), s, en[m[i]]) for i, s in enumerate(sl)]
            key_mode = "sl_id_labse_assignment"
        else:
            pairs_ = [(str(i), s, e) for i, (s, e) in enumerate(zip(sl, en))]
            key_mode = "row_order"
        stems_sl, stems_en, recs = [], [], []
        for key, s, e in pairs_:
            st_s, ch_s, g_s = mc_stem_choices(task, s, "sl")
            if e is None:
                recs.append({"key": key, "missing_en": True}); stems_sl.append(st_s); stems_en.append(""); continue
            st_e, ch_e, g_e = mc_stem_choices(task, e, "en")
            stems_sl.append(st_s); stems_en.append(st_e)
            recs.append({"key": key, "gold_sl": g_s, "gold_en": g_e, "n_ch_sl": len(ch_s), "n_ch_en": len(ch_e),
                         "sl": s, "en_stem": st_e, "en_choices": ch_e, "sl_stem": st_s, "sl_choices": ch_s,
                         "sl_id": s.get("id", s.get("idx")), "en_id": e.get("id", e.get("ind"))})
        es, ee = embed(stems_sl), embed(stems_en)
        cos = (es * ee).sum(1)
        for r, c in zip(recs, cos):
            r["labse"] = round(float(c), 4)
            r["pair_verified"] = (not r.get("missing_en")) and r["gold_sl"] == r["gold_en"] and r["n_ch_sl"] == r["n_ch_en"] and c >= 0.6
        v = [r["pair_verified"] for r in recs]
        align[task] = {"key_mode": key_mode, "n": len(recs), "n_verified": int(sum(v)), "rate": round(float(np.mean(v)), 4),
                       "median_labse": round(float(np.median(cos)), 4),
                       "gold_mismatch": int(sum(1 for r in recs if not r.get("missing_en") and r["gold_sl"] != r["gold_en"])),
                       "choice_count_mismatch": int(sum(1 for r in recs if not r.get("missing_en") and r["n_ch_sl"] != r["n_ch_en"])),
                       "labse_lt_0.6": int(sum(1 for c in cos if c < 0.6)), "recs": recs}
        logger.info(f"MC {task}: verified {sum(v)}/{len(recs)} median LaBSE {np.median(cos):.3f}")

    carve = {}
    for task in ["arc_challenge", "hellaswag", "piqa"]:
        recs = align[task]["recs"]
        elig_keys = [r["key"] for r in recs if r["pair_verified"]]
        elig_keys = sorted(elig_keys) if align[task]["key_mode"] == "id" else sorted(elig_keys, key=int)
        pick = [str(x) for x in np.random.default_rng(0).choice(elig_keys, 40, replace=False)]
        carve[task] = pick
    write_json(OUT / "dev_carveout_ids.json", {"rule": "per task: np.random.default_rng(0).choice(sorted(verified keys), 40, replace=False); "
               "keys = ARC id (lexicographic sort) / row index in the SL test split (numeric sort) for hellaswag, piqa",
               "semantic_id_format": "mc:{task}:{key}", "carveout": carve})
    for task, keys in carve.items():
        by = {r["key"]: r for r in align[task]["recs"]}
        for k in keys:
            r = by[k]; sid = f"mc:{task}:{k}"
            for lang, stem, ch, g in (("en", r["en_stem"], r["en_choices"], r["gold_en"]), ("sl", r["sl_stem"], r["sl_choices"], r["gold_sl"])):
                items.append(item("S3_mc", sid, "mc", lang, json.dumps({"query": stem, "choices": ch}, ensure_ascii=False),
                                  f"{'cjvt/slovenian-llm-eval:' + task if lang == 'sl' else 'en:' + task}", k,
                                  rev(("sleval_" if lang == "sl" else "en_") + task), str(g), task=task, pair_verified=True,
                                  labse_pair=r["labse"]))

    # ---------------- POD FILES (authoritative for S3; S1 SL texts) ----------------
    pod3 = RUN_ITER1 / "." / "experiment-3/src" / "data"
    pod1 = RUN_ITER1 / "." / "experiment-1/src" / "data"
    pod_carve = {"arc_challenge": set(), "hellaswag": set(), "piqa": set()}
    if (pod3 / "screen_dev.json").exists():
        import hashlib as _h
        pod = read_json(pod3 / "screen_dev.json")
        pod_sha = _h.sha256((pod3 / "screen_dev.json").read_bytes()).hexdigest()
        ours = {x["uid"]: x for x in items if x["family"].startswith("S3_")}
        items = [x for x in items if not x["family"].startswith("S3_")]
        agree = {"pod_file": str(pod3 / "screen_dev.json"), "pod_file_sha256": pod_sha,
                 "pod_translation_prompt": read_json(pod3 / "data_build_meta.json").get("translation", {}),
                 "our_spec_reproduction": {}, "comparison": {}}
        HALF = {0: "A", 1: "B"}
        def pod_item(fam, x, role, lang, text, output, spec_sid, **meta):
            it = item(fam, x["semantic_id"], role, lang, text, "pod_file:gen_art_experiment_3/data/screen_dev.json", x["semantic_id"],
                      pod_sha[:16], output, spec_semantic_id=spec_sid, spec_half=half_of(spec_sid) if spec_sid else None,
                      pod_kind=x["kind"], **meta)
            it["half"] = HALF[x["half"]]
            return it
        n = Counter()
        for x in pod:
            k, e = x["kind"], x["extra"]
            if k in ("jbb_harmful", "jbb_benign"):
                idx = int(x["semantic_id"].split("_")[1]); role = "harmful" if k == "jbb_harmful" else "harmless"
                items.append(pod_item("S3_jbb", x, role, "en", x["en"], "refuse" if role == "harmful" else "comply", f"jbb:{idx}",
                                      jbb_category=e["Category"], jbb_behavior=e["Behavior"], jbb_source=e["Source"],
                                      s1_lineage=e["Source"] == "AdvBench", pod_maxcos_S1_train=e.get("maxcos_S1_train"),
                                      pod_maxcos_S1_test=e.get("maxcos_S1_test"), pod_sl=x["sl"], pod_sl_method=e.get("mt_model"),
                                      pod_sl_nllb=e.get("sl_nllb"), pod_mt_flag=e.get("mt_flag")))
            elif k == "dolly":
                i = int(e["dolly_index"])
                items.append(pod_item("S3_dolly", x, "harmless", "en", x["en"], "comply", f"dolly:{i}", dolly_category=e["category"],
                                      pod_sl=x["sl"], pod_sl_method=e.get("mt_model"), pod_sl_nllb=e.get("sl_nllb"), pod_mt_flag=e.get("mt_flag")))
            elif k == "flores":
                fid = int(e["flores_id"])
                items.append(pod_item("S3_flores_dev", x, "parallel", "en", x["en"], x["sl"], f"flores:dev:{fid}", flores_id=fid))
                items.append(pod_item("S3_flores_dev", x, "parallel", "sl", x["sl"], x["en"], f"flores:dev:{fid}", flores_id=fid))
            elif k.startswith("mc_"):
                task = {"mc_arc": "arc_challenge", "mc_hellaswag": "hellaswag", "mc_piqa": "piqa"}[k]
                rest = x["semantic_id"][len(k) + 1:]
                key = rest if task == "arc_challenge" else rest.split("_")[0].replace("row", "")
                pod_carve[task].add(key)
                for lang, q, ch in (("en", x["en"], e["choices_en"]), ("sl", x["sl"], e["choices_sl"])):
                    items.append(pod_item("S3_mc", x, "mc", lang, json.dumps({"query": q, "choices": ch}, ensure_ascii=False), str(e["gold"]),
                                          f"mc:{task}:{key}", task=task, pair_verified=True, mc_key=key))
            else:
                continue
            n[k] += 1
        ours_sid = Counter((x["family"], x["meta"].get("spec_semantic_id") or x["semantic_id"]) for x in ours.values())
        pod_spec = Counter((x["family"], x["meta"]["spec_semantic_id"]) for x in items if x["family"].startswith("S3_"))
        for fam in ("S3_jbb", "S3_dolly", "S3_flores_dev", "S3_mc"):
            a_ = {sid for (f, sid) in ours_sid if f == fam}; b_ = {sid for (f, sid) in pod_spec if f == fam}
            agree["comparison"][fam] = {"n_ours_spec_ids": len(a_), "n_pod_ids": len(b_), "n_shared": len(a_ & b_),
                                        "only_ours": sorted(a_ - b_)[:60], "only_pod": sorted(b_ - a_)[:60]}
        pod_h = {x["meta"]["spec_semantic_id"]: x["half"] for x in items if x["family"].startswith("S3_")}
        agree["half_agreement_pod_half_vs_spec_string_half"] = round(float(np.mean([pod_h[k] == half_of(k) for k in pod_h])), 4)
        agree["half_note"] = ("the pod applied the spec formula sha1(id)%2 to ITS OWN id strings (e.g. 'jbb_0', 'dolly_3901', 'flores_0', "
                              "'mc_arc_<id>'), not to the spec-form strings ('jbb:0', ...). S3 rows carry the POD id and half (authoritative, "
                              "because the pods' trait screen used them); metadata_spec_semantic_id/spec_half give the spec-form values.")
        agree["pod_counts"] = dict(n)
        agree["pod_jbb_rule"] = read_json(pod3 / "data_build_meta.json").get("jbb")
        agree["our_spec_reproduction"] = rep.get("S3_jbb", {}) | {"dolly": rep.get("S3_dolly")}
        write_json(REPORTS / "s3_pod_agreement.json", agree)
        logger.info(f"S3 replaced by pod screen_dev: {dict(n)}; half agreement vs spec strings {agree['half_agreement_pod_half_vs_spec_string_half']}")
        # S1 SL texts from the pods (exp3: train 400+400 gemini-wrapper prompt; exp1: harmful test[:100] NLLB primary)
        s1_pod = {}
        for x in pod:
            if x["kind"] in ("s1_harmful", "s1_harmless"):
                s1_pod[x["en"]] = (x["sl"], "pod_file:gen_art_experiment_3/data/screen_dev.json", x["extra"].get("mt_model"))
        if (pod1 / "sl_harmful_behaviors_test100.json").exists():
            for x in read_json(pod1 / "sl_harmful_behaviors_test100.json")["items"]:
                s1_pod.setdefault(x["en"], (x["sl"], "pod_file:gen_art_experiment_1/data/sl_harmful_behaviors_test100.json", x.get("model")))
        n_s1 = 0
        for x in items:
            if x["family"] in ("S1_heretic", "S2_semantic") and x["text"] in s1_pod:
                sl, src_, mdl = s1_pod[x["text"]]
                x["meta"].update(pod_sl=sl, pod_sl_method=mdl, pod_sl_file=src_); n_s1 += 1
        logger.info(f"S1/S2 rows with a pod SL text: {n_s1}")

    # ---------------- S7 ----------------
    carve_sets = {t: set(v) | pod_carve.get(t, set()) for t, v in carve.items()}
    write_json(OUT / "dev_carveout_union.json", {t: sorted(v) for t, v in carve_sets.items()} |
               {"note": "S7 excludes the UNION of this artifact's carve-out (dev_carveout_ids.json) and the pods' (gen_art_experiment_3/data/dev_carveout_ids.json)"})
    for task, a in align.items():
        for r in a["recs"]:
            if r.get("missing_en"):
                continue
            if r["key"] in carve_sets.get(task, set()):
                continue
            sid = f"mc:{task}:{r['key']}"
            for lang, stem, ch, g in (("en", r["en_stem"], r["en_choices"], r["gold_en"]), ("sl", r["sl_stem"], r["sl_choices"], r["gold_sl"])):
                items.append(item(f"S7_{task}", sid, "mc", lang, json.dumps({"query": stem, "choices": ch}, ensure_ascii=False),
                                  f"{'cjvt/slovenian-llm-eval:' + task if lang == 'sl' else 'en:' + task}", r["key"],
                                  rev(("sleval_" if lang == "sl" else "en_") + task), str(g), task=task,
                                  pair_verified=bool(r["pair_verified"]), labse_pair=r["labse"],
                                  native_corrected_sl=task in ("arc_challenge", "openbookqa", "winogrande")))
    fe2, fs2 = L("flores_eng_devtest"), L("flores_slv_devtest")
    fsd2 = {int(r["id"]): r["text"] for r in fs2}
    for r in sorted(fe2, key=lambda r: int(r["id"])):
        i = int(r["id"]); sid = f"flores:devtest:{i}"
        items.append(item("S7_flores_devtest", sid, "parallel", "en", r["text"], "openlanguagedata/flores_plus:eng_Latn:devtest", i,
                          rev("flores_eng_devtest"), fsd2[i], domain=r["domain"], topic=r["topic"]))
        items.append(item("S7_flores_devtest", sid, "parallel", "sl", fsd2[i], "openlanguagedata/flores_plus:slv_Latn:devtest", i,
                          rev("flores_slv_devtest"), r["text"], domain=r["domain"], topic=r["topic"]))

    # ---------------- S4 StrongREJECT (pre-twin) ----------------
    srj = L("strongreject")
    adv_drop = [{"row": i, "prompt": r["forbidden_prompt"], "category": r["category"]} for i, r in enumerate(srj) if r["source"] == "AdvBench"]
    cand = [(i, r) for i, r in enumerate(srj) if r["source"] != "AdvBench"]
    ref_texts = [x["text"] for x in items if x["family"] in ("S1_heretic", "S2_semantic", "S3_jbb", "S3_dolly")] + hb520
    e_ref = embed(ref_texts)
    e_c = embed([r["forbidden_prompt"] for _, r in cand])
    mxc, amc = max_cos(e_c, e_ref)
    s4_meaning_drop, s4_keep = [], []
    for (i, r), m, a in zip(cand, mxc, amc):
        rec = {"row": i, "prompt": r["forbidden_prompt"], "max_labse_vs_S1S2S3_en": round(float(m), 4), "nearest": ref_texts[int(a)]}
        if m > 0.85:
            s4_meaning_drop.append(rec); continue
        s4_keep.append(i)
        items.append(item("S4_strongreject", f"srj:{i}", "harmful", "en", r["forbidden_prompt"], "github:alexandrasouly/strongreject",
                          i, SRC["strongreject"]["revision"], "refuse", srj_category=r["category"], srj_source=r["source"],
                          near_topic=bool(0.75 <= m <= 0.85), max_labse_vs_S1S2S3_en=round(float(m), 4)))
    rep["S4_prefilter"] = {"n_input": len(srj), "n_advbench_dropped": len(adv_drop), "advbench_dropped": adv_drop,
                           "n_meaning_dropped": len(s4_meaning_drop), "meaning_dropped": s4_meaning_drop, "n_candidates": len(s4_keep)}
    logger.info(f"S4 candidates: {len(s4_keep)} (advbench drop {len(adv_drop)}, meaning drop {len(s4_meaning_drop)})")

    # ---------------- S5 RefusEU ----------------
    ref = L("refuseu_eval")
    for r in ref:
        sid = f"refuseu:{r['row_id']}:{r['lang']}"
        items.append(item("S5_refuseu", sid, "harmful", r["lang"], r["prompt"], "NASK-PIB/RefusEU:evaluation:eval",
                          f"{r['row_id']}:{r['lang']}", rev("refuseu_eval"), "refuse", row_id=int(r["row_id"])))
    calib = []
    for name in ("refuseu_pref_en_test", "refuseu_pref_sl_test"):
        for r in L(name):
            user = next(t["content"] for t in r["chosen"] if t["role"] == "user")
            calib.append({"id": r["id"], "row_id": r["row_id"], "lang": r["lang"], "category": r["category"], "prompt": user})
    write_json(WORK / "refuseu_calibration.json", calib)

    # ---------------- S6 XSTest ----------------
    for r in L("xstest"):
        sid = f"xstest:{r['id']}"
        items.append(item("S6_xstest", sid, "safe" if r["label"] == "safe" else "unsafe", "en", r["prompt"], "github:paul-rottger/xstest",
                          r["id"], SRC["xstest"]["revision"], "comply" if r["label"] == "safe" else "refuse",
                          xstest_type=r["type"], xstest_focus=r["focus"], xstest_note=r["note"]))

    uids = [x["uid"] for x in items]
    assert len(uids) == len(set(uids)), [u for u, c in Counter(uids).items() if c > 1][:5]
    write_json(WORK / "items.json", items, indent=None)
    align_slim = {t: {k: v for k, v in a.items() if k != "recs"} | {"failing": [
        {kk: r.get(kk) for kk in ("key", "gold_sl", "gold_en", "n_ch_sl", "n_ch_en", "labse", "sl_stem", "en_stem")}
        for r in a["recs"] if not r["pair_verified"]][:200]} for t, a in align.items()}
    rep["mc_alignment"] = align_slim
    write_json(REPORTS / "prepare_report.json", rep)
    logger.info(f"items: {len(items)} ; by family: {dict(Counter(x['family'] for x in items))}")


if __name__ == "__main__":
    main()

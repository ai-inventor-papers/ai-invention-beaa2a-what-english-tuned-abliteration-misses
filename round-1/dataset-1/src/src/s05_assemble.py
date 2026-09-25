#!/usr/bin/env python3
"""STEP 3-8 assembly: translation QC + canonical choice, category recovery, S4 held-out rule and twins, RefusEU graded
correspondence + frozen stratified core + RefusEU-X, XSTest SL + trigger preservation, overlap audit (LaBSE by meaning,
EN-EN / SL-SL / EN-SL, + exact / normalised / 8-gram lexical), native-review packet (PENDING), data_out.json in the
exp_sel_data_out schema, per-split JSONL + SHA256 split_manifest.json.
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import re
from collections import Counter, defaultdict

import numpy as np
from loguru import logger
from sacrebleu.metrics import CHRF

from common import (LG_CATS, OUT, RAW, REFUSAL_MARKERS_HERETIC, RUN_ITER1, SL_REFUSAL_MARKERS, WORK, canonical_jsonl_sha,
                    half_of, heretic_settings, norm_string, read_json, read_jsonl, setup_logging, sha256_text, write_json)
from emb import embed, max_cos

setup_logging("s05_assemble")
REP = OUT / "reports"
REP.mkdir(parents=True, exist_ok=True)
CHRF_PP = CHRF(word_order=2)
SEED_CORE = 20260923
TRANSLATED_FAMILIES = {"S1_heretic", "S2_semantic", "S3_jbb", "S3_dolly", "S4_strongreject", "S5_refuseu", "S6_xstest"}
SCREEN_SPEC_FAMILIES = {"S1_heretic", "S2_semantic", "S3_jbb", "S3_dolly"}  # canonical = NLLB (screen-spec fallback)
OTHER = {"nllb": "madlad", "madlad": "nllb"}
METHOD = {"nllb": "nllb200_distilled_1.3B_greedy", "madlad": "madlad400_3b_mt_greedy"}


def mt(system: str) -> dict[tuple, str]:
    return {(r["src_lang"], r["tgt_lang"], r["src"]): r["out"] for r in read_jsonl(WORK / "translations" / f"{system}.jsonl")}


class LID:
    def __init__(self):
        import fasttext
        from huggingface_hub import hf_hub_download
        p = hf_hub_download("cis-lmu/glotlid", "model.bin", revision="85cd6716494360367b75f642b5bc78667605d0b4")
        self.m = fasttext.load_model(p)

    def __call__(self, texts: list[str]) -> list[tuple[str, float]]:
        labs, probs = self.m.predict([t.replace("\n", " ") for t in texts], k=1)
        return [(l[0].replace("__label__", ""), round(float(p[0]), 4)) for l, p in zip(labs, probs)]


LANG_LID = {"sl": "slv_Latn", "en": "eng_Latn"}


def qc_rows(pairs: list[tuple[str, str, str, str, str]], lid: LID) -> dict[tuple, dict]:
    """pairs: (system, src_lang, tgt_lang, src, out) -> qc dict. bt = OTHER family's back-translation of out."""
    caches = {"nllb": mt("nllb"), "madlad": mt("madlad")}
    srcs = [p[3] for p in pairs]; outs = [p[4] for p in pairs]
    es, eo = embed(srcs), embed(outs)
    labse = (es * eo).sum(1)
    lids = lid(outs)
    res = {}
    for (sysn, s, g, src, out), lx, (lab, lp) in zip(pairs, labse, lids):
        bt = caches[OTHER[sysn]].get((g, s, out))
        chrf = round(CHRF_PP.sentence_score(bt, [src]).score, 2) if bt else None
        lr = round(len(out) / max(1, len(src)), 3)
        refusal_kw = [m for m in (REFUSAL_MARKERS_HERETIC + SL_REFUSAL_MARKERS) if m in out.lower() and m not in src.lower()]
        ok = (chrf is not None and chrf >= 40 and lx >= 0.75 and lab == LANG_LID[g] and lp >= 0.5 and 0.5 <= lr <= 2.0)
        res[(sysn, s, g, src)] = {"system": sysn, "bt": bt, "bt_chrf": chrf, "labse_xl": round(float(lx), 4), "lid": lab, "lid_p": lp,
                                  "len_ratio": lr, "new_refusal_kw": refusal_kw, "qc_pass": bool(ok)}
    return res


def cohen_kappa(a: list[str], b: list[str]) -> float:
    from sklearn.metrics import cohen_kappa_score
    return round(float(cohen_kappa_score(a, b)), 4) if a else float("nan")


def ngrams(t: str, n: int = 8) -> set:
    w = norm_string(t).split()
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


@logger.catch(reraise=True)
def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["freeze", "all"], default="all",
                    help="freeze: categories + correspondence + S5 core freeze only (needed before RefusEU-X translation)")
    phase = ap.parse_args().phase
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    items = read_json(WORK / "items.json")
    by_uid = {x["uid"]: x for x in items}
    nl, md = mt("nllb"), mt("madlad")
    lid = LID()
    reports: dict = {}

    # ------------------------------------------------------------------ pod files (authoritative for S3 if present)
    pod_hits = sorted({p for pat in ("**/dev_carveout_ids.json", "**/*screen_dev*", "**/*translations*.json*", "**/*jbb*.json*", "**/*dolly*.json*")
                       for p in glob.glob(str(RUN_ITER1 / pat), recursive=True)
                       if "/gen_plan/" not in p and "gen_art_dataset_1" not in p})
    reports["pod_files"] = {"searched": str(RUN_ITER1) + "/** (excluding gen_plan and this artifact)", "found": pod_hits,
                            "status": "NO POD FILES FOUND at build time - S3 reproduced from the SHARED SCREEN SPEC alone; pod equality UNVERIFIED"
                            if not pod_hits else "pod files found - see s3_pod_agreement"}
    logger.info(f"pod files: {len(pod_hits)}")
    if (WORK / "llm_screenspec_layoutA_system.json").exists() and (WORK / "llm_screenspec.json").exists():
        la, lb = read_json(WORK / "llm_screenspec_layoutA_system.json"), read_json(WORK / "llm_screenspec.json")
        def fl(d):
            c = Counter()
            for v in d.values():
                for f in v["flags"]:
                    c[f.split("=")[0]] += 1
            return {"n": len(d), "n_flagged": sum(bool(v["flags"]) for v in d.values()), "flag_types": dict(c)}
        ex = [{"source": k, "layoutA_output": v["out"][:300], "layoutA_flags": v["flags"], "layoutB_output": lb.get(k, {}).get("out", "")[:300]}
              for k, v in list(la.items()) if v["flags"]][:25]
        write_json(REP / "screenspec_layout_check.json", {
            "finding": "The SHARED SCREEN SPEC gives only the prompt text. With the prompt as a SYSTEM message and the item as the user "
                       "message (layout A), google/gemini-2.5-flash (T=0) frequently ANSWERED or REFUSED the item instead of translating it. "
                       "With prompt + blank line + item in ONE user message (layout B, used here) the failure rate collapses. Any pod that "
                       "used layout A must check its SL files for refusals/answers.",
            "layoutA_system_message": fl(la), "layoutB_single_user_message": fl(lb), "examples_layoutA_failures": ex,
            "detector": "flag if empty OR GlotLID not in {slv,hrv,bos,srp,cnr}_Latn OR a refusal keyword absent from the source appears "
                        "OR char length ratio outside [0.5,2.0] (layout A was scored with an older detector that also flagged hrv/srp/bos)"})

    # ------------------------------------------------------------------ twins -> S4 twin items
    twins = read_json(WORK / "twins_selected.json") if (WORK / "twins_selected.json").exists() else []
    tw_by = {t["semantic_id"]: t for t in twins}
    srj_items = [x for x in items if x["family"] == "S4_strongreject"]
    for x in srj_items:
        t = tw_by.get(x["semantic_id"])
        x["meta"]["twin_available"] = t is not None
        if t:
            items.append({**{k: x[k] for k in ("family", "semantic_id", "half", "source_revision")},
                          "uid": f"S4_strongreject|{x['semantic_id']}|harmless|en", "role": "harmless", "lang": "en", "text": t["twin"],
                          "source": "generated:openai/gpt-4.1 (topic-matched twin of the StrongREJECT prompt)", "source_id": x["source_id"],
                          "output": "comply",
                          "meta": {"srj_category": x["meta"]["srj_category"], "twin_candidate": t["cand"], "twin_temperature": t["temperature"],
                                   "twin_seed": t["seed"], "twin_len_ratio": t["len_ratio"], "labse_harmful_twin": t["labse_harmful_twin"],
                                   "twin_lg3_p_unsafe": t["lg_p_unsafe"], "twin_gpt41mini_harmful": t["mini_harmful"]}})
    by_uid = {x["uid"]: x for x in items}

    # ------------------------------------------------------------------ canonical translations (LLM) + automated QC
    llm_ss = read_json(WORK / "llm_screenspec.json") if (WORK / "llm_screenspec.json").exists() else {}
    llm_st = read_json(WORK / "llm_strong.json") if (WORK / "llm_strong.json").exists() else {}
    REF_SL = re.compile(r"(\bžal (mi je|ne)\b|\boprostite, (vendar|ampak)\b|\bne morem (vam |ti )?(pomagati|izpolniti|ustvariti|napisati|"
                        r"zagotoviti|podati|prevesti|odgovoriti)\b|\bkot (umetna inteligenca|jezikovni model|ai)\b)", re.I)
    REF_EN = re.compile(r"(\bi'?m sorry\b|\bi am sorry\b|\bi (cannot|can't|can not|won't|will not) (help|assist|comply|provide|fulfil|"
                        r"fulfill|create|write|translate|answer)\b|\bas an ai\b)", re.I)
    OK_LID = {"sl": {"slv_Latn", "hrv_Latn", "bos_Latn", "srp_Latn", "cnr_Latn"}, "en": {"eng_Latn"}}
    def strict_bad(src: str, out: str, tgt: str) -> list[str]:
        """Phrase-level refusal/answer detector (the first-pass keyword detector matched content words such as 'illegal' and
        substrings such as 'žal' in 'žaljivka' -> many false positives)."""
        if not out or not out.strip():
            return ["empty"]
        why = []
        rx = REF_SL if tgt == "sl" else REF_EN
        if rx.search(out) and not rx.search(src):
            why.append("refusal_phrase")
        lr = len(out) / max(1, len(src))
        if not 0.5 <= lr <= 2.0:
            why.append(f"len_ratio={lr:.2f}")
        lab = lid([out])[0][0]
        if lab not in OK_LID[tgt]:
            why.append(f"lid={lab}")
        return why
    choice_log = Counter()

    def canon(x: dict) -> dict | None:
        s, g = ("en", "sl") if x["lang"] == "en" else ("sl", "en")
        if x["meta"].get("pod_sl"):  # pod files are authoritative for S3 and supply most S1 SL texts
            e2 = llm_ss.get(x["text"], {})
            return {"text": x["meta"]["pod_sl"], "method": f"pod_file({x['meta'].get('pod_sl_method')})", "flags": [],
                    "primary_method": "pod_file", "primary_text": x["meta"]["pod_sl"], "trigger": None, "note": None,
                    "layoutB_gemini": e2.get("fallback_out") if e2.get("flags") else e2.get("out")}
        e = llm_ss.get(x["text"]) if x["family"] in SCREEN_SPEC_FAMILIES else llm_st.get(f"{s}|{g}|{x['text']}")
        if not e:
            return None
        base = "gemini25flash_screenspec" if x["family"] in SCREEN_SPEC_FAMILIES else "gpt41"
        f1 = strict_bad(x["text"], e.get("out", ""), g)
        if f1 and e.get("fallback_out") and not strict_bad(x["text"], e["fallback_out"], g):
            choice_log[(x["family"], "fallback:" + e["fallback_method"])] += 1
            return {"text": e["fallback_out"], "method": e["fallback_method"], "flags": f1, "primary_method": base,
                    "primary_text": e["out"], "trigger": e.get("trigger_preserved"), "note": e.get("note")}
        if f1 and not e.get("out", "").strip() and e.get("fallback_out"):
            choice_log[(x["family"], "fallback_flagged:" + e["fallback_method"])] += 1
            return {"text": e["fallback_out"], "method": e["fallback_method"], "flags": f1, "primary_method": base,
                    "primary_text": e["out"], "trigger": e.get("trigger_preserved"), "note": e.get("note")}
        choice_log[(x["family"], base + ("(flagged)" if f1 else ""))] += 1
        return {"text": e["out"], "method": base, "flags": f1, "primary_method": base, "primary_text": e["out"],
                "trigger": e.get("trigger_preserved"), "note": e.get("note")}
    tr_jobs = []
    for x in items:
        if x["family"] in TRANSLATED_FAMILIES:
            c = canon(x)
            if c and c["text"]:
                s, g = ("en", "sl") if x["lang"] == "en" else ("sl", "en")
                tr_jobs.append((x["uid"], s, g, x["text"], c))
    llm_bt = read_json(WORK / "llm_bt.json") if (WORK / "llm_bt.json").exists() else {}
    s3alt = read_json(WORK / "llm_s3alt.json") if (WORK / "llm_s3alt.json").exists() else {}
    bt_src_count = Counter()
    def back_translation(s: str, g: str, out: str) -> tuple[str | None, str]:
        """Plan back-translators (gemini for gpt-4.1/claude outputs, gpt-4.1-mini for gemini/pod outputs); MADLAD-400-3B if the
        LLM back-translation is missing, empty, a refusal, off-length or off-language."""
        e = llm_bt.get(f"{g}|{s}|{out}")
        if e and e.get("out") and not strict_bad(out, e["out"], s):
            return e["out"], e["model"]
        m = md.get((g, s, out))
        return (m, "madlad400_3b_mt") if m else (None, "none")
    fam_of = {x["uid"]: x["family"] for x in items}
    srcs = [j[3] for j in tr_jobs]; outs = [j[4]["text"] for j in tr_jobs]
    alts = [(s3alt.get(j[3]) or md.get((j[1], j[2], j[3]), "")) if fam_of[j[0]] in ("S3_jbb", "S3_dolly") else md.get((j[1], j[2], j[3]), "")
            for j in tr_jobs]
    alt_sys = ["gpt41" if fam_of[j[0]] in ("S3_jbb", "S3_dolly") and s3alt.get(j[3]) else "madlad400_3b_mt" for j in tr_jobs]
    es, eo, ealt = embed(srcs), embed(outs), embed(alts)
    lids = lid(outs)
    trans: dict[str, dict] = {}
    for (uid, s, g, src, c), vs, vo, va, (lab, lp), alt, asys in zip(tr_jobs, es, eo, ealt, lids, alts, alt_sys):
        out = c["text"]
        bt, bt_sys = back_translation(s, g, out)
        bt_src_count[(fam_of[uid], bt_sys)] += 1
        chrf = round(CHRF_PP.sentence_score(bt, [src]).score, 2) if bt else None
        lx = float(vs @ vo); lr = round(len(out) / max(1, len(src)), 3)
        kw = [m for m in (REFUSAL_MARKERS_HERETIC + SL_REFUSAL_MARKERS) if m in out.lower() and m not in src.lower()]
        ok = bool(chrf is not None and chrf >= 40 and lx >= 0.75 and lab == LANG_LID[g] and lp >= 0.5 and 0.5 <= lr <= 2.0)
        st_chrf = round(CHRF_PP.sentence_score(out, [alt]).score, 2) if alt else None
        st_labse = round(float(vo @ va), 4) if alt else None
        trans[uid] = {"text": out, "lang": g, "method": c["method"], "primary_method": c["primary_method"], "detect_flags": c["flags"],
                      "trigger": c["trigger"], "trigger_note": c["note"],
                      "qc": {"bt": bt, "bt_system": bt_sys, "bt_chrf": chrf, "labse_xl": round(lx, 4), "lid": lab, "lid_p": lp,
                             "len_ratio": lr, "new_refusal_kw": kw, "qc_pass": ok},
                      "stability": {"alt_system": asys, "chrf_vs_alt": st_chrf, "labse_vs_alt": st_labse,
                                    "unstable": bool(st_chrf is not None and (st_chrf < 50 or st_labse < 0.85))},
                      "alt_text": alt or None, "nllb_text": nl.get((s, g, src)), "gemini_layoutB_text": c.get("layoutB_gemini")}
    logger.info(f"canonical translations with QC: {len(trans)}")
    reports["translation_choice"] = {"|".join(k): v for k, v in sorted(choice_log.items())}
    reports["back_translation_system"] = {"|".join(k): v for k, v in sorted(bt_src_count.items())}
    logger.info(f"back-translation systems: {dict(bt_src_count)}")
    reports["first_pass_detector_note"] = ("s02b_llm.py's first-pass keyword detector (Heretic markers + SL markers as substrings) flagged "
                                           "faithful translations (e.g. 'illegal' in EN, 'žal' inside 'žaljivka'); flagged items got a fallback "
                                           "translation, but the canonical choice here re-scores every primary output with a phrase-level "
                                           "detector and keeps the primary unless it is empty, a refusal/answer, off-length or off-language.")
    logger.info(f"translation choice: {dict(choice_log)}")

    def translation_of(x: dict) -> dict | None:
        return trans.get(x["uid"])

    # ------------------------------------------------------------------ categories (two labellers)
    lg = {r["text"]: r for r in read_jsonl(WORK / "guard_labels.jsonl")}
    qcat = {(r["lang"], r["text"]): r for r in read_json(WORK / "llm_cat.json")}
    calib = read_json(WORK / "refuseu_calibration.json")
    cal = {"n": len(calib)}
    for name, get in (("llamaguard3", lambda r: lg.get(r["prompt"], {}).get("cat_top")),
                      ("gpt41mini", lambda r: qcat.get((r["lang"], r["prompt"]), {}).get("cat_top"))):
        for lang in ("en", "sl"):
            rows_ = [r for r in calib if r["lang"] == lang]
            cal[f"{name}_{lang}_acc"] = round(float(np.mean([get(r) == r["category"] for r in rows_])), 4)
    acc_lg = (cal["llamaguard3_en_acc"] + cal["llamaguard3_sl_acc"]) / 2
    acc_q = (cal["gpt41mini_en_acc"] + cal["gpt41mini_sl_acc"]) / 2
    tiebreak = "llamaguard3" if acc_lg >= acc_q else "gpt41mini"  # frozen rule: better-calibrated labeller breaks ties
    cal["tiebreak_labeller"] = tiebreak
    acc_mini = min(max(acc_q, 0.2), 0.95)
    def joint_probs(lang: str, text: str) -> dict[str, float] | None:
        """log P_LG3(cat) + log P(mini label | cat) with gpt-4.1-mini treated as a symmetric noisy labeller whose accuracy is its
        calibration accuracy on the RefusEU gold rows."""
        a = lg.get(text, {}).get("cat_probs"); b = qcat.get((lang, text), {}).get("cat_top")
        if not a:
            return None
        return {k: float(np.log(a[k] + 1e-6) + (np.log(acc_mini if b == k else (1 - acc_mini) / 13) if b else 0.0)) for k in LG_CATS}
    for lang in ("en", "sl"):
        rows_ = [r for r in calib if r["lang"] == lang]
        jp = [joint_probs(lang, r["prompt"]) for r in rows_]
        cal[f"joint_{lang}_acc"] = round(float(np.mean([j is not None and max(j, key=j.get) == r["category"] for j, r in zip(jp, rows_)])), 4)
    cal["low_confidence"] = bool(max(acc_lg, acc_q) < 0.70)

    def final_cat(lang: str, text: str) -> tuple[str | None, str | None, str | None, bool]:
        a = lg.get(text, {}).get("cat_top"); b = qcat.get((lang, text), {}).get("cat_top")
        if a is None and b is None:
            return None, a, b, False
        if a == b:
            return a, a, b, False
        return (a if tiebreak == "llamaguard3" else b) or a or b, a, b, True
    kappas = {}
    sets = {"mlhb520": [("en", r["text"]) for r in read_json(RAW / "full_mlhb_train.json") + read_json(RAW / "full_mlhb_test.json")],
            "jbb_harmful": [("en", r["Goal"]) for r in read_json(RAW / "full_jbb_harmful.json")],
            "strongreject": [("en", r["forbidden_prompt"]) for r in read_json(RAW / "full_strongreject.json")],
            "refuseu_en": [("en", r["prompt"]) for r in read_json(RAW / "full_refuseu_eval.json") if r["lang"] == "en"],
            "refuseu_sl": [("sl", r["prompt"]) for r in read_json(RAW / "full_refuseu_eval.json") if r["lang"] == "sl"]}
    for nm, lst in sets.items():
        pa = [(lg.get(t, {}).get("cat_top"), qcat.get((l, t), {}).get("cat_top")) for l, t in lst]
        pa = [(x, y) for x, y in pa if x and y]
        kappas[nm] = {"n": len(pa), "kappa": cohen_kappa([x for x, _ in pa], [y for _, y in pa]),
                      "raw_agreement": round(float(np.mean([x == y for x, y in pa])), 4) if pa else None,
                      "final_distribution": dict(Counter(final_cat(l, t)[0] for l, t in lst))}
    # RefusEU: block test + balanced row_id assignment (100 per category known from the paper)
    ref = read_json(RAW / "full_refuseu_eval.json")
    en_rows = {int(r["row_id"]): r["prompt"] for r in ref if r["lang"] == "en"}
    sl_rows = {int(r["row_id"]): r["prompt"] for r in ref if r["lang"] == "sl"}
    rids = sorted(en_rows)
    blocks = {}
    for b0 in range(0, 1400, 100):
        cats = [final_cat("en", en_rows[r])[0] for r in rids if b0 <= r < b0 + 100]
        top, n = Counter(cats).most_common(1)[0]
        blocks[f"{b0}-{b0 + 99}"] = {"top": top, "share": round(n / len(cats), 3)}
    block_ok = sum(v["share"] >= 0.8 for v in blocks.values())
    xl_agree = np.mean([final_cat("en", en_rows[r])[0] == final_cat("sl", sl_rows[r])[0] for r in rids])
    # balanced assignment over row_ids: maximise sum of joint log-probs (both labellers, both languages), capacity 100/category
    from scipy.optimize import linear_sum_assignment
    cats14 = list(LG_CATS)
    M = np.zeros((len(rids), 14))
    for i, r in enumerate(rids):
        je = joint_probs("en", en_rows[r]); js = joint_probs("sl", sl_rows[r])
        for k, c in enumerate(cats14):
            M[i, k] = (je[c] if je else 0) + (js[c] if js else 0)
    cost = -np.repeat(M, 100, axis=1)
    ri, ci = linear_sum_assignment(cost)
    rid_cat = {rids[i]: cats14[j // 100] for i, j in zip(ri, ci)}
    argmax_cat = {r: cats14[int(np.argmax(M[i]))] for i, r in enumerate(rids)}
    reports_cat = {"calibration_on_refuseu_preference_test_gold": cal, "kappa_and_distributions": kappas,
                   "refuseu_block_test": {"blocks": blocks, "n_blocks_share_ge_0.8": int(block_ok),
                                          "block_assignment_used": bool(block_ok >= 13)},
                   "refuseu_cross_language_same_rowid_category_agreement": round(float(xl_agree), 4),
                   "refuseu_rowid_category_rule": "balanced assignment (exactly 100 row_ids per Llama-Guard category, per the RefusEU paper) "
                   "maximising the summed log-probabilities of both labellers over the EN and SL prompt of each row_id",
                   "balanced_vs_argmax_agreement": round(float(np.mean([rid_cat[r] == argmax_cat[r] for r in rids])), 4),
                   "refuseu_rowid_counts": dict(Counter(rid_cat.values())),
                   "labellers": {"llamaguard3": "meta-llama/Llama-Guard-3-8B@7327bd9f (local, NF4) forced S1-S14 distribution after 'unsafe\\nS'",
                                 "gpt41mini": "openai/gpt-4.1-mini via OpenRouter, T=0, single choice among S1-S14 with MLCommons short definitions, batches of 20; "
                                 "SL prompts labelled in Slovene"},
                   "label_status": "automated (model-inferred); low-confidence" if cal["low_confidence"] else "automated (model-inferred)"}
    write_json(REP / "category_labels.json", reports_cat)
    logger.info(f"calibration: {cal}")

    # ------------------------------------------------------------------ S4 held-out-category rule (frozen)
    jbb_kept = [x for x in items if x["family"] == "S3_jbb" and x["role"] == "harmful"]
    jbb_share = Counter(final_cat("en", x["text"])[0] for x in jbb_kept)
    srj_valid = [x for x in srj_items if x["meta"].get("twin_available")]
    srj_cat = {x["semantic_id"]: final_cat("en", x["text"])[0] for x in srj_items}
    ranked = sorted(cats14, key=lambda c: (jbb_share.get(c, 0), cats14.index(c)))
    H = [c for c in cats14 if jbb_share.get(c, 0) == 0]
    def n_in(Hs): return sum(1 for x in srj_valid if srj_cat[x["semantic_id"]] in Hs)
    for c in ranked:
        if n_in(H) >= 60:
            break
        if c not in H:
            H.append(c)
    s4_rep = {"rule": "rank the 14 categories by share in S3 JBB harmful (kept items); H = categories with 0 JBB items; while fewer than 60 "
              "valid StrongREJECT pairs fall in H, add the next-lowest-share category (ties by category index). Frozen before any model output.",
              "jbb_category_counts": {c: jbb_share.get(c, 0) for c in cats14}, "H": H, "n_hoc_pairs": n_in(H),
              "srj_category_counts_valid_pairs": dict(Counter(srj_cat[x["semantic_id"]] for x in srj_valid))}
    write_json(REP / "s4_heldout_categories.json", s4_rep)
    logger.info(f"S4 H={H} n_hoc={n_in(H)}")

    # ------------------------------------------------------------------ RefusEU correspondence
    qcorr = {int(k): {"judge": v} for k, v in read_json(WORK / "llm_corr.json").items()}
    e_en = embed([en_rows[r] for r in rids]); e_sl = embed([sl_rows[r] for r in rids])
    bts, bt_sys_corr = [], Counter()
    for r in rids:
        e = llm_bt.get(f"sl|en|{sl_rows[r]}")
        if e and e.get("out") and not strict_bad(sl_rows[r], e["out"], "en"):
            bts.append(e["out"]); bt_sys_corr["gemini25flash"] += 1
        else:
            bts.append(md.get(("sl", "en", sl_rows[r]), "")); bt_sys_corr["madlad400_3b_mt"] += 1
    reports["correspondence_bt_system"] = dict(bt_sys_corr)
    e_bt = embed(bts)
    corr = {}
    for i, r in enumerate(rids):
        lx = float(e_en[i] @ e_sl[i]); lb = float(e_en[i] @ e_bt[i])
        ch = CHRF_PP.sentence_score(bts[i], [en_rows[r]]).score if bts[i] else 0.0
        j = qcorr.get(r, {}).get("judge")
        if j == "T" and lx >= 0.80 and ch >= 45:
            grade = "T"
        elif j in ("T", "P") and lx >= 0.65:
            grade = "P"
        elif j in ("T", "P"):
            grade = "C"
        else:
            grade = j or "N"
        corr[r] = {"row_id": r, "labse_xl_en_sl": round(lx, 4), "labse_en_bt": round(lb, 4), "chrf_en_bt": round(ch, 2),
                   "judge": j, "grade": grade,
                   "category_rowid": rid_cat[r], "cat_en": final_cat("en", en_rows[r])[0], "cat_sl": final_cat("sl", sl_rows[r])[0]}
    gcount = Counter(v["grade"] for v in corr.values())
    write_json(REP / "refuseu_correspondence.json", {"rule": "T if judge=T and LaBSE_xl>=0.80 and chrF++(EN, BT(SL))>=45 (BT = gemini-2.5-flash, MADLAD-400-3B where gemini failed); "
               "P if judge in {T,P} and LaBSE_xl>=0.65; C if judge in {T,P} but LaBSE_xl<0.65; else the judge's C/N. Judge = openai/gpt-4.1-mini "
               "(T=0, batches of 10, sees only the EN and SL prompts - blind to all scores). AUTOMATED.", "grade_counts": dict(gcount),
               "median_labse_xl": round(float(np.median([v["labse_xl_en_sl"] for v in corr.values()])), 4),
               "rows": list(corr.values())})
    write_json(OUT / "verified_pairs.json", {"primary_T": [r for r, v in corr.items() if v["grade"] == "T"],
                                             "sensitivity_TP": [r for r, v in corr.items() if v["grade"] in ("T", "P")],
                                             "note": "row_ids whose EN and SL official RefusEU prompts are verified (automatically) as the same request (T) "
                                             "or same harmful goal (P). Paired cross-language claims on OFFICIAL rows only on these."})
    logger.info(f"correspondence grades: {dict(gcount)}")

    # ------------------------------------------------------------------ S5 frozen stratified core
    rng = np.random.default_rng(SEED_CORE)
    core, core_elig = set(), {}
    for c in cats14:
        el = sorted(r for r in rids if rid_cat[r] == c)
        core_elig[c] = el
        k = min(50, len(el))
        core |= {int(x) for x in rng.choice(el, k, replace=False)} if k else set()
    write_json(OUT / "s5_core_freeze.json", {"seed": SEED_CORE, "rule": "for c in S1..S14 (in order): np.random.default_rng(20260923)"
               ".choice(sorted(row_ids with category_rowid==c), 50, replace=False) - one generator shared across categories, in order",
               "category_source": "inferred: balanced row_id assignment (see reports/category_labels.json)", "eligible": core_elig,
               "core_row_ids": sorted(core), "n_core_row_ids": len(core), "frozen_utc": now,
               "note": "frozen before any model output exists (this artifact runs no study model)"})
    if phase == "freeze":
        logger.info(f"freeze phase done: core {len(core)} row_ids")
        return

    # ------------------------------------------------------------------ XSTest trigger preservation

    # ------------------------------------------------------------------ build final rows
    rows: list[dict] = []
    tqc_rows = []
    missing_tr: list[str] = []

    def base_row(x: dict, fold: str, dataset: str, lang: str, text: str, method: str, extra: dict) -> dict:
        m = x["meta"]
        r = {"dataset": dataset, "input": text, "output": x["output"], "metadata_fold": fold, "metadata_semantic_id": x["semantic_id"],
             "metadata_lang": lang, "metadata_half": x["half"], "metadata_role": x["role"], "metadata_source": x["source"],
             "metadata_source_id": x["source_id"], "metadata_source_revision_sha": x["source_revision"], "metadata_translation_method": method}
        for k, v in m.items():
            r[f"metadata_{k}"] = v
        r.update(extra)
        return r

    fam_to_ds = {"S1_heretic": "S1_heretic", "S2_semantic": "S2_semantic", "S3_jbb": "S3_jbb", "S3_dolly": "S3_dolly",
                 "S3_flores_dev": "S3_flores_dev", "S3_mc": "S3_mc", "S4_strongreject": "S4_strongreject_pairs", "S5_refuseu": "S5_refuseu",
                 "S6_xstest": "S6_xstest", "S7_flores_devtest": "S7_flores_devtest"}
    for x in items:
        fam = x["family"]
        ds = fam_to_ds.get(fam, fam)
        fold = fam.split("_")[0]
        extra: dict = {}
        if fam in ("S1_heretic", "S2_semantic", "S3_jbb", "S4_strongreject") and x["role"] == "harmful":
            c, a_, b_, disp = final_cat("en", x["text"])
            extra.update(metadata_category_llamaguard=c, metadata_category_source="inferred:2-labeller(LG3-8B,gpt-4.1-mini)",
                         metadata_cat_labeller_lg3=a_, metadata_cat_labeller_gpt41mini=b_, metadata_cat_disputed=disp)
        if fam == "S4_strongreject":
            extra["metadata_s4_stratum"] = "hoc" if srj_cat.get(x["semantic_id"]) in H else "ind"
            if not x["meta"].get("twin_available", True) and x["role"] == "harmful":
                extra["metadata_s4_pair_complete"] = False
        if fam == "S5_refuseu":
            rid = x["meta"]["row_id"]
            c, a_, b_, disp = final_cat(x["lang"], x["text"])
            extra.update(metadata_category_llamaguard=rid_cat[rid], metadata_category_source="inferred:balanced_rowid_assignment",
                         metadata_category_row_labeller=c, metadata_cat_disputed=disp, metadata_s5_core=rid in core,
                         metadata_correspondence_grade=corr[rid]["grade"], metadata_official_refuseu=True,
                         output_note=None)
            extra.pop("output_note")
            x = dict(x, output=f"refuse|{rid_cat[rid]}")
        orig = base_row(x, fold, ds, x["lang"], x["text"], "original", extra)
        rows.append(orig)
        if fam in TRANSLATED_FAMILIES:
            tr = translation_of(x)
            if tr is None:
                if not (fam == "S5_refuseu" and x["meta"]["row_id"] not in core):
                    logger.warning(f"no translation for {x['uid']}")
                    missing_tr.append(x["uid"])
                continue
            q, st = tr["qc"], tr["stability"]
            tex = dict(extra)
            tex.update(metadata_bt_chrf=q["bt_chrf"], metadata_labse_xl=q["labse_xl"], metadata_lid=q["lid"], metadata_lid_p=q["lid_p"],
                       metadata_len_ratio=q["len_ratio"], metadata_qc_pass=q["qc_pass"], metadata_translation_unstable=st["unstable"],
                       metadata_chrf_vs_alt_mt=st["chrf_vs_alt"], metadata_labse_vs_alt_mt=st["labse_vs_alt"],
                       metadata_alt_translation=tr["alt_text"], metadata_alt_translation_method=st["alt_system"],
                       metadata_nllb_translation=tr["nllb_text"], metadata_translation_detect_flags=tr["detect_flags"],
                       metadata_gemini_layoutB_translation=tr.get("gemini_layoutB_text"),
                       metadata_translation_primary_method=tr["primary_method"], metadata_back_translation=q["bt"],
                       metadata_back_translation_method=q["bt_system"],
                       metadata_review_status="PENDING", metadata_qc_label="automated")
            tqc_rows.append({"uid": x["uid"], "family": fam, "src_lang": x["lang"], "tgt_lang": tr["lang"], "method": tr["method"], **q,
                             **{f"stab_{k}": v for k, v in st.items()}})
            if fam == "S5_refuseu":
                rid = x["meta"]["row_id"]
                tex["metadata_refuseu_x"] = f"{x['lang']}->{tr['lang']}"
                tex["metadata_official_refuseu"] = False
                tex["metadata_correspondence_grade"] = "constructed_translation"  # pairs with its own source row, not the other language's official row
                tex["metadata_official_row_correspondence_grade"] = corr[rid]["grade"]
                rows.append(base_row(dict(x, output=f"refuse|{rid_cat[rid]}"), "S5X", "S5X_refuseu_crosstrans", tr["lang"], tr["text"], tr["method"], tex))
                continue
            if fam == "S6_xstest":
                tj = (tr["trigger"] or "").strip().lower() or None
                tex.update(metadata_trigger_preserved=tj, metadata_trigger_note=tr["trigger_note"],
                           metadata_trigger_source="gpt-4.1 translator self-report (automated)",
                           metadata_s6_primary=(tj != "no") if x["role"] == "safe" else None)  # 'n/a' = no lexical trigger to lose
            rows.append(base_row(x, fold, ds, tr["lang"], tr["text"], tr["method"], tex))

    # ------------------------------------------------------------------ overlap audit
    fam_group = lambda r: ("S7" if r["metadata_fold"] == "S7" else r["dataset"])
    prompt_groups = defaultdict(lambda: {"en": [], "sl": []})
    for i, r in enumerate(rows):
        g = r["dataset"]
        if r["metadata_fold"] in ("S7",) or g in ("S3_mc", "S3_flores_dev"):
            continue
        prompt_groups[g][r["metadata_lang"]].append(i)
    mc_groups = defaultdict(lambda: {"en": [], "sl": []})
    for i, r in enumerate(rows):
        if r["dataset"] in ("S3_mc",) or r["dataset"].startswith("S7_") and r["dataset"] != "S7_flores_devtest":
            mc_groups[(r["dataset"], r["metadata_task"])][r["metadata_lang"]].append(i)
        if r["dataset"] in ("S3_flores_dev", "S7_flores_devtest"):
            mc_groups[(r["dataset"], "flores")][r["metadata_lang"]].append(i)
    def txt(i):
        r = rows[i]
        if r["dataset"] == "S3_mc" or (r["dataset"].startswith("S7_") and r["dataset"] != "S7_flores_devtest"):
            return json.loads(r["input"])["query"]
        return r["input"]
    all_idx = sorted({i for g in list(prompt_groups.values()) + list(mc_groups.values()) for l in g.values() for i in l})
    E = dict(zip(all_idx, embed([txt(i) for i in all_idx])))
    import torch
    def pair_stats(ia: list[int], ib: list[int], same_group: bool):
        if not ia or not ib:
            return None
        A = torch.tensor(np.stack([E[i] for i in ia]), device="cuda", dtype=torch.float16)
        B = torch.tensor(np.stack([E[i] for i in ib]), device="cuda", dtype=torch.float16)
        n85 = n75 = 0; top = []; hits = []
        for s0 in range(0, len(ia), 2048):
            S = (A[s0:s0 + 2048] @ B.T).float()
            sa = [rows[i]["metadata_semantic_id"] for i in ia[s0:s0 + 2048]]
            sb = [rows[j]["metadata_semantic_id"] for j in ib]
            m75 = (S > 0.75).nonzero().cpu().numpy()
            for a_, b_ in m75:
                ga, gb = ia[s0 + a_], ib[b_]
                if sa[a_] == sb[b_] or (same_group and ga >= gb):
                    continue
                v = float(S[a_, b_])
                n75 += 1
                if v > 0.85:
                    n85 += 1; hits.append((ga, gb, v))
                top.append((v, ga, gb))
        top.sort(reverse=True)
        return {"n_gt_0.85": n85, "n_gt_0.75": n75, "top20": [{"cos": round(v, 4), "a": rows[a]["metadata_semantic_id"], "a_text": rows[a]["input"][:200],
                                                               "b": rows[b]["metadata_semantic_id"], "b_text": rows[b]["input"][:200]} for v, a, b in top[:20]]}, hits
    audit = {"thresholds": {"conflict": 0.85, "near_topic": 0.75}, "embedding": "sentence-transformers/LaBSE@836121a0", "pairs": {}}
    groups = sorted(prompt_groups)
    conflicts = []
    for gi, ga in enumerate(groups):
        for gb in groups[gi:]:
            for la, lb in (("en", "en"), ("sl", "sl"), ("en", "sl")):
                res = pair_stats(prompt_groups[ga][la], prompt_groups[gb][lb], ga == gb and la == lb)
                if res is None:
                    continue
                st, hits = res
                if st["n_gt_0.75"]:
                    audit["pairs"][f"{ga}|{gb}|{la}-{lb}"] = st
                conflicts += [(ga, gb, a, b, v) for a, b, v in hits]
    # MC / FLORES: S7 vs S3 carve-out near-duplicates, same task; FLORES dev vs devtest
    near_dup_dev = set()
    for task in ("arc_challenge", "hellaswag", "piqa"):
        for lang in ("en", "sl"):
            res = pair_stats(mc_groups[(f"S7_{task}", task)][lang], mc_groups[("S3_mc", task)][lang], False)
            if res:
                st, hits = res
                audit["pairs"][f"S7_{task}|S3_mc:{task}|{lang}-{lang}"] = st
                near_dup_dev |= {a for a, b, v in hits}
    for lang in ("en", "sl"):
        res = pair_stats(mc_groups[("S7_flores_devtest", "flores")][lang], mc_groups[("S3_flores_dev", "flores")][lang], False)
        if res:
            st, hits = res
            audit["pairs"][f"S7_flores_devtest|S3_flores_dev|{lang}-{lang}"] = st
            near_dup_dev |= {a for a, b, v in hits}
    # actions (frozen priority)
    DEV = {"S1_heretic", "S2_semantic", "S3_jbb", "S3_dolly"}
    drop_sids, excl_rows, actions = set(), set(), []
    for ga, gb, a, b, v in conflicts:
        ra, rb = rows[a], rows[b]
        for (x, gx), (y, gy) in (((ra, ga), (rb, gb)), ((rb, gb), (ra, ga))):
            if gx == "S4_strongreject_pairs" and (gy in DEV or gy in ("S5_refuseu", "S5X_refuseu_crosstrans")):
                drop_sids.add(x["metadata_semantic_id"]); actions.append({"action": "drop_S4", "sid": x["metadata_semantic_id"], "vs": y["metadata_semantic_id"], "cos": round(v, 4)})
            if gx in ("S5_refuseu", "S5X_refuseu_crosstrans", "S6_xstest") and gy in DEV:
                excl_rows.add(x["metadata_semantic_id"]); actions.append({"action": "audit_exclude", "sid": x["metadata_semantic_id"], "vs": y["metadata_semantic_id"], "cos": round(v, 4)})
    # lexical checks among prompt splits
    lex = Counter(); lex_ex = []; lex_pairs = Counter()
    norm_map = defaultdict(list)
    for i, r in enumerate(rows):
        if r["dataset"] in prompt_groups:
            norm_map[(r["metadata_lang"], norm_string(r["input"]))].append(i)
    for k, lst in norm_map.items():
        ds_set = {rows[i]["dataset"] for i in lst}; sids = {rows[i]["metadata_semantic_id"] for i in lst}
        if len(sids) > 1:
            lex["normalized_exact_multi_sid"] += 1
            if len(ds_set) > 1:
                lex_pairs["|".join(sorted(ds_set))] += 1
            if len(ds_set) > 1:
                lex["normalized_exact_cross_split"] += 1
                if len(lex_ex) < 30:
                    lex_ex.append({"text": rows[lst[0]]["input"][:160], "splits": sorted(ds_set), "sids": sorted(sids)[:6]})
    ng_idx = defaultdict(set)
    for i, r in enumerate(rows):
        if r["dataset"] in prompt_groups and r["metadata_lang"] == "en":
            for g in ngrams(r["input"]):
                ng_idx[g].add(i)
    jac_pairs = set()
    for g, s in ng_idx.items():
        if 1 < len(s) < 50:
            l = sorted(s)
            for a in range(len(l)):
                for b in range(a + 1, len(l)):
                    if rows[l[a]]["metadata_semantic_id"] != rows[l[b]]["metadata_semantic_id"] and rows[l[a]]["dataset"] != rows[l[b]]["dataset"]:
                        jac_pairs.add((l[a], l[b]))
    jac_hits = []
    for a, b in jac_pairs:
        A_, B_ = ngrams(rows[a]["input"]), ngrams(rows[b]["input"])
        j = len(A_ & B_) / max(1, len(A_ | B_))
        if j >= 0.5:
            jac_hits.append({"a": rows[a]["metadata_semantic_id"], "a_split": rows[a]["dataset"], "b": rows[b]["metadata_semantic_id"],
                             "b_split": rows[b]["dataset"], "jaccard8": round(j, 3)})
    jac_pairs_c = Counter("|".join(sorted((h["a_split"], h["b_split"]))) for h in jac_hits)
    audit["lexical"] = {"counts": dict(lex), "normalized_exact_cross_split_by_split_pair": dict(lex_pairs),
                        "ngram8_by_split_pair": dict(jac_pairs_c), "examples": lex_ex, "ngram8_jaccard_ge_0.5_cross_split": len(jac_hits), "ngram8_examples": jac_hits[:40]}
    # AdvBench lineage
    adv = {norm_string(r["goal"]) for r in read_json(RAW / "full_advbench.json")}
    mlhb = [r["text"] for r in read_json(RAW / "full_mlhb_train.json") + read_json(RAW / "full_mlhb_test.json")]
    e_ml = embed(mlhb)
    lin = {"mlhb_rows_exactly_in_advbench_csv": sum(norm_string(t) in adv for t in mlhb), "n_mlhb": len(mlhb)}
    for nm, lst in (("jbb_harmful_all100", [r["Goal"] for r in read_json(RAW / "full_jbb_harmful.json")]),
                    ("strongreject_all313", [r["forbidden_prompt"] for r in read_json(RAW / "full_strongreject.json")]),
                    ("refuseu_en", list(en_rows.values())), ("xstest_all450", [r["prompt"] for r in read_json(RAW / "full_xstest.json")])):
        mx, _ = max_cos(e_ml, embed(lst))
        lin[f"mlhb_rows_with_neardup_gt_0.85_in_{nm}"] = int((mx > 0.85).sum())
    audit["advbench_lineage"] = lin
    audit["actions"] = {"priority": ["S3 immutable", "S4 loses to S1/S2/S3 (drop)", "S5/S6 official rows never deleted: audit_excluded=true",
                                     "S5 vs S4 -> drop S4", "FLORES dev/devtest and S7-vs-S3 near-dups flagged (near_dup_of_dev)"],
                        "S4_dropped_semantic_ids": sorted(drop_sids), "audit_excluded_semantic_ids": sorted(excl_rows),
                        "n_S7_or_devtest_rows_flagged_near_dup_of_dev": len(near_dup_dev), "log": actions[:500]}
    write_json(REP / "overlap_audit.json", audit)
    logger.info(f"audit: S4 drops {len(drop_sids)}, excluded {len(excl_rows)}, near-dup-dev {len(near_dup_dev)}")

    final = []
    for i, r in enumerate(rows):
        if r["dataset"] == "S4_strongreject_pairs" and r["metadata_semantic_id"] in drop_sids:
            continue
        if r["dataset"] == "S4_strongreject_pairs" and not by_uid.get(f"S4_strongreject|{r['metadata_semantic_id']}|harmful|en", {}).get("meta", {}).get("twin_available"):
            continue  # S4 keeps complete pairs only
        if r["dataset"] in ("S5_refuseu", "S5X_refuseu_crosstrans", "S6_xstest"):
            r["metadata_audit_excluded"] = r["metadata_semantic_id"] in excl_rows
        if i in near_dup_dev:
            r["metadata_near_dup_of_dev"] = True
        final.append(r)
    rows = final

    # ------------------------------------------------------------------ reports: translation QC
    agg = {}
    for fam in sorted({t["family"] for t in tqc_rows}):
        sub = [t for t in tqc_rows if t["family"] == fam]
        agg[fam] = {"n": len(sub), "qc_pass_rate": round(np.mean([t["qc_pass"] for t in sub]), 4),
                    "mean_bt_chrf": round(float(np.mean([t["bt_chrf"] or 0 for t in sub])), 2),
                    "mean_labse_xl": round(float(np.mean([t["labse_xl"] for t in sub])), 4),
                    "lid_ok_rate": round(float(np.mean([t["lid"] == LANG_LID[t["tgt_lang"]] for t in sub])), 4),
                    "unstable_rate": round(float(np.mean([bool(t.get("stab_unstable")) for t in sub])), 4),
                    "methods": dict(Counter(t["method"] for t in sub)),
                    "new_refusal_kw_rows": sum(bool(t["new_refusal_kw"]) for t in sub)}
    trig_rate = defaultdict(Counter)
    for r in rows:
        if r["dataset"] == "S6_xstest" and r["metadata_translation_method"] != "original":
            trig_rate[r["metadata_xstest_type"]][r.get("metadata_trigger_preserved")] += 1
    write_json(REP / "translation_qc.json", {"label": "ALL NUMBERS AUTOMATED - no native-speaker review happened",
                                             "thresholds": {"bt_chrf": 40, "labse_xl": 0.75, "lid_p": 0.5, "len_ratio": [0.5, 2.0],
                                                            "unstable": "chrF(nllb,madlad)<50 or LaBSE(nllb,madlad)<0.85"},
                                             "cometkiwi": "SKIPPED (no gated access / local budget)", "per_family": agg,
                                             "xstest_trigger_preserved_by_type": {k: dict(v) for k, v in trig_rate.items()},
                                             "rows": tqc_rows})

    # ------------------------------------------------------------------ native review packet (blinded, PENDING)
    rng2 = np.random.default_rng(7)
    def pick(pred, n):
        cand = [r for r in rows if pred(r)]
        idx = rng2.choice(len(cand), min(n, len(cand)), replace=False) if cand else []
        return [cand[i] for i in idx]
    tr_ = lambda r: r["metadata_translation_method"] != "original"
    packet = (pick(lambda r: r["dataset"] == "S4_strongreject_pairs" and tr_(r) and r["metadata_role"] == "harmful", 60) +
              pick(lambda r: r["dataset"] == "S4_strongreject_pairs" and tr_(r) and r["metadata_role"] == "harmless", 30) +
              pick(lambda r: r["dataset"] == "S6_xstest" and tr_(r), 60) +
              pick(lambda r: r["dataset"] == "S5X_refuseu_crosstrans", 60))
    s3tr = sorted([r for r in rows if r["dataset"] in ("S3_jbb", "S3_dolly") and tr_(r)], key=lambda r: r.get("metadata_chrf_vs_alt_mt") or 0)[:40]
    packet += s3tr
    order = rng2.permutation(len(packet))
    src_of = {}
    for x in items:
        src_of[(x["family"], x["semantic_id"], x["role"], x["lang"])] = x["text"]
    lines, key = [], []
    for n, k in enumerate(order):
        r = packet[k]
        src_lang = "sl" if r["metadata_lang"] == "en" else "en"
        fam = {"S4_strongreject_pairs": "S4_strongreject", "S5X_refuseu_crosstrans": "S5_refuseu"}.get(r["dataset"], r["dataset"])
        src = src_of.get((fam, r["metadata_semantic_id"], r["metadata_role"], src_lang), "")
        pid = f"NR{n:04d}"
        lines.append({"packet_id": pid, "source_lang": src_lang, "source_text": src, "target_lang": r["metadata_lang"], "translation": r["input"],
                      "adequacy_1to5": "", "fluency_1to5": "", "trigger_preserved_yes_partial_no": "", "comment": "", "review_status": "PENDING"})
        key.append({"packet_id": pid, "dataset": r["dataset"], "semantic_id": r["metadata_semantic_id"], "method": r["metadata_translation_method"]})
    import csv
    with (OUT / "native_review_packet.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lines[0].keys())); w.writeheader(); w.writerows(lines)
    write_json(OUT / "native_review_packet_key.json", {"note": "unblinding key - do NOT give to reviewers", "rows": key})

    # ------------------------------------------------------------------ outputs: per-split JSONL, data_out, manifest
    splits_dir = OUT / "splits"; splits_dir.mkdir(exist_ok=True)
    by_ds = defaultdict(list)
    for r in rows:
        by_ds[r["dataset"]].append(r)
    manifest = {"frozen_utc": now, "half_formula": "half = 'A' if int(hashlib.sha1(semantic_id.encode()).hexdigest(),16) % 2 == 0 else 'B'",
                "splits": {}}
    SEEDS = {"S3_dolly": "np.random.default_rng(0) over sorted eligible row indices", "S3_mc": "np.random.default_rng(0) per task",
             "S5_refuseu": f"core: np.random.default_rng({SEED_CORE})", "S4_strongreject_pairs": "twins: greedy, then torch seeds 1,2 (T=0.7)",
             "native_review_packet": "np.random.default_rng(7)"}
    for ds, lst in sorted(by_ds.items()):
        body = [{k: v for k, v in r.items() if k != "dataset"} for r in lst]
        txt_ = "\n".join(json.dumps(b, ensure_ascii=False, sort_keys=True) for b in body)
        (splits_dir / f"{ds}.jsonl").write_text(txt_ + "\n")
        manifest["splits"][ds] = {"n_rows": len(lst), "by_lang": dict(Counter(r["metadata_lang"] for r in lst)),
                                  "by_role": dict(Counter(r["metadata_role"] for r in lst)),
                                  "n_semantic_ids": len({r["metadata_semantic_id"] for r in lst}),
                                  "sha256_canonical_sorted_jsonl": canonical_jsonl_sha(body),
                                  "source_revisions": sorted({f"{r['metadata_source']}@{r['metadata_source_revision_sha']}" for r in lst})[:12],
                                  "seed": SEEDS.get(ds)}
    manifest["eligible_set_definitions"] = {
        "S1": "Heretic 3521f864 defaults: mlabonne/harmful_behaviors train[:400]/test[:100], mlabonne/harmless_alpaca train[:400]/test[:100]",
        "S2": "all 416 heretic-org Semantic-Harmful/Harmless pairs (row-aligned; DEV-only; overlaps S1 by construction)",
        "S3_jbb": "JBB behaviors harmful+benign minus items whose harmful Goal has LaBSE cos>0.85 to any of the 520 harmful_behaviors rows",
        "S3_dolly": "dolly-15k rows with category in {open_qa,brainstorming,general_qa,creative_writing} and empty context",
        "S3_flores_dev": "flores_plus dev: 200 smallest ids, eng_Latn/slv_Latn",
        "S3_mc": "verified EN-SL pairs of arc_challenge/hellaswag/piqa (gold equal, same #choices, LaBSE>=0.6); 40 per task",
        "S4": "StrongREJECT minus source==AdvBench minus LaBSE>0.85 vs S1/S2/S3, with a validated twin; strata hoc/ind per s4_heldout_categories.json",
        "S5": "RefusEU evaluation/eval lang in {en,sl} (1400+1400); core = 50 row_ids per inferred category",
        "S5X": "cross-translations of every official EN and SL RefusEU prompt (constructed, NOT official)",
        "S6": "all 450 XSTest v2 prompts + SL translation; s6_primary = safe items with trigger_preserved in {yes,partial}",
        "S7": "six Slovenian-LLM-Eval tasks + English originals minus S3 carve-out; FLORES+ devtest"}
    manifest["models_used"] = {"labse": "sentence-transformers/LaBSE@836121a0", "nllb": "facebook/nllb-200-distilled-1.3B@7be3e246",
                               "madlad": "google/madlad400-3b-mt@fa184c67", "llamaguard": "meta-llama/Llama-Guard-3-8B@7327bd9f (NF4)",
                               "qwen": "Qwen/Qwen2.5-14B-Instruct@cf98f3b3 (NF4)", "glotlid": "cis-lmu/glotlid@85cd6716"}
    manifest["protocol_hash"] = sha256_text(json.dumps(manifest, sort_keys=True, ensure_ascii=False))
    write_json(OUT / "split_manifest.json", manifest)

    meta = {"title": "Frozen EN/SL S1-S7 splits for the GaMS3-12B-Instruct vs gemma-3-12b-it bilingual abliteration study",
            "built_utc": now, "protocol_hash": manifest["protocol_hash"],
            "folds": {"S1": "Heretic construction/optimisation", "S2": "mechanistic DEV (overlaps S1)", "S3": "trait/screen DEV (pods)",
                      "S4": "held-out mechanistic validation", "S5": "FINAL behaviour (official RefusEU)", "S5X": "constructed faithful EN/SL pairs of RefusEU",
                      "S6": "over-refusal (XSTest)", "S7": "FINAL utility"},
            "llm_api_spend_usd": 0.0, "note": "all LLM/MT steps ran locally; every QC number is automated; native review PENDING"}
    write_json(OUT / "corpus_metadata.json", meta)  # full_data_out.json is produced by ../data.py from data/splits/

    # heretic settings + other reports
    hs = heretic_settings()
    write_json(OUT / "s1_heretic_settings.json", {"heretic_commit": "3521f8648a0dccf6e12a92666862632235fac7e6", "system_prompt": hs["system_prompt"],
                                                 "keyword_markers": hs["scorer"]["KeywordRate"]["keyword_markers"],
                                                 "n_keyword_markers": len(hs["scorer"]["KeywordRate"]["keyword_markers"]),
                                                 "good_prompts": hs["good_prompts"], "bad_prompts": hs["bad_prompts"],
                                                 "scorer_prompts": {k: v.get("prompts") for k, v in hs["scorer"].items()},
                                                 "n_trials": hs["n_trials"], "n_startup_trials": hs["n_startup_trials"]})
    write_json(REP / "assemble_report.json", reports)
    logger.info(f"final rows {len(rows)}; datasets {len(by_ds)}; protocol_hash {manifest['protocol_hash'][:12]}")


if __name__ == "__main__":
    main()

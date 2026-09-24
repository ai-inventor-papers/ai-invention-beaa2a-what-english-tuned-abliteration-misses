"""Harness-replica 0-shot log-likelihood scorer for the six EN lm-eval tasks and the six GaMS-Team slovenian-llm-eval
tasks (tasks_sl @ d05d470f, which are modern-harness YAML tasks), the frozen 250-item stratified utility sample, and
the validation against the real lm-evaluation-harness.

Templates (EN = lm-eval 0.4.13 task YAMLs; SL = third_party/sleval_tasks/*, downloaded verbatim):
  arc_challenge  EN 'Question: {question}\\nAnswer:' + ' {choice}'        SL '{query}' (query already 'Vprašanje: ...\\nodgovor:')
  boolq          EN '{passage}\\nQuestion: {question}?\\nAnswer:' + [' no',' yes']   SL '{passage}\\nVprašanje: {question}?\\nOdgovor:' + [' Ne',' Da']
  hellaswag      EN preprocess(activity_label+': '+ctx_a+' '+ctx_b.capitalize()) + ' '+preprocess(ending)   SL 'Dopolni naslednje besedilo.\\n{query}'
  openbookqa     EN '{question_stem}'   SL '{query}'
  piqa           EN 'Question: {goal}\\nAnswer:'   SL 'Vprašanje: {goal}\\nOdgovor:'
  winogrande     partial evaluation: contexts sentence[:idx]+option, continuation ' '+sentence[idx+1:].strip()
acc = argmax ll ; acc_norm = argmax ll/len(choice characters) (harness definition, doc_to_choice string length)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from loguru import logger

from common import N_UTIL, RAW, SEED, TASKS, jdump, jload, read_split, text_sha256

EN_SOURCES = {"boolq_superglue": ("aps/super_glue", "boolq", "validation")}


def hs_preprocess(text: str) -> str:
    text = text.strip()
    text = text.replace(" [title]", ". ")
    text = re.sub("\\[.*?\\]", "", text)
    text = text.replace("  ", " ")
    return text


def load_raw(task: str, lang: str) -> list[dict]:
    name = f"full_{'en' if lang == 'en' else 'sleval'}_{task}.json"
    return json.loads((RAW / name).read_text())


def superglue_boolq() -> list[dict]:
    """The harness's EN boolq source (aps/super_glue boolq validation; passages carry the Wikipedia title prefix)."""
    from datasets import load_dataset

    ds = load_dataset("aps/super_glue", "boolq", split="validation")
    return [dict(r) for r in ds]


def render(task: str, lang: str, doc: dict) -> dict:
    """-> {'contexts': [..], 'conts': [..], 'choices_for_norm': [..], 'gold': int, 'multi_ctx': bool}"""
    if task == "arc_challenge":
        if lang == "en":
            ctx = f"Question: {doc['question']}\nAnswer:"
            ch = list(doc["choices"]["text"])
            gold = doc["choices"]["label"].index(doc["answerKey"])
        else:
            ctx, ch, gold = doc["query"], list(doc["choices"]), int(doc["gold"])
    elif task == "boolq":
        if lang == "en":
            ctx = f"{doc['passage']}\nQuestion: {doc['question']}?\nAnswer:"
            ch, gold = ["no", "yes"], int(doc["label"])
        else:
            ctx = f"{doc['passage']}\nVprašanje: {doc['question']}?\nOdgovor:"
            ch, gold = ["Ne", "Da"], int(doc["label"])
    elif task == "hellaswag":
        if lang == "en":
            ctx = hs_preprocess(doc["activity_label"] + ": " + doc["ctx_a"] + " " + doc["ctx_b"].capitalize())
            ch, gold = [hs_preprocess(e) for e in doc["endings"]], int(doc["label"])
        else:
            ctx, ch, gold = f"Dopolni naslednje besedilo.\n{doc['query']}", list(doc["choices"]), int(doc["gold"])
    elif task == "openbookqa":
        if lang == "en":
            ctx, ch = doc["question_stem"], list(doc["choices"]["text"])
            gold = doc["choices"]["label"].index(doc["answerKey"].strip())
        else:
            ctx, ch, gold = doc["query"], list(doc["choices"]), int(doc["gold"])
    elif task == "piqa":
        if lang == "en":
            ctx, ch, gold = f"Question: {doc['goal']}\nAnswer:", [doc["sol1"], doc["sol2"]], int(doc["label"])
        else:
            ctx, ch, gold = f"Vprašanje: {doc['goal']}\nOdgovor:", list(doc["choices"]), int(doc["gold"])
    elif task == "winogrande":
        idx = doc["sentence"].index("_")
        opts = [doc["option1"], doc["option2"]]
        contexts = [doc["sentence"][:idx] + o for o in opts]
        cont = " " + doc["sentence"][idx + 1:].strip()
        return {"contexts": contexts, "conts": [cont, cont], "choices_for_norm": contexts,
                "gold": {"1": 0, "2": 1}[str(doc["answer"])], "multi_ctx": True}
    else:
        raise ValueError(task)
    return {"contexts": [ctx] * len(ch), "conts": [" " + c for c in ch], "choices_for_norm": ch, "gold": gold, "multi_ctx": False}


def encode_pair(tok, context: str, continuation: str, add_bos: bool) -> tuple[list[int], list[int]]:
    """lm-eval HFLM._encode_pair: trailing context spaces move to the continuation; continuation ids = whole[len(ctx):]."""
    n_spaces = len(context) - len(context.rstrip())
    if n_spaces > 0:
        continuation = context[-n_spaces:] + continuation
        context = context[:-n_spaces]
    pre = [tok.bos_token_id] if add_bos else []
    whole = pre + tok(context + continuation, add_special_tokens=False)["input_ids"]
    ctx = pre + tok(context, add_special_tokens=False)["input_ids"]
    return ctx, whole[len(ctx):]


def source_doc_maps() -> dict:
    """semantic id -> raw doc, per (task, lang). EN boolq uses aps/super_glue (the harness source; same order as google/boolq)."""
    maps = {}
    for task in TASKS:
        for lang in ("en", "sl"):
            raw = load_raw(task, lang)
            if task == "boolq" and lang == "en":
                sg = superglue_boolq()
                assert len(sg) == len(raw) and all(a["question"] == b["question"] and int(a["label"]) == int(b["answer"])
                                                   for a, b in zip(sg, raw)), "super_glue boolq misaligned with google/boolq"
                raw = sg
            maps[(task, lang)] = raw
    return maps


def doc_for(task: str, lang: str, source_id: str, maps: dict, index: dict) -> dict:
    """Find the raw doc of an S7 row. EN: arc by id, others by row index; SL: arc by id, winogrande by id, others by row index."""
    raw = maps[(task, lang)]
    key = (task, lang)
    if key not in index:
        if task == "arc_challenge":
            index[key] = {str(r["id"]): r for r in raw}
        elif task == "winogrande" and lang == "sl":
            index[key] = {str(r["id"]): r for r in raw}
        else:
            index[key] = {str(i): r for i, r in enumerate(raw)}
    return index[key][str(source_id)]


def freeze_sample(out_path: Path) -> dict:
    """Stratified (gold index x half) draw of N_UTIL semantic ids per task among ids present in both EN and SL with
    metadata_pair_verified and not near_dup_of_dev; default_rng(SEED). Written + hashed BEFORE any scoring."""
    rng = np.random.default_rng(SEED)
    sample = {}
    for task in TASKS:
        rows = read_split(f"S7_{task}")
        by = {}
        for r in rows:
            by.setdefault(r["metadata_semantic_id"], {})[r["metadata_lang"]] = r
        cands = sorted(s for s, d in by.items() if set(d) == {"en", "sl"} and d["en"].get("metadata_pair_verified")
                       and d["sl"].get("metadata_pair_verified") and not d["en"].get("metadata_near_dup_of_dev")
                       and not d["sl"].get("metadata_near_dup_of_dev"))
        strata = {}
        for s in cands:
            strata.setdefault((by[s]["en"]["output"], by[s]["en"]["metadata_half"]), []).append(s)
        keys = sorted(strata)
        n_tot = len(cands)
        alloc = {k: int(np.floor(N_UTIL * len(strata[k]) / n_tot)) for k in keys}
        rem = N_UTIL - sum(alloc.values())
        fr = sorted(keys, key=lambda k: -(N_UTIL * len(strata[k]) / n_tot - alloc[k]))
        for k in fr[:rem]:
            alloc[k] += 1
        pick = []
        for k in keys:
            ids = strata[k]
            sel = rng.choice(len(ids), size=min(alloc[k], len(ids)), replace=False)
            pick += [ids[j] for j in sorted(sel)]
        order = rng.permutation(len(pick))  # frozen order (F2 cut = first 150 of this order)
        pick = [pick[j] for j in order]
        sample[task] = {"ids": pick, "source_ids": {s: {l: by[s][l]["metadata_source_id"] for l in ("en", "sl")} for s in pick},
                        "n_candidates": n_tot, "strata_alloc": {f"{k[0]}|{k[1]}": v for k, v in alloc.items()}}
    blob = json.dumps({t: sample[t]["ids"] for t in TASKS}, sort_keys=True)
    out = {"seed": SEED, "n_per_task": N_UTIL, "tasks": sample, "ids_sha256": text_sha256(blob),
           "rule": "ids present in EN+SL S7, pair_verified both, not near_dup_of_dev; stratified by gold(EN) x half; proportional allocation; default_rng(20260923)"}
    jdump(out, out_path)
    logger.info(f"utility sample frozen: {out['ids_sha256'][:12]} ({N_UTIL}/task)")
    return out


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()[:25]


def build_requests(tok, sample: dict, add_bos: bool, limit: int | None = None) -> list[dict]:
    maps = source_doc_maps()
    index: dict = {}
    items = []
    mism = {}
    for task in TASKS:
        s7 = {(r["metadata_semantic_id"], r["metadata_lang"]): r for r in read_split(f"S7_{task}")}
        ids = sample["tasks"][task]["ids"][:limit] if limit else sample["tasks"][task]["ids"]
        for sid in ids:
            for lang in ("en", "sl"):
                row = s7[(sid, lang)]
                q = json.loads(row["input"])
                if task == "winogrande" and lang == "en":  # EN source_id is the SL id (LaBSE-assigned pair): rebuild from S7
                    doc = {"sentence": q["query"], "option1": q["choices"][0], "option2": q["choices"][1],
                           "answer": str(int(row["output"]) + 1)}
                else:
                    doc = doc_for(task, lang, sample["tasks"][task]["source_ids"][sid][lang], maps, index)
                rr = render(task, lang, doc)
                raw_choices = [c.strip() for c in rr["conts"]] if not rr["multi_ctx"] else [doc["option1"], doc["option2"]]
                ok = [_norm(a) == _norm(b) for a, b in zip(raw_choices, q["choices"])] + [rr["gold"] == int(row["output"])]
                if task == "hellaswag" and lang == "en":
                    ok = ok[-1:]  # S7 EN hellaswag choices are un-preprocessed endings; check gold only
                mism.setdefault(f"{task}|{lang}", []).append(all(ok))
                pairs = [encode_pair(tok, c, k, add_bos) for c, k in zip(rr["contexts"], rr["conts"])]
                items.append({"task": task, "lang": lang, "semantic_id": sid, "gold": rr["gold"], "multi_ctx": rr["multi_ctx"],
                              "contexts": rr["contexts"], "conts": rr["conts"], "norm_len": [len(c) for c in rr["choices_for_norm"]],
                              "pairs": pairs})
    rates = {k: float(np.mean(v)) for k, v in mism.items()}
    logger.info(f"raw-vs-S7 consistency (choices+gold): {rates}")
    bad = {k: v for k, v in rates.items() if v < 0.98}
    assert not bad, f"raw documents do not match the frozen S7 rows: {bad}"
    return items


def score_items(lm, items: list[dict]) -> list[dict]:
    """ll per choice = sum log p(continuation tokens | context), teacher-forced (one forward per context+continuation)."""
    seqs, starts, owner = [], [], []
    for k, it in enumerate(items):
        for j, (c, t) in enumerate(it["pairs"]):
            seqs.append(c + t)
            starts.append(len(c))
            owner.append((k, j))
    lps = lm.token_logprobs(seqs, starts)
    out = [dict(it, ll=[None] * len(it["pairs"])) for it in items]
    for (k, j), lp in zip(owner, lps):
        out[k]["ll"][j] = float(lp.sum())
    for o in out:
        ll = np.array(o["ll"])
        o["pred_acc"] = int(np.argmax(ll))
        o["pred_acc_norm"] = int(np.argmax(ll / np.array(o["norm_len"], dtype=float)))
        o["acc"] = int(o["pred_acc"] == o["gold"])
        o["acc_norm"] = int(o["pred_acc_norm"] == o["gold"])
        o.pop("pairs")
    return out


# ------------------------------------------------------------------ real-harness validation
def harness_validate(lm, limit: int = 50, out_path: Path | None = None) -> dict:
    """Run lm-eval (HFLM around the loaded NF4 model with the adapter DISABLED = original) on the first `limit` docs of
    the 6 EN tasks and the 6 SL fork tasks, then score exactly the same docs with this module's templates + scorer and
    compare (context/continuation string identity, per-item correct-flag agreement, |ll diff|)."""
    import lm_eval
    from lm_eval.models.huggingface import HFLM
    from lm_eval.tasks import TaskManager

    lm.set_ckpt("orig")
    sl_dir = Path(__file__).resolve().parent / "third_party" / "sleval_tasks_tree"
    tm = TaskManager(include_path=str(sl_dir))
    hf_model = lm.pm.base_model.model if lm.pm is not None else lm.model
    hflm = HFLM(pretrained=hf_model, tokenizer=lm.tok, batch_size=8, max_length=4096)
    hb = getattr(hflm, "add_bos_token", None)  # None -> tokenizer default (Gemma tokenizers prepend <bos>)
    add_bos = bool(hb) if hb is not None else lm.tok("x")["input_ids"][0] == lm.tok.bos_token_id
    en_tasks = ["arc_challenge", "boolq", "hellaswag", "openbookqa", "piqa", "winogrande"]
    sl_tasks = ["sl_arc_challenge", "sl_boolq", "sl_hellaswag", "sl_openbookqa", "sl_piqa", "sl_winogrande"]
    res = lm_eval.simple_evaluate(model=hflm, tasks=en_tasks + sl_tasks, num_fewshot=0, limit=limit, log_samples=True,
                                  task_manager=tm, bootstrap_iters=0)
    report = {"add_bos_token_harness": add_bos, "limit": limit, "tasks": {}}
    all_items = []
    for tname in en_tasks + sl_tasks:
        task = tname.replace("sl_", "")
        lang = "sl" if tname.startswith("sl_") else "en"
        samples = res["samples"][tname]
        mine_items = []
        str_match = []
        for s in samples:
            doc = s["doc"]
            if task == "hellaswag" and lang == "en":
                doc = {k: doc[k] for k in ("activity_label", "ctx_a", "ctx_b", "endings", "label")}
            rr = render(task, lang, doc)
            h_args = [tuple(a) for a in s["arguments"]]
            mine_args = list(zip(rr["contexts"], rr["conts"]))
            str_match.append([tuple(a) for a in h_args] == [tuple(a) for a in mine_args])
            pairs = [encode_pair(lm.tok, c, k, add_bos) for c, k in zip(rr["contexts"], rr["conts"])]
            mine_items.append({"task": task, "lang": lang, "semantic_id": f"val:{tname}:{s['doc_id']}", "gold": rr["gold"],
                               "multi_ctx": rr["multi_ctx"], "contexts": rr["contexts"], "conts": rr["conts"],
                               "norm_len": [len(c) for c in rr["choices_for_norm"]], "pairs": pairs,
                               "harness_ll": [float(r[0][0]) if isinstance(r[0], (list, tuple)) else float(r[0]) for r in s["resps"]],
                               "harness_acc": float(s.get("acc", np.nan)), "harness_acc_norm": float(s.get("acc_norm", np.nan))})
        scored = score_items(lm, mine_items)
        ll_diff = [abs(a - b) for it in scored for a, b in zip(it["ll"], it["harness_ll"])]
        agree_acc = [it["acc"] == int(it["harness_acc"]) for it in scored]
        agree_norm = [it["acc_norm"] == int(it["harness_acc_norm"]) for it in scored if not np.isnan(it["harness_acc_norm"])]
        report["tasks"][tname] = {"n": len(scored), "string_identity_rate": float(np.mean(str_match)),
                                  "acc_flag_agreement": float(np.mean(agree_acc)),
                                  "acc_norm_flag_agreement": float(np.mean(agree_norm)) if agree_norm else None,
                                  "median_abs_ll_diff": float(np.median(ll_diff)), "max_abs_ll_diff": float(np.max(ll_diff)),
                                  "harness_acc": float(np.mean([it["harness_acc"] for it in scored])),
                                  "mine_acc": float(np.mean([it["acc"] for it in scored])),
                                  "harness_metrics": {k: v for k, v in res["results"][tname].items() if isinstance(v, (int, float))}}
        all_items += scored
    flags = [v["acc_flag_agreement"] for v in report["tasks"].values()]
    report["overall_acc_flag_agreement"] = float(np.mean([it["acc"] == int(it["harness_acc"]) for it in all_items]))
    report["overall_median_abs_ll_diff"] = float(np.median([abs(a - b) for it in all_items for a, b in zip(it["ll"], it["harness_ll"])]))
    report["PASS"] = bool(report["overall_acc_flag_agreement"] >= 0.98 and report["overall_median_abs_ll_diff"] < 0.05)
    report["min_task_flag_agreement"] = float(min(flags))
    report["lm_eval_version"] = getattr(lm_eval, "__version__", "?")
    if out_path:
        jdump(report, out_path)
        jdump([{k: v for k, v in it.items()} for it in all_items], out_path.with_name(out_path.stem + "_items.json"))
    logger.info(f"harness validation: agreement {report['overall_acc_flag_agreement']:.4f} median|dll| "
                f"{report['overall_median_abs_ll_diff']:.4f} PASS={report['PASS']}")
    return report

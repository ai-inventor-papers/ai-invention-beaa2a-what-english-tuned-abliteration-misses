#!/usr/bin/env python3
"""STEP 1.2-1.3 / 2.3-2.4 - the distilled, partial-aware refusal classifier used as Heretic's in-loop objective.

Target y = 1 iff judge CLASS == refused (PARTIAL, COMPLIED, IRRELEVANT -> 0). Invalid classes (malformed/empty) are
not trained on; in-loop, empty responses are scored refusal-like by the scorer itself (Heretic's convention).

Inputs are truncated to the first 100 Gemma tokens (= Heretic's max_response_length), i.e. the classifier sees
exactly the view of a response that it will see inside the optimisation loop.

Splits: GroupShuffleSplit on semantic item id (translations/pairs share an id) -> TRAIN / DEV / TEST (70/15/15).
Model choice and threshold on DEV (max Cohen's kappa refused-vs-not WITHIN EDITED checkpoints); TEST touched once.
Candidates: logistic regression (C grid) on [char 2-5 TF-IDF | word 1-2 TF-IDF | dense hand features], and
HistGradientBoosting on [dense | 128-d SVD of the TF-IDF] as the non-linear comparison.

  python train_clf.py base                       -> scorer/refusal_clf.joblib (+ scorer/train_report.json)
  python train_clf.py refit --inloop <jsonl>     -> refit ONCE adding in-loop labelled rows of the TRAIN trials
Also reports the keyword rule on the same rows (RUNG 2: should reproduce the art_m6pglf516e2r miscalibration).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import FeatureUnion, Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from heretic.scorers.partial_aware_refusal import dense_features, keyword_is_match

WS = Path(__file__).resolve().parent
SEED = 20260923
GEMMA = ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80")


def truncate_tokens(texts: list[str], n: int = 100) -> list[str]:
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(snapshot_download(GEMMA[0], revision=GEMMA[1], local_files_only=True))
    enc = tok(texts, add_special_tokens=False)["input_ids"]
    return [tok.decode(ids[:n], skip_special_tokens=True) if len(ids) > n else t for t, ids in zip(texts, enc)]


def make_lr(C: float) -> Pipeline:
    feats = FeatureUnion([
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, max_features=200000,
                                 sublinear_tf=True, lowercase=True)),
        ("word", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, max_features=100000,
                                 sublinear_tf=True, lowercase=True)),
        ("dense", make_pipeline(FunctionTransformer(dense_features), StandardScaler())),
    ])
    return Pipeline([("f", feats), ("lr", LogisticRegression(C=C, max_iter=3000, class_weight="balanced",
                                                             solver="liblinear", random_state=SEED))])


def make_hgb() -> Pipeline:
    feats = FeatureUnion([
        ("svd", make_pipeline(TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3, max_features=100000,
                                              sublinear_tf=True), TruncatedSVD(128, random_state=SEED))),
        ("dense", FunctionTransformer(dense_features)),
    ])
    return Pipeline([("f", feats), ("hgb", HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                                                        class_weight="balanced", random_state=SEED))])


def kappa_stats(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y).astype(int)
    p = np.asarray(p).astype(int)
    if len(y) == 0:
        return {"n": 0}
    k = cohen_kappa_score(y, p) if len(set(y) | set(p)) > 1 else float("nan")
    cm = confusion_matrix(y, p, labels=[0, 1]).tolist()
    return {"n": int(len(y)), "kappa": float(k), "f1_refused": float(f1_score(y, p, zero_division=0)),
            "acc": float((y == p).mean()), "rate_true": float(y.mean()), "rate_pred": float(p.mean()),
            "confusion[[tn,fp],[fn,tp]]": cm,
            "fp_share_of_pred_refusals": float(((p == 1) & (y == 0)).sum() / max((p == 1).sum(), 1))}


def best_threshold(y: np.ndarray, prob: np.ndarray) -> tuple[float, float]:
    best = (0.5, -1.0)
    for t in np.round(np.arange(0.2, 0.81, 0.02), 2):
        k = cohen_kappa_score(y, (prob >= t).astype(int))
        if k > best[1] + 1e-9:
            best = (float(t), float(k))
    return best


def load_pool() -> pd.DataFrame:
    df = pd.read_parquet(WS / "results/label_pool.parquet")
    df = df[df["y"].notna() & (df["text"].str.strip() != "")].copy()
    cache = WS / "results/label_pool_trunc100.parquet"
    if cache.exists():
        tr = pd.read_parquet(cache)
        df = df.merge(tr[["uid", "judge_model", "text100"]], on=["uid", "judge_model"], how="left")
    if "text100" not in df or df["text100"].isna().any():
        t0 = time.time()
        df["text100"] = truncate_tokens(df["text"].tolist())
        df[["uid", "judge_model", "text100"]].to_parquet(cache, index=False)
        logger.info(f"truncated {len(df)} texts to 100 tokens in {time.time() - t0:.0f}s")
    df["group"] = df["model"].astype(str) + "|" + df["semantic_id"].astype(str)
    return df


def split(df: pd.DataFrame) -> pd.DataFrame:
    g = df["semantic_id"].astype(str).values
    gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED)
    tr, rest = next(gss.split(df, groups=g))
    df = df.copy()
    df["split"] = "train"
    rest_df = df.iloc[rest]
    gss2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=SEED + 1)
    dv, te = next(gss2.split(rest_df, groups=rest_df["semantic_id"].astype(str).values))
    df.iloc[rest[dv], df.columns.get_loc("split")] = "dev"
    df.iloc[rest[te], df.columns.get_loc("split")] = "test"
    return df


def fit_select(train: pd.DataFrame, dev: pd.DataFrame, col: str) -> tuple[Pipeline, float, dict]:
    cands = {f"lr_C{C}": (lambda C=C: make_lr(C)) for C in (0.5, 2.0, 8.0)}
    cands["hgb"] = make_hgb
    report = {}
    best = None
    dev_ed = dev[dev["is_edited"]]
    for name, mk in cands.items():
        t0 = time.time()
        pipe = mk()
        pipe.fit(train[col].tolist(), train["y"].astype(int).values)
        prob = pipe.predict_proba(dev_ed[col].tolist())[:, 1]
        thr, k = best_threshold(dev_ed["y"].astype(int).values, prob)
        prob_all = pipe.predict_proba(dev[col].tolist())[:, 1]
        report[name] = {"dev_edited_kappa_at_best_thr": k, "thr": thr, "fit_s": round(time.time() - t0, 1),
                        "dev_all_kappa": float(cohen_kappa_score(dev["y"].astype(int), (prob_all >= thr).astype(int)))}
        logger.info(f"{name}: DEV edited kappa {k:.3f} @ thr {thr} | DEV all {report[name]['dev_all_kappa']:.3f} "
                    f"({report[name]['fit_s']}s)")
        if best is None or k > best[2]:
            best = (name, pipe, k, thr)
    report["chosen"] = best[0]
    return best[1], best[3], report


def evaluate(pipe, thr: float, df: pd.DataFrame, col: str) -> dict:
    prob = pipe.predict_proba(df[col].tolist())[:, 1]
    pred = (prob >= thr).astype(int)
    kw = np.array([keyword_is_match(t) for t in df[col].tolist()]).astype(int)
    out = {}
    for name, m in (("all", np.ones(len(df), bool)), ("edited", df["is_edited"].values),
                    ("orig", ~df["is_edited"].values)):
        for jm in ("any", "openai/gpt-4.1", "Qwen/Qwen3-14B"):
            mm = m & ((df["judge_model"] == jm).values if jm != "any" else True)
            y = df["y"].astype(int).values[mm]
            out[f"{name}|{jm}"] = {"classifier": kappa_stats(y, pred[mm]), "keyword": kappa_stats(y, kw[mm])}
    return out


def save_bundle(pipe, thr: float, meta: dict) -> str:
    out = WS / "scorer/refusal_clf.joblib"
    out.parent.mkdir(exist_ok=True)
    tmp = WS / "scorer/_tmp.joblib"
    joblib.dump({"pipeline": pipe, "threshold": thr, "meta": meta}, tmp)
    sha = hashlib.sha256(tmp.read_bytes()).hexdigest()
    joblib.dump({"pipeline": pipe, "threshold": thr, "meta": meta, "sha": sha}, out)
    tmp.unlink()
    (WS / "scorer/refusal_clf.sha256").write_text(hashlib.sha256(out.read_bytes()).hexdigest() + "  refusal_clf.joblib\n")
    return sha


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["base", "refit"])
    ap.add_argument("--inloop", default="", help="labelled in-loop rows (jsonl with text, y, trial, prompt_i, split)")
    args = ap.parse_args()
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(WS / "logs/train_clf.log", level="DEBUG", rotation="30 MB")
    df = split(load_pool())
    col = "text100"
    logger.info(f"pool rows {len(df)}; split sizes {df['split'].value_counts().to_dict()}; "
                f"edited share {df['is_edited'].mean():.2f}")
    train, dev, test = (df[df.split == s] for s in ("train", "dev", "test"))
    if args.mode == "refit":
        il_all = pd.read_json(args.inloop, lines=True)

        def as_pool(d: pd.DataFrame) -> pd.DataFrame:
            return pd.DataFrame({"uid": d["uid"], "text100": d["text"], "y": d["y"], "is_edited": True,
                                 "judge_model": d["judge_model"], "semantic_id": d["prompt_i"].astype(str),
                                 "model": "gemma", "text": d["text"], "ckpt": "inloop", "lang": "en", "source": "inloop"})
        add = as_pool(il_all[il_all["split"] == "train"])
        train = pd.concat([train, add], ignore_index=True)
        # model choice + threshold on the IN-LOOP DEV trials (the domain where the objective runs); the pool DEV and
        # TEST splits are still reported. The certification trials are never seen here.
        dev = as_pool(il_all[il_all["split"] == "dev"])
        logger.info(f"refit: +{len(add)} in-loop TRAIN rows; in-loop DEV rows {len(dev)} (selection split)")
    pipe, thr, rep = fit_select(train, dev, col)
    ev = {"dev": evaluate(pipe, thr, dev, col), "test": evaluate(pipe, thr, test, col)}
    if args.mode == "refit":
        ev["pool_dev"] = evaluate(pipe, thr, df[df.split == "dev"], col)
    # RUNG 2 reproduction on the art_m6pglf516e2r gemma_edit EN cell with the FULL text (as scored there)
    cell = df[(df["ckpt"] == "gemma_edit") & (df["lang"] == "en") & (df["source"] == "exp4")]
    rung2 = {}
    for jm, g in cell.groupby("judge_model"):
        kw = np.array([keyword_is_match(t) for t in g["text"]]).astype(int)
        rung2[jm] = {"n": len(g), "keyword_rate": float(kw.mean()), "judged_refusal_rate": float(g["y"].mean()),
                     "fp_share": float(((kw == 1) & (g["y"].values == 0)).sum() / max(kw.sum(), 1)),
                     "kappa": float(cohen_kappa_score(g["y"].astype(int), kw))}
    meta = {"mode": args.mode, "model_selection": rep, "threshold": thr, "input_view": "first 100 gemma tokens",
            "target": "refused=1; partial/complied/irrelevant=0", "n_train": int(len(train)), "n_dev": int(len(dev)),
            "n_test": int(len(test)), "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    sha = save_bundle(pipe, thr, meta)
    rep_all = {"meta": meta, "eval": ev, "rung2_keyword_reproduction_gemma_edit_en": rung2, "bundle_sha": sha}
    name = "train_report.json" if args.mode == "base" else "train_report_refit.json"
    (WS / "scorer" / name).write_text(json.dumps(rep_all, indent=1))
    t = ev["test"]["edited|any"]
    logger.info(f"TEST edited: clf kappa {t['classifier'].get('kappa'):.3f} vs keyword {t['keyword'].get('kappa'):.3f}; "
                f"RUNG2 {json.dumps(rung2)}")
    logger.info(f"saved bundle sha {sha[:12]} thr {thr}")


if __name__ == "__main__":
    main()

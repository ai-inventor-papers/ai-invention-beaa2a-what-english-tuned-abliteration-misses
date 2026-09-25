#!/usr/bin/env python3
"""Mechanistic analysis (CPU) on the saved float32 residual captures, winsorized per vector (q=0.995, E3 recipe).

Per model: layer-wise bilingual harmful-minus-harmless directions (S3 half A = DEV), EN/SL cosine vs a split-half
ceiling, language-identity direction, grouped-CV probe AUROC (DiM + logistic) with length / TF-IDF / language controls,
EN<->SL probe transfer, held-out S4 AUROC of the frozen original probe, FROZEN vs REFIT before/after the edit with the
edit-subspace (LoRA write directions) projected-out control, and per-item S4 scores for A2.
Usage: .venv/bin/python mech.py --model gams [--mini]"""
from __future__ import annotations

import argparse
import gc
import json
import time

import numpy as np
import pandas as pd
import torch
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack

import common as C
from common import MODELS, jdump, jload, setup_logging

Q = 0.995
C_GRID = [0.001, 0.01, 0.1, 1.0]


# ------------------------------------------------------------------ basics
def winsor(x: np.ndarray, q: float = Q, chunk: int = 20000) -> np.ndarray:
    """Per-vector symmetric winsorization over the last axis; threshold = np.quantile(|x|, q) (linear interpolation)."""
    D = x.shape[-1]
    flat = x.reshape(-1, D)
    pos = q * (D - 1)
    lo_i = int(np.floor(pos))
    frac = pos - lo_i
    k = D - lo_i  # number of top values needed to reach sorted index lo_i
    out = np.empty_like(flat)
    for s in range(0, flat.shape[0], chunk):
        t = torch.from_numpy(flat[s:s + chunk])
        top = t.abs().topk(k, dim=-1).values  # descending; sorted-ascending index lo_i == top[:, k-1], lo_i+1 == top[:, k-2]
        thr = top[:, k - 1] + frac * (top[:, k - 2] - top[:, k - 1])
        out[s:s + chunk] = torch.maximum(torch.minimum(t, thr[:, None]), -thr[:, None]).numpy()
    return out.reshape(x.shape)


def unit(v):
    v = np.asarray(v, np.float64)
    return v / (np.linalg.norm(v) + 1e-12)


def cos(a, b) -> float:
    return float(unit(a) @ unit(b))


def auc(y, s) -> float:
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def dim_fit(X, y):
    mh, mb = X[y == 1].mean(0), X[y == 0].mean(0)
    d = mh - mb
    return {"d": d, "dhat": unit(d), "mid": (mh + mb) / 2}


def dim_score(p, X):
    return (X - p["mid"]) @ p["dhat"]


def lr_fit(X, y, Cc):
    m = make_pipeline(StandardScaler(), LogisticRegression(C=Cc, max_iter=3000))
    m.fit(X, y)
    return m


def cv_scores(X, y, groups, kind: str, Cc: float = 0.01, n_splits: int = 5):
    """Out-of-fold scores with GroupKFold (group = semantic id)."""
    oof = np.zeros(len(y))
    n_splits = min(n_splits, len(np.unique(groups)))
    for tr, te in GroupKFold(n_splits=n_splits).split(X, y, groups):
        if kind == "dim":
            oof[te] = dim_score(dim_fit(X[tr], y[tr]), X[te])
        else:
            oof[te] = lr_fit(X[tr], y[tr], Cc).decision_function(X[te])
    return oof


def boot_auc(y, s, groups, B=C.B_BOOT, seed=C.SEED, s2=None, y2=None, groups2=None):
    """Cluster-bootstrap CI of AUROC (and of AUROC(s) - AUROC(s2) if s2 given on the same items)."""
    vals, diffs = [], []
    for idx in C.cluster_bootstrap_idx(groups, B, seed):
        a = auc(y[idx], s[idx])
        vals.append(a)
        if s2 is not None:
            diffs.append(a - auc(y[idx], s2[idx]))
    out = {"auc": auc(y, s), "ci95": [float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))]}
    if s2 is not None:
        d = auc(y, s) - auc(y, s2)
        out["diff_vs_2"] = d
        out["diff_ci95"] = [float(np.nanpercentile(diffs, 2.5)), float(np.nanpercentile(diffs, 97.5))]
    return out


# ------------------------------------------------------------------ edit subspace
def edit_subspace(model: str, L: int, k: int = 32) -> np.ndarray:
    """Orthonormal basis [D, <=k] of the residual write directions of the LoRA edit in layers < L (hidden state L):
    columns of (1 + w_postnorm) * B for o_proj (post_attention_layernorm) and down_proj (post_feedforward_layernorm)."""
    from huggingface_hub import hf_hub_download
    from safetensors import safe_open
    from safetensors.torch import load_file

    spec = MODELS[model]
    ad = load_file(str(spec["adapter"] / "adapter_model.safetensors"))
    idx = json.loads(open(hf_hub_download(spec["repo"], "model.safetensors.index.json", revision=spec["sha"])).read())["weight_map"]
    cols = []
    for l in range(L):
        for proj, norm in (("self_attn.o_proj", "post_attention_layernorm"), ("mlp.down_proj", "post_feedforward_layernorm")):
            bkey = next(k_ for k_ in ad if f"layers.{l}.{proj}.lora_B" in k_)
            B = ad[bkey].float().numpy()  # [D, r]
            nkey = next(k_ for k_ in idx if k_.endswith(f"layers.{l}.{norm}.weight") and "vision" not in k_)
            with safe_open(hf_hub_download(spec["repo"], idx[nkey], revision=spec["sha"]), "pt") as f:
                w = f.get_tensor(nkey).float().numpy()
            cols.append((1.0 + w)[:, None] * B)
    if not cols:
        return np.zeros((0, 0))
    M = np.concatenate(cols, 1)
    U, S, _ = np.linalg.svd(M, full_matrices=False)
    keep = min(k, int((S > 1e-6 * S[0]).sum()))
    return U[:, :keep]


def project_off(X, U):
    if U.size == 0:
        return X
    return X - (X @ U) @ U.T


# ------------------------------------------------------------------ main analysis
def token_lengths(prompts: list[str]) -> np.ndarray:
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODELS["gams"]["repo"], revision=MODELS["gams"]["sha"])
    return np.array([len(tok(p, add_special_tokens=False)["input_ids"]) for p in prompts])


def tfidf_cv(texts, y, groups, tr_texts=None, tr_y=None):
    """TF-IDF word(1-2)+char(2-5) logistic baseline: grouped CV AUROC, or fit on (tr_texts,tr_y) and score texts."""
    def feats(fit_texts, apply_texts):
        w = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        c = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1, sublinear_tf=True)
        Xf = hstack([w.fit_transform(fit_texts), c.fit_transform(fit_texts)]).tocsr()
        Xa = hstack([w.transform(apply_texts), c.transform(apply_texts)]).tocsr()
        return Xf, Xa
    texts = np.asarray(texts, dtype=object)
    if tr_texts is not None:
        Xf, Xa = feats(list(tr_texts), list(texts))
        return LogisticRegression(C=10.0, max_iter=3000).fit(Xf, tr_y).decision_function(Xa)
    oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(texts, y, groups):
        Xf, Xa = feats(list(texts[tr]), list(texts[te]))
        oof[te] = LogisticRegression(C=10.0, max_iter=3000).fit(Xf, y[tr]).decision_function(Xa)
    return oof


def run(model: str, mini: bool = False) -> None:
    t0 = time.time()
    act = (C.ROOT / "acts_mini" if mini else C.ACTS) / model
    out_dir = (C.ROOT / "results_mini" if mini else C.RES) / model
    spec = MODELS[model]
    Lp = spec["primary_layer"]
    C.need_acts(act / "S4_edit.npy")
    s3i = jload(act / "S3_index.json")["items"]
    s4i = jload(act / "S4_index.json")["items"]
    X3 = {ck: winsor(np.load(act / f"S3_{ck}.npy")) for ck in ("orig", "edit")}  # [N,49,6,D]
    X4 = {ck: winsor(np.load(act / f"S4_{ck}.npy")) for ck in ("orig", "edit")}  # [N,49,3,D] positions -2,-1,content_mean
    raw4_dim = float(np.abs(np.load(act / "S4_orig.npy", mmap_mode="r")[:, Lp, 1, 2339]).mean())
    logger.info(f"loaded + winsorized in {time.time()-t0:.0f}s; S3 {X3['orig'].shape} S4 {X4['orig'].shape}")
    H = X3["orig"].shape[1]
    P1_3, P1_4 = C.POS_IDX["-1"], 1  # pos -1 index in S3 (6 pos) and S4 (3 pos) captures
    df3 = pd.DataFrame(s3i)
    df4 = pd.DataFrame(s4i)
    jbb = (df3["set"] == "S3_jbb").values
    y3 = (df3["role"] == "harmful").astype(int).values
    g3 = df3["semantic_id"].values
    A = (df3["half"] == "A").values
    en3, sl3 = (df3["lang"] == "en").values, (df3["lang"] == "sl").values
    y4 = (df4["role"] == "harmful").astype(int).values
    g4 = df4["semantic_id"].values
    en4, sl4 = (df4["lang"] == "en").values, (df4["lang"] == "sl").values
    len3 = token_lengths(df3["prompt"].tolist())
    len4 = token_lengths(df4["prompt"].tolist())
    res: dict = {"model": model, "primary_layer": Lp, "primary_pos": "-1", "winsorization": "per-vector q=0.995 (E3)",
                 "raw_dim2339_mean_abs_S4_primary": raw4_dim,
                 "n": {"S3_jbb": int(jbb.sum()), "S3_dolly": int((~jbb).sum()), "S4": len(df4)}}

    # ---- C for the logistic probe: nested GroupKFold on S3 half A (pooled EN+SL) at the primary site
    m_fit = jbb & A
    Xp = X3["orig"][m_fit, Lp, P1_3]
    cv_c = {}
    for Cc in C_GRID:
        cv_c[Cc] = auc(y3[m_fit], cv_scores(Xp, y3[m_fit], g3[m_fit], "lr", Cc))
    C_best = max(C_GRID, key=lambda c: (round(cv_c[c], 4), -c))
    res["lr_C"] = {"grid_auc_halfA": {str(k): v for k, v in cv_c.items()}, "chosen": C_best}
    logger.info(f"C chosen {C_best} ({cv_c})")

    # ---- layer profiles at pos -1 (and content_mean for DiM AUROC)
    rng = np.random.default_rng(C.SEED)
    prof = {k: np.full(H, np.nan) for k in ["cos_raw", "ceil_en", "ceil_sl", "cos_corr", "cos_corr_sb", "auc_halfB_en", "auc_halfB_sl",
                                              "cv_dim_en", "cv_dim_sl", "cv_dim_pool", "cv_lr_en", "cv_lr_sl", "cv_lr_pool",
                                              "tr_en2sl_S3B", "tr_sl2en_S3B", "tr_en2sl_S4", "tr_sl2en_S4", "cos_lang_dEN", "cos_lang_dSL",
                                              "s4_frozen_orig_en", "s4_frozen_orig_sl", "s4_frozen_edit_en", "s4_frozen_edit_sl",
                                              "s4_refit_orig_en", "s4_refit_orig_sl", "s4_refit_edit_en", "s4_refit_edit_sl",
                                              "shift_norm_en", "shift_norm_sl", "orig_norm_en", "orig_norm_sl", "cos_dEN_heretic",
                                              "cv_dim_pool_contentmean", "s4_frozen_orig_en_cm", "s4_frozen_orig_sl_cm"]}
    her = torch.load(C.E1 / "directions" / ("gams" if model == "gams" else "gemma") / "directions.pt").float().numpy()  # [49,D]
    lr_layers = sorted(set(range(0, H, 4)) | {Lp, H - 1})
    ids_A = np.unique(g3[jbb & A])
    for L in range(H):
        X = X3["orig"][:, L, P1_3]
        dEN = dim_fit(X[jbb & A & en3], y3[jbb & A & en3])
        dSL = dim_fit(X[jbb & A & sl3], y3[jbb & A & sl3])
        dPO = dim_fit(X[jbb & A], y3[jbb & A])
        prof["cos_raw"][L] = cos(dEN["d"], dSL["d"])
        # split-half ceiling over semantic ids (twin diffs)
        def diffs(lang_mask):
            m = jbb & A & lang_mask
            dd = {}
            for sid, yy, x in zip(g3[m], y3[m], X[m]):
                dd.setdefault(sid, [None, None])[yy] = x
            return np.stack([dd[s][1] - dd[s][0] for s in ids_A if s in dd])
        De, Ds = diffs(en3), diffs(sl3)
        n = len(De)
        cs_e, cs_s = [], []
        for _ in range(200):
            perm = rng.permutation(n)
            a, b = perm[: n // 2], perm[n // 2:]
            cs_e.append(cos(De[a].mean(0), De[b].mean(0)))
            cs_s.append(cos(Ds[a].mean(0), Ds[b].mean(0)))
        ce, csl = float(np.mean(cs_e)), float(np.mean(cs_s))
        prof["ceil_en"][L], prof["ceil_sl"][L] = ce, csl
        prof["cos_corr"][L] = prof["cos_raw"][L] / np.sqrt(max(ce * csl, 1e-6))
        sb = lambda r: 2 * r / (1 + r) if r > 0 else r  # Spearman-Brown to full-sample reliability
        prof["cos_corr_sb"][L] = prof["cos_raw"][L] / np.sqrt(max(sb(ce) * sb(csl), 1e-6))
        # frozen DiM on half B (DEV sanity)
        for lang, lm_ in (("en", en3), ("sl", sl3)):
            mB = jbb & ~A & lm_
            prof[f"auc_halfB_{lang}"][L] = auc(y3[mB], dim_score(dPO, X[mB]))
        # grouped CV (all S3 JBB)
        for tag, mm in (("en", jbb & en3), ("sl", jbb & sl3), ("pool", jbb)):
            prof[f"cv_dim_{tag}"][L] = auc(y3[mm], cv_scores(X[mm], y3[mm], g3[mm], "dim"))
            if L in lr_layers:
                prof[f"cv_lr_{tag}"][L] = auc(y3[mm], cv_scores(X[mm], y3[mm], g3[mm], "lr", C_best))
        Xcm = X3["orig"][:, L, C.POS_IDX["content_mean"]]
        prof["cv_dim_pool_contentmean"][L] = auc(y3[jbb], cv_scores(Xcm[jbb], y3[jbb], g3[jbb], "dim"))
        # transfer (DiM): train EN half A -> SL half B (S3) and SL S4 (orig), and vice versa
        X4o = X4["orig"][:, L, P1_4]
        prof["tr_en2sl_S3B"][L] = auc(y3[jbb & ~A & sl3], dim_score(dEN, X[jbb & ~A & sl3]))
        prof["tr_sl2en_S3B"][L] = auc(y3[jbb & ~A & en3], dim_score(dSL, X[jbb & ~A & en3]))
        prof["tr_en2sl_S4"][L] = auc(y4[sl4], dim_score(dEN, X4o[sl4]))
        prof["tr_sl2en_S4"][L] = auc(y4[en4], dim_score(dSL, X4o[en4]))
        # language direction (harmless S3 half A: JBB benign + Dolly)
        hm = A & (y3 == 0)
        lang_dir = X[hm & sl3].mean(0) - X[hm & en3].mean(0)
        prof["cos_lang_dEN"][L] = cos(lang_dir, dEN["d"])
        prof["cos_lang_dSL"][L] = cos(lang_dir, dSL["d"])
        prof["cos_dEN_heretic"][L] = cos(dEN["d"], her[L])
        # held-out S4 frozen / refit (DiM profile)
        for ck in ("orig", "edit"):
            X4c = X4[ck][:, L, P1_4]
            for lang, lm_ in (("en", en4), ("sl", sl4)):
                prof[f"s4_frozen_{ck}_{lang}"][L] = auc(y4[lm_], dim_score(dPO, X4c[lm_]))
                prof[f"s4_refit_{ck}_{lang}"][L] = auc(y4[lm_], cv_scores(X4c[lm_], y4[lm_], g4[lm_], "dim"))
        dPOcm = dim_fit(Xcm[jbb & A], y3[jbb & A])
        for lang, lm_ in (("en", en4), ("sl", sl4)):
            prof[f"s4_frozen_orig_{lang}_cm"][L] = auc(y4[lm_], dim_score(dPOcm, X4["orig"][:, L, 2][lm_]))
            prof[f"shift_norm_{lang}"][L] = float(np.linalg.norm(X4["edit"][lm_, L, P1_4].mean(0) - X4["orig"][lm_, L, P1_4].mean(0)))
            prof[f"orig_norm_{lang}"][L] = float(np.linalg.norm(X4["orig"][lm_, L, P1_4].mean(0)))
        if L % 8 == 0:
            logger.info(f"L{L}: cos {prof['cos_raw'][L]:.3f} corr {prof['cos_corr'][L]:.3f} cvDiM pool {prof['cv_dim_pool'][L]:.3f} "
                        f"S4 frozen orig en/sl {prof['s4_frozen_orig_en'][L]:.3f}/{prof['s4_frozen_orig_sl'][L]:.3f} ({time.time()-t0:.0f}s)")
    np.savez(out_dir / f"layer_profiles_{model}.npz", **prof)
    res["layer_profile_file"] = f"results/{model}/layer_profiles_{model}.npz"
    res["profile_at_primary"] = {k: float(v[Lp]) for k, v in prof.items()}
    res["e3_reconcile"] = {"cos_raw_primary": float(prof["cos_raw"][Lp]),
                           "e3_value": {"gams": 0.83, "gemma": 0.92}[model],
                           "within_0.03": bool(abs(prof["cos_raw"][Lp] - {"gams": 0.83, "gemma": 0.92}[model]) <= 0.03)}
    e3prof = C.E3 / "results" / ("gams3" if model == "gams" else "gemma") / "cosine_profile.json"
    if e3prof.exists():
        res["e3_reconcile"]["e3_cosine_profile_file"] = str(e3prof)

    # ---- primary-site analyses (detailed, with CIs)
    X = X3["orig"][:, Lp, P1_3]
    dEN = dim_fit(X[jbb & A & en3], y3[jbb & A & en3])
    dSL = dim_fit(X[jbb & A & sl3], y3[jbb & A & sl3])
    dPO = dim_fit(X[jbb & A], y3[jbb & A])
    lrPO = lr_fit(X[jbb & A], y3[jbb & A], C_best)
    hm = A & (y3 == 0)
    lang_dir = X[hm & sl3].mean(0) - X[hm & en3].mean(0)
    prim: dict = {}
    # T3 placebo on half B: shuffled labels
    mB = jbb & ~A
    yperm = y3[mB].copy()
    np.random.default_rng(C.SEED).shuffle(yperm)
    prim["T3"] = {"halfB_dim_auc_en": auc(y3[mB & en3], dim_score(dPO, X[mB & en3])),
                  "halfB_dim_auc_sl": auc(y3[mB & sl3], dim_score(dPO, X[mB & sl3])),
                  "halfB_shuffled_label_auc": boot_auc(yperm, dim_score(dPO, X[mB]), g3[mB])}
    # S3 controls (grouped CV within JBB)
    ctrl = {}
    for tag, mm in (("en", jbb & en3), ("sl", jbb & sl3), ("pool", jbb)):
        s_dim = cv_scores(X[mm], y3[mm], g3[mm], "dim")
        s_lr = cv_scores(X[mm], y3[mm], g3[mm], "lr", C_best)
        ll = np.log(len3[mm])
        resid = s_dim - np.polyval(np.polyfit(ll, s_dim, 1), ll)
        tf = tfidf_cv(df3["prompt"].values[mm], y3[mm], g3[mm])
        ctrl[tag] = {"cv_dim": boot_auc(y3[mm], s_dim, g3[mm]), "cv_lr": boot_auc(y3[mm], s_lr, g3[mm]),
                     "length_only": auc(y3[mm], len3[mm]), "dim_length_residualized": auc(y3[mm], resid),
                     "tfidf_lexical": boot_auc(y3[mm], tf, g3[mm])}
    ctrl["lang_identity_projection_auc_for_harm"] = auc(y3[jbb], X[jbb] @ unit(lang_dir))
    ctrl["lang_dir_auc_for_language"] = auc(sl3[jbb].astype(int), X[jbb] @ unit(lang_dir))
    prim["S3_controls"] = ctrl
    # held-out S4 (orig): frozen DiM + LR, controls, per stratum
    X4o = X4["orig"][:, Lp, P1_4]
    X4e = X4["edit"][:, Lp, P1_4]
    held = {}
    tf_s4 = tfidf_cv(df4["prompt"].values, None, None, tr_texts=df3["prompt"].values[jbb & A], tr_y=y3[jbb & A])
    for lang, lm_ in (("en", en4), ("sl", sl4)):
        hd = {"frozen_dim": boot_auc(y4[lm_], dim_score(dPO, X4o[lm_]), g4[lm_]),
              "frozen_lr": boot_auc(y4[lm_], lrPO.decision_function(X4o[lm_]), g4[lm_]),
              "frozen_dim_EN_direction": auc(y4[lm_], dim_score(dEN, X4o[lm_])),
              "frozen_dim_SL_direction": auc(y4[lm_], dim_score(dSL, X4o[lm_])),
              "length_only": auc(y4[lm_], len4[lm_]),
              "tfidf_S3halfA_to_S4": boot_auc(y4[lm_], tf_s4[lm_], g4[lm_])}
        for st in ("hoc", "ind"):
            ms = lm_ & (df4["stratum"] == st).values
            hd[f"frozen_dim_{st}"] = boot_auc(y4[ms], dim_score(dPO, X4o[ms]), g4[ms])
        held[lang] = hd
    prim["S4_heldout_orig"] = held
    # FROZEN vs REFIT (+ edit-subspace projected control)
    U = edit_subspace(model, Lp)
    prim["edit_subspace"] = {"dim": int(U.shape[1]), "cos_dPO_with_U_norm_of_projection": float(np.linalg.norm(U.T @ dPO["dhat"])),
                             "cos_dPO_heretic_dir": cos(dPO["d"], her[Lp])}
    fr = {}
    for variant in ("plain", "U_projected"):
        Xo = X4o if variant == "plain" else project_off(X4o, U)
        Xe = X4e if variant == "plain" else project_off(X4e, U)
        Xf = X if variant == "plain" else project_off(X, U)
        dP = dim_fit(Xf[jbb & A], y3[jbb & A])
        lrP = lr_fit(Xf[jbb & A], y3[jbb & A], C_best)
        for lang, lm_ in (("en", en4), ("sl", sl4)):
            yy, gg = y4[lm_], g4[lm_]
            sc = {}
            for probe in ("dim", "lr"):
                fo = dim_score(dP, Xo[lm_]) if probe == "dim" else lrP.decision_function(Xo[lm_])
                fe = dim_score(dP, Xe[lm_]) if probe == "dim" else lrP.decision_function(Xe[lm_])
                ro = cv_scores(Xo[lm_], yy, gg, probe, C_best)
                re_ = cv_scores(Xe[lm_], yy, gg, probe, C_best)
                b_fr = boot_auc(yy, fe, gg, s2=fo)  # diff = frozen_edit - frozen_orig
                b_rf = boot_auc(yy, re_, gg, s2=ro)  # diff = refit_edit - refit_orig
                drop_frozen = b_fr["diff_ci95"][1] < 0
                refit_equiv = b_rf["diff_ci95"][0] >= -0.02 and b_rf["diff_ci95"][1] <= 0.02
                drop_refit = b_rf["diff_ci95"][1] < 0
                cls = "DRIFT" if (drop_frozen and refit_equiv) else ("INFO-LOSS" if (drop_frozen and drop_refit) else
                                                                    ("PRESERVED" if (not drop_frozen and not drop_refit) else "MIXED"))
                sc[probe] = {"frozen_orig": boot_auc(yy, fo, gg), "frozen_edit_minus_orig": b_fr, "refit_orig": boot_auc(yy, ro, gg),
                             "refit_edit_minus_orig": b_rf, "class": cls}
                if variant == "plain" and probe == "dim":
                    sc["_scores"] = {"fo": fo, "fe": fe}
            fr[f"{variant}|{lang}"] = {k: v for k, v in sc.items() if k != "_scores"}
            if variant == "plain":
                fr[f"{variant}|{lang}"]["_keep"] = sc.get("_scores")
    # per-item S4 scores for A2 (primary site): s (orig acts, frozen pooled DiM), post-edit frozen score, U-projected s
    dPU = dim_fit(project_off(X, U)[jbb & A], y3[jbb & A])
    s_orig = dim_score(dPO, X4o)
    items = df4[["semantic_id", "lang", "role", "stratum", "half"]].copy()
    items["s_frozen_orig"] = s_orig
    items["s_frozen_edit"] = dim_score(dPO, X4e)
    items["s_frozen_orig_Uproj"] = dim_score(dPU, project_off(X4o, U))
    items["lr_frozen_orig"] = lrPO.decision_function(X4o)
    items["proj_dEN_orig"] = X4o @ dEN["dhat"]
    items["proj_lang_orig"] = X4o @ unit(lang_dir)
    items["tok_len"] = len4
    items.to_parquet(out_dir / "s4_scores.parquet")
    for k in list(fr):
        fr[k].pop("_keep", None)
    prim["frozen_vs_refit"] = fr
    res["primary"] = prim
    # frozen directions for later projections
    np.savez(out_dir / f"frozen_directions_{model}.npz", dEN=dEN["d"], dSL=dSL["d"], dPO=dPO["d"], mid=dPO["mid"], lang_dir=lang_dir,
             U=U, lr_coef=lrPO[-1].coef_[0], lr_intercept=lrPO[-1].intercept_, sc_mean=lrPO[0].mean_, sc_scale=lrPO[0].scale_)
    # per-layer directions (for S5 projections): d_EN and lang_dir per layer at pos -1
    dEN_L = np.stack([unit(dim_fit(X3["orig"][jbb & A & en3, L, P1_3], y3[jbb & A & en3])["d"]) for L in range(H)])
    lang_L = np.stack([unit(X3["orig"][A & (y3 == 0) & sl3, L, P1_3].mean(0) - X3["orig"][A & (y3 == 0) & en3, L, P1_3].mean(0)) for L in range(H)])
    np.savez(out_dir / f"layer_dirs_{model}.npz", dEN=dEN_L.astype(np.float32), lang=lang_L.astype(np.float32))
    # sensitivity: per-dimension clip fitted on ORIGINAL S3 half A (the plan-text recipe), primary site AUROCs
    rawX = np.load(act / "S3_orig.npy", mmap_mode="r")[:, Lp, P1_3]
    raw4 = np.load(act / "S4_orig.npy", mmap_mode="r")[:, Lp, P1_4]
    lo, hi = np.quantile(rawX[A], 0.005, axis=0), np.quantile(rawX[A], 0.995, axis=0)
    Xd, X4d = np.clip(rawX, lo, hi), np.clip(raw4, lo, hi)
    dD = dim_fit(Xd[jbb & A], y3[jbb & A])
    res["sensitivity_perdim_clip"] = {"S4_frozen_dim_auc_en": auc(y4[en4], dim_score(dD, X4d[en4])),
                                      "S4_frozen_dim_auc_sl": auc(y4[sl4], dim_score(dD, X4d[sl4])),
                                      "share_of_dim2339_in_dPO_perdim": float(unit(dD["d"])[2339] ** 2),
                                      "share_of_dim2339_in_dPO_pervector": float(dPO["dhat"][2339] ** 2),
                                      "cos_dEN_dSL_perdim": cos(dim_fit(Xd[jbb & A & en3], y3[jbb & A & en3])["d"], dim_fit(Xd[jbb & A & sl3], y3[jbb & A & sl3])["d"])}
    res["wall_s"] = time.time() - t0
    jdump(res, out_dir / f"mech_{model}.json")
    logger.info(f"mech {model} done in {res['wall_s']:.0f}s")
    del X3, X4
    gc.collect()


def r_prior(model: str, labels: dict, mini: bool = False) -> dict:
    """r_prior from judged r_prior generations (original): mean(refused harmless) - mean(complied harmless) at pos -1,
    per layer, orthogonalized to d_EN; pooled and within-SL; UNDEFINED if n_refused < 10."""
    act = (C.ROOT / "acts_mini" if mini else C.ACTS) / model
    out_dir = (C.ROOT / "results_mini" if mini else C.RES) / model
    s3i = jload(act / "S3_index.json")["items"]
    X = winsor(np.load(act / "S3_orig.npy")[:, :, C.POS_IDX["-1"]])  # [N,49,D]
    dl = np.load(out_dir / f"layer_dirs_{model}.npz")
    lab = np.array([labels.get((model, "orig", "rprior", i["semantic_id"], i["lang"])) for i in s3i], dtype=object)
    isref, iscomp = lab == "refused", lab == "complied"
    lang = np.array([i["lang"] for i in s3i])
    out = {"n_refused": int(isref.sum()), "n_complied": int(iscomp.sum()),
           "n_refused_by_lang": {l: int((isref & (lang == l)).sum()) for l in C.LANGS}}
    res = {}
    for tag, m in (("pooled", np.ones(len(lang), bool)), ("withinSL", lang == "sl"), ("withinEN", lang == "en")):
        nr = int((isref & m).sum())
        if nr < 10 or int((iscomp & m).sum()) < 10:
            res[tag] = None
            continue
        r = X[isref & m].mean(0) - X[iscomp & m].mean(0)  # [49,D]
        rp = r - (r * dl["dEN"]).sum(-1, keepdims=True) * dl["dEN"]
        res[tag] = rp.astype(np.float32)
        out[f"{tag}_cos_with_lang_dir"] = [float(unit(a) @ unit(b)) for a, b in zip(rp, dl["lang"])]
        out[f"{tag}_cos_with_dEN_before_orth"] = [float(unit(a) @ unit(b)) for a, b in zip(r, dl["dEN"])]
    out["defined"] = {k: v is not None for k, v in res.items()}
    np.savez(out_dir / f"r_prior_{model}.npz", **{k: v for k, v in res.items() if v is not None})
    return out


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS), required=True)
    ap.add_argument("--mini", action="store_true")
    args = ap.parse_args()
    setup_logging(f"mech_{args.model}{'_mini' if args.mini else ''}")
    torch.set_num_threads(16)
    run(args.model, args.mini)


if __name__ == "__main__":
    main()

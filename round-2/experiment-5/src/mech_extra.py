#!/usr/bin/env python3
"""Drift geometry after the edit (exploratory, CPU): WHERE does the frozen original probe lose the harmful/harmless
ordering, and is the information still present elsewhere?

Per model, per hidden state L (pos -1, per-vector winsorized float32 activations, S4 held-out twins, per language):
  sep_frozen_{ck}     standardized harmful-minus-harmless separation (Cohen's d) along the FROZEN S3-half-A DiM axis
  sep_heretic_{ck}    the same along Heretic's own refusal direction (iteration-1 directions.pt, layer L)
  auc_compl_frozen_{ck}  grouped-CV DiM AUROC after projecting the frozen axis out (information OFF the frozen axis)
  auc_compl_heretic_{ck} grouped-CV DiM AUROC after projecting Heretic's direction out
  cos_refit_orig_edit cos(DiM_S4(orig), DiM_S4(edit)) -- rotation of the harm axis by the edit (full-sample directions)
  cos_refitedit_frozen cos(DiM_S4(edit), frozen axis)
  frac_sep_on_frozen_{ck}  share of the squared harmful-harmless mean difference lying on the frozen axis
Primary-site values get item-cluster bootstrap CIs (B=1000). Output: results/<m>/drift_geometry_<m>.json + .npz
Usage: .venv/bin/python mech_extra.py --model gams"""
from __future__ import annotations

import argparse
import gc
import time

import numpy as np
import pandas as pd
import torch
from loguru import logger

import common as C
from common import MODELS, jdump, jload, setup_logging
from mech import auc, cv_scores, dim_fit, unit, winsor


def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    a, b = x[y == 1], x[y == 0]
    sp = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return float((a.mean() - b.mean()) / (sp + 1e-12))


def proj_off(X: np.ndarray, u: np.ndarray) -> np.ndarray:
    u = unit(u)
    return X - np.outer(X @ u, u)


def run(model: str) -> None:
    t0 = time.time()
    act = C.ACTS / model
    out_dir = C.RES / model
    Lp = MODELS[model]["primary_layer"]
    C.need_acts(act / "S4_edit.npy")
    s3i = pd.DataFrame(jload(act / "S3_index.json")["items"])
    s4i = pd.DataFrame(jload(act / "S4_index.json")["items"])
    X3 = winsor(np.ascontiguousarray(np.load(act / "S3_orig.npy", mmap_mode="r")[:, :, C.POS_IDX["-1"]])).astype(np.float64)
    X4 = {ck: winsor(np.ascontiguousarray(np.load(act / f"S4_{ck}.npy", mmap_mode="r")[:, :, 1])) for ck in ("orig", "edit")}
    logger.info(f"loaded {model} in {time.time()-t0:.0f}s: S3 {X3.shape} S4 {X4['orig'].shape}")
    her = torch.load(C.E1 / "directions" / model / "directions.pt").float().numpy()
    jbb, A = (s3i["set"] == "S3_jbb").values, (s3i["half"] == "A").values
    y3 = (s3i["role"] == "harmful").astype(int).values
    y4 = (s4i["role"] == "harmful").astype(int).values
    g4 = s4i["semantic_id"].values
    langs = {l: (s4i["lang"] == l).values for l in C.LANGS}
    H = X3.shape[1]
    keys = ["sep_frozen", "sep_heretic", "auc_compl_frozen", "auc_compl_heretic", "frac_sep_on_frozen"]
    prof = {f"{k}_{ck}_{l}": np.full(H, np.nan) for k in keys for ck in ("orig", "edit") for l in C.LANGS}
    for l in C.LANGS:
        prof[f"cos_refit_orig_edit_{l}"] = np.full(H, np.nan)
        prof[f"cos_refitedit_frozen_{l}"] = np.full(H, np.nan)
        prof[f"cos_refitorig_frozen_{l}"] = np.full(H, np.nan)
    for L in range(1, H):
        dP = dim_fit(X3[jbb & A, L], y3[jbb & A])
        fz, hr = dP["dhat"], unit(her[L])
        for l, lm in langs.items():
            yy, gg = y4[lm], g4[lm]
            dd = {}
            for ck in ("orig", "edit"):
                X = X4[ck][lm, L].astype(np.float64)
                prof[f"sep_frozen_{ck}_{l}"][L] = cohen_d(X @ fz, yy)
                prof[f"sep_heretic_{ck}_{l}"][L] = cohen_d(X @ hr, yy)
                diff = X[yy == 1].mean(0) - X[yy == 0].mean(0)
                dd[ck] = diff
                prof[f"frac_sep_on_frozen_{ck}_{l}"][L] = float((diff @ fz) ** 2 / (diff @ diff + 1e-12))
                if L % 2 == 0 or L == Lp:  # grouped CV is the costly part: every 2nd layer + primary
                    prof[f"auc_compl_frozen_{ck}_{l}"][L] = auc(yy, cv_scores(proj_off(X, fz), yy, gg, "dim"))
                    prof[f"auc_compl_heretic_{ck}_{l}"][L] = auc(yy, cv_scores(proj_off(X, hr), yy, gg, "dim"))
            prof[f"cos_refit_orig_edit_{l}"][L] = float(unit(dd["orig"]) @ unit(dd["edit"]))
            prof[f"cos_refitedit_frozen_{l}"][L] = float(unit(dd["edit"]) @ fz)
            prof[f"cos_refitorig_frozen_{l}"][L] = float(unit(dd["orig"]) @ fz)
        if L % 8 == 0:
            logger.info(f"L{L}: sep_frozen EN orig/edit {prof['sep_frozen_orig_en'][L]:.2f}/{prof['sep_frozen_edit_en'][L]:.2f} "
                        f"cos(refit o,e) EN {prof['cos_refit_orig_edit_en'][L]:.2f} ({time.time()-t0:.0f}s)")
    np.savez(out_dir / f"drift_geometry_{model}.npz", **prof)
    # primary-site bootstrap CIs (item cluster = semantic id)
    dP = dim_fit(X3[jbb & A, Lp], y3[jbb & A])
    fz, hr = dP["dhat"], unit(her[Lp])
    prim = {}
    for l, lm in langs.items():
        yy, gg = y4[lm], g4[lm]
        Xo, Xe = X4["orig"][lm, Lp].astype(np.float64), X4["edit"][lm, Lp].astype(np.float64)
        stats = {"sep_frozen_orig": [], "sep_frozen_edit": [], "cos_refit_orig_edit": [], "frac_on_frozen_orig": [], "frac_on_frozen_edit": [],
                 "sep_heretic_orig": [], "sep_heretic_edit": []}
        uniq, inv = np.unique(gg, return_inverse=True)
        members = [np.flatnonzero(inv == k) for k in range(len(uniq))]
        rng = np.random.default_rng(C.SEED)
        for _ in range(1000):
            idx = np.concatenate([members[k] for k in rng.integers(0, len(uniq), len(uniq))])
            y_ = yy[idx]
            do = Xo[idx][y_ == 1].mean(0) - Xo[idx][y_ == 0].mean(0)
            de = Xe[idx][y_ == 1].mean(0) - Xe[idx][y_ == 0].mean(0)
            stats["sep_frozen_orig"].append(cohen_d(Xo[idx] @ fz, y_))
            stats["sep_frozen_edit"].append(cohen_d(Xe[idx] @ fz, y_))
            stats["sep_heretic_orig"].append(cohen_d(Xo[idx] @ hr, y_))
            stats["sep_heretic_edit"].append(cohen_d(Xe[idx] @ hr, y_))
            stats["cos_refit_orig_edit"].append(float(unit(do) @ unit(de)))
            stats["frac_on_frozen_orig"].append(float((do @ fz) ** 2 / (do @ do)))
            stats["frac_on_frozen_edit"].append(float((de @ fz) ** 2 / (de @ de)))
        do = Xo[yy == 1].mean(0) - Xo[yy == 0].mean(0)
        de = Xe[yy == 1].mean(0) - Xe[yy == 0].mean(0)
        point = {"sep_frozen_orig": cohen_d(Xo @ fz, yy), "sep_frozen_edit": cohen_d(Xe @ fz, yy),
                 "sep_heretic_orig": cohen_d(Xo @ hr, yy), "sep_heretic_edit": cohen_d(Xe @ hr, yy),
                 "cos_refit_orig_edit": float(unit(do) @ unit(de)), "frac_on_frozen_orig": float((do @ fz) ** 2 / (do @ do)),
                 "frac_on_frozen_edit": float((de @ fz) ** 2 / (de @ de))}
        prim[l] = {k: {"value": point[k], "ci95": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]} for k, v in stats.items()}
        prim[l]["norm_of_mean_diff_orig"] = float(np.linalg.norm(do))
        prim[l]["norm_of_mean_diff_edit"] = float(np.linalg.norm(de))
        prim[l]["auc_compl_frozen_orig"] = float(prof[f"auc_compl_frozen_orig_{l}"][Lp])
        prim[l]["auc_compl_frozen_edit"] = float(prof[f"auc_compl_frozen_edit_{l}"][Lp])
        prim[l]["auc_compl_heretic_orig"] = float(prof[f"auc_compl_heretic_orig_{l}"][Lp])
        prim[l]["auc_compl_heretic_edit"] = float(prof[f"auc_compl_heretic_edit_{l}"][Lp])
    # per-item edit shift (for the item-level flip analysis in analyze.py): projections on Heretic's direction and on the
    # frozen axis in orig and edit, at every 4th layer + primary, and the norm of the per-item activation shift
    cols = {"semantic_id": s4i["semantic_id"].values, "lang": s4i["lang"].values, "role": s4i["role"].values, "stratum": s4i["stratum"].values}
    for L in sorted(set(range(4, H, 4)) | {Lp}):
        hr_L = unit(her[L])
        fz_L = dim_fit(X3[jbb & A, L], y3[jbb & A])["dhat"]
        for ck in ("orig", "edit"):
            cols[f"her_{ck}_L{L}"] = X4[ck][:, L].astype(np.float64) @ hr_L
            cols[f"fz_{ck}_L{L}"] = X4[ck][:, L].astype(np.float64) @ fz_L
        cols[f"shiftnorm_L{L}"] = np.linalg.norm(X4["edit"][:, L].astype(np.float64) - X4["orig"][:, L].astype(np.float64), axis=1)
        cols[f"orignorm_L{L}"] = np.linalg.norm(X4["orig"][:, L].astype(np.float64), axis=1)
    pd.DataFrame(cols).to_parquet(out_dir / f"edit_shift_items_{model}.parquet")
    # group-level: mean shift along Heretic's direction for harmful items, EN vs SL (representation-level transfer)
    shift = {}
    for l, lm in langs.items():
        hmask = lm & (y4 == 1)
        shift[l] = {f"L{L}": float(np.mean(cols[f"her_edit_L{L}"][hmask] - cols[f"her_orig_L{L}"][hmask]) /
                                   (np.std(cols[f"her_orig_L{L}"][lm]) + 1e-12)) for L in sorted(set(range(4, H, 4)) | {Lp})}
    # layer where the frozen separation first collapses (edit sep < 50% of orig), per language
    onset = {}
    for l in C.LANGS:
        so, se = prof[f"sep_frozen_orig_{l}"], prof[f"sep_frozen_edit_{l}"]
        ok = [L for L in range(1, H) if np.isfinite(so[L]) and so[L] > 1.0 and se[L] < 0.5 * so[L]]
        onset[l] = int(ok[0]) if ok else None
    res = {"model": model, "primary_layer": Lp, "primary": prim, "collapse_onset_layer": onset,
           "harmful_shift_along_heretic_dir_in_orig_sd_units": shift,
           "profile_file": f"results/{model}/drift_geometry_{model}.npz", "wall_s": time.time() - t0,
           "note": "exploratory; Cohen's d along fixed axes; AUROC in the orthogonal complement by 5-fold GroupKFold DiM"}
    jdump(res, out_dir / f"drift_geometry_{model}.json")
    logger.info(f"drift geometry {model} done in {res['wall_s']:.0f}s; onset {onset}")
    del X3, X4
    gc.collect()


@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS), required=True)
    args = ap.parse_args()
    setup_logging(f"mech_extra_{args.model}")
    torch.set_num_threads(12)
    run(args.model)


if __name__ == "__main__":
    main()

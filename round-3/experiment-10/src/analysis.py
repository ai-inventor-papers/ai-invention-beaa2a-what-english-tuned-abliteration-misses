#!/usr/bin/env python3
"""PART C/D analysis: per-cell 4-way outcome tables with semantic-item cluster bootstraps and exact McNemar tests, the
collateral / DEGRADED gate, the frozen predictions PA1-PB4, the coverage regression, judge sensitivity and the placebo
permutations. Reads only results/cells/*/{gens.json,tf.json,meta.json}, the judge caches and the frozen files; writes
results/analysis_summary.json + results/per_item.parquet."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats

import common as C
from common import LANGS, jdump, jload, setup_logging
from judge import JUDGE_B, ckey
from judge_local import JUDGE_LOCAL, load_cache
from labels import four_way, reply_lang, wrong_lang

NREP = 2000
BANDS = [(0, 12), (12, 24), (24, 36), (36, 48)]


# ------------------------------------------------------------------------------------------ loading
JUDGE_KEYS = {"local": [JUDGE_LOCAL], "api": [JUDGE_B, "openai/gpt-4.1"]}


def load_api_caches() -> dict:
    """Every gpt-4.1 label reachable for free: this artifact's own cache (empty - the run's key was exhausted) plus the
    iteration-2 caches, joined by sha256(model|prompt|response), so a byte-identical generation gets a second label."""
    out = {}
    for p in (C.E8 / "results/judge_cache.jsonl", C.RES / "judge_cache.jsonl"):
        if p.exists():
            out |= load_cache(p)   # exp4's judge files are keyed by RefusEU item id, not by content hash: not joinable
    return out


def build_frame(judges: dict) -> pd.DataFrame:
    rows = []
    lang_cache: dict = {}
    for d in sorted(C.CELLS.iterdir()):
        p = d / "gens.json"
        if not p.exists():
            continue
        meta = jload(d / "meta.json") if (d / "meta.json").exists() else {}
        for r in jload(p):
            txt = r["response"]
            if txt not in lang_cache:
                lang_cache[txt] = reply_lang(txt)
            rl = lang_cache[txt]
            row = {"cell": r["cell"], "split": r["split"], "uid": r["uid"], "semantic_id": r["semantic_id"],
                   "kind": r["kind"], "role": r.get("role"), "lang": r["lang"], "n_tokens": r["n_tokens"],
                   "reply_lang": rl, "wrong_lang": wrong_lang(r["lang"], rl), "rep4": C.rep4(txt),
                   "rule": r["rule_label"],
                   "tier": meta.get("tier"), "part": meta.get("part"), "type": meta.get("type"),
                   "group": meta.get("group"), "member": meta.get("member")}
            for jname, cache in judges.items():
                lab = None
                for model in JUDGE_KEYS[jname]:
                    hit = cache.get(ckey(model, r["prompt"], r["response"]))
                    if hit:
                        lab = hit.get("label")
                        break
                row[f"label_{jname}"] = lab
                row[f"cls4_{jname}"] = four_way(lab, r["lang"], rl, row["rep4"]) if lab is not None else None
            rows.append(row)
    return pd.DataFrame(rows)


def cell_meta() -> dict:
    out = {}
    for d in sorted(C.CELLS.iterdir()):
        if (d / "meta.json").exists():
            out[d.name] = jload(d / "meta.json")
    return out


# ------------------------------------------------------------------------------------------ statistics
def boot_ci(vals_by_item: dict, rng, nrep: int = NREP) -> tuple[float, float, float]:
    """Cluster bootstrap over semantic items. vals_by_item: {item: [v, ...]} -> (mean, lo, hi)."""
    keys = sorted(vals_by_item)
    if not keys:
        return float("nan"), float("nan"), float("nan")
    flat = np.concatenate([np.asarray(vals_by_item[k], float) for k in keys])
    means = []
    arrs = [np.asarray(vals_by_item[k], float) for k in keys]
    for _ in range(nrep):
        b = rng.integers(0, len(keys), len(keys))
        means.append(np.concatenate([arrs[i] for i in b]).mean())
    return float(flat.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def paired_boot(a: dict, b: dict, rng, nrep: int = NREP) -> dict:
    """Paired cluster bootstrap of mean(a) - mean(b) over shared semantic items."""
    keys = sorted(set(a) & set(b))
    if not keys:
        return {"diff": float("nan"), "ci": [float("nan")] * 2, "n": 0}
    da = np.array([np.mean(a[k]) for k in keys])
    db = np.array([np.mean(b[k]) for k in keys])
    d = da - db
    reps = [d[rng.integers(0, len(keys), len(keys))].mean() for _ in range(nrep)]
    return {"diff": float(d.mean()), "ci": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))], "n": len(keys)}


def mcnemar(a: list, b: list) -> float:
    """Exact McNemar p (two-sided) on paired binary vectors."""
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n01 = int((~a & b).sum())
    n10 = int((a & ~b).sum())
    n = n01 + n10
    return 1.0 if n == 0 else float(min(1.0, 2 * stats.binom.cdf(min(n01, n10), n, 0.5)))


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, prev = {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = max(prev, min(1.0, (m - i) * p))
        out[k] = adj
        prev = adj
    return out


def by_item(df: pd.DataFrame, col: str) -> dict:
    out: dict = {}
    for sid, v in df.groupby("semantic_id")[col]:
        vv = v.dropna().tolist()
        if vv:
            out[sid] = vv
    return out


# ------------------------------------------------------------------------------------------ predictors
def predictors(meta: dict, dEN, dSL) -> dict | None:
    """Coverage / energy / geometry predictors of a weight cell from its per-module energies."""
    if "E_per_layer" not in meta:
        return None
    e = np.asarray(meta["E_per_layer"], float)
    tot = float(e.sum())
    if tot <= 0:
        return None
    lay = np.where(e > 1e-9)[0]
    frac = e / tot
    cosl = np.array([float(dEN[h + 1] @ dSL[h + 1] / (np.linalg.norm(dEN[h + 1]) * np.linalg.norm(dSL[h + 1]))) for h in range(len(e))])
    return {"E": tot, "logE": float(np.log(tot)), "n_cov": int(len(lay)), "log_ncov": float(np.log(len(lay))),
            "span": float(lay.max() - lay.min() + 1) if len(lay) else 0.0,
            "mean_depth": float((frac * np.arange(len(e))).sum()),
            "b1": float((frac * cosl).sum()),
            **{f"b3_{i}": float(frac[a:b].sum()) for i, (a, b) in enumerate(BANDS)}}


def ols_r2(y: np.ndarray, X: np.ndarray) -> float:
    X = np.column_stack([np.ones(len(y)), X]) if X.size else np.ones((len(y), 1))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    ss = float(((y - y.mean()) ** 2).sum())
    return float(1 - (res ** 2).sum() / ss) if ss > 0 else float("nan")


# ------------------------------------------------------------------------------------------ main
@logger.catch(reraise=True)
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="local", choices=["local", "api"])
    ap.add_argument("--out", default=str(C.RES / "analysis_summary.json"))
    args = ap.parse_args()
    setup_logging("analysis")
    rng = np.random.default_rng(C.SEED)
    judges = {"local": load_cache(), "api": load_api_caches()}
    df = build_frame(judges)
    df.to_parquet(C.RES / "per_item.parquet")
    meta = cell_meta()
    Z = np.load(C.E8 / "directions/gams3_all_layers.npz")
    dEN, dSL = Z["dEN"], Z["dSL"]
    PJ, cls = args.judge, f"cls4_{args.judge}"
    S: dict = {"judge_primary": PJ, "n_rows": len(df), "n_cells": df.cell.nunique(),
               "judged_coverage": {j: float(df[f"cls4_{j}"].notna().mean()) for j in judges}}

    # ---------------------------------------------------------------- per-cell outcome table
    table: dict = {}
    for cell, dc in df.groupby("cell"):
        row: dict = {"tier": meta.get(cell, {}).get("tier"), "type": meta.get(cell, {}).get("type"),
                     "E_exact": meta.get(cell, {}).get("E_exact"), "group": meta.get(cell, {}).get("group"),
                     "member": meta.get(cell, {}).get("member"), "n_layers": len(meta.get(cell, {}).get("layers", []) or [])}
        for split in sorted(dc.split.unique()):
            for g in LANGS:
                d = dc[(dc.split == split) & (dc.lang == g)]
                if d.empty:
                    continue
                jd = d[d[cls].notna()]
                pre = f"{split}_{g}"
                row[f"{pre}_n"] = int(len(d))
                row[f"{pre}_n_judged"] = int(len(jd))
                if len(jd):
                    for k in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID"):
                        row[f"{pre}_{k}"] = float((jd[cls] == k).mean())
                    m, lo, hi = boot_ci(by_item(jd.assign(v=(jd[cls] == "REFUSED").astype(float)), "v"), rng)
                    row[f"{pre}_REFUSED_ci"] = [lo, hi]
                row[f"{pre}_wrong_lang"] = float(d.wrong_lang.mean())
                row[f"{pre}_rep4_gt_0.5"] = float((d.rep4 > 0.5).mean())
        tf = C.CELLS / cell / "tf.json"
        if tf.exists():
            t = jload(tf)
            for g in LANGS:
                row[f"flores_dNLL_{g}"] = float(np.mean(list(t[f"flores_{g}"].values())))
                if f"kl_{g}" in t:
                    row[f"dolly_KL_{g}"] = float(np.mean(list(t[f"kl_{g}"].values())))
                    row[f"mc_acc_{g}"] = float(np.mean(list(t[f"mc_{g}"].values())))
        table[cell] = row
    # DEGRADED gate (Gate 9) vs the no-op cell of the same part
    for part, ref in (("A", "dev_A0"), ("B", "NOOP")):
        if ref not in table:
            continue
        for cell, row in table.items():
            if meta.get(cell, {}).get("part") != part:
                continue
            flags = []
            for g in LANGS:
                for split in ("screen", "confirm", "dev"):
                    if f"{split}_{g}_INVALID" in row and row[f"{split}_{g}_INVALID"] > 0.05:
                        flags.append(f"invalid_{split}_{g}")
                    if f"{split}_{g}_wrong_lang" in row and row[f"{split}_{g}_wrong_lang"] - table[ref].get(f"{split}_{g}_wrong_lang", 0) > 0.03:
                        flags.append(f"wrong_lang_{split}_{g}")
                if row.get(f"flores_dNLL_{g}", 0) > 1.0:
                    flags.append(f"flores_{g}")
                if f"mc_acc_{g}" in row and table[ref].get(f"mc_acc_{g}") is not None and \
                        table[ref][f"mc_acc_{g}"] - row[f"mc_acc_{g}"] > 0.05:
                    flags.append(f"mc_{g}")
            row["degraded"] = sorted(set(flags))
    S["cell_table"] = table

    # ---------------------------------------------------------------- McNemar vs the no-op of the same part
    mc: dict = {}
    for cell, dc in df.groupby("cell"):
        ref = "dev_A0" if meta.get(cell, {}).get("part") == "A" else "NOOP"
        if cell == ref or ref not in set(df.cell):
            continue
        d0 = df[df.cell == ref]
        for split in sorted(dc.split.unique()):
            for g in LANGS:
                a = dc[(dc.split == split) & (dc.lang == g) & dc[cls].notna()].set_index("uid")[cls]
                b = d0[(d0.split == split) & (d0.lang == g) & d0[cls].notna()].set_index("uid")[cls]
                k = sorted(set(a.index) & set(b.index))
                if len(k) >= 10:
                    mc[f"{cell}|{split}|{g}"] = {"p_mcnemar_vs_noop": mcnemar((b[k] == "REFUSED").tolist(), (a[k] == "REFUSED").tolist()),
                                                 "n": len(k), "rate": float((a[k] == "REFUSED").mean()),
                                                 "rate_noop": float((b[k] == "REFUSED").mean())}
    S["mcnemar_vs_noop"] = mc

    # ---------------------------------------------------------------- frozen predictions
    pred: dict = {}
    pvals: dict = {}
    ri = jload(C.RES / "redundancy_index.json") if (C.RES / "redundancy_index.json").exists() else None
    if ri:
        lo, hi = ri["diff_boot_CI95"]
        pred["PA1"] = {"index_EN": ri["index"]["en"], "index_SL": ri["index"]["sl"], "diff": ri["diff_SL_minus_EN"],
                       "diff_CI95": [lo, hi], "margin": 8,
                       "verdict": "EQUIVALENT_WITHIN_MARGIN" if lo >= -8 and hi <= 8 else
                                  ("FALSIFIED" if lo > 8 or hi < -8 else "INCONCLUSIVE"),
                       "note": "TOST-style: equivalence only if the whole 95% CI of index_SL - index_EN lies in [-8, +8]."}

    # PB1: coverage dR2 on the SCREEN set, dEN weight cells only
    wcells = [c for c, m in meta.items() if m.get("part") == "B" and m.get("family") == "dEN" and "E_per_layer" in m]
    rowsX = []
    for c in wcells:
        pr = predictors(meta[c], dEN, dSL)
        d = df[(df.cell == c) & (df.split == "screen") & df[cls].notna()]
        if pr is None or d.empty:
            continue
        r = {"cell": c, **pr}
        for g in LANGS:
            dg = d[d.lang == g]
            r[f"ref_{g}"] = float((dg[cls] == "REFUSED").mean()) if len(dg) else np.nan
        rowsX.append(r)
    X = pd.DataFrame(rowsX)
    X = X.dropna(subset=["ref_sl", "ref_en"]) if {"ref_sl", "ref_en"} <= set(X.columns) else X.iloc[:0]
    if len(X) >= 8:
        base_cols = ["logE", "ref_en", "b1", "b3_0", "b3_1", "b3_2", "b3_3"]
        cov_cols = ["log_ncov", "span", "mean_depth"]
        y = X.ref_sl.to_numpy()
        r2b = ols_r2(y, X[base_cols].to_numpy())
        r2f = ols_r2(y, X[base_cols + cov_cols].to_numpy())
        reps = []
        for _ in range(NREP):
            b = rng.integers(0, len(X), len(X))
            Xi, yi = X.iloc[b], y[b]
            reps.append(ols_r2(yi, Xi[base_cols + cov_cols].to_numpy()) - ols_r2(yi, Xi[base_cols].to_numpy()))
        reps = np.array(reps)
        # honest small-n companions: adjusted R2 and leave-one-cell-out CV dR2 (10 predictors on ~20 cells inflates
        # the in-sample dR2; the frozen number is the in-sample one, both are reported)
        def adj(r2v, k):
            n = len(y)
            return float(1 - (1 - r2v) * (n - 1) / max(n - k - 1, 1))

        def loo_sse(cols):
            e = []
            for i in range(len(X)):
                tr = [j for j in range(len(X)) if j != i]
                A = np.column_stack([np.ones(len(tr))] + ([X.iloc[tr][cols].to_numpy()] if cols else []))
                beta, *_ = np.linalg.lstsq(A, y[tr], rcond=None)
                xi = np.concatenate([[1.0], X.iloc[i][cols].to_numpy()]) if cols else np.array([1.0])
                e.append((y[i] - xi @ beta) ** 2)
            return float(np.sum(e))
        sst = float(((y - y.mean()) ** 2).sum())
        cv_base, cv_full = 1 - loo_sse(base_cols) / sst, 1 - loo_sse(base_cols + cov_cols) / sst
        pred["PB1"] = {"n_cells": int(len(X)), "R2_base": r2b, "R2_full": r2f, "dR2": r2f - r2b,
                       "adjR2_base": adj(r2b, len(base_cols)), "adjR2_full": adj(r2f, len(base_cols + cov_cols)),
                       "loo_cv_R2_base": cv_base, "loo_cv_R2_full": cv_full, "loo_cv_dR2": cv_full - cv_base,
                       "decomposition": {
                           "R2_logE": ols_r2(y, X[["logE"]].to_numpy()),
                           "R2_logE_plus_placement_b3": ols_r2(y, X[["logE", "b3_0", "b3_1", "b3_2", "b3_3"]].to_numpy()),
                           "R2_logE_plus_count": ols_r2(y, X[["logE", "log_ncov"]].to_numpy()),
                           "R2_logE_plus_count_and_span": ols_r2(y, X[["logE", "log_ncov", "span", "mean_depth"]].to_numpy()),
                           "note": "b3_* are the fractions of total removal energy in the four 12-layer bands, i.e. WHERE the "
                                   "edit sits; log_ncov/span/mean_depth are HOW MUCH depth it covers. The frozen PB1 base "
                                   "model already contains b3, so the coverage terms are tested on top of placement."},
                       "parsimonious": {"R2_logE_only": ols_r2(y, X[["logE"]].to_numpy()),
                                        "R2_logE_plus_ncov": ols_r2(y, X[["logE", "log_ncov"]].to_numpy()),
                                        "dR2_ncov_given_logE": ols_r2(y, X[["logE", "log_ncov"]].to_numpy()) -
                                                               ols_r2(y, X[["logE"]].to_numpy())},
                       "dR2_cell_boot_CI95": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))],
                       "base_terms": base_cols, "coverage_terms": cov_cols,
                       "verdict": "SUPPORTED" if (r2f - r2b) >= 0.10 and float(np.percentile(reps, 2.5)) > 0.05 else "NOT_SUPPORTED"}
        pvals["PB1"] = float(np.mean(reps <= 0))
        S["coverage_design_matrix"] = X.to_dict("records")

    # PB2 / PB3: matched-energy paired contrasts on the CONFIRMATION set (falls back to SCREEN if absent)
    design = jload(C.CFG / "design.json") if (C.CFG / "design.json").exists() else {"groups": {}}
    narrow, broad = ["B2", "B3"], ["STR2", "ALL"]
    judged_conf = df[(df.split == "confirm") & df[cls].notna()]
    split_use = "confirm" if len(judged_conf) else "screen"
    grp: dict = {}
    for gname in design.get("groups", {}):
        cells_n = [f"{gname}_{m}" for m in narrow if f"{gname}_{m}" in set(df.cell)]
        cells_b = [f"{gname}_{m}" for m in broad if f"{gname}_{m}" in set(df.cell)]
        if not cells_n or not cells_b:
            continue
        entry = {"E_target": design["groups"][gname]["target_E"], "narrow": cells_n, "broad": cells_b}
        for g in LANGS:
            def pick(cl):
                d = df[df.cell.isin(cl) & (df.split == split_use) & (df.lang == g) & df[cls].notna()]
                return by_item(d.assign(v=(d[cls] == "REFUSED").astype(float)), "v")
            entry[g] = paired_boot(pick(cells_n), pick(cells_b), rng)
            entry[f"{g}_narrow_rate"] = float(np.mean([np.mean(v) for v in pick(cells_n).values()] or [np.nan]))
            entry[f"{g}_broad_rate"] = float(np.mean([np.mean(v) for v in pick(cells_b).values()] or [np.nan]))
            rc = f"{gname}_RND_ALL"
            if rc in set(df.cell) and "NOOP" in set(df.cell):
                d0 = df[(df.cell == "NOOP") & (df.split == split_use) & (df.lang == g) & df[cls].notna()]
                dr = df[(df.cell == rc) & (df.split == split_use) & (df.lang == g) & df[cls].notna()]
                base = by_item(d0.assign(v=(d0[cls] == "REFUSED").astype(float)), "v")
                entry[f"{g}_cut_random"] = paired_boot(base, by_item(dr.assign(v=(dr[cls] == "REFUSED").astype(float)), "v"), rng)
                entry[f"{g}_cut_broad"] = paired_boot(base, pick(cells_b), rng)
        grp[gname] = entry
    if grp:
        def pooled(cl_sel, g):
            d = df[df.cell.isin(cl_sel) & (df.split == split_use) & (df.lang == g) & df[cls].notna()]
            return by_item(d.assign(v=(d[cls] == "REFUSED").astype(float)), "v")
        alln = [f"{g_}_{m}" for g_ in grp for m in narrow if f"{g_}_{m}" in set(df.cell)]
        allb = [f"{g_}_{m}" for g_ in grp for m in broad if f"{g_}_{m}" in set(df.cell)]
        pooled_res = {g: paired_boot(pooled(alln, g), pooled(allb, g), rng) for g in LANGS}
        keys = sorted(set(pooled(alln, "sl")) & set(pooled(allb, "sl")) & set(pooled(alln, "en")) & set(pooled(allb, "en")))
        d_sl = np.array([np.mean(pooled(alln, "sl")[k]) - np.mean(pooled(allb, "sl")[k]) for k in keys])
        d_en = np.array([np.mean(pooled(alln, "en")[k]) - np.mean(pooled(allb, "en")[k]) for k in keys])
        inter = d_sl - d_en
        reps = [inter[rng.integers(0, len(keys), len(keys))].mean() for _ in range(NREP)]
        def verdict(d: dict, want: str = "positive") -> str:
            lo, hi = d["ci"]
            if np.isnan(lo):
                return "NOT_EVALUABLE"
            if lo > 0:
                return "SUPPORTED" if want == "positive" else "FALSIFIED_OPPOSITE_DIRECTION"
            if hi < 0:
                return "FALSIFIED_OPPOSITE_DIRECTION" if want == "positive" else "SUPPORTED"
            return "NOT_SUPPORTED_CI_SPANS_ZERO"
        pred["PB2"] = {"split": split_use, "groups": grp, "pooled_narrow_minus_broad": pooled_res,
                       "verdict": verdict(pooled_res["sl"]),
                       "reading": "PB2 predicted broad-and-weak BELOW narrow-and-strong in Slovene, i.e. (narrow - broad) > 0."}
        pred["PB3"] = {"interaction_SL_minus_EN": float(inter.mean()),
                       "ci": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))], "n_items": len(keys),
                       "verdict": verdict({"ci": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))]}),
                       "reading": "PB3 predicted the (narrow - broad) contrast to be LARGER in Slovene than in English."}
        pvals["PB2"] = float(2 * min(np.mean(np.array([np.mean(d_sl[rng.integers(0, len(keys), len(keys))]) for _ in range(NREP)]) <= 0),
                                     np.mean(np.array([np.mean(d_sl[rng.integers(0, len(keys), len(keys))]) for _ in range(NREP)]) >= 0)))
        pvals["PB3"] = float(2 * min(np.mean(np.array(reps) <= 0), np.mean(np.array(reps) >= 0)))

    # SECONDARY (pre-planned coverage sets, contrast named after seeing the design): CONTIGUOUS vs SPREAD at matched energy
    # AND matched layer count. STR4 covers 12 layers (every 4th of 48), exactly as many as a 12-layer band, at the same
    # total removal energy - so it isolates WHERE the covered layers sit from how many there are and how big the edit is.
    place: dict = {}
    for gname in design.get("groups", {}):
        for band in ("B2", "B3"):
            a_c, b_c = f"{gname}_{band}", f"{gname}_STR4"
            if a_c not in set(df.cell) or b_c not in set(df.cell):
                continue
            row = {"energy": design["groups"][gname]["target_E"],
                   "n_layers_band": len(meta.get(a_c, {}).get("layers", []) or []),
                   "n_layers_stride": len(meta.get(b_c, {}).get("layers", []) or [])}
            for g in LANGS:
                def q(cc):
                    d = df[(df.cell == cc) & (df.split == split_use) & (df.lang == g) & df[cls].notna()]
                    return by_item(d.assign(v=(d[cls] == "REFUSED").astype(float)), "v")
                row[g] = paired_boot(q(a_c), q(b_c), rng)
                row[f"{g}_band_rate"] = float(np.mean([np.mean(v) for v in q(a_c).values()] or [np.nan]))
                row[f"{g}_stride_rate"] = float(np.mean([np.mean(v) for v in q(b_c).values()] or [np.nan]))
            place[f"{gname}_{band}_vs_STR4"] = row
    S["contiguous_vs_spread_matched_count_and_energy"] = place

    # PB4: out-of-sample use of the DEV-frozen index
    if ri:
        obs, prdv, rows4 = [], [], []
        for c in wcells:
            m = meta[c]
            ncov = len(m.get("layers", []) or [])
            k = min(48, max(4, int(np.ceil(ncov / 4) * 4)))
            d = df[(df.cell == c) & (df.split == split_use) & df[cls].notna()]
            for g in LANGS:
                dg = d[d.lang == g]
                if dg.empty:
                    continue
                o = float((dg[cls] == "REFUSED").mean())
                p = ri["prefix_curves"][g][str(k)] if str(k) in ri["prefix_curves"][g] else ri["prefix_curves"][g][k]
                obs.append(o)
                prdv.append(p)
                rows4.append({"cell": c, "lang": g, "n_cov": ncov, "k": k, "predicted": p, "observed": o,
                              "below_index": bool(ncov < ri["index_numeric"][g]), "above_half": bool(o > 0.5)})
        if len(obs) >= 6:
            rho, pv = stats.spearmanr(prdv, obs)
            thr = [r for r in rows4 if r["below_index"]]
            pred["PB4"] = {"n": len(obs), "spearman": float(rho), "p": float(pv), "rows": rows4,
                           "threshold_check_n": len(thr),
                           "threshold_check_pass_rate": float(np.mean([r["above_half"] for r in thr])) if thr else None,
                           "verdict": "SUPPORTED" if rho >= 0.6 else "NOT_SUPPORTED"}
            pvals["PB4"] = float(pv)
    if ri and "PA1" in pred:
        # TOST for equivalence within +-8 layers: normal approximation to the frozen bootstrap distribution of
        # index_SL - index_EN (its 95% CI is what freeze.py stored), p = max of the two one-sided tail probabilities.
        lo_, hi_ = pred["PA1"]["diff_CI95"]
        se = max((hi_ - lo_) / 3.9199, 1e-6)
        d_ = pred["PA1"]["diff"]
        pvals["PA1"] = float(max(1 - stats.norm.cdf((8 - d_) / se), stats.norm.cdf((-8 - d_) / se)))
        pred["PA1"]["TOST_p_normal_approx"] = pvals["PA1"]
        pred["PA1"]["bootstrap_se"] = se
    S["frozen_predictions_result"] = pred
    pvals = {k: v for k, v in pvals.items() if v is not None and not (isinstance(v, float) and np.isnan(v))}
    S["holm_adjusted_p"] = holm(pvals) if pvals else {}
    S["raw_p"] = pvals

    # ---------------------------------------------------------------- judge sensitivity + placebos
    sens = {}
    both = df[df.cls4_local.notna() & df.cls4_api.notna()]
    for g in LANGS:
        b = both[both.lang == g]
        if len(b) > 20:
            a1 = (b.cls4_local == "REFUSED").to_numpy()
            a2 = (b.cls4_api == "REFUSED").to_numpy()
            po = float((a1 == a2).mean())
            pe = float(a1.mean() * a2.mean() + (1 - a1.mean()) * (1 - a2.mean()))
            sens[f"kappa_{g}"] = float((po - pe) / (1 - pe)) if pe < 1 else float("nan")
            sens[f"n_{g}"] = int(len(b))
            sens[f"rate_local_{g}"] = float(a1.mean())
            sens[f"rate_api_{g}"] = float(a2.mean())
    edit = both[~both.cell.isin(["NOOP", "dev_A0"])]
    if len(edit) > 20:
        a1, a2 = (edit.cls4_local == "REFUSED").to_numpy(), (edit.cls4_api == "REFUSED").to_numpy()
        po = float((a1 == a2).mean())
        pe = float(a1.mean() * a2.mean() + (1 - a1.mean()) * (1 - a2.mean()))
        sens["kappa_within_edited"] = float((po - pe) / (1 - pe)) if pe < 1 else float("nan")
        sens["n_within_edited"] = int(len(edit))
    S["judge_sensitivity"] = sens
    S["rule_vs_judge"] = {"agreement": float((df.rule.eq("refused") == df[cls].eq("REFUSED"))[df[cls].notna()].mean())}
    jdump(S, Path(args.out))
    logger.info(f"analysis written to {args.out}: {S['n_cells']} cells, coverage {S['judged_coverage']}")
    for k, v in pred.items():
        logger.info(f"{k}: {json.dumps({kk: vv for kk, vv in v.items() if kk not in ('groups', 'rows')}, default=str)[:400]}")


if __name__ == "__main__":
    main()

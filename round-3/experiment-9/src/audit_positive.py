#!/usr/bin/env python3
"""PLACEBO AUDIT OF THE SURVIVING POSITIVE CLAIMS (stdlib + numpy only; imports nothing from this repo).

`rederive.py` re-derives every headline number and placebo-tests the two claims that FAILED (P1, P2). A placebo on a
null result is cheap, so this script does the harder half: it placebo-tests the three claims that SURVIVED, each of
which is therefore load-bearing for the write-up. Every one must collapse under the relevant permutation.

  A. P3 — Spearman(index-predicted residual, observed residual) = 0.78 in both languages.
     Placebo: permute the predictions across cells (equivalently, permute k_eff across cells). Must collapse to ~0.
  B. The index gap — index_EN = 16 < index_SL = 20 on the DEV prefix family.
     Placebo: permute the LANGUAGE label within each item across the two languages' generations of the same cell.
     The EN/SL index gap must vanish (the permuted gap distribution must straddle 0).
  C. Band identity — only coverage sets containing layers 13-24 ever drive SL below 0.5.
     Placebo: permute the "contains band 13-24" label across coverage sets. The observed separation in each set's
     minimum SL refusal must sit outside the permuted null.

Writes results/audit_positive.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
JUDGE = "Qwen/Qwen3-14B@40c06982 NF4 local (thinking disabled, greedy) | exp4 protocol rubric"
PREFIX_K = list(range(4, 49, 4))
BAND = set(range(13, 25))
RNG = np.random.default_rng(20260924)


def jl(p):
    return json.loads(Path(p).read_text())


def rows(p):
    out = []
    for line in Path(p).read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def key(prompt, response, hit_max):
    return hashlib.sha256(f"{JUDGE}|{prompt}|{response}|{int(bool(hit_max))}".encode()).hexdigest()


def rank(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else float("nan")


def load_per_item():
    """(cell, lang, role, semantic_id) -> refused 0/1, straight from the raw generations + raw judge cache."""
    lab = {r["key"]: r.get("cls") for r in rows(RES / "judge_local.jsonl") if not r.get("judge_fail")}
    out = {}
    for p in sorted((RES / "gens").glob("*.json")):
        for r in jl(p):
            c = lab.get(key(r["prompt"], r["response"], r["hit_max"]))
            if c is None or c == "judge_fail":
                continue
            out.setdefault((r["cell"], r["lang"], r["role"]), {})[r["semantic_id"]] = 1.0 if c == "refused" else 0.0
    return out


def rate(per, cell, lang, role="harmful"):
    d = per.get((cell, lang, role))
    return (sum(d.values()) / len(d)) if d else float("nan")


def index_from_curve(curve):
    for i, k in enumerate(PREFIX_K):
        if curve[i + 1] < 0.5:
            return k
    return 49


def keff_of(meta):
    if "c_profile" in meta:
        return sum(min(1.0, (a + b) / 2) for a, b in meta["c_profile"])
    return float(meta.get("n_layers", 0) or 0)


def main():
    per = load_per_item()
    cells = {p.stem: jl(p) for p in (RES / "cells").glob("*.json") if "__" not in p.stem}
    fp = jl(RES / "frozen_predictions.json")
    S = jl(RES / "analysis_summary.json")
    out = {}

    # ---------------------------------------------------------------- A. P3 Spearman
    A = {}
    for lang in ("en", "sl"):
        curve = fp["P3"]["prefix_curves"][lang]
        ks = [0] + PREFIX_K
        pred, obs, names = [], [], []
        for c, m in cells.items():
            if m.get("family") != "weight" or c.startswith(("SMK", "S5X", "CF_")):
                continue
            o = rate(per, c, lang)
            if o != o:
                continue
            pred.append(float(np.interp(keff_of(m), ks, curve)))
            obs.append(o)
            names.append(c)
        rho = spearman(pred, obs)
        null = []
        for _ in range(2000):
            pp = list(pred)
            random.Random(len(null)).shuffle(pp)
            null.append(spearman(pp, obs))
        null.sort()
        A[lang] = {"n_cells": len(obs), "observed_spearman": rho,
                   "reported_in_analysis": S["P3_screen"][lang]["spearman"],
                   "matches_reported": abs(rho - S["P3_screen"][lang]["spearman"]) < 1e-9,
                   "placebo_null_ci95": [null[50], null[1949]], "placebo_mean": float(np.mean(null)),
                   "observed_outside_null": bool(rho > null[1949] or rho < null[50]),
                   "placebo_collapses_to_zero": bool(abs(np.mean(null)) < 0.10)}
    out["A_P3_spearman_placebo"] = A

    # ---------------------------------------------------------------- B. the index gap under language permutation
    ids = sorted(set(per[("PA_noop", "en", "harmful")]) & set(per[("PA_noop", "sl", "harmful")]))
    curves = {}
    for lang in ("en", "sl"):
        curves[lang] = [[per[("PA_noop", lang, "harmful")][i] for i in ids]]
        for k in PREFIX_K:
            d = per.get((f"PA_prefix_{k:02d}", lang, "harmful"), {})
            curves[lang].append([d.get(i, float("nan")) for i in ids])
    obs_idx = {lang: index_from_curve([float(np.nanmean(r)) for r in curves[lang]]) for lang in ("en", "sl")}
    obs_gap = obs_idx["sl"] - obs_idx["en"]
    null_gaps = []
    for t in range(1000):
        rg = random.Random(1000 + t)
        swap = [rg.random() < 0.5 for _ in ids]
        cu = {"en": [], "sl": []}
        for r_en, r_sl in zip(curves["en"], curves["sl"]):
            a = [(r_sl[j] if swap[j] else r_en[j]) for j in range(len(ids))]
            b = [(r_en[j] if swap[j] else r_sl[j]) for j in range(len(ids))]
            cu["en"].append(a)
            cu["sl"].append(b)
        gi = {lg: index_from_curve([float(np.nanmean(r)) for r in cu[lg]]) for lg in ("en", "sl")}
        null_gaps.append(gi["sl"] - gi["en"])
    null_gaps.sort()
    out["B_index_gap_language_placebo"] = {
        "n_items": len(ids), "index_en": obs_idx["en"], "index_sl": obs_idx["sl"], "observed_gap": obs_gap,
        "matches_frozen": bool(obs_idx["en"] == jl(RES / "redundancy_index.json")["index"]["en"]["prefix"]["index"]
                               and obs_idx["sl"] == jl(RES / "redundancy_index.json")["index"]["sl"]["prefix"]["index"]),
        "placebo_null_ci95": [null_gaps[25], null_gaps[974]], "placebo_mean_gap": float(np.mean(null_gaps)),
        "placebo_straddles_zero": bool(null_gaps[25] <= 0 <= null_gaps[974]),
        "observed_gap_outside_null": bool(obs_gap > null_gaps[974] or obs_gap < null_gaps[25]),
        "note": ("the gap is a difference of two step functions on a grid of 4, so its null is coarse; the honest read "
                 "is whether the observed gap sits outside the permuted null, not a p-value")}

    # -------------------------------------------------- B2. the CURVE separation (a powered statistic for the same claim)
    # The index is a step function on a grid of 4, so its smallest non-zero gap IS 4 and its permutation null is coarse.
    # The mean vertical gap between the two prefix curves uses all 13 grid points and every item, so it can actually be
    # tested. Same language-permutation placebo.
    def auc_gap(cu):
        return float(np.mean([np.nanmean(rs) - np.nanmean(re_) for re_, rs in zip(cu["en"], cu["sl"])]))
    obs_auc = auc_gap(curves)
    null_auc = []
    for t in range(2000):
        rg = random.Random(50000 + t)
        swap = [rg.random() < 0.5 for _ in ids]
        cu = {"en": [], "sl": []}
        for r_en, r_sl in zip(curves["en"], curves["sl"]):
            cu["en"].append([(r_sl[j] if swap[j] else r_en[j]) for j in range(len(ids))])
            cu["sl"].append([(r_en[j] if swap[j] else r_sl[j]) for j in range(len(ids))])
        null_auc.append(auc_gap(cu))
    null_auc.sort()
    # item-cluster bootstrap CI on the same statistic
    boot = []
    for t in range(2000):
        rg = np.random.default_rng(70000 + t)
        ix = rg.integers(0, len(ids), len(ids))
        cu = {lg: [[r[j] for j in ix] for r in curves[lg]] for lg in ("en", "sl")}
        boot.append(auc_gap(cu))
    boot.sort()
    out["B2_curve_separation"] = {
        "statistic": "mean over the 13 prefix grid points of (SL refusal - EN refusal), DEV half A, paired items",
        "observed": obs_auc, "bootstrap_ci95": [boot[50], boot[1949]],
        "placebo_null_ci95": [null_auc[50], null_auc[1949]], "placebo_mean": float(np.mean(null_auc)),
        "observed_outside_null": bool(obs_auc > null_auc[1949] or obs_auc < null_auc[50]),
        "permutation_p_two_sided": float(sum(1 for x in null_auc if abs(x) >= abs(obs_auc)) / len(null_auc)),
        "reading": ("this is the statistic that actually supports 'Slovene needs more coverage than English'; the "
                    "INDEX gap of 4 is one grid step and is NOT separable from its own permutation null")}

    # ---------------------------------------------------------------- C. band identity
    by_cov = {}
    for c, m in cells.items():
        cov = m.get("coverage")
        if m.get("family") != "weight" or not cov or c.startswith(("SMK", "S5X", "CF_")):
            continue
        r = rate(per, c, "sl")
        if r == r:
            by_cov.setdefault(cov, []).append(r)
    cov_layers = {"B1": set(range(1, 13)), "B2": set(range(13, 25)), "B3": set(range(25, 37)), "B4": set(range(37, 49)),
                  "C24": set(range(1, 25)), "C36": set(range(1, 37)), "ALL48": set(range(1, 49)),
                  "S2": set(range(1, 49, 2)), "S4": set(range(1, 49, 4)), "K96": set(range(12, 49))}
    minsl = {cov: min(v) for cov, v in by_cov.items()}
    # Band DENSITY, not mere intersection: S2 covers 6/12 of layers 13-24 and does NOT reach SL < 0.5, so the binary
    # "contains the band" rule is wrong. "Dense" = covers the band in full (12/12).
    frac = {cov: len(cov_layers[cov] & BAND) / len(BAND) for cov in minsl}
    hit = {cov: frac[cov] >= 0.999 for cov in minsl}
    a = [minsl[c] for c in minsl if hit[c]]
    b = [minsl[c] for c in minsl if not hit[c]]
    obs_sep = float(np.mean(b) - np.mean(a))
    labels = [hit[c] for c in minsl]
    vals = [minsl[c] for c in minsl]
    null = []
    for t in range(5000):
        lg = list(labels)
        random.Random(t).shuffle(lg)
        aa = [v for v, h in zip(vals, lg) if h]
        bb = [v for v, h in zip(vals, lg) if not h]
        if aa and bb:
            null.append(np.mean(bb) - np.mean(aa))
    null.sort()
    out["C_band_identity_placebo"] = {
        "min_SL_by_coverage_set": minsl, "fraction_of_band_13_24_covered": frac,
        "covers_band_in_full": hit,
        "min_SL_by_band_density": sorted([(round(frac[c], 3), c, round(minsl[c], 3)) for c in minsl], reverse=True),
        "spearman_band_density_vs_min_SL": spearman([frac[c] for c in minsl], [minsl[c] for c in minsl]),
        "sets_reaching_band": sorted(c for c in minsl if hit[c]), "sets_not_reaching": sorted(c for c in minsl if not hit[c]),
        "mean_min_SL_reaching": float(np.mean(a)), "mean_min_SL_not_reaching": float(np.mean(b)),
        "observed_separation": obs_sep,
        "placebo_null_ci95": [float(null[int(0.025 * len(null))]), float(null[int(0.975 * len(null))])],
        "placebo_mean": float(np.mean(null)),
        "observed_outside_null": bool(obs_sep > null[int(0.975 * len(null))]),
        "permutation_p": float(sum(1 for x in null if x >= obs_sep) / len(null)),
        "every_reaching_set_below_0.5": bool(all(x < 0.5 for x in a)),
        "every_non_reaching_set_above_0.5": bool(all(x >= 0.5 for x in b))}

    Path(RES / "audit_positive.json").write_text(json.dumps(out, indent=1, default=float))
    print("A. P3 Spearman placebo")
    for lg, v in out["A_P3_spearman_placebo"].items():
        print(f"   {lg}: observed {v['observed_spearman']:.3f} (matches analysis: {v['matches_reported']}), "
              f"placebo null {[round(x,3) for x in v['placebo_null_ci95']]} mean {v['placebo_mean']:+.3f}, "
              f"outside null: {v['observed_outside_null']}")
    b_ = out["B_index_gap_language_placebo"]
    print(f"B. index gap: EN {b_['index_en']} SL {b_['index_sl']} gap {b_['observed_gap']} (matches frozen: {b_['matches_frozen']}); "
          f"language-permuted null {b_['placebo_null_ci95']} mean {b_['placebo_mean_gap']:+.2f}, straddles 0: {b_['placebo_straddles_zero']}, "
          f"observed outside: {b_['observed_gap_outside_null']}")
    c_ = out["C_band_identity_placebo"]
    print(f"C. band identity: reaching {c_['sets_reaching_band']} mean min SL {c_['mean_min_SL_reaching']:.3f}; "
          f"not reaching {c_['sets_not_reaching']} mean min SL {c_['mean_min_SL_not_reaching']:.3f}; "
          f"separation {c_['observed_separation']:.3f}, permuted null {[round(x,3) for x in c_['placebo_null_ci95']]}, "
          f"p = {c_['permutation_p']:.4f}, all-reaching-below-0.5 {c_['every_reaching_set_below_0.5']}, "
          f"all-others-above {c_['every_non_reaching_set_above_0.5']}")


if __name__ == "__main__":
    main()

"""S10 placebos / positive controls P1-P6 -> results/placebos.json"""
from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd

from lib import E4, RES, SEED, cluster_boot_mean, cohen_kappa, kappa_codes, read_json, setup, within, write_json


def all_records() -> list[dict]:
    out = []
    for f in sorted((RES / "records").glob("*.json")):
        out += read_json(f)
    return out


def recheck(r: dict, value) -> bool:
    """re-run the draft comparator on a (perturbed) recomputed value; True = still a match."""
    d = r["draft_value"]
    tol = 0.0055 if r["step"] == "s2i_claims" else None
    if r["id"].startswith("iter1_") and isinstance(d, int):
        return value == d
    if tol is None:
        tol = 0.0015
    return abs(value - d) <= tol + 1e-12


def main():
    setup("s07_placebos")
    recs = all_records()
    P = {}
    # P1 comparator sensitivity: perturb 5 matched values by +0.01
    pool = [r for r in recs if r["status"] == "RECOMPUTED_MATCH" and isinstance(r["recomputed_value"], (int, float)) and isinstance(r["draft_value"], (int, float))]
    rng = np.random.default_rng(SEED)
    pick = [pool[i] for i in rng.choice(len(pool), 5, replace=False)]
    flagged = [not recheck(r, r["recomputed_value"] + 0.01) for r in pick]
    unperturbed_ok = [recheck(r, r["recomputed_value"]) for r in pick]
    P["P1_comparator_sensitivity"] = dict(ids=[r["id"] for r in pick], flagged_after_plus_0p01=flagged, unperturbed_still_match=unperturbed_ok,
                                          passed=bool(all(flagged) and all(unperturbed_ok)))
    # P2 known-mismatch recall
    st = {r["id"]: r["status"] for r in recs}
    known = {"iter1_gemma_orig_sl": "RECOMPUTED_MISMATCH", "iter1_gemma_own_sl": "RECOMPUTED_MISMATCH", "iter1_gemma_swap_en": "RECOMPUTED_MISMATCH",
             "iter1_gemma_swap_sl": "RECOMPUTED_MISMATCH", "iter1_eff_ratio_of_medians": "MISDESCRIBED", "exp7_Pa_definition": "RECOMPUTED_MISMATCH",
             "iter1_a3_reading": "RECOMPUTED_MISMATCH"}
    got = {k: st.get(k) for k in known}
    P["P2_known_mismatch_recall"] = dict(expected=known, got=got, recall=sum(got[k] == v for k, v in known.items()) / len(known),
                                         passed=all(got[k] == v for k, v in known.items()))
    # P3 known-match: GaMS3 iter-1 rows + the 10 exp4 S5 refusal cells
    ids = [r["id"] for r in recs if r["id"].startswith("iter1_gams_") and r["id"].split("_")[2] in ("orig", "own", "swap")]
    ids += [f"claim_exp4_{ck}_S5_{lg}" for ck in ("gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref") for lg in ("en", "sl")]
    got3 = {i: st.get(i) for i in ids}
    P["P3_known_match"] = dict(n=len(ids), n_match=sum(v == "RECOMPUTED_MATCH" for v in got3.values()), non_match={k: v for k, v in got3.items() if v != "RECOMPUTED_MATCH"},
                               passed=all(v == "RECOMPUTED_MATCH" for v in got3.values()))
    # P4 within-cell label shuffle (gpt-4.1 vs Qwen on edited cells, exp4 and exp8)
    L = pd.read_parquet(RES / "labels_long.parquet")
    p4 = {}
    for art in ("exp4", "exp8"):
        W = L[(L.artifact == art) & (~L.is_orig) & L.judge.isin(["gpt41", "qwen3_14b"])].dropna(subset=["label"]).pivot_table(
            index=["cell", "item"], columns="judge", values="label", aggfunc="first").dropna().reset_index()
        a = np.where(W.gpt41 == "REFUSED", 1, 0)
        b = np.where(W.qwen3_14b == "REFUSED", 1, 0)
        cells = W.cell.values
        obs = cohen_kappa(a, b)
        percell, pooled = [], []
        groups = [np.where(cells == c)[0] for c in np.unique(cells)]
        for _ in range(1000):
            bb = b.copy()
            for g in groups:
                bb[g] = rng.permutation(bb[g])
            pooled.append(cohen_kappa(a, bb))
            ks = [cohen_kappa(a[g], bb[g]) for g in groups if len(g) >= 20]
            ks = [k for k in ks if np.isfinite(k)]
            percell.append(np.mean(ks) if ks else np.nan)
        percell = np.array(percell)
        pooled = np.array(pooled)
        p4[art] = dict(n=len(W), n_cells=len(groups), observed_pooled_edited_kappa=obs,
                       shuffled_mean_within_cell_kappa=float(np.nanmean(percell)),
                       shuffled_within_cell_kappa_ci=[float(np.nanquantile(percell, .025)), float(np.nanquantile(percell, .975))],
                       shuffled_pooled_kappa_mean=float(pooled.mean()),
                       shuffled_pooled_kappa_ci=[float(np.quantile(pooled, .025)), float(np.quantile(pooled, .975))],
                       note=("within-cell shuffles destroy item-level agreement; the POOLED kappa that survives the shuffle is agreement produced "
                             "only by between-cell prevalence contrasts (the inflation mechanism)"))
    P["P4_within_cell_shuffle"] = dict(results=p4, passed=all(abs(v["shuffled_mean_within_cell_kappa"]) < 0.05 and v["shuffled_within_cell_kappa_ci"][0] <= 0 <= v["shuffled_within_cell_kappa_ci"][1]
                                                              for v in p4.values()))
    # P5 language-label permutation on S5X pairs (gemma_edit, Qwen, strict)
    fr = read_json(E4 / "frozen_samples.json")
    X = L[(L.artifact == "exp4") & (L.cell == "gemma_edit") & (L.judge == "qwen3_14b")].set_index("item").label
    en = np.array([X.get(p["en_item"]) == "REFUSED" for p in fr["s5x_pairs"]], float)
    sl = np.array([X.get(p["sl_item"]) == "REFUSED" for p in fr["s5x_pairs"]], float)
    gaps = []
    for _ in range(1000):
        sw = rng.random(len(en)) < 0.5
        e2, s2 = np.where(sw, sl, en), np.where(sw, en, sl)
        gaps.append(s2.mean() - e2.mean())
    gaps = np.array(gaps)
    P["P5_language_permutation_s5x"] = dict(observed_gap=float(sl.mean() - en.mean()), permuted_mean=float(gaps.mean()),
                                            permuted_ci=[float(np.quantile(gaps, .025)), float(np.quantile(gaps, .975))],
                                            share_ge_observed=float((gaps >= sl.mean() - en.mean()).mean()),
                                            passed=bool(abs(gaps.mean()) < 0.10 and np.quantile(gaps, .025) <= 0 <= np.quantile(gaps, .975)))
    # P6 keyword reimplementation
    k = read_json(RES / "p6_keyword_check.json")
    P["P6_keyword_reimplementation"] = dict(**k, also="iter-1 exp1 EN keyword flags reproduced exactly on all 600 responses (assert in s02)",
                                            passed=k["n"] == k["n_match"])
    P["n_passed"] = sum(v["passed"] for kk, v in P.items() if kk.startswith("P"))
    write_json(RES / "placebos.json", P)
    print(json.dumps({k: (v["passed"] if isinstance(v, dict) else v) for k, v in P.items()}))


if __name__ == "__main__":
    main()

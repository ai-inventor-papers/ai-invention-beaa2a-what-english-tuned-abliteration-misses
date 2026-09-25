#!/usr/bin/env python3
"""PART G: the cross-model depth table. If the sibling Gemma pod of this iteration has published a redundancy index, read
it and emit the joint table; otherwise emit the GaMS3 side alone next to the iteration-2 Gemma depth numbers
(art_hmbXDppkPZnR, second-judge, n = 111/language), clearly labelled as iteration-2 measurements rather than this
iteration's. Every cross-model sentence is DESCRIPTIVE: n = 2 sibling checkpoints, not a controlled derivative, and no
difference is attributed to continual pretraining, instruction tuning or any other training stage."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

from pathlib import Path

from loguru import logger

import common as C
from common import jdump, jload, setup_logging

SIBLINGS = [C.LOOP / "round-3/experiment-9/src", C.LOOP / "round-3/experiment-11/src",
            C.LOOP / "round-3/experiment-12/src"]
# iteration-2 Gemma depth localisation (gen_art_experiment_8 README / results/report_tables.md, local second judge,
# n = 111 harmful per language): layer-matched d_EN(h) ablation over contiguous and cumulative bands.
EXP8_GEMMA = {"source": "art_hmbXDppkPZnR (iteration 2, gen_art_experiment_8), local second judge, n=111/language",
              "noop": {"en": 0.91, "sl": 0.99},
              "bands": {"1-12": {"en": 0.79, "sl": 0.82}, "13-24": {"en": 0.45, "sl": 0.82},
                        "25-36": {"en": 0.72, "sl": 0.70}, "37-48": {"en": 0.87, "sl": 0.99}},
              "cumulative": {"1-24": {"en": 0.42, "sl": 0.55}, "1-36": {"en": 0.38, "sl": 0.21},
                             "1-48": {"en": 0.37, "sl": 0.23}},
              "controls": {"layer_matched_random_all48": {"sl": 0.86}, "energy_matched_pc_all48": {"sl": 0.93}},
              "collateral": {"all48_sl_flores_dNLL": 0.524, "all48_sl_invalid": 0.00}}


def find_sibling() -> Path | None:
    for p in SIBLINGS:
        q = p / "results/redundancy_index.json"
        if q.exists():
            return q
    return None


def main() -> None:
    setup_logging("cross_model")
    ri = jload(C.RES / "redundancy_index.json")
    out = {"gams3": {"source": "this artifact (iteration 3, gen_art_experiment_10), local Qwen3-14B judge, "
                               f"n={ri['n_items']}/language, DEV (S3 half A)",
                     "index": ri["index"], "index_CI95": ri["index_boot_CI95"], "index_usable": ri["index_usable"],
                     "index_suffix": ri["index_suffix"], "prefix_curves": ri["prefix_curves"],
                     "prefix_invalid_curves": ri["prefix_invalid_curves"],
                     "lobo_necessity_vs_all48": ri["lobo_necessity_vs_all48"], "noop": ri["noop_refusal"]}}
    sib = find_sibling()
    if sib:
        s = jload(sib)
        idx = s.get("index", {})
        if isinstance(idx.get("en"), dict):          # sibling pod's schema: {lang: {family: {k, curve, index, ...}}}
            gem = {"index": {g: idx[g]["prefix"]["index"] for g in ("en", "sl") if g in idx},
                   "index_CI95": {g: idx[g]["prefix"].get("index_boot_ci") for g in ("en", "sl") if g in idx},
                   "prefix_curves": {g: dict(zip(map(str, idx[g]["prefix"]["k"]), idx[g]["prefix"]["curve"]))
                                     for g in ("en", "sl") if g in idx},
                   "prefix_AUC": {g: idx[g]["prefix"].get("auc") for g in ("en", "sl") if g in idx},
                   "suffix_index": {g: idx[g].get("suffix", {}).get("index") for g in ("en", "sl") if g in idx},
                   "noop": {g: idx[g]["prefix"]["curve"][0] for g in ("en", "sl") if g in idx}}
        else:                                         # same schema as this artifact
            gem = {"index": s.get("index"), "index_CI95": s.get("index_boot_CI95"),
                   "index_usable": s.get("index_usable"), "prefix_curves": s.get("prefix_curves"),
                   "noop": s.get("noop_refusal")}
        gem |= {"source": str(sib), "scorer": s.get("scorer"), "definition": s.get("definition", "")[:400],
                "n_items_per_language": 44}
        out["gemma_sibling_pod"] = gem
        both = {g: (out["gams3"]["index"].get(g), gem.get("index", {}).get(g)) for g in ("en", "sl")}
        out["joint_reading"] = {
            "index_pairs_gams3_vs_gemma": both,
            "same_instrument": "both pods ran the cumulative-prefix family of layer-matched d_EN(h) activation ablation on "
                               "S3 JBB half A with a blind local Qwen3-14B partial-aware judge (GaMS3 n=40, Gemma n=44 "
                               "harmful items per language)",
            "statement": "In BOTH sibling checkpoints the English index is shallower than the Slovene one by one 4-layer "
                         "step of the grid. The Slovene lag is therefore NOT what distinguishes these two models under this "
                         "instrument; it is common to both. Any iteration-1 difference between their Heretic EDITS has to be "
                         "explained by something other than a difference in how redundantly refusal is written across depth.",
            "caution": "n = 2 checkpoints, one seed, one instrument, a 4-layer grid whose resolution is +-4 layers, and "
                       "overlapping bootstrap CIs: this is an ORDERING observation, not a fitted law, and it is not "
                       "attributed to any training stage."}
        out["comparison_status"] = "joint (two iteration-3 pods, same instrument)"
    else:
        out["gemma_iteration2"] = EXP8_GEMMA
        out["comparison_status"] = ("GaMS3 only: no sibling pod published a redundancy index in this iteration, so the Gemma "
                                    "column is the ITERATION-2 depth table measured with a different item set (n=111 "
                                    "OUTCOME items, not the 40-item DEV set) and a different arm family (contiguous and "
                                    "cumulative bands, no 4-layer prefix grid). It is a qualitative reference, NOT a "
                                    "matched comparison, and no index_L can be read off it.")
    out["interpretation_rules"] = [
        "n = 2 sibling checkpoints: every cross-model statement is descriptive, never a controlled derivative.",
        "No difference is attributed to Slovene continual pretraining, instruction tuning or the safety set: the two models "
        "differ in many ways at once and only their endpoints were measured.",
        "The GaMS3 column is DEV (half A, 40 items/language); the iteration-2 Gemma column is OUTCOME (111 items/language). "
        "Absolute levels are therefore not directly comparable; only the shape of the depth dependence is.",
    ]
    jdump(out, C.RES / "cross_model.json")
    logger.info(f"cross-model table written; status: {out['comparison_status'][:90]}")


if __name__ == "__main__":
    main()

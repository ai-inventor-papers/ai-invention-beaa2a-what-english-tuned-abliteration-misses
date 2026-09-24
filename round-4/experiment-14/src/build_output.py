#!/usr/bin/env python3
"""method_out.json in the exp_gen_sol_out schema, laid out as the comparison this pod makes.

One example per (split, semantic item, language). `output` is the UNEDITED model's frozen 4-way class on that item,
and there is one `predict_<method>` per condition that actually ran on it: the single-layer causal write probes that
build the profile, the matched-energy confirmation cells, the layer-matched random and energy-matched PC controls, the
A1-A4 placement/dose ladder and the re-labelled iteration-3 anchors. Every value is the 4-way label of a generation
that exists on disk under results/cells/<cell>/gens.json; its text is kept beside it in metadata_response_<method>."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import re

import pandas as pd
from loguru import logger

import alib as A
import common as C
from common import jdump, jload, setup_logging

SPLIT_DS = {"dev": "S3_jbb_halfA_DEV_harmful", "dev_ben": "S3_jbb_halfA_DEV_harmless",
            "screen": "S3_jbb_halfB_SCREEN_harmful", "confirm": "S4_strongreject_hoc_CONFIRM_harmful",
            "confirm_ben": "S4_strongreject_hoc_CONFIRM_harmless"}
BANDS = {1: "1_12", 2: "13_24", 3: "25_36", 4: "37_48"}


def method_name(cell: str) -> str:
    if cell in ("dev_NOOP", "R_NOOP"):
        return "baseline_noop"
    m = re.fullmatch(r"dev_L(\d+)_c([\d.]+)", cell)
    if m:
        return f"write_probe_single_layer_h{int(m.group(1))}_c{m.group(2).replace('.', 'p')}"
    m = re.fullmatch(r"dev_W(\d+)L(\d+)_c([\d.]+)", cell)
    if m:
        return f"write_probe_window{m.group(1)}_h{int(m.group(2))}_c{m.group(3).replace('.', 'p')}"
    m = re.fullmatch(r"C_B(\d)_(E\d)", cell)
    if m:
        return f"band_{BANDS[int(m.group(1))]}_matched_energy_{m.group(2)}"
    m = re.fullmatch(r"C_STR4p(\d)_(E\d)", cell)
    if m:
        return f"stride4_phase{m.group(1)}_matched_energy_{m.group(2)}"
    m = re.fullmatch(r"C_HYB_(\w+)_(E\d)", cell)
    if m:
        return f"hybrid_{m.group(1)}_matched_energy_{m.group(2)}"
    m = re.fullmatch(r"X_RND(\d)_E3", cell)
    if m:
        return f"control_layer_matched_random_draw{m.group(1)}"
    m = re.fullmatch(r"X_PC(\d)_E3", cell)
    if m:
        return f"control_energy_matched_pc_draw{m.group(1)}"
    return {"A1_ship": "shipped_heretic_edit_trial88", "A2_swap": "sibling_kernel_as_is",
            "A3_swap_up": "sibling_kernel_energy_matched_to_shipped",
            "A4_ship_down": "shipped_edit_energy_matched_to_sibling",
            "R_G1_single_site": "single_site_activation_probe_h34", "R_HER88_c1": "anchor_trial88_kernel_c1",
            "R_ALL_c1": "anchor_all48_c1", "R_STR2_c1": "anchor_stride2_c1", "R_STR4_c1": "anchor_stride4_c1",
            "R_B1_c1": "anchor_band_1_12_c1", "R_B2_c1": "anchor_band_13_24_c1", "R_B3_c1": "anchor_band_25_36_c1",
            "R_B4_c1": "anchor_band_37_48_c1"}.get(cell, "cell_" + re.sub(r"[^A-Za-z0-9_]", "_", cell))


def main() -> None:
    setup_logging("build_output")
    cells = A.load_cells()
    base = {}
    for split, b in (("dev", "dev_NOOP"), ("dev_ben", "dev_NOOP"), ("screen", "R_NOOP"), ("confirm", "R_NOOP"),
                     ("confirm_ben", "R_NOOP")):
        for r in cells.get(b, {}).get("rows", []):
            if r["split"] == split:
                base[(split, r["semantic_id"], r["lang"])] = r
    ex: dict = {}
    per_item = []
    for cell, d in sorted(cells.items()):
        mname = method_name(cell)
        meta = d["meta"]
        for r in d["rows"]:
            k = (r["split"], r["semantic_id"], r["lang"])
            b = base.get(k)
            if b is None:
                continue
            e = ex.get(k)
            if e is None:
                e = ex[k] = {"input": r["prompt"], "output": b["cls4"] or "UNJUDGED",
                             "metadata_split": r["split"], "metadata_dataset": SPLIT_DS.get(r["split"], r["split"]),
                             "metadata_semantic_id": r["semantic_id"], "metadata_lang": r["lang"],
                             "metadata_role": r.get("role"), "metadata_kind": r["kind"],
                             "metadata_model": "cjvt/GaMS3-12B-Instruct@1d0b27af (bnb NF4)",
                             "metadata_judge": "local Qwen3-14B, frozen iteration-2 rubric, blind to condition",
                             "metadata_baseline_response": b["response"]}
            e[f"predict_{mname}"] = r["cls4"] or "UNJUDGED"
            e[f"metadata_response_{mname}"] = r["response"]
            e[f"metadata_rulelabel_{mname}"] = r["rule_label"]
            e[f"metadata_replylang_{mname}"] = r["reply_lang"]
            per_item.append({"cell": cell, "method": mname, "split": r["split"], "semantic_id": r["semantic_id"],
                             "lang": r["lang"], "cls4": r["cls4"], "rule_label": r["rule_label"],
                             "reply_lang": r["reply_lang"], "rep4": r["rep4"], "n_tokens": r["n_tokens"],
                             "E": meta.get("E_exact"), "c": meta.get("c"), "level": meta.get("level")})
    ds: dict = {}
    for (split, sid, lang), e in ex.items():
        ds.setdefault(SPLIT_DS.get(split, split), []).append(e)
    out = {"metadata": {"method_name": "causal write-profile overlap (O) for refusal edits in GaMS3-12B-Instruct",
                        "description": "Per-language causal write profile e_L(h) measured with single-layer Heretic-"
                                       "operator edits on DEV items, frozen into the overlap statistic "
                                       "O = sum_h e_L(h) g(h)/||g||_2, then raced out of sample against log energy, "
                                       "layer count, depth span, the EN/SL direction-cosine overlap and the cheap "
                                       "one-forward-pass baselines on held-out harm categories.",
                        "baseline_condition": "the unedited checkpoint under the identical decoding and batching "
                                              "schedule (`output`)",
                        "outcome": "frozen 4-way class REFUSED / PARTIAL / COMPLIED / INVALID",
                        "frozen_predictions": "configs/frozen_predictions.json (hashed in configs/FREEZE.sha256)"},
           "datasets": [{"dataset": k, "examples": sorted(v, key=lambda e: (e["metadata_semantic_id"],
                                                                            e["metadata_lang"]))}
                        for k, v in sorted(ds.items())]}
    jdump(out, C.ROOT / "method_out.json", indent=1)
    pd.DataFrame(per_item).to_parquet(C.RES / "per_item.parquet", index=False)
    n = sum(len(d["examples"]) for d in out["datasets"])
    logger.info(f"method_out.json: {len(out['datasets'])} datasets, {n} examples, "
                f"{len(per_item)} per-item rows -> results/per_item.parquet")


if __name__ == "__main__":
    main()

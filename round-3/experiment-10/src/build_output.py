#!/usr/bin/env python3
"""method_out.json in the exp_gen_sol_out schema, laid out as the COMPARISON the paper makes.

One example per (split, semantic item, language). `output` is what the UNEDITED model did on that item (the baseline
condition, as a 4-way class), and there is one `predict_<method>` per intervention that was actually run on that item:
our concentrated band edits, the matched-total-removal-energy spread edits, the layer-matched random and energy-matched
PC controls, the depth-coverage activation arms, and the shipped iteration-1 Heretic edit. Every value is the frozen
4-way label (REFUSED / PARTIAL / COMPLIED / INVALID) of a generation that exists on disk under
results/cells/<cell>/gens.json; the generating text of each method is kept beside it in metadata_response_<method>.
Nothing here is estimated, copied or padded."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import re

import pandas as pd
from loguru import logger

import common as C
from common import jdump, jload, setup_logging

SPLIT_DS = {"dev": "S3_jbb_halfA_DEV_harmful", "dev_ben": "S3_jbb_halfA_DEV_harmless",
            "screen": "S3_jbb_halfB_SCREEN_harmful", "confirm": "S4_strongreject_hoc_CONFIRM_harmful",
            "confirm_ben": "S4_strongreject_hoc_CONFIRM_harmless"}
BASELINE = {"dev": "dev_A0", "dev_ben": "dev_A0", "screen": "NOOP", "confirm": "NOOP", "confirm_ben": "NOOP"}


def method_name(cell: str) -> str:
    """Readable slug for a cell; the name says what the intervention IS, not which file it came from."""
    if cell in ("NOOP", "dev_A0"):
        return "baseline_noop"
    m = re.fullmatch(r"dev_P(\d+)", cell)
    if m:
        return f"prefix_depth_first_{m.group(1)}_layers"
    m = re.fullmatch(r"dev_S(\d+)", cell)
    if m:
        return f"suffix_depth_last_{m.group(1)}_layers"
    m = re.fullmatch(r"dev_LOBO_(\d+)_(\d+)", cell)
    if m:
        return f"all48_except_band_{m.group(1)}_{m.group(2)}"
    if cell == "dev_X3_rand_all":
        return "control_random_all_layers_activation"
    if cell == "dev_X5_pc_all":
        return "control_pc_all_layers_activation"
    m = re.fullmatch(r"(E\d)_(B2|B3|STR2|STR4|ALL|RND_ALL|PC_ALL)", cell)
    if m:
        grp, mem = m.groups()
        base = {"B2": "band_13_24", "B3": "band_25_36", "STR2": "spread_stride2", "STR4": "spread_stride4",
                "ALL": "spread_all48", "RND_ALL": "control_random_all48", "PC_ALL": "control_pc_all48"}[mem]
        return f"{base}_matchedE_{grp}"
    m = re.fullmatch(r"GRID_(.+)_c1\.0", cell)
    if m:
        return f"grid_{m.group(1).lower()}_c1"
    return {"CORE_trial88": "core_heretic_edit_trial88", "G1_single_site": "single_site_direction_ablation",
            "SWAP_in_trial96": "swap_in_gemma_trial96_kernel"}.get(cell, cell.lower())


def main() -> None:
    setup_logging("build_output")
    S = jload(C.RES / "analysis_summary.json")
    df = pd.read_parquet(C.RES / "per_item.parquet")
    meta_cells = {d.name: jload(d / "meta.json") for d in sorted(C.CELLS.iterdir()) if (d / "meta.json").exists()}
    texts: dict = {}
    for d in sorted(C.CELLS.iterdir()):
        if (d / "gens.json").exists():
            for r in jload(d / "gens.json"):
                texts[(r["cell"], r["split"], r["uid"], r["lang"])] = (r["prompt"], r["response"])

    datasets, method_index = {}, {}
    for split, dname in SPLIT_DS.items():
        d = df[df.split == split]
        if d.empty:
            continue
        base_cell = BASELINE[split]
        cells = sorted(d.cell.unique())
        names = {c: method_name(c) for c in cells}
        assert len(set(names.values())) == len(names), f"method slug collision in {split}"
        method_index[dname] = {names[c]: {"cell": c, "type": meta_cells.get(c, {}).get("type"),
                                          "energy": meta_cells.get(c, {}).get("E_exact"),
                                          "n_layers_edited": len(meta_cells.get(c, {}).get("layers", []) or []),
                                          "per_layer_strength": meta_cells.get(c, {}).get("c"),
                                          "is_baseline": c == base_cell,
                                          "is_control": "control" in names[c]} for c in cells}
        rows = []
        for (uid, lang), g in d.groupby(["uid", "lang"]):
            by_cell = {r.cell: r for r in g.itertuples()}
            if base_cell not in by_cell:
                continue
            b = by_cell[base_cell]
            prompt = texts[(base_cell, split, uid, lang)][0]
            ex = {"input": prompt, "output": b.cls4_local,
                  "metadata_baseline_condition": "unedited cjvt/GaMS3-12B-Instruct, greedy, NF4",
                  "metadata_output_meaning": "frozen 4-way class of the UNEDITED model's reply (REFUSED / PARTIAL / "
                                             "COMPLIED / INVALID); PARTIAL counts as compliance in refusal-removal metrics",
                  "metadata_split": split, "metadata_uid": uid, "metadata_semantic_id": b.semantic_id,
                  "metadata_lang": lang, "metadata_role": b.role, "metadata_kind": b.kind,
                  "metadata_judge": "local:Qwen/Qwen3-14B@40c06982 (blind, frozen rubric)"}
            n_pred = 0
            for c in cells:
                if c not in by_cell:
                    continue
                r = by_cell[c]
                nm = names[c]
                if r.cls4_local is not None:
                    ex[f"predict_{nm}"] = str(r.cls4_local)
                    n_pred += 1
                ex[f"metadata_response_{nm}"] = texts[(c, split, uid, lang)][1]
                if r.cls4_api is not None:
                    ex[f"metadata_gpt41_label_{nm}"] = str(r.cls4_api)
                ex[f"metadata_rulelabel_{nm}"] = str(r.rule)
                ex[f"metadata_replylang_{nm}"] = str(r.reply_lang)
            if n_pred >= 2:
                rows.append(ex)
        datasets[dname] = rows
        logger.info(f"{dname}: {len(rows)} items x {len(cells)} methods")

    n_methods = len({m for v in method_index.values() for m in v})
    out = {"metadata": {
        "method_name": "depth-coverage x strength factorial of Heretic's abliteration operator on cjvt/GaMS3-12B-Instruct",
        "description": "Each example is one semantic item in one language; `output` is the unedited model's frozen 4-way "
                       "class and every `predict_<method>` is the class the SAME item got under one intervention that was "
                       "actually run. Methods span our concentrated band edits, matched-total-removal-energy spread edits "
                       "(stride-2, stride-4, all-48), layer-matched random and energy-matched principal-component controls, "
                       "the cumulative-prefix / suffix / leave-one-band-out activation arms, and the shipped iteration-1 "
                       "Heretic edit. All labels come from the blind local Qwen3-14B judge over generations on disk.",
        "n_distinct_methods": n_methods, "methods_by_dataset": method_index,
        "primary_comparison": "at matched total removal energy, band_25_36_matchedE_E* (concentrated) vs "
                              "spread_all48_matchedE_E* / spread_stride2 / spread_stride4, against control_random_all48 "
                              "and control_pc_all48 and the baseline_noop column in `output`",
        "model": C.MODEL, "seed": C.SEED, "precision": "bnb NF4, bf16 compute", "decoding": "greedy",
        "analysis_summary": S,
        "redundancy_index": jload(C.RES / "redundancy_index.json") if (C.RES / "redundancy_index.json").exists() else None,
        "frozen_predictions": jload(C.RES / "frozen_predictions.json") if (C.RES / "frozen_predictions.json").exists() else None,
        "design": jload(C.CFG / "design.json"),
        "cross_model": jload(C.RES / "cross_model.json") if (C.RES / "cross_model.json").exists() else None,
        "judge_certification_on_disk": jload(C.RES / "judge_cert_pool.json") if (C.RES / "judge_cert_pool.json").exists() else None,
        "rederive": jload(C.RES / "rederive.json") if (C.RES / "rederive.json").exists() else None,
        "deviations": jload(C.RES / "deviations.json") if (C.RES / "deviations.json").exists() else None,
        "data_usage": jload(C.RES / "data_usage.json") if (C.RES / "data_usage.json").exists() else None,
        "timings_seconds": jload(C.RES / "timings.json"), "workspace": str(C.ROOT),
        "kept_artifacts": {"per-generation outputs + labels": str(C.CELLS), "frozen index": str(C.RES / "redundancy_index.json"),
                           "analysis": str(C.RES / "analysis_summary.json"), "tables": str(C.RES / "report_tables.md")},
    }, "datasets": [{"dataset": k, "examples": v} for k, v in sorted(datasets.items()) if v]}
    jdump(out, C.ROOT / "method_out.json", indent=1)
    tot = sum(len(d["examples"]) for d in out["datasets"])
    preds = sum(sum(1 for k in e if k.startswith("predict_")) for d in out["datasets"] for e in d["examples"])
    logger.info(f"method_out.json: {tot} items in {len(out['datasets'])} datasets, {n_methods} distinct methods, "
                f"{preds} per-item method outcomes")


if __name__ == "__main__":
    main()

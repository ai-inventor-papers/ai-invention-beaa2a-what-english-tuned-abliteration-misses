#!/usr/bin/env python3
"""method_out.json in the exp_gen_sol_out schema: one dataset per (model, phase); one example per generation
(input = the prompt, output = the model's reply), with the 4-way judge label, GlotLID consistency, truncation and the
cell's frozen instrument value O and its cheap competitor B_site as per-example predictions (strings). The metadata
block carries the verdict, every headline statistic and the deviations."""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd

import common as C


def fmt(x) -> str:
    return "" if x is None or (isinstance(x, float) and not math.isfinite(x)) else f"{float(x):.6f}"


def main() -> None:
    A = json.loads((C.RES / "analysis.json").read_text())
    FP = json.loads((C.CFG / "frozen_predictions.json").read_text())
    conds = {c["cell"]: c for c in FP["confirmation_condition_list"]}
    ofz = C.RES / "outside" / "frozen_outside.json"
    if ofz.exists():
        conds |= {c["cell"]: c for c in json.loads(ofz.read_text())["conditions"]}
    items = pd.read_csv(C.RES / "per_item.csv")
    lab = {(r.model, r.cell, r.uid, r.lang): r for r in items.itertuples()}
    ds: dict = {}
    for p in sorted(C.GENS.glob("*.json")):
        if not p.stem.startswith(("PF_", "CF_", "QPF_", "QCF_")):
            continue
        phase = {"PF": "phase1_profile_DEV", "CF": "phase4_confirmation_CONF", "QPF": "phase5_outside_profile_DEV",
                 "QCF": "phase5_outside_confirmation_CONF"}[p.stem.split("_")[0]]
        for r in json.loads(p.read_text()):
            model = r.get("model", "gemma")
            L = lab.get((model, r["cell"], r["uid"], r["lang"]))
            cd = conds.get(r["cell"], {})
            ex = {"input": r["prompt"], "output": r["response"], "metadata_model": model, "metadata_cell": r["cell"],
                  "metadata_family": cd.get("family", "act_single" if "_h" in r["cell"] else "noop"),
                  "metadata_lang": r["lang"], "metadata_uid": r["uid"], "metadata_semantic_id": r["semantic_id"],
                  "metadata_stratum": r.get("stratum"), "metadata_category": r.get("category"),
                  "metadata_label_4way": (L.cls4 if L is not None and L.judged else "UNJUDGED"),
                  "metadata_rubric_unsafe": (bool(L.unsafe) if L is not None and L.judged else None),
                  "metadata_lid_consistency": (None if L is None or not isinstance(L.lid_ok, float) or math.isnan(L.lid_ok) else float(L.lid_ok)),
                  "metadata_hit_max_tokens": bool(r["hit_max"]), "metadata_max_new_tokens": r["max_tok"],
                  "metadata_layers": cd.get("layers"), "metadata_energy": cd.get("E"), "metadata_group": cd.get("group"),
                  "metadata_side": cd.get("side")}
            if cd.get("family") == "weight":
                ex["predict_overlap_instrument_O"] = fmt(cd.get(f"O_{r['lang']}"))
                ex["predict_baseline_single_site_peak"] = fmt(cd.get(f"B_site_{r['lang']}"))
                ex["predict_baseline_log_energy"] = fmt(cd.get("log_energy"))
            ds.setdefault(f"{model}|{phase}", []).append(ex)
    meta = {"method_name": "Frozen weight-space write-mass overlap instrument O vs one-forward-pass baselines",
            "anchor": C.MODEL, "outside": A.get("outside", {}).get("status"),
            "scorer": "local Qwen/Qwen3-14B@40c06982 NF4, frozen exp4 rubric, 4-way partial-aware, blind",
            "verdict": A["verdict"], "profile": A["profile"],
            "screen": {g: {k: A["screen"][g][k] for k in ("n", "spearman", "dR2_O", "LOO_dR2_O", "cell_boot")} for g in C.LANGS},
            "confirm": {g: {k: A["confirm"]["per_language"][g][k] for k in
                            ("n", "spearman", "item_boot", "dR2_O", "LOO_dR2_O", "R2_base", "R2_full", "R2_O_alone",
                             "failed_edits_excluded", "noop_refusal", "placebo", "mde_dR2", "mde_spearman")} for g in C.LANGS},
            "pooled_race": {k: A["confirm"]["pooled_race"][k] for k in ("spearman", "O_minus_baseline_ci", "n_rows", "n_items")},
            "matched_groups": A["confirm"]["matched"]["groups"],
            "pooled_matched": {g: A["confirm"]["matched"].get(f"pooled_hi_minus_lo_{g}") for g in C.LANGS},
            "controls": A["confirm"]["matched"]["controls"], "dose_rival": A["confirm"]["matched"]["dose"],
            "argmax_check": A["confirm"]["argmax_check"], "outside_family": A.get("outside"),
            "judge_gate": {k: v for k, v in A["judge"].items() if k != "rogan_gladen_sensitivity"},
            "deviations": json.loads((C.RES / "deviations.json").read_text()) if (C.RES / "deviations.json").exists() else None,
            "rederive": {k: v for k, v in json.loads((C.RES / "rederive_report.json").read_text()).items() if k in ("n_checks", "n_pass", "n_fail")}
            if (C.RES / "rederive_report.json").exists() else None,
            "frozen_predictions_sha256": C.file_sha256(C.CFG / "frozen_predictions.json"),
            "kept_artifacts_relative": ["results/gens/", "results/judge_local.jsonl", "results/judge_api.jsonl", "results/analysis.json",
                                        "results/cell_table.csv", "results/per_item.csv", "configs/frozen_predictions.json",
                                        "configs/FREEZE.sha256", "figures/"]}
    out = {"metadata": meta, "datasets": [{"dataset": k, "examples": v} for k, v in sorted(ds.items())]}
    (C.ROOT / "method_out.json").write_text(json.dumps(out, ensure_ascii=False, default=lambda o: None if isinstance(o, float) and not math.isfinite(o) else (o.item() if hasattr(o, "item") else str(o))))
    print({k: len(v) for k, v in ds.items()})


if __name__ == "__main__":
    main()

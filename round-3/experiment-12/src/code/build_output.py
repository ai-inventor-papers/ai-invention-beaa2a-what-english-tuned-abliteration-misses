#!/usr/bin/env python3
"""STAGE 8 - assemble method_out.json in the exp_gen_sol_out schema.
One example per (model, language, cell, item) with the prompt, the response, the judged 4-way label, the GlotLID language,
the QC flags and the frozen index; metadata carries the indices, the frozen predictions + hashes, the analysis, the
verdicts, the judge certification, costs, the load log and the deviations."""
from __future__ import annotations

import numpy as np
from loguru import logger

import common as C


def deviations() -> list[dict]:
    return [
        {"id": "D1-judge", "planned": "local Qwen3-14B certified against a fresh gpt-4.1 calibration subsample covering DE/LT "
                                      "(gate G-J2), with gpt-4.1 as fallback primary (F-J)",
         "actual": "the run-level OpenRouter budget ($7.00) was already exhausted by earlier steps when this artifact started, "
                   "so NO API judging was possible. The local judge is the only judge. It is instead calibrated on the FREE pool "
                   "of 4,660 exp8 generations already labelled by gpt-4.1: three rubric variants are scored on a DEV split and "
                   "the best is certified once on a disjoint HOLDOUT split (results/judge_certification_local.json).",
         "cost": "the chosen variant reaches kappa 0.683 on the holdout, BELOW the pre-registered 0.80 gate, and the planned "
                 "fallback (gpt-4.1 primary) could not fire. The judge is sensitive (Se 0.984) but over-calls refusal "
                 "(Sp 0.741), so absolute refusal levels are biased upward; a Rogan-Gladen-corrected re-run of P1/P2 is "
                 "reported. No DE/LT calibration against a stronger judge exists."},
        {"id": "D2-translation-QC", "planned": "gemini-2.5-flash independent back-translation chrF++ per row",
         "actual": "same budget exhaustion; QC uses the NLLB round-trip chrF++ (same-system, optimistic), LaBSE cosine and "
                   "GlotLID. qc_pass thresholds unchanged.", "cost": "back-translation QC is same-system, so it cannot detect "
                   "systematic NLLB biases; the qc-pass-only sensitivity analysis is correspondingly weaker."},
        {"id": "D3-M3", "planned": "utter-project/EuroLLM-9B-Instruct as the third model",
         "actual": "EuroLLM is a gated repo and returned HTTP 403 with this run's HF_TOKEN; the recorded fallback order was "
                   "followed and mistralai/Mistral-7B-Instruct-v0.3 was used (results/load_log.json).", "cost": "no EU-centric "
                   "multilingual model in the panel; LT is out-of-distribution for all three models."},
        {"id": "D4-max-new-tokens", "planned": "max_new_tokens = 256",
         "actual": "96, matching exp8 (the anchor run whose numbers this replicates) and the judge rubric's truncation note, "
                   "on a 20 GB L4 within the wall-clock budget.", "cost": "long-form compliance after a refusal opener cannot be "
                   "observed; the judge rubric explicitly handles truncation."},
        {"id": "D5-sample-size", "planned": "41 DEV harmful per language, 60 CONF harmful per language",
         "actual": "as planned; below Wang et al. (572) and Arditi (100).", "cost": "per-cell 95% CIs are about +/-0.12, so "
                   "adjacent coverage levels can tie; AUC is the pre-registered tie-break and the primary test pools rows."},
        {"id": "D6-W3-new-models", "planned": "a Heretic optimiser search per model",
         "actual": "trial-96's kernel mapped to relative depth with an English dose calibration on CAL ('Heretic-style "
                   "EN-calibrated kernel'); Gemma uses the REAL iter-1 trial-96 adapter, sha256-verified.",
         "cost": "for the new models W3 is a practitioner-like edit, not a replication of Heretic's 116-trial optimiser."},
        {"id": "D7-nf4", "planned": "NF4 for every model", "actual": "as planned (20 GB GPU).",
         "cost": "absolute levels are NF4-specific; all conditions share one load path so contrasts are unaffected."},
        {"id": "D8-native-review", "planned": "PENDING", "actual": "PENDING - no native speaker reviewed the SL/DE/LT items or "
                                                                   "outputs.", "cost": "translation adequacy rests on automated checks only."},
    ]


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("build_output")
    from judge_local import load_labels, qkey
    labels = load_labels()
    frozen = C.jload(C.CFG / "frozen_predictions.json")
    idx = C.jload(C.RES / "indices.json")
    A = C.jload(C.RES / "analysis.json")
    preds = C.jload(C.RES / "predictions.json") if (C.RES / "predictions.json").exists() else {"cell_predictions": {}, "scores": {}}
    cellp = preds.get("group_predictions", preds.get("cell_predictions", {}))
    items = {it["uid"]: it for it in C.read_jsonl(C.DATA / "items_conf.jsonl")}
    items |= {it["uid"]: it for it in C.read_jsonl(C.DATA / "items_idx.jsonl")}
    ds: dict = {}
    n_lab = 0
    for p in sorted(C.RES.glob("*/gens/*.jsonl")):
        for r in C.read_jsonl(p):
            if r["phase"] not in ("dev", "conf"):
                continue
            lab = labels.get(qkey(r))
            n_lab += lab is not None
            it = items.get(r["uid"], {})
            name = "S4_strongreject_pairs (CONF, held out)" if r["phase"] == "conf" else "S3_jbb half B (DEV index)"
            t = frozen["per_model_lang"].get(f"{r['model']}|{r['lang']}", {})
            ex = {"input": r["prompt"], "output": r["response"],
                  "metadata_model": r["model"], "metadata_cell": r["cond"], "metadata_phase": r["phase"],
                  "metadata_lang": r["lang"], "metadata_role": r["role"], "metadata_semantic_id": r["semantic_id"],
                  "metadata_uid": r["uid"], "metadata_stratum": r.get("stratum"), "metadata_category": r.get("category"),
                  "metadata_text_variant": r["text_variant"], "metadata_n_tokens": r["n_tokens"], "metadata_hit_max": r["hit_max"],
                  "metadata_judge_label_4way": lab["four"] if lab else None,
                  "metadata_judge_label_raw": lab["label"] if lab else None,
                  "metadata_judge_wrong_lang": lab["wrong_lang"] if lab else None,
                  "metadata_glotlid": lab["lid"] if lab else None,
                  "metadata_rep4_flag": C.rep_flag(r["response"]),
                  "metadata_translation_qc_pass": it.get(f"{r['lang']}_qc_pass") if r["lang"] in ("de", "lt") else it.get("sl_qc_pass"),
                  "metadata_frozen_index_for_cell": t.get("index"), "metadata_eligible": t.get("eligible"),
                  }
            # Head-to-head predictions. Each competing predictor is a frozen DEV quantity mapped to a predicted CONF
            # refusal rate by a leave-one-model-out fit (code/predictors.py), so no row is predicted by a fit that saw
            # it. All items in a cell share that cell's rate, because every one of these predictors is cell-level.
            ck = f"{r['model']}|{r['cond']}|{r['role']}|{r['lang']}"
            for mname, table_ in cellp.items():
                if ck in table_:
                    ex[f"predict_{mname}"] = "refused" if table_[ck] >= 0.5 else "not_refused"
                    ex[f"metadata_predicted_rate_{mname}"] = table_[ck]
            if lab:
                ex["metadata_observed_outcome"] = "refused" if lab["four"] == "REFUSED" else (
                    "excluded_invalid" if lab["four"].startswith("INVALID") else "not_refused")
            ds.setdefault(name, []).append(ex)
    cert_local = C.jload(C.RES / "judge_certification_local.json")
    meta = {
        "method_name": "Depth-redundancy index as a predictor of cross-lingual refusal-edit failure",
        "description": "For each instruct model, the English per-layer refusal direction d_EN(h) is ablated over cumulative "
                       "depth prefixes and the coverage needed to push judged harmful refusal below 0.5 is recorded per "
                       "language (index_L) on DEV items. The index is frozen and hashed, then tested out of sample as a "
                       "predictor of the residual refusal left by English-derived Heretic-operator WEIGHT edits on held-out "
                       "StrongREJECT items in four languages, against the familiar predictors (EN/L direction cosine, "
                       "baseline refusal, single-site transfer, first-token margin).",
        "models": frozen["models"], "languages": list(C.LANGS),
        "workspace": str(C.ROOT),
        "kept_artifact_paths": {"generations": str(C.RES / "<model>/gens/*.jsonl"), "labels": str(C.RES / "labels_qwen.jsonl"),
                                "directions": str(C.RES / "<model>/directions.npz"), "indices": str(C.RES / "indices.json"),
                                "frozen_predictions": str(C.CFG / "frozen_predictions.json"),
                                "analysis": str(C.RES / "analysis.json"), "rederivation": str(C.RES / "rederive.json")},
        "frozen_predictions": frozen, "indices": idx["table"], "dev_curves": idx["curves"],
        "weight_panel_choices": frozen["weight_panel_choices"],
        "panel_info": {m: C.jload(C.RES / m / "panel_info.json") for m in frozen["models"] if (C.RES / m / "panel_info.json").exists()},
        "panel_collateral": {m: C.jload(C.RES / m / "panel_collateral.json") for m in frozen["models"]
                             if (C.RES / m / "panel_collateral.json").exists()},
        "direction_diagnostics": {m: {k: v for k, v in C.jload(C.RES / m / "direction_diagnostics.json").items()
                                      if k not in ("auroc", "auroc_shuffled", "dprime")} for m in frozen["models"]},
        "analysis": {k: v for k, v in A.items() if k != "rows"}, "verdict": A["verdict"],
        "judge": {"primary": cert_local.get("chosen"), "certification_local": cert_local,
                  "certification_stage1_existing_labels": C.jload(C.RES / "judge_certification_stage1.json"),
                  "rubric": C.jload(C.CFG / "judge_rubric.json")},
        "rederivation": C.jload(C.RES / "rederive.json") if (C.RES / "rederive.json").exists() else None,
        "translation_qc": C.jload(C.DATA / "qc_summary.json"), "load_log": C.jload(C.RES / "load_log.json"),
        "hardware": "1x NVIDIA L4 (23 GB), 48 vCPU; every model NF4 (bnb double-quant, bf16 compute)",
        "api_cost_usd": sum(float(r.get("usd") or 0) for r in C.read_jsonl(C.RES / "cost_log.jsonl")),
        "deviations": deviations(), "cuts_applied": C.CUTS_APPLIED, "n_examples_labelled": n_lab,
        "audit_checks": C.jload(C.RES / "checks.json") if (C.RES / "checks.json").exists() else None,
        "analysis_post_freeze_patch": C.jload(C.RES / "analysis_patch.json") if (C.RES / "analysis_patch.json").exists() else None,
        "report_tables_md": "results/report_tables.md",
        "head_to_head_predictions": preds.get("scores"),
        "n_prediction_groups": preds.get("n_groups"),
        "prediction_protocol": preds.get("method"),
        "prediction_scope_note": (
            "predict_* fields are on EVERY judged generation. A prediction is made for the group "
            "(model, condition, role, language) the item belongs to, by a leave-one-model-out one-way fixed-effects "
            "fit: rate = level(condition, role) + b * (X - mean X), where the level and the slope are estimated only "
            "from the OTHER models' groups. `majority` is the same model with b = 0 (the condition's level alone), so "
            "a predictor that does not beat `majority` has added nothing over knowing which condition the item came "
            "from. Note that every one of these predictors is constant within a group and varies only by (model, "
            "language), so it cannot distinguish edit shapes within a model - which is why the matched-energy contrast "
            "(prediction P3) is a separate, cell-level test. Items the judge marked INVALID have no observed outcome "
            "and are excluded from scoring."),
        "posthoc_decomposition": C.jload(C.RES / "posthoc_decomposition.json") if (C.RES / "posthoc_decomposition.json").exists() else None,
        "freeze_sha256": (C.CFG / "FREEZE.sha256").read_text().splitlines(),
    }
    out = {"metadata": meta, "datasets": [{"dataset": k, "examples": v} for k, v in sorted(ds.items())]}
    C.jdump(out, C.ROOT / "method_out.json", indent=1)
    logger.info(f"method_out.json: {sum(len(v) for v in ds.values())} examples ({n_lab} labelled) in {len(ds)} datasets")


if __name__ == "__main__":
    main()

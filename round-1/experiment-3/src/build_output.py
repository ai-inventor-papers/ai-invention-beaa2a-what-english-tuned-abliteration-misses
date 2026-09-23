"""Assemble method_out.json (exp_gen_sol_out schema): metadata = full analysis summary + provenance;
datasets = per-model half-B JBB items with per-condition refusal log-odds as predict_* fields."""
from __future__ import annotations

import json

import pandas as pd
from loguru import logger

import common as C
from common import LANGS, file_sha256, jdump, jload

COND_NAMES = {"C0": "noop", "C1": "ablate_dEN", "C2": "ablate_dSL", "C3": "ablate_span_dEN_dSL", "C4": "ablate_uSL",
              "C5": "ablate_uEN", "C6": "ablate_random_R1", "C7": "ablate_random_R2", "C8": "ablate_random_R3",
              "C9": "ablate_dEN_plus_randQ1", "C10": "ablate_dEN_plus_randQ2", "C11": "ablate_dEN_plus_randQ3",
              "C12": "ablate_dEN_plus_unoiseSL", "C13": "ablate_dSL_plus_unoiseEN", "C14": "ablate_span_dSL_uEN",
              "C6r": "ablate_random_rawE_R1", "C7r": "ablate_random_rawE_R2", "C8r": "ablate_random_rawE_R3",
              "C9r": "ablate_dEN_plus_rawE_Q1", "C10r": "ablate_dEN_plus_rawE_Q2", "C11r": "ablate_dEN_plus_rawE_Q3"}


def frozen_predictions(summary: dict) -> dict:
    pm = summary["per_model"]
    out = {}
    for m, r in pm.items():
        proto = jload(C.CFG / f"frozen_protocol_{m}.json")
        out[m] = {"h_star": proto["h_star"], "pos_star": proto["pos_star_name"], "directions_npz": f"results/{m}/frozen_directions.npz",
                  "directions_sha256": proto["directions_npz_sha256"], "prefix_sets": f"configs/prefix_sets_{m}.json",
                  "predicted": {"T_en->sl": r["transfer_matrix_ablation"]["en->sl"]["est"], "T_sl->en": r["transfer_matrix_ablation"]["sl->en"]["est"],
                                "F_raw": r["u_increment"]["F_raw"]["est"], "F_ctrl": r["u_increment"]["F_ctrl"]["est"],
                                "rho_gap_C1": r["matched_efficacy"].get("rhoSL_C1_minus_rhoEN_C1", {}).get("est")}}
    out["rule_to_retest"] = ("Apply the frozen directions (no refitting) and the frozen A1 rules (SURVIVE_RAW / SURVIVE_CTRL / KILL) on "
                             "S4 held-out items and RefusEU-EN/SL grade-T pairs (produced by the DATASET artifact) and on Heretic TPE trials "
                             "61-200 / seed-20260924 edits (produced by the Heretic core pod). Not produced here; named only.")
    return out


def build(summary: dict) -> None:
    datasets = []
    for m in summary["per_model"]:
        df = pd.read_parquet(C.RES / m / "per_item.parquet")
        judged = [j for j in (jload(C.RES / "judged_generations.json") if (C.RES / "judged_generations.json").exists() else []) if j["model"] == m]
        jmap = {(j["condition"], j["lang"], j["kind"], j["semantic_id"]): j for j in judged}
        items = {it["semantic_id"] + it["kind"]: it for it in jload(C.DATA / "screen_dev.json")}
        ex = []
        sub = df[df.kind.isin(["jbb_harmful", "jbb_benign"]) & df.condition.str.startswith("abl:")]
        for (lang, kind, sid), g in sub.groupby(["lang", "kind", "semantic_id"]):
            it = items[sid + kind]
            rec = {"input": it[lang], "output": "refuse" if kind == "jbb_harmful" else "comply",
                   "metadata_model": m, "metadata_lang": lang, "metadata_kind": kind, "metadata_semantic_id": sid,
                   "metadata_category": it["extra"].get("Category"), "metadata_source": it["extra"].get("Source"),
                   "metadata_mt_chrF": it["extra"].get("chrF")}
            for _, row in g.iterrows():
                cn = row.condition.split(":")[1]
                rec[f"predict_{COND_NAMES[cn]}_R"] = f"{row.R:.4f}"
            for cn in ("C0", "C1", "C2", "C3", "C4", "C6", "C6r"):
                j = jmap.get((cn, lang, kind, sid))
                if j:
                    rec[f"predict_{COND_NAMES[cn]}_response"] = j["response"]
                    rec[f"metadata_judge_{COND_NAMES[cn]}"] = j["judge_label"]
            ex.append(rec)
        datasets.append({"dataset": f"JBB-Behaviors half-B (EN + NLLB-SL), {C.MODELS[m]['repo']}", "examples": ex})
    meta = {"method_name": "A1 screen: EN vs SL refusal-direction transfer (2x2 source x eval matrix, u_SL increment, controls)",
            "models": C.MODELS, "heretic_sha": C.HERETIC_SHA, "precision_deviation": jload(C.RES / "deviations.json") if (C.RES / "deviations.json").exists() else None,
            "translations_sha256": (C.DATA / "translations.sha256").read_text().split()[0],
            "data_build": jload(C.DATA / "data_build_meta.json"),
            "frozen_protocol_sha256": {m: (C.CFG / f"frozen_protocol_{m}.sha256").read_text().strip() for m in summary["per_model"]},
            "api_cost_total_usd": 0.0,
            "per_model": summary["per_model"], "validity": summary["validity"], "judge_based": summary["judge_based"],
            "cos_vs_transfer": summary["cos_vs_transfer"], "mt_quality_subset": summary.get("mt_quality_subset"), "freeze_check": summary["freeze_check"],
            "screen_verdict": summary["screen_verdict"], "baseline_kw_refusal_halfA": summary["baseline_kw_refusal_halfA"],
            "heretic_bridge": {m: (jload(C.RES / m / "heretic_bridge.json") if (C.RES / m / "heretic_bridge.json").exists() else "not run")
                               for m in C.MODELS},
            "frozen_predictions_for_confirmation": frozen_predictions(summary),
            "per_example": {m: {"per_item_parquet": f"results/{m}/per_item.parquet", "generations": f"results/{m}/generations.json"} for m in summary["per_model"]}
            | {"judged": "results/judged_generations.json"}}
    out = {"metadata": meta, "datasets": datasets}
    jdump(out, C.ROOT / "method_out.json", indent=None)
    logger.info(f"method_out.json written: {sum(len(d['examples']) for d in datasets)} examples, "
                f"{(C.ROOT / 'method_out.json').stat().st_size/1e6:.1f} MB")

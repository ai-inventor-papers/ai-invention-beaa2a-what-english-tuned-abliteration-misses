#!/usr/bin/env python3
"""Collect run metadata for method_out.json: pins, smoke/certification, runtime decisions, generation stats, costs,
judge bookkeeping, second-judge / guard / R_seq / audit summaries, sanity flags, deviations, absolute workspace paths
and what the results do NOT show.  -> results/run_metadata.json (read by to_schema.py)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from loguru import logger

from common import ALL_CKPTS, WS, read_jsonl, setup_logging


def rjson(rel: str):
    p = WS / rel
    return json.loads(p.read_text()) if p.exists() else None


def rjl(rel: str) -> list[dict]:
    p = WS / rel
    return read_jsonl(p) if p.exists() else []


def judge_bookkeeping(sub: str) -> dict:
    out = {}
    for ck in ALL_CKPTS:
        rows = rjl(f"{sub}/{ck}.jsonl")
        if not rows:
            continue
        last = {}
        for r in rows:  # later rows (successful retries) supersede earlier failures
            if r["item_key"] not in last or last[r["item_key"]].get("judge_fail"):
                last[r["item_key"]] = r
        v = list(last.values())
        out[ck] = {"n_labelled_items": len(v), "n_judge_fail_final": sum(bool(r.get("judge_fail")) for r in v),
                   "n_auto_empty": sum(r.get("judge_model") == "auto_empty" for r in v),
                   "n_rows_in_file_incl_failed_attempts": len(rows),
                   "class_counts": dict(Counter(r.get("cls") for r in v))}
    return out


def cost_summary() -> dict:
    rows = rjl("results/cost_log.jsonl")
    by = Counter()
    n = Counter()
    for r in rows:
        by[r["model"]] += float(r.get("cost") or 0)
        n[r["model"]] += 1
    return {"total_usd": round(sum(by.values()), 4), "by_model_usd": {k: round(v, 4) for k, v in by.items()},
            "n_calls_by_model": dict(n), "cap_usd": 10.0, "hard_stop_usd": 9.0,
            "source": str(WS / "results/cost_log.jsonl")}


DEVIATIONS = [
    "JUDGE SUBSTITUTION (F1, the largest deviation): the primary gpt-4.1 judge labelled 716 of 3,840 core items - in a "
    "SEEDED-RANDOM SHUFFLED order, so a random subset, not a prefix - before the RUN-LEVEL OpenRouter budget for this phase "
    "was exhausted (HTTP 403 aii_run_budget_exhausted, $7.00 of $7.00 for the whole run; this artifact spent $1.07). A "
    "substitute judge from a third family, Qwen/Qwen3-14B run LOCALLY (NF4, thinking disabled, greedy), applies the SAME "
    "frozen rubric verbatim and labels all 4,800 items. It agrees with gpt-4.1 at kappa 0.83 (6-way CLASS) and 0.91 "
    "(refused vs not); every headline is reported under both label sources (results/analysis.json vs "
    "results/analysis_gpt41_subset.json) and the validation is in results/judge_validation.json.",
    "ASR IS NOT TAKEN FROM THE SUBSTITUTE JUDGE: its safe/unsafe first line tracks the REQUEST, not the response (it marks "
    "judged REFUSALS of harmful prompts 'unsafe' - see analysis.judge_unsafe_line_diagnostic). The reported ASR is therefore "
    "RefusEU's own guard pipeline (Llama-Guard-3-8B + PolyGuard-Qwen, 91.2% agreement, full reproduction), with the gpt-4.1 "
    "unsafe line on its 716-item subset as the secondary reading.",
    "GUARD DISAGREEMENTS ARE UNADJUDICATED: RefusEU's gpt-4o-mini adjudicator needs API budget, so 292 of 3,300 guard "
    "disagreements have no final label. They are EXCLUDED from the ASR point estimate and BOUNDED (all-safe / all-unsafe) in "
    "results/guard/summary.json; the bounds do not change any conclusion.",
    "LANGUAGE CONSISTENCY IS SCORED BY GlotLID, not by the judge's LANG line: the substitute judge mislabels SHORT Slovene "
    "refusals ('Oprostite, vendar...') as English, which would confound the outcome with refusal itself. GlotLID agrees with "
    "gpt-4.1's LANG line on 100% of the 352-item Slovene overlap (analysis.lang_line_vs_glotlid_sl).",
    "SECOND JUDGE (Stage F, gemini-2.5-flash on the frozen 400) NOT RUN - same budget block. The cross-family agreement check "
    "is served by the local substitute judge on ALL items plus the 30-item blind EXECUTOR CHECK; the frozen 400-item sample "
    "is still in frozen_samples.json and judge2.py is one command away.",
    "JUDGE PARSE FAILURES were fixed in the PARSER, never the prompt (F8): gpt-4.1 sometimes emits CLASS/LANG as bare lines; "
    "raw outputs are logged, so reparse.py re-derived those labels without any new call. The local judge's failures are "
    "truncations (it enumerates every category, hitting the 40-token cap); those rows were re-labelled once at a 160-token "
    "cap and 1 of 4,800 remains unparsed.",
    "SESSION INTERRUPTION: the executing container restarted at ~22:40 UTC while Stage C was running (gams_edit 930/960 done, "
    "gemma not started). Generation resumed by item_key from the append-only jsonl on a fresh model load; completed batches "
    "are written atomically, so no item was generated twice and the frozen batch schedule was unchanged.",
    "BATCHING CERTIFICATION (B3): Gemma failed left-pad eager (11/16, one row diverging within 8 tokens) and left-pad sdpa "
    "(12/16) and PASSED exact-length buckets (14/16, all first-8 match). GaMS failed ALL three modes at 12/16, INCLUDING "
    "exact-length buckets (no padding at all), so part of the batch-1 disagreement is NF4/bf16 batch-shape numerics, not "
    "padding; every observed divergence is a coherent near-tie paraphrase (results/smoke/*.json mismatch_examples). Per F2, "
    "exact-length buckets were used for ALL five checkpoints with one shared schedule (schedule_sha in "
    "logs/generation_stats.jsonl). Greedy outputs are therefore reproducible only under the same bucket schedule.",
    "EXECUTION: orig and edit of one model ran as two concurrent processes (0.48 VRAM each); batch 32 OOMed on long buckets "
    "and was halved (chunks of 16/14/13...); the chunk size is stored per row (batch_size_used). Content and order unchanged.",
    "SMOKE: Gemma B2 ran in --quick mode (5 harmful + 5 benign JBB prompts per language instead of 10+10) for time; the "
    "20-prompt S1 keyword check was complete. The community slot check ran B1+B2 only (no adapter, no batching re-test: "
    "the frozen bucket mode was reused, as the plan requires one mode for all checkpoints).",
    "T5 MINI END-TO-END: generation was launched directly after Stage B because the OpenRouter key was at its daily limit "
    "(403 at 21:15 UTC); the judge-side T5 check (10 items) was run after the 00:00 UTC reset and before the full judge.",
    "JUDGE TIMING: all API stages (B5 calibration, primary judge, second judge, adjudicator) ran after the 00:00 UTC key "
    "reset; nothing was judged before generation of all five checkpoints was complete.",
    "OPENROUTER ENDPOINT: the first draft of judge.py hard-coded openrouter.ai; fixed to the run proxy OPENROUTER_BASE_URL "
    "before any judge call (no label was affected).",
    "COMMUNITY MODEL CARD: verified Heretic v1.0.0, KL 0.16, refusals 3/100 vs 97/100; the card does NOT state a trial count "
    "(an earlier note said 100 trials; unverified). Card saved to results/community/model_card_e037e6e1.md.",
    "ADAPTER COPIES: adapters/<tag>_selected_path2 matched SHA256SUMS for both models and was used; adapters/<tag>_selected "
    "is NOT byte-identical to the _path2 copy (recorded in results/smoke/*.json; not used).",
    "PRECISION: all five checkpoints are NF4 4-bit (double quant, bf16 compute); the community bf16 merged edit is quantised "
    "on load, so it is 'community edit under NF4', not the published model.",
    "MAX_NEW_TOKENS=256 (not HarmBench's 512); hit_max is stored per output and shown to the judge as [TRUNCATED AT 256 TOKENS].",
]

NOT_SHOWN = [
    "Nothing here attributes a difference to a training stage (Slovene continual pretraining, instruction tuning, safety data): "
    "Gemma-3-12B-it is a same-family reference, not GaMS3's parent, and n = 2 models.",
    "Prompt-level CIs do NOT measure Heretic run-to-run (optimiser seed) variance: one optimisation run per model.",
    "S5 EN vs SL contrasts are UNPAIRED (RefusEU rows sharing an id are not translations: 0 T / 158 P grades); only S5X pairs "
    "support paired cross-language claims, and S5X Slovene/English sides are machine translations with automated QC only.",
    "Absolute refusal/ASR levels are under NF4 and 256 tokens, with a gpt-4.1 extended-rubric judge; they are not comparable "
    "to published bf16 numbers or to RefusEU's official ASR except through the official-pipeline sensitivity arm.",
    "Per-category breakdowns use INFERRED, low-confidence RefusEU categories and are descriptive only.",
    "Human (native-speaker) review was prepared but NOT performed (NATIVE_REVIEW_PENDING); the executor check is not human review.",
    "Utility (lm-eval / Slovenian LLM Eval) and harmless KL are owned by the other C1 artifact and are not measured here.",
    "R_seq validity is a supplementary FINAL-distribution check; it does not replace DEV validation elsewhere.",
]


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("build_metadata")
    A = rjson("results/analysis.json") or {}
    gen_stats = rjl("logs/generation_stats.jsonl")
    last_stats = {}
    for s in gen_stats:
        last_stats[s["ckpt"]] = s
    paths = {
        "workspace": str(WS),
        "frozen_samples": str(WS / "frozen_samples.json"), "protocol": str(WS / "protocol.yaml"),
        "protocol_runtime": str(WS / "protocol_runtime.json"),
        "generations": {ck: str(WS / "results/gen" / f"{ck}.jsonl") for ck in ALL_CKPTS},
        "primary_judge_labels": {ck: str(WS / "results/judge" / f"{ck}.jsonl") for ck in ALL_CKPTS},
        "second_judge_labels": str(WS / "results/judge2"), "autoscores": str(WS / "results/autoscore"),
        "guard_pipeline": str(WS / "results/guard"), "analysis": str(WS / "results/analysis.json"),
        "audit": str(WS / "results/audit.json"), "judge2_agreement": str(WS / "results/judge2_agreement.json"),
        "executor_audit": str(WS / "results/executor_audit.json"), "rseq": str(WS / "results/rseq"),
        "substitute_judge_labels": {ck: str(WS / "results/judge_local" / f"{ck}.jsonl") for ck in ALL_CKPTS},
        "judge_validation": str(WS / "results/judge_validation.json"),
        "headline_table_csv": str(WS / "results/headline_table.csv"),
        "analysis_gpt41_subset": str(WS / "results/analysis_gpt41_subset.json"),
        "guard_summary": str(WS / "results/guard/summary.json"),
        "human_packet": str(WS / "results/human_packet/packet.csv"),
        "human_packet_key": str(WS / "results/human_packet/packet_key.json"),
        "figures": str(WS / "figures"), "judge_debug_log": str(WS / "logs/judge_debug.log"),
        "core_adapters_read_only": {
            "gams_edit": str(Path(__file__).resolve().parents[3] / "round-1/experiment-1/src/adapters/gams_selected_path2"),
            "gemma_edit": str(Path(__file__).resolve().parents[3] / "round-1/experiment-1/src/adapters/gemma_selected_path2")},
    }
    frozen = rjson("frozen_samples.json") or {}
    meta = {
        "artifact": "C1 BEHAVIOUR (FINAL, run once): 4 core checkpoints + community sanity reference, EN/SL",
        "freeze_hashes": (WS / "logs/freeze_hashes.txt").read_text().strip().splitlines()[-1] if (WS / "logs/freeze_hashes.txt").exists() else None,
        "dataset_protocol_hash": frozen.get("dataset_protocol_hash"),
        "n_items_per_checkpoint": len(frozen.get("items", [])),
        "set_sizes": dict(Counter(it["set"] + "_" + it["lang"] for it in frozen.get("items", []))),
        "pins": rjson("results/pins_verified.json"),
        "smoke": {m: {k: v for k, v in (rjson(f"results/smoke/{m}.json") or {}).items() if k not in ("b2",)}
                  for m in ("gams", "gemma", "community")},
        "smoke_b2_keyword_refusals_of_20": {m: {c: d.get("s1_keyword_refusals_of_20") for c, d in (rjson(f"results/smoke/{m}.json") or {}).get("b2", {}).items()}
                                            for m in ("gams", "gemma", "community")},
        "runtime": rjson("protocol_runtime.json"),
        "generation_stats": last_stats,
        "costs": cost_summary(),
        "judge_primary_bookkeeping": judge_bookkeeping("results/judge"),
        "judge_secondary_bookkeeping": judge_bookkeeping("results/judge2"),
        "judge_local_substitute_bookkeeping": judge_bookkeeping("results/judge_local"),
        "judge_local_batching_certification": rjson("results/judge_local_cert.json"),
        "judge_validation_local_vs_gpt41": rjson("results/judge_validation.json"),
        "guard_official_summary": rjson("results/guard/summary.json"),
        "judge_dev_calibration": rjson("results/judge_dev_calibration.json"),
        "judge_t5_mini": rjson("results/judge_t5_mini.json"),
        "judge_blocked": rjson("results/judge_blocked.json"),
        "judge2_agreement": rjson("results/judge2_agreement.json"),
        "executor_audit": rjson("results/executor_audit.json"),

        "rseq_validity": rjson("results/rseq/rseq_validity.json"),
        "audit_summary": {k: v for k, v in (rjson("results/audit.json") or {}).items() if k != "checks"},
        "independent_reverification": {k: v for k, v in (rjson("results/verify_headlines.json") or {}).items() if k != "checks"},
        "t8_stats_sanity": rjson("results/t8_stats_sanity.json"),
        "sanity_flags": A.get("sanity"),
        "cuts_applied": rjson("results/cuts_applied.json"),
        "deviations": DEVIATIONS,
        "what_this_does_NOT_show": NOT_SHOWN,
        "human_review_status": "NATIVE_REVIEW_PENDING (200-item blinded packet prepared, not reviewed)",
        "paths": paths,
    }
    (WS / "results/run_metadata.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False, default=str))
    logger.info(f"wrote results/run_metadata.json; costs {meta['costs']['total_usd']}")


if __name__ == "__main__":
    main()

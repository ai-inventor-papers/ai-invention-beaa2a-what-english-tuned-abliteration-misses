#!/usr/bin/env python3
"""Write results/deviations.json: every departure from the artifact plan, with the evidence file that motivated it."""
from __future__ import annotations

import common as C
from common import jdump, jload


def main() -> None:
    D = []

    def add(what, why, evidence, when="pre-freeze"):
        D.append({"deviation": what, "reason": why, "evidence": evidence, "when": when})
    add("Hardware: RTX 4090 24 GB (plan: A4500 20 GB)", "machine provided", "results/gemma/load_info.json")
    add("Pre-freeze labels for r_prior construction, openers and split-half ceilings come from a narrow opener-rule labeller, not gpt-4.1",
        "the shared OpenRouter key was at its $50 daily limit from the start of this artifact (HTTP 403 'Key limit exceeded'); the rule "
        "was validated on iteration-1 A1 gpt-4.1 labels of Gemma benign twins (agreement .95 EN / .96 SL, 100-char window); post-hoc "
        "agreement with gpt-4.1 on the same HALF_A outputs is reported in analysis_summary.label_agreement.halfA_construction_labels",
        "common.py:rule_refused; logs/judge.log")
    add("Stage 2 (GaMS3 load #1 for per-item compliance references) not run; R_seq uses per-language canonical 8-token refusal and "
        "compliance openers mined from Gemma's own HALF_A outputs (plan fallback), OPENER_TOK=8 instead of 24",
        "GPU-time budget (single GPU, ~6 h total incl. judge wait)", "references/openers_gemma.json")
    add("Layer selection, matched efficacy, shuffle-median choice and weight-band choice use R1 (first-token log-odds) instead of R_seq",
        "the canonical-opener R_seq failed its T2 sign check on judged-complied items (negative on only 1/8 EN, 1-2/8 SL), whereas "
        "iteration-1 A1 validated R1 for Gemma (condition Spearman .91, item AUROC .96); both traits are still recorded for every arm",
        "results/gemma/rseq_sanity.json; results_mini/gemma/rseq_sanity.json")
    add("Batching certification gate: 13/16 prompts identical over 32 tokens (< 15/16); batched left-padded generation accepted by "
        "amendment because all 16 refusal classes matched and every divergence was late bf16 drift (no corruption)",
        "the known trap is corrupted left-padded output, not late drift; bucketed generation would have cost several GPU-hours",
        "results/gemma/batch_cert.json (first_divergence)")
    add("Layer-selection filter relaxed: no candidate layer passed Dolly first-token KL < 0.1 (KL 0.41-12 at all 20 layers); the plan "
        "fallback (smallest FLORES among top-3 drops) would have chosen h=12 with FLORES +7.4 nats. Only the KL filter was dropped: "
        "max SL-benign R1 drop among |FLORES|<0.1 layers, ties within 5% broken by smaller KL",
        "decided on HALF_A only, before freeze; KL failure is itself a finding (r_prior ablation shifts first-token distributions on "
        "harmless Dolly prompts)", "results/gemma/layer_selection.json")
    add("Outcome generations: 96 new tokens (plan: 128); HALF_A generations 64", "plan's GPU fallback", "method.py GEN_TOK_OUT")
    rd = C.RES / "gemma" / "rand_draws.json"
    if rd.exists():
        r = jload(rd)
        if r.get("amendment"):
            add("Random controls: " + r["amendment"], "energy+collateral matching failed within the draw budget",
                "results/gemma/rand_draws.json", "pre-freeze")
    add("Weight edit implemented as exact output hooks on o_proj/down_proj (Heretic-style orthogonalisation). Gemma-3 applies "
        "post_attention_layernorm / post_feedforward_layernorm AFTER these projections, so orthogonalising their outputs does not "
        "guarantee that r_prior is absent from the residual write (same limitation as Heretic's weight edit on Gemma-3)",
        "fidelity to the plan and to Heretic", "interventions.py:set_weight_edit; results/gemma/hook_tests.json")
    add("Weight band chosen with the trial-96 LoRA attached (core edit), then reused unchanged on the community model", "plan 3.11/Stage 4",
        "results/gemma/weight_edit.json")
    add("Community model pinned to p-e-w/gemma-3-12b-it-heretic@e037e6e1 (HF API head on 2026-09-23), NF4-quantised on load", "plan", "common.py MODELS")
    add("Norm-preserving Heretic weight-edit variant and GaMS3 load #1 (per-item compliance references) not run; the S2 stability "
        "rebuild (3.12) ran inside the exploratory stage with rule labels (same labeller as the S3 construction), teacher-forced outcome only",
        "time budget; plan priority order", "results/gemma/s2_stability.json")
    add("ADDED exploratory post-freeze arms X1 (layer-matched d_EN(h) at every hidden index), X2 (layer-matched span{d_EN(h), d_SL(h)}), "
        "X4 (d_EN at c=2) - declared in configs/explore_protocol.json (sha in FREEZE.sha256) before their outcome passes; they are "
        "NOT part of the frozen F-family and are reported as exploratory boundary tests ('can any harm-direction family remove the "
        "Slovene residual?')", "the frozen arms left ~70-90% SL harmful refusal after d_EN; the reviewer-facing question is where the "
        "claim stops", "method.py:main_explore", "post-freeze (exploratory)")
    add("Gemma run was interrupted once (session end at 22:39 UTC, after arm A7) and resumed from per-arm checkpoints; arms are "
        "resumable by file, so no completed generation was regenerated", "session interruption", "logs/method_gemma.log", "post-freeze")
    add("Judge endpoint: the run-scoped OPENROUTER_BASE_URL proxy with an explicit User-Agent (default urllib/aiohttp agents get HTTP 403)",
        "environment", "judge.py", "post-freeze (labels only)")
    add("Judging ran after the GPU stages, once the shared key's daily limit reset (00:00 UTC); items without a gpt-4.1 label fall back "
        "to the rule labeller and are flagged per item (label_source)", "key limit", "results/judge_cache.jsonl; analysis_summary.label_coverage",
        "post-freeze (labels only; no protocol change)")
    add("Second judge is a LOCAL cross-family model (Qwen/Qwen3-14B, 4-bit, same frozen rubric, blind) instead of the planned "
        "google/gemini-2.5-flash on a 150-item stratified sample; it labelled EVERY generation, so it also supplies the "
        "full-coverage rates for the arms the primary judge could not reach",
        "the run's OpenRouter budget for this phase ($7.00, shared by the phase's artifacts, non-resetting) was reached after 5,295 of 9,134 generations; a resume attempt on 2026-09-24 02:58 UTC was refused (HTTP 403 aii_run_budget_exhausted) and every free OpenRouter model was at its shared daily cap (HTTP 429, reset ~21 h later), so no API judge - paid or free - could be used",
        "local_judge.py; results/judge2_local.jsonl; analysis_summary.label_agreement.second_judge", "post-freeze (labels only)")
    add("Primary judging is BATCHED (10 blind cases per gpt-4.1 call) rather than one call per item",
        "cost: it halves the per-case price; validated against 450 single-case labels from the same model (kappa .95 refused-vs-not)",
        "judge.py:_judge_batches; analysis_summary.label_agreement.batch10_vs_single_gpt41", "post-freeze (labels only)")
    add("ADDED exploratory post-freeze arms X3/X5 (layer-matched random and energy-matched principal-component controls for X1), "
        "Y1-Yc36 (depth bands of layer-matched d_EN(h)) and W3/W4 (core Heretic edit + layer-matched ablation / random control), "
        "each declared in configs/explore2_protocol.json or explore3_protocol.json and hashed into FREEZE.sha256 before its outcome pass",
        "X1 was the strongest effect in the artifact and needed matched controls and a depth profile; W3/W4 turn it into the "
        "practitioner question the core study asks", "method.py:main_explore2, main_explore3", "post-freeze (exploratory)")
    add("Layer-matched random controls (X3) match d_EN(h) projection energy at only 15/48 hidden indices; the principal-component "
        "control (X5) matches at 46/48 and is reported beside it", "Gaussian draws in a 60-dim PC span cannot reach the harm "
        "direction's energy at most layers - itself a property of d_EN(h)", "results/gemma/layerwise_random_match.json, layerwise_pc_match.json",
        "post-freeze (exploratory)")
    add("Native-speaker review of Slovene items and outputs: PENDING (not performed)", "no qualified reviewer available", "-")
    jdump(D, C.RES / "deviations.json")
    print(len(D), "deviations")


if __name__ == "__main__":
    main()

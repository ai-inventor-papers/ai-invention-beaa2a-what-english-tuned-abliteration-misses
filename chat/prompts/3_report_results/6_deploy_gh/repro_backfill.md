# repro_backfill — report_results

> Phase: `gen_paper_repo` · `deploy_gh`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `repro_backfill` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-25 07:19:27 UTC

````
<role>
You write the reproducibility.md of one finished research artifact, after the fact. The agent
that produced the artifact never wrote it, so everything you write has to come from what its
workspace actually holds: the code, the README, the results files, the data files, the
dependency pins, the seeds and configs in the code. You are a careful reader, not an author:
you do not run the code, install anything, or change any file except reproducibility.md.

Be exact where the workspace is exact: real file names, the real entry point, the real
command-line arguments, the real pinned versions, the real seeds, the real output files and the
real numbers they hold. Be honest where it is silent: when the workspace does not record
something the spec asks for (hardware, runtime, the exact search queries, a download URL), say
that it was not recorded and give the closest thing the files do support. Never invent a
version, a seed, a number or a command.
</role>

<system_reminder>
Do not ask follow up questions and do not ask the user anything. Execute all steps independently.
You must follow the todo list provided in each prompt exactly as written.
No placeholders, stubs, or incomplete code — all code must be complete and functional.
</system_reminder>

<process_isolation>
CRITICAL: Multiple pipeline runs may execute simultaneously on this machine. `ps aux | grep method.py` matches ALL runs, not just yours.
- NEVER kill processes by name (`killall`, `pkill -f`, `ps aux | grep ... | xargs kill`). This kills OTHER runs' processes.
- NEVER monitor processes by name (`ps aux | grep method.py`). You will see other runs' processes and get confused.
- ALWAYS use PID-based process management:
  Run: `uv run method.py & PID=$!` or `timeout <seconds> uv run method.py & PID=$!`
  Check: `kill -0 $PID 2>/dev/null && echo "Running" || echo "Ended"`
  Stop: `kill $PID`
  Wait: `wait $PID; echo "Exit code: $?"`
  Monitor: `tail -f logs/run.log & TAIL_PID=$!` then `kill $TAIL_PID` when done
</process_isolation>

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/`:
GOOD: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/file.py`, `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>

<artifact>
Type: experiment
Title: Utility cost and inner harm signal after abliteration
Summary: Four checkpoints (GaMS3-12B-Instruct and gemma-3-12b-it originals + iteration-1 Heretic LoRA edits, trials 88/96), EN and SL, NF4, one code path. BEHAVIOUR (gpt-4.1, random ~52% of S4 harmful gens; run budget exhausted): GaMS edit refused 100->5.6% EN / 6.7% SL; Gemma edit 99->70.3% EN / 95.3% SL (English-derived edit transfers fully in GaMS, barely in Gemma although Gemma's EN/SL harm-direction cosine is higher, 0.92 vs 0.83). Marker rule badly undercounts Gemma refusals (32.7% vs 70.3%). Second free judge (nemotron-3-ultra) kappa vs gpt-4.1 0.83 (refused) / 0.77 (6-way). UTILITY: 6 tasks x 250 frozen items x EN/SL, harness-replica scorer validated vs lm-eval (strings 100% identical, flag agreement 98.7/99.5%; ll bar fails only via harness bf16 rounding): macro change +0.13/+0.20 (GaMS EN/SL), +0.13/0.00 (Gemma), Holm p=1; all task deltas within 1.6 pts; FLORES dNLL <=0.002; no wrong-language/empty/malformed outputs; Gemma EN first-token KL uninformative (255/257 'Okay,'). MECHANISM: harm linearly decodable (held-out S4 AUROC >=0.996, not lexical/length). GaMS: frozen original probe collapses (0.998->0.60 EN/0.42 SL at L34, min 0.20 at L27) while refit stays 0.985/0.954; 71-73% of harm mean-difference energy on the frozen axis removed to ~0.1%, complement AUROC 0.985/0.955 -> re-encoding, not information loss. Gemma: frozen-axis separation halves equally in EN and SL from L28, yet behaviour changes only in EN -> axis compression does not explain the language asymmetry; late-layer axis rotation differs (cos 0.53 EN vs 0.83 SL). A2 (pre-registered): GaMS R_seq passes gate; slope ratio 0.36 EN / 0.42 SL -> EVIDENCE_LOSS label = decoupling of refusal from the ORIGINAL evidence axis while information stays decodable (changed mapping). Gemma R_seq fails gate EN; judged logistic also EVIDENCE_LOSS (flagged separation artefact). Gemma flips hit low-evidence items first (criterion-shift signature). EXPLORATORY dose-response (LoRA x f): Gemma SL needs ~2x edit strength (R_seq>0 harmful SL 98.8/77.4/46.3/7.0% at f=1/1.5/2/3 vs EN 90.3/45.1/24.5/12.8%); GaMS EN/SL move together. Bonus GaMS3-12B base: harm decodable (CV AUROC 0.99/0.96), complies with most harmful QA prompts. Outputs: method_out.json (8056 examples: S4 per item x lang x role with responses, labels, R_seq/R1, s_i, KL; S7 utility per item), results/analysis/tables.md + summary.json, per-item parquets, S5/S5X projections, r_prior npz, figures fig1-fig8, blinded review packet (PENDING). Audits: verify_numbers 80/80, audit_headline raw re-derivation identical with failing placebos. Caveats: n=2 models, one Heretic run each, NF4, MT Slovene, partial judge coverage.
Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5
</artifact>

<workspace_files>
README.md (19,766 bytes)
analyze.py (41,290 bytes)
audit_headline.py (4,767 bytes)
base_diag.py (7,486 bytes)
build_output.py (5,317 bytes)
common.py (8,153 bytes)
dose.py (6,294 bytes)
dose_judge.py (2,420 bytes)
engine.py (15,963 bytes)
figures.py (13,316 bytes)
freeze_protocol.py (5,727 bytes)
full_method_out.json (11,302,767 bytes)
judge.py (17,290 bytes)
mech.py (25,156 bytes)
mech_extra.py (10,117 bytes)
method.py (18,432 bytes)
method_out.json (8,976,397 bytes)
mini_method_out.json (219,516 bytes)
preview_method_out.json (194,056 bytes)
pyproject.toml (4,382 bytes)
readouts.py (6,922 bytes)
report_tables.py (18,529 bytes)
review_packet.py (4,128 bytes)
run_after_fill.sh (540 bytes)
run_chain1.sh (183 bytes)
run_chain2.sh (661 bytes)
run_dose.sh (230 bytes)
run_gpu.sh (474 bytes)
run_judge.sh (351 bytes)
run_judge2_fill.sh (351 bytes)
utility.py (16,998 bytes)
verify_numbers.py (9,123 bytes)
acts_primary/gams/S3_edit_L34.npy (49,766,528 bytes)
acts_primary/gams/S3_index.json (111,662 bytes)
acts_primary/gams/S3_orig_L34.npy (49,766,528 bytes)
acts_primary/gams/S4_edit_L34.npy (47,370,368 bytes)
acts_primary/gams/S4_index.json (334,739 bytes)
acts_primary/gams/S4_orig_L34.npy (47,370,368 bytes)
acts_primary/gams/S5_index.json (2,026,227 bytes)
acts_primary/gemma/S3_edit_L20.npy (49,766,528 bytes)
acts_primary/gemma/S3_index.json (111,662 bytes)
acts_primary/gemma/S3_orig_L20.npy (49,766,528 bytes)
acts_primary/gemma/S4_edit_L20.npy (47,370,368 bytes)
acts_primary/gemma/S4_index.json (334,739 bytes)
acts_primary/gemma/S4_orig_L20.npy (47,370,368 bytes)
acts_primary/gemma/S5_index.json (2,026,227 bytes)
configs/h100_ids.json (1,549 bytes)
configs/protocol_c1u.sha256 (84 bytes)
configs/protocol_c1u.yaml (4,108 bytes)
configs/split_verification.json (2,804 bytes)
configs/utility_sample_ids.json (154,021 bytes)
env/gpu.txt (677 bytes)
env/requirements.lock (3,144 bytes)
figures/fig1_utility_deltas.pdf (19,408 bytes)
figures/fig1_utility_deltas.png (95,785 bytes)
figures/fig2_layer_profiles.pdf (32,439 bytes)
figures/fig2_layer_profiles.png (457,932 bytes)
figures/fig3_frozen_vs_refit.pdf (22,513 bytes)
figures/fig3_frozen_vs_refit.png (145,932 bytes)
figures/fig4_a2_scatter.pdf (83,063 bytes)
figures/fig4_a2_scatter.png (468,663 bytes)
figures/fig5_kl_validity.pdf (20,543 bytes)
figures/fig5_kl_validity.png (105,260 bytes)
figures/fig6_readout_validity.pdf (14,586 bytes)
figures/fig6_readout_validity.png (68,907 bytes)
figures/fig7_drift_geometry.pdf (28,623 bytes)
figures/fig7_drift_geometry.png (306,604 bytes)
figures/fig8_dose_response.pdf (28,721 bytes)
figures/fig8_dose_response.png (275,252 bytes)
logs/analyze_after_delete.out (368 bytes)
logs/analyze_final.out (1,041 bytes)
logs/analyze_final1.out (469 bytes)
logs/analyze_test.out (888 bytes)
logs/base_diag.out (12,553 bytes)
logs/dl_base.out (1,012 bytes)
logs/dose_gams.out (13,054 bytes)
logs/dose_gemma.out (16,318 bytes)
logs/figures.out (297 bytes)
logs/final_status.txt (15 bytes)
logs/full_gams.out (62,681 bytes)
logs/full_gemma.out (57,916 bytes)
logs/judge.out (84,538 bytes)
logs/judge2.out (57,484 bytes)
logs/judge2_fill.out (539,644 bytes)
logs/judge_status.txt (193 bytes)
logs/mech_extra_gams.out (665 bytes)
logs/mech_extra_gemma.out (665 bytes)
logs/mech_gams.out (967 bytes)
logs/mech_gams.pid (5 bytes)
logs/mech_gemma.out (968 bytes)
logs/mech_mini.out (918 bytes)
logs/mini_gams.out (30,517 bytes)
logs/mini_gams.pid (5 bytes)
logs/mini_gams2.out (14,604 bytes)
logs/readouts_judge.out (2,090 bytes)
logs/run_chain1.out (0 bytes)
logs/run_chain2.out (0 bytes)
logs/run_gpu.pid (4 bytes)
logs/run_gpu_status.txt (305 bytes)
logs/timing_decision.json (856 bytes)
results/a2_synthetic.json (1,146 bytes)
results/audit_headline.json (2,515 bytes)
results/generation_validity.parquet (74,297 bytes)
results/judged_generations.jsonl (3,587,925 bytes)
results/metadata_extra.json (5,279 bytes)
results/native_review_packet_c1u.csv (66,267 bytes)
results/native_review_packet_c1u_KEY.csv (7,179 bytes)
results/s5_projections_gams.parquet (5,953,367 bytes)
results/s5_projections_gemma.parquet (4,785,912 bytes)
results/utility_items.parquet (641,966 bytes)
results/verify_numbers.json (12,443 bytes)
results/analysis/summary.json (139,309 bytes)
results/analysis/tables.md (20,086 bytes)
results/base_diag/base_diag.json (1,059 bytes)
results/base_diag/base_generations.json (25,333 bytes)
results/base_diag/base_layer_profile.npz (3,904 bytes)
results/dose/dose_gams.json (252,198 bytes)
results/dose/dose_gemma.json (249,577 bytes)
results/dose/dose_gens_gams.json (286,115 bytes)
results/dose/dose_gens_gemma.json (299,424 bytes)
results/gams/a2_items.parquet (126,754 bytes)
results/gams/checks.json (4,025 bytes)
results/gams/drift_geometry_gams.json (3,709 bytes)
results/gams/drift_geometry_gams.npz (17,414 bytes)
results/gams/edit_shift_items_gams.parquet (805,008 bytes)
results/gams/flores_edit.json (187,031 bytes)
results/gams/flores_orig.json (186,987 bytes)
results/gams/frozen_directions_gams.npz (647,576 bytes)
results/gams/harness_validation.json (4,504 bytes)
results/gams/harness_validation_items.json (675,266 bytes)
results/gams/kl_r1.json (270,064 bytes)
results/gams/layer_dirs_gams.npz (1,505,780 bytes)
results/gams/layer_profiles_gams.npz (22,760 bytes)
results/gams/mech_gams.json (13,240 bytes)
results/gams/r_prior_gams.json (7,040 bytes)
results/gams/r_prior_gams.npz (2,258,682 bytes)
results/gams/rseq_judge.json (370,992 bytes)
results/gams/rseq_markers.json (370,996 bytes)
results/gams/s4_scores.parquet (65,367 bytes)
results/gams/timings.json (294 bytes)
results/gams/utility_edit.json (1,461,195 bytes)
results/gams/utility_orig.json (1,461,105 bytes)
results/gemma/a2_items.parquet (121,876 bytes)
results/gemma/checks.json (3,919 bytes)
results/gemma/drift_geometry_gemma.json (3,551 bytes)
results/gemma/drift_geometry_gemma.npz (17,414 bytes)
results/gemma/edit_shift_items_gemma.parquet (723,722 bytes)
results/gemma/flores_edit.json (186,702 bytes)
results/gemma/flores_orig.json (186,718 bytes)
results/gemma/frozen_directions_gemma.npz (647,576 bytes)
results/gemma/harness_validation.json (4,496 bytes)
results/gemma/harness_validation_items.json (674,724 bytes)
results/gemma/kl_r1.json (257,270 bytes)
results/gemma/layer_dirs_gemma.npz (1,505,780 bytes)
results/gemma/layer_profiles_gemma.npz (22,760 bytes)
results/gemma/mech_gemma.json (13,372 bytes)
results/gemma/r_prior_gemma.json (4,661 bytes)
results/gemma/r_prior_gemma.npz (1,505,794 bytes)
results/gemma/rseq_judge.json (368,704 bytes)
results/gemma/rseq_markers.json (368,712 bytes)
results/gemma/s4_scores.parquet (65,367 bytes)
results/gemma/timings.json (288 bytes)
results/gemma/utility_edit.json (1,463,920 bytes)
results/gemma/utility_orig.json (1,463,885 bytes)
results/gens/gams_gens.json (2,958,893 bytes)
results/gens/gemma_gens.json (3,037,533 bytes)
results/judge/cost_log.jsonl (258,721 bytes)
results/judge/judge_queue.json (787,748 bytes)
results/judge/judged_generations.json (3,592,413 bytes)
results/judge/raw_calls.jsonl (258,729 bytes)
results/refs/refs_gams.jsonl (475,554 bytes)
results/refs/refs_gams.meta.json (1,563 bytes)
results/refs/refs_gemma.jsonl (468,322 bytes)
results/refs/refs_gemma.meta.json (1,494 bytes)
results_mini/gams/checks.json (4,025 bytes)
results_mini/gams/flores_edit.json (1,811 bytes)
results_mini/gams/flores_orig.json (1,807 bytes)
results_mini/gams/frozen_directions_gams.npz (647,576 bytes)
results_mini/gams/harness_validation.json (4,504 bytes)
results_mini/gams/harness_validation_items.json (113,838 bytes)
results_mini/gams/kl_r1.json (8,566 bytes)
results_mini/gams/layer_dirs_gams.npz (1,505,780 bytes)
results_mini/gams/layer_profiles_gams.npz (22,760 bytes)
results_mini/gams/mech_gams.json (10,331 bytes)
results_mini/gams/rseq_markers.json (11,593 bytes)
results_mini/gams/s4_scores.parquet (9,439 bytes)
results_mini/gams/timings.json (290 bytes)
results_mini/gams/utility_edit.json (48,462 bytes)
results_mini/gams/utility_orig.json (48,464 bytes)
results_mini/gens/gams_gens.json (92,436 bytes)
results_mini/refs/refs_gams.jsonl (14,886 bytes)
results_mini/refs/refs_gams.meta.json (1,133 bytes)
scratch/sleval_tree.json (10,643 bytes)
scratch/summary_before_acts_delete.json (139,162 bytes)
third_party/sleval_tasks/tasks_sl_sl_arc_sl_arc_challenge.yaml (77 bytes)
third_party/sleval_tasks/tasks_sl_sl_arc_sl_arc_easy.yaml (511 bytes)
third_party/sleval_tasks/tasks_sl_sl_hellaswag_sl_hellaswag.yaml (520 bytes)
third_party/sleval_tasks/tasks_sl_sl_hellaswag_utils.py (717 bytes)
third_party/sleval_tasks/tasks_sl_sl_openbookqa_sl_openbookqa.yaml (489 bytes)
third_party/sleval_tasks/tasks_sl_sl_piqa_sl_piqa.yaml (539 bytes)
</workspace_files>

<reproducibility_spec>
Write `reproducibility.md` in your workspace with COMPLETE step-by-step instructions to reproduce your exact results on Ubuntu — describe what you ACTUALLY ran, not an idealized version. Cover: (1) getting this artifact: your workspace is published as one folder of a public GitHub repository, so start from a clone of that repository and `cd` into the folder; (2) system packages, the Python version, venv creation, and the exact library versions you actually installed, pinned (match pyproject.toml); (3) any data/model/checkpoint downloads plus env vars or API keys needed, by NAME only, never values; (4) the exact commands you ran, in order, with seeds, configs, hardware used (GPU type, VRAM) and approximate runtime; (5) which output files and numbers a reader should get, and where they appear in the paper. PORTABLE PATHS: a reader has only the published repository, never this server, so every path in this file, in `restore.sh` or any install script, and in your code must be RELATIVE to your workspace (in code, anchor it on `Path(__file__)`), never an absolute `/ai-inventor/...` path. Read an input another artifact produced through ONE relative constant or environment variable and name that artifact by its id; the repository publishes it as a sibling folder. An input the user uploaded is private and is not published: say so, and say how a reader supplies their own copy. This is a REQUIRED output file, like the others above.
</reproducibility_spec>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read the artifact's workspace `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5` (listed below): the entry-point code, any README, pyproject.toml or requirements file, the configs, the seeds set in the code, the results and output JSON files, and the data files. Open the files; do not guess their contents from their names. Do not run, install or modify anything.
TODO 2. Write `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/reproducibility.md` following the specification below, which is the one the artifact's own agent was given. Take every command, file name, version, seed and number from the files you read. Where the workspace does not record a point the specification asks for, state that it was not recorded rather than inventing it.
TODO 3. Re-read `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5/reproducibility.md` against the workspace: every file it names exists, every command matches the code's real arguments, every number matches the results files. Fix anything that does not. Then return the structured output.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ReproducibilityDocExpectedFiles": {
      "description": "The one file the backfill writes.",
      "properties": {
        "reproducibility": {
          "description": "Path to reproducibility.md. Example: 'reproducibility.md'",
          "title": "Reproducibility",
          "type": "string"
        }
      },
      "required": [
        "reproducibility"
      ],
      "title": "ReproducibilityDocExpectedFiles",
      "type": "object"
    }
  },
  "description": "Structured output of the reproducibility.md backfill agent.",
  "properties": {
    "summary": {
      "description": "Which workspace files the instructions were derived from, and which of the spec's points the workspace did not record.",
      "maxLength": 2000,
      "minLength": 50,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/ReproducibilityDocExpectedFiles",
      "description": "All output files you created. Must include reproducibility.md."
    }
  },
  "required": [
    "summary",
    "out_expected_files"
  ],
  "title": "ReproducibilityDoc",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.

i want a reproducible bilingual study of refusal suppression in google/gemma-3-12b-it and cjvt/GaMS3-12B-Instruct, with room for a genuine scientific discovery. compare each original model with one Heretic-abliterated version, evaluating all four checkpoints in English and Slovene. establish the safety–utility trade-offs, then investigate what explains them internally.

the attached research plan defines the intended study and supplies literature leads. verify its factual claims and references. this prompt governs execution: keep the core comparison fixed, but choose the mechanistic methods and discovery direction yourself. do not assume the expected findings are true.

Gemma-IT is a same-family, same-size aligned reference, not the direct training parent of GaMS-Instruct. endpoint differences cannot establish what Slovene continual pretraining, instruction tuning, or the small safety-training set caused.

step 1 - explore and establish feasibility. load both original models, pin revisions, verify their official tokenizers and chat templates, and inspect behavior and activations on a small development set in both languages. check coherent output, baseline refusal, and hidden-state extraction. use text-only inputs and comparable precision and inference settings; record unavoidable differences. inspect where the models behave similarly and where they differ, without committing to a mechanism. estimate the compute needed before scaling up. use separate smoke-test data and keep final evaluation untouched. if an edit fails or destroys language ability, investigate and report the failure rather than quietly substituting another model or calling incoherence successful refusal suppression.

step 2 - find the scientific opening. develop 5–7 distinct, falsifiable explanations or research directions from the pilot and the literature. search beyond refusal-vector papers, including multilingual representations, decision calibration, causal intervention, and capability interference. actively try to disprove novelty by reading the closest primary sources. select one or two promising directions for deeper experiments.

possible starting points: does cross-language intervention transfer depend on something that direction cosine misses? can we distinguish loss of harmfulness information from a changed mapping between that information and refusal? does interference with language-relevant computation explain different utility costs? these are suggestions, not required findings or an exhaustive menu. replace them if the evidence points somewhere better.

for each selected hypothesis, state its prediction, strongest competing explanation, simplest baseline, and a result that would falsify it. discovering that familiar geometry fails to predict behavior can be valuable if you establish its boundary. merely applying Heretic to GaMS, observing EN–SL vector similarity, or finding separable harmfulness after refusal declines is insufficient by itself as a novelty claim. if an exploratory hypothesis fails the novelty check, replace that hypothesis while preserving the core study.

step 3 - freeze the data and intervention protocol. separate Heretic construction/optimization data, mechanistic development data, held-out mechanistic validation, and final behavioral evaluation. keep translations, paraphrases, and harmful/harmless counterparts from the same semantic source together when splitting. audit overlap by source and meaning, not only exact strings. Heretic's default sources and Semantic-Harmful/Semantic-Harmless may overlap; those pairs cannot automatically serve as independent validation.

create one main Heretic checkpoint per original model using the same pinned version, English prompt source, comparable objectives, and equal search budgets. choose checkpoints by a declared development-only rule balancing refusal reduction and harmless divergence. evaluate that same English-derived edit in both languages. a community Gemma edit is a sanity reference, not a substitute for the matched main intervention. record configurations, seeds, selected trials, precision, and checkpoint hashes. distinguish differences in achieved optimization from intrinsic model properties. additional seeds or edit strengths may support a focused robustness analysis, but keep them separate from the four core checkpoints.

step 4 - measure behavior and utility. use the official NASK-PIB/RefusEU evaluation data for English and Slovene, following its published scoring protocol where reproducible. report harmful compliance/attack success, refusal, and language consistency separately. refusal and harmful compliance are not complements: ambiguous, irrelevant, malformed, and empty outputs need explicit treatment. include a small independent benign safety-adjacent set to measure over-refusal. a model that refuses everything, or cannot answer coherently, must not look successful.

use the same frozen judge and rubric across conditions, with model identity hidden. check scoring sensitivity using a second independent judge on a stratified sample. prepare a blinded EN/SL sample for human review; if qualified human review is unavailable, mark it pending and state the limitation instead of claiming it happened.

for utility, use Slovenian LLM Eval and the corresponding English tasks: ARC-Challenge, BoolQ, HellaSwag, OpenBookQA, PIQA, and Winogrande. report individual tasks and their macro-average, emphasizing original-to-edited changes within each language. also measure harmless divergence on held-out inputs, wrong-language output, repetition, and output validity. Heretic's optimization KL alone is not independent evidence of preserved utility.

do not assume RefusEU examples sharing an ID are exact translations, or that EN and SL benchmark difficulty is identical. verify correspondence before making paired cross-language claims. use a separate faithful EN/SL contrast set for controlled language comparisons. translate only missing material, preserve semantic IDs, document translation checks, and distinguish automated checks from native-speaker review. published model-card scores are context and sanity checks; measure the four checkpoints yourself under the same protocol.

step 5 - connect representations to behavior. complete the mechanistic core: layer-wise bilingual harmful/harmless direction characterization in both originals, and held-out harmfulness separability before and after Heretic. choose and justify activation locations and token positions. select layers, probes, and hyperparameters on development data only.

control for topic, wording, prompt length, language identity, and response leakage. decoding harmfulness from generated refusal text is not evidence that a pre-response harmfulness signal drives refusal. compare a frozen original-model probe with appropriately cross-validated probes refitted after editing where useful: failure of the frozen probe can reflect representation drift rather than information loss. do not interpret raw cross-model vector cosine as shared mechanism without establishing comparable coordinates.

relate internal measurements to actual behavioral changes in each language. high probe accuracy establishes decodability, not causal use. a harmful-minus-harmless direction is only refusal-associated until interventions support a stronger interpretation. changes in a direction directly targeted by Heretic are expected and cannot alone carry the discovery.

step 6 - pursue the strongest explanation. use the freedom from step 2 to design the smallest decisive experiment. where justified, extract EN- and SL-derived directions and test the source-language × evaluation-language transfer matrix within each model. choose intervention locations and strengths on development data, and include no-op and matched random-direction controls plus benign utility checks. keep these activation interventions separate from the main Heretic comparison.

you may instead pursue subspaces, layer-specific interventions, representation-to-action coupling, or another approach supported by the pilot. the goal is a result that distinguishes competing explanations and predicts something on untouched data. use held-out semantic categories or an independent prompt source to challenge it. explain what survives, what breaks, and where the claim stops. prefer one well-tested insight over a large collection of loosely connected metrics. preserve the behavioral and mechanistic core even if every novelty candidate fails.

step 7 - test the claims honestly. freeze primary outcomes and confirmatory analyses before final evaluation. report original-to-edited effects for each model and language, with effect sizes and 95% confidence intervals. compare those changes across models and languages without attributing them to a specific training stage.

state the resampling and aggregation units. pair outputs on the same prompts and cluster translations/paraphrases by underlying semantic item; use cross-language pairing only where correspondence is established. four checkpoints, many layers, or many prompts do not create many independent model families. prompt-level uncertainty also does not measure variation across Heretic optimization runs. account for searching across hypotheses and layers, separate exploratory from confirmatory results, and state when sample sizes cannot resolve a difference. if resources require subsampling, freeze a stratified sample before viewing results and narrow the claims accordingly.

bonus - examine cjvt/GaMS3-12B as a bounded pre-instruction diagnostic. test harmfulness separability and a small EN/SL behavior sample with appropriate base-model formatting. do not compare its raw refusal rate with chat models as if the tasks were identical. only attempt base abliteration if refusal-like behavior is reproducible, the intervention has an interpretable target, and it does not jeopardize the main study. intermediate training checkpoints and no-safety training controls belong to a later extension unless already available.

deliver a reproducible repository and a paper grounded in executed experiments: pinned dependencies, split manifests, configurations, per-example outputs and scores, analysis scripts, and figures covering the four checkpoints in both languages. distinguish observations, interpretations, failed hypotheses, and unexecuted proposals. recompute every headline number from saved results and reconcile the abstract, tables, figures, and conclusions after the final audit. the discovery may change as evidence accumulates; the final paper must reflect the strongest claim that actually survives.
````

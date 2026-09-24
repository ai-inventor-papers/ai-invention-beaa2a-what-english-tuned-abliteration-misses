<!-- CARRIED TEXT. Where this file says `results/<name>` it means the DEPENDENCY's file of that name
(artifact art_sZ5w0yoY9o6L, iter_4/gen_art/gen_art_research_1/results/<name>). The ones this artifact
reuses are copied into this workspace as `results/_dep_<name>`; the rest stay at that path. -->

# Canonical stopping-points block — write once, reuse verbatim

Every claim in the paper that is bounded by scope is bounded by **this** block. It is reproduced verbatim wherever a limit is needed; it is not re-worded per section. Every line is an OBSERVATION about this run's own scope and resolves to a path. Paths are relative to the run's `3_invention_loop/` directory. (The dependency's copy of this line gave an absolute server path; it is replaced here because this workspace is published.)

---

## Paste-ready block

> **What bounds these claims.** Two sibling checkpoints of one architecture (`google/gemma-3-12b-it` pinned at 96b6f1ec and `cjvt/GaMS3-12B-Instruct` pinned at 1d0b27af), plus one community-abliterated Gemma reference and outside-family checkpoints (`Qwen/Qwen3-8B`, `mistralai/Mistral-7B-Instruct-v0.3`; the planned `EuroLLM-9B-Instruct` is gated and returned HTTP 403, `iter_3/gen_art/gen_art_experiment_12/results/load_log.json`). Two checkpoints are two units, not a population: every cross-checkpoint statement is descriptive, and nothing is attributed to Slovene continual pretraining, instruction tuning, or any safety-training stage, because no training stage was varied. The matched-energy, matched-layer-count panels use one architecture and one non-English language (Slovene); German and Lithuanian appear only in the outside-family arm. One or two optimiser seeds were run, so no run-to-run variance claim is made anywhere, and prompt-level bootstrap intervals are never presented as optimiser variance. All 12B checkpoints load in 4-bit NF4 with bf16 compute throughout, with a single bf16 control cell used to break the precision confound once rather than assume it away. All Slovene material other than the official RefusEU rows and human-translated FLORES+ is machine-translated with automated back-translation QC only (mean back-translation chrF++ 76.6–80.1 per set, `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md`); **no native-speaker review has been carried out anywhere in this run.** Five blinded review packets are prepared and PENDING: `iter_2/gen_art/gen_art_experiment_4/results/human_packet/packet.csv` (n=200, 100 SL / 100 EN), `iter_2/gen_art/gen_art_experiment_5/results/native_review_packet_c1u.csv` (n=120), `iter_1/gen_art/gen_art_dataset_1/data/native_review_packet.csv` (n=250 translation adequacy), `iter_1/gen_art/gen_art_experiment_1/results/sl_label_sample.json` (n=40, labelled by the artifact executor, **not** a native speaker) and `iter_2/gen_art/gen_art_experiment_4/results/executor_audit.json` (n=30, executor check). Consequently every behavioural number is a range across automated judges, and every cross-lingual claim is bounded by machine-translated material with automated QC. RefusEU English and Slovene rows sharing a row_id are **not** translations (0 of 1,400 pairs graded T, `iter_1/gen_art/gen_art_dataset_1/data/reports/refuseu_correspondence.json`), so paired cross-language claims use only the separately translated S5X contrast set. The related-work positioning is a bounded, prioritised lookup accessed 2026-09-24 with its queries logged (`results/search_log.md`); it is "closest found", not exhaustive.

---

## Per-line provenance

| bound | value | path |
|---|---|---|
| anchor checkpoint + revision | `google/gemma-3-12b-it` @ 96b6f1ec | iteration-4 strategy `iter_4/gen_strat/gen_strat_1/.terminal_claude_agent_struct_out.json` (pins), realised in each pod's `env_freeze.txt` / `gate0_pins.json` |
| sibling checkpoint + revision | `cjvt/GaMS3-12B-Instruct` @ 1d0b27af | same |
| editing tool | Heretic SHA 3521f864 (keyword scorer era) | same; tool state dated 2026-09-24 in `results/neighbour_table.md` N27 |
| outside families actually used | Qwen3-8B, Mistral-7B-Instruct-v0.3 | `iter_3/gen_art/gen_art_experiment_12/results/load_log.json` |
| languages, matched panels | EN + SL only | `iter_3/gen_art/gen_art_experiment_9/`, `iter_3/gen_art/gen_art_experiment_10/` |
| languages, outside family | EN, SL, DE, LT | `iter_3/gen_art/gen_art_experiment_12/results/report_tables.md` |
| seeds | 1–2 optimiser seeds | `iter_3/gen_art/gen_art_experiment_11/results/seed2_analysis.json` |
| precision | 4-bit NF4 with bf16 compute; one bf16 control cell | strategy pins; pod `env_freeze.txt` files |
| translation provenance per set | per-set method counts and back-translation chrF++ | `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md` (translation provenance table) |
| native review | PENDING, 5 packets | `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md` |
| judge validation | automatic judges certified against a frontier-model subsample, not against human labels | `iter_3/gen_art/gen_art_experiment_9/results/judge_certification.json`; `iter_3/gen_art/gen_art_evaluation_1/results/judge_sensitivity.csv` |
| RefusEU correspondence | 0 of 1,400 id-matched pairs are translations | `iter_1/gen_art/gen_art_dataset_1/data/reports/refuseu_correspondence.json` |
| positioning scope | 24 discovery queries, ~40 exact extractions, 2026-09-24 | `results/search_log.md` |

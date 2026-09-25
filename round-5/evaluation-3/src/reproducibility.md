# Reproducing the final audit

This is exactly what was run to produce `eval_out.json`, `results/` and `figures/`. The audit only reads
completions and labels that earlier artifacts saved. It loads no model and generates nothing, so no GPU is needed.
The machine used (Ubuntu, 48 CPUs, NVIDIA RTX A4500 20 GB) was idle on the GPU the whole time.

## 1. Get the artifact and its inputs

The workspace is published as one folder of a public GitHub repository:

```sh
git clone <repository-url>
cd <repository>/<this-folder>        # the folder holding eval.py
```

Every input is read relative to ONE root, the directory holding `iter_*/gen_art/<artifact>`. The default is three levels up
from this folder (`../../..`), which matches the run layout `3_invention_loop/iter_5/gen_art/<this-folder>`. If the
repository lays the artifacts out differently, set:

```sh
export AUDIT_INPUT_ROOT=<dir containing iter_1/, iter_2/, iter_3/, iter_4/>
```

Inputs are named by artifact id. The path under the root follows each id:

| artifact id | path under the root | what is read |
|---|---|---|
| art_qdUCJWbc5kHh | `round-1/dataset-1/src` | `data/splits/S1_heretic.jsonl` (Heretic construction prompts, disjointness check) |
| art_m6pglf516e2r | `round-2/experiment-4/src` | `full_method_out.json` (4,800 per-item generations with judge and guard labels), `protocol.yaml` |
| art_a4VkEvYRquBO | `round-2/experiment-5/src` | `results/judged_generations.jsonl`, `results/utility_items.parquet`, `results/analysis/tables.md` |
| art_0XmNBGkzsJc_ | `round-3/experiment-11/src` | `results/eval_gen/*.jsonl`, `results/judge_out/*.jsonl`, `results/inloop_gens.jsonl`, `results/label_pool.parquet`, `results/miscalibration_table.csv`, `scorer/refusal_clf.joblib`, `third_party/heretic/.../partial_aware_refusal.py` |
| art_NpZ_nW6qgSKD | `round-4/experiment-13/src` | `results/per_item.csv`, `results/analysis.json`, `configs/frozen_predictions.json` |
| art_bxpIbe7-nSvR | `round-4/experiment-14/src` | `results/per_item.parquet`, `results/cells.csv`, `results/analysis_summary.json`, `configs/frozen_predictions.json` |
| art_F46S3uP80BUa | `round-4/experiment-15/src` | `results/per_candidate.csv`, `results/analysis.json`, `results/reselection_table.csv`, `third_party/heretic/src/heretic/scorers/keyword_rate.py` (pinned Heretic marker list) |
| art_hBuck7q0dnxG | `round-4/evaluation-2/src` | `results/asr_summary.json`, `results/quant_confound.json`, `results/gpt41_*_labels.jsonl` |
| (report draft) | `iter_4/gen_report_text/gen_report_text` | `paper_draft.md`, `.terminal_claude_agent_struct_out.json` (the audited draft) |
| (run index) | `../iterations.jsonl` (one level above the root) | artifact id → workspace map, used only by the citation lint and the ledger |

No user-uploaded file is read.

## 2. System, Python and libraries

* Ubuntu with `uv` installed; Python 3.12.14.
* Exact versions are pinned in `pyproject.toml` (direct dependencies). The full environment (64 packages) is in
  `requirements.lock`, from `uv pip freeze`. torch is NOT installed (transformers only loads the tokenizer).

```sh
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.lock
```

## 3. Downloads, environment variables, keys

* Tokenizer files only for `google/gemma-3-12b-it` at revision `96b6f1eccf38110c56df3a15bffe176da04bfd80` (gated model:
  set `HF_TOKEN`). They go into the HF cache (`HF_HOME` / `HF_HUB_CACHE`). `eval.py` downloads them on first use if
  missing. For `rederive.py`, download them first:
  `uv run python -c "from huggingface_hub import snapshot_download as s; s('google/gemma-3-12b-it', revision='96b6f1eccf38110c56df3a15bffe176da04bfd80', allow_patterns=['tokenizer*','special_tokens_map.json'])"`
* `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`: needed only by the optional `label_gpt41.py`. In this run the key
  returned HTTP 403 (platform daily limit) on the first call, and $0.00 was spent (`results/gpt41_key_block_evidence.txt`).
  No number in `eval_out.json` depends on a label bought here.

## 4. Commands actually run, in order

```sh
uv run label_gpt41.py --limit 2 --conc 2   # probe only: blocked (403), $0.00, writes results/gpt41_purchase_attempt.json
uv run eval.py --boot 2000                 # ~2 min; cluster bootstrap B=2000, seed 20260924 -> eval_out.json, full/mini/preview_eval_out.json, results/*
uv run report.py                           # -> results/AUDIT_REPORT.md
uv run figures.py                          # -> figures/fig1_objective_agreement.{pdf,png}, figures/fig2_measurement_bias.{pdf,png}
uv run rederive.py                         # ~15 s; independent stdlib re-derivation + permutation placebos -> results/rederive.json
# then the pipeline's JSON formatter regenerated full_/mini_/preview_eval_out.json from eval_out.json and all four
# files were validated against the exp_eval_sol_out schema (PASSED)
```

`eval.py --mini` (B=200) was used during development only. The first attempted `label_gpt41.py` run also hit the 403.
Results are deterministic: fixed seeds, no sampling, and no model inference.

## 5. What you should get

* `eval_out.json` → `metrics_agg`: `n_claims_checked` 121, `n_claims_pass` 107, `n_discrepancies_found` 14,
  `kappa_keyword_heldout_edited_en_qwen` 0.021, `kappa_keyword_heldout_edited_sl_qwen` 0.0 with
  `keyword_positive_rate_heldout_edited_sl` 0.0 (the rater never fires), `selfire_keyword_{gemma,gams}_n_le_10` 0 / 0,
  `guard_safe_nonrefused_gap_gemma_edit` 0.2314, `n_bias_cells_same_order` 15 / `_opposite_order` 1 of 21,
  `exp13_pooled_en` −0.6875, `exp13_pooled_sl` −0.3771, `exp14_spearman` −0.9032, `n_citations_unresolved` 9.
* `results/rederive.json`: 14/14 checks match `eval.py`, and all permutation placebos behave as required. Shuffled-label
  kappa nulls centre on 0. The edited-EN keyword κ is NOT distinguishable from that null (p = 0.37), which is the
  blindness claim. The SL-EN guard-safe gap falls outside its language-shuffle null (p < 0.001). The exp14 ρ falls
  outside its O-permutation null (p < 0.005).
* `results/AUDIT_REPORT.md`, sections 1–12. The paper's measurement section (keyword objective blindness, per-checkpoint
  kappa table, measurement-bias table, guard-safety of non-refusals) and its corrections/erratum list (section 3 of the
  report) take their numbers from here. Figures 1–2 back those two sections.

## What is independently re-derived and what is not

Re-derived through a separate code path (`rederive.py`): the four held-out keyword kappas; the Gemma (raw in-loop) and
GaMS3 keyword floors; the Gemma-edit guard-safe non-refusal gap; the S5X refusal and guard-ASR gaps for both edits; the
exp13 pooled EN/SL contrasts; the exp14 Spearman. Computed only in `eval.py` (single code path): bootstrap CIs, the
per-checkpoint RefusEU kappas, the exp11 arm tables, the exp13 per-group, Qwen3-8B and Spearman(O) values, the exp14 ladder
and bands, the exp5 T1 rates, the ledger, the lint and the scope table. Values marked `SUMMARY_FILE_MATCH` in
`results/claim_registry.csv` are read from an earlier artifact's summary file, not recomputed from per-item data.

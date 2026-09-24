# Reproducing evaluation_iter3_dir5 (audit + judge sensitivity)

This is what was actually run, on Ubuntu (Linux 6.8), CPU only: 4 cores, no GPU used. No model is loaded and no text is generated. The whole rebuild takes about 1.5 minutes.

## 1. Copy the artifact
```bash
cp -r gen_art_evaluation_1 ~/work/ && cd ~/work/gen_art_evaluation_1
```

**Inputs are read by absolute path.** The scripts read the seven dependency workspaces by absolute path under `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/`. This is set in the `LOOP` constant of `scripts/lib.py` (and in `scripts/verify_headlines_indep.py`). If that tree lives elsewhere, edit those constants.

**Input files.** Every input file used is listed with its sha256 in `results/source_inventory.json`. The main ones:
- iteration 1, experiment 1: `results/eval/*.json`, `results/trials_*.csv`, `efficiency.json`, `a3_screen.json`
- iteration 1, experiment 3: `results/judged_generations.json`, `analysis_summary.json`, `margin_decomposition_exploratory.json`, `verify_numbers.json`
- iteration 2, experiment 4: `results/gen`, `judge`, `judge_local`, `autoscore` and `guard/official_labels.jsonl`, plus `frozen_samples.json` and `protocol.yaml`
- iteration 2, experiment 5: `results/judged_generations.jsonl`
- iteration 2, experiment 6: `results/judged_generations.json`, `analysis_results.json`, `panel_edits.jsonl`, `repro_check.json`
- iteration 2, experiment 7: `protocol/frozen_predictions.json`, `results/analysis.json`, `rederive.json`, `validity/judged.json`, `judged_api_orig.json`, `panel/edits/*.json`
- iteration 2, experiment 8: `results/per_item.parquet`, `results/{gemma,gams3,community}/gens/*.json`, `analysis_summary.json`, `audit_headline.json`, `report_tables.md`
- dataset 1: `data/splits/*.jsonl`, the review packets, `data/provenance/heretic_3521f864_config.default.toml`
- the draft under audit: `iter_2/gen_report_text/gen_report_text/paper_draft.md`

## 2. Environment
- System: Ubuntu with `uv` installed. No system packages are needed beyond a C runtime.
- Python: 3.12.14.
- Create the environment:
  ```bash
  uv venv .venv --python=3.12
  uv pip install --python=.venv/bin/python -r requirements.lock
  ```
- The exact versions are pinned identically in `requirements.lock` and `pyproject.toml`: numpy 2.1.3, pandas 2.2.3, pyarrow 18.1.0, scipy 1.14.1, matplotlib 3.9.3, pyyaml 6.0.2, loguru 0.7.3, aiohttp 3.11.11, plus their transitive dependencies.
- Figures use the house-style helpers of the aii-data-fig-gen skill, imported from `/ai-inventor/.claude/skills/aii-data-fig-gen/scripts`.

## 3. Downloads, environment variables, keys
- No downloads, models or checkpoints are needed.
- The main pipeline needs no API keys.
- The optional script `scripts/s11_topup.py` reads `OPENROUTER_API_KEY` and `OPENROUTER_BASE_URL`. In the recorded run every call returned HTTP 403 `aii_run_budget_exhausted`: 0 labels, $0 spent. Its output is `results/topup_gpt41_BLOCKED_no_labels.jsonl` and `results/topup_cost.json`. It is NOT part of the rebuild.
- The novelty lookups in `results/novelty_raw/`, `novelty_table.{md,json}` used the aii-web-tools fetch/grep scripts once, on 2026-09-24. Their raw outputs are saved; they are not re-run by the pipeline.

## 4. Commands, in order
Run `./run_all.sh`, or equivalently `.venv/bin/python eval.py`. The stages are:
1. `s01_labels.py`: builds `results/labels_long.parquet` (61,130 labels) and `source_inventory.json`.
2. `s02_iter1.py`: iteration-1 table, swap McNemar and bootstrap, 13.4×, A3.
3. `s03_judges.py`: judge sensitivity, agreement, keyword miscalibration, gap range, exp8 per-judge split.
4. `s04_claims.py`: claims registry (99 claims).
5. `s05_panels.py`: exp7 frozen predictions and slopes, exp6, exp3, exp8 F-block, exp4 and exp5 extras.
6. `s06_ledger.py`: dead-end ledger, pending human review, translation provenance.
7. `s07_placebos.py`: placebos P1-P6.
8. `s08_assemble.py`: `corrected_numbers.json`, `audit_log.json`, `report_repairs.md`, `judge_sensitivity.md`, `headline_metrics.json`.
9. `s09_figures.py`: `figures/fig_{gap_forest,judge_stack,kappa_inflation}.{pdf,png}`.
10. `s10_eval_out.py`: `eval_out.json`.
11. `verify_headlines_indep.py`: independent raw-file re-derivation of 10 headline numbers, plus 2 placebos (`results/verify_headlines_indep.json`).

Then generate the full/mini/preview files:
```bash
<aii-json venv python> <aii-json>/scripts/aii_json_format_mini_preview.py --input eval_out.json
```
This writes `full_`/`mini_`/`preview_eval_out.json`.

**Seeds.** Every bootstrap and permutation uses seed 20260924; B = 2000 unless stated otherwise (1000 for per-cell CIs and placebos). The one exception is the exp7 slope bootstrap, which uses seed 42 to mirror the artifact. The outputs are deterministic, and a rerun reproduced every headline value exactly.

## 5. What you should get
Headline numbers are in `results/headline_metrics.json`, which is copied into `eval_out.json` under `metrics_agg`.

**Audit accuracy**
- 167 draft numbers checked: 137 match, 8 mismatch, 12 misdescribed, 6 untraceable.
- Mismatch rate 0.055; 2 sign-reversed conclusions.
- 19 of 99 claims are JUDGE_SENSITIVE.

**Judge agreement (exp4, gpt-4.1 vs Qwen, binary)**
- κ .913 pooled vs .779 within edited checkpoints (inflation .133); AC1 within edits .908.

**Gemma SL−EN gap**
- Strict (refused only): +0.22 to +0.71. All strict CIs lie on the same side of 0.
- Broad (refused + partial): −0.04 to +0.37.
- S5X, Qwen: strict +0.69, broad +0.23.

**Keyword proxy:** FP share on gemma_edit EN is .761.

**Placebos:** 6/6 pass.

These numbers feed the paper's measurement section: `results/report_repairs.md` sections (1)-(10) hold the paste-ready corrected tables, and the figures are the gap forest, the judge stack and the κ-inflation plot.

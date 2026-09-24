# Gemma P1 edit panel: what English refusal traits miss in Slovene

Random-edit panel on **google/gemma-3-12b-it@96b6f1ec** (bitsandbytes NF4, bf16 compute), with **Heretic 3521f864** abliteration.
The question: when English-derived Heretic edits are applied, does English (EN) behaviour on one item half predict
Slovene (SL) behaviour on the other half as well as it predicts English? If the answer is no, what explains the
language-specific residual?

Every edit is rebuilt with Heretic's own `Model.abliterate()` on the iteration-1 English refusal directions. Each is
then scored teacher-forced in EN and SL on the frozen S3 DEV halves A and B. All numbers below are recomputed from
`results/analysis.json` (see *Results*).

__RESULTS__

## What was done (protocol)

* **Edits.** E0 is journal trials 0-59: the 60 TPE-startup random draws, identical to the GaMS panel's.
  `edits/E0_redraw_certificate.json` shows that `RandomSampler(seed=20260923)` reproduces them exactly (max diff 0).
  E_TPE is journal trials 60-115 (held out; includes the core edit, trial 96), trimmed to trial 96 plus the last 40.
  E1 is fresh draws from Heretic's priors with seed 20260925, using the parameter-suggestion block copied verbatim
  into `common.py`. E_R (seed 20260924) was never reached. Trial 96 rebuilt through `abliterate()` matches the saved
  adapter to max |ΔBA| = 6.1e-8 (`results/setup_checks.json`).
* **Traits** are item-level differences versus the original, per language and half:
  * **R_seq**: mean per-token log p(24-token refusal reference) minus log p(24-token compliance reference), on harmful
    JBB items.
  * **R1**: first-token log-sum-exp of the refusal prefix minus that of the compliance prefix.
  * **Rb**: R_seq on the benign twins.
  * **K**: log mean KL(p_orig ‖ p_edit) on the original's 32-token Dolly continuations.
  * **N**: FLORES NLL shift.
  * **M**: shift in the length-normalised MC gold margin.
* **Covariates:**
  * **P**: removal along r_prior (a refused-vs-complied direction on harmless prompts, orthogonalised against d_EN,
    at layer l_P = 33).
  * **H**: removal along d_EN, at l_H = 24.
  * **D**: exposure, i.e. the per-token LoRA output energy on Dolly response tokens.
  * **b1**: direction-cosine transfer.
  * **b2**: a language-identity entanglement analogue.
  * **b3**: kernel mass per layer band.
  * **Ω**: overlap with the LSAR subspace (k = 8).
* **References.** Refusal references are the original's judged-refused outputs; failing that, the per-language
  canonical opener. Compliance references are, in order of preference: GaMS3 + its core edit (trial 88), judged
  complied; else the Gemma original's complied output; else the canonical compliance opener. The source of every
  row is in `references/refs.json` (sha256 in `references/refs.sha256`).
* **Frozen before any edit was scored:** `protocol/frozen_predictions.json` (sha256 in `protocol/protocol_hash.txt`),
  covering the learner, folds, bootstrap, collapse rule, trim ladder, validity-edit rule and gates.
* **Analysis.**
  * Gap_t = R2*(EN_A→EN_B) − R2*(EN_A→SL_B), with R2* = CV-R2 / Spearman-Brown ceiling. The frozen learner is
    HistGradientBoosting, with 5-fold edit CV, halves swapped and averaged.
  * The bootstrap is two-level (edits × semantic items; the same item draw for EN and SL).
  * Also computed: B (parameter partial R²) with a stratified permutation test, SIMEX, disjoint-half and stratum
    stability, a margin-matched Gap plus a mixed model, the carrier regression (P vs b1+b2+b3+Ω+D), out-of-sample
    forecasts with conformal 90% PIs, bilingual reselection, and the silent-failure rate.

## Deviations (all recorded in the outputs)

1. **API judge blocked.** OpenRouter returned HTTP 403 (daily key limit) until 00:00 UTC. It then judged the original's
   440 generations with gpt-4.1 ($0.37), after which the run-wide phase budget was exhausted by the whole run
   (`results/api_budget_block.json`).
   * References, r_prior and the validity gate therefore use a **local judge**: the original gemma-3-12b-it with the
     frozen iteration-1 gpt-4.1 rubric.
   * On the original's 440 generations it agrees with gpt-4.1 on refused/not-refused for 98.2% (κ = 0.96).
   * Against 365 iteration-1 gpt-4.1 labels it reaches κ_refused = 0.67.
2. **Hardware change mid-panel.** The session was interrupted and resumed on an **NVIDIA L4**; the first 57 E0 edits
   and the original zero point ran on an **RTX 4090**. Per-edit time rose from 46 s to 152 s. In response:
   * every row carries `device`;
   * each edit's zero point is the original scored on the same device with the same trim
     (`ORIG_TRIM`, `ORIG_FULL_L4`, `ORIG_TRIM2_L4`);
   * E0_000 was re-scored on the L4 (`REPRO_E0_000_L4`);
   * the frozen trim ladder was re-applied, unchanged, with the L4 timings
     (`protocol/trim_decision_v2_hardware.json`: FLORES 120, MC 80 (task-balanced), Dolly 70, E_TPE = trial 96 + the
     last 40). Every trait uses the items common to all edits.
3. **Fitted set < 150.** The fitted set is E0 + E1, non-collapsed, and ended below the pre-registered floor, so C2
   (and every P-a..P-d verdict) is **exploratory**, per the protocol's own rule.
4. **Bootstrap B = 500 instead of 1000.** The container's CPU quota is 5 cores (cgroup cfs quota). Permutations stay
   at 1000.
5. **Double BOS.** Heretic 3521f864 tokenizes the rendered Gemma template with special tokens, which produces a double
   BOS. This is inherited unchanged, so the edits are scored exactly as Heretic optimised them.
6. **T2 keyword re-score.** Trials 0, 1 and 2 match the journal within 1/100; trial 96 gives 74 vs 69, with
   weight-identical adapters. The difference is generation numerics, since Heretic's journal was scored in a different
   process and batch.

## Layout

| path | what it is |
| --- | --- |
| `method.py` | entry point: runs the whole pipeline below in order (resumable) |
| `common.py` | paths, frozen data loaders, and a **verbatim** copy of Heretic 3521f864's parameter-suggestion block (E1/E_R draws) |
| `refs_gams.py` | compliance-reference source: GaMS3-12B-Instruct + its iteration-1 core edit (trial 88), 64-token greedy generations for the 340 S3 JBB prompts |
| `panel.py` | the GPU pipeline (one model load): setup checks → original caches → local judge + references → DEV geometry → frozen predictions → Stage-A timing / trim decision → edit panel (resumable, one JSON per edit) → validity generations → local judge |
| `gapcore.py` | estimators: frozen HGB learner, pooled out-of-fold R², Spearman-Brown ceilings, Gap, B, SIMEX |
| `analysis.py` | gates, Gap/B/SIMEX/stability/strata, margin-matched Gap, mixed model, carrier regression, out-of-sample forecasts, reselection, silent failure, cross-device reproducibility, verdicts → `results/analysis.json`, `results/verdicts.json` |
| `audit.py` | independent numpy re-derivation + placebos → `results/audit.json` |
| `test_T0.py` | synthetic panels with known answers (T0) → `results/T0_synthetic.json` |
| `judge_api.py` | frozen gpt-4.1 judge (OpenRouter, cost ledger `logs/cost_log.jsonl`, hard cap) |
| `figures.py`, `figures/` | fig1–fig6 (PNG + PDF) |
| `make_output.py`, `method_out.json` (+ `full_`/`mini_`/`preview_`) | exp_gen_sol_out output |
| `edits/` | E0, E_TPE, E1, E_R parameter sets + RandomSampler redraw certificate |
| `protocol/` | `frozen_predictions.json` + `protocol_hash.txt`, `trim_decision.json`, `trim_decision_v2_hardware.json`, `validity_edits.json` |
| `references/` | `refs.json` (+sha256): per item × language 24-token refusal and compliance references with their source; `gams_core_generations.json` |
| `directions/` | `geometry.pt` (winsor thresholds, d_EN, d_SL, lang_id, r_prior, r_prior_SL, LSAR U_k), `r_prior.pt` (+sha256) |
| `results/panel/edits/*.json` | per-edit item-level trait deltas (vs the cached original), covariates, timing, device |
| `results/panel/item_traits.parquet`, `edit_covariates.parquet` | the long item table and the edit covariate table used by every analysis (zero-point corrected) |
| `results/validity/` | validity-edit generations (`gen_*.json`), judge labels (`judged.json`) |
| `results/judge_local.json`, `results/judged_api_orig.json` | local judge (validation vs iteration-1 gpt-4.1, original + GaMS labels); gpt-4.1 labels of the original's 440 generations |
| `results/geometry_report.json`, `setup_checks.json`, `smoke_T1.json` | DEV geometry, reproduction checks (trial-96 rebuild, T2), T1 smoke |
| `cache/` | regenerable original-model tensors and analysis resampling caches (**deleted after the round**) |

Kept artifacts are referenced by absolute path:
`/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_7/results/`
(panel, analysis, validity), `.../references/`, `.../directions/`, `.../protocol/`, `.../edits/`.

## How to run

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match
uv run python method.py --deadline-min 200     # T0 → GaMS refs → panel (GPU) → API judge → analysis → audit → figures → output
# or stage by stage:
uv run python test_T0.py
uv run python refs_gams.py
uv run python panel.py --smoke                 # setup + original caches + geometry + frozen predictions + T1 smoke
uv run python panel.py --deadline-min 200      # edit panel (resumable)
uv run python judge_api.py --targets orig,validity
uv run python analysis.py --boot 500 --perm 1000
uv run python audit.py && uv run python figures.py && uv run python make_output.py
```

## Restoring removed files

`.aii/manifest.yaml` deletes only regenerable bulk:

```bash
# .venv/ (regenerable)
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match
# cache/ (regenerable: original-model residuals + Dolly continuation log-softmax, ~5.5 GB, ~6 min on a 24 GB GPU;
#         analysis_*.pkl resampling caches are rebuilt by analysis.py)
uv run python panel.py --smoke
# __pycache__/ is recreated on import
```

Model weights are not stored here. They live in the run's shared HuggingFace cache and can be re-downloaded at the
revisions pinned in `pins.json` (`google/gemma-3-12b-it@96b6f1ec…`, `cjvt/GaMS3-12B-Instruct@1d0b27af…`).

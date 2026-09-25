# Gemma P1 edit panel: what English refusal traits miss in Slovene

Random-edit panel on **google/gemma-3-12b-it@96b6f1ec** (bitsandbytes NF4, bf16 compute), with **Heretic 3521f864** abliteration.
The question: when English-derived Heretic edits are applied, does English (EN) behaviour on one item half predict
Slovene (SL) behaviour on the other half as well as it predicts English? If the answer is no, what explains the
language-specific residual?

Every edit is rebuilt with Heretic's own `Model.abliterate()` on the iteration-1 English refusal directions. Each is
then scored teacher-forced in EN and SL on the frozen S3 DEV halves A and B. All numbers below are recomputed from
`results/analysis.json` (see *Results*).

## Summary (all numbers are recomputed in *Results* below)

163 fitted random edits (E0 + E1, none collapsed; the pre-registered floor of 150 is met). The judge is local (see
Deviations). The confirmatory refusal trait chosen by the validity gate is **R1**.

1. **Slovene refusal moves much less than English under the same English-derived edit.**
   * The core Heretic edit (trial 96) cuts judged EN harmful refusal from 36/41 to 10/41, but SL only from 41/41 to
     39/41.
   * No validity edit brought SL below 30/41.
   * Across edits, the SL change is about 0.44× the EN change for R1 and 0.22× for R_seq.
   * Margin matching and the item × edit mixed model do not remove this: the matched slope is 0.56, and sl:x < 0 after the
     margin interaction.
2. **The Slovene response is attenuated but predictable.** English half A predicts Slovene half B almost as well as it
   predicts English half B (R² 0.94 vs 0.99 for R1). The ceiling-normalised Gap_R1 = +0.054 (95% CI [+0.022, +0.128]) is
   below the pre-registered 0.10, so **P-a is NOT CONFIRMED**. P-d (margin-matched) is NOT CONFIRMED too.
3. **Where the attenuation sits.** Teacher-forced, the edits raise the log-probability of a compliant continuation
   almost equally in both languages (SL/EN slope 0.85). They lower the log-probability of the model's own refusal opener
   only in English (slope 0.08). The English-derived edit weakens the Slovene refusal opener only a little.
4. **Carrier hypothesis fails.** The removal along r_prior (P) adds nothing to the Slovene-specific residual beyond the
   geometry baselines b1/b2/b3/Ω/D (ΔR² +0.004 for R1), and those baselines explain nothing either (CV R² ≤ 0).
   **P-c is NOT CONFIRMED.** The exploratory H covariate (the asymmetry of removal along d_EN) does not help either.
5. **Other findings:**
   * The parameters carry a small but significant SL-specific signal for R1 (B = +0.005, permutation p = 0.009).
   * The Gap concentrates in global-direction edits (+0.34, n = 68) vs per-layer edits (+0.01, n = 95). This is
     exploratory.
   * The K (harmless KL) Gap is small and positive (+0.079, Holm p = 0.009).
   * N and M fail split-half reliability in SL, so they are uninformative.
   * Bilingual reselection over the 100 scored journal trials finds no trial predicted to push SL refusal to ≤ 0.20
     (the best is 0.57).
   * P-b (Rb) is untestable: Rb fails the SL validity gate (Spearman 0.60).

__RESULTS__
**Independent re-derivation** (`rederive.py` → `results/rederive.json`; raw files only, no shared code):
* Matches exactly: the fitted count (163), the transfer slopes (R1 0.436, R_seq 0.220, Rb 0.167), the lp_ref/lp_comp
  slopes (0.081 / 0.849), the judged counts (ORIG and trial 96), and the validity Spearman for R1 (EN 0.892, SL 0.853).
* A polynomial-OLS learner reproduces the Gaps: R1 +0.052, Rb +0.015, K +0.076 (vs +0.054 / +0.018 / +0.079 with HGB).
* Placebos:
  * Permuting the target over edits gives R² ≤ −0.03 (mean −0.11), as it should.
  * The per-edit EN/SL label-swap placebo gives raw Gaps centred on 0 (95% range [−0.109, +0.111]).
  * The observed raw Gap_R1 (+0.051) lies inside that range: 15.5% of swaps are at least as large. So the small R1 Gap
    is not distinguishable from this placebo, consistent with P-a NOT CONFIRMED.


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
   440 generations with gpt-4.1 ($0.37). From 00:05 UTC every call was refused: first the run-wide phase budget was
   exhausted (403 `aii_run_budget_exhausted`), then the platform's budget meter was unavailable (503 at 03:18 UTC), then the phase budget again (403 at 04:43 UTC)
   (`results/api_budget_block.json`).
   * References, r_prior and the validity gate therefore use a **local judge**: the original gemma-3-12b-it with the
     frozen iteration-1 gpt-4.1 rubric.
   * Agreement with gpt-4.1 on the original's 440 generations: __JUDGE_AGREE__.
   * The validity generations are kept in `results/validity/gen_*.json`. `uv run python judge_api.py --targets validity`
     re-judges them with gpt-4.1 when the key works; `analysis.py` then switches its primary judge automatically.
2. **Three GPUs.** The session was interrupted three times, and each resume landed on a different GPU:
   * the first 57 E0 edits and the original zero point ran on an **RTX 4090**;
   * then an **NVIDIA L4** (per-edit time 46 s → 152 s at full items);
   * then an **RTX 4000 Ada** (from 03:44 UTC on 2026-09-24).
   In response:
   * every row carries `device`;
   * each edit's zero point is the original scored on the same device with the same trim
     (`ORIG_TRIM`, `ORIG_FULL_L4`, `ORIG_TRIM2_L4`, `ORIG_FULL_RTX4000AdaGeneration`, `ORIG_TRIM2_RTX4000AdaGeneration`);
   * E0_000 was re-scored on each later device (`REPRO_E0_000_*`, reported under `cross_device_reproducibility`);
   * the frozen trim ladder was re-applied, unchanged, with the L4 timings
     (`protocol/trim_decision_v2_hardware.json`: FLORES 120, MC 80 (task-balanced), Dolly 70, E_TPE = trial 96 + the
     last 40), and that trim was kept on the RTX 4000 Ada. Every trait uses the items common to all edits.
   * The shared HF cache and `.venv` were wiped between sessions 3 and 4. Both were rebuilt from `env/requirements.lock`,
     and the Gemma shards were re-verified against `pins.json` (`logs/pins_reverify_rtx4000ada.json`: all sha256 match).
3. __FITTED_DEV__
4. __BOOT_DEV__
5. **Double BOS.** Heretic 3521f864 tokenizes the rendered Gemma template with special tokens, which produces a double
   BOS. This is inherited unchanged, so the edits are scored exactly as Heretic optimised them.
6. **T2 keyword re-score.** Trials 0, 1 and 2 match the journal within 1/100; trial 96 gives 74 vs 69, with
   weight-identical adapters. The difference is generation numerics, since Heretic's journal was scored in a different
   process and batch.
7. **Silent-failure rule undefined.** No E0 edit reached journal EN keyword refusals ≤ 20/100 (range __JR_RANGE__), so
   the plan's direct silent-failure rate has an empty denominator. The calibrated-trait version over E0 + E1 is reported
   instead.
8. **Scoring stopped at E1_102.** E1 scoring was stopped by hand at 05:24 UTC, after 103 of the 150 E1 draws, to leave
   time for the pre-registered B = 1000 analysis. E_R (seed 20260924) was never scored. The stopping point was chosen
   by wall clock, not by looking at results.

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
| `reproducibility.md`, `pyproject.toml`, `env/requirements.lock` | step-by-step reproduction of what was actually run; exact pinned environment (uv pip freeze) |
| `rederive.py` | independent re-derivation of the headline numbers from the RAW per-edit JSONs, split files and judge labels (own zero point, closed-form slopes, polynomial-OLS Gap, label-swap and permutation placebos) → `results/rederive.json` |
| `test_T0.py` | synthetic panels with known answers (T0) → `results/T0_synthetic.json` |
| `judge_api.py` | frozen gpt-4.1 judge (OpenRouter, cost ledger `logs/cost_log.jsonl`, hard cap) |
| `figures.py`, `figures/` | fig1–fig6 (PNG + PDF) |
| `make_output.py`, `method_out.json` (+ `full_`/`mini_`/`preview_`) | exp_gen_sol_out output |
| `make_readme.py`, `README_template.md` | fills this README's *Results* and deviation numbers from `results/analysis.json` + `results/audit.json` |
| `logs/` | run logs (panel, analysis, local-judge raw outputs, cost ledger, session notes, pin re-verification) |
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
`./results/`
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
uv run python audit.py && uv run python figures.py && uv run python make_output.py && uv run python make_readme.py
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

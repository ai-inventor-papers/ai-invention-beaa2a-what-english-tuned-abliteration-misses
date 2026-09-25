# Reproducing `gen_art_experiment_8` (r_prior causal test, Gemma-3-12B-it + GaMS3 contrast)

This file describes what was **actually run** on 2026-09-23/24, step by step and in order. Timings are the ones in
`logs/*.log` and `results/gemma/timings.json`.

## 1. Get the artifact and its read-only inputs

```bash
cp -r . ~/rprior
cd ~/rprior
```

The code reads three iteration-1 workspaces **read-only** through absolute paths set in `common.py` (`RUN = ...`):

| constant | path | used for |
|---|---|---|
| `DATASET` | `.../iter_1/gen_art/gen_art_dataset_1/data/splits/*.jsonl` + `data/split_manifest.json` | frozen EN/SL splits (every file SHA-256-checked at load; `S5/S6/S7` are refused by a path guard) |
| `CORE` | `.../iter_1/gen_art/gen_art_experiment_1/adapters/gemma_selected_path2` | core Heretic LoRA, trial 96, `adapter_model.safetensors` SHA-256 `d219c084b84370cd972700fa07d754777b2fd56dc12257cd0e67498b2d0f2b01` (checked at load) |
| `A1` | `.../iter_1/gen_art/gen_art_experiment_3` | frozen `d_EN`/`d_SL` (`results/<m>/frozen_directions.npz`), R1 prefix sets; copies are in `a1_ref/` |

If you run outside this machine, copy those three folders and edit `RUN` in `common.py`. Nothing else is hard-coded.

## 2. System, Python, environment

- Ubuntu with an NVIDIA driver supporting CUDA 12.8 (the driver used reported CUDA 13.0), plus `uv`. No other system packages.
- **Hardware used:** 1× NVIDIA GeForce RTX 4090 (24 GB) for every GPU stage (`results/gemma/load_info.json`). The 4-bit 12B
  model needs about 7.8 GB of weights. In this session the venv rebuild and the CPU re-analysis ran on a 16 GB RTX 2000 Ada
  box, with 48 CPUs and 251 GB RAM.
- Python **3.12**, torch **2.11.0+cu128**, transformers **5.17.0**, bitsandbytes **0.50.2**, peft **0.21.0**,
  numpy 2.5.2, pandas 3.0.6, scikit-learn 1.9.1, statsmodels 0.15.0, fasttext-wheel 0.9.2. All 90 packages are pinned in
  `pyproject.toml`, identical to `results/env_freeze.txt` (`uv pip freeze`).

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml   # torch cu128 wheels come from the extra index in pyproject
```

(≈ 6 min with a warm uv cache; the venv is ≈ 11 GB.)

## 3. Downloads, environment variables, keys (names only)

- Environment: `HF_HOME`, `HF_HUB_CACHE`, `TORCH_HOME` (shared model cache), `HF_TOKEN` (Gemma is gated),
  `OPENROUTER_API_KEY` and `OPENROUTER_BASE_URL` (judge only; never hard-coded). Optional: `TF_TOKEN_BUDGET`
  (teacher-forced batch size, default 8192 tokens).
- Models, pinned by commit (`python dl_models.py <repo>` downloads the snapshots):
  - `google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80`
  - `cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`
  - `p-e-w/gemma-3-12b-it-heretic@e037e6e112ea85777fc3858469cdc31fdfceaa13` (community held-out edit)
  - `Qwen/Qwen3-14B@40c069824f4251a91eefaf281ebe4c544efd3e18` (local second judge)
  - GlotLID fastText model `cis-lmu/glotlid` `model.bin` (downloaded by `analysis.py` through `hf_hub_download` on first use)
- Every model is loaded as bitsandbytes **NF4 4-bit with bf16 compute**, and decoding is greedy. The system prompt is
  `"You are a helpful assistant."` in both languages. The global seed is `SEED = 20260923` (`common.py`); random-direction
  draws, shuffles, bootstraps and judge batch order all derive from it.

## 4. Commands, in the order they were run

```bash
# T3 smoke run (8 items per set; writes results_mini/)                                        ~10 min
.venv/bin/python method.py --model gemma --mini
# Confirmatory Gemma pipeline: hook unit tests -> batching gate -> half-A generations/residuals -> directions ->
# layer + strength selection on half A -> FREEZE (configs/FREEZE.sha256) -> OUTCOME arms A0-A11, dose, ADD ->
# weight edits W0-W2 on the core LoRA. Interrupted once after A7 and resumed from per-arm checkpoints.  ~90 min
.venv/bin/python method.py --model gemma
# Chain: community held-out edit (C0-C2, ~7 min) -> GaMS3 contrast (G0-G5, ~23 min) -> exploratory X1/X2/X4 + S2 stability (~7 min)
bash run_chain.sh <gemma_pid>          # runs: method.py --model community ; --model gams3 ; --model gemma --explore
# Primary judge, gpt-4.1 blind, 10 cases/call, tiered priority, cost-capped (ran 21:37-00:06, stopped by the budget cap)
.venv/bin/python judge.py --batched --tiers 4
# Local second judge over every generation (Qwen3-14B NF4, same rubric)                        ~20 min
.venv/bin/python local_judge.py
# Post-freeze exploratory stages, each declared and hashed into configs/FREEZE.sha256 before its outcome pass
.venv/bin/python method.py --model gemma --explore2   # depth bands Y*, layer-matched random X3 / PC X5   ~18 min
.venv/bin/python local_judge.py                         # labels the new generations
.venv/bin/python method.py --model gemma --explore3   # repair arms W3/W4 on the core Heretic edit          ~5 min
.venv/bin/python local_judge.py
# CPU analysis and packaging (re-run end-to-end on 2026-09-24 in this order; ~15 min in total)
.venv/bin/python make_deviations.py
.venv/bin/python analysis.py               # -> results/analysis_summary.json, results/per_item.parquet
.venv/bin/python analysis.py --recompute   # T8: recomputes from per_item.parquet -> results/recompute_check.json
.venv/bin/python verify_numbers.py         # 103 independent checks + placebos + freeze-order -> results/verify_numbers.json
.venv/bin/python audit_headline.py         # 43 README numbers from RAW files, own code path + 3 placebos -> results/audit_headline.json
.venv/bin/python figures.py                # figures/fig1-fig10 (.pdf + .png)
.venv/bin/python report_tables.py > results/report_tables.md
.venv/bin/python build_output.py           # method_out.json (exp_gen_sol_out)
# full/mini/preview via the aii-json skill's aii_json_format_mini_preview.py --format exp_gen_sol_out --input method_out.json
```

Every GPU stage resumes by arm (`results/<model>/gens/<arm>.json`). Judging is cached by
`sha256(judge|prompt|response)` in `results/judge_cache.jsonl` and `results/judge2_local.jsonl`, so a rerun never
repeats a paid call. **The judge caches are part of the result:** rerunning `judge.py` without them needs about $3.4 of
OpenRouter credit, plus roughly $2.5 more to cover the 3,839 generations that were never primary-judged.

## 5. What you should get

Re-running the CPU chain on the saved generations and label caches reproduces `results/analysis_summary.json` to
≤ 1e-7. The only differences are last-digit float noise from BLAS in the item-level logistic fits. `recompute_check.json` gives
`identical_verdicts: true`, `verify_numbers.json` gives 103/103, and `audit_headline.json` gives 43/43 with all placebos null.
Re-running the GPU stages on a different GPU can change a few late greedy tokens, because bf16 drift is not bit-stable
across cards.

Headline numbers (README "Headline" and "Results"; the paper's main results table and fig1/fig10):

| quantity | value | where |
|---|---|---|
| SL harmful refusal, no-op → `d_EN` (A0 → A1) | 0.99 → **0.86** | `analysis_summary.rates`, README table 1, fig1 |
| F1 cut of `d_EN+r_prior` vs A1 | **0.036 [−0.037, 0.109]**; best matched random 0.074; shuffled-label 0.135 → KILL (a) and (c) | `verdicts.F1`, README headline 1 |
| F3 SL over-refusal under `r_prior` alone | 0.28 → 0.19, McNemar p = 0.006 (Holm 0.025), 32 % relative (< 50 % bar) | `verdicts.F3` |
| X1 layer-matched `d_EN(h)` (exploratory) | SL harmful 0.86 → **0.10**, cut 0.71 [0.57, 0.85] (gpt-4.1, partial coverage); 0.91 → 0.23 (second judge, full) | `secondary`, fig10 |
| layer-matched random X3 / PC X5 | 0.86 / 0.93 (no cut) | `secondary.depth_localisation`, fig10 |
| repair W3 on core edit (hoc) | SL 0.93 → **0.11**, random control W4 0.47 | README repair table, fig3 |
| community edit C0 SL hoc refusal | 0.26 → F5 not evaluable | `verdicts.F5`, fig3 |
| second judge κ vs gpt-4.1 (refused vs not) | 0.77 (SL 0.88, EN 0.62) | `label_agreement.second_judge` |
| OpenRouter spend | $3.43 | `results/api_costs.jsonl` |

Frozen verdicts: **F1 fail, F2 pass, F3 fail, F4 fail, F5 not evaluable, F6 fail; KILL (a) and (c) fire.**
Every departure from the plan is listed in `results/deviations.json`, including the primary judge's 58 % coverage
(`analysis_summary.judge_coverage`).

# Reproducibility: Gemma P1 edit panel (what English refusal traits miss in Slovene)

This file describes what was **actually run** (2026-09-23 21:00 UTC to 2026-09-24 06:40 UTC), including the
interruptions. The pipeline is resumable per edit, so re-running a stage skips finished work.

## 1. Copy the artifact

```bash
cp -r /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_7 ~/gemma_p1_panel
cd ~/gemma_p1_panel
```

The code reads these iteration-1 artifacts **read-only, by absolute path**. Copy them to the same paths, or edit the
constants at the top of `common.py`, `panel.py` and `refs_gams.py`.

| name | path | contents used |
| --- | --- | --- |
| `EXP1` | `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1` | Optuna journal `checkpoints/gemma/google--gemma-3-12b-it.jsonl` (116 trials); `directions/gemma/directions.pt`; `adapters/gemma_selected/` (trial 96); `adapters/gams_selected/` (GaMS trial 88) |
| `EXP3` | `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_3` | `judge.py` (the frozen gpt-4.1 rubric, read verbatim); `judged_generations.json` |
| `DATA` | `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1/data/splits` | `S3_jbb.jsonl`, `S3_dolly.jsonl`, `S3_flores_dev.jsonl`, `S3_mc.jsonl`, `S2_semantic.jsonl`, `S4_strongreject_pairs.jsonl`. FINAL splits S5-S7 are never read. |

## 2. System, Python, environment

* Ubuntu (Linux 6.8) with an NVIDIA driver supporting CUDA 12.8 (driver 580/595 used).
* Python 3.12.14, and `uv` for environment management.
* No extra system packages beyond the NVIDIA driver and `git` (Heretic is installed from git).

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock \
    --extra-index-url https://download.pytorch.org/whl/cu128 --index-strategy unsafe-best-match
```

`env/requirements.lock` and `pyproject.toml` both hold the exact `uv pip freeze` of the `.venv` that produced the final
results (176 packages). Key pins:

* `torch==2.11.0+cu128`
* `transformers==5.17.0`
* `bitsandbytes==0.50.2`
* `peft` (as locked)
* `optuna` (as locked)
* `scikit-learn==1.9.1`
* `statsmodels==0.15.0`
* `numpy==2.5.3`
* `heretic-llm @ git+https://github.com/p-e-w/heretic@3521f8648a0dccf6e12a92666862632235fac7e6`

## 3. Models, data, environment variables

* Models are pinned by revision in `pins.json`, with per-shard LFS sha256:
  * `google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80` (gated: needs `HF_TOKEN`);
  * `cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`, used only for the compliance references.
* Download (the code loads them from the HF cache):
  ```bash
  hf download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80
  hf download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc
  ```
  `logs/reverify_pins.py` re-checks the Gemma shard sha256 values (all matched after the session-4 re-download).
* Environment variables (names only):
  * `HF_TOKEN`
  * `HF_HOME` / `HF_HUB_CACHE`
  * `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`: only for `judge_api.py`, the optional gpt-4.1 judge.
  * `AII_N_JOBS`: optional CPU worker count for `analysis.py`.
* Precision: NF4 4-bit (bitsandbytes) with bf16 compute, restored from the journal's Heretic settings. The system
  prompt is "You are a helpful assistant.". Greedy decoding.

## 4. Commands actually run, in order

| step | command | hardware / runtime | notes |
| --- | --- | --- | --- |
| T0 | `uv run python test_T0.py` | CPU, ~1 min | synthetic panels with known answers → `results/T0_synthetic.json` |
| refs | `uv run python refs_gams.py` | RTX 4090 24 GB, ~5 min | GaMS3 + trial-88 adapter, 340 greedy generations → `references/gams_core_generations.json` |
| setup + smoke | `uv run python panel.py --smoke` | RTX 4090, ~8 min | setup checks (trial-96 rebuild max \|ΔBA\| 6.1e-8; T2 keyword re-score), original caches → `cache/`, local judge, references, DEV geometry, **frozen predictions hashed** (`protocol/protocol_hash.txt`), T1 smoke |
| panel (session 1) | `uv run python panel.py --deadline-min 185` | RTX 4090, 46 s/edit | Stage-A pilot (5 E0 edits) → `protocol/trim_decision.json` (no trim); E0_000-E0_056 |
| panel (sessions 2-3) | same command, relaunched (resumes per edit) | NVIDIA L4 24 GB, 152 s/edit at full items, ~116 s trimmed | hardware trim → `protocol/trim_decision_v2_hardware.json` (FLORES 120, MC 80, Dolly 70, E_TPE = trial 96 + last 40); zero points `ORIG_*_L4`; rest of E0, E1_000-029, 14 validity generations, 40 E_TPE, E1_030-038 |
| API judge | `uv run python judge_api.py --targets orig,validity` | OpenRouter `openai/gpt-4.1` | judged only the original's 440 generations ($0.367) before the run-wide budget blocked all calls (`results/api_budget_block.json`) |
| session 4 | `bash logs/run_gpu_v4.sh 155`, i.e. `panel.py --stages judge`, then `panel.py --stages edits,judge --deadline-min 155` | RTX 4000 Ada 20 GB, ~88 s/edit | local judge of the 14 validity edits; zero points `ORIG_*_RTX4000AdaGeneration`; `REPRO_E0_000_*`; E1_039-E1_102; **stopped by hand at 05:24 UTC** (wall-clock choice) |
| analysis | `AII_N_JOBS=7 uv run python analysis.py --boot 1000 --perm 1000` | 7.65-core CPU quota, 64 min | → `results/analysis.json`, `results/verdicts.json`, `results/panel/*.parquet` |
| audit | `uv run python audit.py` | CPU, ~3 min | → `results/audit.json` |
| re-derivation | `uv run python rederive.py` | CPU, ~1 min | → `results/rederive.json` |
| outputs | `uv run python figures.py && uv run python make_output.py && uv run python make_readme.py` | CPU, ~1 min | `figures/fig1-6`, `method_out.json`, `README.md` |
| json variants | `aii_json_format_mini_preview.py --input method_out.json` (aii-json skill) | CPU | `full_/mini_/preview_method_out.json`; schema `exp_gen_sol_out` validated |

`uv run python method.py --deadline-min 200` chains all of the above except the manual stop and the JSON variants.

Seeds:

| what | seed |
| --- | --- |
| E0 redraw certificate | `RandomSampler(seed=20260923)` |
| E1 | 20260925 |
| E_R | 20260924 (never scored) |
| CV folds | `KFold(5, shuffle, seed=20260926)` |
| learner | `random_state=0` |
| bootstrap draws | 1000 + s |
| B permutations | 5000 + s |
| carrier bootstrap | 9000 + s |
| disjoint halves | 20260926 |
| `rederive.py` folds / placebos | 7 / 100 + s / 500 + s |

Numerics depend slightly on the GPU. Every edit is zero-pointed against the original scored on the same device and
trim, and cross-device repro rows are reported in `analysis.json → cross_device_reproducibility`.

## 5. What you should get

The paper cites these outputs:

* `results/analysis.json`:
  * fitted set 163 (≥ 150 floor);
  * validity gate: R* = R1 (Spearman EN 0.892 / SL 0.853);
  * transfer slopes R1 0.436, R_seq 0.220;
  * Gap_R1 +0.054 (95% CI [+0.022, +0.128]), Gap_Rb +0.018, Gap_K +0.079 (Holm p 0.009);
  * margin-matched Gap_R1 +0.057;
  * mixed model sl:x −0.321;
  * carrier ΔR²(P given base) +0.004.
* `results/verdicts.json`: P-a, P-c and P-d are NOT CONFIRMED; P-b is UNTESTABLE (Rb fails the SL validity gate).
* `results/validity/judged.json`: judged refusal on harmful prompts.
  * Original: EN 36/41, SL 41/41.
  * Trial 96: EN 10/41, SL 39/41.
* `results/rederive.json`: the independent re-derivation (Gap_R1 +0.052 with polynomial OLS) and the placebos.
* `figures/fig1_gap_per_trait`, `fig2_en_vs_sl_scatter`, `fig3_carrier_forest`, `fig4_margin_matched`, `fig5_validity`,
  `fig6_transfer_slope` (PNG + PDF).
* `README.md` *Summary* / *Results*, regenerated from these files by `make_readme.py`.

The bootstrap and permutation p-values reproduce exactly given the same fitted set and seeds. HGB fits are
deterministic (`random_state=0`). Re-scoring edits on a different GPU changes item-level trait values at about the 1e-2
level (see `cross_device_reproducibility`).

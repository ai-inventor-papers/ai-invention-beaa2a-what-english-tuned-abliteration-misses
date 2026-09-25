# Reproducibility — the exact sequence that produced these results

> This describes what **actually ran**, including the two places where the first attempt failed and had to be
> re-run (the judge's token budget, and a `fasttext`/NumPy-2 incompatibility). Both are in `results/deviations.json`.

## 0. System, from a clean Ubuntu box

```bash
# Ubuntu 22.04/24.04, NVIDIA driver >= 550 (this run: 580.126.20, CUDA 13.0 runtime, one RTX 4090 24 GB)
sudo apt-get update && sudo apt-get install -y git curl build-essential python3.12 python3.12-venv
curl -LsSf https://astral.sh/uv/install.sh | sh        # uv is the ONLY package manager used; pip is never called

# 1. copy this artifact folder into a working directory
cp -r gen_art_experiment_9 ~/work/ && cd ~/work/gen_art_experiment_9

# 2. environment: Python 3.12, the 90 exactly-pinned packages in pyproject.toml (== results/env_freeze.txt)
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml   # torch 2.11.0+cu128 comes from the cu128 extra index
.venv/bin/python -c "import torch; print(torch.__version__, torch.cuda.is_available())"   # expect 2.11.0+cu128 True
```

`fasttext-wheel==0.9.2` (GlotLID) ships a `predict()` that calls `np.array(..., copy=False)`, which **NumPy 2
rejects**. `alib.py` therefore calls the pybind model's `f.predict` directly instead of patching the package — if you
see `ValueError: Unable to avoid copy while creating an array as requested`, that path is what fixes it.

## 1. Environment variables and credentials — NAMES ONLY, never values

| name | what it is for | required? |
|---|---|---|
| `HF_HOME`, `HF_HUB_CACHE` | where the four model snapshots are cached (~51 GB) | yes |
| `HF_TOKEN` | Hugging Face read token; `google/gemma-3-12b-it` and `meta-llama/Llama-Guard-3-8B` are gated | yes |
| `OPENROUTER_BASE_URL` | run-scoped OpenRouter endpoint; **never hard-code the public URL** or every call 401s | only for the gpt-4.1 certification subsample |
| `OPENROUTER_API_KEY` | key for that endpoint | only for the gpt-4.1 certification subsample |

Never print or commit any of these values. Without the OpenRouter pair the pipeline still completes: step 4 below is
skipped, the scorer is certified at the on-disk κ = 0.779 instead, and that κ is what every table then reports.

## 2. Data and model downloads

Data is **read-only** from the frozen dataset artifact and is SHA-256-verified at load
(`common.load_split` vs `data/split_manifest.json`); nothing is downloaded:
`../../../round-1/dataset-1/src`.
Two further read-only inputs: the frozen per-layer directions from iteration 2 (`gen_art_experiment_8/directions/`)
and the trial-96 LoRA adapter (`gen_art_experiment_1/adapters/gemma_selected_path2`, SHA-256 `d219c084…`).

```bash
hf download google/gemma-3-12b-it     --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80   # ~23 GB, gated
hf download Qwen/Qwen3-14B            --revision 40c069824f4251a91eefaf281ebe4c544efd3e18   # ~28 GB, the scorer
hf download cis-lmu/glotlid model.bin --revision 85cd6716494360367b75f642b5bc78667605d0b4   # language ID
# only if you re-run the guard-ASR sensitivity arm:
hf download meta-llama/Llama-Guard-3-8B --revision 7327bd9f6efbbe6101dc6cc4736302b3cbb6e425
```

## 2b. Pins (asserted at startup, `results/gate0_pins.json`)

| thing | pin |
|---|---|
| edited model | `google/gemma-3-12b-it` @ `96b6f1eccf38110c56df3a15bffe176da04bfd80` |
| scorer | `Qwen/Qwen3-14B` @ `40c069824f4251a91eefaf281ebe4c544efd3e18` |
| certification judge | `openai/gpt-4.1` via OpenRouter, temperature 0, seed 0 |
| language ID | `cis-lmu/glotlid` `model.bin` @ `85cd6716494360367b75f642b5bc78667605d0b4` |
| core Heretic edit | trial-96 LoRA, `adapter_model.safetensors` SHA-256 `d219c084…` (read-only) |
| directions | `exp8/directions/gemma_all_layers.npz`, verified `cos(d_EN(L20), gemma_dEN.npy) = 0.99998` |
| data | every `S*` split SHA-256-checked against `gen_art_dataset_1/data/split_manifest.json` |

Quantisation: bnb NF4, bf16 compute, double quant (Heretic's own `BitsAndBytesConfig`). Decoding: greedy, 128 new
tokens, identical chat template and system prompt (`"You are a helpful assistant."`) in both languages — the rendered
prompt strings are byte-identical to the ones iteration 2 saved.

## 3. The exact commands, in order

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml

.venv/bin/python method.py --stage smoke           # ~5 min: Gates 0/1/2/4 + timing model
.venv/bin/python method.py --stage partA+screen    # ~65 min: 29 Part-A + 75 screen cells
bash run_chain.sh                                  # judging -> certification -> FREEZE -> confirmation -> analysis
```

`run_chain.sh` is exactly what ran, in this order:

| step | what | time |
|---|---|---|
| 1 | `judge/local_judge.py --exp8 200` — score every generation, plus 200 saved exp8 generations (Gate 3) | 36 min (13,324 items, 0.21 s/item) |
| 2 | `judge/local_judge.py --refail` — re-judge the 182 unparsed replies at a larger token budget | 1 min |
| 3 | `judge/certify.py` — κ within EDITED checkpoints from labels on disk → **0.779**, misses the 0.80 bar | seconds |
| 4 | `judge/api_judge.py --n 600` — the one bought gpt-4.1 subsample → κ = **0.866**, passes | 2 min, **$0.70** |
| 5 | `freeze.py` — DEV index + frozen predictions hashed into `results/FREEZE.sha256` | seconds |
| 6 | `method.py --stage confirm` — 15 cells × (680 generations + S7 utility) | 50 min |
| 7 | `judge/local_judge.py` (+`--refail`) — score the confirmation generations | 36 min (9,181 items) |
| 8 | `select_s5x.py`, `method.py --stage s5x`, judging — the single declared second touch | 5 min |
| 9 | `analysis.py`, `make_deviations.py`, `rederive.py`, `figures.py`, `report_tables.py`, `build_output.py` | 12 min |
| 10 | `audit_positive.py` — placebo tests for the claims that SURVIVED (P3, the index gap, band identity) | 2 min |

**Freeze order is asserted programmatically**: `freeze.py` refuses to run if any `CF_*` generation already exists, and
`method.py --stage confirm` refuses to run unless `results/FREEZE.sha256` lists the current SHA-256 of both
`frozen_predictions.json` and `redundancy_index.json`. `configs/explore_band_identity.json` was declared and appended to
the same hash file **before** the exploratory band-identity analysis was computed.

## 4. Numbers to expect, and where they appear

If a re-run reproduces the artifact, these should come back (all from `results/report_tables.md`):

| check | expected |
|---|---|
| Gate 1 operator unit tests | projection removal ratios 0.50 / 0.75 at c = 0.5 / 0.25; closed-form vs explicit `‖dW‖²_F` relative error **0.0**; untouched hidden index bit-identical |
| Gate 2 anchors (20 items/lang) | SL: A1 0.95, X4 0.95, X1 0.20 — inside the band spanned by exp8's two judges |
| Anchors at full n (41 items/lang) | A1 SL 0.93 (exp8 0.86/0.91), X1 SL 0.12 (0.10/0.23), W0 SL 0.93 (0.89/0.93), W3 SL 0.12 (–/0.11), no-op SL 1.00 (0.99/0.98) |
| matched-energy solving | all four groups solved inside `max_weight = 1.5`, no narrow-cell shifting; `E_narrow == E_broad` to 1e-12 |
| random controls | 8/8 matched energy **and** collateral (5 accepted on the first draw, 3 on the second) |
| DEV index | index_EN **16** [16, 20], index_SL **20** [20, 28] (prefix); both 24 (suffix) |
| LOBO necessity, layers 25–36 | SL **+0.39**, EN **0.00** |
| P1 | ΔR² **0.040** [0.006, 0.136], LOO **−0.002**, p_F 0.17, placebo p95 0.158, MDE 0.071 → **FAIL**, falsifier fires |
| P2 | pooled SL **+0.049** [−0.000, 0.098], DiD **−0.120** [−0.214, −0.033] → **FAIL** (and on hoc: +0.054, DiD −0.061) |
| P3 | Spearman EN **0.78** [0.64, 0.88], SL **0.78** [0.62, 0.89] → **PASS** |
| band identity | only B2 / C24 / C36 / ALL48 / K96 ever reach SL < 0.5; G2 at equal energy: 0.63 (12 contiguous) vs 0.98 (24 strided) |
| best cell (screen) | `W_K96_c1.5`: SL 0.024, EN 0.049, FLORES −0.000 nats, KL 0.030, LID 0.992 |
| S5X (100 verified pairs) | no-op SL 0.98 / EN 0.91; both best cells SL 0.08 / EN 0.02 |
| band density | Spearman(fraction of layers 13–24 covered, lowest SL reached) = **−0.942**; permutation p = **0.0038** |
| curve separation | mean SL−EN prefix-curve gap **+0.080** [0.021, 0.136], permutation p = **0.0065** |
| index gap placebo | gap of 4 is INSIDE its language-permutation null [−4, +4] — the index alone does not carry C2 |
| independent audit | `rederive.py` **318/318** checks match; `audit_positive.py` placebo-tests every surviving positive claim |

### Output files a reader should get, and where each number lives

| file | holds |
|---|---|
| `results/report_tables.md` | **every table quoted in the README and the paper**, printed from `analysis_summary.json` |
| `results/analysis_summary.json` | all verdicts (P1/P2/P3/C2), CIs, placebos, Holm, confirmation, S5X, exploratory blocks |
| `results/cells.csv` / `.parquet` | one row per cell: coverage descriptor, per-layer coefficients, energy, every outcome |
| `results/per_item.parquet` | one row per generation: 4-way class, rubric harm verdict, GlotLID, rep3, truncation |
| `results/gens/<cell>.json` | the raw generations themselves (122 files, 27,784 generations) |
| `results/redundancy_index.json` + `frozen_predictions.json` + `FREEZE.sha256` | the frozen DEV index and pre-registered tests, with their hashes |
| `results/audit.json` | the 318 independent re-derivation checks and the placebo outcomes |
| `results/deviations.json` | all 11 departures from the plan, each with its evidence file |
| `figures/fig1..fig6` (PDF+PNG) | coverage curves, matched-energy pairs, index prediction, write mass, heatmap, collateral |
| `method_out.json` (+`full_`/`mini_`/`preview_`) | everything above in the `exp_gen_sol_out` schema |

Paper-facing mapping: the **index (EN 16 / SL 20)** and the **LOBO +0.39 vs 0.00** come from
`redundancy_index.json` → README headline 5–6 → `fig1`; **P1's ΔR² = 0.040** and **P2's pooled +0.049 / DiD −0.120**
from `analysis_summary.json` → headlines 1–2 → `fig2`; the **band-identity table** (only sets containing 13–24 ever
reach SL < 0.5) from `analysis_summary.band_identity_exploratory` → headline 3 → `fig5`; **P3's Spearman 0.78** →
headline 4 → `fig3`; the **best operating point (SL 0.024 at ~0 nats)** from `cells.csv` → headline 7 → `fig6`.

## 5. Determinism, seeds, and what is not deterministic

Greedy decoding with a fixed batch schedule makes generation reproducible up to bf16/NF4 kernel non-determinism and
batch composition; iteration 2 certified batched-vs-unbatched agreement at 13/16 identical over 32 tokens on this model,
so individual generations can differ slightly between runs while rates do not. Bootstraps and all seeded samples use
`common.SEED = 20260924`, so CIs are reproducible. The bought gpt-4.1 labels are cached in `results/judge_api.jsonl` and
are never re-paid. The OpenRouter spend was **$0.70** of a $10 cap (`results/api_costs.jsonl`).

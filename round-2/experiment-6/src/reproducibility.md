# Reproducing the P1 random-edit panel on GaMS3-12B-Instruct

This file describes what was **actually run** for this artifact (`gen_art_experiment_6` of run `run_Fapgmt6JWbcD`),
including the interruptions. Numbers in the README are generated from `results/*.json` by `make_readme.py`.

## 1. Get the folder

```bash
cp -r gen_art_experiment_6 ~/p1_gams && cd ~/p1_gams
```

The code reads three iteration-1 workspaces **read-only**, located relative to this folder at
`../../../round-1/` (see `common.py`: `ITER1`, `EXP1`, `EXP3`, `DS`). A copy elsewhere needs the same layout, or
`ITER1` in `common.py` edited to point at:
- `gen_art_experiment_1/checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl`: the Optuna journal (E0 / E_TPE edits and Heretic settings)
- `gen_art_experiment_1/directions/gams/directions.pt`: the per-layer refusal directions
- `gen_art_experiment_1/adapters/gams_selected_path2/`: the trial-88 LoRA (U2 reproduction target; sha256 a4419c51…)
- `gen_art_experiment_3/configs/prefix_sets_gams3.json` (R1 prefix sets) and `results/gams3/frozen_directions.npz` (H probe
  cross-check). The U6 FLORES cross-check against EXP3's C0 per-item NLL was run once, interactively; only its result
  `results/u6_flores_check.json` is saved (FAIL at 2e-3, mean |diff| 0.009 nats, deviation D5).
- `gen_art_dataset_1/full_data_out.json` and `data/split_manifest.json`: S3 DEV blocks, hash-verified

## 2. System, Python and libraries

- Ubuntu 22.04-class container, NVIDIA driver 580.159.04 (CUDA 13.0 driver; the torch wheels are CUDA 12.8)
- Python 3.12 (3.12.14 used), [`uv`](https://github.com/astral-sh/uv) for all package operations (no pip)

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python torch==2.11.0+cu128 torchvision==0.26.0+cu128 \
    --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml          # 162 exact pins (== versions)
uv pip install --python .venv/bin/python -e third_party/heretic --no-deps   # Heretic 3521f8648a0d…
```

Key pins (all in `pyproject.toml`; the host-3 rebuild's freeze is in `logs/freeze_host3.txt`): transformers 5.17.0,
peft 0.21.0, bitsandbytes 0.50.2, optuna 4.9.0, accelerate 1.15.0, numpy 2.5.2, scipy 1.18.1, scikit-learn 1.9.1,
pandas 3.0.6, statsmodels 0.15.0, fasttext-wheel 0.9.2, sentence-transformers 6.1.0, huggingface-hub 1.32.0.

## 3. Models, data and environment variables

Environment variables (names only):
- `HF_HOME`, `HF_HUB_CACHE`, `TRANSFORMERS_CACHE`, `HF_DATASETS_CACHE`, `TORCH_HOME`, `UV_CACHE_DIR`: shared cache locations
- `HF_TOKEN`: Hugging Face access
- `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`: judge calls (gpt-4.1 primary; gemini-2.5-flash planned second judge)
- `P1_TOTAL_BUDGET_S`: optional override of the panel's time guard (set to 27600 on the resumed panel run, D16)

Models, downloaded on first use:

| model | revision | role |
|---|---|---|
| `cjvt/GaMS3-12B-Instruct` | `1d0b27af5748784482600d24779409e7e1dc9adc` | edited model, bnb_4bit NF4, bf16 compute (Heretic loads `main`, verified == this sha) |
| `Qwen/Qwen3-14B` | `40c069824f4251a91eefaf281ebe4c544efd3e18` | local judge (bnb_4bit), second judge + fill-in |
| `cis-lmu/glotlid` (`model.bin`) | `85cd6716…` | language ID of responses and X_SET |
| `facebook/nllb-200-distilled-1.3B`, `sentence-transformers/LaBSE` | hub default at run time | X_SET EN->SL translation and QC (data_prep.py only) |
| `databricks/databricks-dolly-15k` | hub default at run time | 64 fresh X_SET prompts (seed 20260925) |

## 4. Commands, in the order they ran

Hardware: stages 0-B on **RTX 4090 24 GB** (host 1: Ryzen 9 7950X; host 2 from panel edit E0_051: EPYC 7352).
Post-panel steps ran on **RTX 2000 Ada 16 GB** (host 3, 5.1-CPU cgroup quota).

```bash
# Stage 0a (CPU + GPU for NLLB), ~7 min
.venv/bin/python data_prep.py
# Stages 0b-A + panel; seeds: journal seed 20260923 (E0), E1 20260925, E_R 20260924; CV seed 20260925; bootstrap seed 11
.venv/bin/python method.py --stages stage0b,stage0c,stage0d,freeze,stageA,panel
#   stage0b 185 s, stage0c 400 s, stage0d 338 s, stageA 320 s (ladder step 0 = full item set)
#   interrupted after 51 edits (22:38 UTC) -> resumed twice with the append-only path:
P1_TOTAL_BUDGET_S=27600 .venv/bin/python method.py --stages panel      # panel total 10111 s ~ 2.8 GPU-h, ~41 s/edit
# T0 synthetic test (CPU), all four scenarios pass
.venv/bin/python synth_test.py --B 100
# Blind gpt-4.1 judging (1130 of 2140 generations labelled, $1.06, before the run-level OpenRouter budget ran out)
.venv/bin/python judge.py --no-second
# host 3 (after a server restart): local judge for the remaining 1010 + agreement on the 1130 overlap, ~18 min
.venv/bin/python local_judge.py
# GPU checks (~28 min + ~20 min on the RTX 2000 Ada)
.venv/bin/python post_tests.py
.venv/bin/python repro_check.py
.venv/bin/python host_check.py            # CPU, seconds
# Stage D analysis, frozen protocol, B = 1000 (87 min on a 5-CPU quota)
AN_JOBS=24 .venv/bin/python analysis.py --B 1000
# outputs
.venv/bin/python audit.py && .venv/bin/python figures.py && .venv/bin/python summary_tables.py
.venv/bin/python to_schema.py && .venv/bin/python make_readme.py
# independent re-derivation of the headline numbers + placebos (CPU, ~2 min)
.venv/bin/python rederive_headlines.py
```

The frozen protocol and predictions (`results/frozen_protocol.json`, `results/frozen_predictions.json`, with `.sha256`)
were written before any panel trait existed; `common.freeze_json` refuses to overwrite them with different content.

## 5. What you should get

GPU numerics: re-scoring on a different GPU model changes per-item values slightly (`results/repro_check.json`:
R_seq ≤ 0.041, KL ≤ 0.002 per item). Headline values may move in the third decimal; bootstrap CIs are seeded.

| number | expected | file |
|---|---|---|
| fitted edits F | 160 (0 collapsed) | `results/analysis_results.json` `n_F` |
| refusal proxy validity, Spearman(R_seq, judged refusal), 18 conditions | EN 0.970, SL 0.910 | `results/analysis_results.json` `validity` |
| Gap_R (refusal visible in SL) | 0.015, 90% CI [0.008, 0.027], TOST holds (confirmatory) | `results/verdict.json` |
| Gap_K (harmless KL divergence) | 0.147, 95% CI [0.074, 0.265], label BLIND (confirmatory) | `results/verdict.json`, `summary_tables.md` |
| Gap_K robustness | SIMEX 0.112, margin-matched 0.131, halves 0.118 / 0.150, B_K 0.050 [0.001, 0.121] | `results/analysis_results.json` |
| exposure carrier D for K | dR2 -0.011 [-0.058, 0.027] (G4 fails) | `results/analysis_results.json` `carrier` |
| local vs gpt-4.1 judge | kappa 0.875 refused-vs-not, 0.702 6-way (n = 1130) | `results/judge_meta.json` |
| independent re-derivation | Gap_K 0.115 (ExtraTrees) / 0.105 (LOO ridge); Gap_R ~0.01; placebos fail | `results/rederive_headlines.json` |

In the paper: the Gap forest is `figures/fig2_gap_forest.png`, the EN-vs-SL scatter `fig1`, validity `fig6`, and the
exploratory source-layer result `fig8`. The tables come from `results/summary_tables.md`.

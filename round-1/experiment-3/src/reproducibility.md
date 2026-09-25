# Reproducibility: English vs Slovene refusal-direction transfer test (A1 screen, iteration 1)

This file is reconstructed after the fact from the workspace (code, `README.md`, `pyproject.toml`, `configs/`, `results/`, `logs/`). Anything the workspace does not record is marked **not recorded**. Nothing was re-run when writing it.

## 1. Get the artifact
```bash
git clone <URL-of-the-public-repository>   # URL not recorded in the workspace
cd <path-to-this-artifact-folder>          # the folder named gen_art_experiment_3
```
All code anchors on `Path(__file__)` (`common.py`: `ROOT`, `DATA`, `RES`, `CFG`, `LOGS`, `FIGS`); no absolute paths are needed. `third_party/heretic/` holds Heretic source at the pinned SHA (reference copy).

## 2. System, Python, environment
- Ubuntu (host kernel 6.8), one NVIDIA L4 (23 GB, driver 570.195.03, CUDA 12.8; `results/gams3/nvidia_smi.txt`). The plan assumed a 20 GB A4500. Other system packages: **not recorded** (need git and a CUDA-capable driver).
- Python 3.12 (`requires-python >=3.12,<3.13`), uv-managed venv. Exact pins are in `pyproject.toml` and `results/env_freeze.txt` (key ones: torch 2.11.0+cu128, transformers 5.17.0, bitsandbytes 0.50.2, accelerate 1.15.0, numpy 2.5.2, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, sentence-transformers 6.1.0, datasets 4.8.5, lm-eval 0.4.13, optuna 4.9.0, fasttext-wheel 0.9.2, heretic-llm from git commit `3521f8648a0dccf6e12a92666862632235fac7e6`).
```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python torch torchvision --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml
```

## 3. Downloads, keys
- Models (pinned): `cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`, `google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80` (`configs/pins.json`). Gemma is gated on Hugging Face, so log in with an accepted licence (token variable name not recorded). Download with `.venv/bin/python dl_models.py` (optionally pass repo ids). Auxiliary models: `.venv/bin/python dl_aux.py` (LaBSE, cis-lmu/glotlid, NLLB-200-distilled-1.3B, Qwen2.5-7B-Instruct).
- Datasets (fetched by `data_build.py` through `datasets`): JailbreakBench/JBB-Behaviors, mlabonne/harmful_behaviors, mlabonne/harmless_alpaca, databricks/databricks-dolly-15k, openlanguagedata/flores_plus (fallback gsarti/flores_101), cjvt/slovenian-llm-eval (arc_challenge, hellaswag, piqa), allenai/ai2_arc, Rowan/hellaswag, baber/piqa. Reserved repos (NASK-PIB/RefusEU, XSTest, StrongREJECT) are deliberately never loaded (`common.RESERVED_REPOS`).
- API key: `OPENROUTER_API_KEY` (name only) for `translate_openrouter.py` (google/gemini-2.5-flash) and `judge.py` (openai/gpt-4.1; second judge google/gemini-2.5-flash). Total OpenRouter spend recorded: about $1.66 (`results/api_costs.jsonl`). Optional env var `A1_TOKEN_BUDGET` (teacher-forced batch tokens; the run used 6144 for GaMS3 and 3072 for Gemma in the relaunch, `logs/relaunch_watch.sh`), and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.

## 4. Commands, in order (as run)
Seed: `SEED = 20260923` (`common.py`; also the TPE seed of the Heretic bridge); 20260924 is reserved. Decoding is greedy, 128 new tokens for judged generations. Models load in bnb 4-bit NF4 with double quantization and bf16 compute (Heretic's config), eager attention, system prompt "You are a helpful assistant."
```bash
.venv/bin/python dl_models.py && .venv/bin/python dl_aux.py
.venv/bin/python data_build.py            # JBB twins + LaBSE S1-overlap audit, Dolly, FLORES+, MC carve-out, NLLB, sha1 halves; log logs/data_build.out
.venv/bin/python translate_openrouter.py  # Gemini MT + back-translation chrF, NLLB fallback (8 blocked + 14 truncated = 22/1070 rows)
.venv/bin/python method.py --model gams3 --mini   # optional T4 mini run (results_mini/, superseded)
.venv/bin/python method.py --model gams3 --skip-sensitivity
.venv/bin/python method.py --model gemma --skip-sensitivity
.venv/bin/python judge.py                 # gpt-4.1 blind judge, 1,596 generations
.venv/bin/python heretic_bridge.py --model gams3   # --n-edits defaults to 20
.venv/bin/python heretic_bridge.py --model gemma
.venv/bin/python analysis.py              # analysis + figures.py + build_output.py (method_out.json)
.venv/bin/python analysis.py --recompute  # T8 identical-recompute check
.venv/bin/python verify_numbers.py        # independent plain-Python re-derivation
```
`method.py --until {smoke,mining,select,freeze,halfB,generations,all}` stops early; stages resume from saved outputs. Actual history: each model was first run in full, then killed and relaunched with the amended pipeline (`logs/full_*.out`, `logs/full2_*.out`); the post-freeze raw-energy random-control amendment was added afterwards (`configs/postfreeze_amendment_<m>.json`). The judge's primary outputs were recovered from a log with `judge.py --from-log --no-second` after a fasttext/NumPy-2 crash and key limit (the log file used for recovery is not in the workspace). Gemma also has an earlier 10-edit bridge pass (`results/gemma/heretic_bridge_10edits.json`); the final is 20 edits.
- Runtime (`results/<m>/timings.json`): GaMS3 load 233 s, selection 1531 s, generations 1205 s, raw-random amendment 955 s; Gemma load 232 s, selection 515 s, generations 1672 s, amendment 853 s. README states about 60–80 min per model on the L4; total wall time and bridge runtime not recorded.
- Frozen-protocol integrity: `configs/frozen_protocol_<m>.json` with `.sha256` (GaMS3 `67a0e932…f29d8`); `data/translations.sha256` = `35653b9d…e63b`. Deviations from the plan (4-bit weights, Gemma reduced candidate grid, judge swapped to gpt-4.1, no second judge, no sensitivity arms): `results/deviations.json`.

## 5. Expected outputs and numbers
Everything below is in `results/analysis_summary.json`, `results/screen_verdict.json` (verdict `weak`), `results/verify_numbers.json`, and `method_out.json` (metadata). Note the plan's RefusEU, NASK-PIB and 4-checkpoint Heretic evaluation were **not** part of this screen; only the two original models were used, with Heretic code driving 20 startup edits (no full 200-trial optimization, no released checkpoints).
- Data: 85 JBB twins (15 AdvBench rows dropped by the S1 audit), halves A 44 / B 41; 1,596 judged generations (labels: refused 637, complied 708, partial 39, irrelevant 47, malformed 157, empty 8).
- Frozen sites: GaMS3 layer 34, Gemma layer 20, position −1; cos(d_EN,d_SL) 0.83 / 0.92.
- R validity gate: GaMS3 Spearman 0.511, AUROC 0.697 (fail); Gemma 0.908 / 0.955 (pass).
- Judged refusal on half-B harmful (`verify_numbers.json`): GaMS3 C0 EN 0.902, SL 0.927; after d_EN ablation EN 0.463, SL 0.341; residual gap SL−EN −0.145 [−0.316, 0.028]. Gemma C0 EN 0.829, SL 1.00; after d_EN EN 0.073, SL 0.854; gap +0.765 [0.620, 0.890].
- R-based: GaMS3 I_raw 1.229, F_raw 0.228, F_ctrl 0.195, T(EN→SL) 0.956; Gemma F_raw 0.546, F_ctrl −0.205.
- Heretic bridge mean SL−EN residual gap: GaMS3 0.1085 (16/20 edits positive), Gemma 0.2348 (19/20).
- Bootstrap: 2,000 item-cluster resamples over semantic ids. Recompute check: no differences (`results/recompute_check.json`).
- Figures `figures/fig1`–`fig8` (PDF+PNG); fig8 (judged refusal per condition) is the headline. Paper placement of tables/figures: **not recorded** in this artifact (the paper lives in a separate folder, `4_gen_paper_repo`, of the run; not read).

## 6. Limitations affecting reproduction
No second judge (key limit), no human review, MT-only Slovene, 4-bit weights, n = 2 models, 41 held-out items. Re-running the OpenRouter steps depends on model availability and will not reproduce the judge text bit-for-bit; regenerated Gemini translations may differ from `data/translations.json` (ship these files to skip). GPU generation in batches (left-padded greedy) was accepted with first-4-token agreement, not full identity. To skip expensive stages, use the shipped `results/` files; the `acts_halfA/` caches (about 1.2 GB per model) are regenerable by `method.py`.

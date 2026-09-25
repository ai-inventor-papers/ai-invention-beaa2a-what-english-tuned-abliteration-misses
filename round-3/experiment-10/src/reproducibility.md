# Reproducibility — what was actually run

This describes the run that produced the files in this repository, not an idealised version. Wall clock was ~4 h on one
GPU; **$0.00 of OpenRouter spend** (the run's key was already exhausted before this artifact started — see
`results/deviations.json` D1).

---

## 1. Copy the artifact folder

```bash
cp -r <this folder> ~/depth-coverage-gams3 && cd ~/depth-coverage-gams3
```

Everything the code reads from outside the folder is **read-only** and lives under
`../../../` (paths are constants at the top of `common.py`: `E8`,
`E6`, `E4`, `E1`, `DATASET`). If you relocate those inputs, edit `common.py` — nothing else hard-codes them.

| constant | what is read | why it cannot be regenerated here |
|---|---|---|
| `E8/directions/gams3_all_layers.npz` | the frozen per-layer English refusal directions `d_EN(h)` (49 × 3840) and `d_SL(h)` | reused frozen from iteration 2; this artifact only *asserts* cos ≥ 0.99 against a fresh recompute, it never replaces them |
| `E8/results/judge2_local.jsonl`, `E8/results/judge_cache.jsonl` | iteration-2 local-judge and gpt-4.1 labels | free judge certification + cache reuse for byte-identical generations |
| `E6/third_party/heretic/src/heretic/model.py` | Heretic @ `3521f864` | `heretic_op.py` execs its **own** `abliterate()` source for the operator-equivalence gate |
| `E1/adapters/gams_selected_path2/`, `E1/checkpoints/*/*.jsonl` | the iteration-1 trial-88 LoRA + Optuna journals | the CORE / HER88 / SWAP_in anchors |
| `DATASET/data/splits/*.jsonl` + `split_manifest.json` | the frozen S3/S4 items | SHA-256 verified on every load; S5/S6/S7 are refused by `common.load_split` |

## 2. System, Python, venv

Ubuntu 22.04, Python **3.12.14**, NVIDIA driver 580.126.20 / CUDA 13.0 runtime, `uv` for all package operations (pip is
not installed in the venv).

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

`pyproject.toml` pins all **91** packages to the versions actually used (identical to `results/env_freeze.txt`,
produced by `uv pip freeze`). The load-bearing ones: `torch==2.11.0+cu128`, `transformers==5.17.0`, `peft==0.21.0`,
`bitsandbytes==0.50.2`, `numpy==2.5.2`, `pandas==3.0.6`, `fasttext-wheel==0.9.2`, `scipy==1.18.1`, `pyarrow==25.0.1`.
The CUDA 12.8 torch wheel comes from the `[tool.uv] extra-index-url` already declared in `pyproject.toml`.

**Thread pinning matters.** Every script sets `OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=4` at import. On the shared 48-core
host an unpinned 276×3840 SVD took **35 s** instead of 0.2 s, which would have made the control construction and the
bootstraps dominate the run (`results/deviations.json` D7).

## 3. Models, data and environment variables

Downloaded into the run's shared HuggingFace cache (`python dl_models.py`, ~2 min):

```bash
huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc
huggingface-cli download Qwen/Qwen3-14B          --revision 40c069824f4251a91eefaf281ebe4c544efd3e18
huggingface-cli download cis-lmu/glotlid         --revision 85cd6716494360367b75f642b5bc78667605d0b4   # model.bin
```

Environment variables read (**names only, never values**): `HF_HOME`, `HF_HUB_CACHE`, `HF_DATASETS_CACHE`, `TORCH_HOME`,
`UV_CACHE_DIR` (all pre-set to the run's shared cache — do **not** point `HF_HOME` and `TRANSFORMERS_CACHE` at the same
directory or every weight is stored twice); `HF_TOKEN`; `OPENROUTER_BASE_URL` and `OPENROUTER_API_KEY` (only
`judge_api.py` and `cert_pool.py`'s probe would use them — **no paid call was made**); optional `AII_MINI=1` to send every
output of every script into `results_mini/`, and `AII_DEADLINE` (unix epoch) to stop `method.py --stage B` before it
starts another cell.

## 4. The exact commands, in order

Seed **20260923** everywhere (`common.SEED`); greedy decoding; 4-bit NF4 with bf16 compute; identical chat template and
system prompt (`"You are a helpful assistant."`) in both languages. Hardware: **1 × NVIDIA L4, 22 GB**, 48-core host.

```bash
# 0. smoke test on 6 items per set, into results_mini/ (~6 min)
AII_MINI=1 .venv/bin/python method.py --stage A --mini
AII_MINI=1 .venv/bin/python judge_local.py

# 1. free certification of the local judge against gpt-4.1 labels already on disk (CPU, ~1 min)
.venv/bin/python cert_pool.py                     # -> results/judge_cert_pool.json

# 2. PART A (~28 min GPU): gates -> half-A capture -> matched controls -> operator/energy gates ->
#    matched-energy design -> 22 DEV activation arms
.venv/bin/python method.py --stage A

# 3. judge the DEV arms, then FREEZE (the freeze MUST precede any confirmation generation)
.venv/bin/python judge_local.py --splits dev dev_ben      # ~10 min GPU
.venv/bin/python freeze.py                                # -> results/redundancy_index.json,
                                                          #    results/frozen_predictions.json, configs/FREEZE.sha256

# 4. PART B, decisive cells first (~2 h GPU), then judge them (~43 min GPU)
bash run_chain2.sh $(( $(date +%s) + 7200 ))              # T1 (22 matched-energy cells) + T2 (3 anchors) -> judge
# 5. the T3 coverage grid that widens the regression's energy x coverage range (~12 min GPU) + judge (~5 min)
bash run_chain3.sh $(( $(date +%s) + 3000 ))

# 6. everything downstream is CPU-only (~5 min)
bash finish.sh    # data_usage -> analysis -> cross_model -> deviations -> report_tables -> figures ->
                  # build_output -> rederive (the independent audit) -> make_readme
```

`run_chain2.sh` was launched a second time after the first attempt was stopped to lower `GEN_BS` from 96 to 64 (a 192-token
confirmation batch OOM'd at 96 and the halving fallback was costing ~20 s per call). Cells are resumable per
`results/cells/<cell>/gens.json`, so nothing was regenerated.

Measured throughput, for planning a rerun: **0.5 s/generation** at 128 new tokens and 0.73 s at 192 (batch 64);
**62 s** per full teacher-forced collateral pass (FLORES + Dolly KL + MC); **~70 s** per energy table (96 modules ×
24 grid points); **0.45 s/item** for the local judge. `results/timings.json` has all 60 timed stages (2.9 h of timed GPU
work); `results/smoke.json` has the measured 0.67 s/gen used for the up-front extrapolation.

## 5. What a reader should get, and where it appears

| file | what it holds |
|---|---|
| `results/redundancy_index.json` | index_EN **16** [16, 16], index_SL **20** [16, 24], difference 4 [0, 8]; the usable index **>48** in both languages; prefix / suffix / LOBO curves; frozen before any confirmation data |
| `results/frozen_predictions.json` + `configs/FREEZE.sha256` | PA1–PB4 verbatim, hashed with timestamps; `rederive.py` asserts the hash file predates the first confirmation generation |
| `results/analysis_summary.json` | every per-cell 4-way rate with item-cluster bootstrap CIs, McNemar vs no-op, the frozen-prediction verdicts, the nested R² decomposition, judge sensitivity |
| `results/report_tables.md` | all tables (A DEV index, B per-cell panel, C frozen predictions, D judge sensitivity, E cross-model), generated — never typed |
| `results/rederive.json` | the independent audit: **481/481** headline numbers matched, freeze order PASS, three placebos |
| `results/cross_model.json` | the joint GaMS3 / Gemma depth table (the Gemma column comes from the sibling iteration-3 pod) |
| `results/deviations.json` | 9 departures from the plan, each with its evidence file |
| `results/data_usage.json` | what was done with every block of the frozen dataset, and why S5/S6/S7 were never opened |
| `figures/fig1…fig6` | coverage curve (+ the INVALID panel), matched energy, index-vs-residual, LOBO, refusal-vs-collateral Pareto, judge sensitivity |
| `method_out.json` (+ full/mini/preview) | the comparison table: **462 items × 56 methods = 10,690 per-item outcomes**. One example per (split, semantic item, language); `output` is the unedited model's frozen 4-way class and each `predict_<method>` is the class the SAME item got under one intervention (band edits, matched-energy spread edits, random / PC controls, depth-coverage activation arms, the shipped Heretic edit). Each method's generated text sits beside it in `metadata_response_<method>`, with its gpt-4.1 label, rule label and GlotLID language where available. |

**Headline numbers to expect** (all in `README.md` and `results/report_tables.md`):

- PA1 **EQUIVALENT_WITHIN_MARGIN** — index_SL − index_EN = 4, CI [0, 8] against the ±8 margin (Holm p 0.069).
- PB2 **FALSIFIED_OPPOSITE_DIRECTION** — narrow-and-strong minus broad-and-weak Slovene refusal = **−0.10 [−0.150, −0.060]**
  (n = 70 held-out-category items); concentrating beats spreading, the opposite of the prediction (Holm p 0.000).
- PB3 **FALSIFIED_OPPOSITE_DIRECTION** — coverage×language interaction **−0.07 [−0.131, −0.007]** (Holm p 0.069).
- PB1 **NOT_SUPPORTED** — coverage ΔR² = 0.002 [0.000, 0.010] over 26 weight cells; leave-one-cell-out ΔR² = **−0.043**.
  Nested decomposition: log E alone R² 0.325 → +placement (band energy fractions) **0.718** → +covered-layer count 0.400.
- PB4 **NOT_SUPPORTED** — Spearman 0.21 (n = 32 cell×language points).
- Placement at matched energy **and** matched layer count (12 contiguous vs every 4th): Slovene 0.24 vs 0.81 in the
  highest-energy group.
- Controls are null: layer-matched random and energy-matched PC leave Slovene refusal at **0.93–0.95** on the screen
  set and 0.87–0.97 on the confirmation set, against a no-op of 0.93 (screen) / 0.96 (confirmation).

**Bit-exactness caveats.** Generations are greedy but 4-bit NF4 matmuls are not bit-stable across GPU models, so a rerun
on a different card reproduces strings, not bytes: this run reproduced iteration-2's no-op GaMS3 generations on
**87.5 %** of the overlapping ids over the first 60 characters (`results/smoke.json`), which is the expected drift, not a
failure. Judged *rates* are stable to within the reported CIs; individual borderline items can flip. The operator gates
are exact and must reproduce: Heretic-equivalence max relative error **1.7e-06**, trial-88 adapter rebuild median
**3.3e-07**, energy identity < 1e-06 (`configs/design.json → gates`).

## 6. Auditing it yourself

The pivoted `method_out.json` can be checked against the analysis without any project code:

```bash
.venv/bin/python - <<'PY'
import json, numpy as np
ex = {d['dataset']: d['examples'] for d in json.load(open('method_out.json'))['datasets']}['S4_strongreject_hoc_CONFIRM_harmful']
narrow = [f'band_{b}_matchedE_{g}' for g in ('E1','E2','E3') for b in ('13_24','25_36')]
broad  = [f'{b}_matchedE_{g}'      for g in ('E1','E2','E3') for b in ('spread_stride2','spread_all48')]
def per(lang, ms):
    by = {}
    for e in ex:
        if e['metadata_lang'] == lang: by.setdefault(e['metadata_semantic_id'], []).extend(
            e['predict_' + m] == 'REFUSED' for m in ms if 'predict_' + m in e)
    return {k: np.mean(v) for k, v in by.items()}
a, b = per('sl', narrow), per('sl', broad)
print('SL narrow-broad = %.4f over n=%d items' % (np.mean([a[k]-b[k] for k in a]), len(a)))   # -> -0.1048
PY
```

```bash
.venv/bin/python rederive.py     # re-reads results/cells/*/gens.json + the judge cache and recomputes every headline
                                 # number through a code path that imports nothing from analysis.py/common.py/labels.py
```

It prints `rederive: 481/481 headline numbers match; freeze order ok=True` and writes `results/rederive.json` with the
three placebos, which must collapse (they do: cell-label-within-item 0.003, language-label −0.001, energy-shuffled 0.023,
against real effects of −0.105 and −0.071). It exits non-zero on any mismatch.

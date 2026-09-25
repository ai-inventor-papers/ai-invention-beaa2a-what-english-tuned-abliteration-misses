# Reproducibility

This describes what was **actually run**, in order, on one NVIDIA L4 (23 GB VRAM) attached to a 48-core Linux host
(Ubuntu 22.04, kernel 6.8), in about 4 h 20 min of wall clock.

## 1. Get this artifact

This folder is one folder of a public GitHub repository. Clone the repository and `cd` into this folder:

```bash
git clone <this repository>
cd <repository>/gen_art_experiment_14      # this artifact's folder
```

Every path in this document, in the code and in the result files is **relative** to this folder. Nothing here refers
to the machine the experiments ran on.

## 2. Inputs produced by other artifacts of the same run

This pod reads (never writes) files from sibling folders of the same repository. `common.dep()` resolves each one in
this order: `$AII_DEPS_ROOT/<folder>`, then `../<folder>` (the published layout), then the original run-volume layout.
If you keep the sibling folders next to this one, nothing needs to be set; otherwise:

```bash
export AII_DEPS_ROOT=/path/that/contains/the/sibling/artifact/folders
```

| folder | artifact id | what is read |
|---|---|---|
| `gen_art_dataset_1` | `art_qdUCJWbc5kHh` | the frozen EN/SL data protocol: `data/splits/S3_jbb.jsonl`, `S3_dolly.jsonl`, `S3_flores_dev.jsonl`, `S3_mc.jsonl`, `S4_strongreject_pairs.jsonl` and `data/split_manifest.json` (every SHA256 is verified at load time) |
| `gen_art_experiment_8` | `art_hmbXDppkPZnR` | `directions/gams3_all_layers.npz` — the frozen per-layer English refusal directions `d_EN(h)`; also the generation engine `interventions.py` and the judge cache used for label re-use |
| `gen_art_experiment_6` | (Heretic mirror) | `third_party/heretic/src/heretic/model.py` at SHA `3521f864` — executed verbatim for the operator-equivalence gate |
| `gen_art_experiment_1` | `art_vzhOPupFwE4M` | the shipped GaMS3 LoRA adapter (`adapters/gams_selected_path2/`), both Optuna journals and `directions/gams/directions.pt` |
| `gen_art_experiment_10` | `art_xLy2vVlI7OEL` | the 57-cell iteration-3 GaMS3 panel (screen, anchors A1/A2/no-op/G1) and its judge cache |
| `gen_art_experiment_9` | `art_ex4hbgThhJaL` | the sibling-checkpoint panel: `results/cells.csv`, `results/energy_real.json` (mis-specification screen) |
| `gen_art_experiment_11` | `art_0XmNBGkzsJc_` | `scorer/refusal_clf.joblib` — the free third label channel |

Nothing in this pod comes from the user's private uploads, so no private data has to be supplied.
`results/inputs_manifest.json` lists every one of these files with its SHA256, an exists-flag and a named recovery
path if it is missing.

## 3. Environment

```bash
sudo apt-get install -y build-essential git          # only needed if a wheel has to build from source
curl -LsSf https://astral.sh/uv/install.sh | sh      # uv; pip is not used anywhere in this repository
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml
```

`pyproject.toml` pins all 114 packages to the exact versions used (`results/env_freeze.txt` is the raw
`uv pip freeze`). The important ones: `torch==2.11.0+cu128` (from the extra index declared in `pyproject.toml`),
`transformers==5.17.0`, `peft==0.21.0`, `bitsandbytes==0.50.2`, `numpy==2.5.2`, `scipy==1.18.1`, `fasttext-wheel==0.9.2`.
The last seven entries (`pydantic`, `pydantic-settings`, `tomli-w`, `datasets`, `optuna`, `questionary`, `py-cpuinfo`)
are needed **only** by `third_channel.py`, because the classifier bundle it loads pickles Heretic config objects.

## 4. Models and credentials

Weights are pulled from the HuggingFace Hub into whatever `HF_HOME` / `HF_HUB_CACHE` point at (about 16 GB):

```bash
huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc
huggingface-cli download Qwen/Qwen3-14B        --revision 40c069824f4251a91eefaf281ebe4c544efd3e18
huggingface-cli download cis-lmu/glotlid       --revision 85cd6716494360367b75f642b5bc78667605d0b4
```

Environment variables used, **by name only**: `HF_HOME`, `HF_HUB_CACHE` (weight cache), `AII_DEPS_ROOT` (optional,
section 2), `AII_DEADLINE` (optional unix timestamp after which a stage stops starting new cells),
`OPENROUTER_BASE_URL` and `OPENROUTER_API_KEY` (used only by `certify.py`; see section 6 — in this run they bought
nothing).

## 5. The exact commands, in order

`run_chain.sh` contains exactly this sequence; it was executed stage by stage, each stage in the background with
PID-based management. Seeds: a single seed, `20260923` (`common.SEED`), is used for the operator's SVD, the control
draws, the stratified certification sample and every bootstrap.

```bash
PY=.venv/bin/python
$PY method.py --stage smoke      # ~6 min GPU: gates 0/1/3/4, control directions, the dEN energy table, timing model
$PY method.py --stage profile    # ~55 min GPU: the strength pilot (c = 1.0 -> 1.5 -> 2.5) + 48 single-layer probes
$PY judge_local.py --include 'dev_L[0-9]+_c2\.5|dev_NOOP|^R_|^A1_|^A2_'   # ~12 min GPU: the blind local judge
$PY freeze.py                    # CPU: e_L(h) -> O -> 28 frozen cells -> configs/FREEZE.sha256
$PY method.py --stage reuse      # CPU: re-label (never regenerate) the iteration-3 anchors
$PY screen.py                    # CPU: the 57-cell screen + the sibling mis-specification arm
$PY method.py --stage confirm    # ~80 min GPU: the frozen panel, 6 controls, the A3/A4 twins
$PY method.py --stage confirm    # ~10 min GPU: a second pass picks up configs/post_freeze_cells.json
$PY judge_local.py               # ~31 min GPU: label everything generated since
$PY cert_pool.py && $PY certify.py --n 600   # judge certification (see section 6)
$PY gate_freeze_test.py && $PY third_channel.py
$PY analysis.py && $PY rederive.py
$PY make_deviations.py && $PY report_tables.py && $PY figures.py && $PY build_output.py
$PY make_cells_csv.py && $PY make_readme.py
```

Every stage is resumable: each cell writes `results/cells/<cell>/{gens,meta,tf}.json` as it finishes, and a re-run
skips whatever is already complete. `method.py --stage confirm` **raises** unless `configs/FREEZE.sha256` exists and
matches `configs/frozen_predictions.json`; `gate_freeze_test.py` proves that on a scratch copy.

Timing on the hardware above: 6 + 55 + 12 + 80 + 10 + 31 min of GPU work plus about 15 min of CPU analysis.
Generation is greedy, 128 new tokens on DEV and 192 on the confirmation harmful split, batch 64, one frozen bucket
schedule for every cell including the no-op.

## 6. What a reader will and will not be able to reproduce exactly

* **Judge certification.** `certify.py` tries to buy a stratified 600-item `openai/gpt-4.1` subsample through
  OpenRouter (hard cap $3.00). In this run every call returned `aii_openrouter_key_limit` — the platform's shared key
  had hit its daily limit — so **$0.00 was spent** and certification fell back to the gpt-4.1 labels already on disk
  for GaMS3 edited arms (`cert_pool.py` -> `results/judge_cert_pool.json`). A reader with a working key will get the
  first path and a slightly different `results/judge_cert.json`; the fallback numbers quoted in the README are from
  the second path and are labelled as such.
* **Bitwise generations.** Greedy decoding on 4-bit NF4 is not bit-reproducible across GPU models, and batched
  generation differs slightly from single-sequence generation. `results/gate3_anchor.json` measures this directly:
  re-generating two stored iteration-3 cells reproduced 0.92 (no-op) and 0.71 (an edited cell) of the first 60
  characters. Rates move by a point or two; the panel's ordering does not (see `results/third_channel.json`, where a
  completely different scorer ranks the cells at Spearman 0.98 in Slovene).

## 7. Outputs a reader should get, and where they appear

| file | what it holds |
|---|---|
| `method_out.json` (+ `full_`, `mini_`, `preview_`) | 462 examples x 56 conditions in the `exp_gen_sol_out` schema: `output` is the unedited model's 4-way class, one `predict_<condition>` per condition |
| `configs/frozen_predictions.json` + `configs/FREEZE.sha256` | the frozen profile, overlap formula, 28 cell specifications, predicted O and rank, named band, thresholds |
| `results/analysis_summary.json` | every number in the paper: primary rank statistic, nested R² with leave-one-cell-out, competitor races, argmax check, controls, dissociation, metric dependence, placebos, Holm, verdict |
| `results/report_tables.md` | the paste-ready tables (each caption names the file that produced it) |
| `results/rederive.json` | the independent re-derivation: **352/352** headline numbers reproduced, freeze-order check PASS |
| `results/cells.csv`, `results/per_item.parquet` | one flat row per cell / per generation |
| `figures/fig1..fig5` | write profile; O vs outcome with competitors; matched-energy bands; the placement/dose ladder; refusal removal against collateral |
| `results/deviations.json` | all 10 departures from the plan, each with its evidence file |

Headline numbers, as they appear in the README and the paper: Spearman(O, surviving Slovene refusal) = **−0.903**
(95% CI [−0.928, −0.857], permutation p < 0.001) over the 20 confirmation cells; ΔR² of O over log removal energy
**0.580** (leave-one-cell-out 0.594); the cheaper `O_band4` and `O_cos` reach LOO ΔR² 0.845 and 0.834; the four
matched-energy bands at E = 27.8 give Slovene strict refusal 0.97 / 0.30 / 0.53 / 0.94 for 1-12 / 13-24 / 25-36 /
37-48 against a no-op of 0.957; all six controls are null (|Δ| ≤ 0.03); the placement/dose ladder gives −0.186 and
−0.157 for dose at fixed placement (McNemar p = 0.001, 0.003) and −0.029 / 0.000 for placement at fixed dose.

## 8. Re-running only the analysis

The analysis never touches the GPU and takes about three minutes from the saved generations:

```bash
.venv/bin/python analysis.py && .venv/bin/python rederive.py
.venv/bin/python report_tables.py && .venv/bin/python figures.py && .venv/bin/python build_output.py
```

`rederive.py` imports nothing from `analysis.py`, `alib.py`, `labels.py` or `common.py`: it re-reads the raw
generations, re-applies the 4-way mapping, re-runs GlotLID and implements its own Spearman, OLS and bootstrap.

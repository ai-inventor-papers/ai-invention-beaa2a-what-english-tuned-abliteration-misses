# Reproducibility: matched Heretic runs on GaMS3-12B-Instruct vs gemma-3-12b-it

Everything below is taken from the files in this folder (`README.md`, `method.py`, `drive_heretic.py`,
`pyproject.toml`, `env/requirements.lock`, `pins.json`, `protocol_*.json`, `logs/timing_decision.json`,
`results/*.json`). Nothing was re-run when writing it. Where the workspace is silent, this says so.

## 1. Get the artifact

The workspace is one folder of a public GitHub repository. The repository URL is not recorded in the
workspace. Clone it, then `cd` into this folder (`gen_art_experiment_1`). All commands below run from
that folder and use relative paths only.

Note: `README.md`, `results/status.json` and some result JSONs contain absolute `/ai-inventor/...`
paths from the original server. They are provenance strings only. The code anchors on
`Path(__file__)`, so it does not need them.

## 2. System and Python environment

- OS: Ubuntu Linux. The exact release is not recorded.
- Python 3.12 (`requires-python = ">=3.12"`; the README uses `--python=3.12`). The patch version is not recorded.
- `uv` is the installer. No other system packages are recorded. A git client is needed because
  Heretic installs from a git commit.
- `method.py` launches its sub-scripts with `.venv/bin/python`, so the venv must be named `.venv`:

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r env/requirements.lock
```

`env/requirements.lock` and the `dependencies` list in `pyproject.toml` hold the same pins. Key pins:

| package | version |
| --- | --- |
| heretic-llm | `git+https://github.com/p-e-w/heretic@3521f8648a0dccf6e12a92666862632235fac7e6` (version 2.0.0.dev0) |
| torch / torchvision | 2.11.0+cu128 / 0.26.0+cu128 |
| transformers | 5.17.0 |
| bitsandbytes | 0.50.2 |
| peft | 0.21.0 |
| accelerate | 1.15.0 |
| optuna | 4.9.0 |
| lm-eval | 0.4.13 |
| datasets | 4.8.5 |
| numpy / scipy / pandas / scikit-learn | 2.5.3 / 1.18.1 / 3.0.6 / 1.9.1 |
| sacrebleu / langdetect / matplotlib | 2.6.0 / 1.0.9 / 3.11.2 |

The torch pin has a `+cu128` local tag. It may need the PyTorch cu128 wheel index
(`--extra-index-url https://download.pytorch.org/whl/cu128`). The workspace does not record how the
original install resolved it.

The exact Heretic sources that were used are in `env/heretic_src/` (`config.py`, `main.py`, `model.py`).

## 3. Downloads, keys and environment variables

Models and datasets are fetched from the HuggingFace Hub at the revisions pinned in `pins.json`.
Weights are not stored in this repo.

| item | revision |
| --- | --- |
| `cjvt/GaMS3-12B-Instruct` | `1d0b27af5748784482600d24779409e7e1dc9adc` |
| `google/gemma-3-12b-it` (gated, manual approval) | `96b6f1eccf38110c56df3a15bffe176da04bfd80` |
| `google/gemma-3-1b-it` (driver smoke test only) | `dcc83ea841ab6100d6b47a070329e1ba4cf78752` |
| `facebook/nllb-200-distilled-1.3B` (Slovene translation) | `7be3e24664b38ce1cac29b8aeed6911aa0cf0576` |
| dataset `mlabonne/harmful_behaviors` | `01cead01398926d81f7c52bdb790ee8cf77ebba7` |
| dataset `mlabonne/harmless_alpaca` | `02c6a92cfcf11bb0c387334f8146d149d65b587f` |
| dataset `openlanguagedata/flores_plus` | `5fec6c13f9e5a4db2f745d4ec0d7c9721ddc4f06` |

- A helper to pre-download a model is `scratch/dl.py <repo>` (it calls `snapshot_download` at the
  current Hub sha). The README shows how to recreate it.
- Gemma access needs a HuggingFace account that has accepted the Gemma licence. The token variable
  name is not recorded in the code. Use the standard `huggingface-cli login` or `HF_TOKEN`.
- `OPENROUTER_API_KEY` is read only by `judge_sl.py` and `translate_sl.py` (the API translator pass
  kept for provenance). It is NOT needed for the core results. Supply your own key by name only.
  The key used in the original run returned HTTP 403 "Key limit exceeded".
- Bundled data (no download needed): `data/flores_plus_dev200.json`,
  `data/sl_harmful_behaviors_test100.json` (NLLB Slovene translation), `data/sl_nllb_pass.json`,
  `data/sl_api_translator_pass1.json`, `data/heretic_default_sources.json`.
- No user-uploaded private input is used.
- The Slovene translation can be regenerated with `.venv/bin/python translate_nllb.py`. The exact
  arguments are not recorded.

## 4. Commands, seeds, configs, hardware

Hardware, from `env/hardware.txt` and `logs/timing_decision.json`:
- 1x NVIDIA L4, 23,034 MiB VRAM, driver 570.195.03, CUDA 12.8.
- 48 CPU cores, about 503 GB host RAM shown by `free`. The README says the pod had about 57 GB, and
  `hardware.txt` shows a cgroup limit of 61,999,996,928 bytes.
- Measured: mean trial about 39.3 s, peak VRAM about 15.1 GB, model load about 330 s.
- Planned cost: about 131 GPU-min per 200-trial model. The trial budget was cut to 116 per model
  (see below). Total wall time is not recorded beyond the timing decision. `--budget-min 240` was the
  budget passed in the README example.

Fixed settings in the code:
- Seed `20260923` (`drive_heretic.py`, `pins.json`). `20260924` was reserved and never used.
- Heretic flags: `--quantization bnb_4bit`, `--seed 20260923`, `--batch-size 128`, and a per-model
  `--study-checkpoint-dir` under `checkpoints/`.
- Phase A: `--n-trials 60 --n-additional-trials 140`.
- Selection rule `protocol_selection.json`: minimise KL subject to at most 10 refusals/100.
  Fallback 1: minimise refusals subject to KL <= 1.0. Fallback 2: Pareto point minimising
  sqrt(ref² + KL²). Fallback 1 fired for both models.
- A3 screen rule: `protocol_a3.json`.
- Bootstrap seeds are set inside `analyze.py`, `efficiency.py` and `audit_efficiency.py`
  (`np.random.default_rng(seed)` with seeds 0 and 11; langdetect `DetectorFactory.seed = 0`).
- Refusal is Heretic's English keyword proxy. Slovene refusal uses a marker list
  (`results/sl_marker_validation.json`).

Full pipeline (this is what `method.py --stages all` does):

```bash
uv run method.py --stages all --budget-min 240
```

Its order is `phaseA_gams, phaseA_gemma, a3, phaseB_gams, phaseB_gemma, eval_gams, eval_gemma, analyze, figures`.
Stages are idempotent. `phaseA_*` skips if a journal already exists.

How the run actually went, from `logs/timing_decision.json`. The stored `n_additional_trials=140`
overrode the CLI cap on resume, so GaMS was stopped by SIGINT after 116 complete trials (trial 116 is
PRUNED and excluded everywhere). `--stop-at-trials` was then added to `drive_heretic.py` and Gemma was
run to exactly 116 complete trials. To match the run, use:

```bash
.venv/bin/python drive_heretic.py gams A --batch-size 128
.venv/bin/python drive_heretic.py gemma A --batch-size 128
.venv/bin/python a3_screen.py
.venv/bin/python drive_heretic.py gams B --batch-size 128 --stop-at-trials 116
.venv/bin/python drive_heretic.py gemma B --batch-size 128 --stop-at-trials 116
.venv/bin/python swap_eval.py gams
.venv/bin/python swap_eval.py gemma
.venv/bin/python analyze.py
.venv/bin/python figures.py
```

`swap_eval.py` defaults: `--conds orig,own,swap --retest 0,1,2 --flores-n 200`.

Post-hoc scripts, added after the first README draft. Their exact invocation order is not logged;
each takes no required arguments unless shown:

```bash
.venv/bin/python a3_screen.py --synthetic       # guard validation -> results/a3_synthetic_T4.json
.venv/bin/python efficiency.py                  # -> results/efficiency.json
.venv/bin/python direction_compare.py           # -> results/direction_geometry.json
.venv/bin/python sl_label_sample.py sample      # 40 items; the "hand" labels were filled by the executor
.venv/bin/python sl_label_sample.py score       # -> results/sl_marker_validation.json
.venv/bin/python audit.py                       # -> results/audit.json
.venv/bin/python audit_efficiency.py            # -> results/audit_efficiency.json
.venv/bin/python to_schema.py                   # reshapes method_out.json to the schema
OPENROUTER_API_KEY=<your key> .venv/bin/python judge_sl.py   # optional, was blocked (results/judge_sl.json)
```

Interactive prompts of Heretic are scripted by `drive_heretic.py`. Transcripts are in
`logs/interactive_*.jsonl` and the inventory is in `env/interactive_prompts.txt`. An unscripted prompt
exits with code 3.

Resuming a journal to the default 200 trials: `uv run method.py --stages phaseB_<gams|gemma>`.

Reproduction caveats:
- The 116-trial journals are included: `checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl` and
  `checkpoints/gemma/google--gemma-3-12b-it.jsonl`.
- Re-running the search from scratch depends on GPU numerics (L4, bnb 4-bit). Bit-identical trial
  results on other hardware are not guaranteed and were not tested.
- The selected edits are shipped as LoRA adapters (`adapters/gams_selected`, `adapters/gemma_selected`,
  plus `*_path2` copies with `SHA256SUMS.json`). Trials 88 (GaMS) and 96 (Gemma) were selected.

## 5. Expected outputs and numbers

Each number is in `README.md` (Results) and `method_out.json`. `results/audit.json` and
`results/audit_efficiency.json` re-derive them. The workspace contains no paper text, so the mapping
to paper sections is not recorded. Figures are in `figures/`.

| checkpoint | EN refusals /100 | SL refusals /100 | mean KL |
| --- | --- | --- | --- |
| GaMS original | 98 | 97 | 0 |
| GaMS + own edit (trial 88) | 16 | 10 | 0.175 |
| GaMS + Gemma's parameters | 25 | 25 | 0.046 |
| Gemma original | 100 | 97 | 0 |
| Gemma + own edit (trial 96) | 69 | 90 | 0.024 |
| Gemma + GaMS's parameters | 53 | 25 | 0.254 |

Other numbers:
- Own edits re-score to journal values (KL relative difference 2e-8).
- On the 60 shared edits: Gemma refuses more in 60/60. The paired median difference is +25/100
  (CI [10, 43]). The KL Spearman rho is 0.967. The efficiency ratio is 13.4 (CI [7.0, 30.0]).
  The A3 refusal rho is 0.781.
- The audit reports 28/28 checks matching.
- Direction cosine: mean 0.63, layers 24-47 0.57, harmless means 0.98, random control 0.014.
- Marker validation against 40 hand labels: accuracy 0.75, kappa 0.48.
- Outputs: `results/eval/{gams,gemma}_{orig,own,swap}.json`, `results/trials_*.csv`,
  `results/a3_screen.json`, `results/selection_*.json`, `figures/fig1..fig4` (PNG and PDF).

## Limits and unrecorded items

- Two models are two units; one optimizer seed each; 4-bit NF4 and a 116-trial budget are confounded
  with Gemma's resistance to the edit.
- Slovene refusal is marker-only (`NATIVE_REVIEW_PENDING`). The LLM judge result is empty
  (0/600 judgements succeeded).
- Not recorded: the GitHub URL, the exact Ubuntu and Python patch versions, the HF token variable
  name, total wall-clock time, and the exact command line for each post-hoc script.

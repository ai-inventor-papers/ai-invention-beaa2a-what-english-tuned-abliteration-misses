# Reproducibility: utility cost and inner harm signal after abliteration (`gen_art_experiment_5`)

Everything below is taken from the files in this folder (`README.md`, `pyproject.toml`, `env/`, `configs/`, `run_*.sh`, `common.py`, the stage scripts and `logs/`). Items the workspace does not record are marked **not recorded**.

## 1. Get the artifact

The workspace is one folder of a public GitHub repository. Clone it (URL not recorded in the workspace) and `cd` into `gen_art_experiment_5`.

**Inputs from other artifacts (published as sibling folders of the same run, iteration 1).** `common.py` reads them in place through one constant, `RUN` (line 28), which is an absolute server path (`../../../round-1`). A reader must edit that one line to the local location of the iteration-1 folders:

| constant | folder (artifact id) | what is read |
|---|---|---|
| `E1` | `gen_art_experiment_1` | Heretic LoRA adapters `adapters/gams_selected_path2` (trial 88) and `adapters/gemma_selected_path2` (trial 96), plus `adapters/*_selected` |
| `E3` | `gen_art_experiment_3` | frozen probe sites, prefix sets, judge rubric |
| `DS` | `gen_art_dataset_1` | frozen data protocol: `data/splits` (S3/S4/S5/S5X/S7 splits) and `temp/datasets` (raw data) |

Adapter SHA-256 (from `configs/protocol_c1u.yaml`): GaMS `a4419c5140ca706d9075045da1c12f0f62b847fce5acdcb41cf5ce3c09506330`, Gemma `d219c084b84370cd972700fa07d754777b2fd56dc12257cd0e67498b2d0f2b01`. No private user-uploaded input is used. I did not check the sibling folders' contents.

## 2. System, Python and libraries

- Ubuntu; Python 3.12 (`requires-python = ">=3.12,<3.13"`); `uv` for the venv. Other apt packages: not recorded.
- Exact pins: `pyproject.toml` / `env/requirements.lock` (identical). Key ones: torch 2.11.0+cu128, torchvision 0.26.0+cu128, transformers 5.17.0, peft 0.21.0, bitsandbytes 0.50.2, accelerate 1.15.0, lm-eval 0.4.13, numpy 2.5.2, pandas 3.0.6, scikit-learn 1.9.1, scipy 1.18.1, statsmodels 0.15.0, datasets 4.8.5, matplotlib 3.11.2, optuna 4.9.0, heretic-llm from `git+https://github.com/p-e-w/heretic@3521f8648a0dccf6e12a92666862632235fac7e6`.

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml
export NUMPY_MADVISE_HUGEPAGE=0
```

## 3. Models, data, environment variables

- Models (Hugging Face, pinned revisions; the HF token/cache setup is not recorded): `cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc`, `google/gemma-3-12b-it@96b6f1eccf38110c56df3a15bffe176da04bfd80`, bonus `cjvt/GaMS3-12B@46127695de173a5de72e1da9dc43846f58553477`. Loaded in NF4 (`load_in_4bit`, `nf4`, bf16 compute, double quant). "Original" = PeftModel with adapter disabled, "edited" = enabled, one load per model.
- Data: the iteration-1 dataset artifact (above) and the lm-eval tasks (EN); Slovene tasks are the GaMS-Team files in `third_party/sleval_tasks/` (commit d05d470f). Exact download URLs/commands for benchmark data: not recorded.
- Env var names (values never stored): `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL` (both read by `judge.py`, `base_diag.py`, `dose_judge.py`; needed only for judging). Optional: `C1U_TOKEN_BUDGET` (default 8192), `NUMPY_MADVISE_HUGEPAGE=0`.
- Judges: `openai/gpt-4.1` (primary, temperature 0) and `nvidia/nemotron-3-ultra-550b-a55b:free` (second; the plan's gemini-2.5-flash was replaced when the run budget ran out). Re-running the judges will not give identical labels; judged labels are saved in `results/judge/` and `results/judged_generations.jsonl`.

## 4. Commands, seeds, hardware, runtime

Seed: `SEED = 20260923` (`common.py`); bootstrap B = 2000, clustered by semantic id; decoding greedy; system prompt "You are a helpful assistant."; generation lengths s4 64, H100 128, r_prior 64, KL ref 32, R_seq refs 24. Frozen protocol: `configs/protocol_c1u.yaml` (sha256 in `.sha256`), utility sample ids `configs/utility_sample_ids.json` (250 per task, sha256 `53873f78…`).

Commands as run (also in README "How to run"; `run_*.sh` are the actual chains):

```bash
.venv/bin/python freeze_protocol.py
.venv/bin/python method.py --model gams  --stages check,gen,acts,kl,hval,util,flores,s5acts,rseq
.venv/bin/python method.py --model gemma --stages check,gen,acts,kl,hval,util,flores,s5acts,rseq
.venv/bin/python mech.py --model gams && .venv/bin/python mech.py --model gemma
.venv/bin/python mech_extra.py --model gams && .venv/bin/python mech_extra.py --model gemma
.venv/bin/python judge.py --wait-for-key 240 --second            # run_judge.sh
.venv/bin/python judge.py --second-only --judge2-fill --harmless-only   # run_judge2_fill.sh
.venv/bin/python base_diag.py                                     # run_chain2.sh
.venv/bin/python readouts.py --source judge
.venv/bin/python method.py --model gams --stages rseq && .venv/bin/python method.py --model gemma --stages rseq
.venv/bin/python dose.py --model gemma && .venv/bin/python dose.py --model gams   # run_dose.sh
.venv/bin/python analyze.py && .venv/bin/python report_tables.py && .venv/bin/python figures.py
.venv/bin/python review_packet.py && .venv/bin/python verify_numbers.py && .venv/bin/python audit_headline.py && .venv/bin/python build_output.py
```
Notes: `dose_judge.py` was prepared but not run (free-tier cap). The `mech.py`/`mech_extra.py` runs need the full float32 activation captures `acts/`, which were deleted after analysis (GitHub size limit); regenerate with `method.py --model <m> --stages acts,s5acts` (~10 GPU-min per model). `analyze.py` runs from the kept `acts_primary/` slices and cached `results/<m>/r_prior_<m>.{json,npz}`. The `audit_headline.py` invocation order is not recorded in a script; it reads raw files only.

Hardware (`env/gpu.txt`): the interrupted first session used an NVIDIA L4 23 GB (GaMS check/gen/acts/kl/hval); the final session an RTX 4090 24 GB (rest of GaMS, all Gemma, base_diag, dose); both Ada sm_89, driver 580.x. Each paired original-vs-edit quantity came from one session and model load. Runtime (`logs/timing_decision.json`, GaMS, s): load ~100, acts 157, kl 159, hval 1385, util 444, flores 53, s5acts 92, rseq 94; Gemma projected ~65 min total; dose runs ~12 min per model (from `logs/run_gpu_status.txt` timestamps). CPU/RAM: not recorded. Judge cost: $1.11 for this artifact (README D8).

## 5. Expected outputs and numbers

Headline numbers appear in `results/analysis/tables.md` and `results/analysis/summary.json`; audits in `results/verify_numbers.json` (80/80) and `results/audit_headline.json`. Final outputs: `method_out.json`, `figures/fig1–fig8` (PDF+PNG). The paper is not in this folder; the mapping is: behaviour → `tables.md` behaviour tables/fig; utility → fig1; layer profiles → fig2; frozen vs refit → fig3; A2 → fig4; KL → fig5; readout validity → fig6; drift → fig7; dose → fig8.

| quantity | value |
|---|---|
| gpt-4.1 refusal EN/SL: GaMS orig → edit | 100/100 → 5.6/6.7 % |
| Gemma orig → edit | 99.3/99.2 → 70.3/95.3 % |
| marker-rule Gemma edit EN | 32.7 % (kappa vs gpt-4.1 0.707) |
| second judge kappa vs gpt-4.1 | 0.828 (refused, n=200), 0.765 (6-way) |
| utility macro change (pts) EN/SL | GaMS +0.13/+0.20; Gemma +0.13/0.00; Holm p = 1.0 |
| FLORES NLL change | ≤ 0.002 |
| EN/SL harm-direction cosine (raw) | Gemma 0.919, GaMS 0.832 |
| GaMS frozen-probe S4 AUROC at L34 | 0.998 → ~0.60 EN / ~0.42 SL after edit (drop 0.40/0.58); refit 0.985/0.954 |
| A2 slope ratio GaMS | 0.359 EN, 0.420 SL (EVIDENCE_LOSS) |
| Gemma dose (R_seq>0 harmful, f=1/1.5/2/3) | EN 90.3/45.1/24.5/12.8 %; SL 98.8/77.4/46.3/7.0 % |
| base GaMS3-12B CV AUROC | 0.988 EN / 0.958 SL |

Tolerances: GPU numerics are non-deterministic to a small degree, so recomputed generations/activations may differ slightly; `analyze.py` and later stages are deterministic given the saved results. Human native-speaker review is **pending** (`results/native_review_packet_c1u.csv`, key in `_KEY.csv`); no human labels exist.

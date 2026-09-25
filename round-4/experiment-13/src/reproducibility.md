# Reproducing `gen_art_experiment_13` (write-mass overlap instrument O)

This file describes what was **actually run** on 2026-09-24, in order. Every path is relative to this folder.

## 1. Getting the artifact

This folder is one folder of the run's public GitHub repository. Clone the repository and `cd` into this folder.

Other artifacts of the same run are read through **one** relative constant, `RUN` in `common.py`. It defaults to three
levels above this folder, i.e. the run's `3_invention_loop/` (this folder is `round-4/experiment-13/src`).
Set `AII_LOOP_DIR=<path to 3_invention_loop>` if your checkout lays the sibling folders out differently. Inputs used:

| input | artifact id / folder under `3_invention_loop/` | what is read |
|---|---|---|
| frozen EN/SL splits | `art_qdUCJWbc5kHh` = `round-1/dataset-1/src/data/` | `splits/*.jsonl`, `split_manifest.json` (SHA-checked) |
| frozen directions | `round-2/experiment-8/src/directions/gemma_all_layers.npz`, `results/gemma/layerwise_pc.npy` | d_EN(h), d_SL(h), PC control |
| rubric | `round-2/experiment-4/src/protocol.yaml` (a byte-identical copy is in `configs/exp4_protocol.yaml`) | judge prompt |
| screen cells, energies | `round-3/experiment-9/src/results/{rhat_orth.npy, energy_real.json, cells.csv, cells/}` | closed-form energies, screen |
| outside family | `round-3/experiment-12/src/{data/items_*.jsonl, results/qwen3/directions.npz}` | DE/LT items, Qwen3 directions |

No user-uploaded (private) input is used.

## 2. System, Python, environment

- Ubuntu (container), NVIDIA driver 580, CUDA 13.0 runtime available; **one NVIDIA L4 (23 GB VRAM)**; 48 CPU cores;
  251 GB RAM.
- Python **3.12**, environment built with `uv` only:

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r pyproject.toml   # exact pins (== uv pip freeze of the .venv that ran)
```

`pyproject.toml` pins every package exactly as installed, e.g. `torch==2.11.0+cu128` (from the PyTorch cu128 extra
index declared in `[tool.uv]`), `transformers==5.17.0`, `bitsandbytes==0.50.2`, `accelerate==1.15.0`, `numpy==2.5.2`,
`pandas==3.0.6`, `scipy==1.18.1`, `fasttext-wheel==0.9.2`, `loguru==0.7.3`, `matplotlib==3.11.2`.

## 3. Models, data, keys

Weights come from the Hugging Face hub into the standard HF cache (`HF_HOME` / `HF_HUB_CACHE`):

```bash
hf download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80   # anchor (gated: needs HF_TOKEN)
hf download Qwen/Qwen3-8B         --revision b968826d9c46dd6066d109eabc6255188de91218   # outside family
hf download Qwen/Qwen3-14B        --revision 40c069824f4251a91eefaf281ebe4c544efd3e18   # local judge
hf download cis-lmu/glotlid model.bin --revision 85cd6716494360367b75f642b5bc78667605d0b4 # language ID
```

Environment variables, by name only: `HF_TOKEN` (gated Gemma download), `OPENROUTER_API_KEY` and
`OPENROUTER_BASE_URL` (only for `judge/api_judge.py`, the gpt-4.1 judge gate; it cost $0.97 for 800 calls).
All models are loaded in bitsandbytes NF4 with bf16 compute. Decoding is greedy, and the system prompt is
"You are a helpful assistant." Seeds: `common.SEED = 20260925`; bootstrap B = 2000.

## 4. Commands, in the order they were run

| step | command | runtime on the L4 |
|---|---|---|
| smoke: gates 0/1/2 + timing | `.venv/bin/python method.py --stage smoke` | ~6 min incl. first load |
| Phase 1 profile (49 cells x 88 gens, 96 tok) | `.venv/bin/python method.py --stage profile` | ~37 min |
| judge pass 1 | `.venv/bin/python judge/local_judge.py --batch 48` (run by `run_chain1.sh`) | ~40 min |
| re-judge parse failures | `.venv/bin/python judge/local_judge.py --refail --batch 32` | ~5 min |
| Phase 2 freeze | `.venv/bin/python freeze.py` | < 1 min |
| Phase 4 confirmation (29 cells x 120 gens, 128 tok) | `bash run_chain2.sh` (confirm stage) | ~62 min |
| Phase 5A (crashed in run_chain2.sh, fixed) + judge + freeze_outside + Phase 5B + judge | `bash run_chain3.sh` | ~85 min |
| judge gate | `.venv/bin/python judge/api_judge.py --n 800 --conc 16` | ~1 min, $0.97 |
| analysis | `.venv/bin/python analysis.py && .venv/bin/python make_deviations.py` | ~2 min |
| audit | `.venv/bin/python rederive.py` | < 1 min |
| tables, figures, output | `.venv/bin/python report_tables.py && .venv/bin/python figures.py && .venv/bin/python build_output.py` | < 1 min |

Mini/preview variants of the output were then made with the aii-json formatting script
(`--input method_out.json` -> `full_`/`mini_`/`preview_method_out.json`). In a from-scratch re-run, `freeze.py` refuses
to run once any `results/gens/CF_*.json` exists, and `method.py --stage confirm` refuses to run unless
`configs/FREEZE.sha256` matches. Since `common.py` was edited after the run (portable paths, deviation D17), re-run
`freeze.py` on a fresh `results/` before the confirm stage. Every GPU stage is resumable per cell.

## 5. What you should get

Greedy NF4 generation is deterministic on the same GPU class, but bf16 kernels can differ across GPUs, so expect
single-item flips rather than bit-identical text on other hardware. Key numbers, all in `results/analysis.json` and
`results/report_tables.md`:

- Frozen DEV profile: split-half r (judged) EN 0.84, SL 0.51; argmax h EN 19, SL 16.
- Confirmation (18 weight conditions per language): Spearman(O, residual refusal) EN −0.96, SL −0.83. O's dR2 over
  the nuisance stack is EN 0.026, SL 0.052, so the frozen verdict is **FALSIFIED**.
- Matched groups, high-O minus low-O pooled over 8 groups: EN −0.69 [−0.75, −0.62], SL −0.38 [−0.46, −0.31].
- Controls: random and PC controls at the high-O layers stay within ±0.03 of the no-op.
- Dose rival: G3 low-O at 2× energy leaves EN 0.88 / SL 0.92.
- Judge gate: within-edited kappa 0.818 pooled; EN 0.856, SL 0.744 (Slovene is JUDGE_SENSITIVE).
- Qwen3-8B: Spearman(O) EN −0.76, SL −0.93, DE −0.84 (LT excluded by the gate); 9/9 matched contrasts favour high-O.
- `results/rederive_report.json`: 209/209 checks pass.

The README (`README.md`) is the write-up these numbers feed. Figures: `figures/fig1_profile` (profile),
`fig2_O_vs_residual`, `fig3_matched_forest`, `fig4_r2_ladder`, `fig5_fourway_bars`, `fig6_outside_family`.

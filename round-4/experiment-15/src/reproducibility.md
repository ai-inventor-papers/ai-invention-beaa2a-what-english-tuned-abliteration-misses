# Reproducibility

This is what was **actually run**, in this order, on one machine in one session (2026-09-24, about 16:00–20:10 UTC).
Every path below is relative to this folder.

## 0. Hardware and OS actually used

| | |
| --- | --- |
| OS | Ubuntu (Linux 6.8.0-101-generic), container with 48 CPUs and 503 GB RAM (no cgroup limits) |
| GPU | 1× NVIDIA L4, 23 GB VRAM (driver 580.126.20). This is the GPU type of the iteration-1 journals, which is why the replay is bit-exact |
| Python | 3.12.14 (`uv venv --python=3.12`) |
| wall clock | ≈ 4 h 10 min in total: ≈ 1.3 GPU-h replay (116 trials × 38 s), ≈ 1.6 GPU-h judging (Qwen3-14B at 0.78 s/item), ≈ 2 min for the gpt-4.1 purchase |

A 24 GB card is needed for the 12B target in NF4 at Heretic's batch 128 (peak ≈ 14.7 GB). The 14B judge
(≈ 20 GB at batch 24) runs afterwards, never co-resident with the target.

## 1. Get the artifact

The workspace is published as one folder of a public GitHub repository:
```bash
git clone <the run's repository URL> && cd <repository>/<this artifact's folder>
```
**Inputs from earlier artifacts of the same run** are read through ONE root, `AII_PRIOR_ARTIFACTS_ROOT` (see
`common.py`). By default it is this folder's grandparent's parent, i.e. the run tree `<root>/iter_4/gen_art/<this>`.
Below it the layout must be `iter_<k>/gen_art/<artifact folder>`:

| artifact id | folder under the root | what is read (read-only) |
| --- | --- | --- |
| art_0XmNBGkzsJc_ | `iter_3/gen_art/gen_art_experiment_11` | Gemma in-loop generations and Qwen labels, `miscalibration_table.csv`, `coverage_descriptors.csv`, `replay_fidelity.json`, S4 eval generations and labels (the classifier bundle, Heretic tree, rubric and selection rule are **copied** into this folder) |
| art_vzhOPupFwE4M | `iter_1/gen_art/gen_art_experiment_1` | both Optuna journals, `directions/{gams,gemma}/residual_means_A.pt` |
| art_qdUCJWbc5kHh | `iter_1/gen_art/gen_art_dataset_1` | `data/splits/*.jsonl`, `data/reports/overlap_audit.json`, `data/split_manifest.json` |

If they are checked out elsewhere: `export AII_PRIOR_ARTIFACTS_ROOT=<path to that root>`. No user-uploaded file is
used.

## 2. Environment (pinned; matches `pyproject.toml` and `env/requirements.lock`)

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 -r env/requirements.base.lock
uv pip install --python .venv/bin/python --no-deps -e third_party/heretic
uv pip install --python .venv/bin/python fasttext-numpy2-wheel openai
```
Key pins: torch 2.11.0+cu128, transformers 5.17.0, bitsandbytes 0.50.2, optuna 4.9.0, scikit-learn 1.9.1 (the
classifier bundle is version-sensitive), numpy 2.5.3, pandas 3.0.6. `env/requirements.lock` is the full
`uv pip freeze` of the venv actually used (178 pins plus the editable Heretic line). Install time is ≈ 15 min on a
network filesystem. No system packages are needed beyond a CUDA-capable driver.

## 3. Models, data, credentials (names only)

Downloaded into the Hugging Face cache (`HF_HOME` / `HF_HUB_CACHE` from the environment; do not override them):
```bash
huggingface-cli download cjvt/GaMS3-12B-Instruct --revision 1d0b27af5748784482600d24779409e7e1dc9adc
huggingface-cli download Qwen/Qwen3-14B --revision 40c069824f4251a91eefaf281ebe4c544efd3e18
huggingface-cli download google/gemma-3-12b-it --revision 96b6f1eccf38110c56df3a15bffe176da04bfd80 \
    tokenizer.json tokenizer_config.json tokenizer.model special_tokens_map.json added_tokens.json config.json
```
Heretic pulls `mlabonne/harmful_behaviors@01cead01` and `mlabonne/harmless_alpaca@02c6a92c` itself. Gemma is gated
and needs `HF_TOKEN`. The gpt-4.1 stage needs `OPENROUTER_BASE_URL` and `OPENROUTER_API_KEY`. Values are never
stored here. Spend this run: **$0.86** (801 calls, every call in `results/api_costs.jsonl`).

## 4. Exact commands, in the order run

```bash
.venv/bin/python method.py --stages s0,s1      # env.json, T0 instrument identity, both journals + gate G1
.venv/bin/python method.py --stages t2         # Gemma scoring, descriptors, unit tests, Gemma dress rehearsal
.venv/bin/python method.py --stages s2         # FREEZE -> configs/frozen_predictions.json + FREEZE.sha256 (16:27 UTC)
.venv/bin/python method.py --stages s3         # 3-trial probe (0, 59, 88) + gate G2
.venv/bin/python method.py --stages s4 &       # replay of all 116 trials (tiers 60/10/46) + collect; PID-tracked
bash chain.sh <PID of s4>                      # waits on the PID, then s4a (J1 Qwen labels), s4b (gpt-4.1, in the
                                               # background), s4j2 (remaining 50 startup draws), s5 (score + certify)
.venv/bin/python method.py --stages s6         # dataset audit + analysis (first pass; writes the reselection table)
.venv/bin/python method.py --stages s4j3       # POST HOC selection-point labels (GaMS3 trials 88 and 85)
.venv/bin/python method.py --stages s6,s8,s9 --force   # final analysis, rederive/checks/deviations, figures, schema
.venv/bin/python placebo_audit.py              # TODO-5 placebos on the independent code path
```
Seeds: Heretic 20260923 (the journal's own; greedy decoding, so the replay is deterministic). Certification
trials and gpt-4.1 sample: 20260924. Judge presentation order: 20260923. Bootstraps: fixed numpy seeds in `gbf.py`
(0–7) and `rederive.py` (99, 777). Resample count B = 2000.

## 5. What you should get

| number | file | value |
| --- | --- | --- |
| replay fidelity | `results/replay_fidelity_s3.json`, `results/replay/gams_trials.jsonl` | 116/116 trials, keyword count and KL identical to the journal |
| judge gate | `results/judge_certification.json` | κ(Qwen3-14B, gpt-4.1) = 0.850 [0.772, 0.911], n = 800 |
| G3 classifier gate | `results/gams_certification.json` | κ = 0.841 [0.745, 0.910] (keyword 0.591) |
| PRIMARY paired GBF difference | `results/analysis.json` → `paired_headline` | +0.006 [0, 0.019] → PRED-1 falsified |
| judge-referenced paired difference | same, `judge_referenced_paired` | −0.029 [−0.060, −0.005] |
| TBF | same, `searches.*.gbf_C.all.secondary_threshold_blind_C_le_10` | 1.00 in both searches |
| per-candidate table | `results/per_candidate.csv` | 232 rows |
| audits | `results/rederive.json`, `results/placebo_audit.json`, `results/checks.json` | 81/81 checks, 0 mismatches; placebos fail as required |

Figures `figures/fig1…fig6` show these numbers (fig. 2 is the headline and fig. 6 the judge-referenced view). The
README's results section reports every number with its CI. On an L4 the replay should be bit-exact. On a different
GPU model, greedy NF4 output can differ at near-ties; this run documented that for Gemma (4090 vs L4: mean |Δ| 0.16).

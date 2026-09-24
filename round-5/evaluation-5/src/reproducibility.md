# Reproducing "How blind is an English-only refusal score"

These are the exact steps that produced the shipped results. The analysis is CPU-only: no model is loaded, nothing is
generated, and no API call is made (spend $0.00).

## 1. Get the artifact

This folder is one folder of the run's public GitHub repository. Clone the repository, then `cd` into this folder
(`iter_5/gen_art/gen_art_evaluation_5/` in the run layout):

```bash
git clone <repository-url> run && cd run/<path-to-this-folder>
```

### Inputs from other artifacts (read-only)

Every input is a per-item or per-candidate file written by an earlier artifact of the same run. All of them are read
through ONE root, `LOOP` in `common.py` (`LOOP` in `rederive.py` for the second code path). `LOOP` is the directory
that holds `iter_1/ … iter_5/`. It defaults to three levels above this folder, `Path(__file__).parents[2]`, which is
correct when the repository keeps the run layout. Otherwise, point it at your copy:

```bash
export AII_LOOP_DIR=/path/to/folder/that/contains/iter_1_to_iter_5
```

| Artifact id | Folder under `LOOP` | Used for |
|---|---|---|
| art_F46S3uP80BUa | `iter_4/gen_art/gen_art_experiment_15` | `results/per_candidate.csv`, `analysis.json`, `reselection_table.csv` (leg A) |
| art_0XmNBGkzsJc_ | `iter_3/gen_art/gen_art_experiment_11` | `results/eval_gen/*.jsonl`, `autoscore/*.jsonl`, `judge_out/*.jsonl`, `guard_analysis.json`, `third_party/.../keyword_rate.py` |
| art_m6pglf516e2r | `iter_2/gen_art/gen_art_experiment_4` | `results/gen`, `autoscore`, `judge_local`, `judge`, `guard/*` |
| art_vzhOPupFwE4M | `iter_1/gen_art/gen_art_experiment_1` | `protocol_selection.json` (frozen selection rule text) |
| art_qdUCJWbc5kHh | `iter_1/gen_art/gen_art_dataset_1` | `data/provenance/heretic_3521f864_config.default.toml` (pinned marker list), `data/split_manifest.json` |
| (undeclared) | `iter_4/gen_art/gen_art_evaluation_2/results/judge_calibration.json` | Se/Sp and gates for Rogan-Gladen (leg B5) |
| (undeclared) | `iter_4/gen_art/gen_art_research_1/results/neighbour_table.json` | verified quotes N19/N20 (leg C) |
| (undeclared) | `iter_4/gen_report_text/gen_report_text/paper_draft.md` | draft cross-reference in `paste_text.md` |
| (undeclared, companion) | `iter_5/gen_art/gen_art_evaluation_4/results/judge_agreement.csv` | panel-specific gate status (B5) |

`results/source_inventory.json` records the sha256, size, record count and schema keys of every input as read. If a
companion file differs or is missing when you rerun, the B5 panel column changes; everything else is unaffected. No
user-uploaded file is used.

## 2. Environment

* Ubuntu (Debian 12 container was used), Python **3.12.14**, `uv` for package management (no pip).
* Hardware used: 4 CPU cores, 29 GB RAM (cgroup limit), **no GPU**.

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.lock.txt
```

`pyproject.toml` and `requirements.lock.txt` pin the same 30 packages. The main ones are numpy 2.5.3, pandas 3.0.6,
scipy 1.18.1, pyarrow 25.0.1, matplotlib 3.11.2, tokenizers 0.23.2, huggingface-hub 1.33.0, loguru 0.7.3 and
pyyaml 6.0.3.

## 3. Downloads and credentials

* One file is downloaded: `tokenizer.json` of `google/gemma-3-12b-it` at revision
  `96b6f1eccf38110c56df3a15bffe176da04bfd80`, fetched with `huggingface_hub.hf_hub_download` into the standard HF
  cache. It defines the 100-token in-loop view used by leg A4. The model is gated, so set `HF_TOKEN` (name only)
  to a token with access.
* No OpenRouter key is needed: no LLM is called.
* `figures.py` imports house-style helpers from the `aii-data-fig-gen` skill. It finds them by walking up from this
  folder to `.claude/skills/aii-data-fig-gen/scripts`, or through `AII_DATA_FIG_GEN`. The helpers are not part of
  the published repository, so without them `figures.py` cannot run; the shipped PDFs/PNGs are the reference output.

## 4. Commands, in the order run

```bash
.venv/bin/python eval.py        # ~11 s: S0 inventory, legs A/A4/A5/B1-B5/C, placebos P1 P2 P3 P5
.venv/bin/python rederive.py    # ~3 s: independent stdlib-only second code path -> results/rederive.json
.venv/bin/python audit.py       # ~10 s: cross-path comparison, P4, path lint, audit_log, eval_out.json, paste_text.md
.venv/bin/python figures.py     # ~12 s: three figures
# full / mini / preview variants (aii-json skill formatter):
python <aii-json>/scripts/aii_json_format_mini_preview.py --input eval_out.json
```

The total wall time was about 40 s on the hardware above. Seeds:

* Bootstraps: seed 20260924, B = 2000, clustered on semantic item / verified pair.
* Paired-draw bootstrap of the falsified between-search prediction: seed 2, reused from art_F46S3uP80BUa.
* Placebo permutations: 1000 each, seeds 20260924 + offsets as coded.
* rederive.py: `random.Random(20260924)`.

Bootstrap endpoints therefore reproduce exactly on the same library versions.

## 5. What you should get

| File | Key numbers |
|---|---|
| `results/blindness_per_search.csv` | objective floor 72 / 16; TBF 1.00 in both searches (6/6 and 37/37 classifier-referenced; 5/5 and 6/6 judge-referenced); slope K on C 0.308 / 0.738; low-region GBF 0.470 (chance 0.459) / 0.017 |
| `results/heldout_agreement.csv` | edited EN κ 0.021, FP share 0.814 (MISFIRING); edited SL κ 0.000 with keyword positive rate 0/490 (SILENT) |
| `results/delta_lang.csv` | gemma_edit Δ_lang −1.56 [−1.68, −1.44] = −0.87 (rule positive-rate shift) + −0.69 (reference level) |
| `results/downstream_sensitivity.csv` | cost-difference shift range [−1.68, −0.11]; rank inversion possible = True |
| `results/placebos.json` | 5/5 pass |
| `results/audit_log.json` | 573/573 cross-path statistics OK; 2 plan mismatches (both explained in README) |
| `results/path_lint.json` | 0 failures |
| `eval_out.json` (= `full_eval_out.json`) | `metrics_agg` holds all of the above; schema `exp_eval_sol_out` |

In the paper, these numbers feed the measurement-validity section: threshold blindness, the Slovene-silence
correction to "κ 0.02 EN / 0.00 SL", Δ_lang, and the leg-C sensitivity sentence. The ready-to-paste sentences, each
with its source, are in `results/paste_text.md`.

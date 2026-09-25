# Reproducing this artifact (iteration-5 evaluation: "Recheck every number and every path")

This is exactly what was run. CPU only. No model is loaded, no text is generated, no network is used, and $0.00 is spent.

## 1. Get the artifact

The workspace is published as one folder of the run's public GitHub repository. Clone the repository and `cd` into this folder.
The audit reads the saved outputs of other artifacts in the same run. It locates them through ONE setting:

- `AII_LOOP_ROOT` is the directory that holds the run's round folders `iter_1/ ... iter_5/`, i.e. the run's `3_invention_loop/`.
  The default is three levels above this folder (`Path(__file__).resolve().parents[2]`), which is correct when the run tree is intact.
  In the published repository, point it at the folder that contains the round folders, for example
  `export AII_LOOP_ROOT=$(realpath ../../..)`.

Artifacts read (by id; each is a sibling folder of the published repository):

| id | folder (relative to `AII_LOOP_ROOT`) | files read |
|---|---|---|
| art_NpZ_nW6qgSKD (exp13) | `round-4/experiment-13/src/results` | `per_item.csv`, `cells/*.json`, `judge_api.jsonl`, `analysis.json` (outside-panel O descriptors, MDE; reference only) |
| art_bxpIbe7-nSvR (exp14) | `round-4/experiment-14/src/results` | `per_item.parquet`, `cells.csv`, `judge_cert.json`, `deviations.json` |
| art_F46S3uP80BUa (exp15) | `round-4/experiment-15/src/results` | `per_candidate.csv`, `reselection_table.csv`, `conventional_table.csv`, `analysis.json` (label text only), `deviations.json` |
| art_hBuck7q0dnxG (eval2) | `round-4/evaluation-2/src/results` | `pooled_generations.parquet`, `gpt41_*_labels.jsonl`, `quant_behaviour_bf16_gens.jsonl`, `corrected_numbers_iter4.json`, `flip_analysis.json`, `pending_human_review_iter4.md` |
| art_0XmNBGkzsJc_ (exp11) | `round-3/experiment-11/src/results` | `miscalibration_table.csv` |
| art_ex4hbgThhJaL (exp9) | `round-3/experiment-9/src/results` | `cells.csv`, `cells/*.json` |
| art_xLy2vVlI7OEL (exp10) | `round-3/experiment-10/src/results` | `per_item.parquet` |
| art_kfCCWf7o8eJ9 (exp12) | `round-3/experiment-12/src/results` | `analysis.json` (`rows`), `indices.json` |
| art_a4VkEvYRquBO (exp5) | `round-2/experiment-5/src/results` | `gemma/rseq_markers.json`, `gams/rseq_markers.json` |
| art_m6pglf516e2r (exp4) | `round-2/experiment-4/src` | `frozen_samples.json` (S5X pair map) |
| art_sZ5w0yoY9o6L (research 1) | `round-4/research-1/src/results` | `failed_and_unexecuted.md` (ledgers, verbatim) |
| art_Z3I1K3VnFZuz (eval1) | `round-3/evaluation-1/src/results` | `gap_range_summary.csv` (carried) |
| draft under audit | `iter_4/gen_report_text/gen_report_text/paper_draft.md` | the whole file (citation lint and draft line numbers) |

No user-uploaded input is used. No API key is needed.

## 2. Environment (Ubuntu, Python 3.12, uv)

```bash
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.lock   # same pins as pyproject.toml
```

Pinned versions (as installed): numpy 2.1.3, pyarrow 18.1.0, pandas 2.2.3, scipy 1.14.1, matplotlib 3.9.2, loguru 0.7.2, pyyaml 6.0.2
(the full list is in `pyproject.toml` and `requirements.lock`). The independent recompute (`rederive_iter5.py`) needs only numpy + pyarrow.
pandas and scipy are used only by the separate headline self-audit (`audit_headlines.py`), so that audit takes a different code path.

## 3. Commands, in the order they were run

```bash
export AII_LOOP_ROOT=...            # only if the run tree is not three levels up
.venv/bin/python eval.py            # runs lint_paths.py (hard gate), rederive_iter5.py, then assembles everything (~20 s)
.venv/bin/python audit_headlines.py # independent pandas re-derivation of the headline numbers + shuffled-input placebos (~10 s)
```

Then the pipeline's JSON formatter produced `full_eval_out.json`, `mini_eval_out.json` and `preview_eval_out.json` from `eval_out.json`
(full = identical content; mini = first 3 examples per dataset; preview = mini with strings truncated).

Seeds: every bootstrap and permutation uses `numpy.random.default_rng(20260924 + k)` with a fixed per-analysis offset k
(`rederive_iter5.py`). The Slovene re-certification draw is ordered by `sha256('iter5-sl-recert-20260924|' + gid)`.
Hardware: 4 vCPU / 32 GB RunPod CPU pod (cpu3m-4-32). Peak memory under 2 GB. Total runtime about 30 s.
`eval.py` exits 0 only if the citation lint passes (exit 2 if the lint gate fails, 1 if the recompute fails).

## 4. What you should get

| file | what | key numbers |
|---|---|---|
| `eval_out.json` (+ full/mini/preview) | `metrics_agg` plus 4 datasets: every audited number, every cited path, every placebo, every structural check | defect rate 21/136 = 15.4% [10.3, 22.5]; 14 material; 0 SIGN_REVERSED; lint 0 not found after rewrite, 10/10 known misses detected |
| `results/corrected_numbers.json` | one record per number: draft value, recomputed value, CI, unit, judge, kappa, definition, source path, provenance, verdict, severity, note | 185 first-pass records + 102 carried from eval2 |
| `results/path_lint.csv`, `path_lint_summary.json` | citation lint (R4) | 41 cited, 27 resolve as written, 14 after rewrite |
| `results/report_repairs_iter5.md` | the twelve paste-ready repair blocks R1-R12 | |
| `results/placebo_table.json` | placebos recomputed in the audit's own path | 8/8 scored placebos collapse |
| `results/judge_agreement.csv`, `rogan_gladen_companions.json` | within-edited vs pooled kappa per artifact x language (+ headline cells) | exp4 Gemma-edit EN kappa 0.39 inside the headline cell |
| `results/definition_sensitivity.csv` | strict / broad / keyword gap | S5X gap +0.69 strict, +0.23 broad |
| `results/sl_recert_draw_spec.json` | frozen draw for the Slovene gpt-4.1 re-certification (to be bought by the experiment executor) | |
| `results/ledger_F1_F14.md`, `ledger_U1_U10.md`, `pending_human_review_consolidated.md` | ledgers and the single pending-review list | |
| `results/headline_audit.json` | the separate self-audit | all 7 checks agree; 3/3 shuffled placebos collapse |
| `figures/fig1..3.{pdf,png}` | defect rate per pass; forest plot of recomputed contrasts; kappa panel | |

These numbers go into the final paper's audit / reproducibility section and into the corrections that the R1-R12 blocks prescribe for the iteration-4 draft.

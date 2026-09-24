# Reproducibility

Everything in this repository was produced by `method.py` on one NVIDIA L4 (23 GB) + 48 vCPU, Python 3.12, every model
loaded NF4 (bitsandbytes double-quant, bf16 compute) through a single shared load path.

## Exact environment

`results/env_freeze.txt` is `uv pip freeze` of the `.venv` every number here came from (109 packages; torch
2.11.0+cu128). Recreate it with the command in README "How to run"; `pyproject.toml` pins the same versions.

**`source env.sh` before anything.** It caps BLAS/OpenMP to 8 threads. With the host default of 48 threads on this
shared machine the direction-stage SVDs ran >10x slower (an early run sat CPU-bound for 12 minutes on work that takes
~30 s); nothing else about the results changes.

## Pinned model revisions

| role | repo | revision |
|---|---|---|
| M1 anchor | google/gemma-3-12b-it | 96b6f1eccf38110c56df3a15bffe176da04bfd80 |
| M2 | Qwen/Qwen3-8B | b968826d9c46dd6066d109eabc6255188de91218 |
| M3 | mistralai/Mistral-7B-Instruct-v0.3 | c170c708c41dac9275d15a8fff4eca08d52bab71 |
| judge | Qwen/Qwen3-14B | 40c069824f4251a91eefaf281ebe4c544efd3e18 |
| translation | facebook/nllb-200-distilled-1.3B | 7be3e24664b38ce1cac29b8aeed6911aa0cf0576 |
| Gemma W3 edit | iteration-1 trial-96 LoRA adapter | sha256 d219c084b84370cd972700fa07d754777b2fd56dc12257cd0e67498b2d0f2b01 (verified at load) |

`utter-project/EuroLLM-9B-Instruct` was the planned M3 and is a gated repo that returned HTTP 403 with this run's token;
the recorded fallback order was followed instead of substituting silently (`results/load_log.json`).

## Determinism

Greedy decoding everywhere (`do_sample=False`), `max_new_tokens=96`, left-padded length-bucketed batches, fixed seeds
(items 20260924, random controls 99+draw and 500+draw, bootstrap 20260924). Heretic's randomized `svd_lowrank` is
re-seeded immediately before each call exactly as upstream does. Batch size changes on OOM recovery can perturb a
generation at the last token; iteration-2 measured this at 13/16 byte-identical and 16/16 same-label.

## The freeze

`configs/frozen_predictions.json` (sha256 `6c9fcf377b1ce879...`) holds every
index, AUC, eligibility flag, baseline predictor and the four predictions P1-P4 plus the verdict rule. Its sha256 is in
`configs/FREEZE.sha256`, which also carries the sha256 of each frozen data file. `code/run_model.py --phase conf`
raises unless both are present, so no confirmation generation can precede the freeze.

Frozen-file integrity at the end of the run: **data files True**, frozen predictions recorded in
FREEZE **True**.

### One post-freeze patch, declared

`code/analysis.py` is hashed inside the freeze. It was patched **after** the freeze and the audit reports
`analysis_py_unchanged = False` so the change cannot hide.
`results/analysis_patch.json` carries both hashes and the full diff. Scope: an empty bootstrap array made numpy's
`quantile` raise, and an undefined residual difference was being counted as a "decided" comparison. Both are
robustness only - no estimator, threshold, prediction or verdict rule changed. It was found by a dry run *before* the
confirmation labels existed.

## Independent re-derivation

`code/rederive.py` imports nothing from the analysis code (standard library + numpy only) and recomputes every index,
AUC, eligibility flag, residual and P1-P4 statistic from the raw generations, the raw labels and the frozen file:
**102 checks, 0 mismatches**.

Placebos: (b) permuting the index -> -0.009; (c) swapping REFUSED/COMPLIED ->
sign flips (+0.009 vs real -0.009); (d) feeding DEV items in
place of confirmation items -> correctly flagged `LEAKAGE` while the real set is
`OK`. Placebo (a), the language shuffle, returns
-0.356; its pass criterion asks the placebo to be smaller in magnitude than the
real effect, which is degenerate when the real effect is ~0. Rather than discard it, `code/posthoc.py` runs the
decomposition it points to (README section 5b).

## Splits

No semantic id is shared between the set that built the directions, the set that chose the index and the set that tests
it (audited in `results/checks.json:split_overlap`: True). `S5`/`S6`/`S7` of the frozen dataset
were never opened by this artifact.

## Judging

Primary and only judge: `Qwen/Qwen3-14B`, rubric variant `V2`, chosen on a DEV split of the free pool of
exp8 generations already labelled by gpt-4.1 and certified once on a disjoint HOLDOUT split:
**kappa = 0.683** [0.629, 0.737], below the
pre-registered 0.80 gate. gpt-4.1 could not be used at all (the run-level OpenRouter budget was exhausted before this
artifact started; this artifact spent **$0.00**), so the planned fallback could not fire. Se = 0.984, Sp = 0.741, so
absolute refusal levels are biased upward and `results/analysis.json:sensitivity_judge_corrected` carries a
Rogan-Gladen-corrected re-run of P1 and P2.

Judging is blind (request + reply only, shuffled across models and cells) and 4-way; `PARTIAL` counts as not-refused and
is always shown; a reply whose GlotLID language differs from the prompt's is `INVALID` regardless of the judge. No
keyword rule decides any reported number.

## Headline numbers and where they come from

| number | value | file |
|---|---|---|
| P1 pooled Spearman | -0.009 [-0.131, 0.192] | `results/analysis.json:P1` |
| P2 concordance | 8/12 | `results/analysis.json:P2` |
| P3 Spearman(index, W2-W1) | -0.474 | `results/analysis.json:P3` |
| single-site transfer baseline | +0.732 | `results/analysis.json:P4` |
| baseline-refusal baseline | +0.661 | `results/analysis.json:P4` |
| EN/L direction cosine | +0.010 | `results/analysis.json:P4` |
| within-gemma rho(index) (post-hoc) | +0.678 | `results/posthoc_decomposition.json` |
| verdict | FALSIFY | `results/analysis.json:verdict` |
| positive control vs iteration-2 | 4/4 within 0.15 | `results/checks.json` |

`results/report_tables.md` prints every table; `code/report_tables.py` regenerates it from `results/` alone.

## Kept artifacts (absolute paths, this volume)

The publish step skips files >= 100 MB, so these live only here:

- generations: `./results/<model>/gens/*.jsonl`
- judged labels: `./results/labels_qwen.jsonl`
- frozen directions: `./results/<model>/directions.npz`
- the freeze: `./configs/frozen_predictions.json`

`code/cleanup.py` moved the top-100 harmless PC basis (used only to draw matched random controls) out of
`directions.npz` into `results/<model>/harmless_pcs.npy` - gemma: 80.5->5.3 MB, mistral: 57.9->3.8 MB, qwen3: 64.9->4.2 MB.
It is declared `delete: regenerable` in `.aii/manifest.yaml` and is rebuilt by re-running the DEV phase.

## Known non-reproducible elements

- Native-speaker review of the Slovene/German/Lithuanian items and outputs is **PENDING**; it was not performed.
- The gemini back-translation QC leg could not run (budget), so translation QC is a same-system NLLB round trip plus
  LaBSE and GlotLID.
- Wall-clock cuts are recorded in `method_out.json:metadata.cuts_applied`: confirmation harmless twins were generated and
  judged for the no-op and selected-kernel cells only, and M3 was dropped from the weight panel (all its rows had already
  failed the frozen eligibility gate).

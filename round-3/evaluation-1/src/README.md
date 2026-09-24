# evaluation_iter3_dir5: recheck every number and every judge

A CPU-only audit and measurement-robustness evaluation over seven executed artifacts:
- iteration 1: experiments 1 and 3
- iteration 2: experiments 4, 5, 6, 7 and 8

It also audits the iteration-2 paper draft (`iter_2/gen_report_text/gen_report_text/paper_draft.md`). No model was loaded and no text was generated. OpenRouter spend was $0: the one optional gpt-4.1 top-up was blocked, see below.

It does two jobs:
- **(A) Re-derivation.** Every number in the draft is re-derived from the lowest-level per-item files by a new code path. None of the prior artifacts' analysis scripts were imported or executed.
- **(B) Judge-sensitivity instrument.** Each edited cell is labelled refused / partial / complied / invalid under every judge. Agreement is computed within edited checkpoints, the keyword proxy's miscalibration is measured, and the Gemma SL−EN refusal gap is reported as a range across judges and definitions.

## Headline results (all recomputed; `results/headline_metrics.json`)

### Observations (measured)

**Audit accuracy**
- 167 draft numbers checked: 137 match, 8 mismatch, 12 misdescribed, 6 untraceable. The mismatch rate is 0.055.
- 44 numbers are NEW (missing from the draft).
- 29 are SUMMARY_ONLY: HistGBT bootstrap CIs, not re-run on CPU.

**Two sign-reversed conclusions**
1. The iteration-1 swap. Under GaMS3's trial-88 parameters, Gemma's refusal falls EN 100→53 and SL 97→25, at KL 0.254. The draft says "91/95 at 0.293", which is in no file.
2. Exp7's P-a. The frozen prediction was `Gap_R >= 0.10 with 95% LB > 0`. It failed because the gap is small (0.054). The draft inverts it into "Gap_R is small, ≤ 0.05".

**Judge agreement is inflated by pooling**
- exp4 gpt-4.1 vs Qwen3-14B, binary: κ .913 pooled, but .779 [.678, .861] within edited checkpoints (inflation .133). Four-class: .833 pooled vs .727 within edits.
- exp8 binary: .769 pooled vs .737 within edits.
- A within-cell label shuffle (P4) leaves a pooled κ of .24 (exp4) and .12 (exp8). That part is produced purely by between-cell prevalence contrasts.

**Keyword proxy inverts on the selected Gemma edit**
- EN keyword "refusal" rate .851 vs Qwen-judged .255.
- 76% of keyword "refusals" are judged not-refused (71% of those are PARTIAL). κ = −.04.
- On GaMS3's edit, 97% of keyword "refusals" are false positives.

**The Gemma SL−EN gap depends on the definition**
- Across LLM judges and datasets (n ≥ 30 per language), the gap is +0.22 to +0.71 STRICT (refused only). All strict CIs exclude 0.
- It is −0.04 to +0.37 BROAD (refused + partial).
- On the only paired basis (S5X, Qwen): strict +0.69 [0.60, 0.78] becomes broad +0.23 [0.14, 0.32].
- On RefusEU S5 (Qwen), broad is −0.04 [−0.10, 0.02].

**Claim-level judge dependence**
- 19 of 99 behavioural claims are JUDGE_SENSITIVE.
- Example: exp8 A1 EN harmful is .225 under gpt-4.1 but +.44 higher under Qwen on the same 111 items, which crosses 0.5.
- 20 claims rest on a single judge (the exp8 depth table, exp3, the community cells).

**Placebos:** 6/6 pass.
- A +0.01 planted error is caught (5/5).
- All known mismatches are re-detected.
- The GaMS3 iteration-1 rows and the ten exp4 S5 cells match.
- Shuffled labels give κ ≈ 0.
- A language-label permutation collapses the S5X gap to 0.00 [−0.15, 0.15].
- The keyword re-implementation reproduces exp4 autoscore on 4,800/4,800 items.

### Interpretations (not measured directly)
- The English Heretic edit on Gemma mostly turns English refusals into hedged PARTIAL replies rather than into compliance. The Slovene "residual refusal" is therefore real in the strict sense, but its size is a definitional choice.
- The paper should report the gap as a range under both definitions, not as one judge's +0.69.

### Failed hypotheses and closed leads
See `results/dead_end_ledger.md`: the exposure differential D, static b1/b2/b3 and Ω, r_prior, the thin-margin rival, and the language-identity direction (it works but costs +1.93 nats).

### Unexecuted or blocked
- Optional S2(j) gpt-4.1 top-up on 521 S5X items: blocked with HTTP 403 `aii_run_budget_exhausted`. 0 labels, $0 spent.
- Also listed in the ledger: P2 Sobol, the English-only forecast, the language-orthogonalised matched-efficacy arm, the Gemini second judge, and the empty iteration-1 pods (experiments 2 and 4).

### Pending
No native-speaker review exists anywhere in the run. `results/pending_human_review.md` lists three native-review packets that are ready but unlabelled (570 rows), plus two executor-only checks.

### Mismatches against the evaluation plan itself
These are logged, not hidden:
- The 13.4× CI in the draft ([6.9, 30.4]) is the artifact's CI rounded. The plan's "expected [7.0, 30.0]" was wrong.
- The S1 Slovene text is mostly gemini-2.5-flash, not NLLB.
- The exp3 "+0.77" is a level gap, while the GaMS3 "−0.15" is a difference-in-differences.
- The exp6 source-layer Spearman recomputes to 0.753 over all non-collapsed edits, against 0.77 on the artifact's fitted subset.
- The exp8 cosine-transfer AUROC is 0.244, not 0.240.
- The 2607.02714 "2-3 middle layers" quote is NOT VERIFIED.

## How to run

```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r requirements.lock
./run_all.sh          # or: .venv/bin/python eval.py  (CPU only, ~1.5 min, no API keys)
```

Full step-by-step instructions are in `reproducibility.md`.

## Layout

| path | contents |
|---|---|
| `eval.py`, `run_all.sh` | entry points; rebuild everything, about 1.5 min on CPU |
| `reproducibility.md` | step-by-step reproduction |
| `full_eval_out.json`, `mini_eval_out.json`, `preview_eval_out.json` | size variants of `eval_out.json` |
| `scripts/verify_headlines_indep.py`, `results/verify_headlines_indep.json` | independent raw-file re-derivation of 10 headline numbers (all match) plus 2 placebos (both collapse to ~0) |
| `pyproject.toml`, `requirements.lock` | pinned Python 3.12 deps |
| `configs/label_map.yaml` | native → canonical 4-class map for every judge, plus the verbatim keyword marker lists; reusable by iteration-3 X-4(b) |
| `scripts/lib.py` | loaders, keyword judge, Wilson / cluster bootstrap / McNemar / κ / AC1, and the three-way comparator (`Recorder`) |
| `scripts/s01_labels.py` | S0 inventory; unified long label table `results/labels_long.parquet` (61,130 labels) |
| `scripts/s02_iter1.py` | S1: iteration-1 table, swap statistics, 13.4×, KL-matched subset, A3 |
| `scripts/s03_judges.py` | S2(d-h): judge-sensitivity cells, agreement, keyword miscalibration, gap range, exp8 per-judge split, official ASR |
| `scripts/s04_claims.py` | S2(i): claims registry, 99 behavioural claims × every judge |
| `scripts/s05_panels.py` | S3-S7: exp7 frozen predictions and slopes (recomputed), exp6 bounds, exp3 restoration, exp8 F-block, exp4 and exp5 extras |
| `scripts/s06_ledger.py` | S8: dead-end ledger, pending review, translation provenance, repro units |
| `scripts/s07_placebos.py` | S10 placebos P1-P6 |
| `scripts/s08_assemble.py` | corrected numbers, audit log, `report_repairs.md`, `judge_sensitivity.md` |
| `scripts/s09_figures.py` | the three figures |
| `scripts/s10_eval_out.py` | `eval_out.json` |
| `scripts/s11_topup.py` | optional gpt-4.1 top-up (frozen exp4 prompt, $3 hard stop); blocked by the run budget |
| `results/corrected_numbers.json` | 236 records: draft value, recomputed value, artifact-summary value, plan-expected value, status, CI, n, source path and key, paste text |
| `results/report_repairs.md` | paste-ready corrected tables for repairs (1)-(10), each with a source path |
| `results/judge_sensitivity.{csv,md}` | per cell × judge: n, coverage, random-subset flag, class shares with Wilson and cluster-bootstrap CIs |
| `results/judge_agreement.csv`, `judge_confusions.json` | κ (binary and 4-class) with bootstrap CI, raw agreement, PABAK, AC1, confusion matrices; pooled all / originals / edited and per edited cell |
| `results/keyword_miscalibration.csv` | keyword vs judged rate, FP / FN shares, share of FPs judged PARTIAL, κ |
| `results/gap_range.csv`, `gap_range_summary.csv` | SL−EN gap per checkpoint × dataset × judge × definition (paired McNemar and DiD on S5X) |
| `results/claims_registry.csv` | JUDGE_SENSITIVE / JUDGE_ROBUST / SINGLE_JUDGE per draft claim |
| `results/exp8_by_judge.csv`, `exp8_overlap_gpt41_vs_qwen.csv`, `exp8_report_tables_verbatim.md` | exp8 re-split by judge |
| `results/novelty_table.{md,json}`, `novelty_raw/` | verbatim-quote positioning against 9 neighbours (regex grep over the fetched PDF / HTML) |
| `results/dead_end_ledger.md`, `pending_human_review.md` | S8 |
| `results/audit_log.json`, `placebos.json`, `headline_metrics.json`, `source_inventory.json` | audit trail (inventory has sha256 for every input file) |
| `figures/fig_gap_forest`, `fig_judge_stack`, `fig_kappa_inflation` (`.pdf` + `.png`) | figures |
| `eval_out.json` | `exp_eval_sol_out` schema (validated): `metrics_agg` = headline metrics; datasets = corrected_numbers (236), judge_sensitivity_cells (1,126), claims_registry (99), gemma_gap_range (88) |

## Units, rules and caveats

**Status vocabulary**

| status | meaning |
|---|---|
| RECOMPUTED_MATCH | recomputed value matches the draft within tolerance |
| RECOMPUTED_MISMATCH | the draft is wrong |
| MISDESCRIBED | the number is right but its label or definition is wrong |
| NEW | missing from the draft |
| UNTRACEABLE | the draft number exists in no file |
| SUMMARY_ONLY | read by key from the artifact summary; not recomputed |

**Tolerances**

| quantity | tolerance |
|---|---|
| counts | exact |
| rates | 0.0015; 0.0055 for 2-dp draft values |
| CI endpoints | 0.02 |
| p-values | within a factor of 1.5 when < 1e-3 |

**Resampling units**
- Semantic items, with EN/SL twins clustered.
- S5X pairs.
- For iteration 1, the same 100 prompts.
- Seed 20260924, B = 2000 unless noted.

**Caveats**
- All judges are automated, so the ranges measure between-judge disagreement, not accuracy.
- exp8's gpt-4.1 subset is arm-prioritised and exp5's is priority-ordered. Neither is a random draw, so between-judge comparisons use item overlap only.
- exp7's validity judge is Gemma judging its own edits, validated on originals only.
- Two models are two units. There is one optimiser seed, all models run in NF4, and the Slovene prompts are machine-translated (except RefusEU S5 and FLORES+).

## Restoring removed files

Only the virtual environment is deleted before upload. Recreate it, then rebuild all outputs:

```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r requirements.lock   # .venv/
./run_all.sh    # or: .venv/bin/python eval.py
```

# Recheck every number and every path (iteration-5 evaluation)

A CPU-only reporting-integrity audit of the iteration-4 paper draft (`iter_4/gen_report_text/gen_report_text/paper_draft.md`).
It carries out plan `gen_plan_evaluation_3`. It loads no model, generates no text and spent $0.00.

> **Provenance note.** This executor's task prompt arrived truncated: only the tail of the user's research request came through.
> The plan was recovered by matching the run log's dispatch order (plans evaluation_1, _3 and _4 were dispatched as artifacts
> evaluation_3, _4 and _5, and this is a 4-vCPU CPU pod, which matches plan _3's `cpu_plus` profile). The plan is
> `iter_5/gen_plan/gen_plan_evaluation_3/.terminal_claude_agent_struct_out.json`.

## What it found

**Citation lint (R4): gate PASS.** The draft cites 41 files. 27 resolve as written, 14 resolve only after a rewrite, and 0 remain unresolved.
The 10 known misses (9 distinct paths) were planted as a positive control and all 10 were detected. Each rewrite target is checked
to contain a number that the citing sentence quotes. 20 of the draft's 37 tables carry no source path.

**Independent recompute (R12).** `rederive_iter5.py` imports only stdlib, numpy and pyarrow, and reads per-item files.
It re-derived **136 draft numbers**. **21 are defective: 15.4%, Wilson 95% CI [10.3%, 22.5%].** They form 13 distinct defects,
9 of them material. **None is sign-reversed.** Counting numeric MISMATCH only, the rate is 9/136 = 6.6%. Under the same all-class
definition, the earlier passes measured 15.6% (eval1: 26/167, which the draft quotes as "5.5%") and 4.9% (eval2: 5/102).
The material defects:

| # | draft says | the saved files say |
|---|---|---|
| G3 | exp13's O fails its bar because "energy already correlates with effective placement" | log energy alone explains R² 0.001 EN / 0.008 SL; O fails because it is collinear with the EN/SL cosine (ρ 0.81 / 0.76). Over logE + layer count alone, O adds 0.89 / 0.77 |
| G1 | the 0.088 / 0.668 / 0.790 / 0.806 nested-R² table belongs to exp13 and is cumulative | it is exp14 (GaMS3, SL), each predictor added separately; the cumulative rows are 0.805 / 0.822 |
| G2 | exp14 dose contrast "EN -0.186, SL -0.157" | all four A1-A4 contrasts are Slovene strict; no English contrast exists |
| G12 | "the critical band differs between siblings" | at matched energy, 13-24 wins in GaMS3 too (E2 0.50 < 0.59; E3 0.30 < 0.53); only the DEV profile's argmax differs |
| G4 | exp11 trial 107 judged 10/100; trial 96 judged 15/100 | 63/100; 37 REFUSED + 49 PARTIAL (15/100 is arm B's S5X EN rate) |
| G13 | the EN-SL compliance gap is "smaller in magnitude" than the refusal gap | official-guard ASR 0.738 EN vs 0.103 SL: a larger gap than refusal (0.287 vs 0.739) |
| G10 | 7.2% of non-refused Gemma-edit EN outputs are guard-safe | 7.2% is exp11's corrected arm C; the Gemma edit gives 0.116 EN vs 0.370 SL (+0.254 [0.136, 0.374]) |
| G11 | exp10 EN judge agreement "within edited GaMS3 arms is 0.54" | 0.54 is the exp8 certification pool (mostly Gemma); exp10's own edited arms give 1.00 EN / 0.98 SL |
| G9 | exp15 reselection "Judge (gpt-4.1)" | the Qwen3-14B workhorse; gpt-4.1 was only the 800-item certification subsample |

**What survives the recompute (MATCH).** At matched energy, placement orders residual refusal. In Gemma, 8/8 matched groups hold
in both languages: pooled EN -0.688 on the 58 items shared by all groups (-0.682 on all items), SL -0.377, with ρ(O) -0.96 / -0.83.
In GaMS3, ρ(O_SL) is -0.90, and -0.98 / -0.95 within level. In Qwen3-8B, 9/9 matched contrasts hold. Doubling the dose on the late
band does not help (EN 0.88 / SL 0.92 vs 0.07 / 0.27). The exp4 RefusEU headline table matches cell for cell (20/20). The S5X gap is
+0.69 strict and +0.23 broad. The NF4/bf16 probe gives bf16 +0.60 [0.40, 0.80] vs NF4 +0.45 [0.20, 0.70]. exp12 P1 ρ is -0.009 over 21 rows.

**Placebos in the audit's own path: 8/8 collapse** (shuffled O, cell-label and energy-profile permutations, band-density permutation,
within-item cell and language swaps). A separate pandas self-audit (`audit_headlines.py`) reproduces all 7 headline numbers.
Its 3 shuffled-input placebos collapse.

**New judge finding (first report).** Inside the headline cell (Gemma edit, English), the workhorse agrees with gpt-4.1 at only
**κ = 0.39 [0.10, 0.64]** (n = 80, Se 0.60, Sp 0.87). The draft quotes only the pooled calibration κ of 0.91. The Slovene cell reaches 0.80.
The Rogan-Gladen corrected S5 gap is +0.44 against +0.45 raw, so the asymmetry survives the correction. The English rate in that cell
is judge-sensitive. The exp11 English panel κ is 0.226 (n = 65).

## Layout

| path | content |
|---|---|
| `eval.py` | entry point: runs the lint and the recompute, applies documented verdict overrides, writes everything |
| `lint_paths.py` | citation lint (R4); exits non-zero on any unresolved path |
| `rederive_iter5.py` | independent recompute (stdlib + numpy + pyarrow); placebos; structural checks |
| `repairs.py`, `figures.py` | R1-R12 paste-ready blocks; three figures |
| `audit_headlines.py` | separate pandas re-derivation of the headline numbers + shuffled-input placebos |
| `eval_out.json` / `full_` / `mini_` / `preview_eval_out.json` | exp_eval_sol_out output: `metrics_agg` + 4 datasets (numbers, lint, placebos, structural checks) |
| `results/corrected_numbers.json` | per-number records (draft, recomputed, CI, unit, judge, kappa, strict/broad, source, provenance, verdict, severity, note) |
| `results/report_repairs_iter5.md` | the twelve repair blocks R1-R12 |
| `results/path_lint.csv`, `claims_registry.csv`, `judge_agreement.csv`, `definition_sensitivity.csv`, `placebo_table.json`, `rogan_gladen_companions.json`, `defect_groups.json`, `headline_audit.json`, `audit_log.json` | tables behind the headline |
| `results/ledger_F1_F14.md`, `ledger_U1_U10.md` | failed hypotheses vs unexecuted proposals (U10 filled from iteration-4 deviations) |
| `results/pending_human_review_consolidated.md` | ONE pending list; nothing has been human-reviewed |
| `results/sl_recert_draw_spec.json` | frozen 702-item stratified draw (32 strata; est. $1.40) for the Slovene gpt-4.1 re-certification; to be bought by the experiment executor, not here |
| `figures/` | fig1 defect rate per pass (two definitions); fig2 forest plot of recomputed contrasts; fig3 kappa pooled vs within-edited vs gate |
| `reproducibility.md`, `pyproject.toml`, `requirements.lock` | how to rerun (about 30 s, CPU) |

## Limits (stated, not hidden)

- **No regeneration.** A generation-time error, such as a wrong adapter or a mislabelled cell, would be certified as MATCH. The structural checks (row counts 10,000 / 12,024 / 10,690 / 56,866) are the substitute.
- **Not re-derived in this pass.** exp6-exp8, exp5 T2-T11, iteration 1, and eval2's flip / curve statistics. They are carried with their sources and marked **[carried]**. exp12 P1 is re-derived arithmetically from the saved rows, not from the labels.
- **Rule versions.** The S5X keyword gap (+0.06) is NOT re-derived: the pooled table's keyword column is an English-only re-implementation. The recomputed keyword rate and FP share (0.839 / 0.726 vs 0.851 / 0.761) differ for the same reason.
- **Slovene judge gate unresolved.** No labels were bought. The Slovene re-certification is specified, not run. Every Slovene number stays machine-translated and machine-judged, with no native review.
- **UNRESOLVED design disagreement.** The matched-energy panels favour 13-24. The unmatched c = 1 grid favours 25-36 by +0.12 [0.00, 0.27]. This audit makes no band recommendation.

## How to run

```bash
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock
.venv/bin/python eval.py            # lint + independent recompute + all outputs (~20 s, CPU, $0)
.venv/bin/python audit_headlines.py # separate pandas self-audit of the headline numbers
```
Set `AII_LOOP_ROOT` to the folder holding the run's `iter_1 ... iter_5` round folders if the run tree is not three levels up (see `reproducibility.md`).

## Restoring removed files

| removed path | restore command |
|---|---|
| `.venv/` | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock` |

<!-- CARRIED TEXT. Where this file says `results/<name>` it means the DEPENDENCY's file of that name
(artifact art_sZ5w0yoY9o6L, iter_4/gen_art/gen_art_research_1/results/<name>). The ones this artifact
reuses are copied into this workspace as `results/_dep_<name>`; the rest stay at that path. -->

# Tagged ledger: FAILED HYPOTHESES vs UNEXECUTED PROPOSALS

Built from `iter_3/gen_art/gen_art_evaluation_1/results/dead_end_ledger.md`, the iteration-4 strategy's own record, and the producing artifacts' result files. Paths are relative to the run's `3_invention_loop/` directory. (The dependency's copy of this line gave an absolute server path; it is replaced here because this workspace is published.)

**Rule for the report author:** "we show", "we find", "we demonstrate" may attach to nothing in either table. A FAILED HYPOTHESIS is written as "we predicted X; the measurement was Y; the prediction failed [in direction D]". An UNEXECUTED PROPOSAL is written in a tense that cannot be mistaken for execution: "was not run", "is planned", "remains PENDING".

---

## A. FAILED HYPOTHESES — predicted, tested, killed, with the number and the direction

| # | hypothesis as pre-registered | what killed it (number + direction) | producing path |
|---|---|---|---|
| F1 | Depth COVERAGE (number of layers the edit touches) explains residual Slovene refusal over and above total removal energy. | dR² = 0.040 [0.006, 0.136] but leave-one-out dR² = **-0.002**, partial F p = 0.17, and a permutation placebo produced a **larger** dR² on average (p95 0.158); MDE 0.071 < the 0.10 bar, so this is a **powered rejection**, not an underpowered null. | `iter_3/gen_art/gen_art_experiment_9/results/report_tables.md` (P1) |
| F2 | At matched energy, BROAD-and-weak beats NARROW-and-strong for the non-English language. | **FALSIFIED IN THE OPPOSITE DIRECTION**: narrow minus broad SL refusal = **-0.10 [-0.150, -0.060]**, Holm p 0.000. Concentrating the same energy on one 12-layer band beats spreading it, and the coverage x language interaction also runs backwards (-0.07 [-0.131, -0.007]), i.e. concentrating helps Slovene MORE. | `iter_3/gen_art/gen_art_experiment_10/results/report_tables.md` (PB2, PB3) |
| F3 | A count-based depth index, frozen on development items, predicts cross-model / cross-language residual refusal after English-derived weight edits. | Spearman **-0.009 [-0.131, 0.192]** over 21 rows, permutation p 0.1628; concordance 8/12 decided (0.67) below the 0.75 bar, 6/12 under judge-error correction. Verdict recorded as FALSIFY by the pod's own frozen rule. | `iter_3/gen_art/gen_art_experiment_12/results/analysis.json` (P1, P2, verdict) |
| F4 | The EN/SL direction cosine is the geometric quantity that carries cross-lingual transfer. | Spearman **+0.010** on the same rows — it fails alongside the index, so "familiar geometry stops predicting" is real but is not a point in our instrument's favour. | `iter_3/gen_art/gen_art_experiment_12/results/analysis.json` (P4, `B_cos`) |
| F5 | The corrected (partial-aware) objective produces a BETTER edit, not merely a different one. | **Its own pre-registered falsifier P7 fired**: dose-scaling the keyword-selected edit to equal English refusal achieves comparable gap reduction (+0.33 vs the corrected arm's +0.38 [0.29, 0.47] against a keyword baseline of +0.68), and the cheaper dose arm reaches a zero gap at lower divergence. The reportable finding is the **miscalibration**, not an improvement. | `iter_3/gen_art/gen_art_experiment_11/results/eval_analysis.json`; `iter_3/gen_art/gen_art_experiment_11/README.md` |
| F6 | The exposure differential D carries the surrogacy gap. | dR²(D | S0) ≈ 0 or negative for every trait; e.g. K: dR² -0.011 [-0.058, 0.027] (exp6), Gemma +0.004 (exp7 P-c). | `iter_2/gen_art/gen_art_experiment_6/README.md`; `iter_2/gen_art/gen_art_experiment_7/results/analysis.json` (verdicts.P-c) |
| F7 | A false-refusal / r_prior direction (Wang-style) carries the Slovene residual. | Cut 0.036 [-0.037, 0.109] — smaller than the best random control (0.074) and the shuffled control (0.135); KILL criteria a and c fired. | `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md` (F1) |
| F8 | A thin-margin account explains the cross-language gap. | Margin-matched gap remains: +0.057 [0.029, 0.130] (Gemma), +0.131 (GaMS3). | `iter_2/gen_art/gen_art_experiment_7/results/analysis.json` (verdicts.P-d) |
| F9 | Static geometric predictors (b1/b2/b3, LSAR Omega) forecast the gap. | Cross-validated R² <= 0 for all. | `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json` (carrier) |
| F10 | A language-identity direction is a usable lever on Slovene residual refusal. | It works and is **unusable**: SL residual falls by 0.315 but Slovene harmful-request behaviour collapses (0.86 -> 0.55) and FLORES per-token NLL rises +2.02 EN / +1.93 SL — collateral, not a repair. | `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md` (A4) |
| F11 | The depth index's EN/SL difference is itself informative (index_EN 16 vs index_SL 20). | The 4-layer difference is **one k-grid step** and sits inside its own language-permutation null [-4, +4] in both checkpoints; the index alone does not carry the cross-language claim. | `iter_3/gen_art/gen_art_experiment_9/results/report_tables.md`; `iter_3/gen_art/gen_art_experiment_10/results/report_tables.md` (PA1) |
| F12 | Energy-matched random ablations are an adequate control by themselves. | LESSON, recorded as a failure of the control design: energy-matched random directions at every layer/position are destructive, so their refusal drops are collateral. Controls must be matched on collateral as well as energy. | `iter_1/gen_art/gen_art_experiment_3/results/deviations.json` |
| F13 | Conformal forecasting of Slovene outcomes from English ones is usable. | 85% coverage reached in only 50% of trait x holdout cells. | `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json` (forecast) |
| F14 | Batched and single generation are interchangeable for this harness. | Certification B3 FAILED and was reported: batched vs single generations are not identical. | `iter_2/gen_art/gen_art_experiment_4/results/smoke/` |

---

## B. UNEXECUTED PROPOSALS — proposed, never run, with the reason

| # | proposal | reason not run | evidence path |
|---|---|---|---|
| U1 | **Native-speaker review of all non-English material.** Five packets are prepared and blinded: behaviour packet (n=200, 100 SL/100 EN), C1 utility/refusal packet (n=120), translation adequacy packet (n=250), a 40-item SL label sample and a 30-item executor check (the last two labelled by the executor, explicitly **not** a native speaker). | No qualified native reviewer available to this run. Status: **PENDING** everywhere. All behavioural numbers are therefore "ranges across automated judges". | `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md` (packet paths and n) |
| U2 | Second independent LLM judge (Gemini) on the iteration-1 Slovene arm. | Budget block: OpenRouter HTTP 403 daily key limit. **0 judgements produced.** | `iter_1/gen_art/gen_art_experiment_1/results/judge_sl.json` |
| U3 | Full gpt-4.1 primary-judge coverage in iterations 2-3. | Same key limit; coverage is partial and arm-prioritised (exp4 716/3,840; exp6 1,130/2,140; exp8 5,298/12,136). | `iter_2/gen_art/gen_art_experiment_4/results/judge_blocked.json` |
| U4 | P2 Sobol sensitivity bands (exp6/exp7). | Cut for time. | exp6/exp7 deviations files |
| U5 | English-only-vs-full forecast arm (exp6). | Cut after the conformal coverage failure (F13). | `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json` |
| U6 | Language-orthogonalised matched-efficacy arm (exp8). | Cut for time. | `iter_2/gen_art/gen_art_experiment_8/results/deviations.json` |
| U7 | `EuroLLM-9B-Instruct` as the planned outside family M3. | Gated repository, HTTP 403; the pre-recorded fallback order was followed and `Mistral-7B-Instruct-v0.3` used instead. | `iter_3/gen_art/gen_art_experiment_12/results/load_log.json` |
| U8 | Racing this run's placement quantity against published cheap predictors — the logit-lens Linear Accessibility Profile (arXiv 2604.15557), separability statistics (arXiv 2609.14151), or the multilingual a-priori layer rule (arXiv 2605.23036). | Identified only in this positioning artifact (2026-09-24); no experiment was run against them. **No result is claimed for any of them.** | `results/neighbour_table.md` N7, N8, N23 |
| U9 | Two iteration-1 experiment pods (`gen_art_experiment_2`, `gen_art_experiment_4`) produced empty workspaces. | The pods produced no files; nothing was measured. They must not appear in any results sentence. | `iter_1/gen_art/gen_art_experiment_2`, `iter_1/gen_art/gen_art_experiment_4` (1 file each) |
| U10 | Any iteration-4 experiment arm not reached by its pod. | This positioning artifact was written without the iteration-4 experiment outputs and cannot report them. Whatever those pods do not reach belongs in this table before the paper is written. | (to be filled by the final audit from the iteration-4 pods' `deviations.json`) |

---

## C. Two entries that are neither, and must not be filed as either

- **The depth-coverage instrument's replacement finding** (placement, not count) is an OBSERVATION with its own support (C03, C05, C06 in `results/claims_to_position.csv`), not a rescue of F1. The paper must state F1 as falsified and C03/C05/C06 as what replaced it, in that order.
- **The transferable negative** (F3 + F4 + the winning baselines) is a FAILED HYPOTHESIS *for this run's instrument* and simultaneously the paper's most transferable OBSERVATION. It is filed as F3/F4 above and as C09–C12 in the claims inventory; the discussion must not present it as a positive result about an instrument.

# Ledger U1-U10: UNEXECUTED proposals (distinct from F1-F14)

Source: `iter_4/gen_art/gen_art_research_1/results/failed_and_unexecuted.md` section B, verbatim, with U10 filled from the iteration-4 deviations files (this audit).

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
| U10 | Iteration-4 arms not reached (filled below from each pod's deviations.json) | see U10.* rows | below |

### U10, filled

| # | pod | not run / not reached | evidence |
|---|---|---|---|
| U10.exp13.D5 | exp13 art_NpZ_nW6qgSKD | Screen restricted to iteration-3 exp9 Gemma weight cells (screen stage, S3 JBB half B). The 57 GaMS3 cells of exp10 are NOT RUN in the screen: O needs a GaMS3 causal profile, which this artifact did not measure (the sibling GaMS3 artifact o | `iter_4/gen_art/gen_art_experiment_13/results/deviations.json` |
| U10.exp13.D9 | exp13 art_NpZ_nW6qgSKD | Harmless KL and FLORES dNLL are the collateral panel for every Gemma confirmation cell; the six-task utility panel (plan: extremes only) is NOT RUN (last item of the frozen cut order). | `iter_4/gen_art/gen_art_experiment_13/results/deviations.json` |
| U10.exp13.D10 | exp13 art_NpZ_nW6qgSKD | Official Llama-Guard ASR pipeline NOT RUN; the rubric's own harm verdict (ASR-by-rubric) is reported separately from refusal instead. | `iter_4/gen_art/gen_art_experiment_13/results/deviations.json` |
| U10.exp13.D11 | exp13 art_NpZ_nW6qgSKD | Native-speaker review of Slovene/German/Lithuanian items and outputs remains PENDING (not performed). | `iter_4/gen_art/gen_art_experiment_13/results/deviations.json` |
| U10.exp14.D5_asr_pipeline | exp14 art_bxpIbe7-nSvR | not run: no S5/S5X generation was produced in this pod | `iter_4/gen_art/gen_art_experiment_14/results/deviations.json` |
| U10.exp14.D10_judge_buy_failed | exp14 art_bxpIbe7-nSvR | NOT bought: the platform's shared OpenRouter key returned aii_openrouter_key_limit for every call; $0.00 spent. Certification fell back to the gpt-4.1 labels already on disk for GaMS3 EDITED arms (iteration-2 cells, same pinned judge and ru | `iter_4/gen_art/gen_art_experiment_14/results/deviations.json` |
| U10.exp15.D11 | exp15 art_F46S3uP80BUa | Plan item (6) (an extra optimiser seed for the second search) was DROPPED, as the plan pre-declares; no edited checkpoint was selected, built, exported or recommended. | `iter_4/gen_art/gen_art_experiment_15/results/deviations.json` |
| U10.exp15.D15 | exp15 art_F46S3uP80BUa | T7 (mid-flight look at the GaMS3 K-vs-C plot after Tier 1) was deliberately skipped. | `iter_4/gen_art/gen_art_experiment_15/results/deviations.json` |
| U10.exp15.D18 | exp15 art_F46S3uP80BUa | Judge extension J2 incomplete: 4999/5000 rows labelled. | `iter_4/gen_art/gen_art_experiment_15/results/deviations.json` |

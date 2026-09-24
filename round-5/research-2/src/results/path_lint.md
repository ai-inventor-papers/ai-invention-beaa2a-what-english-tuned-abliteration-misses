# Path lint (repair R4, partial)

Every workspace-relative path THIS artifact cites was opened with a file tool this session. Paths are relative
to `3_invention_loop/`; no absolute server path appears in any published file. A path that did not resolve would
be dropped from the sentence that needed it rather than guessed.

**Scope limit (OBSERVATION).** This lint covers only the paths this artifact cites. The reviewer's nine
unresolved paths span other artifacts' citations, and this artifact has no shell over those files' own reference
lists, so the paper-writing step must still lint the rest. That is recorded as a follow-up question, not as done.

| artifact | path (relative to `3_invention_loop/`) | status | note |
|---|---|---|---|
| art_NpZ_nW6qgSKD | `iter_4/gen_art/gen_art_experiment_13/results/analysis.json` | **RESOLVES** | - |
| art_NpZ_nW6qgSKD | `iter_4/gen_art/gen_art_experiment_13/results/report_tables.md` | **RESOLVES** | - |
| art_bxpIbe7-nSvR | `iter_4/gen_art/gen_art_experiment_14/results/analysis_summary.json` | **RESOLVES** | - |
| art_bxpIbe7-nSvR | `iter_4/gen_art/gen_art_experiment_14/results/report_tables.md` | **RESOLVES** | - |
| art_F46S3uP80BUa | `iter_4/gen_art/gen_art_experiment_15/results/analysis.json` | **RESOLVES** | - |
| art_hBuck7q0dnxG | `iter_4/gen_art/gen_art_evaluation_2/results/asr_summary.json` | **RESOLVES** | - |
| art_hBuck7q0dnxG | `iter_4/gen_art/gen_art_evaluation_2/results/judge_calibration.json` | **RESOLVES** | - |
| art_m6pglf516e2r | `iter_2/gen_art/gen_art_experiment_4/results/analysis.json` | **RESOLVES** | - |
| art_m6pglf516e2r | `iter_2/gen_art/gen_art_experiment_4/results/headline_table.csv` | **RESOLVES** | - |
| art_m6pglf516e2r | `iter_2/gen_art/gen_art_experiment_4/README.md` | **RESOLVES** | - |
| art_KFZCxJcrr84K? | `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json` | **RESOLVES** | - |
| art_Z3I1K3VnFZuz | `iter_3/gen_art/gen_art_evaluation_1/results/novelty_table.md` | **RESOLVES** | - |
| art_Z3I1K3VnFZuz | `iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md` | **RESOLVES** | - |
| art_kfCCWf7o8eJ9 | `iter_3/gen_art/gen_art_experiment_12/results/analysis.json` | **RESOLVES** | - |
| art_kfCCWf7o8eJ9 | `iter_3/gen_art/gen_art_experiment_12/results/load_log.json` | **RESOLVES** | - |
| (iter3 exp9) | `iter_3/gen_art/gen_art_experiment_9/results/report_tables.md` | **RESOLVES** | - |
| (iter3 exp10) | `iter_3/gen_art/gen_art_experiment_10/results/report_tables.md` | **RESOLVES** | - |
| (iter3 exp11) | `iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv` | **RESOLVES** | - |
| (iter3 exp11) | `iter_3/gen_art/gen_art_experiment_11/results/selection_point_cert.json` | **RESOLVES** | - |
| (iter3 exp11) | `iter_3/gen_art/gen_art_experiment_11/scorer/certification.json` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/neighbour_table.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/neighbour_table.json` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/positioning_positive.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/positioning_negative.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/unverified_claims.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/stopping_points.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/search_log.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/failed_and_unexecuted.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/claims_to_position.csv` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `iter_4/gen_art/gen_art_research_1/results/reconciliation_map.csv` | **RESOLVES** | - |
| (iter1 dataset1) | `iter_1/gen_art/gen_art_dataset_1/data/reports/refuseu_correspondence.json` | **RESOLVES** | - |
| (iter4 draft) | `iter_4/gen_report_text/gen_report_text/paper_draft.md` | **RESOLVES** | - |
| (iter4 draft) | `iter_4/gen_report_text/gen_report_text/references.bib` | **RESOLVES** | - |

**Total: 33 paths checked, 33 resolve, 0 do not.**

Re-run with `python3 scripts/path_lint.py` (the same list, re-checked).

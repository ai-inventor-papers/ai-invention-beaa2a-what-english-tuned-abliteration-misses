# Path lint (repair R4, partial)

Every workspace-relative path THIS artifact cites was opened with a file tool this session. Paths are relative
to `3_invention_loop/`; no absolute server path appears in any published file. A path that did not resolve would
be dropped from the sentence that needed it rather than guessed.

**Scope limit (OBSERVATION).** This lint covers only the paths this artifact cites. The reviewer's nine
unresolved paths span other artifacts' citations, and this artifact has no shell over those files' own reference
lists, so the paper-writing step must still lint the rest. That is recorded as a follow-up question, not as done.

| artifact | path (relative to `3_invention_loop/`) | status | note |
|---|---|---|---|
| art_NpZ_nW6qgSKD | `round-4/experiment-13/src/results/analysis.json` | **RESOLVES** | - |
| art_NpZ_nW6qgSKD | `round-4/experiment-13/src/results/report_tables.md` | **RESOLVES** | - |
| art_bxpIbe7-nSvR | `round-4/experiment-14/src/results/analysis_summary.json` | **RESOLVES** | - |
| art_bxpIbe7-nSvR | `round-4/experiment-14/src/results/report_tables.md` | **RESOLVES** | - |
| art_F46S3uP80BUa | `round-4/experiment-15/src/results/analysis.json` | **RESOLVES** | - |
| art_hBuck7q0dnxG | `round-4/evaluation-2/src/results/asr_summary.json` | **RESOLVES** | - |
| art_hBuck7q0dnxG | `round-4/evaluation-2/src/results/judge_calibration.json` | **RESOLVES** | - |
| art_m6pglf516e2r | `round-2/experiment-4/src/results/analysis.json` | **RESOLVES** | - |
| art_m6pglf516e2r | `round-2/experiment-4/src/results/headline_table.csv` | **RESOLVES** | - |
| art_m6pglf516e2r | `round-2/experiment-4/src/README.md` | **RESOLVES** | - |
| art_KFZCxJcrr84K? | `round-2/experiment-6/src/results/analysis_results.json` | **RESOLVES** | - |
| art_Z3I1K3VnFZuz | `round-3/evaluation-1/src/results/novelty_table.md` | **RESOLVES** | - |
| art_Z3I1K3VnFZuz | `round-3/evaluation-1/src/results/pending_human_review.md` | **RESOLVES** | - |
| art_kfCCWf7o8eJ9 | `round-3/experiment-12/src/results/analysis.json` | **RESOLVES** | - |
| art_kfCCWf7o8eJ9 | `round-3/experiment-12/src/results/load_log.json` | **RESOLVES** | - |
| (iter3 exp9) | `round-3/experiment-9/src/results/report_tables.md` | **RESOLVES** | - |
| (iter3 exp10) | `round-3/experiment-10/src/results/report_tables.md` | **RESOLVES** | - |
| (iter3 exp11) | `round-3/experiment-11/src/results/miscalibration_table.csv` | **RESOLVES** | - |
| (iter3 exp11) | `round-3/experiment-11/src/results/selection_point_cert.json` | **RESOLVES** | - |
| (iter3 exp11) | `round-3/experiment-11/src/scorer/certification.json` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/neighbour_table.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/neighbour_table.json` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/positioning_positive.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/positioning_negative.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/unverified_claims.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/stopping_points.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/search_log.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/failed_and_unexecuted.md` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/claims_to_position.csv` | **RESOLVES** | - |
| art_sZ5w0yoY9o6L | `round-4/research-1/src/results/reconciliation_map.csv` | **RESOLVES** | - |
| (iter1 dataset1) | `round-1/dataset-1/src/data/reports/refuseu_correspondence.json` | **RESOLVES** | - |
| (iter4 draft) | `iter_4/gen_report_text/gen_report_text/paper_draft.md` | **RESOLVES** | - |
| (iter4 draft) | `iter_4/gen_report_text/gen_report_text/references.bib` | **RESOLVES** | - |

**Total: 33 paths checked, 33 resolve, 0 do not.**

Re-run with `python3 scripts/path_lint.py` (the same list, re-checked).

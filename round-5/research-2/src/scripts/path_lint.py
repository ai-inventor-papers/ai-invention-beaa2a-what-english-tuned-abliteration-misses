"""Re-check every workspace-relative path this artifact cites.

Paths are relative to the run's 3_invention_loop/ directory, which is located
relative to this file so the script works wherever the workspace is mounted.
Writes results/path_lint.md and results/_path_lint.json. Exit code is 0 only if
every path resolves.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOOP = HERE.parents[3]          # .../3_invention_loop
RES = HERE.parent / "results"

PATHS = [
    ('art_NpZ_nW6qgSKD', 'iter_4/gen_art/gen_art_experiment_13/results/analysis.json'),
    ('art_NpZ_nW6qgSKD', 'iter_4/gen_art/gen_art_experiment_13/results/report_tables.md'),
    ('art_bxpIbe7-nSvR', 'iter_4/gen_art/gen_art_experiment_14/results/analysis_summary.json'),
    ('art_bxpIbe7-nSvR', 'iter_4/gen_art/gen_art_experiment_14/results/report_tables.md'),
    ('art_F46S3uP80BUa', 'iter_4/gen_art/gen_art_experiment_15/results/analysis.json'),
    ('art_hBuck7q0dnxG', 'iter_4/gen_art/gen_art_evaluation_2/results/asr_summary.json'),
    ('art_hBuck7q0dnxG', 'iter_4/gen_art/gen_art_evaluation_2/results/judge_calibration.json'),
    ('art_m6pglf516e2r', 'iter_2/gen_art/gen_art_experiment_4/results/analysis.json'),
    ('art_m6pglf516e2r', 'iter_2/gen_art/gen_art_experiment_4/results/headline_table.csv'),
    ('art_m6pglf516e2r', 'iter_2/gen_art/gen_art_experiment_4/README.md'),
    ('art_KFZCxJcrr84K?', 'iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json'),
    ('art_Z3I1K3VnFZuz', 'iter_3/gen_art/gen_art_evaluation_1/results/novelty_table.md'),
    ('art_Z3I1K3VnFZuz', 'iter_3/gen_art/gen_art_evaluation_1/results/pending_human_review.md'),
    ('art_kfCCWf7o8eJ9', 'iter_3/gen_art/gen_art_experiment_12/results/analysis.json'),
    ('art_kfCCWf7o8eJ9', 'iter_3/gen_art/gen_art_experiment_12/results/load_log.json'),
    ('(iter3 exp9)', 'iter_3/gen_art/gen_art_experiment_9/results/report_tables.md'),
    ('(iter3 exp10)', 'iter_3/gen_art/gen_art_experiment_10/results/report_tables.md'),
    ('(iter3 exp11)', 'iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv'),
    ('(iter3 exp11)', 'iter_3/gen_art/gen_art_experiment_11/results/selection_point_cert.json'),
    ('(iter3 exp11)', 'iter_3/gen_art/gen_art_experiment_11/scorer/certification.json'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/neighbour_table.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/neighbour_table.json'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/positioning_positive.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/positioning_negative.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/unverified_claims.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/stopping_points.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/search_log.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/failed_and_unexecuted.md'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/claims_to_position.csv'),
    ('art_sZ5w0yoY9o6L', 'iter_4/gen_art/gen_art_research_1/results/reconciliation_map.csv'),
    ('(iter1 dataset1)', 'iter_1/gen_art/gen_art_dataset_1/data/reports/refuseu_correspondence.json'),
    ('(iter4 draft)', 'iter_4/gen_report_text/gen_report_text/paper_draft.md'),
    ('(iter4 draft)', 'iter_4/gen_report_text/gen_report_text/references.bib'),
]


def main() -> int:
    rows = []
    for artifact, rel in PATHS:
        full = LOOP / rel
        ok = full.exists()
        note = ""
        if not ok:
            parent = full.parent
            note = ("directory exists; contains: "
                    + ", ".join(sorted(p.name for p in parent.iterdir())[:6])) if parent.is_dir() \
                else "directory does not exist either"
        rows.append(dict(artifact=artifact, path=rel,
                         status="RESOLVES" if ok else "DOES NOT RESOLVE", note=note))
    (RES / "_path_lint.json").write_text(json.dumps(rows, indent=1) + "\n")
    bad = [r for r in rows if r["status"] != "RESOLVES"]
    print(f"{len(rows)} paths checked, {len(rows) - len(bad)} resolve, {len(bad)} do not")
    for r in bad:
        print("  -", r["path"], "|", r["note"])
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

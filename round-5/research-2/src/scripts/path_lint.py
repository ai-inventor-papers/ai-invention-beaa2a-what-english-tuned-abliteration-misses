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
    ('art_NpZ_nW6qgSKD', 'round-4/experiment-13/src/results/analysis.json'),
    ('art_NpZ_nW6qgSKD', 'round-4/experiment-13/src/results/report_tables.md'),
    ('art_bxpIbe7-nSvR', 'round-4/experiment-14/src/results/analysis_summary.json'),
    ('art_bxpIbe7-nSvR', 'round-4/experiment-14/src/results/report_tables.md'),
    ('art_F46S3uP80BUa', 'round-4/experiment-15/src/results/analysis.json'),
    ('art_hBuck7q0dnxG', 'round-4/evaluation-2/src/results/asr_summary.json'),
    ('art_hBuck7q0dnxG', 'round-4/evaluation-2/src/results/judge_calibration.json'),
    ('art_m6pglf516e2r', 'round-2/experiment-4/src/results/analysis.json'),
    ('art_m6pglf516e2r', 'round-2/experiment-4/src/results/headline_table.csv'),
    ('art_m6pglf516e2r', 'round-2/experiment-4/src/README.md'),
    ('art_KFZCxJcrr84K?', 'round-2/experiment-6/src/results/analysis_results.json'),
    ('art_Z3I1K3VnFZuz', 'round-3/evaluation-1/src/results/novelty_table.md'),
    ('art_Z3I1K3VnFZuz', 'round-3/evaluation-1/src/results/pending_human_review.md'),
    ('art_kfCCWf7o8eJ9', 'round-3/experiment-12/src/results/analysis.json'),
    ('art_kfCCWf7o8eJ9', 'round-3/experiment-12/src/results/load_log.json'),
    ('(iter3 exp9)', 'round-3/experiment-9/src/results/report_tables.md'),
    ('(iter3 exp10)', 'round-3/experiment-10/src/results/report_tables.md'),
    ('(iter3 exp11)', 'round-3/experiment-11/src/results/miscalibration_table.csv'),
    ('(iter3 exp11)', 'round-3/experiment-11/src/results/selection_point_cert.json'),
    ('(iter3 exp11)', 'round-3/experiment-11/src/scorer/certification.json'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/neighbour_table.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/neighbour_table.json'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/positioning_positive.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/positioning_negative.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/unverified_claims.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/stopping_points.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/search_log.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/failed_and_unexecuted.md'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/claims_to_position.csv'),
    ('art_sZ5w0yoY9o6L', 'round-4/research-1/src/results/reconciliation_map.csv'),
    ('(iter1 dataset1)', 'round-1/dataset-1/src/data/reports/refuseu_correspondence.json'),
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

#!/usr/bin/env python3
"""Citation lint (repair R4). Exit code 0 only if every cited path resolves after rewriting.

For each file reference in the audited draft: resolve (i) against the workspace of the artifact whose
[ARTIFACT:art_*] section it sits in, then (ii) by basename inside that workspace, then (iii) through an
explicit rewrite table whose every target is checked to exist AND to contain a marker value quoted in the
draft sentence (so a rewrite cannot silently repoint to an unrelated file). Anything else is NOT_FOUND.
Writes results/path_lint.csv and results/path_lint_summary.json. Paths are written relative to 3_invention_loop/.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOOP = Path(os.environ.get("AII_LOOP_ROOT", HERE.parents[2]))
DRAFT = LOOP / "iter_4/gen_report_text/gen_report_text/paper_draft.md"
RES = HERE / "results"
RES.mkdir(exist_ok=True)

ART_DIR = {
    "art_vzhOPupFwE4M": "round-1/experiment-1/src", "art_qdUCJWbc5kHh": "round-1/dataset-1/src",
    "art_jxrJNc9o4QSp": "round-1/experiment-3/src", "art_a4VkEvYRquBO": "round-2/experiment-5/src",
    "art_m6pglf516e2r": "round-2/experiment-4/src", "art_KFZCxJcrr84K": "round-2/experiment-6/src",
    "art_CUChUm6wCwo5": "round-2/experiment-7/src", "art_hmbXDppkPZnR": "round-2/experiment-8/src",
    "art_ex4hbgThhJaL": "round-3/experiment-9/src", "art_xLy2vVlI7OEL": "round-3/experiment-10/src",
    "art_0XmNBGkzsJc_": "round-3/experiment-11/src", "art_kfCCWf7o8eJ9": "round-3/experiment-12/src",
    "art_Z3I1K3VnFZuz": "round-3/evaluation-1/src", "art_NpZ_nW6qgSKD": "round-4/experiment-13/src",
    "art_bxpIbe7-nSvR": "round-4/experiment-14/src", "art_F46S3uP80BUa": "round-4/experiment-15/src",
    "art_hBuck7q0dnxG": "round-4/evaluation-2/src", "art_sZ5w0yoY9o6L": "round-4/research-1/src",
}

# Rewrites for citations that do not resolve as written: (section artifact, cited path) -> (target, marker values that
# must appear in the target file). The markers are numbers quoted in the draft sentence that carries the citation.
REWRITE = {
    ("art_a4VkEvYRquBO", "results/t1_harmful.json"): ("round-2/experiment-5/src/results/analysis/tables.md", ["70.3", "95.3", "24.6"]),
    ("art_a4VkEvYRquBO", "results/flip_analysis.json"): ("round-4/evaluation-2/src/results/flip_analysis.json", ["slope"]),
    ("art_KFZCxJcrr84K", "results/gap_table.json"): ("round-2/experiment-6/src/results/analysis_results.json", ["0.147", "0.968"]),
    ("art_ex4hbgThhJaL", "results/dev_index.json"): ("round-3/experiment-9/src/results/redundancy_index.json", ["index"]),
    ("art_ex4hbgThhJaL", "results/matched_energy_groups.json"): ("round-3/experiment-9/src/results/report_tables.md", ["16.7", "-0.34"]),
    ("art_xLy2vVlI7OEL", "results/dev_index.json"): ("round-3/experiment-10/src/results/redundancy_index.json", ["index"]),
    ("art_xLy2vVlI7OEL", "results/panel_summary.json"): ("round-3/experiment-10/src/results/report_tables.md", ["0.718", "0.325"]),
    ("art_0XmNBGkzsJc_", "results/s5x_headline.json"): ("round-3/experiment-11/src/results/headline_table.csv", ["0.83", "0.41"]),
    ("art_kfCCWf7o8eJ9", "results/dev_indices.json"): ("round-3/experiment-12/src/results/indices.json", ["0.75"]),
}
KNOWN_MISSES = {(168, "results/t1_harmful.json"), (183, "results/t1_harmful.json"), (263, "results/flip_analysis.json"),
                (351, "results/gap_table.json"), (489, "results/dev_index.json"), (535, "results/dev_index.json"),
                (502, "results/matched_energy_groups.json"), (537, "results/panel_summary.json"),
                (586, "results/s5x_headline.json"), (622, "results/dev_indices.json")}

PAT = re.compile(r"(?<![\w/.-])((?:results|configs|figures|iter_\d)/[\w./\-]+|/ai-inventor/[\w./\-]+|[\w\-]+\.(?:json|jsonl|csv|md|parquet|yaml|npz|py))")


def main() -> int:
    lines = DRAFT.read_text().splitlines()
    art = None
    rows = []
    for i, line in enumerate(lines, 1):
        m = re.search(r"\[ARTIFACT:(art_[\w\-]+)\]", line)
        if m:
            art = m.group(1)
        if line.startswith("## ") and "[ARTIFACT" not in line:
            art = None if not line.startswith("## Iteration") else art
        for tok in PAT.findall(line):
            tok = tok.rstrip(".,);:`")
            if tok.endswith(".md") and tok in ("report.md",) and "iter_1/gen_report_text" in line:
                pass
            status, resolved, marker_ok = "NOT_FOUND", "", ""
            if tok.startswith("/ai-inventor/"):
                status = "ABSOLUTE_PATH"
            elif tok.startswith("iter_"):
                if (LOOP / tok).exists():
                    status, resolved = "RESOLVES", tok
            elif art and art in ART_DIR:
                base = LOOP / ART_DIR[art]
                if (base / tok).exists():
                    status, resolved = "RESOLVES", f"{ART_DIR[art]}/{tok}"
                elif (art, tok) in REWRITE:
                    tgt, markers = REWRITE[(art, tok)]
                    txt = (LOOP / tgt).read_text(errors="ignore") if (LOOP / tgt).exists() else ""
                    ok = bool(txt) and all(mk in txt for mk in markers)
                    status = "RESOLVES_AFTER_REWRITE" if ok else "NOT_FOUND"
                    resolved, marker_ok = tgt, ("markers " + ",".join(markers) + (" present" if ok else " MISSING"))
                else:
                    hits = [p for p in base.rglob(Path(tok).name) if ".venv" not in p.parts]
                    if hits:
                        status, resolved = "RESOLVES_AFTER_REWRITE", str(hits[0].relative_to(LOOP))
            elif (LOOP / "iter_4/gen_report_text/gen_report_text" / tok).exists():
                status, resolved = "RESOLVES", f"iter_4/gen_report_text/gen_report_text/{tok}"
            if status == "NOT_FOUND" and not tok.startswith("/ai-inventor/"):
                # (ii) repo-wide basename search over every artifact workspace; accepted only if the hit is unique
                hits = sorted({str(p.relative_to(LOOP)) for d in ART_DIR.values() for p in (LOOP / d).rglob(Path(tok).name)
                               if ".venv" not in p.parts})
                if len(hits) == 1:
                    status, resolved, marker_ok = "RESOLVES_AFTER_REWRITE", hits[0], "unique repo-wide basename hit"
                elif hits:
                    marker_ok = f"ambiguous: {len(hits)} hits"
            rows.append({"claim_id": f"L{i}:{tok}", "draft_line": i, "section_artifact": art or "",
                         "cited_path_as_written": tok, "resolved_path_relative_to_3_invention_loop": resolved,
                         "status": status, "known_miss_positive_control": (i, tok) in KNOWN_MISSES, "check": marker_ok})
    with open(RES / "path_lint.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    n_nf = sum(r["status"] in ("NOT_FOUND", "ABSOLUTE_PATH") for r in rows)
    as_written_nf = sum(r["status"] != "RESOLVES" for r in rows)
    ctrl_detected = sum(1 for r in rows if r["known_miss_positive_control"] and r["status"] != "RESOLVES")
    # tables with no source path in the 3 lines above them (A2)
    tables, no_path = 0, []
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and (i == 0 or not lines[i - 1].startswith("|")):
            tables += 1
            ctx = " ".join(lines[max(0, i - 3):i])
            if "source:" not in ctx and "results/" not in ctx:
                no_path.append(i + 1)
        i += 1
    summary = {"draft": str(DRAFT.relative_to(LOOP)), "n_cited": len(rows),
               "n_resolving_as_written": sum(r["status"] == "RESOLVES" for r in rows),
               "n_rewritten": sum(r["status"] == "RESOLVES_AFTER_REWRITE" for r in rows),
               "n_not_found_after_rewrite": n_nf, "n_not_resolving_as_written": as_written_nf,
               "positive_control_known_misses": len(KNOWN_MISSES), "positive_control_detected": ctrl_detected,
               "n_tables": tables, "n_tables_without_path_before": len(no_path), "tables_without_path_lines": no_path,
               "gate": "PASS" if n_nf == 0 and ctrl_detected == len(KNOWN_MISSES) else "FAIL"}
    (RES / "path_lint_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))
    return 0 if summary["gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())

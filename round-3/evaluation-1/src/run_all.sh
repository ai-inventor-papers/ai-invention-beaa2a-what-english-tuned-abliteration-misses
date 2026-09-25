#!/usr/bin/env bash
# Rebuild every output of this audit from the raw per-item files of the seven prior artifacts (CPU only, ~2 min).
set -euo pipefail
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || { uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r requirements.lock; }
PY=.venv/bin/python
$PY scripts/s01_labels.py      # S0/S2(a-c): labels_long.parquet + source_inventory.json
$PY scripts/s02_iter1.py       # S1: iteration-1 table, swap stats, 13.4x, A3
$PY scripts/s03_judges.py      # S2(d-h): judge sensitivity, agreement, keyword miscalibration, gap range, exp8 split
$PY scripts/s04_claims.py      # S2(i): claims registry with judge-dependence flags
$PY scripts/s05_panels.py      # S3-S7: exp7 predictions/slopes, exp6 bounds, exp3, exp8 F-block, exp4/exp5 extras
$PY scripts/s06_ledger.py      # S8: dead-end ledger, pending human review, translation provenance
$PY scripts/s07_placebos.py    # S10: placebos P1-P6
$PY scripts/s08_assemble.py    # corrected_numbers.json, audit_log.json, report_repairs.md, judge_sensitivity.md
$PY scripts/s09_figures.py     # figures/*.pdf|png
$PY scripts/s10_eval_out.py    # eval_out.json
$PY scripts/verify_headlines_indep.py  # independent re-derivation of headline numbers + placebos
# OPTIONAL (not part of the rebuild; needs OPENROUTER_API_KEY; attempted once, blocked with HTTP 403): $PY scripts/s11_topup.py

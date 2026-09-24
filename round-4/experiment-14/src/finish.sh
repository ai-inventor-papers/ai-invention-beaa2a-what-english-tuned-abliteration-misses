#!/usr/bin/env bash
# Runs after the confirmation stage: the post-freeze rungs, the judge, certification, analysis and every deliverable.
set -x
PY=.venv/bin/python
CPID=$(cat logs/confirm.pid)
while kill -0 "$CPID" 2>/dev/null; do sleep 20; done
AII_DEADLINE=$(( $(date +%s) + 1500 )) $PY method.py --stage confirm  >> logs/confirm_stdout.txt 2>&1
$PY judge_local.py                                                     > logs/judge2_stdout.txt 2>&1
$PY certify.py --n 600                                                 > logs/certify_stdout.txt 2>&1
$PY analysis.py                                                        > logs/analysis_stdout.txt 2>&1
$PY rederive.py                                                        > logs/rederive_stdout.txt 2>&1
$PY make_deviations.py && $PY report_tables.py && $PY figures.py && $PY build_output.py
$PY make_readme.py
.venv/bin/python -m pip freeze > /dev/null 2>&1 || true
uv pip freeze --python .venv/bin/python > results/env_freeze.txt 2>/dev/null || true
echo FINISH_DONE

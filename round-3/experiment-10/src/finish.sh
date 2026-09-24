#!/usr/bin/env bash
# Final CPU chain once results/GEN_DONE exists. Order is deliberate: everything a later step needs is written before the
# slowest step (the independent re-derivation), and the README is generated last so it can quote the audit.
set -u
cd "$(dirname "$0")"
PY=.venv/bin/python
echo "=== finish $(date -u)" >> logs/chain.log
$PY data_usage.py    > logs/data_usage.out 2>&1;   echo "data_usage exit $?"   >> logs/chain.log
$PY analysis.py      > logs/analysis.out 2>&1;     echo "analysis exit $?"     >> logs/chain.log
$PY cross_model.py   > logs/cross_model.out 2>&1;  echo "cross_model exit $?"  >> logs/chain.log
$PY make_deviations.py > logs/deviations.out 2>&1; echo "deviations exit $?"   >> logs/chain.log
$PY report_tables.py > logs/tables.out 2>&1;       echo "tables exit $?"       >> logs/chain.log
$PY figures.py       > logs/figures.out 2>&1;      echo "figures exit $?"      >> logs/chain.log
$PY build_output.py  > logs/build_output.out 2>&1; echo "build_output exit $?" >> logs/chain.log
$PY rederive.py      > logs/rederive.out 2>&1;     echo "rederive exit $?"     >> logs/chain.log
$PY make_readme.py   > logs/readme.out 2>&1;       echo "readme exit $?"       >> logs/chain.log
echo "=== finish done $(date -u)" >> logs/chain.log

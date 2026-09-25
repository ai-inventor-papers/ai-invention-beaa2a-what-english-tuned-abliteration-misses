#!/usr/bin/env bash
# Post-panel driver: waits for the panel process to exit, then (1) re-collects all generations with judge.py (the
# OpenRouter run budget is exhausted, so new generations stay PENDING for gpt-4.1), (2) local gemma judge (second judge
# + fill-in), then in parallel (3a) the final CPU analysis and (3b) GPU post-tests + cross-machine repro check.
cd "$(dirname "$0")"
PANEL_PID=${1:-$(cat logs/method_resume2.pid)}
while kill -0 "$PANEL_PID" 2>/dev/null; do sleep 20; done
echo "panel exited $(date -u)"
.venv/bin/python judge.py --no-second > logs/finish_judge.log 2>&1; echo "judge.py exit $? $(date -u)"
.venv/bin/python local_judge.py > logs/finish_local_judge.log 2>&1; echo "local_judge exit $? $(date -u)"
(AN_JOBS=11 .venv/bin/python analysis.py --B 500 > logs/finish_analysis.log 2>&1; echo "analysis exit $? $(date -u)") &
A=$!
.venv/bin/python post_tests.py > logs/finish_post_tests.log 2>&1; echo "post_tests exit $? $(date -u)"
.venv/bin/python repro_check.py > logs/finish_repro.log 2>&1; echo "repro_check exit $? $(date -u)"
wait $A
echo "ALL DONE $(date -u)"

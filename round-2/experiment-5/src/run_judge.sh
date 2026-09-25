#!/bin/bash
# Blind judge (gpt-4.1) of all generations + gemini-2.5-flash second judge on a stratified 200; waits for the key's daily reset.
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
.venv/bin/python judge.py --wait-for-key ${WAIT_MIN:-240} --second >> logs/judge.out 2>&1
echo "judge exit $? $(date -u +%H:%M:%S)" >> logs/judge_status.txt

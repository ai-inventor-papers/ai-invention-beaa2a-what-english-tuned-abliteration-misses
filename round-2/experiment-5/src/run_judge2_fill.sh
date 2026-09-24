#!/bin/bash
# Free second-family judge over the frozen H100 harmless sample (gate cells + benign refusal); paced ~18 req/min.
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
.venv/bin/python judge.py --second-only --judge2-fill --harmless-only >> logs/judge2_fill.out 2>&1
echo "judge2_h100 exit $? $(date -u +%H:%M:%S)" >> logs/judge_status.txt

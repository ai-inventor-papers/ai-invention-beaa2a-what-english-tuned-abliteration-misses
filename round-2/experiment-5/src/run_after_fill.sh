#!/bin/bash
# After the judge2 fill: judge the Gemma dose generations (free second judge), then GaMS f in {0.25,0.5} (edit-strength midpoints).
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
until grep -q "judge2_h100 exit" logs/judge_status.txt 2>/dev/null; do sleep 20; done
until grep -q "dose gams exit" logs/run_gpu_status.txt 2>/dev/null; do sleep 20; done
.venv/bin/python dose_judge.py --model gemma --factors 1.0,1.5,2.0,3.0 >> logs/dose_judge.out 2>&1
echo "dose_judge exit $? $(date -u +%H:%M:%S)" >> logs/judge_status.txt

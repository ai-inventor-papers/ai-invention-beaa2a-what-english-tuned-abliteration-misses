#!/bin/bash
# Second GPU chain: bonus base-model diagnostic after the Gemma session, then (after the judge) the judged-reference R_seq.
cd "$(dirname "$0")"
export NUMPY_MADVISE_HUGEPAGE=0
until grep -q "gemma exit" logs/run_gpu_status.txt 2>/dev/null; do sleep 20; done
.venv/bin/python base_diag.py >> logs/base_diag.out 2>&1
echo "base_diag exit $? $(date -u +%H:%M:%S)" >> logs/run_gpu_status.txt
until [ -f logs/judge_status.txt ]; do sleep 20; done
.venv/bin/python readouts.py --source judge >> logs/readouts_judge.out 2>&1
echo "readouts_judge exit $? $(date -u +%H:%M:%S)" >> logs/run_gpu_status.txt
STAGES=rseq MODELS_TO_RUN="gams gemma" ./run_gpu.sh

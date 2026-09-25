#!/bin/bash
# STEP 4: the corrected-objective Heretic run, exactly the iteration-1 procedure (phase A: 60 seeded startup trials;
# phase B: resume to 116 COMPLETE trials), objective from runs/corrected_gemma/config.toml. Driver cwd = run dir.
cd "$(dirname "$0")/runs/corrected_gemma"
WS=../..
DEADLINE=$(( $(date +%s) + 80*60 ))
$WS/.venv/bin/python $WS/drive_heretic.py gemma_corrected A --batch-size 128 --n-trials 60 --ckpt-root $WS/checkpoints \
    --no-export --deadline-epoch $DEADLINE > $WS/logs/corrected_A.log 2>&1
echo "phase A exit $?"
$WS/.venv/bin/python $WS/drive_heretic.py gemma_corrected B --batch-size 128 --stop-at-trials 116 --ckpt-root $WS/checkpoints \
    --no-export --deadline-epoch $DEADLINE > $WS/logs/corrected_B.log 2>&1
echo "phase B exit $?"
echo CHAIN3_DONE

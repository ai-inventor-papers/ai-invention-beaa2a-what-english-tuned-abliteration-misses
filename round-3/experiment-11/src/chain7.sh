#!/bin/bash
# cut_2 executed: a SECOND optimiser seed (20260926) for the corrected objective - identical in every other respect.
cd "$(dirname "$0")/runs/corrected_gemma_s2"
WS=../..
D=$(( $(date +%s) + 45*60 ))
$WS/.venv/bin/python $WS/drive_heretic.py gemma_corrected_s2 A --batch-size 128 --n-trials 60 --seed 20260926 \
    --ckpt-root $WS/checkpoints --no-export --deadline-epoch $D > $WS/logs/corrected_s2_A.log 2>&1
echo "s2 phase A exit $?"
$WS/.venv/bin/python $WS/drive_heretic.py gemma_corrected_s2 B --batch-size 128 --stop-at-trials 116 --seed 20260926 \
    --ckpt-root $WS/checkpoints --no-export --deadline-epoch $D > $WS/logs/corrected_s2_B.log 2>&1
echo "s2 phase B exit $?"
echo CHAIN7_DONE $(date +%T)

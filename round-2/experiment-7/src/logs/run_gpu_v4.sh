#!/bin/bash
# session 4 (RTX 4000 Ada): (1) local-judge the remaining validity generations, (2) continue E1 scoring (resumable),
# with the new device's own zero point (ORIG_FULL_/ORIG_TRIM2_<dev>) and cross-device repro row, then judge again.
cd ..
.venv/bin/python panel.py --stages judge > logs/panel_judge_v4.out 2>&1
echo "JUDGE_EXIT $?" >> logs/panel_judge_v4.out
.venv/bin/python panel.py --stages edits,judge --deadline-min "$1" > logs/panel_main4.out 2>&1
echo "EDITS_EXIT $?" >> logs/panel_main4.out

#!/usr/bin/env bash
# Stage C GPU queue (resume after session interruption): two concurrent slots at 0.48 VRAM each.
# Slot A: gams_edit (resume) -> gemma_edit -> community_ref S6 ; Slot B: gemma_orig -> community_ref S5+S5X
cd "$(dirname "$0")"
PY=.venv/bin/python
export GEN_VRAM_FRAC=0.48
( $PY generate.py --model gams --ckpts gams_edit > logs/gen_gams_edit_resume.out 2>&1
  $PY generate.py --model gemma --ckpts gemma_edit > logs/gen_gemma_edit.out 2>&1
  $PY generate.py --model community --ckpts community_ref --sets S6 --out-dir results/gen_part/b > logs/gen_community_b.out 2>&1
  echo SLOT_A_DONE >> logs/gpu_queue.status ) &
( $PY generate.py --model gemma --ckpts gemma_orig > logs/gen_gemma_orig.out 2>&1
  $PY generate.py --model community --ckpts community_ref --sets S5,S5X --out-dir results/gen_part/a > logs/gen_community_a.out 2>&1
  echo SLOT_B_DONE >> logs/gpu_queue.status ) &
wait
echo ALL_DONE >> logs/gpu_queue.status

#!/usr/bin/env bash
# Full C1-BEHAVIOUR pipeline, in the order it was executed. Every step is resumable (item_key based).
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
$PY verify_pins.py                                   # Stage 0.3: revisions + shard sha256 vs iteration-1 pins
$PY freeze.py                                        # Stage A: frozen_samples.json + protocol.yaml (hashes -> logs/freeze_hashes.txt)
$PY tests/test_stats.py                              # T8 + parser/empty-label unit tests
$PY smoke.py gams && $PY smoke.py gemma --quick      # Stage B: templates, adapter T3, B2 coherence, B3 batching cert, B4 timing
# (protocol_runtime.json records the B3 decision: exact-length buckets)
for ck in gams_orig gams_edit; do GEN_VRAM_FRAC=0.48 $PY generate.py --model gams --ckpts $ck & done; wait
for ck in gemma_orig gemma_edit; do GEN_VRAM_FRAC=0.48 $PY generate.py --model gemma --ckpts $ck & done; wait
GEN_VRAM_FRAC=0.48 $PY generate.py --model community --ckpts community_ref --sets S5,S5X --out-dir results/gen_part/a &
GEN_VRAM_FRAC=0.48 $PY generate.py --model community --ckpts community_ref --sets S6 --out-dir results/gen_part/b &
wait; cat results/gen_part/a/community_ref.jsonl results/gen_part/b/community_ref.jsonl > results/gen/community_ref.jsonl
$PY autoscore.py                                     # Stage D
$PY guard_pipeline.py polyguard && $PY guard_pipeline.py llamaguard   # Stage G (GPU)
$PY judge2.py calibrate                              # B5 DEV calibration (40 iteration-1 items)
$PY reparse.py results/judge_dev_calibration.jsonl   # F8: parser fix applied to LOGGED raw outputs, never a re-call
$PY judge2.py recalibrate
$PY judge.py                                         # Stage E primary judge (gpt-4.1) - BLOCKED at 716/3840 by the run budget
$PY local_judge.py all && $PY local_judge.py retry   # F1 SUBSTITUTE judge (Qwen3-14B local): all 4800 items
$PY agreement_local.py                               # validate the substitute against the 716 gpt-4.1 labels
$PY executor_audit.py sample                         # 30 blind EN items for the EXECUTOR CHECK (labels filled in by hand)
$PY executor_audit.py score
$PY judge2.py sample                                 # Stage F second judge (gemini-2.5-flash, frozen 400) - budget permitting
$PY guard_pipeline.py adjudicate && $PY guard_pipeline.py combine
$PY agreement.py
$PY analyze.py --judge-dir results/judge_local --label-name judge_local_qwen3_14b --no-fallback   # Stage I (primary label source)
$PY analyze.py --judge-dir results/judge --label-name judge_gpt41 --no-fallback --out results/analysis_gpt41_subset.json
$PY audit.py --judge-dir results/judge_local --asr-from-guard --lang-from-glotlid   # 2nd code path + placebos
$PY verify_headlines.py                              # 3rd, from-scratch re-derivation of all headlines + permutation placebo
for st in "refs" "score --model gams" "score --model gemma" "score --model community" "report"; do $PY rseq.py $st --labels-dir results/judge_local; done  # Stage H
$PY figures.py && $PY human_packet.py && $PY build_metadata.py && $PY to_schema.py

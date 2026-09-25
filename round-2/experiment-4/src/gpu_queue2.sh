#!/usr/bin/env bash
# Post-generation GPU chain: waits for gpu_queue.sh (Stage C) to finish, then
# merge community parts -> community B1/B2 slot smoke -> autoscore (Stage D) -> PolyGuard -> Llama-Guard (Stage G).
cd "$(dirname "$0")"
PY=.venv/bin/python
until grep -q ALL_DONE logs/gpu_queue.status 2>/dev/null; do sleep 20; done
if [ -f results/gen_part/a/community_ref.jsonl ] && [ -f results/gen_part/b/community_ref.jsonl ]; then
  cat results/gen_part/a/community_ref.jsonl results/gen_part/b/community_ref.jsonl > results/gen/community_ref.jsonl
fi
$PY smoke.py community --quick --b12-only > logs/smoke_community.out 2>&1; echo "smoke_community rc=$?" >> logs/gpu_queue2.status
$PY autoscore.py > logs/autoscore.out 2>&1; echo "autoscore rc=$?" >> logs/gpu_queue2.status
$PY guard_pipeline.py polyguard > logs/guard_polyguard.out 2>&1; echo "polyguard rc=$?" >> logs/gpu_queue2.status
$PY guard_pipeline.py llamaguard > logs/guard_llamaguard.out 2>&1; echo "llamaguard rc=$?" >> logs/gpu_queue2.status
echo ALL_DONE >> logs/gpu_queue2.status

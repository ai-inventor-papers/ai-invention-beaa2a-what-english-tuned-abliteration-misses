#!/usr/bin/env bash
# Waits for the shared OpenRouter key's daily reset (00:00 UTC), probes it, then judges all saved generations
# (primary judge only; the stratified second judge runs once at the end, after the panel).
cd "$(dirname "$0")"
target=$(date -u -d "tomorrow 00:01" +%s)
case "$(date -u +%H)" in 00|01|02|03|04) target=0;; esac
while [ "$(date -u +%s)" -lt "$target" ]; do sleep 30; done
for k in $(seq 1 12); do
  .venv/bin/python judge.py --probe && grep -q '"ok": true' results/judge_probe.json && break
  sleep 300
done
.venv/bin/python judge.py --no-second

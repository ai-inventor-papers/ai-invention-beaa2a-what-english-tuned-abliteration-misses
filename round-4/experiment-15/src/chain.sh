#!/usr/bin/env bash
# Background job chain actually executed after the S4 replay (PID-based; never matches processes by name).
# usage: bash chain.sh <pid of the S4 run>
set -u
cd "$(dirname "$0")"
S4PID=$1
while kill -0 "$S4PID" 2>/dev/null; do sleep 20; done
echo "$(date -u +%FT%TZ) S4 ended" 
.venv/bin/python method.py --stages s4a || exit 1
.venv/bin/python method.py --stages s4b > logs/s4b.out 2>&1 &
BPID=$!
echo "$(date -u +%FT%TZ) s4b PID $BPID"
.venv/bin/python method.py --stages s4j2 || echo "s4j2 failed"
wait $BPID; echo "$(date -u +%FT%TZ) s4b exit $?"
.venv/bin/python method.py --stages s5 || exit 1
echo "$(date -u +%FT%TZ) CHAIN_DONE"

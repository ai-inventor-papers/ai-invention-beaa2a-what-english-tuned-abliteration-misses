#!/bin/bash
cd "$(dirname "$0")"
while kill -0 $(cat logs/chain5.pid) 2>/dev/null; do sleep 5; done
.venv/bin/python kl_arms.py > logs/kl_arms.out 2>&1
echo CHAIN6_DONE $(date +%T)

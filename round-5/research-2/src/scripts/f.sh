#!/bin/bash
# usage: f.sh <outname> <url> [maxchars]
SKILL_DIR=/ai-inventor/.claude/skills/aii-web-tools
PY=$SKILL_DIR/../.ability_client_venv/bin/python
OUT=../results/raw/$1.txt
{ echo "# fetch $2  accessed $(date -u +%F)"; $PY $SKILL_DIR/scripts/aii_fast_web_fetch.py fetch --url "$2" --max-chars ${3:-6000}; } > "$OUT" 2>&1
echo "saved $OUT ($(wc -c <"$OUT") bytes)"

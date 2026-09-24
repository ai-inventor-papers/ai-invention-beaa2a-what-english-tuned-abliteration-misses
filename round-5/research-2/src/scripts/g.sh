#!/bin/bash
# usage: g.sh <outname> <url> <pattern> [maxmatches] [context]
SKILL_DIR=/ai-inventor/.claude/skills/aii-web-tools
PY=$SKILL_DIR/../.ability_client_venv/bin/python
OUT=../results/raw/$1.txt
{ echo "# grep $2  pattern=/$3/  accessed $(date -u +%F)"; $PY $SKILL_DIR/scripts/aii_fast_web_fetch.py grep --url "$2" --pattern "$3" -i --max-matches ${4:-15} --context-chars ${5:-250}; } > "$OUT" 2>&1
echo "saved $OUT ($(wc -c <"$OUT") bytes)"

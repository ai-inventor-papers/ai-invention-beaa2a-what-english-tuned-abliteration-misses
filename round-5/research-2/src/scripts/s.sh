#!/bin/bash
# usage: s.sh <outname> <query> [mode]
SKILL_DIR=/ai-inventor/.claude/skills/aii-web-tools
PY=$SKILL_DIR/../.ability_client_venv/bin/python
OUT=../results/raw/search_$1.txt
{ echo "# search '$2' mode=${3:-general} accessed $(date -u +%F)"; $PY $SKILL_DIR/scripts/aii_fast_web_search.py --query "$2" --max-results 10 --mode ${3:-general}; } > "$OUT" 2>&1
echo "saved $OUT"

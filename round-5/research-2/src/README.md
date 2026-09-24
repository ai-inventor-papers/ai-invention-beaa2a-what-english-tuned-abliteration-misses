# Pin the neighbours and fix the citations

Iteration-5 positioning artifact for a bilingual (English / Slovene) study of refusal suppression in
`google/gemma-3-12b-it` and `cjvt/GaMS3-12B-Instruct`. **Web research only** — no GPU, no model loading, no code
run over model weights, no API calls. **OpenRouter spend: $0.00.** Everything was accessed 2026-09-24.

This artifact does four things for the final paper:

1. **Strikes the qualifiers this run's own placebos falsified** and rewrites the positioning paragraphs around the
   ordering result that survives.
2. **Gives the measurement / selection-blindness result the neighbours it never had** (21 rows), including three
   that shrink it and one that contradicts its strong form.
3. **Quotes the named consumers of abliterated checkpoints** rather than paraphrasing them, and credits the
   compression-era origin of the English-proxy principle instead of claiming it.
4. **Repairs the bibliography** — a wrong venue year, three missing arXiv ids, one mis-cited finding direction and
   one mis-placed citation.

## Layout

```
README.md                         this file
research_report.md                the full report, with the paste-ready paragraphs as appendices
reproducibility.md                how the research was actually done, including what went wrong
research_out.json                 structured output (answer, sources, follow-ups) — saved by the harness
.aii/manifest.yaml                no heavy paths; nothing marked for deletion
results/
  positioning_positive_v2.md      paste-ready paragraph for the placement result
  positioning_negative_v2.md      paste-ready paragraph for the transferable negative + its companion
  positioning_diff.md             the 7 edits against the dependency's text, verbatim before/after
  qualifier_table_v2.md           qualifier-by-qualifier verdicts; the struck row shown struck
  neighbour_table_measurement.md  M1-M21, the measurement claim's neighbours  (+ .json mirror)
  neighbour_table_positive_additions.md  P1-P5, added/re-verified for the positive  (+ .json mirror)
  consumers.md                    C1-C10, the consumers and the origin credits  (+ .json mirror)
  bibliography_repairs.md/.csv    9 repairs with BibTeX-ready field sets
  depth_attribution_provenance.md the "2-3 middle layers" provenance + reconciliation sentence
  evidenced_absence.md            A1-A6, absence claims in the required wording, with falsifiers
  search_log_iter5.md             rows 26-49, continuing the dependency's log
  carried_forward.md              the 30 rows reused unchanged, 11 of them re-verified
  dependency_deltas.md            what had to change in the dependency, and why
  claims_to_position_v2.csv       42 claims, each with a neighbour id or an evidenced absence
  reconciliation_map_v2.csv       42 rows: claim -> neighbours -> producing file -> paper sections
  failed_and_unexecuted_v2.md     tagged ledger + this round's 3 failed hypotheses and 5 retractions
  path_lint.md                    33 cited workspace paths, all resolving
  stopping_points.md              the canonical stopping-points block (copied byte-for-byte)
  raw/                            every fetch/grep extract behind every quote (100 files, ~1.6 MB)
  _dep_*.md/.csv                  the dependency files this artifact edits or extends, copied in
scripts/
  s.sh f.sh g.sh                  thin wrappers over the aii-web-tools search / fetch / grep scripts
  rows_m.py rows_p.py rows_c.py   the row data for the three tables
  self_check.py                   quote-occurrence + word-count checker; rebuilds the tables
  provenance_check.py             every declared URL must match the URL its saved extract came from
  make_v2.py                      rebuilds both v2 paragraphs from the dependency text
  path_lint.py                    re-checks every cited workspace path
```

## How to run it

```bash
python3 scripts/self_check.py    # -> 36 rows, 34 VERIFIED-QUOTE, 2 CARRIED, max 39 words, ALL CHECKS PASSED
python3 scripts/provenance_check.py  # -> 100 extracts indexed, ALL URLS MATCH THEIR EXTRACTS
python3 scripts/path_lint.py     # -> 33 paths checked, 33 resolve, 0 do not
python3 scripts/make_v2.py       # -> rebuilds positioning_*_v2.md from the dependency's text
```

`self_check.py` reads each row's `raw_file` under `results/raw/` and requires the quote to occur there verbatim
(after unicode dash/quote unification, PDF line-break repair and whitespace collapse — never word deletion). A row
whose quote cannot be found fails the build rather than shipping.

To redo the web lookups:

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel)/.claude/skills/aii-web-tools"  # the aii-web-tools skill dir
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
scripts/g.sh <outname> <url> <regex> [max-matches] [context-chars]   # saves results/raw/<outname>.txt
scripts/f.sh <outname> <url> [max-chars]
scripts/s.sh <row-number> "<query>"
```

## What a downstream reader should take from it

- The kept delta is an **ordering result on matched contrasts**, not a band prescription. The sentence to use is in
  `results/qualifier_table_v2.md` ("Delta sentence for the abstract (v2)").
- **Three claims must not appear in the paper**: that the effective region differs between the sibling
  checkpoints, that the band differs by language, and that selection blindness explains the divergent search
  outcomes. All three were killed by this run's own controls; see `results/failed_and_unexecuted_v2.md` F15-F17.
- **Every absence sentence** reads "not found by these queries" plus its row ids. Never "first to".
- Where a neighbour shrinks a claim, the narrowing belongs in the same paragraph as the claim, not in a later
  limitations section.

## Restoring removed files

**Nothing is marked for deletion.** `.aii/manifest.yaml` is `entries: []`: this artifact contains only text files
(markdown, JSON, CSV, Python) plus `results/raw/`, which is ~1.5 MB of primary-source extracts and is the evidence
base for every quoted row — it must be kept. There are no caches, checkpoints, downloads or model weights to
restore, and no file here exceeds the publish-step size limit, so the whole artifact travels with the repository.

All file references in this artifact are relative to the artifact directory, or, for other artifacts in the run,
relative to the run's `3_invention_loop/` directory. No absolute server path appears in any published file.

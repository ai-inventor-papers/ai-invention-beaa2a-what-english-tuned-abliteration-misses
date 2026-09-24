# How this research was ACTUALLY conducted

Executed 2026-09-24, roughly 22:44–01:00 UTC, in a single session. No idealisation below: this is the order things
actually happened, including the two places where the plan's expectations turned out to be wrong and the one place
where a first attempt at a deliverable had to be redone.

## Tooling

- **`aii-web-tools` skill** for everything web-facing. There were no built-in `WebSearch` / `WebFetch` tools
  available in this session, so the skill's own scripts were used throughout:
  - `scripts/aii_fast_web_search.py --query ... --max-results 10 --mode general`
  - `scripts/aii_fast_web_fetch.py fetch --url ... --max-chars N`
  - `scripts/aii_fast_web_fetch.py grep --url ... --pattern ... -i --max-matches N --context-chars N`
  - Interpreter: the skill's pre-provisioned venv at
    `<skills-dir>/.ability_client_venv/bin/python`.
- **Three thin wrappers were written first** so that every call would save its own raw output with a header naming
  the URL, the pattern and the access date: `scripts/s.sh` (search), `scripts/f.sh` (fetch), `scripts/g.sh` (grep).
  Every raw file they produced is in `results/raw/` and is cited by name from the row that used it.
- **Local Python 3** for table building (`scripts/rows_*.py`, `scripts/self_check.py`), for the positioning diff
  (`scripts/make_v2.py`) and for the path lint (`scripts/path_lint.py`).
- **No environment variables or API keys were needed or read.** The free-first search stack is keyless; the
  platform's shared OpenRouter key was never used, because nothing in this artifact needs a model call. Budget:
  $0.00.

## Order of work

1. **Read the dependency in full** (`iter_4/gen_art/gen_art_research_1/results/`): `positioning_positive.md`,
   `positioning_negative.md`, `unverified_claims.md`, `stopping_points.md`, `search_log.md`, `neighbour_table.json`
   (all 30 rows printed), `claims_to_position.csv`, `reconciliation_map.csv`, `failed_and_unexecuted.md`.
2. **Checked this run's own numbers against the files that produced them**, with `grep`/`sed`/small Python over
   `iter_4/gen_art/gen_art_experiment_13`, `_14`, `_15`, `iter_4/gen_art/gen_art_evaluation_2`,
   `iter_2/gen_art/gen_art_experiment_4` and `_6`, and `iter_3/...`. This is where the three falsified qualifiers
   were confirmed from the primary result files rather than from prose: `NAMED_AND_LOST` rows and Tables 6/6b/7 in
   experiment 14, `language_swapped_O_spearman = -0.941` in experiment 13's `analysis.json`,
   `paired_headline.verdict_PRED_1 = "FALSIFIED"` in experiment 15's `analysis.json`.
3. **Read the iteration-4 draft and the reviewer's verification log** to get the four bibliography defects in their
   own words (`iter_4/gen_report_text/gen_report_text/paper_draft.md` lines 900-935 and
   `iter_4/review_report/review_report/notes/verification_log.md`).
4. **Fetched 22 abs pages in parallel** (ids listed in `results/search_log_iter5.md` row 48) to resolve titles,
   authors, versions and venue comments. This is where the ICLR-2025 comment field, the 2408.17003 v1/v5 title
   drift, the EMNLP-2026 acceptance of 2608.22490 and the EACL-2026 acceptance of 2601.18306 came from.
5. **Grepped the primary PDFs/HTML for each quote** (row 49), in batches of 5-10 parallel calls. Quotes were copied
   from those saved extracts, never from a search snippet or an aggregator page.
6. **Ran 22 discovery/adversarial searches** (rows 26-47), including the deliberately scoop-seeking ones. Six
   returned NO NEIGHBOUR FOUND and are the evidence behind `results/evidenced_absence.md`. Two returned the
   neighbours that most narrowed this run's claims (2510.02768 from row 44, 2603.06594 from rows 34 and 42).
7. **Built the row tables and the checker**, then fixed what the checker caught.
8. **Built the v2 paragraphs by programmatic edit** of the dependency's text, so "carried character-for-character"
   is enforced rather than asserted.
9. **Ran the path lint** over every path this artifact cites.
10. **Wrote the report, README and manifest.**

## The searches, in the order they were run

Rows 26-47 of `results/search_log_iter5.md` are in execution order, with each query verbatim, the top results
examined and the outcome. Rows 48-49 list every URL fetched or grepped. Raw outputs: `results/raw/search_26.txt`
… `search_47.txt` (searches), `results/raw/abs_*.txt` and `g_*.txt` (fetches and greps).

## Things that did not go as planned

- **The plan's expectation about arXiv 2609.10594 was wrong.** It was named as the closest neighbour for
  "substring metrics over-report removal". Two greps over the full PDF
  (`results/raw/g_2609.10594_string.txt`, `g_2609.10594_findings.txt`) show it compares six LLM-based evaluators
  and mentions string matching only as background. The sentence the plan wanted is StrongREJECT's. Recorded as a
  correction in row M2 and in the report, not quietly dropped.
- **The plan's numbers for arXiv 2607.02235 were not in the paper.** Greps for `agreement|kappa|80%|60%|script`
  and for `[0-9]{2}%|correlat|human validation|reliab|single judge` return ~80% as Zheng et al.'s English MT-Bench
  figure and no <60% figure. M16 quotes what the paper does say.
- **2505.19056's paired numbers mean the opposite of what the plan assumed.** They are real and in Table 4 of
  Appendix A, but the authors read them as agreement within 4 percentage points, not divergence. That flipped the
  row from "the closest instance of our divergence" to "the closest instance of our PRACTICE, and a contrast to our
  finding".
- **arXiv 2408.17003 turned out closer than planned.** The plan anticipated it might only localise safety layers.
  Its §3.4 procedure actually compares layer RANGES by scaling their weights, which is a weight-space range
  comparison. That produced edits E5 and E7 (a new paragraph sentence and a narrowed load-bearing qualifier) rather
  than a footnote.
- **One deliverable had to be rebuilt.** The first attempt at the row-data file was truncated mid-row; the
  remaining rows were appended in smaller batches (`scripts/rows_m.py` carries the seam, which is harmless because
  `self_check.py` validates the assembled list).
- **The output verifier rejected one published passage after the first submission**, and it was my bookkeeping
  error, not a bad quote: source [8]'s sentence had been extracted from the arXiv **abs page** (where it is
  continuous) while the source entry cited the **PDF** (where it is line-broken as "ex-\nisting validation
  protocols"). Fixed by pointing the three affected sources (8, 12, 27) at the abs pages their extracts came from
  and re-fetching each passage live to confirm it is there (rows 50-52 of the search log). I then added a
  provenance check comparing every declared URL against the URL in the header of the raw extract the quote came
  from; it caught one more mismatch, row C7, which was corrected the same way. No quote text was weakened: the
  only change to a quote was extending source [8]'s to end at a word boundary ("inherent to red-teaming").
- **The checker rejected five of my own quotes on the first run** — one over 40 words, four not matching their raw
  extract. Causes: a PDF page-break artifact inside a sentence (2607.02714), line-break hyphenation inside a model
  name (`Llama-3.1-70B-\nInstruct`), and two rows pointing at the wrong raw file. Fixes: three normalisation modes
  in the checker, a `" [...] "` marker for a quote that spans a page-break artifact, and corrected `raw_file`
  fields. No quote was loosened to make it pass.

## How to retrace this

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel)/.claude/skills/aii-web-tools"  # the aii-web-tools skill dir
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"

# 1. re-verify every quote against freshly fetched primary sources
#    (scripts/g.sh re-saves each extract with today's date in its header)
scripts/g.sh recheck_2408.17003 https://arxiv.org/pdf/2408.17003 "contiguous|middle|over-reject|scaling" 20 250
scripts/g.sh recheck_2510.02768 https://arxiv.org/pdf/2510.02768 "regex tends to over" 3 600

# 2. re-run the checks
python3 scripts/self_check.py      # 36 rows, quote occurrence + word counts
python3 scripts/path_lint.py       # 33 cited workspace paths
python3 scripts/make_v2.py         # rebuild both v2 paragraphs from the dependency text
```

Search results drift. The row ids in `results/search_log_iter5.md` fix what was examined on 2026-09-24; the
quotes are anchored to arXiv version numbers, so a re-grep of the same version should reproduce them exactly, while
a re-run of the searches may surface newer neighbours. If it does, the falsifiers named in
`results/evidenced_absence.md` say what to do with them.

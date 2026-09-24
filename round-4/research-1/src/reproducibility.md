# Reproducibility — how this positioning research was actually conducted

**Date of all web access: 2026-09-24.** Web results drift; a reader re-running these queries later will get a different ranking, and arXiv identifiers in the 26xx range are recent enough that versions may change. Everything quoted here was retrieved on that date and the raw retrieval output is committed under `results/raw/`, so the quotes can be checked without re-running any search.

There is **no experiment and no code to re-run** beyond `scripts/self_check.py`. No model was loaded, no GPU was used, no paid API was called. Total spend: **$0** (the shared OpenRouter key was not used; this artifact needs no LLM call).

## Tooling actually used

- The `aii-web-tools` skill was loaded first. Its instructions say to prefer built-in `WebSearch`/`WebFetch` when they exist, so `ToolSearch("select:WebSearch,WebFetch")` was called once to load them, and **discovery** was done with the built-in `WebSearch` tool.
- **Exact extraction** — every quote and every number attributed to a source — used the skill's own script, never a summary:
  ```bash
  export SKILL_DIR=/ai-inventor/.claude/skills/aii-web-tools
  export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
  $PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url <URL> --pattern <REGEX> -i \
      --max-matches N --context-chars C
  ```
  Identifier resolution used the same script's `fetch` subcommand on each `arxiv.org/abs/<id>` page before anything else was believed about that paper.
- **Environment variables / keys:** none were set by this artifact. The `aii-web-tools` scripts call an internal ability server which may use a `SERPER_API_KEY` as a paid fallback when the free engines miss; no value is printed or stored anywhere in this workspace. The built-in `WebSearch`/`WebFetch` tools need no key from the caller.
- No `WebFetch` "gist" summary was ever quoted. Where `WebFetch`/`WebSearch` snippets suggested a claim, the claim was re-retrieved by regex over the source's full text before being written down (this is why several search-result assertions in the log are marked "source to be located" and then resolved in a later row).

## What was read locally, read-only, before any search (step R0)

By absolute path under `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/`:

| input | what was taken from it |
|---|---|
| `iter_4/gen_strat/gen_strat_1/.terminal_claude_agent_struct_out.json` | the two results to position, the six targets, the candidate identifiers, the stopping points. Treated as a PLAN: none of its numbers were used as a source. |
| `iter_3/gen_art/gen_art_evaluation_1/results/` (`novelty_table.md`, `claims_registry.csv`, `dead_end_ledger.md`, `pending_human_review.md`, `corrected_numbers.json`, `gap_range_summary.csv`, `report_repairs.md`) | the predecessor neighbour pass, the claim inventory, the failed/unexecuted split, the translation provenance, and the only admissible corrected numbers for iterations 1–2. |
| `iter_3/gen_art/gen_art_experiment_{9,10,11,12}/` (`report_tables.md`, `analysis.json`, `analysis_summary.json`, `miscalibration_table.csv`, `audit_headline.json`, `selection_point_cert.json`, `verify_numbers.json`, `load_log.json`, `README.md`) | every iteration-3 number quoted in the positioning paragraphs, each cited by its own path. |
| `iter_2/gen_report_text/gen_report_text/paper_draft.md`, `iter_3/gen_report_text/gen_report_text/paper_draft.md`, `iter_2/review_report/review_report/notes/recompute_log.md`, `iter_3/review_report/review_report/.terminal_claude_agent_struct_out.json` | the sentences needing neighbours and the reviewer's standing novelty objection. **No number was taken from either draft**; the recompute log shows why (multiple MISMATCH rows, one with the sign of the conclusion reversed). |

## Order in which the work was actually done

1. R0 — read the strategy, the audit artifact and the drafts; traced where the `2-3 middle layers` attribution entered the run (it first appears in `iter_3/gen_strat` and `iter_3/gen_plan_*` files, not in any executed artifact).
2. Identifier resolution: 9 `arxiv.org/abs/<id>` pages fetched in parallel. All nine resolved to the titles the strategy named; two (2609.22135, 2608.05164) turned out to be about emotion steering and SAE concept transfer, **not** refusal or language, which materially changed the delta wording.
3. R2 (run early, deliberately) — the negative's neighbours: 8 discovery queries including four adversarial ones, then exact extraction from Hase et al. 2023, 2606.00926, 2609.04721, 2608.24988.
4. R3 — Arditi et al. full-text extraction, then the **single bounded verification pass** on arXiv 2607.02714: `abs` page, PDF v1, PDF v2 and HTML v2, with the regexes recorded in `results/unverified_claims.md`. Outcome: the sentence exists in §3.2 of both PDF versions as an attribution to Arditi et al.; the corresponding claim was **not found** in Arditi et al. by the queries run, and 2607.02714 rejects it in the following sentence. The inherited flag is resolved with that correction, not laundered.
5. R4 — StrongREJECT, XSTest, 2609.00498, plus the adversarial query that found AdvPrefix (2412.10321), which is the closest neighbour on the selection side and forced the objective-blindness claim to be narrowed.
6. R5 — Wang et al. full text (language list, all-layer ablation), 2608.08032, 2608.11146, 2606.01196, 2608.29936, and the adversarial language-depth query that surfaced 2609.22144 — a partial scoop that narrowed the positive's delta.
7. R6 — Heretic tooling state: repo README, `raw.githubusercontent.com/p-e-w/heretic/master/config.default.toml`, PR #444, PR #445, releases page, and the `heretic-org/Multilingual-Harmless-Harmful` dataset card (9 subsets, no Slovene).
8. R7–R9 — synthesis into `results/`, the canonical stopping-points block, and `scripts/self_check.py`, which was run until it printed `SELF-CHECK PASSED`.

## Retracing this investigation

```bash
# 1. the six self-checks over the shipped files
python3 scripts/self_check.py

# 2. re-verify any quote without re-running a search (example: the inherited attribution)
export SKILL_DIR=/ai-inventor/.claude/skills/aii-web-tools
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url https://arxiv.org/pdf/2607.02714v2 \
  --pattern "middle layer|2-3|2–3|two to three|two or three|few layers|as effective as|all layers|single layer" \
  -i --max-matches 40 --context-chars 300

# 3. the counter-check in the paper it is attributed to
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url https://arxiv.org/pdf/2406.11717v3 \
  --pattern "middle layers|narrow|local region|single layer|subset of layers|all layers|2-3|2–3|few layers" \
  -i --max-matches 40 --context-chars 300
```

Every other quote in `results/neighbour_table.md` can be re-checked the same way: the URL is in the table, the locator names the section, and the raw output of the original call is already in `results/raw/` under a filename derived from the identifier.

## Known limitations of this method

- **Not a systematic review.** 24 discovery queries and ~40 extraction calls, in a fixed priority order, with a declared cut order. A neighbour can have been missed; the mitigation is that the queries are logged so a reviewer can see exactly what was and was not asked.
- **Search-engine drift and regional bias.** The built-in `WebSearch` is US-only, and both engines re-rank over time. The two searches that mattered most (the negative's absence claim, and the language-depth scoop check) were each run with four differently-phrased queries for this reason.
- **A previous pass in this run missed a sentence that was present** (the `2-3 middle layers` case), because a truncated match list hid §3.2. That is the reason every extraction here uses an explicit `--max-matches` large enough to reach the body of the paper, and the reason the verification pass was run against the PDF as well as the HTML.
- **One-pass verification by design.** Where a claim could not be located, the recorded outcome is "not found by these queries", which is weaker and more accurate than "does not exist".

## Quote verification pass (run last, 2026-09-24)

After the structured output was assembled, every supporting passage in it was re-fetched and regex-matched against the URL it is attributed to, by `results/quote_verification.txt`'s generating loop (fixed-string pattern over the first 120 characters of each quote, via the same `aii_fast_web_fetch.py grep` script). Result: **44 passages, 42 matched on the first pass, 2 failed and were corrected** —

- source 18 (arXiv 2608.08032): the sentence quoted from an earlier extract spanned a PDF line break, so the quote was replaced with the single-line Appendix C sentence "mean cross-lingual Jaccard rises through the mid-network, peaks at 0.43 at L11", and the prose was reworded to match the verified numbers (0.43 at L11, 0.027 at L18);
- source 33 (arXiv 2608.29936): the passage is on the abstract page, not in the PDF body text as fetched, so the URL was changed to the `abs` page.

Both were re-checked and match. `results/quote_verification.txt` holds the full pass. This is a mechanical occurrence check only: it shows the string is present at that URL, not that the claim it is cited for follows from it.

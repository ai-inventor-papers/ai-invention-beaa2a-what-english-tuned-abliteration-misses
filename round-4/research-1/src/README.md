# Positioning the two reportable results: nearest published work, deltas, stopping points

Web-research-only artifact (iteration 4, slot 5). **No code was run against a model, no GPU, no paid API call, $0 spend.** It produces the related-work spine for the final paper: one row per neighbour with a verbatim quote and its location, two positioning paragraphs (one per result), a tagged ledger separating what failed from what was never run, a claims-to-neighbour map, and the canonical limits block the paper reuses verbatim.

All web access: **2026-09-24**. All local inputs were read **read-only** by absolute path; nothing outside this workspace was written.

## What it answers

1. **RESULT 1 (positive).** At matched total edit size and matched layer count, where in depth a refusal-removal edit acts decides how much refusal survives, per language and per checkpoint. Nearest work: effect-based site selection (2609.22135, 2606.00926, Hase et al. 2023), depth-distributed refusal (2607.02714, 2608.11583, 2608.01414), and — the neighbour that narrows the delta — language-specific safety-sensitive layers (2609.22144).
2. **RESULT 2 (the more transferable negative).** An activation-space depth measurement fails to predict weight-edit outcomes cross-lingually (Spearman -0.009), direction cosine fails beside it (+0.010), and two one-forward-pass baselines win (+0.732 and +0.661). Partial neighbours exist (Hase et al. 2023; 2606.00926; 2609.04721; 2608.24988); **the conjunction was not found** after the logged searches, and that absence is reported as "not found by these queries".
3. **The inherited unverified attribution is resolved.** The `2-3 middle layers` sentence **does** exist in arXiv 2607.02714 §3.2 — as that paper's own attribution to Arditi et al., which we could not locate in Arditi et al., and which 2607.02714 rejects in the next sentence. See `results/unverified_claims.md`.

## Layout

| path | contents |
|---|---|
| `results/neighbour_table.md` | the 30-row neighbour table: verbatim quote + locator + URL + what it establishes + delta + stopping point |
| `results/neighbour_table.json` | the same table, machine-readable, one object per neighbour (`N1`–`N30`) |
| `results/claims_to_position.csv` | 30 claims the paper will make, each with its tag, its producing path, its number's path, its neighbour ids, and its status |
| `results/reconciliation_map.csv` | claim id -> neighbour ids -> producing file path -> tag -> which paper sections must agree |
| `results/positioning_positive.md` | paste-ready paragraph for RESULT 1 plus the qualifier-by-qualifier delta check |
| `results/positioning_negative.md` | paste-ready paragraph for RESULT 2, the practitioner recommendation, and the selection-blindness companion |
| `results/unverified_claims.md` | the bounded verification pass on the inherited attribution, and what still cannot be verified |
| `results/failed_and_unexecuted.md` | 14 FAILED HYPOTHESES (with the number and direction that killed each) vs 10 UNEXECUTED PROPOSALS (with reasons) |
| `results/stopping_points.md` | the canonical limits block, written once, with per-line provenance |
| `results/search_log.md` | every query, engine, date and outcome, including the queries behind the evidenced absence |
| `results/raw/` | raw `fetch`/`grep` output for every source, so each quote is checkable without re-searching |
| `scripts/self_check.py` | the six shipping checks (quote length, URL+date+locator, no unclosed claim row, numbers carry paths, tag vocabulary, forbidden verbs on unrun work) |
| `results/quote_verification.txt` | mechanical re-check that every quoted passage occurs at the URL it is attributed to (44 passages; 2 corrected and re-checked) |
| `results/_sources_for_research_out.json` | the source list handed to the bibliography step (no BibTeX is hand-written here) |
| `reproducibility.md` | how this was actually done, in the order it was done, with the exact commands |

Every line in these files carries exactly one of four tags: **OBSERVATION**, **INTERPRETATION**, **FAILED HYPOTHESIS**, **UNEXECUTED PROPOSAL**. The tags travel into the paper.

## How to run

```bash
python3 scripts/self_check.py     # must print: SELF-CHECK PASSED: all 6 checks green
```

Re-verifying any quote needs only the `aii-web-tools` grep script; the exact commands are in `reproducibility.md`.

## Restoring removed files

**Nothing was removed, so nothing needs restoring.** `.aii/manifest.yaml` has `entries: []`: this artifact produced only small text files (markdown, CSV, JSON and one Python script), with no large binaries and no caches, so no path carries a `delete` decision and there is no restore command to give. The raw retrieval outputs in `results/raw/` (1.3 MB of text) are part of the deliverable — they are the evidence behind each quote, and re-fetching them later would return different page states.

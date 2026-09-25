# How blind is an English-only refusal score

A CPU-only **measurement audit** of Heretic's English keyword refusal rule (the pinned 33-substring
`KeywordRate` list, Heretic 3521f864), built entirely from per-item and per-candidate files that earlier artifacts of
this run already put on disk. It loads no model, generates nothing, produces no edit and spends $0 on API calls. It
asks three questions:

* **Leg A:** How blind is the objective inside its **own** candidate pool, in both Heretic searches of the run
  (gemma-3-12b-it and GaMS3-12B-Instruct, 116 candidates each)?
* **Leg B:** How large is the keyword score's under-report **per language**, cell by cell, against certified
  references on the same items? How much of it is the rule being silent on Slovene?
* **Leg C:** How far could one named downstream multilingual design move if it assumed the ablation lands equally in
  every language? This is reported as a bounded sensitivity range, not a re-estimate.

**Status:** all five placebos pass. eval.py and the independently written rederive.py agree on 573/573 shared
statistics. 0 cited paths fail the lint. No leg is marked UNRELIABLE.

## Headline results (all recomputed; exact sentences with sources in `results/paste_text.md`)

| # | Result | Value | Source |
|---|---|---|---|
| A1 | Objective floor vs rule threshold (≤10/100) | floor **72** (gemma) and **16** (GaMS3); the primary branch cannot fire and the fallback fires in **both** searches | `results/blindness_per_search.csv` |
| A1 | Threshold-blind fraction (classifier reference) | **1.00** in both: 6/6 (CP 95% lower bound 0.54) and 37/37 (0.91). Judge-referenced: 5/5 and 6/6 (GaMS3: 70 judged candidates) | same |
| A2 | Calibration K on C (on J) | slope 0.308 / 0.738 (0.316 / 0.813); mean K−ref +20.5 / +15.0 (+19.6 / +6.0); Spearman 0.924 / 0.969. This is range compression, not mis-ranking | same |
| A3 | Low-region blindness (C ≤ 50) | gemma **0.470** (23 candidates), which **equals** the permutation chance level of 0.459; GaMS3 0.017 (chance 0.265) | `results/blindness_per_search.json` |
| A3 | Frozen "one search is blinder" prediction | **FALSIFIED**: +0.006 [0.000, 0.019] (C); sign reverses when judge-referenced, −0.029 [−0.060, −0.005] | same |
| A4 | Held-out agreement, edited checkpoints | EN κ 0.021 (n=490): **MISFIRING**, positive rate 0.341 vs reference 0.173, FP share 0.814. SL κ 0.000 (n=490): **SILENT**, the rule fires on **0/490**, reference 0.439; FP share undefined (0/0), not "0.000" | `results/heldout_agreement.csv` |
| B2 | Δ_lang = d_SL − d_EN, gemma_edit, 100 verified pairs | **−1.56 [−1.68, −1.44]** = rule positive-rate shift −0.87 + reference-level difference −0.69. PolyGuard channel −1.49; Rogan-Gladen −1.78 | `results/delta_lang.csv` |
| B2 | Original (unedited) checkpoints | Δ_lang ≈ **−1.01** in all four cells, almost entirely rule silence | same |
| B4 | Guard channel vs judged refusal | 0 of 26 cells order EN/SL differently; unadjudicated guard items carried as intervals (e.g. community_ref SL S5 ASR [0.714, 0.893]) | `results/guard_beside_refusal.csv` |
| B5 | Judge sensitivity | 72 JUDGE_SENSITIVE, 6 JUDGE_ROBUST. The SL gate is unmet (κ 0.723 unweighted), and the panel within-edited gates miss in EN too (exp4 0.42, exp11 0.23; exp11 SL 0.745) | `results/judge_sensitive_registry.json` |
| C | Cost-difference shift (ASSUMPTION form) | between **−1.68 and −0.11** refusal-rate units across the three ablated exp4 checkpoints and both channels. The residual-refusal ordering of EN vs SL **inverts** between the keyword and reference views (gemma_edit and community_ref under both channels; gams_edit under PolyGuard only) | `results/downstream_sensitivity.csv` |

**How to read the Slovene zero.** κ = 0.00 on Slovene does not mean the keyword rule "disagrees" with the judge. It
means the rule never fires on Slovene text. On edited English the rule fires often and is wrong (FP share 0.81).
These are opposite failures, so a sentence of the form "κ 0.02 EN / 0.00 SL" must be replaced by the wording in
`results/paste_text.md` §6.

**How to read Δ_lang.** On the gemma_edit pairs, the per-language disagreement **rates** happen to be equal (exact
McNemar p = 1.00), but their **directions** are opposite: English errors are false refusals and Slovene errors are
missed refusals (exact sign test p = 5e−29). A keyword-measured cross-language gap equals the reference gap plus
Δ_lang, so the rule's language biases any EN–SL comparison it is used for.

## Reconciliations and plan mismatches (see `results/audit_log.json`)

* **Calibration numbers.** The plan's 0.308/0.738 and +20.5/+15.0 are **classifier**-referenced. The strategy's
  0.32/0.81 and +19.6/+6.0 are **judge**-referenced (0.316/0.813, +19.6/+6.0). Both are correct; every shipped slope
  names its reference.
* **"0.744".** This is exp11's Slovene within-edited κ (companion panel table, n=70). The language-level certification
  file gives κ 0.723 unweighted / 0.871 weighted, and the gate is **not met**.
* **Second leg-C quote.** "non-English users consistently bear a higher Safety Cost than English users" is **not** in
  the verified quote field of neighbour_table N20; only a paraphrase is. It is not quoted verbatim anywhere here.
* **Pinned marker source.** `iter_1/.../env/heretic_src/config.py` holds no marker list. The verbatim list was read
  from the dataset artifact's copy of Heretic 3521f864's default config
  (`round-1/dataset-1/src/data/provenance/heretic_3521f864_config.default.toml`) and is identical to
  art_0XmNBGkzsJc_'s `keyword_rate.py`. P3 then reproduces all 8,480 stored keyword verdicts exactly.
* **Companion artifacts.** The Slovene re-certification purchase in this round was blocked (HTTP 403, 0 items). No new
  Se/Sp exists, so Rogan-Gladen companions use the evaluation_2 certification (SL Se 0.697, Sp 0.980, n=456). The
  in-progress companion `round-5/evaluation-4/src/results/judge_agreement.csv` was consumed for
  panel-specific gate status (sha256 and mtime in the registry).

## Departures from the field's practice (costs stated)

No human reference anywhere: every reference is an LLM judge, a distilled classifier or a guard model, so the correct
reading is "certified against a frontier-proxy reference", not "accurate". The Slovene reference is uncertified;
Slovene rows therefore ship raw + Rogan-Gladen, flagged JUDGE_SENSITIVE. All generations are NF4. Slovene is
machine-translated (native review PENDING), so "silent on Slovene" means "silent on this Slovene material". The
panels cover two searches, one outside-family edit, one seed per search and two languages. Candidate-level CIs are
not optimiser run-to-run variance. RefusEU official EN/SL rows are **unpaired** (0/1400 graded translations): they
get no paired test, and every paired claim uses the verified S5X / S4hoc pairs.

## Settled negatives reused (not re-analysed)

* Between-search blindness prediction: falsified, +0.006 [0.000, 0.019], sign reversing judge-referenced (recomputed
  here, leg A3).
* Partial-transition account: falsified by its own frozen rule (art_0XmNBGkzsJc_, P7).
* Depth-redundancy index as a predictive instrument: falsified out of family (iter-4 draft).
* Language-conditioned and checkpoint-specific readings of the placement observation: falsified by the run's
  placebos. **This artifact adds nothing to the placement question** (see `configs/scope_guard.md`).

## Layout

| Path | What |
|---|---|
| `eval.py` | Analysis path 1: S0 inventory, legs A/A4/A5/B1–B5/C, placebos P1, P2, P3, P5 |
| `common.py` | Paths, pinned keyword rule, truncation, κ/PABAK/AC1, bootstraps, Rogan-Gladen (used by eval.py only) |
| `rederive.py` | Analysis path 2: pure standard library, own parsing, own statistics and RNG → `results/rederive.json` |
| `audit.py` | Cross-path comparator, P4 planted errors, path lint, audit log, `eval_out.json`, `paste_text.md` |
| `figures.py` | The three figures |
| `configs/scope_guard.md` | What this artifact does not compute |
| `eval_out.json`, `full_/mini_/preview_eval_out.json` | Top-level copy of `results/eval_out.json` and its aii-json variants |
| `results/eval_out.json` | Schema `exp_eval_sol_out`: headline `metrics_agg` plus per-row examples |
| `results/paste_text.md` | Paste-ready sentences with sources, plus the iter-4 draft lines they replace |
| `results/blindness_per_search.{csv,json}` | Leg A1–A3 (and the falsified prediction) |
| `results/heldout_agreement.csv` | Leg A4, per language × original/edited × {first-100-token, full-response} view |
| `results/reselection_scope.csv` | Leg A5 (identifier, branch, reference count, KL only) |
| `results/discrepancy_per_cell.csv` | Leg B1: 177 rows (artifact × unit × set × language × reference channel) |
| `results/delta_lang.csv` | Leg B2–B3: Δ_lang on verified pairs with decomposition, McNemar and sign tests, Rogan-Gladen |
| `results/guard_beside_refusal.csv` | Leg B4 |
| `results/judge_sensitive_registry.json` | Leg B5 (machine-readable flags) |
| `results/downstream_sensitivity.{csv,md,json}` | Leg C, with the `scope_caveat` column |
| `results/placebos.json` | P1–P5 with their statistics |
| `results/audit_log.json`, `results/path_lint.json`, `results/source_inventory.json` | Audit trail, lint and input inventory (sha256, record counts, schema keys) |
| `results/items_scored.parquet` | Item-level table: keyword verdicts and reference labels per item (no response text) |
| `results/eval_core.json`, `results/rederive.json` | Raw outputs of the two code paths |
| `figures/fig_floor_threshold`, `fig_discrepancy_forest`, `fig_delta_lang_decomp` (`.pdf`/`.png`) | Figures |

All input paths are relative to the run's `3_invention_loop/` directory and are read-only. The root is set once (`LOOP` in `common.py` / `rederive.py`), and `AII_LOOP_DIR` overrides it. Full reproduction steps are in `reproducibility.md`.

## How to run

```bash
uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock.txt
.venv/bin/python eval.py       # ~15 s; downloads only the Gemma tokenizer.json (pinned revision) into the HF cache
.venv/bin/python rederive.py   # ~5 s
.venv/bin/python audit.py      # comparator, P4, lint, eval_out.json, paste_text.md
.venv/bin/python figures.py
```

Seeds: 20260924 (bootstrap, B=2000); seed 2 for the paired-draw bootstrap (reused from the source artifact); 1000
permutations for the placebos.

## Restoring removed files

| Removed path | Restore with |
|---|---|
| `.venv/` | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock.txt` |
| `__pycache__/` | regenerated automatically by running any script |

No model weights, checkpoints or large binaries are produced or kept by this artifact.

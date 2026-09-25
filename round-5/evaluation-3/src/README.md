# Final audit: recompute every number, classify every claim

Terminal, audit-only evaluation for the bilingual (English / Slovene) refusal-suppression study on
`google/gemma-3-12b-it` and `cjvt/GaMS3-12B-Instruct`. It re-derives the draft's headline numbers from the
per-item result files that earlier rounds saved. It classifies each saved source as a real run or a stand-in, and each draft assertion as
an observation, interpretation, failed hypothesis or unexecuted proposal. It then reconciles the iteration-4 draft
(`iter_4/gen_report_text/gen_report_text/paper_draft.md`) against the recomputed values.

**What this artifact does not do:** it loads no model and generates nothing. It has no metric that ranks edit
configurations by how well they remove refusal, and it names no optimal layer, depth band or edit strength. The
depth-band confirmation panel dropped in `iter_5/gen_strat/gen_strat_1` was never run. It appears in the scope table as not
executed.

## Main results (all from `results/AUDIT_REPORT.md`, generated from the saved outputs)

* **The English keyword selection objective cannot fire its own selection rule.** Heretic's primary branch needs a
  candidate with at most 10/100 refusals. Under the keyword counter, 0/116 candidates in either search reach it:
  the floor is 72 for Gemma and 16 for GaMS3. Under the distilled classifier, 6 and 37 candidates do. I re-derived the Gemma keyword
  counts from the raw in-loop generations, and they match on 116/116 draws.
* **On held-out-category StrongREJECT outputs of the edited Gemma arms, the objective shows no usable agreement:**
  English κ = 0.02 [−0.09, 0.14] (n = 490) against Qwen3-14B strict labels, 0.09 against broad (refused + partial), and
  −0.14 / −0.08 against the 38 on-disk gpt-4.1 labels. These prompts do not overlap the objective's in-loop prompts or Heretic's
  construction data.
* **The "κ = 0.00 in Slovene" is not measured chance agreement.** The English-only marker list never fires on Slovene
  output: 0/490 edited and 0/70 original held-out responses, and 0% on RefusEU for every checkpoint, while the judge finds Slovene refusal in up to 96% of the
  same outputs. κ is 0 by construction. The accurate statement is that the objective has zero sensitivity to Slovene
  refusal.
* **Reproduced:** guard-safety of non-refusals, Gemma edit, SL − EN = +0.231 [0.123, 0.340] (EN 0.106, n = 245;
  SL 0.338, n = 80). Also reproduced: the Gemma matched-group placement contrasts (−0.688 EN / −0.377 SL, 8/8 groups), the GaMS3
  ρ = −0.903 with null controls, and the Qwen3-8B contrasts (9/9 favour high-O, 8/9 CIs exclude 0).
* **Not supported, to be struck:** "judged refusal and guard ASR order the two languages oppositely". On 21
  paired cells, 15 show the same ordering (11 with both CIs excluding 0), 1 shows the opposite ordering (CI not excluding 0), and
  5 are ties.
* **14 discrepancies in the draft** out of 121 checked claims (section 3 of the report). Examples: the Evaluation-2
  non-refusal numbers (7.2% / 32.7%) belong to a different arm; the trial-96 and trial-107 judge counts are wrong;
  the abstract claims Qwen3-8B ρ > 0.83 but it is 0.76; the abstract reverses the NF4/bf16 attenuation direction;
  exp14 Slovene values are labelled English; two fig_gams3_profile bar values are wrong; fig_dose_response plots substring
  "marker" refusal. Also 9 unresolved citation paths, and 12 claims resting on a judge that failed its certification gate.
* **The distilled classifier is not held-out on these items:** its training pool contains all 140 held-out prompts
  (responses from other checkpoints). Its held-out κ must be reported as in-distribution.

## Layout

| path | what it is |
|---|---|
| `eval.py` | the whole audit: provenance inventory, per-cell recomputation (exp4, exp11, exp13, exp14, exp5 T1), held-out objective agreement, self-firing, disjointness, claim registry vs draft, surface reconciliation, citation lint, evidence ledger, scope table, measurement bias |
| `report.py` | renders `results/AUDIT_REPORT.md` from eval.py's outputs (no hand-typed numbers) |
| `figures.py` | `figures/fig1_objective_agreement.*`, `figures/fig2_measurement_bias.*` |
| `rederive.py` | independent stdlib re-derivation of 14 headline numbers, with permutation placebos -> `results/rederive.json` (14/14 match, placebos fail as required) |
| `reproducibility.md` | exact commands, versions, inputs by artifact id, expected numbers |
| `requirements.lock` | full pinned environment (`uv pip freeze`) |
| `label_gpt41.py` | attempted purchase of gpt-4.1 labels for the 1,120 held-out items (blocked by the platform key limit, $0.00 spent) |
| `eval_out.json` / `full_eval_out.json` | schema `exp_eval_sol_out`: `metrics_agg` + 9 datasets (recomputation_fidelity, selection_objective_agreement, per_cell_behaviour_exp4, cross_lingual_measurement_bias, guard_safety_of_nonrefusals, evidence_status_ledger, citation_path_lint, scope_table, provenance_inventory) |
| `mini_eval_out.json`, `preview_eval_out.json` | first 3 examples per dataset (preview: strings truncated to 200 chars) |
| `results/AUDIT_REPORT.md` | the human-readable audit (start here) |
| `results/recomputed_all.json` | every recomputed quantity with CIs, denominators and marginals |
| `results/claim_registry.csv` | 121 draft claims: location, draft value, recomputed value, CI, status, source, scorer status, surfaces quoting it |
| `results/evidence_ledger.csv` | 897 draft assertions, each with one evidence class and its backing workspace or registry link |
| `results/citation_lint.csv` | every in-text file citation and whether it resolves |
| `results/scope_table.csv` | checkpoint × language × prompt set: executed or not, n, decoding, seed |
| `results/measurement_bias.csv` | paired SL−EN judged refusal vs guard ASR per cell |
| `results/provenance_inventory.csv` | every source file with sha256 and real-run / stand-in class |
| `results/gpt41_purchase_attempt.json`, `results/gpt41_key_block_evidence.txt` | evidence of the blocked gpt-4.1 purchase |
| `configs/exp4_frozen_judge_protocol.yaml` | verbatim copy of the frozen judge rubric (used only by `label_gpt41.py`) |
| `logs/` | run logs |

## How to run

The inputs are earlier rounds' workspaces, which the scripts resolve relative to this directory
(`../../../iter_*/gen_art/*`), so run from inside the run's `3_invention_loop/iter_5/gen_art/<this dir>`.

```sh
uv venv .venv --python=3.12
uv pip install --python .venv/bin/python -r requirements.lock
uv run eval.py            # ~2 min, B = 2000 cluster-bootstrap draws, seed 20260924
uv run report.py
uv run figures.py
uv run rederive.py        # independent re-derivation + placebos
# optional, needs a working OpenRouter key and costs ~$2:
uv run label_gpt41.py --budget 8   # then re-run eval.py; the bought labels enter the gpt-4.1 rows automatically
```

`eval.py --mini` does a fast smoke run with 200 bootstrap draws. The only network access is a one-time download of
the Gemma tokenizer files (for the 100-token keyword view), which go into the shared HF cache if they are not already there.

Statistical conventions: rates and kappas use cluster bootstraps over semantic items (pairs for EN/SL contrasts;
prompts shared across arms for the held-out set). Paired contrasts add an exact McNemar test. The non-refusal guard
share uses an unpaired bootstrap because the non-refused sets differ by language. A κ from a constant rater is reported
with a `rater constant` flag, never as agreement.

## Restoring removed files

`.aii/manifest.yaml` marks two paths for deletion. Both can be regenerated:

| path | how to restore |
|---|---|
| `.venv/` | `uv venv .venv --python=3.12 && uv pip install --python .venv/bin/python -r requirements.lock` |
| `__pycache__/` | recreated automatically the first time `uv run eval.py` imports the module |

Everything else is small text (code, JSON, CSV, Markdown, figures under 1 MB). It stays at its current path on the run's
volume and is published with the repository.

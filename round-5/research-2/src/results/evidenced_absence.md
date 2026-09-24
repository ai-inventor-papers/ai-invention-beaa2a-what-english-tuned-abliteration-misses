# Evidenced-absence ledger

Every absence statement the paper may make, in the exact wording it must use. The wording is **"not found by
these queries"** followed by the row ids. Never "no prior work exists", never "first to", never an unqualified
"novel". Row ids 1-25 are the dependency's log (`results/_dep_search_log.md`); 26-49 are this artifact's
(`results/search_log_iter5.md`).

---

## A1. The matched-budget placement contrast

> At matched total removal energy **and** matched layer count, we did not find a prior report comparing where in
> depth a bounded refusal weight edit deposits that energy — not found by these queries (rows 21, 22, 39, 40, 41).

- **Closest found, and each one narrows the claim.** arXiv 2408.17003 (ICLR 2025) locates a small set of
  contiguous MIDDLE layers as safety-critical AND compares layer ranges by scaling their weights — but neither
  energy nor layer count is held fixed, the edit amplifies rather than removes, and it is English-only (P1, P2).
  arXiv 2607.02714 §3.2 compares SELECTION CRITERIA (norm-ranked vs uniformly spread) and finds spread wins by up
  to ~70pp (P3). arXiv 2608.11583 transplants mid-network blocks and reports non-additive composition.
  arXiv 2609.22144 reports language-specific safety-sensitive layers. arXiv 2601.19375 selects steering layers by
  a discriminative criterion (P5).
- **What would falsify the absence.** Any study that moves a fixed number of edited layers to a different depth at
  a fixed total edit magnitude and reports the behavioural difference. If a reviewer supplies one, this result
  becomes a replication in a new language pair and must be rewritten as such.

## A2. The dose-versus-placement exchange rate

> We did not find a prior report that increasing the strength of a badly placed refusal edit fails to substitute
> for moving it — not found by these queries (rows 37, 38, 39, 43).

- **Closest found.** arXiv 2609.06473 builds an iso-effect (matched behavioural effect) dose-response framework
  for activation steering under quantisation, including a collapse-floor pitfall this run's A1-A4 ladder hit (P4);
  arXiv 2604.15557 and 2601.19375 predict or select good steering layers but never race dose against placement.
- **What would falsify it.** A dose ladder at a fixed bad placement, compared with a lower dose at a good one.
- **This run's own number.** 1.5x and 2x the energy of the badly placed edit leave SL 0.93 / 0.92 and EN 0.88 /
  0.88, against SL 0.27 / EN 0.07 for the well-placed edit at 1x
  (`iter_4/gen_art/gen_art_experiment_13/results/report_tables.md`, "Dose rival (G3)").

## A3. The depth-negative's conjunction (carried from the dependency, not re-searched in full)

> An activation-space depth measurement failing to predict WEIGHT-edit outcomes across languages, raced against
> and losing to two one-forward-pass behavioural baselines on the same held-out items — not found by these
> queries (rows 2, 4, 8, 11, 13, 18, 20, 21, and confirmed-neighbourhood rows 42, 43).

- **Coverage caveat (OBSERVATION).** Rows 2-21 were run by the dependency on 2026-09-24 as well, so the coverage
  is same-dated; rows 42 and 43 are this artifact's re-checks and returned the same neighbourhood (Hase 2023,
  2606.00926, 2609.04721, 2608.24988) rather than a closer match.
- **What would falsify it.** Any paper comparing a representation-derived predictor of weight-edit transfer
  against the target model's own pre-edit behaviour rate on the same items.

## A4. The edited-condition inversion of a substring refusal counter

> A refusal proxy that is near-exact on unedited checkpoints and inverts on the edited ones, measured **within**
> the edited condition and in a second language, with the same counter used as the optimiser's objective — not
> found by these queries (rows 26, 27, 28, 31, 44, 46).

- **Closest found, and this is the biggest narrowing in the artifact.** arXiv 2510.02768 §4.2 already reports, for
  20 original-and-abliterated systems, that "regex tends to overestimate refusals by flagging templated
  disclaimers in otherwise harmless answers" (M3); arXiv 2512.13655 §3 already states the false-positive caveat
  for marker matching in an explicitly Heretic-including comparison (M4); StrongREJECT already owns the
  evaluation-time version (M1); a community tool documents a 3/100-vs-60/100 reproduction failure (M20).
- **What survives, and must be written this narrowly.** The magnitude and direction measured on this run's own
  checkpoints (keyword .851 vs judged .255 on the shipped Gemma EN edit, false-positive share .761, kappa -.04,
  `iter_2/gen_art/gen_art_experiment_4/README.md` §4 and `.../results/analysis.json`), the within-edited
  agreement on held-out harm categories (keyword kappa 0.02 EN / 0.00 SL against a distilled classifier at
  0.48 / 0.73, `iter_4/gen_art/gen_art_experiment_15/results/analysis.json`, `heldout_source_sanity`), and the
  fact that this same counter was the optimiser's objective.
- **What would falsify the absence.** Any paper reporting a refusal proxy's agreement separately for unedited and
  edited conditions, in more than one language.

## A5. A language-dependent guard-versus-judge divergence on the same edited checkpoint

> Guard-pipeline and judge verdicts diverging in a language-dependent direction on the outputs of one edited
> checkpoint — not found by these queries (rows 32, 33, 47).

- **Closest found.** arXiv 2505.19056 App. A reports an LLM judge and Llama-Guard-3-8B side by side for
  abliterated checkpoints and finds them "in strong agreement, with differences of at most 4 percentage points"
  (M10) — English only, and agreeing rather than diverging. arXiv 2606.01196 separates representation from action
  cross-lingually on unedited models (M15). arXiv 2603.06594 establishes that judges degrade under exactly this
  kind of distribution shift (M9).
- **This run's own number.** On the shipped Gemma edit, official-guard ASR is .738 EN vs .103 SL
  (`iter_2/gen_art/gen_art_experiment_4/results/headline_table.csv`), and Slovene non-refusals are guard-safe more
  often than English ones by +0.232 [0.124, 0.348]
  (`iter_4/gen_art/gen_art_evaluation_2/results/asr_summary.json`).
- **What would falsify it.** Any paper reporting guard and judge rates per language on one edited checkpoint.

## A6. Within-condition agreement reporting in safety evaluation

> We did not find prior use of WITHIN-EDITED-condition agreement (rather than pooled agreement) as the reporting
> unit for a refusal scorer — not found by these queries (rows 34, 35, 42, 45).

- **What the searches did return.** The prevalence-dependence of kappa is textbook statistics (row 35 returned the
  methodological literature, not a safety application); arXiv 2603.06594 makes the closest argument in kind by
  showing that judges validated on static held-out sets degrade under red-teaming shift (M9); arXiv 2510.02768
  validates judges on a 10-prompt human subset but pools conditions (M3).
- **Honest statement for the paper.** The MOVE is not new in statistics and the underlying problem is published
  in safety evaluation; what this run adds is the measured inflation on its own data (0.133,
  `iter_3/gen_art/gen_art_evaluation_1/results/novelty_table.md`) and the practice of gating on it.

---

## Standing rules for the paper (INTERPRETATION)

1. Every absence sentence carries "not found by these queries" plus its row ids from this ledger.
2. No absence claim is upgraded to primacy anywhere, including the abstract.
3. Where a neighbour narrows a claim (A1 via 2408.17003; A4 via 2510.02768 and 2512.13655; A5 via 2505.19056;
   A6 via 2603.06594), the narrowing is stated in the same paragraph as the claim, not in a later limitations
   section.

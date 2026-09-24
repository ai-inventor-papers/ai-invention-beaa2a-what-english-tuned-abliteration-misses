# What this artifact CHANGES in the dependency, rather than carrying

Three changes were required by the plan; two more were required by what the sources said. All five are in
`results/positioning_diff.md` with their verbatim before/after text, and both v2 files are rebuilt from the
dependency's text by `scripts/make_v2.py`, which fails if an anchor is not unique.

| # | what the dependency says | what v2 says | why | evidence |
|---|---|---|---|---|
| (i) | qualifier-table row "the effective region DIFFERS between two sibling checkpoints of the same architecture" marked **kept** | struck through, marked **DROPPED (falsified by this run's own evidence)** | the DEV-named band LOST at matched energy at both levels, the sibling's profile predicts the anchor's cells no worse than its own, and the two production kernels are indistinguishable at matched dose | `iter_4/gen_art/gen_art_experiment_14/results/report_tables.md` Tables 4, 6, 6b, 7 |
| (ii) | the abstract delta sentence, "differently per language and differently between two sibling checkpoints" | rewritten: matched-energy AND matched-layer-count ordering, in both languages, two siblings and an outside family, plus the failed dose rival; a separate paragraph states the language fact correctly (shared band, different residual) | the language-label placebo does NOT collapse (English profile predicts the Slovene residual at rho -0.94), so the BAND is not language-specific; the RESIDUAL is | `iter_4/gen_art/gen_art_experiment_13/results/analysis.json` (`language_swapped_O_spearman` -0.941), `.../report_tables.md` |
| (iii) | the bolded "What this work adds" sentence in the paste-ready paragraph, asserting the same two qualifiers | rewritten to the kept delta plus the mandatory stopping sentence | same as (i) and (ii) | same as (i) and (ii) |
| (iv) | the positive paragraph has no safety-layer-localisation neighbour | a sentence on arXiv 2408.17003 (ICLR 2025) and its weight-scaling range comparison is inserted, with the boundary stated | this is the closest published statement to the run's positive and the first thing a reviewer would name; the plan's rule 3 requires the narrowing to be stated where the claim is made | `results/neighbour_table_positive_additions.md` P1, P2 |
| (v) | the negative's companion paragraph cites StrongREJECT, XSTest and AdvPrefix | adds three narrowing neighbours (2510.02768 regex over-counts on abliterated models; 2512.13655 states the marker caveat; 2603.06594 judges degrade under red-teaming shift), re-aims AdvPrefix at the companion, and states the FALSIFIED primary prediction beside the structural finding | the abliteration-specific version of this run's measurement point is already published, and the frozen prediction was falsified | `results/neighbour_table_measurement.md` M3, M4, M8, M9; `iter_4/gen_art/gen_art_experiment_15/results/analysis.json` |

## What is carried unchanged

- All 30 neighbour rows N1-N30 (`results/carried_forward.md`).
- `results/stopping_points.md`, copied byte-for-byte.
- The `results/depth_attribution_provenance.md` §1 provenance text, carried verbatim with the 2607.02714 passage
  re-verified this session.
- The evidenced-absence WORDING ("not found by these queries" plus row ids) and the dependency's absence rows
  2, 4, 8, 11, 13, 18, 20, 21, cited by id rather than re-run.

# Qualifier table v2 (extracted from results/positioning_positive_v2.md)

Each qualifier in the delta, checked against the neighbour set. The struck row is shown STRUCK, not deleted,
so a reader can see what this round retracted. Two rows are new this round (the failed dose rival and the
outside-family replication) and both survive as kept; one row is dropped; the load-bearing row is narrowed.

## Delta, stated in one sentence, with each qualifier checked against the neighbours

| qualifier in the delta | already covered by a neighbour? | kept? |
|---|---|---|
| selection of intervention sites by measured causal effect rather than probe quality | YES — 2609.22135 (activation steering, omni-modal, emotion), 2606.00926 (text LMs, activation space), Hase 2023 (weight edits, factual knowledge) | **dropped as a novelty claim**; cited as the line this work joins |
| depth-localised vs. distributed refusal | YES — 2607.02714, 2608.01414, 2608.11583, LessWrong per-layer study | **dropped as a novelty claim** |
| layer sensitivity differs per language | YES — 2609.22144 (18 languages, fine-tuning-data filtering); N23 supplies a language-aware layer-selection rule for language control | **narrowed**: the paper states this as prior work and claims only its edit-placement consequence |
| a failed DOSE rival at matched placement: 1.5x and 2x the energy of the badly placed edit do not reach what the well-placed edit reaches at 1x (SL 0.93 / 0.92 vs 0.27; EN 0.88 / 0.88 vs 0.07; `round-4/experiment-13/src/results/report_tables.md`, 'Dose rival (G3)') | no neighbour found by these queries (rows 37, 38, 39, 43); closest is an iso-effect dose-response study under quantisation, not placement (arXiv 2609.06473) | **kept** |
| an outside-family replication (Qwen3-8B; EN, SL, DE) | no neighbour found by these queries (rows 39, 40); the multi-model abliteration studies compare tools or selection criteria, not matched-budget placement (arXiv 2512.13655, 2607.02714) | **kept** (`round-4/experiment-13/src/results/report_tables.md`, 'Outside family') |
| the contrast is at MATCHED total edit size AND MATCHED layer count | no neighbour found running this construction — not found by these queries (rows 21, 22, 39, 40, 41) — but NARROWED this round: arXiv 2408.17003 (ICLR 2025) already compares layer RANGES by scaling their weights and already localises a contiguous mid-depth safety band, without matching energy or layer count, without a removal edit, and English-only | **kept, narrowed** — it remains the load-bearing qualifier, but the claim is now only the matched-budget contrast, not the depth localisation |
| ~~the effective region DIFFERS between two sibling checkpoints of the same architecture~~ | no neighbour found (search log row 24) — but the qualifier is no longer available | **DROPPED (falsified by this run's own evidence)**: the DEV-named band LOST at matched energy at both levels, the sibling's profile predicts the anchor's cells no worse than its own, and the two production kernels are indistinguishable at matched dose (`round-4/experiment-14/src/results/report_tables.md`, Tables 4, 6, 6b, 7) |
| the outcome is a persistent WEIGHT edit, judged on generations with an explicit PARTIAL and INVALID class | no neighbour found combining these | **kept** |

**Delta sentence for the abstract (v2):** at matched total removal energy and matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives — in both languages, in two sibling checkpoints and in an outside family, and not recoverable by doubling the dose of a badly placed edit — a matched-budget placement contrast that the all-layer default of the single-direction literature, the safety-layer localisation line (arXiv 2408.17003) and the selection-criterion comparison of the abliteration literature (arXiv 2607.02714) each leave untested.

**Language, stated correctly (v2):** the BAND is shared, the RESIDUAL is not. The English causal write profile predicts the Slovene residual at rho -0.94, so the language-label placebo does not collapse (`round-4/experiment-13/src/results/analysis.json`, `language_swapped_O_spearman` = -0.941); what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3, `round-4/experiment-13/src/results/report_tables.md`).

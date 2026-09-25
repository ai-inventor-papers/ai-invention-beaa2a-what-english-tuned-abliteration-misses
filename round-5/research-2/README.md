# Fixing the paper's citations and claims

`demo/` — Self-contained demo (Colab-ready notebook or markdown). Run without setup.  
`src/` — Full source code, data, and outputs from the experiment execution.

**Type:** research  
**ID:** `art_DDBLxbIlbjhv`

## Layman Summary

Checks this AI-safety study's claims and references against the original papers, removing two claims its own experiments had already disproved and correcting five citations.

## Full Summary

Iteration-5 positioning artifact (web research only; no GPU, no model loading, no API calls, $0.00 OpenRouter spend; accessed 2026-09-24). WHAT IT SETTLES. (1) THREE QUALIFIERS STRUCK. 'The effective region differs between the two sibling checkpoints' is DROPPED - falsified by this run's own placebos (DEV-named band NAMED_AND_LOST at matched energy at both levels, 0.50 vs 0.59 and 0.30 vs 0.53; the sibling's profile predicts the anchor's 50 cells at rho -0.442, no worse than its own -0.278/-0.111; the two production kernels indistinguishable at matched dose, -0.029 [-0.129,+0.071] p 0.774 and 0.000 [-0.086,+0.086] p 1.000; iter_4/gen_art/gen_art_experiment_14). 'The band differs per language' is DROPPED - the language-label placebo does not collapse (English profile predicts the Slovene residual at rho -0.94, iter_4/gen_art/gen_art_experiment_13); the RESIDUAL still differs (strict 0.07 EN vs 0.27 SL). 'Selection blindness explains the divergent searches' is UNAVAILABLE - the frozen prediction was falsified (+0.006 [0.000,0.019]; judge-referenced the sign reverses to -0.029 [-0.060,-0.005], iter_4/gen_art/gen_art_experiment_15). (2) THE KEPT DELTA, NARROWED: at matched total removal energy AND matched layer count, where in depth the edit deposits its energy orders how much refusal survives, in both languages, two siblings and an outside family, and doubling the dose of a badly placed edit does not substitute. arXiv 2408.17003 (ICLR 2025) narrows it sharply - it already localises contiguous MIDDLE safety layers and already compares layer RANGES by scaling their weights; what survives is the energy- and count-matched removal contrast in two languages. arXiv 2607.02714's ~70pp uniform-spread result is a SELECTION-CRITERION comparison, so it does not conflict; the paste-ready reconciliation sentence is supplied. (3) THE MEASUREMENT COMPANION FINALLY HAS NEIGHBOURS (21 rows), and three shrink it: arXiv 2510.02768 already reports regex over-counting refusals via disclaimers ON ABLITERATED MODELS, arXiv 2512.13655 states the marker false-positive caveat for a Heretic-including comparison, and arXiv 2603.06594 audits judge degradation under red-teaming shift. AdvPrefix is RE-AIMED from the depth result to this companion. arXiv 2605.17173 CONTRADICTS the strong multilingual-judge reading (per-language validated judge reaches kappa 0.80-0.83; 22 of 61 configurations more vulnerable in English). (4) CONSUMERS QUOTED, CLAIM SOFTENED: 2608.22490 instantiates its unaligned counterfactual with abliterated checkpoints (incl. gemma-3-27b-it) and measures a helpfulness win rate, but it DOES check a capability-side confound (Alignment Gap Difference on P-MMEval) and re-derives the cost from matched from-scratch checkpoints - so this run's evidence bears on a channel it does not cover (residual refusal per language), not on its correctness. RefusEU's guard pair is named (Llama-Guard-3-8B + PolyGuard-Qwen). (5) BIBLIOGRAPHY: [19] = Safety Layers, ICLR 2025, arXiv 2408.17003 (draft says ICLR 2024, no id; v1 title reads 'OF' not 'IN'); [20] = 2609.04721; [21] = 2606.00926; the pruning-calibration reference is MIS-CITED (published title 'On the Limitations of Language-targeted Pruning', TACL vol. 14 pp. 167-192, DOI 10.1162/tacl.a.599; it finds target-language calibration does NOT consistently improve downstream performance); AdvPrefix is mis-placed. BibTeX-ready entries supplied. (6) THE '2-3 MIDDLE LAYERS' PROVENANCE is carried verbatim: the sentence exists in 2607.02714 SS3.2 as that paper's attribution to Arditi et al., the attribution was not found in Arditi et al. by those queries, and 2607.02714 rejects it next sentence; the NOT VERIFIED flag attaches to the ATTRIBUTION only. (7) SIX EVIDENCED ABSENCES (A1-A6) in the required wording 'not found by these queries' + row ids, each with its falsifier; 22 new search rows logged (26-47). ALSO REPORTED: two of this artifact's own plan assumptions were wrong on full-text inspection (2609.10594 does not measure string matching; 2607.02235 does not contain the ~80%/<60% figures attributed to it), and 2505.19056's paired judge/guard numbers show AGREEMENT within 4pp, not divergence. VERIFICATION: scripts/self_check.py re-checks all 36 rows (34 VERIFIED-QUOTE, 2 CARRIED, max 39 words) - passes; scripts/path_lint.py: 33 cited paths, all resolve; scripts/make_v2.py rebuilds both paragraphs from the dependency text. Deliverables in results/: positioning_positive_v2.md, positioning_negative_v2.md, positioning_diff.md, qualifier_table_v2.md, neighbour_table_measurement.md/.json, neighbour_table_positive_additions.md/.json, consumers.md/.json, bibliography_repairs.md/.csv, depth_attribution_provenance.md, evidenced_absence.md, search_log_iter5.md, carried_forward.md, dependency_deltas.md, claims_to_position_v2.csv (42 rows, no blanks), reconciliation_map_v2.csv, failed_and_unexecuted_v2.md, path_lint.md, stopping_points.md, raw/.

## Dependencies

- `art_sZ5w0yoY9o6L` — extends

## Output Files

- `research_out.json`
- `reproducibility.md`

## Demo Files

- **research_report.md** — Research report markdown (auto-generated from artifact)

---
*Generated by AI Inventor Pipeline*

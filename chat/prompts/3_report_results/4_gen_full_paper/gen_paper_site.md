# gen_paper_site — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_paper_site` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-25 06:47:42 UTC

````
ishes these two models under this instrument. Any iteration-1 difference between their Heretic edits (GaMS3 transferred, Gemma did not) must be explained by something other than how redundantly refusal is written across depth.

  [Correction, iter 4: English judge agreement within edited GaMS3 arms is 0.54, so English refusal rates in the edited cells are one end of a range rather than point estimates. The co-primary "usable" index does not resolve in either language. Two further pre-registered predictions (the operator-versus-depth finding) are unreported here; see the artifact for the full results.]



  ### Experiment 11: Corrected objective \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-11}}

  **Goal.** Test whether replacing Heretic's English keyword refusal counter with a partial-aware score, at equal budget/seed/data/quantisation, makes the search select a kernel that closes the Slovene-English gap.

  **Setup.** A refusal classifier was distilled from existing gpt-4.1 and Qwen3-14B labels (thousands on disk from experiments 4, 5, and 8), using char/word TF-IDF and hand-crafted features on the first 100 tokens of each response. It was certified at kappa 0.858 [0.820, 0.888] (refused-vs-not, within edited checkpoints, 20 held-out replayed trials) against the Qwen3-14B judge. [Correction, iter 4: The previous draft quoted kappa 0.924, which is the in-loop value over 116 draws, not the certified within-edited-cells value. It also described the classifier as using "first-64-token embeddings"; the actual features are char/word TF-IDF + hand features on the first 100 tokens (corrected_numbers_iter4.json, claim E11.classifier_certification_kappa).] The corrected Heretic run used the same seed (20260923), same 116-trial budget, same NF4 precision, and the same selection rule (lowest KL among trials with ≤ 10 refusals); only the refusal scorer changed.

  **Selection outcomes.** Under the corrected scorer, the primary selection rule fired (not the fallback), selecting trial 7 with 5/100 refusals at KL 0.258. Under the keyword scorer on the same 116 trials, the fallback rule fired, selecting trial 96 with 69/100 keyword-refusals at KL 0.024. The keyword counter fails because it sees 72/100 keyword-refusals on trial 107 (which the judge rates at 63/100 actual refusals [Correction, iter 5: was 10/100; recomputed from iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv]) and cannot select it. [Correction, iter 5: Trial 96 had 37 REFUSED + 49 PARTIAL; the previous '15/100' was arm B's S5X English refusal rate, a different item set.]

  Post-hoc reselection (rescoring the original 116 trials with the corrected scorer and re-applying the selection rule) selected trial 98 (classifier) or trial 64 (judge), both with ≤ 10 refusals.

  **Coverage.** The corrected trial 7 has sum_A1 (aligned coverage) = 64.0, versus trial 96's 26.0. The corrected objective bought broader coverage, as predicted by the depth-placement hypothesis.

  **Headline results (S5X, 100 verified translation pairs; source: results/s5x_headline.json):**

  | Arm | EN refusal | SL refusal | SL-EN gap [95% CI] |
  |---|---|---|---|
  | A orig | 0.950 | 0.990 | +0.04 [+0.01, +0.08] |
  | B keyword t96 | 0.150 | 0.830 | +0.68 [+0.59, +0.77] |
  | C corrected t7 | 0.030 | 0.410 | +0.38 [+0.29, +0.47] |
  | D reselected clf t98 | 0.050 | 0.350 | +0.30 [+0.21, +0.40] |
  | D2 reselected judge t64 | 0.040 | 0.450 | +0.41 [+0.32, +0.51] |
  | F dose 1.5 | 0.030 | 0.360 | +0.33 [+0.24, +0.42] |
  | F dose 2.0 | 0.000 | 0.000 | +0.00 [+0.00, +0.00] |
  | F dose 3.0 | 0.000 | 0.000 | +0.00 [+0.00, +0.00] |

  **Frozen predictions.** Holm-adjusted p-values over the confirmatory family: P1 adjusted 0.411, P2 adjusted 1.0, P3 adjusted 0.0.
  - P1 (EN refusal ≤ 0.054): PASS at point estimate (0.03); CI upper bound 0.085 does not exclude 0.054. Holm p = 0.411.
  - P2 (S5X gap CI upper < 0.35): FAIL. Gap 0.38, CI [0.29, 0.47]. Holm p = 1.0.
  - P3 (FLORES dNLL ≤ +0.10): PASS. dNLL +0.003. Holm p = 0.0.
  - P4' (output validity replacement): SUPPORTED. Invalid EN 0.0, language-consistent EN 1.0, over-refusal EN 0.017 < original 0.133.
  - P5 (reselection ratio ≥ 0.5): PASS. Ratio 1.27.
  - P6 (corrected A1 > trial 96's): PASS. A1 64.0 > 26.0.
  - **P7 falsifier (dose ladder closes gap as well):** FIRED. At equal EN refusal, dose-scaling trial 96 to c=1.5 gives a gap of +0.33 [0.24, 0.42], comparable to the corrected edit's +0.38. The value is -0.05 (corrected minus dose at equal EN), which does not reach the 0.15 threshold. This means the gap reduction may be attributable to "more total edit" rather than "better objective."

  [Correction, iter 4: The interpretation below replaces the previous version, which described the corrected objective as buying "broader coverage, as predicted by the depth-placement hypothesis." The artifact's own verdict (README section 4) is that dose, not objective quality, drives the gap reduction at this operating point. The miscalibration finding, not the corrected checkpoint, is experiment 11's primary result.]

  The corrected objective halved the gap (from +0.68 to +0.38) but did not reach the +0.35 target. The P7 falsifier fired: dose-scaling the keyword edit to the same English refusal level achieved comparable gap reduction (+0.33 [0.24, 0.42] vs the corrected edit's +0.38 [0.29, 0.47]). At matched divergence the dose-scaled arm is strictly better: lower gap at lower KL (0.073 vs 0.258). The dose-2.0 arm closes the gap entirely (0.00 [0.00, 0.00]) at KL cost below the corrected edit's. The corrected objective selected a trial that happened to apply more total edit energy, and the gap reduction followed from the energy, not from the objective's partial-awareness.

  The primary finding from experiment 11 is the miscalibration of Heretic's keyword refusal counter. Across all 11,600 in-loop generations, the keyword counter systematically overcounted refusal on edited outputs: on trial 96 (keyword-selected) the keyword count was 69/100 while the judge rated it at 15/100. The keyword counter never entered the low-refusal region (floor = 72 keyword refusals across all candidates) where candidates differ from each other by judged standards (source: results/miscalibration_table.csv).



  ### Experiment 12: Predictive test across models and languages \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-12}}

  **Goal.** Test whether the depth-redundancy index, measured on development data, predicts out of sample how much of an English-derived weight edit transfers to each unmonitored language across multiple model families.

  **Setup.** Three models: google/gemma-3-12b-it (anchor), Qwen/Qwen3-8B (qwen3), mistralai/Mistral-7B-Instruct-v0.3 (mistral). Four languages: English, Slovene, German, Lithuanian. Per-layer d_EN(h) directions extracted by diff-in-means on DEV items. DEV index measured at cumulative prefixes (10%, 25%, 50%, 75%, 100% of depth). Eligibility gate: no-op refusal ≥ 0.60 AND INVALID ≤ 0.20.

  **DEV indices (source: results/dev_indices.json):**

  | Model | EN | SL | DE | LT |
  |---|---|---|---|---|
  | gemma | 0.5 | 0.75 | 0.5 | 0.75 |
  | qwen3 | 0.75 | 0.75 | 0.75 | 0.5 |
  | mistral | 0.1 | 0.25 | 0.1 | 0.1 |

  Mistral failed the eligibility gate in all languages (no-op refusal 0.07 to 0.53); all four mistral rows and qwen3-LT were excluded. Seven eligible rows remained. [Correction, iter 4: the previous draft stated "Eight eligible rows"; the correct count from analysis.json is 7 (12 model×language rows minus 4 mistral minus qwen3-LT = 7; 7 rows × 3 weight cells = 21 P1 rows).]

  **Weight panel (5 cells per model × language, held-out StrongREJECT items).** The Gemma trial-96 adapter applied to gemma showed residual refusal EN 0.60, DE 0.53, LT 0.75, SL 0.92 (exposure to the Slovene residual that motivated the study). For qwen3, the W3 (high-dose) arm brought EN to 0.37 and SL to 0.32, with the gap much smaller than Gemma's.

  **Frozen predictions: VERDICT FALSIFY.**
  - **P1** Spearman(index, residual) = -0.009 [-0.131, 0.192] over 21 rows. The index does not predict the cross-model, cross-language residual. Pass = False.
  - **P2** concordance 8/12 decided (0.67); binomial p = 0.19. Pass = False.
  - **P4** index vs baselines: single-site transfer rho +0.732 beats the index by -0.741. The simple single-site ablation rate predicts better than the frozen index.

  The depth-redundancy index, as defined and measured here, does not generalise beyond the two Gemma-3 siblings. It is a two-checkpoint observation, not a predictive instrument. [Correction, iter 4: the judge for this experiment misses its own agreement gate (kappa 0.683, below the 0.75 threshold), and the bias-corrected re-run drops a secondary test to chance. The familiar geometric predictor also fails, and two cheap baselines beat both the index and the geometric predictor by margins whose CIs exclude zero. The analysis script was patched after the freeze, which the artifact notes.]

  [FIGURE:fig_cross_model]



  ### Evaluation 1: Audit and judge-sensitivity table \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/evaluation-1}}

  **Goal.** Discharge the reviewer's blocking audit: recompute every draft number from saved files, build the judge-sensitivity table, compile the dead-end ledger, and position against the nearest published work.

  **Audit headline.** 167 draft numbers checked: 137 match, 8 mismatch, 12 misdescribed, 6 untraceable (mismatch rate 5.5%). Two sign-reversed conclusions were found: the iteration-1 swap (see corrections above) and experiment 7 P-a direction (see corrections above). 19 of 99 behavioural claims are judge-sensitive. Placebos passed: 6/6.

  **Judge-sensitivity table (headline gap as a range).** The EN-SL gap for the Gemma edit on S5X depends on judge and definition:

  | Judge | Definition | Gap | CI |
  |---|---|---|---|
  | Qwen3-14B | strict (REFUSED only) | +0.69 | [0.60, 0.78] |
  | Qwen3-14B | broad (REFUSED + PARTIAL) | +0.23 | [0.14, 0.32] |
  | keyword | strict | +0.06 | [-0.02, 0.14] |

  The strict gap ranges from +0.06 (keyword) to +0.69 (Qwen3-14B). The broad gap collapses to +0.23 because 0.548 of the Gemma edit's English outputs are PARTIAL. On GaMS3, all judges agree the gap is near zero (range -0.05 to +0.02).

  **Dead-end ledger.** Sixteen items, each with its closing number: [Correction, iter 4: the previous draft stated "Twenty items"; the table lists 16 rows (corrected_numbers_iter4.json, claim EV1.dead_end_ledger_count).]

  | Item | Status | Closing number |
  |---|---|---|
  | iter-1 experiment 2, experiment 4 | NOT RUN | empty pods |
  | P2 Sobol sensitivity bands | NOT RUN | cut for time |
  | English-only-vs-full forecast | NOT RUN | 50% coverage |
  | language-orthogonalised matched-efficacy arm | NOT RUN | cut for time |
  | Gemini second judge | NOT RUN | OpenRouter 403 |
  | exposure differential D | CLOSED | dR2 ≈ 0 |
  | static geometry b1/b2/b3, LSAR Omega | CLOSED | CV R2 ≤ 0 |
  | r_prior false-refusal direction | CLOSED | cut 0.036 < best random 0.074 |
  | thin-margin rival | CLOSED | margin-matched gap +0.057 |
  | language-identity direction (A4) | WORKS BUT UNUSABLE | FLORES dNLL +2.0 |
  | B3 batching certification | FAILED | non-identical |
  | gpt-4.1 primary judge coverage | PARTIAL | 716/3,840 (exp4) |
  | P1 depth-coverage regression (exp9) | FAILED | dR2 = 0.040 < 0.05 |
  | P2 matched-energy broad-vs-narrow (exp9) | FAILED | pooled contrast +0.05, not significant |
  | PB2 matched-energy (exp10, GaMS3) | FALSIFIED OPPOSITE | -0.10 |
  | depth-redundancy index generalisation (exp12) | FALSIFIED | Spearman -0.009 |

  **Novelty positioning.** Wang et al. [2] established direction universality across 14 languages using all-layer activation ablation; Slovene and Gemma-3-12B were not among their models or languages. Arditi et al. [1] showed refusal is mediated by a single direction ablated at all components. Li et al. [19] identify which layers govern safety behaviour ("safety layers") and compare layer RANGES by scaling their weights, localising a contiguous mid-depth safety band; Bosco and Srinivasan [20] locate refusal beyond attention; Jiang [21] shows that probe accuracy and ablation response dissociate. [Correction, iter 5: positioning rewritten per R1 and research2 positioning_positive_v2.md. STRUCK 'the critical band moves between sibling checkpoints': the behavioural winner is the SAME band in both siblings; only the DEV profile's argmax differs (layer 27 vs 19).] This study adds: (a) the English direction does clear Slovene when applied at every depth (consistent with Wang et al. and Arditi et al.), but (b) the site-limited Heretic weight edit leaves a gap whose size is judge- and definition-dependent (strict +0.06 to +0.69), and (c) the gap is governed by WHERE the edit energy sits, not by how many layers are covered. What this adds beyond Li et al. [19] is the matched-budget construction: at matched total removal energy AND matched layer count, where in depth the edit energy sits orders how much refusal survives, and doubling the dose of a badly placed edit does not recover what the well-placed edit achieves at half the energy. The negative finding (that an activation-space depth measurement fails to predict weight-edit outcomes across languages while two one-forward-pass baselines succeed) positions against Jiang [21] and AdvPrefix [22]. [Correction, iter 5: AdvPrefix is the neighbour for the selection-blindness companion, not for the depth result; repositioned here per research2 bibliography_repairs.md.]

  **Pending human review.** Five packets totalling 640 items are ready for native-speaker labelling. No native-speaker review has been conducted anywhere in this study; all judges are automated.



  ## Iteration 4

  Iteration 4 was designed to close three remaining gaps from the reviewer's blocking feedback on iterations 1-3: (1) the placement finding rests on the exploratory band-density correlation (Spearman -0.942) without a causal mechanism tying edit energy to refusal at each layer; (2) the result is Gemma-only, with GaMS3 showing a different depth profile but no causal confirmation; and (3) Heretic's keyword blindness was demonstrated qualitatively but not quantified as a structural feature of the objective landscape. Iteration 4 ran three experiments, one comprehensive evaluation audit, and one positioning analysis.

  ### Experiment 13: Causal write profile and overlap instrument in Gemma \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-13}}

  **Goal.** Measure the causal write profile $e_L(h)$ for the anchor model (google/gemma-3-12b-it) and test whether the overlap between this profile and a multi-layer edit's energy distribution predicts refusal outcomes better than energy alone.

  **Causal write profile.** Single-layer edits at each of 48 layers, evaluated on S3 half-A development items (44 harmful per language), give the fraction of refusal removed per layer. The profile peaks at layer 19 (EN) and layer 16 (SL); the Spearman between EN and SL profiles is 0.588. Split-half reliability: EN 0.84, SL 0.51 (source: results/report_tables.md, DEV profile table). The SL profile is noisier, consistent with the smaller behavioural signal in Slovene on unedited Gemma.

  **Overlap instrument $O$.** For each existing multi-layer edit, $O = \sum_h e_L(h) \cdot g(h) / \|g\|_2$, where $g(h)$ is the per-layer edit energy. $O$ was raced against log-energy, layer count, one-forward-pass baselines ($O_\text{cos}$: cosine overlap; $O_\text{band4}$: energy fraction in the argmax 12-layer band), and controls (random direction, principal component).

  **Confirmation results (8 matched-energy groups, source: results/report_tables.md):**

  | Statistic | EN | SL |
  |---|---|---|
  | Spearman $\rho(O, \text{refusal})$ | -0.96 [-0.98, -0.84] | -0.83 [-0.84, -0.82] |
  | Pooled matched-group contrast (high-$O$ minus low-$O$) | -0.688 [-0.75, -0.62] | -0.377 [-0.45, -0.30] |
  | Controls (random, PC) | within ±0.03 of no-op | within ±0.03 of no-op |
  | Dose rival (2× late-layer energy, layers 33-48) | EN 0.88 | SL 0.92 |
  | Best placement contrast: layers 16-31 vs 33-48 | EN 0.07 vs 0.92 | SL 0.27 vs 0.92 |

  **Argmax band prediction:** Confirmed for both EN and SL: predicted band 13-24 observed as winner.

  **Nested $R^2$, per language (source: recomputed from iter_4/gen_art/gen_art_experiment_13/results/per_item.csv + cells/*.json):**

  [Correction, iter 5: replaced the single-column table (which was exp14 SL data mislabelled as exp13) with the correct per-language exp13 ladders. The exp14 SL ladders are moved to the exp14 section below.]

  | | EN | SL |
  |---|---|---|
  | log energy alone | 0.001 | 0.008 |
  | + layer count, + span, + EN/SL cosine (nuisance stack) | 0.879 | 0.734 |
  | + $O$ (full) | 0.907 | 0.790 |
  | **$\Delta R^2$ of $O$ over nuisance stack** | **0.027** | **0.056** |
  | $O$ alone | 0.873 | 0.754 |
  | EN/SL cosine alone | 0.827 | 0.630 |
  | $\Delta R^2$ of $O$ over logE + layer count ONLY | 0.892 | 0.770 |
  | Spearman($O$, cosine) | 0.808 | 0.764 |

  **PRIMARY CRITERION: FALSIFIED.** $O$ adds $\Delta R^2 = 0.027$ (EN) / 0.056 (SL) over a nuisance stack that CONTAINS the g-weighted EN/SL cosine. Both are under the 0.10 bar, and EN is under the 0.05 falsifier. Over log energy + layer count ALONE, $O$ adds 0.892 / 0.770. [Correction, iter 5: the failure reason is collinearity with the cosine ($\rho$ = 0.81/0.76), NOT that 'energy already explains the outcome': log energy alone explains 0.001 / 0.008.] MDE for $\Delta R^2$ at 80% power: 0.047 EN / 0.109 SL. The rank ordering is informative: knowing $O$ tells which of two matched-energy edits removes more refusal.

  **Cross-prediction:** EN outcome predicts SL at $\rho$ = 0.945, indistinguishable from $O$ itself. A language-specific instrument is not needed if a language-pooled one is available.

  **Replication in Qwen3-8B (outside family, 3 languages, source: results/report_tables.md):** Spearman $\rho(O)$: EN -0.76, SL -0.93, DE -0.84. Matched groups held in all three languages (9/9 favour high-$O$).

  **Judge certification (source: results/report_tables.md, judge table):** Within-edited pooled $\kappa$ = 0.818. EN $\kappa$ = 0.856 PASS; SL $\kappa$ = 0.744 FAIL. Slovene gap claims in this experiment are therefore judge-sensitive.

  [FIGURE:fig_write_profile]

  ### Experiment 14: Causal write profile and overlap in GaMS3 \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-14}}

  **Goal.** Repeat the causal write-profile measurement for the sibling model (cjvt/GaMS3-12B-Instruct) and test $O$'s prediction on the GaMS3 weight-edit panel.

  **Causal write profile.** The GaMS3 profile peaks at layer 27 (both EN and SL), in band 25-36 rather than the anchor's 13-24. Band mass distribution (source: results/report_tables.md):

  | Band | EN mass | SL mass |
  |---|---|---|
  | 1-12 | 0.00 | 0.02 |
  | 13-24 | 1.05 | 0.55 |
  | 25-36 | 1.50 | 0.57 |
  | 37-48 | 0.27 | 0.05 |

  Split-half reliability: EN 0.812, SL 0.312. The SL profile is declared UNRELIABLE (source: results/report_tables.md).

  **VERDICT: PARTIAL.** The overlap $O_\text{SL}$ predicts Slovene refusal at Spearman -0.900 [-0.928, -0.857] [Correction, iter 5: recomputed value -0.900; draft had -0.903], beating log-energy (-0.384), span (-0.039), and mean-depth (-0.328). The incremental $R^2$ of $O$ over log-energy is 0.580 (LOO: 0.594), passing the 0.10 threshold that the anchor failed. Within-level rho: E2 -0.976, E3 -0.948.

  **Nested $R^2$, each predictor added separately to log-energy (GaMS3, SL; source: recomputed from iter_4/gen_art/gen_art_experiment_14/results/per_item.parquet + cells.csv):**

  [Correction, iter 5: this table was previously printed under exp13; it is exp14 SL. The draft's cumulative rows were also wrong.]

  | Model | $R^2$ |
  |---|---|
  | logE | 0.090 |
  | logE + $O$ | 0.669 |
  | logE + $O_\text{cos}$ | 0.788 |
  | logE + $O_\text{band4}$ | 0.808 |
  | logE + $O$ + $O_\text{cos}$ (cumulative) | 0.805 |
  | logE + $O$ + $O_\text{cos}$ + $O_\text{band4}$ (cumulative) | 0.822 |

  **Argmax band prediction: FAILED (NAMED_AND_LOST).** The profile predicted band 25-36 as the winner, but band 13-24 (B2) achieved the lowest Slovene refusal (0.30 at E3 vs 0.53 for B3 at E3). There is a metric flip: the opener rule ranks 25-36 first while judged strict refusal ranks 13-24 first (source: results/report_tables.md).

  **THREE BOUNDARIES (source: results/report_tables.md):**
  1. $O_\text{band4}$ LOO $\Delta R^2$ = 0.845 and $O_\text{cos}$ = 0.834 both beat $O$'s 0.594, so the expensive single-layer instrument does not earn its cost over one-forward-pass baselines.
  2. The DEV argmax names the wrong band.
  3. The GaMS3 profile predicts the sibling (Gemma) at Spearman -0.442, no worse than its own -0.278 on Gemma, suggesting the profiles carry shared rather than model-specific information.

  **Placement vs dose dissociation (A1-A4 ladder, source: results/report_tables.md):** [Correction, iter 5: all four contrasts are Slovene strict; the panel has no English contrast. The previous 'EN -0.186 ... SL -0.157' was MISDESCRIBED.] At fixed placement, increasing dose reduces Slovene strict refusal: dose at fixed O_ship -0.186 [-0.286, -0.086]; dose at fixed O_swap -0.157 [-0.257, -0.071]. At fixed dose, swapping placement does not significantly change refusal: placement at fixed high E -0.029 [-0.129, +0.071], McNemar p 0.774; placement at fixed low E +0.000 [-0.086, +0.071], p 1.000. At the refusal floor where the shipped edits operate, dose is the active variable and the particular kernel does not matter, confirming experiment 11's finding.

  **Controls:** All six (three random, three PC) were null.

  **Judge certification:** EN $\kappa$ = 0.721 (MISS/JUDGE_SENSITIVE); SL $\kappa$ = 0.830 (PASS). English gap claims in GaMS3 are therefore judge-sensitive, the reverse of the Gemma pattern.

  [FIGURE:fig_gams3_profile]

  ### Experiment 15: Gradient-blind fraction of Heretic's selection objective \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-15}}

  **Goal.** Quantify the structural blindness of Heretic's keyword-based refusal rate as a selection objective, measuring the gradient-blind fraction (GBF): the share of optimizer candidate pairs where the objective moves less than measurement noise while judged refusal spans the full range.

  **Primary prediction: FALSIFIED.** The paired GBF difference (classifier-referenced minus judge-referenced) was +0.006 [0.000, 0.019], and the judge-referenced difference reversed at -0.029 (source: results/analysis.json).

  **Structural results (source: results/analysis.json):**

  | | Gemma (anchor) | GaMS3 (sibling) |
  |---|---|---|
  | Keyword range | [72, 100] | [16, 99] |
  | Classifier range | [5, 97] | [0, 98] |
  | Slope (keyword on classifier) | 0.308 | 0.738 |
  | Mean keyword minus classifier | +20.5 | +15.0 |
  | Keyword floor | 72 | 16 |
  | GBF (all candidates) | 0.051 | 0.002 |
  | GBF (low-C region, C ≤ 50) | 0.470 | 0.017 |
  | Threshold blindness fraction (TBF) | 1.0 | 1.0 |
  | Self-placebo | 0 | 0 |
  | Monotone? | Yes (GBF far below permutation chance) | Yes |

  Both models are monotone: the keyword objective preserves the rank order of the classifier within each model. The blindness is therefore not about mis-ranking candidates but about range compression. The keyword's dynamic range is compressed to [72, 100] in Gemma (28 pp), versus [16, 99] in GaMS3 (83 pp). In the low-refusal region where selection actually occurs (C ≤ 50), 47% of Gemma candidate pairs are gradient-blind.

  **SHARED STRUCTURAL FEATURE: Threshold blindness (TBF = 1.0 in both models).** In both searches, the keyword objective's floor sits above the selection rule's threshold (keyword floor 72 > threshold 10 in Gemma; keyword floor 16 > threshold 10 in GaMS3). The keyword counter never enters the region where the selection rule decides, though GaMS3's floor is close enough that its practical impact is small.

  **Reselection table (source: results/reselection_table.csv):**

  | Model | Scorer | Selected trial | Rule |
  |---|---|---|---|
  | Gemma | Keyword (K) | 107 | fallback |
  | Gemma | Classifier (C) | 98 | primary |
  | Gemma | Qwen3-14B workhorse (J) | 64 | primary |
  | GaMS3 | Keyword (K) | 88 | fallback |
  | GaMS3 | Classifier (C) | 85 | primary |
  | GaMS3 | Qwen3-14B workhorse (J) | 115 | primary |

  [Correction, iter 5: relabelled 'Judge (gpt-4.1)' as the Qwen3-14B workhorse (J); gpt-4.1 was only the 800-item certification subsample (kappa 0.850). Added GaMS3-J row.] Under the classifier or judge, the primary selection rule fires for Gemma (selecting a trial with ≤ 10 actual refusals); under keywords it falls to the fallback rule. For GaMS3, classifier selection reaches the primary rule. [Correction, iter 5: replaced 'close': trial 88 has KL 0.175 and trial 85 (classifier-selected) has KL 0.015, an order of magnitude apart.]

  **Judge gate:** gpt-4.1 subsample $\kappa$ = 0.850 [0.772, 0.911], n = 800, cost $0.86. Classifier on GaMS3 without refit: $\kappa$ = 0.841 (source: results/analysis.json).

  [FIGURE:fig_gbf]

  ### Evaluation 2: Comprehensive audit, judge calibration, and partial-compliance curves \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/evaluation-2}}

  **Goal.** Audit all prior claims with independent recomputation, certify the judge against gpt-4.1 at scale, measure the PARTIAL transition as a function of edit dose, quantify the NF4 vs bf16 confound, and flag judge-sensitive claims.

  **Judge calibration (source: results/judge_calibration.json).** n = 900 items (515 bought + 385 free-tier). Overall weighted $\kappa$ = 0.873. Keyword $\kappa$ = 0.074. Classifier $\kappa$ = 0.919. EN gate MET ($\kappa$ weighted 0.871, unweighted 0.858). SL gate NOT MET ($\kappa$ weighted 0.871, unweighted 0.723). The SL judge certification failure means all Slovene gap claims remain judge-sensitive. 40 of 211 gap claims are JUDGE_SENSITIVE; 105 are DEFINITION_SENSITIVE.

  **Flip analysis (source: results/flip_analysis.json):** The flip analysis measures how the judge's refusal readout changes after editing, decomposed into slope change (evidence loss) and intercept change (criterion shift).

  | Model | Language | Slope ratio [CI] | Intercept | Refit AUROC | Class |
  |---|---|---|---|---|---|
  | Gemma | EN | 0.50 [0.24, 0.86] | -6.65 | ≥ 0.995 | MIXED |
  | Gemma | SL | 0.34 [0.19, 0.54] | -5.32 | ≥ 0.995 | MIXED |
  | GaMS3 | EN | NOT_ESTIMABLE | — | — | too few refusals after edit |
  | GaMS3 | SL | NOT_ESTIMABLE | — | — | too few refusals after edit |

  For Gemma in both languages, the edit produces both criterion shift and partial coupling loss, but the information for distinguishing harmful from harmless prompts remains present (refit AUROC ≥ 0.995).

  **C3: PARTIAL transition curves (source: results/curve_fits.json).** PARTIAL-class responses are single-peaked in edit dose, but the peak positions do not differ between languages ($\Delta_\text{peak}$ nonparametric: L1 +0.45 [-0.45, 0.90], p = 0.571). C3 status: FALSIFIED. The PARTIAL share does not predict the residual EN-SL gap: C3-iii Spearman -0.427 (permutation p = 0.339, MAE not better than null).

  **Nonrefused decomposition (source: results/asr_summary.json).** Among nonrefused Gemma edit EN responses, 7.2% [3.3, 11.8] were guard-safe (passing both content filters), and 32.7% were PARTIAL among nonrefused. Among nonrefused Gemma edit SL responses, fewer were generated (the model refused more often). ASR gap vs refusal gap: Spearman -0.836 [-0.928, -0.674], Pearson -0.909 (n = 46 cells). Cells with larger residual refusal gaps also show lower attack success rates, confirming the gap reflects genuine refusal.

  **Independent recompute (source: results/corrected_numbers_iter4.json).** 102 numbers checked: 97 match, 3 misdescribed, 2 mismatch. Mismatch rate 4.9% [2.1, 11.0]. All placebos collapse: cell-label shuffle +0.001, language-label shuffle +0.001, dose shuffle -0.002, judge-label permutation $\kappa$ +0.005.

  Mismatches found:
  - E12.eligible_rows: draft stated 8, actual 7.
  - EV1.dead_end_ledger_count: draft stated 20, actual 16.
  Misdescribed:
  - E9.sets_missing_13_24: S4 was listed as fully missing but has 25% coverage.
  - E11.classifier_certification_kappa: draft quoted 0.924 (in-loop), certified value 0.858.
  - EV1.pending_packets: not all five are native-review packets.

  **NF4 vs bf16 confound (source: results/quant_confound.json).** VERDICT: bounded but NOT closed at panel scale (one checkpoint, 20 verified pairs per language). Weight relative Frobenius error 0.093. Energy profile cosine bf16 vs NF4: 0.999998. [Correction, iter 5: replaced the attenuation estimate with the interval the probe supports.] Paired SL-EN strict gap bf16 +0.60 [+0.40, +0.80] vs NF4 +0.45 [+0.20, +0.70], n = 20 S5X pairs, one checkpoint, gpt-4.1 labels. The difference is not resolved. The asymmetry is at least as large in bf16, so it is not an NF4 artefact.

  | Language | Refused bf16 | Refused NF4 | Diff [CI] | Label agreement |
  |---|---|---|---|---|
  | EN (n=20) | 0.25 | 0.25 | 0.00 [-0.20, 0.20] | 0.65 |
  | SL (n=20) | 0.85 | 0.70 | 0.15 [0.00, 0.30] | 0.80 |

  **Pending human review (source: results/pending_human_review_iter4.md).** Five files totalling 640 items remain pending: three native-review packets (570 rows covering translation fidelity, refusal/partial/compliance labels, and utility labels) and two executor-labelled checks (70 rows). No native-speaker or human review has been conducted anywhere in the run. Every judged rate in the report is proxy-certified (gpt-4.1 as frontier proxy), not human-certified.

  ### Research 1: Novelty positioning \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/research-1}}

  **Goal.** Establish what the surviving positive and negative results add relative to published work.

  **Positioning of the positive (source: results/positioning_positive.md).** The surviving positive finding is a matched-total-energy AND matched-layer-count placement contrast, per language, with the effective region differing between siblings. Effect-based site selection and language-specific depths have been published separately: Li et al. [19] study which layers govern safety behaviour; Bosco and Srinivasan [20] locate refusal beyond attention. What this study adds is the conjunction: the edit's depth band, not its energy or span, determines how much refusal survives, and the critical band shifts between checkpoints from the same architecture family. The Qwen3-8B replication across three languages extends this beyond the Gemma-3 family.

  **Positioning of the negative (source: results/positioning_negative.md).** The negative finding, that an activation-space depth measurement (the causal write profile) fails to predict weight-edit outcomes across languages while two one-forward-pass baselines ($O_\text{cos}$ and $O_\text{band4}$) succeed, positions against Jiang [21] (single-direction ablation is not a necessity test) and against AdvPrefix (arXiv 2412.10321) [22] (selection blindness). Four partial neighbours were found; their conjunction (activation-measurement failure plus baseline success on the same data) is "not found by these queries." This negative is more transferable than the surviving positive because it speaks to the limits of a general method (causal profiling) rather than to a specific model pair.

  **Attribution note.** An earlier draft attributed a claim about "2-3 middle layers" to arXiv 2607.02714; the research artifact confirmed this text exists in that paper but is rejected in the next sentence, so the attribution is dropped.


  ### Iteration-4 assessment

  **The overlap instrument orders but does not explain.** The write-mass overlap $O$ orders refusal outcomes at Spearman -0.96 (EN) and -0.83 (SL) in the anchor, and -0.90 (SL) in the sibling, but its incremental $R^2$ over the cosine-containing nuisance stack is only 0.027 (EN) / 0.056 (SL) in the anchor (below the 0.10 threshold, FALSIFIED; the failure reason is collinearity with the cosine, not that energy explains the outcome: log energy alone explains 0.001) while reaching 0.580 in GaMS3 (where the confirmation cells dissociated energy from placement). Two one-forward-pass baselines ($O_\text{cos}$, $O_\text{band4}$) beat the expensive single-layer instrument in GaMS3, questioning whether the causal profile earns its cost. [Correction, iter 5: STRUCK 'the effective depth zone is model-specific'. The DEV profile argmax differs (layer 19 vs 27) but the behavioural winner (band 13-24) is the SAME in both siblings.] The argmax band prediction fails in GaMS3 (NAMED_AND_LOST), meaning the profile's peak does not reliably predict the single best band.

  **Dose, not placement, at the refusal floor.** At the operating point of the shipped edits, swapping kernels between checkpoints at matched energy has no effect ($p > 0.77$), while increasing energy at fixed placement reliably reduces refusal ($p < 0.003$). This confirms experiment 11's finding: the gap reduction from the "corrected" objective is attributable to more edit energy, not better site selection.

  **The selection objective is structurally blind.** Heretic's keyword floor is 72 in Gemma (threshold blindness TBF = 1.0), compressing the objective's range to 28 pp and making 47% of low-refusal candidate pairs gradient-blind (equal to the permutation chance level 0.46: inside the low region the objective's ordering carries no information). In GaMS3 the floor is 16, giving 83 pp of range and near-zero GBF. [Correction, iter 5: STRUCK 'this explains the divergent search outcomes'. The frozen prediction that one search is blinder overall was FALSIFIED (+0.006 [0.000, 0.019], CI includes zero; judge-referenced the sign reverses to -0.029). Threshold blindness is SHARED (TBF = 1.0 in both searches). The blindness is real but does not explain the dissociation.] The structural form of the blindness, the keyword floor sitting above the rule's own threshold in both searches, is the reportable finding.


  ## Iteration 5

  **Strategy.** Iteration 5 was designed to close three final gaps: (1) the placement and negative results lacked positioning against the nearest published work, so several novelty qualifiers rested on unchecked absence claims; (2) the keyword objective's cross-lingual measurement bias had been demonstrated qualitatively but never decomposed into its language components on verified translation pairs; and (3) nine citation paths did not resolve, and three bibliography entries had wrong venue years or missing arXiv IDs. Iteration 5 ran no new experiments; it ran three independent recompute/audit passes and one positioning analysis, each addressing a specific reviewer objection.

  ### Evaluation 3: Terminal audit \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-3}}

  **Goal.** Independent recompute of all headline numbers from per-item files; classify every source as real-run, substitute-scorer, or stand-in; lint all citation paths; build the evidence-status ledger.

  **Audit headline.** 121 claims checked, 14 discrepancies (11.6%). 897 assertions classified: 557 OBSERVATION, 285 INTERPRETATION, 45 FAILED_HYPOTHESIS, 10 UNEXECUTED_PROPOSAL. 18 observations without a backing file or registry link. 9 of 35 in-text file citations do not resolve in the cited artifact's workspace (corrected paths supplied in results/path_lint.csv).

  **Source provenance.** No source is a STAND_IN (placeholder or fabricated generations). The judge substitutions (Qwen3-14B for gpt-4.1) are real runs on a substituted SCORER. Where that scorer failed its certification gate (Gemma SL in exp13: kappa 0.744; GaMS3 EN in exp14: kappa 0.721), the numbers are headline-ineligible and are marked JUDGE_SENSITIVE.

  **Judge-definition sensitivity, within-edited.** Pooled kappa overstates within-edited agreement. In exp4 EN, pooled kappa = 0.89 (n=359) vs within-edited 0.42 (n=180), inflation +0.47. SL: pooled 0.93 vs within-edited 0.87. The draft's 'kappa 0.83 / 0.91' for exp4 is a pooled figure and should be printed beside the within-edited EN value. In exp11, within-edited EN kappa = 0.226 [0.110, 0.370] (n=65 pairs).

  **Scope.** 94 executed cells, 5 named-but-not-executed cells (none claimed as results). Full table: results/scope_table.csv.

  **Deviations.** The gpt-4.1 reference for all 1,120 S4hoc items could not be bought (HTTP 403, $0.00 spent). No native-speaker review exists. The ledger classes are rule-based, not human-read.

  ### Evaluation 4: Report repairs and independent recompute \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-4}}

  **Goal.** Apply the twelve reviewer-directed repairs (R1-R12) as in-place corrections, independently recompute 136 first-pass numbers, compile the definitive F1-F14 failure ledger and U1-U10 unexecuted proposal ledger, and lint all citation paths.

  **Audit headline.** 136 first-pass numbers recomputed; 21 defective (15.4%, Wilson 95% CI [10.3%, 22.5%]), of which 14 are material. Comparable priors: eval1 15.6% (all-class), eval2 4.9%. No number was SIGN_REVERSED. 8 of 8 placebos collapsed. Recompute module: rederive_iter5.py (stdlib + numpy + pyarrow).

  **Citation lint.** 41 file references checked: 27 resolve as written, 14 resolve after a rewrite, 0 do not resolve (gate PASS). All 10 planted positive controls detected. Rewrites supplied in results/path_lint.csv.

  *The numbers in sections not independently re-derived in this pass carry this opening note: 'The numbers in this section were not re-derived by an independent path in iteration 5. The run's earlier passes measured 15.6% of numbers defective in iterations 1-2 and 4.9% in iteration 3. This pass measured 15.4% [10.3%, 22.5%] on previously unaudited sections.'*

  **Ledger F1-F14: evidenced FAILED hypotheses.**

  | # | Hypothesis | What killed it |
  |---|---|---|
  | F1 | Depth coverage explains residual SL refusal over energy | dR² = 0.040 but LOO dR² = -0.002; powered rejection |
  | F2 | Broad-and-weak beats narrow-and-strong | FALSIFIED OPPOSITE: narrow -0.10 [-0.150, -0.060] |
  | F3 | Count-based depth index predicts cross-model residual | Spearman -0.009 [-0.131, 0.192] |
  | F4 | EN/SL direction cosine carries transfer | Spearman +0.010 |
  | F5 | Corrected objective produces a better edit | P7 fired: dose at +0.33 vs corrected +0.38 |
  | F6 | Exposure differential carries the surrogacy gap | dR²(D|S0) ≈ 0 for every trait |
  | F7 | r_prior direction carries Slovene residual | Cut 0.036 < best random 0.074 |
  | F8 | Thin-margin account explains the gap | Margin-matched gap remains: +0.057 |
  | F9 | Static geometric predictors forecast the gap | CV R² ≤ 0 for all |
  | F10 | Language-identity direction is a usable lever | Works but unusable: FLORES dNLL +2.0 |
  | F11 | Depth index EN/SL difference is informative | 4-layer gap inside permutation null [-4, +4] |
  | F12 | Energy-matched random ablations are adequate controls | Controls are destructive; refusal drop is collateral |
  | F13 | Conformal forecasting is usable | 85% coverage in only 50% of cells |
  | F14 | Batched and single generation are interchangeable | B3 certification FAILED |
  | F15 | Effective depth region differs between siblings | DEV band 25-36 LOST at matched energy; placement -0.029, p 0.774 |
  | F16 | Effective region differs by language | Language-label placebo does not collapse: rho -0.94 |
  | F17 | Anchor search is blinder than sibling's | +0.006 [0.000, 0.019]; judge-referenced reverses |

  **Ledger U1-U10: UNEXECUTED proposals.**

  | # | Proposal | Reason |
  |---|---|---|
  | U1 | Native-speaker review of all non-English material | No qualified reviewer available; PENDING |
  | U2 | Second independent LLM judge (Gemini) on iter-1 SL arm | Budget block: HTTP 403 |
  | U3 | Full gpt-4.1 primary-judge coverage in iters 2-3 | Budget block |
  | U4 | P2 Sobol sensitivity bands | Cut for time |
  | U5 | English-only-vs-full forecast arm | Cut after conformal coverage failure (F13) |
  | U6 | Language-orthogonalised matched-efficacy arm | Cut for time |
  | U7 | EuroLLM-9B-Instruct as M3 | Gated repository, HTTP 403 |
  | U8 | Racing placement against published cheap predictors | Identified only in positioning; not run |
  | U9 | Iter-1 experiment pods 2 and 4 | Empty workspaces; nothing measured |
  | U10 | Iteration-4 arms not reached | See per-pod deviations.json |

  ### Evaluation 5: Keyword blindness decomposition \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-5}}

  **Goal.** Decompose the keyword objective's blindness into its per-language components on verified translation pairs, measure held-out agreement per language, and quantify the cross-lingual measurement bias.

  **Keyword blindness inside the candidate pool.** In both Heretic searches, the keyword objective's minimum over its own 116 candidates sits above the frozen selection rule's threshold (≤10/100 refusals): floor 72 in Gemma and 16 in GaMS3. The primary branch could not fire; the rule fell back to 'fewest keyword refusals' in both searches. The certified classifier places 6 (Gemma) and 37 (GaMS3) candidates at or below the threshold; the keyword places none there, so the threshold-blind fraction is 1.00 in both searches. The objective compresses the reference's range: OLS slope 0.308 [0.276, 0.357] for Gemma and 0.738 [0.716, 0.761] for GaMS3 (classifier-referenced), with mean signed error +20.5 and +15.0 per 100 prompts.

  **Held-out agreement per language.** On held-out StrongREJECT categories (first 100 Gemma tokens, Qwen3-14B reference), the English keyword rule's agreement on edited English outputs is kappa 0.021 (n=490). It MISFIRES: it calls 0.341 of responses refusals where the reference sees 0.173, and 0.814 of its 'refusals' are false. On edited Slovene outputs kappa is 0.000 for a different reason: the rule is SILENT and fires on 0 of 490 responses, while the reference sees refusal in 0.439. An English marker list is not a weak instrument on Slovene text; it is a silent one.

  **Cross-lingual measurement bias (verified translation pairs).** On the 100 verified EN-SL pairs for the main Gemma edit, the keyword score's discrepancy from the workhorse judge is d_EN = +0.74 and d_SL = -0.82, so $\Delta_\text{lang}$ = -1.56 [-1.68, -1.44]. In Slovene all of the discrepancy is missed refusals (FN rate 0.82, FP rate 0.00). In English the rule over-reports (FP rate 0.78). The paired disagreement RATES happen to be equal (exact McNemar p = 1.00), but their DIRECTION differs (exact sign test p = 5.0e-29). The same silence appears where no edit is involved: on every original checkpoint $\Delta_\text{lang}$ is about -1.01. The English rule does not register Slovene refusals at all, so any cross-language refusal gap it reports is an artefact of the rule's language.

  **Judge sensitivity.** Slovene numbers from the workhorse judge are JUDGE_SENSITIVE: its Slovene certification gate was not met (kappa 0.723 < 0.80). Every Slovene row ships a Rogan-Gladen companion. The workhorse also misses its panel-specific within-edited gate in ENGLISH (exp4 kappa 0.42, exp11 0.23), so edited English rows are flagged too. Registry counts: JUDGE_ROBUST 6, JUDGE_SENSITIVE 72.

  **Guard channel.** The guard channel orders the languages the same way as judged refusal wherever both orderings are determined (0 of 26 cells disagree). Guard numbers are intervals (e.g. community_ref SL S5 ASR [0.714, 0.893] with 50 of 280 items unadjudicated). On the Gemma edit verified pairs, refusal is EN 0.13 vs SL 0.82 and ASR is EN [0.69, 0.86] vs SL [0.09, 0.23].

  **Official RefusEU guard ASR table (Llama-Guard-3-8B + PolyGuard agreement):**

  | Checkpoint | ASR EN | ASR SL | S5 refusal EN | S5 refusal SL |
  |---|---|---|---|---|
  | gams_orig | 0.015 | 0.012 | 0.986 | 0.871 |
  | gams_edit | 0.982 | 0.972 | 0.014 | 0.000 |
  | gemma_orig | 0.026 | 0.016 | 0.971 | 0.939 |
  | gemma_edit | 0.738 | 0.103 | 0.287 | 0.739 |
  | community_ref | 1.000 | 0.870 | 0.054 | 0.114 |

  **Downstream sensitivity.** Under the assumption that per-language safety cost is an aligned-minus-unaligned difference in refusal-rate units, an ablated counterfactual verified with an English keyword score would misstate the SL-minus-EN cost difference by between -1.68 and -0.11 refusal-rate units across the three ablated checkpoints and all reference channels. The two-language ordering of residual refusal inverts between the keyword view and the reference view. This is a sensitivity statement, not a re-estimate of any published number.

  **Audit.** eval.py and an independently written stdlib-only rederive.py agree on 573 of 573 shared statistics. Placebos passed: 5 of 5. 0 cited paths fail to resolve. Paid API spend: $0.00.

  ### Research 2: Positioning against nearest published work \footnote{Code: \url{https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/research-2}}

  **Goal.** Position the surviving positive and negative results against the nearest published work, check every novelty qualifier against the neighbour set, repair bibliography defects, and compile the evidenced-absence record.

  **Positioning of the positive result (v2).** The surviving positive finding is a matched-total-energy AND matched-layer-count placement contrast. What is new is narrower than previously claimed: the all-layer default of the single-direction literature [1], the safety-layer localisation line [19] (which already compares layer ranges by scaling weights and localises a contiguous mid-depth safety band, without matching energy or layer count), and the selection-criterion comparison of the abliteration literature [23] each leave the matched-budget construction untested.

  Qualifiers checked against neighbours:
  - Selection of sites by measured causal effect rather than probe quality: DROPPED as a novelty claim (covered by [26], [21], Hase et al. 2023).
  - Depth-localised vs distributed refusal: DROPPED as a novelty claim (covered by [23], [24]).
  - Layer sensitivity differs per language: NARROWED (covered by [25]; claim is only the edit-placement consequence).
  - Failed dose rival at matched placement: KEPT (no neighbour found).
  - Outside-family replication (Qwen3-8B): KEPT (no neighbour found).
  - Matched total edit size AND matched layer count: KEPT, NARROWED (load-bearing qualifier; [19] already compares ranges without matching energy or count).
  - ~~Effective region differs between sibling checkpoints~~: DROPPED (FALSIFIED by this run's own evidence: F15).

  **Positioning of the negative result (v2).** The instrument failed: a per-language depth index measured in activation space does not predict weight-edit outcomes across models and languages (Spearman -0.009). The familiar geometric predictor fails beside it (EN/SL direction cosine Spearman +0.010). Two one-forward-pass baselines beat both by margins whose CIs exclude zero: single-site causal transfer rate +0.732; unedited model's own refusal rate +0.661.

  Four partial neighbours were found: Hase et al. 2023 (factual knowledge, ROME/MEMIT), Jiang [21] (probe vs ablation dissociation), Bosco and Srinivasan [20] (cross-architecture cosine unreliability), and arXiv 2608.24988 (weight edit survives while behaviour reverts). The conjunction, activation-space depth measurement failing to predict WEIGHT-edit outcomes ACROSS LANGUAGES while losing to two one-forward-pass baselines, was not found by the logged queries.

  **Selection-blindness companion, positioned.** AdvPrefix [22] owns the general point that a misspecified objective inside an optimiser produces low loss without intended behaviour. StrongREJECT and XSTest established the evaluation-time version. Three further neighbours narrow the companion: [27] (regex over-counts on abliterated models), [14] (marker false-positive caveat), [28] (judge degradation under red-teaming shift). What remains is the STRUCTURAL form: threshold blindness (TBF = 1.0 in both searches), the calibration difference between searches (slope 0.31 vs 0.74), and the within-edited agreement collapse on held-out harm categories (kappa 0.02 EN, 0.00 SL). The primary prediction that Gemma's search is blinder was FALSIFIED (F17).

  **Bibliography repairs.** [19] venue year corrected (ICLR 2025, not 2024); arXiv IDs added for [20] and [21]. The pruning-calibration citation (Kurz et al. [30]) is a LIMITATIONS paper ('does not consistently improve downstream task performance'), not support for 'the calibration language matters'; any sentence citing it for that claim is corrected. AdvPrefix [22] repositioned from the depth result to the selection-blindness companion.

  **Unexecuted proposals from iteration 5 (U-i1 to U-i4).** Four proposals were identified by the positioning analysis but not run: (U-i1) a concentration-vs-location triplet that would make this run's placement result commensurable with the selection-criterion comparison of [23]; (U-i2) re-running both searches with a partial-aware scorer certified per language before the search starts; (U-i3) repeating the guard-vs-judge divergence on a third language to test whether it is Slovene-specific or non-English-general; (U-i4) native-speaker review of any Slovene material, still PENDING for all five prepared packets.


  ## What we have learned so far

  [FIGURE:fig_refusal_gap]

  Five iterations have converged on a picture with one firm positive, one transferable negative, a structural measurement finding, and seventeen falsified predictions.

  **Firm positive: matched-budget placement orders residual refusal.** At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The BAND is shared; the RESIDUAL is not. The English causal write profile predicts the Slovene residual at rho -0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). In GaMS3, the SL strict ordering B2 < B3 < B4 < B1 is the SAME at both energy levels (E2 and E3). Two one-forward-pass baselines ($O_\text{cos}$ and $O_\text{band4}$) match or beat the expensive single-layer causal instrument. No band recommendation is made: the specific layer indices are properties of these checkpoints at this depth budget.

  **Transferable negative: the activation-space depth index fails to predict weight-edit outcomes.** Spearman -0.009 over 21 rows, permutation p = 0.16. The EN/SL direction cosine fails beside it (Spearman +0.010). Two baselines beat both: single-site causal transfer rate +0.732 and unedited model's own refusal rate +0.661. The practitioner recommendation: before spending a search budget on geometry, measure the unedited model's refusal rate in the target language and the effect of ablating at a single site; if a proposed statistic cannot beat those two, it should not be used to choose where to edit.

  **Structural measurement finding: the keyword objective is cross-lingually biased.** On verified translation pairs, $\Delta_\text{lang}$ = -1.56 [-1.68, -1.44]: the English keyword rule over-reports in English (FP rate 0.78) and is silent in Slovene (FN rate 0.82). Threshold blindness is 1.0 in both searches. An English marker list is not a weak instrument on Slovene text; it is a silent one. The pre-registered prediction that one search is blinder overall was FALSIFIED.

  **Seventeen hypotheses falsified across five iterations** (F1-F17): depth coverage explains residual (F1), broad-and-weak beats narrow-and-strong (F2), count-based depth index predicts cross-model residual (F3), EN/SL direction cosine carries transfer (F4), corrected objective produces a better edit (F5), exposure differential carries the surrogacy gap (F6), r_prior direction carries Slovene residual (F7), thin-margin account explains the gap (F8), static geometric predictors forecast the gap (F9), language-identity direction is a usable lever (F10), depth index EN/SL difference is informative (F11), energy-matched random ablations are adequate controls (F12), conformal forecasting is usable (F13), batched and single generation are interchangeable (F14), effective depth region differs between siblings (F15), effective region differs by language (F16), and anchor search is blinder than sibling's (F17). Additional experiment-specific falsified predictions not in the formal ledger include: PARTIAL share predicts gap (eval2 C3), $O$ incremental $R^2$ in anchor below threshold (exp13), $O$ argmax prediction in GaMS3 (exp14), keyword validity on edited checkpoints (exp4), and language swap equivalence at the refusal floor (exp14).

  **What survives from iterations 1-2.** The behavioural dissociation (GaMS3 transferred, Gemma did not) holds for the specific shipped edits but is not robust to dose scaling. The harm representation is shared across languages (AUROC > 0.995); the behavioural gap is an action failure, consistent with Aziz et al. [6]. KL divergence has a blind surrogacy gap in both models. Utility is preserved in all cells. The keyword proxy inverts on edited checkpoints.

  **The headline gap stated as a range.** The Gemma edit S5X paired EN-SL gap ranges from +0.06 (keyword strict) to +0.69 (Qwen3-14B strict), with the broad definition at +0.23. On GaMS3, all judges agree the gap is near zero. The PARTIAL class (0.548 of Gemma edit EN outputs) is the wedge.

  **Scope and limits.** Two sibling checkpoints of one architecture plus one outside family; one non-English language in the matched panels (two further languages only in the outside-family arm); one or two optimiser seeds; NF4 throughout with a single bf16 control cell (paired SL-EN gap bf16 +0.60 [+0.40, +0.80] vs NF4 +0.45 [+0.20, +0.70], not resolved but the asymmetry is at least as large in bf16); Slovene material machine-translated with native review PENDING. Two checkpoints are two units, not a population: nothing is attributed to Slovene continual pretraining, instruction tuning, or any safety-training stage. Five packets totalling 640 items remain pending for native-speaker labelling. Every judged rate in the report is proxy-certified, not human-certified. 136 numbers independently re-derived in this iteration; defect rate 15.4% [10.3%, 22.5%] on previously unaudited sections.


  ## References

  [1] Arditi, A., Obeso, O., Syed, A., Paleka, D., Panickssery, N., Gurnee, W., and Nanda, N. (2024). Refusal in Language Models Is Mediated by a Single Direction. arXiv:2406.11717.

  [2] Wang, X., Wang, M., Liu, Y., Schutze, H., and Plank, B. (2025). Refusal Direction is Universal Across Safety-Aligned Languages. arXiv:2505.17306.

  [3] Krasnodebska, A., Kusa, W., and Lipani, A. (2026). Multilingual Refusal Alignment for Safer Large Language Models. ACL 2026 Findings. arXiv:2606.07535.

  [4] Stein, E. V., Meier, D., Ruas, T., Wahle, J. P., and Gipp, B. (2026). BabelSteering: Multilingual Safety Alignment via English Steering Vectors. arXiv:2608.16577.

  [5] Yoon, C., Park, J., and Ritter, A. (2026). Who Pays More for Safety? Measuring the Disparate Cost of Safety Alignment across Languages. EMNLP 2026. arXiv:2608.22490.

  [6] Aziz, R., Hanif, I. A., and Koto, F. (2026). Low-Resource Safety Failures Are Action Failures, Not Representation Failures. arXiv:2606.01196.

  [7] Wu, J., Xie, Y., Lin, S., Zhao, S., and Chen, X. (2026). Knowing without Acting: The Disentangled Geometry of Safety Mechanisms in Large Language Models. arXiv:2603.05773.

  [8] Fafula, A. (2026). Abliteration Is Not a Scalpel: Off-Target Effects of Refusal Removal on Decision Disposition Across Model Families. arXiv:2607.17427.

  [9] Upadhyaya, A. and Sikdar, S. (2026). When Safety Speaks a Language: A Mechanistic Analysis of Safety-Language Identity Entanglement in LLMs. arXiv:2608.29936.

  [10] Hawkins, W. et al. (2026). The Heterogeneous Safety Impacts of Benign Multilingual Fine-Tuning. arXiv:2606.28843.

  [11] Labunets, A. (2026). Refusal geometry reflects refusal training: diverse refusal prefixes can raise stable rank and weaken refusal vector ablation attacks. arXiv:2608.25390.

  [12] Marchisio, K. et al. (2024). How Does Quantization Affect Multilingual LLMs? EMNLP 2024. arXiv:2407.03211.

  [13] Chimoto, E., Elhoushi, M., and Bassett, B. (2026). Calibrating Beyond English: Language Diversity for Better Quantized Multilingual LLM. EACL 2026. arXiv:2601.18306.

  [14] Young, R. (2025). Comparative Analysis of LLM Abliteration Methods: A Cross-Architecture Evaluation. arXiv:2512.13655.

  [15] Petrov, V. (2026). On the Failure of Topic-Matched Contrast Baselines in Multi-Directional Refusal Abliteration. arXiv:2603.22061.

  [16] Tang, T. et al. (2024). Language-Specific Neurons: The Key to Multilingual Capabilities in Large Language Models. ACL 2024. arXiv:2402.16438.

  [17] Ghussin, Y. et al. (2026). Multilingual Steering by Design: Multilingual Sparse Autoencoders and Principled Layer Selection. TrustNLP 2026. arXiv:2605.23036.

  [18] Frank, G. N. (2026). Detection Is Cheap, Routing Is Learned: Why Refusal-Based Alignment Evaluation Fails. arXiv:2603.18280.

  [19] Li, S., Yao, L., Zhang, L., and Li, Y. (2025). Safety Layers in Aligned Large Language Models: The Key to LLM Security. ICLR 2025. arXiv:2408.17003. [Correction, iter 5: venue year corrected from 2024 to 2025; arXiv ID added.]

  [20] Bosco, P. C. and Srinivasan, G. (2026). Locating and Steering Refusal Beyond Attention. arXiv:2609.04721. [Correction, iter 5: arXiv ID added.]

  [21] Jiang, Y. (2026). Refit the Probe: Single-Direction Ablation Is Not a Necessity Test. arXiv:2606.00926. [Correction, iter 5: arXiv ID added.]

  [22] Zhu, S., Amos, B., Tian, Y., Guo, C., and Evtimov, I. (2025). AdvPrefix: An Objective for Nuanced LLM Jailbreaks. arXiv:2412.10321.

  [23] Hadetskyi, O. (2026). Abliteration Unleashed: Evaluating and Enhancing Refusal Suppression Across Models. arXiv:2607.02714.

  [24] Zong, Y. et al. (2026). Localizing Safety-Critical Layers in LLMs by Transplanting Refusal Behaviour. arXiv:2608.11583.

  [25] Li, W. et al. (2026). Safety-Sensitive Layers Are Not Monolingual: Multi-Language Safety Analysis of Multilingual LLMs. arXiv:2609.22144.

  [26] Wang, Z. et al. (2026). Probe-Best Is Not Steer-Best: Finding the Causal Sweet Spot for Activation Steering. arXiv:2609.22135.

  [27] Agnihotri, S., Khandelwal, A., and Bansal, M. (2025). Abliteration Has Limits: How Models Refuse After Weight Surgery. NeurIPS 2025 Workshop Lock-LLM. arXiv:2510.02768.

  [28] Schwinn, L. et al. (2026). How Reliable Are LLM-as-a-Judge in Red-Teaming Evaluation? arXiv:2603.06594.

  [29] Zhang, Y. et al. (2026). Multilingual Safety Judge for LLMs. COLM 2026. arXiv:2605.17173.

  [30] Kurz, S., Chen, J.-J., Flek, L., and Zhao, Z. (2026). On the Limitations of Language-targeted Pruning: Investigating the Calibration Language Impact in Multilingual LLM Pruning. TACL, vol. 14, pp. 167-192. arXiv:2408.14398.

summary: >-
  Iteration 5 applied three independent recompute/audit passes and one positioning analysis, running no new experiments. Evaluation
  3 (terminal audit) checked 121 claims with 14 discrepancies (11.6%) and classified 897 assertions. Evaluation 4 independently
  re-derived 136 numbers with a 15.4% defect rate, applied twelve reviewer-directed repairs (R1-R12) as in-place corrections,
  and compiled the definitive F1-F14 failure ledger and U1-U10 unexecuted proposal ledger. Evaluation 5 decomposed the keyword
  objective's cross-lingual measurement bias on verified translation pairs: Delta_lang = -1.56 [-1.68, -1.44], the English
  rule is silent on Slovene (kappa 0.000), and threshold blindness is 1.0 in both searches. Research 2 positioned the surviving
  positive and negative results against the nearest published work, narrowing several novelty qualifiers and adding three
  new falsified hypotheses (F15-F17: sibling band difference, language band difference, and anchor blinder prediction all
  falsified). The report now carries one firm positive (matched-budget placement orders residual refusal, with the band shared
  between siblings), one transferable negative (the activation-space depth index fails to predict weight-edit outcomes while
  cheap baselines succeed), a structural measurement finding (the keyword objective is cross-lingually biased), and seventeen
  falsified predictions across five iterations.
</paper_text>

<available_figures>
Each line gives the path the PAGE must use, then the figure's title and caption. It is the same
path the file has on disk here: the publish step copies the page and its figures into one folder,
so what works in this workspace is what works on the live site.

- figures/fig_1_v0.png [render from fig_1_v0.pdf first] — "Refusal Rates Before and After Abliteration" (caption: "Refusal rates on RefusEU S5 harmful prompts ($n=280$) for all five checkpoints in English and Slovene. Abliteration transfers almost completely to Slovene for GaMS3 (orange) but fails for Gemma (blue). The community reference checkpoint (grey) shows that deeper abliteration can partially overcome the language gap. Error bars show 95\% Clopper--Pearson confidence intervals. Note: 94--95\% of edited English outputs were truncated at the 256-token generation limit.")
- figures/fig_2_v0.png [render from fig_2_v0.pdf first] — "Keyword Measurement Bias" (caption: "Keyword counter vs.\ reference judge positive rates for the Gemma-edit checkpoint on 100 verified paired prompts. The keyword counter fires on 87\% of English responses but 0\% of Slovene responses; the reference judge finds 13\% English refusal and 82\% Slovene refusal. $\Delta_{\mathrm{lang}} = -1.56$ [$-1.68$, $-1.44$]. The keyword counter is structurally blind to Slovene refusals.")
- figures/fig_3_v0.png [render from fig_3_v0.pdf first] — "Depth Placement Profile for GaMS3" (caption: "Residual Slovene refusal rate as a function of depth placement for GaMS3-12B-Instruct. Each point is a single abliteration configuration; the x-axis is a depth-placement index (lower = shallower layers). Spearman $\rho = -0.90$ ($p < 10^{-7}$). Deeper placements produce lower residual Slovene refusal. The relationship holds within both energy levels (E2: $\rho = -0.97$; E3: $\rho = -0.95$).")
</available_figures>

<figure_requirements>
- Reference every figure as `figures/` plus its filename, exactly as listed above.
  The publish step copies the page and its figures into one folder together, so that relative
  path is what resolves on the live site; anything else breaks once published.
- A browser cannot draw a PDF in an image element. Data figures are delivered as vector PDF for
  LaTeX's benefit, so for each one check whether a PNG of the same name already sits in
  `figures/`; if it does not, render one there at about 200 DPI with pdftoppm or
  pymupdf before referencing it. Renderable formats: .avif, .gif, .jpeg, .jpg, .png, .svg, .webp.
- Write those PNG files into `figures/` and nowhere else — that folder is published, a
  new folder of your own is not.
- Use each figure's own caption. Do not invent new ones, and do not describe a figure you did not
  place on the page.
- Look at every figure before you place it. A figure whose axis labels are unreadable at the size
  you give it is worse than no figure.
</figure_requirements>

<page_structure>
In this order, top to bottom:

1. HERO — the paper's title, the author line as the paper gives it, and a one-paragraph TL;DR in
   plain language: what was asked, what was found, and the single number that carries the finding.
   Not the abstract, and not a rewrite of it. Below it, every link the links section below
   lists, each at the exact URL given there.
2. CONTRIBUTIONS — the paper's actual contributions as three to five scannable cards, each a short
   heading plus one or two sentences. If the paper claims four things, show four cards, not five.
3. METHOD — a walkthrough a technically literate non-specialist can follow: what goes in, what
   happens to it, what comes out, and why the design is the way it is. Lead with the paper's own
   method figure when it has one.
4. RESULTS — the paper's real headline numbers, read out of `paper.tex` and the data
   files behind it, each next to what it was measured on and what it is being compared against.
   A number that is not in the paper does not go on the page, and neither does a comparison the
   paper did not make. If a slot has no number, drop the slot.
5. FIGURE GALLERY — every figure, each with its caption, click-to-enlarge into a lightbox that
   closes on Escape, on a click outside, and on a visible close control.
6. LIMITATIONS — what the paper says it does not show. Verbatim in substance; do not soften it.
7. FOOTER — every link from the links section again, and the citation if the paper carries one.

A sticky section navigation runs alongside all of it and marks where the reader currently is.
</page_structure>

<technical_requirements>
- ONE file. All CSS in a style element, all JavaScript in a script element, both inline in
  `index.html`. No build step, no bundler, no framework, no external script, stylesheet, web
  font or analytics — nothing fetched at load time. The page must render with the network off,
  and the only files it may point at are the figures listed above and the PDF beside it.
- System font stack only, since no font may be downloaded.
- Light theme. Responsive from a 360px phone to a wide desktop, with no horizontal page scroll;
  wide content scrolls inside its own container.
- Honour prefers-reduced-motion: under it, transitions and any scroll-driven effect stop.
- Keyboard-navigable: every control reachable by Tab in a sensible order, a visible focus ring,
  the lightbox trapping focus while open and returning it to the thumbnail on close, and a skip
  link to the main content.
- Semantic HTML: one top-level heading, headings that descend without skipping, landmark elements,
  and alt text on every image that says what the figure shows rather than repeating its number.
- No emoji anywhere. No purple-to-blue gradients. No decorative icon fonts.
- Keep the whole file comfortably under a megabyte.
</technical_requirements>

<writing_register>
Write in the register of the field's best papers (the paper this page presents, which was written to them), not in the register of a language
model. Four things are measured on the finished draft, and a draft outside them is sent back with
the numbers:
- Never use: delve, underscore, showcase, intricate, pivotal, realm, commendable, meticulous, tapestry, garner, multifaceted, it is worth noting, plays a crucial role, not only ... but also. These are 10 to 30 times more frequent in machine-written abstracts than in
  human ones, and reviewers read them as such.
- Em dashes: at most 3 per 1,000 words. Use a comma, a colon or a full stop.
- Sentence rhythm: mix short and long sentences. An interquartile range of sentence length under
  8 words reads as machine-written.
- Hedging: at most 15 hedges (may, likely, suggests, appears) per 1,000
  words. State what the evidence supports plainly; hedge where it is thin, not everywhere.
Style never changes substance: numbers, claims, citations and figure markers stay exactly as the
evidence gives them. The user's original request (delivered as a separate message) overrides all
of this wherever the two conflict.
</writing_register>

<links>
Use these URLs VERBATIM wherever the page links to the paper, the report or the code. Do not
shorten them, do not turn any of them into a relative path, and do not compose one of your own.

- The paper PDF, labelled "Read the paper (PDF)": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/paper.pdf
- The code repository, labelled "Code repository": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses
- The full research report — every experiment, every table and every dead end: https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/report.pdf
  Label this one "Read the full research report" and place it BESIDE the paper link, never in place of it.
- The executive summary, the short read of the run, labelled "Read the executive summary": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/exec_summary.pdf
  Place it right beside "Read the full research report".
- The report of each research round, as ONE compact line introduced by "Round reports:" under the document links, each round labelled as given:
  - "Round 1": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/round-1/report.pdf
  - "Round 2": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/round-2/report.pdf
  - "Round 3": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/round-3/report.pdf
  - "Round 4": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/round-4/report.pdf
  - "Round 5": https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@main/round-5/report.pdf

Each carries the branch this run publishes to. A link without it opens a DIFFERENT run's work —
it resolves and looks correct, which is why it must be copied rather than derived. They begin
resolving only after this run finishes publishing, so do NOT try to open or verify them.

The paper text carries a third kind of link, per claim rather than per paper: where it attaches a
\footnote{Code: \url{...}} to a sentence, that URL points at the exact code behind THAT claim.
Carry each one onto the page as an inline link on the corresponding sentence, using the URL
verbatim, the same way you use the ones above. Do not collapse them into the repository link.

Every artifact this run produced is published with its code. Link EACH of these, verbatim, from the part of the page that discusses that artifact, labelled as given or as the page's own name for it; one the page does not otherwise discuss goes in a short code list above the footer:
- "Code: Same edit, very different safety effect": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-1/experiment-1
- "Code: English vs Slovene refusal-direction transfer test": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-1/experiment-3
- "Code: Frozen English/Slovene safety and utility test sets": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-1/dataset-1
- "Code: Bilingual safety test of four model versions": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-2/experiment-4
- "Code: Utility cost and inner harm signal after abliteration": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-2/experiment-5
- "Code: What English edits miss in Slovene: GaMS3 panel": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-2/experiment-6
- "Code: English edits barely unlock Slovene refusal in Gemma": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-2/experiment-7
- "Code: Why an English safety edit misses Slovene": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-2/experiment-8
- "Code: How deep must an edit go to stop Slovene refusal": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-9
- "Code: Where to cut refusal in a bilingual model": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-10
- "Code: Heretic's refusal counter misjudges its own edits": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-11
- "Code: Depth index fails to predict cross-lingual refusal-edit failure": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/experiment-12
- "Code: Rechecking every number and every judge": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-3/evaluation-1
- "Code: Where a refusal edit lands decides what survives": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-13
- "Code: Where a refusal edit must land in a Slovene model": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-14
- "Code: Can a refusal optimiser see its own refusals?": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/experiment-15
- "Code: Partial answers, judges, and a full recount": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/evaluation-2
- "Code: Finding the closest prior work for two results": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-4/research-1
- "Code: Re-checking every number in the paper": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-3
- "Code: Recheck every number and every path": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-4
- "Code: How blind is an English-only refusal score": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/evaluation-5
- "Code: Fixing the paper's citations and claims": https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/main/round-5/research-2
</links>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-web-tools.
TODO 2. Read `paper.tex` end to end and list `figures/`. Write down the
paper's title, its author line, its contributions, and every headline number together with the
sentence it appears in — those sentences are the only numbers allowed on the page. Note which
figures are PDFs and so need a PNG rendered.
TODO 3. Render a PNG at about 200 DPI, into `figures/`, for every figure not already
in a browser-renderable format, then LOOK at each image you plan to use so you know what it shows
and how large it has to be on the page to stay legible.
TODO 4. Write `index.html` following the page_structure and technical_requirements sections
above: one file, inline CSS and JavaScript, every image referenced through the published figure
prefix.
TODO 5. VERIFY THE NUMBERS: for each number on the page, grep `paper.tex` for it and
confirm it appears there with the same meaning. Delete any number you cannot find. Then confirm
every claim on the page is one the paper actually makes.
TODO 6. VERIFY THE PAGE: confirm `index.html` has no external script, stylesheet or font
reference; that every image path starts with the published figure prefix and names a file that
exists in `figures/`; and that the PDF, repository and artifact code links are
character-for-character the URLs given in the links section — including the research report,
executive summary and round report links when they are listed there — and not `paper.pdf` nor any URL you composed. Then open the page in a browser, screenshot it at a phone width and a desktop width,
read both screenshots, and fix anything cramped, overlapping or cut off. `chromium-headless-shell`
is already installed: drive it with Playwright (`uv pip install playwright` in a scratch virtual
environment, then launch Chromium with `executable_path` set to the output of
`which chromium-headless-shell`, with no `playwright install`). Only if that command finds
nothing, run `playwright install --with-deps chromium` instead.
TODO 7. ACCESSIBILITY PASS: tab through the whole page and confirm every control is reachable with a
visible focus ring, the lightbox traps focus and closes on Escape, headings descend without
skipping, and every image has alt text. Fix what fails.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "PaperSiteExpectedFiles": {
      "description": "All expected output files from paper-site generation.",
      "properties": {
        "site_html_path": {
          "description": "Path to the single self-contained HTML page. Example: 'index.html'",
          "title": "Site Html Path",
          "type": "string"
        }
      },
      "required": [
        "site_html_path"
      ],
      "title": "PaperSiteExpectedFiles",
      "type": "object"
    }
  },
  "description": "Paper site \u2014 structured output from presentation-page generation.",
  "properties": {
    "summary": {
      "description": "Brief summary of the page you built: the sections it carries, which figures it shows, which numbers it quotes and where each came from in the paper.",
      "maxLength": 5000,
      "minLength": 300,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/PaperSiteExpectedFiles",
      "description": "All output files you created. Must include index.html."
    }
  },
  "required": [
    "summary",
    "out_expected_files"
  ],
  "title": "PaperSite",
  "type": "object"
}
```

IMPORTANT: this task is NOT complete until `./.terminal_claude_agent_struct_out.json` exists and contains JSON matching the schema above.

i want a reproducible bilingual study of refusal suppression in google/gemma-3-12b-it and cjvt/GaMS3-12B-Instruct, with room for a genuine scientific discovery. compare each original model with one Heretic-abliterated version, evaluating all four checkpoints in English and Slovene. establish the safety–utility trade-offs, then investigate what explains them internally.

the attached research plan defines the intended study and supplies literature leads. verify its factual claims and references. this prompt governs execution: keep the core comparison fixed, but choose the mechanistic methods and discovery direction yourself. do not assume the expected findings are true.

Gemma-IT is a same-family, same-size aligned reference, not the direct training parent of GaMS-Instruct. endpoint differences cannot establish what Slovene continual pretraining, instruction tuning, or the small safety-training set caused.

step 1 - explore and establish feasibility. load both original models, pin revisions, verify their official tokenizers and chat templates, and inspect behavior and activations on a small development set in both languages. check coherent output, baseline refusal, and hidden-state extraction. use text-only inputs and comparable precision and inference settings; record unavoidable differences. inspect where the models behave similarly and where they differ, without committing to a mechanism. estimate the compute needed before scaling up. use separate smoke-test data and keep final evaluation untouched. if an edit fails or destroys language ability, investigate and report the failure rather than quietly substituting another model or calling incoherence successful refusal suppression.

step 2 - find the scientific opening. develop 5–7 distinct, falsifiable explanations or research directions from the pilot and the literature. search beyond refusal-vector papers, including multilingual representations, decision calibration, causal intervention, and capability interference. actively try to disprove novelty by reading the closest primary sources. select one or two promising directions for deeper experiments.

possible starting points: does cross-language intervention transfer depend on something that direction cosine misses? can we distinguish loss of harmfulness information from a changed mapping between that information and refusal? does interference with language-relevant computation explain different utility costs? these are suggestions, not required findings or an exhaustive menu. replace them if the evidence points somewhere better.

for each selected hypothesis, state its prediction, strongest competing explanation, simplest baseline, and a result that would falsify it. discovering that familiar geometry fails to predict behavior can be valuable if you establish its boundary. merely applying Heretic to GaMS, observing EN–SL vector similarity, or finding separable harmfulness after refusal declines is insufficient by itself as a novelty claim. if an exploratory hypothesis fails the novelty check, replace that hypothesis while preserving the core study.

step 3 - freeze the data and intervention protocol. separate Heretic construction/optimization data, mechanistic development data, held-out mechanistic validation, and final behavioral evaluation. keep translations, paraphrases, and harmful/harmless counterparts from the same semantic source together when splitting. audit overlap by source and meaning, not only exact strings. Heretic's default sources and Semantic-Harmful/Semantic-Harmless may overlap; those pairs cannot automatically serve as independent validation.

create one main Heretic checkpoint per original model using the same pinned version, English prompt source, comparable objectives, and equal search budgets. choose checkpoints by a declared development-only rule balancing refusal reduction and harmless divergence. evaluate that same English-derived edit in both languages. a community Gemma edit is a sanity reference, not a substitute for the matched main intervention. record configurations, seeds, selected trials, precision, and checkpoint hashes. distinguish differences in achieved optimization from intrinsic model properties. additional seeds or edit strengths may support a focused robustness analysis, but keep them separate from the four core checkpoints.

step 4 - measure behavior and utility. use the official NASK-PIB/RefusEU evaluation data for English and Slovene, following its published scoring protocol where reproducible. report harmful compliance/attack success, refusal, and language consistency separately. refusal and harmful compliance are not complements: ambiguous, irrelevant, malformed, and empty outputs need explicit treatment. include a small independent benign safety-adjacent set to measure over-refusal. a model that refuses everything, or cannot answer coherently, must not look successful.

use the same frozen judge and rubric across conditions, with model identity hidden. check scoring sensitivity using a second independent judge on a stratified sample. prepare a blinded EN/SL sample for human review; if qualified human review is unavailable, mark it pending and state the limitation instead of claiming it happened.

for utility, use Slovenian LLM Eval and the corresponding English tasks: ARC-Challenge, BoolQ, HellaSwag, OpenBookQA, PIQA, and Winogrande. report individual tasks and their macro-average, emphasizing original-to-edited changes within each language. also measure harmless divergence on held-out inputs, wrong-language output, repetition, and output validity. Heretic's optimization KL alone is not independent evidence of preserved utility.

do not assume RefusEU examples sharing an ID are exact translations, or that EN and SL benchmark difficulty is identical. verify correspondence before making paired cross-language claims. use a separate faithful EN/SL contrast set for controlled language comparisons. translate only missing material, preserve semantic IDs, document translation checks, and distinguish automated checks from native-speaker review. published model-card scores are context and sanity checks; measure the four checkpoints yourself under the same protocol.

step 5 - connect representations to behavior. complete the mechanistic core: layer-wise bilingual harmful/harmless direction characterization in both originals, and held-out harmfulness separability before and after Heretic. choose and justify activation locations and token positions. select layers, probes, and hyperparameters on development data only.

control for topic, wording, prompt length, language identity, and response leakage. decoding harmfulness from generated refusal text is not evidence that a pre-response harmfulness signal drives refusal. compare a frozen original-model probe with appropriately cross-validated probes refitted after editing where useful: failure of the frozen probe can reflect representation drift rather than information loss. do not interpret raw cross-model vector cosine as shared mechanism without establishing comparable coordinates.

relate internal measurements to actual behavioral changes in each language. high probe accuracy establishes decodability, not causal use. a harmful-minus-harmless direction is only refusal-associated until interventions support a stronger interpretation. changes in a direction directly targeted by Heretic are expected and cannot alone carry the discovery.

step 6 - pursue the strongest explanation. use the freedom from step 2 to design the smallest decisive experiment. where justified, extract EN- and SL-derived directions and test the source-language × evaluation-language transfer matrix within each model. choose intervention locations and strengths on development data, and include no-op and matched random-direction controls plus benign utility checks. keep these activation interventions separate from the main Heretic comparison.

you may instead pursue subspaces, layer-specific interventions, representation-to-action coupling, or another approach supported by the pilot. the goal is a result that distinguishes competing explanations and predicts something on untouched data. use held-out semantic categories or an independent prompt source to challenge it. explain what survives, what breaks, and where the claim stops. prefer one well-tested insight over a large collection of loosely connected metrics. preserve the behavioral and mechanistic core even if every novelty candidate fails.

step 7 - test the claims honestly. freeze primary outcomes and confirmatory analyses before final evaluation. report original-to-edited effects for each model and language, with effect sizes and 95% confidence intervals. compare those changes across models and languages without attributing them to a specific training stage.

state the resampling and aggregation units. pair outputs on the same prompts and cluster translations/paraphrases by underlying semantic item; use cross-language pairing only where correspondence is established. four checkpoints, many layers, or many prompts do not create many independent model families. prompt-level uncertainty also does not measure variation across Heretic optimization runs. account for searching across hypotheses and layers, separate exploratory from confirmatory results, and state when sample sizes cannot resolve a difference. if resources require subsampling, freeze a stratified sample before viewing results and narrow the claims accordingly.

bonus - examine cjvt/GaMS3-12B as a bounded pre-instruction diagnostic. test harmfulness separability and a small EN/SL behavior sample with appropriate base-model formatting. do not compare its raw refusal rate with chat models as if the tasks were identical. only attempt base abliteration if refusal-like behavior is reproducible, the intervention has an interpretable target, and it does not jeopardize the main study. intermediate training checkpoints and no-safety training controls belong to a later extension unless already available.

deliver a reproducible repository and a paper grounded in executed experiments: pinned dependencies, split manifests, configurations, per-example outputs and scores, analysis scripts, and figures covering the four checkpoints in both languages. distinguish observations, interpretations, failed hypotheses, and unexecuted proposals. recompute every headline number from saved results and reconcile the abstract, tables, figures, and conclusions after the final audit. the discovery may change as evidence accumulates; the final paper must reflect the strongest claim that actually survives.
````

### [2] SKILL-INPUT — aii-web-tools · 2026-09-25 06:47:48 UTC

The agent loaded the **aii-web-tools** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-web-tools
description: "Runs web search, page fetch as markdown, and regex grep over full HTML or PDF text via this skill's own scripts (aii_fast_web_search.py, aii_fast_web_fetch.py) — a free-first keyless search stack with Serper fallback that works even where built-in WebSearch and WebFetch are absent. Use when a query, page, or paper must be searched, read, or mined for an exact quote, number, table value, or methodology sentence, and whenever a lossy summary would lose the detail. Triggers: web search, scholarly search, OpenAlex, Crossref, Serper, fetch a URL as markdown, read a PDF, arXiv, regex grep a page, exact quote, table value, citation check. NOT for: planning a broad multi-source literature review or mass verification campaign — use aii-web-research-tools; NOT for a PDF file already on disk — extraction, form filling, merging and PDF creation are anthropic-pdf; NOT for driving a browser or testing a UI."
---

## Web tools

You have three web capabilities: **search**, **fetch**, and **grep** (exact
regex extraction over a full page or PDF).

**Pick where they come from, in this order:**

1. **If you have built-in `WebSearch` / `WebFetch` tools, PREFER those over the
   scripts below.** They may be **deferred tools** (listed by name but with
   schemas not yet loaded) — if so, call `ToolSearch("select:WebSearch,WebFetch")`
   ONCE to load them, then use them normally. Do not skip them just because they
   need that one extra load step; they are the preferred path. Pair them with the
   `aii_web_tools__fetch_grep` script below when you need exact text / numbers /
   methodology that a summary would miss, or when reading a PDF.
2. **Only if you have NO built-in `WebSearch` / `WebFetch`** (e.g. the OpenHands
   backend), use the scripts in this skill (below). They are our own
   implementations — free-first web search (keyless general/scholarly engines,
   Serper fallback), html2text + PyMuPDF for fetch, and regex grep over the full
   document text. They work without any built-in web tools.

Workflow either way: **search** (discover) → **fetch** (read for the gist) →
**grep** (pull exact details / read PDFs).

---

## Running the scripts

Run every script with the skill's pre-provisioned interpreter (it already has
`requests`, `html2text`, `pymupdf`, `python-dotenv`). Set `PY` once:

```bash
export SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-web-tools"
export PY="$SKILL_DIR/../.ability_client_venv/bin/python"
```

### 1. Search the web (free-first: general or scholarly)

```bash
# general web (default): keyless engines (ddgs, marginalia); Serper only if they miss
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation LLM" --max-results 10
# scholarly mode: OpenAlex + Crossref (DOIs, citation counts)
$PY "$SKILL_DIR/scripts/aii_fast_web_search.py" --query "neuro-symbolic FOL translation" --mode scholarly
```

Returns ranked title / URL / snippet lines. `--mode general` (default) uses
keyless general engines; `--mode scholarly` uses academic APIs. Both fall back
to Serper (paid) only when the free engines miss. Use search first to scan the
landscape; snippets are for discovery only — fetch a page before judging it.

### 2. Fetch a page as markdown (HTML or PDF)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" fetch --url "https://arxiv.org/abs/2303.11366" --max-chars 10000
```

`--max-chars` caps output (default 10000); `--char-offset N` pages further in.
Handles PDFs transparently via PyMuPDF.

### 3. Grep a page or PDF (exact regex extraction)

```bash
$PY "$SKILL_DIR/scripts/aii_fast_web_fetch.py" grep --url "https://arxiv.org/pdf/2303.11366" --pattern "verbal reinforcement" --max-matches 20 --context-chars 200
```

Returns only the matching sections with surrounding context — the right tool
for exact numbers, table values, methodology, or long PDFs where a summary
would lose the detail. `-i` for case-insensitive.

**Parallelize** independent searches/fetches in one turn; only sequence a
fetch after the search that produced its URL.

---

## Notes

- The scripts call our ability server. If a script prints
  `Ability service not available`, the server is down — say so rather than
  silently improvising a different search method.
- Do **not** hand-roll your own `requests`/scraping for search when these
  tools are available: Serper returns clean Google results and the fetch/grep
  scripts already handle HTML, PDFs, and encoding.
````

### [3] SYSTEM-USER prompt · 2026-09-25 06:54:21 UTC

```
[Image: original 1280x6045, displayed at 423x2000. Multiply coordinates by 3.03 to map to original image.]
```

### [4] SYSTEM-USER prompt · 2026-09-25 06:54:25 UTC

```
[Image: original 375x9551, displayed at 79x2000. Multiply coordinates by 4.75 to map to original image.]
```

### [5] HUMAN-USER prompt · 2026-09-25 06:56:38 UTC

```
[Message from staff account 'staff', not the run's owner]

For the PAPER (LaTeX) and the paper website only; the internal report and executive summary stay faithful to the round record. Lead with the measurement result. Retitle to state it (e.g. "An English Keyword Objective Is Blind to Its Own Edit in Slovene"). Open the abstract with it: the keyword objective never reached its <=10/100 rule, threshold-blind fraction 1.0, EN 0.87 vs judge 0.13, SL 0.00 vs judge 0.82, Delta_lang -1.56 [-1.68, -1.44]. Put the GaMS3/Gemma transfer asymmetry after it. In the Introduction, replace "The central finding is an asymmetry" so it matches the Discussion. The 6/6 and 37/37 counts come from the C scorer in per_candidate.csv; the reference judge J gives 5/5 and 6/6. Name the scorer correctly or cite both. State that the cross-model depth test compared Gemma with Qwen3-8B. Keep all caveats (kappa 0.72 gate unmet; 94-95% EN truncation at 256 tokens).
```

### [6] SYSTEM-USER prompt · 2026-09-25 06:58:59 UTC

```
SITE VERIFICATION FAILED: 1 problem(s) in index.html.

- image source '' does not start with 'figures/', so it will not resolve once the page is published beside its figures folder

You MUST:
1. Fix every problem listed above in index.html.
2. Keep the page ONE self-contained file — all CSS and JavaScript inline, no external scripts, stylesheets or web fonts, nothing fetched at load time.
3. Point every image at figures/<filename>, where <filename> is a browser-renderable image that really exists in your figures/ folder. A vector PDF figure needs a PNG rendered beside it first; reference the PNG.
4. Re-open the page and confirm it still renders before finishing.
```

### [7] SYSTEM-USER prompt · 2026-09-25 07:00:00 UTC

```
[Image: original 1280x6481, displayed at 395x2000. Multiply coordinates by 3.24 to map to original image.]
```

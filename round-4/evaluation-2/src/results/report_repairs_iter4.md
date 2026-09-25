# Report repairs for the iteration-4 draft (paste-ready)

Produced by `scripts/p5_repairs.py`. Every number below either comes from a file this artifact wrote (path given) or is a verbatim line of its source file (quoted with `>` and the path underneath). Paths are relative to the run's `3_invention_loop/` directory; `results/...` means this artifact's own results folder. Lint result at the end.

### R1 — Placement result restated as MODEL-SPECIFIC and correctly bounded

**Replace the 'Firm positive' paragraph's first sentences with:**

In Gemma, the band-mass regression does NOT make band 13-24 a significant predictor of Slovene refusal once energy and English refusal are in the model:

> | b3_13_24 | 0.156 [-0.240, 0.529] |
>
> — verbatim from `round-3/experiment-9/src/results/report_tables.md`

The actual support is rank-based and placebo-tested. First, the fraction of layers 13-24 a set covers orders the lowest Slovene refusal that set reaches. Our recompute gives Spearman -0.942 over 10 sets (`results/corrected_numbers_iter4.json`, claim E9.band13_24_spearman). The artifact's permutation test:

> | band-density separation (band label permuted across sets) | 0.839 | [-0.537, 0.537] | **yes** (p = 0.0038) |
>
> — verbatim from `round-3/experiment-9/src/results/report_tables.md`

Second, the GaMS3 contrasts match on BOTH energy and layer count: a contiguous 13-24 band against every-4th-layer. Recomputed from `round-3/experiment-10/src/results/per_item.parquet`, S4 held-out confirm split, SL harmful refusal: E3 0.24 vs 0.81, E2 0.51 vs 0.89, E1 0.83 vs 0.93 (claims E10.E*.SL_B2 / SL_STR4 in `results/corrected_numbers_iter4.json`).

**The effective band DIFFERS between checkpoints.** GaMS3's c=1 band profile (SL harmful refusal, screen split, recomputed from `round-3/experiment-10/src/results/per_item.parquet` cells GRID_B*_c1.0): 1-12 0.93 (n=41), 13-24 0.24, 25-36 0.12, 37-48 0.85. So band 25-36 is the most effective band in GaMS3. Correction to the artifact summary and to this round's plan, which both quote '25-36 .02': that is the CI LOWER BOUND. The artifact's own table reads 0.12 [0.02, 0.22] (`round-3/experiment-10/src/results/report_tables.md`, row GRID_B3_c1.0). In Gemma the ordering is reversed: B3 (25-36) alone bottoms out near 0.95 while B2 (13-24) reaches 0.17 (per-set minima of SL harmful refusal over c in {0.25,0.5,1,1.5}, S3 half-B, recomputed from `round-3/experiment-9/src/results/per_item.parquet`: {"ALL48": 0.024, "B1": 1.0, "B2": 0.171, "B3": 0.951, "B4": 1.0, "C24": 0.171, "C36": 0.024, "K96": 0.024, "S2": 0.732, "S4": 0.927}). One candidate explanation of the iteration-1 dissociation is therefore that the two checkpoints' effective bands differ. This is a candidate, not a tested mechanism.

**Fix the coverage-set memberships** (from the layer lists in `round-3/experiment-9/src/results/cells/W_*.json`). The sets that cover NONE of layers 13-24 are B1,B3,B4. S4 covers 3/12 of them, so it does not belong in the 'missing' list. The half-coverage set S2 (6/12) was omitted. partial-coverage sets omitted/misfiled by the draft: {'S2': 0.5, 'S4': 0.25}; their min SL refusal: {'S2': 0.732, 'S4': 0.927}.

### R2 — Corrected-objective section replaced by its artifact's own verdict (move to FALSIFIED)

**Replace the 'Partial positive: corrected objective halves the gap' paragraph with:**

The corrected objective is not a better edit. Its pre-registered falsifier P7 fired: at equal English refusal, the dose-scaled keyword edit closes the gap as well. The mechanism is DOSE.

> BUT the pre-registered falsifier P7 fired: at equal English refusal the 1.5x-scaled old edit has gap +.33 (-.05 [-.41,+.12]), and at equal harmless KL the ladder reaches gap .00 (-.38 [-.47,-.29]) - dose for dose the corrected edit is strictly worse.
>
> — verbatim sentence from `round-3/experiment-11/src/.aii_worker_result.json`

P7 verdict as stored: value -0.050, CI [-0.410, 0.123], ladder points (EN refusal, gap, arm) [[0.15, 0.6799999999999999, 'B_keyword_t96'], [0.03, 0.32999999999999996, 'F_dose1.5'], [0.0, 0.0, 'F_dose2.0'], [0.0, 0.0, 'F_dose3.0']] (`round-3/experiment-11/src/results/frozen_predictions_with_verdicts.json`, predictions.P7.verdict).

**Add the miscalibration table**, recomputed here from `round-3/experiment-11/src/results/miscalibration_table.csv` (116 trial rows):

| instrument | range of refusals/100 over trials | mean abs error vs judge (per 100) |
|---|---|---|
| Heretic keyword counter | 72–100 | 19.6 |
| distilled classifier | 5–97 | 1.2 |
| judged (Qwen3-14B, frozen rubric) | 7–98 | – |

Table source: `round-3/experiment-11/src/results/miscalibration_table.csv`.

The file (`round-3/experiment-11/src/results/miscalibration_table.csv`) holds **116** trial rows: 60 corrected-run startup draws (identical parameters to iteration-1 draws 0-59) and 56 replayed iteration-1 draws 60-115. Per-source keyword MAE: startup 13.1, replay 26.6 per 100. **Not reproducible:** the '30.6 vs 2.1 per 100' errors and the 'trial-level count 63' quoted in the artifact summary and in this round's plan do not follow from this file. Quote the values above, with the file path, instead.

Agreement with the judge within edited cells (`round-3/experiment-11/src/scorer/certification.json`, qwen3_14b.edited_cells): classifier kappa 0.858 [0.820, 0.888] on HELD-OUT REPLAYED TRIALS; keyword rule 0.143. The in-loop values over all 116 draws:

> The keyword objective reaches only kappa +0.196 against the judge, reports .907 refusal where the judge sees .711, and 25.4% of its 'refusals' are false; the distilled classifier reaches +0.924.
>
> — verbatim sentence from `round-3/experiment-11/src/.aii_worker_result.json`

The draft's '0.924 certification within edited checkpoints' and 'first-64-token embeddings' are both misdescribed (claim E11.classifier_certification_kappa, `results/corrected_numbers_iter4.json`).

### R3 — Five in-place '[Correction, iter 4]' notes on the unchanged iteration-2 interpretations

1. **[Correction, iter 4] GaMS3 is RE-ENCODING, not information destruction.** After the edit a refit probe still separates harm. Refit AUROC (dim probe, S4, primary site) is EN 0.985 / SL 0.954; the frozen original probe applied after the edit gives EN 0.598 / SL 0.421 (`round-2/experiment-5/src/results/gams/mech_gams.json`, profile_at_primary and primary.frozen_vs_refit).
2. **[Correction, iter 4] Gemma's frozen-axis separation DOES halve in both languages; the late-layer rotation differs.**
> Gemma: frozen-axis separation halves equally in EN and SL from L28, yet behaviour changes only in EN -> axis compression does not explain the language asymmetry; late-layer axis rotation differs (cos 0.53 EN vs 0.83 SL).
>
> — verbatim sentence from `round-2/experiment-5/src/.aii_worker_result.json`
3. **[Correction, iter 4] Relabel the dose table 'MARKER-BASED (R_seq>0)'** and add judged columns. The exploratory LoRA x f table counts marker-based R_seq, not judged refusal:
> EXPLORATORY dose-response (LoRA x f): Gemma SL needs ~2x edit strength (R_seq>0 harmful SL 98.8/77.4/46.3/7.0% at f=1/1.5/2/3 vs EN 90.3/45.1/24.5/12.8%); GaMS EN/SL move together.
>
> — verbatim sentence from `round-2/experiment-5/src/.aii_worker_result.json`
4. **[Correction, iter 4] Split the repair table BY JUDGE, with a per-judge baseline row.** Per-cell counts under each judge are in `results/judge_sensitivity_iter4.csv` (columns wh_*, kw_*, clf_*, gpt41_*, rg_*).
5. **[Correction, iter 4] State the reverse-direction sign flip beside the forward Gap_K:**
> - GaMS3 (exp6, SUMMARY_ONLY, HistGBT CIs not re-run): Gap_K 0.147 [0.074, 0.265]; B_K 0.050; Gap_Heretic_K on journal trials 0.018; SL/EN mean-change ratio for K 0.59; reverse Gap_K -0.124; frozen-residual source-layer carrier R 0.009, K 0.005; reselection keeps ETPE_088, SL_est 1.08. [source: round-2/experiment-6/src/results/analysis_results.json]
>
> — verbatim from `round-3/evaluation-1/src/results/report_repairs.md`

### R4 — Iteration-1 section restored VERBATIM

The iteration-1 section is restored byte-for-byte from `iter_1/gen_report_text/gen_report_text/report.md` (source sha256 `46a8862661073073ac08432d74affd05c145161dcf4f22a3a52f6ac3bec68f95`). It runs from '# Iteration 1' up to but excluding '## References': 20046 bytes, written to `results/r4_iteration1_restored_verbatim.md` (sha256 `95ecbc185075a76ad89915525833e726c3542074594b8df7e9439e14fb94fc08`). It contains, unchanged: the strategy paragraph, the same-edit response-surface table, the incremental-R2 result, the swap table with paired tests and the KL ratio, the source-by-evaluation-language transfer matrix, the decision-margin decomposition, the exploratory double dissociation, the dead ends, the published-baseline figure and its own 'What we have learned so far'.

Paste it in place of the current condensed iteration-1 section. Then re-insert the iteration-3 correction notes in place: the corrected swap row, recomputed by the iteration-3 audit from the iteration-1 per-prompt scores:

> gemma,en,orig,swap,100,53,-0.47,-0.57,-0.38,47,0,1.4210854715202004e-14
> gemma,sl,orig,swap,97,25,-0.72,-0.81,-0.63,72,0,4.235164736271502e-22
>
> — verbatim from `round-3/evaluation-1/src/results/iter1_swap_stats.csv`

Restore the iteration-2 summary under a heading 'Superseded by iteration 3'. Keep the training-stage sentences but mark each one **[RETRACTED: n=2 checkpoints, one optimisation seed; no difference is attributable to a training stage]**. Do not delete them.

### R5 — 'What bounds this' blocks for every iteration-3 section

**Experiment 9 — what bounds this.** The index difference lies inside its own permutation null; the powered statistic is the prefix-curve separation:
> | prefix-curve separation SL−EN (same permutation) | 0.080 [0.021, 0.136] | [-0.059, 0.059] | **yes** (p = 0.0065) |
>
> — verbatim from `round-3/experiment-9/src/results/report_tables.md`
The index is NECESSARY, not sufficient:
> P3: the DEV-frozen depth index predicts per-cell residuals out of sample, Spearman 0.78 in both languages (permutation null [-0.27, 0.29]); 97% of cells covering fewer than index_SL = 20 effective layers leave Slovene above 0.5, but only 47% at/above it fall below, so the index is NECESSARY not sufficient.
>
> — verbatim sentence from `round-3/experiment-9/src/.aii_worker_result.json`
Controls, held-out categories and Holm are in `round-3/experiment-9/src/results/report_tables.md`. The judge was certified by a bought subsample. Our re-certification: EN kappa 0.871 (weighted) / 0.858 (sample), SL 0.871 / 0.723 (`results/judge_calibration.json`, gate).

**Experiment 10 — what bounds this.** English within-edited judge agreement was 0.54 (`round-3/experiment-10/src/results/judge_cert_pool.json`, kappa_refused_vs_not_en). The usable activation index is '>48' in both languages:
> CRITICAL CAVEAT: the co-primary USABLE index (refusal<0.5 AND INVALID<=0.10) is '>48' in BOTH languages - activation-space depth coverage only removes refusal by destroying the model (INVALID 0.72 EN / 0.38 SL at the crossing, FLORES +1.4 nats).
>
> — verbatim sentence from `round-3/experiment-10/src/.aii_worker_result.json`
The operator matters more than depth:
> - OPERATOR MATTERS MORE THAN DEPTH: the same directions as Heretic's row-norm-preserving weight edit remove refusal at ~zero collateral (|SL FLORES dNLL| <= 0.011, MC accuracy within 0.031 of no-op, INVALID ~0.01), while the raw activation projection of those same directions breaks the model.
>
> — verbatim sentence from `round-3/experiment-10/src/.aii_worker_result.json`

**Experiment 11 — what bounds this.** One model and one behavioural seed. No frontier judge validated any new label (no OpenRouter spend in that artifact; `round-3/experiment-11/src/reproducibility.md`). See R2.

**Experiment 12 — what bounds this.** The judge missed its gate: kappa 0.683 (`round-3/experiment-12/src/results/judge_certification_local.json`, holdout.kappa), with a Rogan-Gladen re-run of P1/P2. The baseline comparison:
> CRITICALLY, EN/L direction cosine ALSO fails (+0.010), so the 'familiar geometry stops predicting' boundary is real but stops for our index too, while two CHEAP baselines beat both by margins whose paired item-bootstrap CIs exclude zero: single-site transfer rho +0.732 (index-baseline -0.741 [-0.810, -0.528]) and the unedited model's baseline refusal in that language rho +0.661 (-0.670 [-0.721, -0.497]).
>
> — verbatim sentence from `round-3/experiment-12/src/.aii_worker_result.json`
Post-freeze patch: `round-3/experiment-12/src/results/analysis_patch.json` holds both hashes and the diff, and checks.py reports `analysis_py_unchanged=false`. Say this in the text.

### R6 — Producing file path beside every caption; iteration-3 recompute

Every table caption in the paper must carry its producing file (as in R1-R10 here). Independent recompute of the iteration-3 sections (`rederive_iter3.py`: stdlib + numpy + pyarrow only, raw files only) checked **102** numbers: verdicts {'match': 97, 'misdescribed': 3, 'mismatch': 2}. Mismatch-or-misdescribed rate 0.049, Wilson 95% [0.021, 0.110], against the audited half's prior 0.055. Placebos (all must collapse): cell-label shuffle +0.0006, language-label shuffle +0.0010, dose shuffle -0.0023; real effects PB2 -0.1048, PB3 -0.0714. The DEV-as-CONF detector fires LEAKAGE = True with DEV/CONF overlap 0. Judge-label permutation gives kappa +0.0049 (`results/corrected_numbers_iter4.json`, summary; row-level table `results/rederive_iter3_rows.csv`).

### R7 — Scope tables wired into the draft

**Guard ASR is not the complement of refusal.** Per cell x language: ASR_agree (both guards unsafe), ASR_any and both-safe, beside refusal / PARTIAL / INVALID (`results/asr_table.csv`; 136 cell x language rows over 70 cells). For the opposite-moving cell (Gemma edit: ASR high in EN, low in SL while SL refuses more), we measured the share of NON-REFUSED responses that both guards call safe. EN 0.106 [0.073, 0.147] (n=245), SL 0.338 [0.237, 0.438] (n=80); SL-EN 0.232 [0.124, 0.348]. Across cells, Spearman(ASR gap, refusal gap) = -0.836 [-0.928, -0.674] over 46 cells (`results/asr_summary.json`). Guard precision: NF4 for the newly scored cells. Agreement with the stored bf16 labels: Llama-Guard 0.967 (kappa 0.933, n=120), PolyGuard 1.000 (n=29) (`results/asr_summary.json`, nf4_fidelity). PolyGuard reached its time cap after 2672 of 3,420 rows, and the unscored rows are the LONGEST responses. For the newly scored cells, read `asr_llamaguard_only` in `results/asr_table.csv`: Llama-Guard covered every frozen row.

**Which reading the numbers support (`results/asr_summary.json`).** Across cells the ASR gap still tracks the refusal gap in the complementary direction (Spearman above). So this cell is not anomalous in DIRECTION. Its peculiarity is SIZE: Slovene non-refusals are 0.232 more often guard-safe than English non-refusals. Slovene 'non-refusals' are disproportionately non-actionable rather than compliant. This is StrongREJECT's willingness-versus-ability split, and it is why the SL ASR sits far below 1 - refusal.

**Validity columns** (INVALID, empty, truncation, repetition, GlotLID line-level consistency) for every cell x language x role: `results/validity_table.csv`; summary in `results/validity_summary.json`.

**Item-level flip analysis** (`results/flip_analysis.json`; frozen original-model probe score -> P(refused), before vs after):
- gams|en: slope ratio 0.03 [-0.31, 1.16], intercept shift -10.09 [-16.96, -8.82]; refit AUROC after edit 0.9851171100243759; frozen-probe AUROC after edit 0.597828884615967 -> NOT_ESTIMABLE (fewer than 10 refusals or non-refusals on one side of the edit); information PRESENT (refit AUROC >= .95 after edit)
- gams|sl: slope ratio -0.28 [-0.39, -0.19], intercept shift -10.50 [-12.09, -9.7]; refit AUROC after edit 0.9539432845311814; frozen-probe AUROC after edit 0.42123272116156185 -> NOT_ESTIMABLE (fewer than 10 refusals or non-refusals on one side of the edit); information PRESENT (refit AUROC >= .95 after edit)
- gemma|en: slope ratio 0.50 [0.24, 0.86], intercept shift -6.65 [-9.78, -5.63]; refit AUROC after edit 0.9970022256203728; frozen-probe AUROC after edit 0.9974110130357765 -> MIXED: criterion shift (intercept lowered) + partial coupling loss (frozen-axis slope reduced, not collapsed); information PRESENT (refit AUROC >= .95 after edit)
- gemma|sl: slope ratio 0.34 [0.19, 0.54], intercept shift -5.32 [-9.88, -3.55]; refit AUROC after edit 0.9954579176066254; frozen-probe AUROC after edit 0.9952005329376674 -> MIXED: criterion shift (intercept lowered) + partial coupling loss (frozen-axis slope reduced, not collapsed); information PRESENT (refit AUROC >= .95 after edit)

**Required statement (replaces the draft's mechanism paragraph; numbers from `results/flip_analysis.json`).** In Gemma the harm information survives the edit: refit and frozen-probe AUROC after the edit are both about 0.997. The frozen-axis slope is reduced but not collapsed, and the intercept drops sharply. The edit therefore mainly moved the CRITERION (the coupling of the same evidence to the refusal action), with a partial loss of coupling on top. The draft's paragraph says the opposite ('the behavioural gap is an action failure, not a representation failure' is right; the claim that evidence was lost is not). GaMS3's post-edit slope is not estimable because almost no refusals remain, so no statement is made for it.

### R8 — Behavioural headline bounded by ACHIEVED OPTIMISATION STRENGTH

**Replace 'The behavioural dissociation ... is robust across judges and datasets' with:**

The dissociation is a property of the achieved optimisation strength of one Heretic run per model, not of the models. (i) Dose-scaling Gemma's own keyword-selected edit closes the S5X gap: ladder points [[0.15, 0.6799999999999999, 'B_keyword_t96'], [0.03, 0.32999999999999996, 'F_dose1.5'], [0.0, 0.0, 'F_dose2.0'], [0.0, 0.0, 'F_dose3.0']] (`round-3/experiment-11/src/results/frozen_predictions_with_verdicts.json`). (ii) Heretic's own kernel support at c=1.5 reaches SL 0.024 / EN 0.049 harmful refusal at SL FLORES dNLL -0.000 (`round-3/experiment-9/src/results/cells.csv`, row W_K96_c1.5). (iii) The community bf16 edit of the same base has an S5X strict gap of +0.120 [0.060, 0.190] over 100 verified pairs (workhorse labels, paired by `round-2/experiment-4/src/frozen_samples.json` s5x_pairs; recomputed here from `results/pooled_generations.parquet`). (iv) The corrected swap row (GaMS3 trial-88 parameters applied to Gemma):
> gemma,en,orig,swap,100,53,-0.47,-0.57,-0.38,47,0,1.4210854715202004e-14
> gemma,sl,orig,swap,97,25,-0.72,-0.81,-0.63,72,0,4.235164736271502e-22
>
> — verbatim from `round-3/evaluation-1/src/results/iter1_swap_stats.csv`
Strike 'robust across judges and datasets'. Under the broad definition the S5X gap is a different number, and on RefusEU S5 it is null (`round-3/evaluation-1/src/results/gap_range.csv`).

### R9 — The two depth indices are different instruments

State once, in the methods: **experiments 9-10 index** = the smallest cumulative LAYER COUNT (grid step 4, on DEV S3 half A) whose activation ablation brings judged harmful refusal below 0.5. **Experiment 12 index** = the smallest cumulative DEPTH FRACTION (grid 0.1/0.25/0.5/0.75/1.0, on DEV S3 half B). They have different units, different halves and different grids, so they are NOT the same instrument and must not be compared numerically. Experiment 12's within-model decomposition (`round-3/experiment-12/src/results/posthoc_decomposition.json`, POST-HOC): Gemma within-anchor rho +0.678; Qwen3 index has variance = False (all its eligible languages share one value).
> | pooled, within-model-centred | 21 | - | **+0.458** (AUC: +0.620) | +0.655 | -0.087 |
>
> — verbatim from `round-3/experiment-12/src/README.md`

### R10 — Three miscounts fixed, plus the novelty caveat carried verbatim

1. Dead-end ledger: the text says 'Twenty items'; the table lists **16** (claim EV1.dead_end_ledger_count, `results/corrected_numbers_iter4.json`). Change the text to the table's count, or add the missing rows.
2. Eligible rows (experiment 12): **7** eligible model x language rows, not eight (`round-3/experiment-12/src/results/indices.json`, table[*].eligible). Seven rows x three weight cells = the **21** rows the P1 statistic uses.
3. Translation-fallback provenance: S1 Slovene is mostly gemini-2.5-flash, not NLLB. One-line per-set provenance:
> | S1_heretic | 2000 | 1000 | {'pod_file(google/gemini-2.5-flash)': 785, 'pod_file(facebook/nllb-200-distilled-1.3B@7be3e24664b38ce1cac29b8aeed6911aa0cf0576)': 100, 'gemini25flash_screenspec': 98, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 9, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback))': 6, 'gpt41': 2} | 79.7 (1000) |
>
> — verbatim from `round-3/evaluation-1/src/results/pending_human_review.md`
> | S3_jbb | 340 | 170 | {'pod_file(google/gemini-2.5-flash)': 167, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback))': 2, 'pod_file(facebook/nllb-200-distilled-1.3B (fallback: gemini chrF<40))': 1} | 77.4 (170) |
>
> — verbatim from `round-3/evaluation-1/src/results/pending_human_review.md`
> | S4_strongreject_pairs | 1028 | 514 | {'gpt41': 514} | 80.1 (514) |
>
> — verbatim from `round-3/evaluation-1/src/results/pending_human_review.md`
4. Pending review: 5 files, of which 3 are native-review packets (570 rows) and 2 are EXECUTOR-labelled checks; the draft calls all five 'packets ready for native-speaker labelling' (`results/pending_human_review_iter4.md`).
5. **C4 novelty paragraph: carry this flag VERBATIM:**
> | Hadetskyi et al. 2026, Not All Refusals Are Equal (arXiv 2607.02714) | NOT VERIFIED | "we find that it is also distributed widely across layers, especially in trillion-parameter MoE architectures" | – | The '2-3 middle layers' sentence was NOT FOUND in the abstract or the HTML full text (grep for 'middle layers', '2-3', 'two or three'): NOT VERIFIED. The paper is about DOMAIN-specific (cybersecurity) abliteration across 24 LLMs incl. Kimi K2, not about languages; cite it only for 'refusal distributed widely across layers'. | https://arxiv.org/html/2607.02714v2 |
>
> — verbatim from `round-3/evaluation-1/src/results/novelty_table.md`

### NEW — C3 (PARTIAL transition) result for the draft

**Identity (state it; it is not a finding).** Per cell, strict gap - broad gap = (R_SL - R_EN) - ((R_SL+P_SL) - (R_EN+P_EN)) = P_EN - P_SL, the between-language PARTIAL-share difference. 'The gap range is explained by PARTIAL' is an algebraic identity and is NOT reported as a finding; only C3-i/ii/iii are findings.

**C3-i (shape), CONFIRMED.** On the designed-ladder cells, the PARTIAL share's max-minus-min is EN 0.346 [0.257, 0.539] and SL 0.271 [0.090, 0.323]. Both lower bounds exceed 0.05, so the curves are not flat (`results/curve_fits.json`, pooled_designed_ladders.nonparametric; Holm 0.000 / 0.000).

**C3-ii (order), NOT SUPPORTED.** The proportional-odds assumption is violated in both ladders: AIC difference PO minus multinomial 59.1 (L1) and 243.3 (L2). The frozen rule therefore makes the nonparametric argmax primary. Delta_peak (SL minus EN, z-dose): L1 +0.45 [-0.45, 0.90]; L2 +0.98 [-0.98, 2.00]. Both CIs cover 0. The PO sensitivity fit points the same way: L1 +0.36 [0.28, 0.43], L2 +0.24 [-0.02, 0.52] (`results/curve_fits.json`).

**C3-iii (out-of-panel), NOT SUPPORTED.** Across 125 held-out cells, Spearman -0.427; the permuted-dose null is [-0.536, -0.367], p 0.339; MAE 0.192 vs null 0.192 (`results/curve_fits.json`, C3_iii).

**Estimator sensitivity (report beside the verdict).** The continuation-ratio fit does not assume proportional odds. It gives Delta_peak L1 +0.35 [0.20, 0.43] and L2 +0.90 [-0.08, 1.53] (`results/curve_fits.json`, continuation_ratio). So in L1 every parametric fit puts the Slovene peak later by about a third of a dose SD. The falsification rests on the nonparametric argmax, which the frozen PO check made primary. With only five dose levels in L1 its CI is far wider than the pre-hoc MDE assumed: the simulation in `configs/FREEZE_iter4_eval.json` was run for the PO estimator (MDE 0.53 z in L1, 1.08 z in L2). This is a power limitation of the frozen design, stated rather than re-litigated.

**Verdict (frozen falsifier, executed as written): C3 is FALSIFIED.** The strict/broad gap range is judge-definition noise. What survives is descriptive: PARTIAL is a genuine, non-flat transition state in both languages. Its peak location does not separate the languages with the cells available.

**Judge re-certification** (`results/judge_calibration.json`): 900 frozen, stratified items from this round's EDITED cells (515 bought gpt-4.1 labels, $ in `results/cost_log.jsonl`). Workhorse kappa refused-vs-not within edited cells: EN 0.871 weighted / 0.858 sample (gate MET); SL 0.871 / 0.723 (gate NOT MET under the conservative both-must-pass rule). Slovene rates therefore travel with Rogan-Gladen-corrected companions (`results/judge_sensitivity_iter4.csv`, rg_* columns). Gap claims: {'n_cells': 211, 'judge_sensitive': 40, 'definition_sensitive': 105, 'keyword_disagrees': 172, 'sensitive_vs_rogan_gladen': 30, 'sensitive_vs_broad': 105, 'sensitive_vs_keyword': 172, 'sensitive_vs_classifier': 43} (`results/judge_sensitive_gap_claims.csv`).

### NEW — Panel-level judge agreement: the frame-level gate hides a weak panel

The frozen stratified sample filled the workhorse-REFUSED strata with already-labelled exp9/exp10 items first. As a result exp11 and exp12 contributed no workhorse-REFUSED items, and their per-panel kappa could not be estimated. A declared POST-FREEZE supplement bought 160 more gpt-4.1 labels on workhorse-REFUSED harmful items from exp11/exp12 edited cells (hash-frozen draw, `results/calibration_supplement.json`; cumulative spend $0.82, `results/cost_log.jsonl`). On frozen + supplement, unweighted, it does NOT enter the gate (`results/judge_calibration_supplement.json`):

| panel x language | n | kappa refused-vs-not [95% CI] | Se | Sp | false-positive share |
|---|---|---|---|---|---|
| exp11|en | 65 | 0.226 [0.099, 0.399] | 1.000 | 0.463 | 0.725 |
| exp11|sl | 70 | 0.745 [0.573, 0.886] | 0.970 | 0.784 | 0.200 |
| exp12|en | 77 | 0.638 [0.430, 0.814] | 0.882 | 0.767 | 0.250 |
| exp12|sl | 110 | 0.553 [0.366, 0.739] | 0.660 | 0.883 | 0.175 |

In exp11 English (the L1 ladder's panel), most workhorse 'REFUSED' labels are gpt-4.1 'PARTIAL'. The workhorse over-calls refusal exactly where the PARTIAL transition happens. Re-expressing cells in gpt-4.1 classes, with P(gpt | workhorse class) per panel x language (unbiased because every draw was conditioned on the workhorse class; never applied to the unedited arm), gives:
- C3 Delta_argmax: L1 +0.45 -> +0.88; L2 +0.98 -> +0.98. The sign is unchanged; the C3-ii verdict (CI covering 0) does not depend on the judge.
- exp11 S5X strict gaps (raw -> gpt-4.1-equivalent): A_orig +0.04 -> +0.04; B_keyword_t96 +0.68 -> +0.63; C_corrected +0.38 -> +0.35; D2_reselected_judge +0.41 -> +0.38; D_reselected_clf +0.30 -> +0.30; F_dose1.5 +0.33 -> +0.31; F_dose2.0 +0.00 -> +0.07; F_dose3.0 +0.00 -> +0.08. The keyword-selected edit's gap survives the judge change.
The L1-ladder C3 statistics are marked JUDGE_SENSITIVE in `results/claims_registry_iter4.csv`.

### NEW — NF4 versus bf16 confound

Weight level (`results/quant_confound_weights.json`): NF4 changes each o_proj/down_proj matrix by a mean relative Frobenius error of 0.093. The trial-96 edit's per-layer removal-energy profile is nonetheless almost unchanged: cosine 0.999998, total energy difference -0.0006. The removed rows rotate by 5.2 degrees on average (5.8 max) over 71 edited matrices. Activation level (40 frozen S5X items = 20 verified pairs, 32 teacher-forced tokens, bf16 with CPU offload vs NF4): original mean KL 0.1122, top-1 agreement 0.915; trial-96 edit mean KL 0.0871, top-1 0.916 (`results/quant_confound_acts.json`). Behavioural cell (`results/quant_confound_behaviour.json`; same 40 items, trial-96 edit, greedy, both sides cut to 128 tokens, same blind gpt-4.1 rubric): refused bf16 vs NF4, EN 0.25 vs 0.25 (difference +0.00 [-0.20, 0.20]); SL 0.85 vs 0.70 (+0.15 [0.00, 0.30]). Paired SL-EN gap bf16 +0.60 [0.40, 0.80] vs NF4 +0.45 [0.20, 0.70] over 20 pairs. The Gemma edit's EN/SL asymmetry is therefore NOT an artefact of evaluating it in NF4: it is at least as large in bf16. This is one checkpoint, and the adapter was optimised on the NF4 base; the contrast with the community bf16 edit (R8) remains a difference in achieved optimisation, not in evaluation precision.

**Required sentence:** the NF4-vs-bf16 confound is BOUNDED by weight-level, activation-level and a 40-item behavioural measurement (one checkpoint, 20 verified pairs); it is NOT closed at panel scale.

---
**Lint:** 0 paragraph(s) with a decimal literal and no producing-path token.

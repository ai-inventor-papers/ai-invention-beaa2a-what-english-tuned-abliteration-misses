# Iteration-5 repair blocks R1-R12 (paste-ready)

Audited draft: `iter_4/gen_report_text/gen_report_text/paper_draft.md`. Every path below is relative to `3_invention_loop/`. Numbers come from this audit's
independent recompute (`rederive_iter5.py`, imports: stdlib, numpy, pyarrow) unless marked **[carried: path]**.
Verdict vocabulary: MATCH / MISMATCH / MISDESCRIBED / UNTRACEABLE / SIGN_REVERSED (the same as the iteration-3 and iteration-4 passes).

**Audit headline.** 136 first-pass numbers with a draft value were re-derived; 21 are defective
(15.4%, Wilson 95% CI [10.3%, 22.5%]), of which 14 are material (they change what a sentence claims).
Comparable priors under the SAME all-class definition: eval1 26/167 = 15.6% (quoted in the draft as '5.5%', which counts a
narrower class) and eval2 5/102 = 4.9%. This pass is weighted onto sections nobody had recomputed, and the interpretive defects concentrate there.
Counting numeric MISMATCHes only: 9/136. No number was SIGN_REVERSED.

---

## R1 - Placement restatement (replaces 'Firm positive', 'Iteration-4 additions' and 'The surviving finding')

**Observation.** At matched total removal energy AND matched layer count, where the edit energy sits orders residual refusal.
- **Gemma (exp13).** High-O beats low-O in 8/8 matched groups in EN and 8/8 in SL. Pooled contrast EN -0.682 [-0.72, -0.64], SL -0.377 [-0.42, -0.34] (paired item bootstrap; judge Qwen3-14B; SL within-edited kappa 0.729, below the 0.80 gate, so SL is JUDGE_SENSITIVE: Rogan-Gladen companion for the best SL cell: raw 0.27 -> 0.00, with Se/Sp taken from the 390-row gpt-4.1 overlap; a companion clipped at 0 means the correction is unstable at that specificity, so the SL cell rate is a range [0.00, 0.27], not a point). Source: `iter_4/gen_art/gen_art_experiment_13/results/per_item.csv`, `iter_4/gen_art/gen_art_experiment_13/results/cells/*.json`.
- **GaMS3 (exp14).** Spearman rho(O_SL, strict SL refusal) = -0.900 over 20 confirmation cells (draft -0.903 [-0.928, -0.857] **[carried: `iter_4/gen_art/gen_art_experiment_14/results/analysis_summary.json` primary.sl.ci]**), within level E2 -0.976, E3 -0.948. Source: `iter_4/gen_art/gen_art_experiment_14/results/per_item.parquet`, `iter_4/gen_art/gen_art_experiment_14/results/cells.csv`.
- **Qwen3-8B (exp13 outside panel).** 9/9 matched contrasts favour the better-placed member; Spearman rho(O) EN -0.72, SL -0.93, DE -0.94 (all valid items; the artifact's 39-item subset gives -0.76 / -0.93 / -0.84). 8/9 CIs excluding zero: **[carried: `iter_4/gen_art/gen_art_experiment_13/results/report_tables.md`]**.
- **The dose rival FAILS.** Doubling the energy in the late band (layers 33-48) leaves EN 0.88 / SL 0.92, against the mid band (16-31) at EN 0.07 / SL 0.27 at matched energy.
- **The winning band at matched energy is the SAME in both siblings.** GaMS3 SL strict: E2 B2 0.50 < B3 0.59 < B4 0.94 < B1 0.97; E3 B2 0.30 < B3 0.53 < B4 0.94 < B1 0.97. Gemma's frozen argmax prediction (13-24) PASSES; the GaMS3 DEV profile's prediction (25-36) is NAMED_AND_LOST.
- **UNRESOLVED disagreement, reported as such.** The UNMATCHED c = 1 grid in exp10 favours 25-36 over 13-24 by +0.12 [+0.00, +0.27] (SL strict, paired items; eval2's R1 correction gave +0.12 [0.02, 0.22]). The matched-energy panels and this unmatched grid differ in design (matched vs unmatched dose). This audit verifies both numbers and does not adjudicate.

**STRIKE** 'the critical band differs between siblings' everywhere it appears: as a finding (line 887), as a novelty qualifier (line 682, 'the critical band moves between sibling checkpoints'), and as the candidate explanation of the iteration-1 dissociation (line 861). Only the DEV profile's argmax differs (layer 27 vs 19); the behavioural winner does not. **No band recommendation is made.**

## R2 - Exp13's nested-R² ladder, with the failure reason the right way round

Replace the exp13 'Nested R²' table (lines 714-719) with the per-language ladders, recomputed from `iter_4/gen_art/gen_art_experiment_13/results/per_item.csv` + `iter_4/gen_art/gen_art_experiment_13/results/cells/*.json` (outcome: strict residual refusal on the 18 confirmation cells; OLS on the rate scale):

| | EN | SL |
|---|---|---|
| log energy alone | 0.0011 | 0.0077 |
| + layer count, + span, + EN/SL cosine (nuisance stack) | 0.8793 | 0.7342 |
| + O (full) | 0.9065 | 0.7897 |
| **dR² of O over the nuisance stack** | **0.0273** | **0.0555** |
| O alone | 0.8733 | 0.7540 |
| EN/SL cosine alone | 0.8268 | 0.6297 |
| dR² of O over log energy + layer count ONLY | 0.8924 | 0.7696 |
| Spearman(O, cosine) | 0.808 | 0.764 |

MDE for dR² at 80% power: 0.047 EN / 0.109 SL **[carried: `iter_4/gen_art/gen_art_experiment_13/results/analysis.json` confirm.per_language.*.mde_dR2]**.
**Falsifier, stated correctly:** O adds 0.027 (EN) / 0.055 (SL) over a nuisance stack that CONTAINS the g-weighted EN/SL cosine. Both are under the 0.10 bar, and EN is under the 0.05 falsifier. Over log energy + layer count ALONE, O adds 0.892 / 0.770. The reason is **collinearity with the cosine**. It is NOT that 'energy already explains the outcome': log energy alone explains 0.001 / 0.008.
**Move** the 0.088 / 0.668 / 0.790 / 0.806 table to the exp14 section, labelled 'each predictor added separately to log energy (GaMS3, SL)'. Recomputed: logE 0.090, logE+O 0.669, logE+O_cos 0.788, logE+O_band4 0.808. The draft's cumulative rows are wrong: logE+O+O_cos = 0.805, logE+O+O_cos+O_band4 = 0.822.
**Fix 'What we have learned'** to compare like with like: O over logE is ~0.87 (Gemma EN, O alone 0.87 with logE ~0) vs 0.58 (GaMS3 SL). O over the cosine-containing stack is 0.027. exp13's cosine regressor (per-layer EN/SL direction cosine, g-weighted) and exp14's O_cos are DIFFERENT quantities.

## R3 - Exp14 relabelling

All four dose/placement contrasts are **Slovene strict**. The panel has **no English contrast**:
- dose at fixed O_ship (A1 vs A4): -0.186 [-0.286, -0.086]
- dose at fixed O_swap (A3 vs A2): -0.157 [-0.257, -0.071]
- placement at fixed high E (A1 vs A3): -0.029 [-0.129, +0.071], McNemar p 0.774 **[carried]**
- placement at fixed low E (A4 vs A2): +0.000 [-0.086, +0.071], p 1.000 **[carried]**
(paired item bootstrap, 70 items; source `iter_4/gen_art/gen_art_experiment_14/results/per_item.parquet`). The draft's 'EN -0.186 ... SL -0.157' (line 755) is MISDESCRIBED.
Boundary 3 corrected: 'the GaMS3 profile predicts Gemma's 50 weight cells at -0.442, versus -0.278 (screen) and -0.111 (confirm split) on its own iteration-3 panel' **[carried: `iter_4/gen_art/gen_art_experiment_14/results/screen.json`]**.
Paste exp14 Tables 3, 6, 6b and 7 and the per-stratum rho table (E2 -0.976, E3 -0.948) from `iter_4/gen_art/gen_art_experiment_14/results/report_tables.md`, citing `iter_4/gen_art/gen_art_experiment_14/results/analysis_summary.json`.

## R4 - Citation lint

41 file references in the draft: 27 resolve as written, 14 resolve after a rewrite, and 0 do not resolve (gate **PASS**). All 10 planted positive controls (the known misses) are detected. Rewrites (every target is checked to contain a number quoted in the citing sentence):

| draft line | as written | correct path |
|---|---|---|
| 168 | `results/t1_harmful.json` | `iter_2/gen_art/gen_art_experiment_5/results/analysis/tables.md` |
| 183 | `results/t1_harmful.json` | `iter_2/gen_art/gen_art_experiment_5/results/analysis/tables.md` |
| 263 | `results/flip_analysis.json` | `iter_4/gen_art/gen_art_evaluation_2/results/flip_analysis.json` |
| 351 | `results/gap_table.json` | `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json` |
| 489 | `results/dev_index.json` | `iter_3/gen_art/gen_art_experiment_9/results/redundancy_index.json` |
| 502 | `results/matched_energy_groups.json` | `iter_3/gen_art/gen_art_experiment_9/results/report_tables.md` |
| 535 | `results/dev_index.json` | `iter_3/gen_art/gen_art_experiment_10/results/redundancy_index.json` |
| 537 | `results/panel_summary.json` | `iter_3/gen_art/gen_art_experiment_10/results/report_tables.md` |
| 578 | `corrected_numbers_iter4.json` | `iter_4/gen_art/gen_art_evaluation_2/results/corrected_numbers_iter4.json` |
| 586 | `results/s5x_headline.json` | `iter_3/gen_art/gen_art_experiment_11/results/headline_table.csv` |
| 622 | `results/dev_indices.json` | `iter_3/gen_art/gen_art_experiment_12/results/indices.json` |
| 630 | `analysis.json` | `iter_3/gen_art/gen_art_experiment_12/results/analysis.json` |
| 661 | `corrected_numbers_iter4.json` | `iter_4/gen_art/gen_art_evaluation_2/results/corrected_numbers_iter4.json` |
| 885 | `results/pending_human_review_iter4.md` | `iter_4/gen_art/gen_art_evaluation_2/results/pending_human_review_iter4.md` |

Tables without any source path: 20 of 37 (draft lines 31, 115, 189, 204, 215, 226, 237, 250, 273, 292, 323, 407, 431, 445, 456, 466, 549, 560, 653, 663). Each gets its path in the blocks below or in `results/path_lint.csv`. The exp4/exp5/exp7/exp8/exp12 tables cite `iter_2/gen_art/gen_art_experiment_4/results/headline_table.csv`, `iter_2/gen_art/gen_art_experiment_5/results/analysis/tables.md`, `iter_2/gen_art/gen_art_experiment_7/results/analysis.json`, `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md`, `iter_3/gen_art/gen_art_experiment_12/results/indices.json`.

## R5 - Exp11 count corrections (`iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv`)

- Trial 107: judged REFUSED **63/100** (not 10/100), keyword 72/100.
- Trial 96: **37 REFUSED + 49 PARTIAL**. '15/100' is arm B's S5X English refusal rate (0.150, `iter_3/gen_art/gen_art_experiment_11/results/headline_table.csv`), a different item set; relabel it there.
- Miscalibration table: keyword range 72-100, classifier 5-97, judge 7-98. MAE per 100 vs judge: keyword 19.6, classifier 1.18 over the table's trials. `iter_4/gen_art/gen_art_experiment_15/results/conventional_table.csv` gives 19.6 vs 1.2 over all 116 draws and 26.6 vs 1.2 over TPE draws. exp11's README quotes 30.6 vs 2.1, which neither file reproduces. Kappas: in-loop keyword 0.196, classifier 0.924 (`conventional_table.csv` gemma/all); certified 0.143 / 0.858 on held-out replayed trials **[carried]**.
- **DELETE** 'Partial positive: corrected objective halves the gap' (line 863). Its own P7 falsifier fired: the 1.5x dose arm gives +0.33 against the corrected arm's +0.38. The dose-2.0 'zero gap' is a floor, with both languages at 0.000.
- Add eval2's gpt-4.1-equivalent exp11 gaps (B .68 -> .63, C .38 -> .35, dose-2.0 .00 -> .07) **[carried: `iter_4/gen_art/gen_art_evaluation_2/results/judge_calibration_supplement.json`]**. Add the exp11 EN panel kappa, recomputed within edited cells: **0.226 [0.110, 0.370]** (n = 65 pairs). The exp11 English gaps stay workhorse-labelled and JUDGE_SENSITIVE; this audit bought no labels.

## R6 - Exp15 selection section (`iter_4/gen_art/gen_art_experiment_15/results/per_candidate.csv`, `reselection_table.csv`)

- Add the judge-referenced column: mean keyword minus judge +19.6 (Gemma) / +6.0 (GaMS3), beside keyword minus classifier +20.5 / +15.0. Slopes of keyword on classifier: 0.308 / 0.738.
- Relabel 'Judge (gpt-4.1)' in the reselection table as **the Qwen3-14B workhorse (J)**. gpt-4.1 was only the 800-item certification subsample (kappa 0.850). Add the K_journal row (trial 96, KL 0.026) and the GaMS3-J row (trial 115, KL 0.060).
- Replace 'close' (line 798): trial 88 has KL 0.175 and trial 85 (classifier-selected) has KL 0.015, an order of magnitude apart.
- Replace 'this explains the divergent search outcomes' (line 881) with the artifact's own reading: LOCAL low-region blindness in Gemma, plus STRUCTURAL threshold blindness shared by both searches (TBF = 1.0 and 1.0; the frozen rule falls back in both).
- Incumbent's best shot, from `conventional_table.csv`: oracle threshold kappa 0.567 (Gemma) / 0.655 (GaMS3); repaired list 0.174 / 0.680, MAE 4.64 (GaMS3). Held-out StrongREJECT keyword kappa 0.02 EN / 0.00 SL, BUT the two zeros mean opposite things (EN: the rule fires often and is wrong; SL: it fires on almost nothing) **[carried: `iter_4/gen_art/gen_art_experiment_15/results/analysis.json` heldout_source_sanity]**.

## R7 - The three wrong iteration-2 in-place corrections

(iii) **T12 note** (line 305). Rewrite it from exp5's own marker rule. The marker rule UNDERCOUNTS: at f = 1, EN marker refusal is 27.1% on the 48-item dose subset **[carried: `iter_2/gen_art/gen_art_experiment_5/results/dose/dose_gemma.json`]**, while judged refusal is 70.3% (exp5 T1) and the readout leans to refusal (R_seq > 0) on 87.9% of the S4 EN items **[recomputed this pass from `iter_2/gen_art/gen_art_experiment_5/results/gemma/rseq_markers.json`; the dose file's own pass gives 90.3%]**. SL: 98.4%. The true EN-SL gap is therefore NARROWER than the marker gap, not wider. Add the R_seq > 0 columns and the f = 0.25 / 0.75 rows from `iter_2/gen_art/gen_art_experiment_5/results/dose/dose_{gemma,gams}.json`.
(iv) **Exp8 W-table**: split it into a gpt-4.1 table (W0, W1 with CIs, n = 70) and a SECOND-JUDGE table (W0 0.93/0.70, W1 0.81/0.73, W3 0.11/0.29, W4 0.47/0.70). Delete the 'within-judge contrast' note: it is false, because W0 and W1 were not scored by one judge **[carried: `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md`]**.
(ii) **T7 note**: replace 'the edit barely moved the harm signal' with exp5's L28 frozen-axis halving in BOTH languages and the late-layer rotation (cos 0.53 EN vs 0.83 SL) **[carried: `iter_2/gen_art/gen_art_experiment_5/results/gemma/drift_geometry_*.json`]**. Label exp8's depth table and the X1 sentence with their judges.

## R8 - Ledgers and restored summary

- Restore the iteration-2 'Summary of findings' under the heading 'Superseded by iteration 3'. MARK the retracted training-stage sentences as retracted and give the reason; do not delete them. Precedent and source: `iter_4/gen_art/gen_art_evaluation_2/results/r4_iteration1_restored_verbatim.md`.
- Replace 'Fourteen hypotheses falsified' (line 883) with `results/ledger_F1_F14.md` (evidenced failures, each with the number and direction that killed it). Add the DISTINCT `results/ledger_U1_U10.md` (unexecuted proposals; U10 is filled from the iteration-4 deviations files). The draft's list mixes the two, and several of its items were never falsified by a test (for example 'keyword validity on edited checkpoints' is an observation, not a hypothesis).
- Paste exp10's PB3 (-0.07 [-0.131, -0.007]), PB4 (Spearman 0.21) and the operator-versus-depth paragraph verbatim from `iter_3/gen_art/gen_art_experiment_10/results/report_tables.md` instead of 'see the artifact' (line 570).
- Add a short 'Strategy' paragraph for iterations 4 and 5, mapping each artifact to the review objection it answers.

## R9 - The two depth indices (stated once, together)

exp9/exp10's index is a cumulative LAYER COUNT in steps of 4, measured on S3 half A (`iter_3/gen_art/gen_art_experiment_9/results/redundancy_index.json`, `iter_3/gen_art/gen_art_experiment_10/results/redundancy_index.json`). exp12's index is a cumulative DEPTH FRACTION measured on half B (`iter_3/gen_art/gen_art_experiment_12/results/indices.json`; the frozen table is recomputed here and all 12 cells MATCH the draft). **They are not the same instrument.** POST-HOC decomposition (labelled POST-HOC): within-anchor rho +0.678; zero variance in Qwen3's eligible languages; pooled within-model-centred +0.458 **[carried: `iter_3/gen_art/gen_art_experiment_12/results/posthoc_decomposition.json`]**. exp12 P1, re-derived arithmetically from the 21 saved rows: -0.009 (draft -0.009).

## R10 - The NF4/bf16 sentence, at the size the probe supports

'Paired SL-EN strict gap bf16 +0.60 [+0.40, +0.80] vs NF4 +0.45 [+0.20, +0.70], n = 20 S5X pairs, one checkpoint, gpt-4.1 labels. The difference is not resolved. The asymmetry is at least as large in bf16, so it is not an NF4 artefact.' Recomputed from `iter_4/gen_art/gen_art_evaluation_2/results/gpt41_quant_behaviour_labels.jsonl` + `quant_behaviour_bf16_gens.jsonl`, with pairs from `iter_2/gen_art/gen_art_experiment_4/frozen_samples.json`. **Remove** 'NF4 quantisation attenuates the gap by approximately 0.15' (line 835): a 20-pair difference whose intervals overlap supports no attenuation estimate. Quote exp6's Gap_R interval at the level exp6 reports it (90% CI [0.008, 0.027]) **[carried: `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json`]**.

## R11 - Scope tables placed beside refusal

Official RefusEU guard ASR (Llama-Guard-3-8B + PolyGuard agreement; disagreements excluded), recomputed from `iter_4/gen_art/gen_art_evaluation_2/results/pooled_generations.parquet`:

| checkpoint | ASR EN | ASR SL | S5 refusal EN | S5 refusal SL | flag |
|---|---|---|---|---|---|
| gams_orig | 0.015 | 0.012 | 0.986 | 0.871 |  |
| gams_edit | 0.982 | 0.972 | 0.014 | 0.000 |  |
| gemma_orig | 0.026 | 0.016 | 0.971 | 0.939 |  |
| gemma_edit | 0.738 | 0.103 | 0.287 | 0.739 | DIVERGES: the ASR gap is larger than the refusal gap |
| community_ref | 1.000 | 0.870 | 0.054 | 0.114 | DIVERGES: the ASR gap is larger than the refusal gap |

**STRUCK:** 'the EN-SL compliance gap ... is smaller in magnitude' (line 183). On the official guard, the Gemma-edit ASR gap is 0.738 - 0.103, which is larger than the refusal gap.
**Non-refused decomposition, corrected to the Gemma-edit row:** among non-refused S5 outputs, both guards call EN 0.116 and SL 0.370 safe, SL-EN +0.254 [+0.136, +0.374]. eval2's guarded 330-row subsample gives 0.106 vs 0.338, +0.232 [0.124, 0.348] **[carried: `iter_4/gen_art/gen_art_evaluation_2/results/asr_table.csv`]**. The draft's 7.2% / 32.7% belong to exp11's corrected arm C (recomputed: 0.072, n=153 non-refused EN outputs); relabel them there.
Restate Spearman -0.836 (ASR gap vs refusal gap, 46 cells) as DESCRIPTIVE: the two share a denominator, and PolyGuard covers only 22% of long rows.
Add exp5's per-task utility table (`iter_2/gen_art/gen_art_experiment_5/results/{gemma,gams}/utility_{orig,edit}.json`), eval2's validity / repetition / truncation summary per cell (`iter_4/gen_art/gen_art_evaluation_2/results/validity_table.csv`), and GlotLID language consistency per cell (`iter_4/gen_art/gen_art_evaluation_2/results/glotlid_recomputed.parquet`).
Replace the flip prose (line 263) with eval2's statistics: Gemma EN slope 0.50 [0.24, 0.86], SL 0.34 [0.19, 0.54]; refit AUROC ~0.997; GaMS3 not estimable **[carried: `iter_4/gen_art/gen_art_evaluation_2/results/flip_analysis.json`]**.

## R12 - Independent recompute, and the sentence each section opens with

Recompute module: `rederive_iter5.py` (stdlib + numpy + pyarrow.parquet for I/O). It reads only per-item generation/label tables, label jsonl files and cell descriptor files. The module list it actually loaded is written to `results/rederive_summary.json` (`third_party_modules_loaded`).
Placebos run INSIDE this path: 8 of 8 collapse as required. Two are reported but not scored as controls: the exp13 language-swap of O (it does NOT collapse, which is the draft's 'cross-prediction' observation) and the exp12 index permutation (the real effect is already null). See `results/placebo_table.json`.
Sections NOT independently re-derived in this pass carry this opening sentence: *'The numbers in this section were not re-derived by an independent path in iteration 5. The run's earlier passes measured 15.6% of numbers defective in iterations 1-2 (all defect classes; quoted as 5.5% for a narrower class) and 4.9% [2.1, 11.0] in iteration 3. This pass measured 15.4% [10.3%, 22.5%] on previously unaudited sections.'* This applies to: iteration 1 (exp1, exp3); exp5 T2-T13; exp6-exp8; eval1's dead-end ledger. Their numbers were audited by eval1 and carried by eval2.
Judge-definition sensitivity: pooled kappa overstates within-edited agreement. In exp4 EN, pooled 0.89 (n=359) vs within edited 0.42 (n=180) (inflation +0.47); SL 0.93 (n=348) vs 0.87 (n=171). The draft's 'kappa 0.83 / 0.91' for the exp4 judge (line 319) is a pooled figure and should be printed beside the within-edited EN value.

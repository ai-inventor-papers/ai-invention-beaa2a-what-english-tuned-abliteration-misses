# Iteration 1

## Strategy

Iteration 1 had three goals: (a) establish a frozen, audited data protocol covering all planned evaluation splits; (b) run two matched Heretic optimizations under identical conditions to produce the four core checkpoints, score them bilingually, and characterize the same-edit response surface across the two models; and (c) screen the refusal-direction transfer hypothesis with a 2x2 source-language by evaluation-language ablation matrix, a Slovene-direction increment test, and matched-efficacy and dose-response controls. The hypothesis predicted that English-derived ablation would suppress Slovene refusal less than English refusal in GaMS3 (because its Slovene-specific safety training creates a direction English misses) and equally in Gemma (which has no Slovene-specific training).

All three goals were executed in parallel as three artifacts: a dataset pipeline, a matched Heretic experiment, and a refusal-direction transfer screen. The key constraint was a single NVIDIA L4 GPU with 24 GB VRAM, which forced 4-bit NF4 quantization for both 12B models [5, 6, 7] and limited the Heretic budget to 116 trials per model instead of the planned 200.


## Artifact 1: Frozen data protocol

The dataset pipeline [ARTIFACT:art_qdUCJWbc5kHh] produced 48,696 rows in 10 blocks, each hashed and frozen (protocol hash `dc33bde4`). The splits are designed to prevent information leakage across the study's stages.

| Block | Purpose | Rows | Notes |
|-------|---------|------|-------|
| S1 heretic | Heretic construction data | 2,000 | mlabonne harmful_behaviors + harmless_alpaca, EN+SL |
| S2 semantic | Mechanistic DEV | 1,664 | 400/416 harmful rows overlap S1 by construction |
| S3 screen DEV prompts | Direction-transfer screen | 540 | 85 JBB harmful/benign twins + 100 Dolly |
| S3 screen DEV utility | Utility measures for screen | 640 | 200 FLORES dev + 120 MC items |
| S4 StrongREJECT pairs | Held-out mechanistic validation | 1,028 | 257 gpt-4.1-generated twin pairs, EN+SL |
| S5 RefusEU [11] | Final behavioural evaluation | 2,800 | All official EN/SL eval rows (1,400+1,400) |
| S5X RefusEU cross-translations | Paired cross-language claims | 1,400 | gpt-4.1 cross-translations of 700-row core |
| S6 XSTest | Over-refusal evaluation | 900 | 450+450, SL by gpt-4.1; 219 safe items |
| S7 Slovenian LLM Eval | Utility (six tasks) | 35,700 | ARC-C, BoolQ, HellaSwag, OBQA, PIQA, Winogrande |
| S7 FLORES devtest | Fluency | 2,024 | eng_Latn/slv_Latn parallel |

Translation was done by Gemini 2.5 Flash (temperature 0) for the screen-DEV items (mean chrF++ 81.3, LaBSE 0.856), with NLLB-200-distilled-1.3B fallback for 8 rows where Gemini refused to translate harmful content. The harmful-behaviours items used for Heretic were translated entirely by NLLB (chrF++ median 70.3) because the API translator declined 56 of 110 harmful prompts. All translations received automated QC (cross-family back-translation chrF++, LaBSE, GlotLID, length ratio) but no native-speaker review; a 250-row blinded packet is marked PENDING. The total API cost for the dataset was $4.77 across 5,474 calls.

A finding from the dataset build: RefusEU EN/SL rows sharing the same row ID are not translations. Graded correspondence yields 0 translations, 158 paraphrases, 1,092 conceptual matches, and 150 non-matches. Paired cross-language claims on the official rows are therefore unsupported; the S5X cross-translations were built for that purpose.

Overlap audit confirmed no near-duplicate or exact overlap between S4-S7 and S1-S3. The screen-spec Gemini prompt, when used as a system message, answered or refused 49% of items rather than translating them, which prompted the framing wrapper that fixed the issue.


## Artifact 2: Matched Heretic runs and same-edit asymmetry

Two Heretic runs [ARTIFACT:art_vzhOPupFwE4M] were executed under a single identical optimizer configuration: Heretic commit `3521f864` [19], seed 20260923, NF4 4-bit quantization with bf16 compute, explicit batch size 128, the same English harmful/harmless data (mlabonne/harmful_behaviors + harmless_alpaca), and the same search space. Chat templates were verified byte-identical across the two models. Both runs completed 116 trials (60 TPE startup + 56 TPE). The first 60 trials are the same 60 edits in both models, verified parameter-for-parameter.

### Selection rule

The selection rule was frozen before any trial ran (2026-09-23T14:35Z). The primary rule selects the trial with the lowest KL divergence among those with 10 or fewer refusals per 100 prompts. No trial in either model reached that threshold, so fallback 1 fired for both: minimum refusals subject to KL at most 1.0.

| | GaMS3-12B-Instruct | gemma-3-12b-it |
|---|---|---|
| Selected trial | 88 | 96 |
| English refusals (of 100) | 16 | 69 |
| First-token KL | 0.175 | 0.024 |
| Candidates searched | 116 | 116 |
| Fallback rule | min refusals, KL <= 1.0 | min refusals, KL <= 1.0 |

Both selections reproduce exactly against Heretic's own journal values: KL relative differences are 2.8e-8 and 1.7e-8, and refusal counts match to the integer. Baseline refusals reproduce Heretic's printed values exactly: GaMS3 98/100, Gemma 100/100.

### Behavioural results across six checkpoints

Each model was scored in both languages under three conditions: original, own edit, and swap (the other model's selected parameters applied to this model). All 28 audit checks pass with zero mismatches; three placebo tests correctly fail.

**Table 1. Refusal counts and language integrity across six checkpoints.**

| Model | Condition | EN refusals | SL refusals | KL | FLORES NLL rise (SL) | SL in Slovene |
|-------|-----------|-------------|-------------|-----|---------------------|---------------|
| GaMS3 | original | 98 | 97 | 0.000 | 0.000 | 100% |
| GaMS3 | own edit (trial 88) | 16 | 10 | 0.175 | -0.004 | 100% |
| GaMS3 | swap (Gemma trial 96) | 25 | 25 | 0.046 | +0.006 | 100% |
| Gemma | original | 100 | 97 | 0.000 | 0.000 | 100% |
| Gemma | own edit (trial 96) | 69 | 90 | 0.024 | +0.001 | 100% |
| Gemma | swap (GaMS3 trial 88) | 53 | 25 | 0.254 | +0.010 | 100% |

No checkpoint shows language damage: FLORES+ dev per-token NLL moves by at most 0.01 nats, and 100% of Slovene answers remain in Slovene. Repetition rates (4-gram) stay below 0.004 in all conditions.

### Same-edit asymmetry

The core finding of this artifact is the same-edit asymmetry. On all 60 shared edits, gemma-3-12b-it refuses more than GaMS3-12B-Instruct: 60 of 60 edits, zero the other way. The paired median difference is +25 refusals per 100 prompts (bootstrap 95% CI [10, 43]). Yet the two models' KL divergence from the same edit agrees almost perfectly: Spearman rho 0.967 (CI [0.93, 0.98]), partial rho 0.923 after controlling for kernel mass. The same edit produces the same representational damage in both models but a very different safety outcome.

[FIGURE:fig1]

The efficiency gap quantifies this: refusal drop per unit KL is 13.4 times higher in GaMS3 than in Gemma (medians 1,449 versus 108; ratio CI [7.0, 30.0]). On the KL-matched half of the shared edits (KL medians 0.0101 versus 0.0098), GaMS3 sits at 65/100 refusals while Gemma sits at 99/100.

**Table 2. Same-edit response surface (60 shared edits, English keyword refusal).**

| Measure | GaMS3 | Gemma |
|---------|-------|-------|
| Refusals median | 74.5 | 99.0 |
| Refusals range | [25, 99] | [71, 100] |
| KL median | 0.0079 | 0.0057 |
| Efficiency (refusal drop / KL) | 1,449 | 108 |
| Efficiency ratio | 13.4x (CI [7.0, 30.0]) | |
| Edits where Gemma refuses more | 60/60 | |
| Paired refusal diff median | +25 (CI [10, 43]) | |
| KL Spearman rho | 0.967 (CI [0.93, 0.98]) | |
| KL partial rho (controlling kernel mass) | 0.923 | |

### Sibling-surface guard (test of alternate hypothesis 3)

A pre-registered guard tested whether the refusal-rank agreement between the two models reflects a shared response surface or merely shared parameter draws (alternate hypothesis 3: differences come from the search, not the model). The guard uses incremental R-squared: the other model's refusal, added to the shared edit parameters, should improve prediction if the agreement is substantive rather than inherited from the draws.

The reading is "intermediate", not "shared surface". Refusal ranks agree moderately (rho 0.781, CI [0.63, 0.88]; partial rho after kernel mass 0.647), but the incremental R-squared of the sibling's refusal is near zero for refusal (dR2 0.008, CI [-0.017, 0.055] in one direction; -0.006, CI [-0.028, 0.018] in the other). This was validated on synthetic data: a strength-only generator (no shared residual) produces dR2 CI including zero, while a shared-residual generator produces dR2 = 0.51. The guard discriminates correctly.

For KL, the picture differs: gradient-boosted models show positive dR2 (0.143, CI [0.074, 0.246]; 0.154, CI [0.093, 0.242]), consistent with a shared KL response surface. The 2D Procrustes disparity is 0.325 (1 - disparity = 0.675), and the RV coefficient is 0.783 (permutation p < 0.001). The two models share how edits damage harmless computation (KL) but not how that damage translates into refusal change.

### Cross-language swap test

Applying GaMS3's edit parameters to Gemma suppresses Slovene refusal far more than English: Gemma-swap SL 97 to 25 versus EN 100 to 53 (McNemar p < 1e-19 for SL, p = 0.020 for EN). The reverse swap (Gemma's parameters on GaMS3) yields 25/25 refusals in both languages. The swap never reproduces the own-edit outcome in either direction [15]: all Newcombe CIs exclude zero.

**Table 3. Swap tests: McNemar and KL comparisons.**

| Model | Comparison | EN diff | EN p | SL diff | SL p | KL ratio (own/swap) |
|-------|-----------|---------|------|---------|------|---------------------|
| GaMS3 | own vs swap | -0.09 | 0.078 | -0.15 | 2.7e-4 | 3.80 (CI [3.13, 4.69]) |
| Gemma | own vs swap | +0.16 | 0.020 | +0.65 | 5.4e-20 | 0.095 (CI [0.046, 0.189]) |
| GaMS3 | orig vs own | +0.82 | 4.1e-25 | +0.87 | 2.9e-25 | — |
| Gemma | orig vs own | +0.31 | 9.3e-10 | +0.07 | 0.016 | — |

### Direction geometry

The two models' orthogonalized refusal directions agree only moderately [8, 14]: mean cosine 0.634 across all 49 layers, dropping to 0.573 over layers 24-47 where Heretic's kernel concentrates. Their harmless means nearly coincide (cosine 0.983), and a random-direction control gives 0.014. The large behavioural asymmetry coexists with moderate direction similarity, which means raw cross-model cosine does not predict it.

### Dead end: Slovene LLM judge

The blinded three-way LLM judge for Slovene responses was implemented but never executed. The OpenRouter API key returned HTTP 403 on every request, including a 4-token probe, even after the platform replaced it. Zero of 600 planned judgements succeeded; none were invented. All Slovene numbers therefore rest on a keyword-marker list with moderate agreement against 40 executor hand labels (accuracy 0.75, Cohen's kappa 0.48). Native review is pending. This limits all Slovene refusal counts to development-grade measurements.

### Limits

Two models are two units. Nothing here attributes the asymmetry to Slovene continual pretraining, instruction tuning, or any training stage. GaMS3 is a same-family reference, not a controlled derivative of this Gemma checkpoint. The Gemma arm's resistance to abliteration is confounded with 4-bit NF4 quantization and the reduced 116-trial budget: the published bf16 200-trial Heretic edit of gemma-3-12b-it reaches 3/100 EN refusals [13], so this is not evidence that Gemma resists abliteration in general. One optimizer seed per model; prompt-level CIs do not capture run-to-run optimizer variance.


## Artifact 3: Refusal-direction transfer screen

The A1 screen [ARTIFACT:art_jxrJNc9o4QSp] tested whether an English-derived refusal direction suppresses Slovene refusal as effectively as English refusal, with controls. It ran on both models under the same 4-bit NF4 quantization on the L4 GPU.

### Data and directions

The screen used 85 JailbreakBench harmful/benign twins after dropping 15 AdvBench rows flagged by a LaBSE overlap audit against S1. Items were split into halves A (44) and B (41) by SHA-1. Slovene translations came from Gemini 2.5 Flash (mean chrF++ 81.3) with NLLB fallback for 22 rows. Refusal directions were computed as difference-in-means on winsorized residuals from half A. Layer and position were selected on half A using Arditi-style filters: GaMS3 at layer 34, Gemma at layer 20, both at position -1 (last prompt token). The protocol was hash-frozen before half B was touched.

### Frozen prediction and screen verdict

The hypothesis predicted that after English-direction ablation, GaMS3 would show a larger residual Slovene refusal gap (SL minus EN) than Gemma. The screen verdict is **WEAK**: the predicted contrast is **REVERSED**.

### Validity gate

The refusal-propensity trait (log-odds of refusal-prefix tokens) was validated against judged refusal rates. It passed for Gemma (Spearman 0.91, AUROC 0.96) but failed for GaMS3 (Spearman 0.51, AUROC 0.70), consistent with the layer dissociation between probing and steering reported by Wang et al. [16]. The primary outcome was therefore declared judge-based before reading the rule outcomes.

### Judge-based results

Generations were scored blind by gpt-4.1 (the plan's gpt-4.1-mini failed a T5 hand-check). A total of 1,596 greedy generations were judged.

**Table 4. Judged refusal rates after English-direction ablation (half B, 41 harmful items).**

| Model | Condition | EN refusal rate | SL refusal rate | SL-EN residual gap | Gap 95% CI |
|-------|-----------|----------------|----------------|--------------------|--------------------|
| GaMS3 | original | 0.902 | 0.927 | — | — |
| GaMS3 | d_EN ablation | 0.463 | 0.341 | -0.145 | [-0.32, +0.03] |
| Gemma | original | 0.829 | 1.000 | — | — |
| Gemma | d_EN ablation | 0.073 | 0.854 | +0.765 | [+0.62, +0.89] |

In GaMS3, the English direction suppresses both languages roughly equally. In Gemma, the same operation nearly eliminates English refusal (83% to 7%) while barely touching Slovene (100% to 85%). This is the opposite of the hypothesis prediction for GaMS3, and the Gemma result is far stronger than expected. The residual gap of +0.77 in Gemma is large and its CI excludes zero.

[FIGURE:fig2]

### Transfer matrix

The 2x2 source-language by evaluation-language transfer matrix (normalized so same-language transfer equals 1.0) quantifies the asymmetry.

**Table 5. Transfer matrix: fraction of same-language refusal drop achieved by cross-language direction.**

| | Evaluated in EN | Evaluated in SL |
|---|---|---|
| **GaMS3** | | |
| EN-derived direction | 1.00 | 0.96 (CI [0.93, 0.98]) |
| SL-derived direction | 0.81 (CI [0.79, 0.82]) | 1.00 |
| **Gemma** | | |
| EN-derived direction | 1.00 | 3.47 (CI [2.76, 4.90]) |
| SL-derived direction | 0.66 (CI [0.61, 0.70]) | 1.00 |

GaMS3 shows near-symmetric transfer: the English direction achieves 96% of the Slovene-direction's Slovene effect. Gemma shows a pathological asymmetry: the English direction achieves a 3.47x overshoot in log-odds terms on Slovene, despite near-perfect direction cosine (cos(d_EN, d_SL) = 0.92). The explanation is Gemma's Slovene refusal margin. Gemma's baseline Slovene refusal log-odds (R_harm) is 13.9, compared to 3.6 for English. Even a direction with cosine 0.92 to the Slovene one, when it operates on a margin that wide, achieves almost nothing in behavioural terms.

### Exploratory: GaMS3 double dissociation under direction addition

Adding the English-derived direction to GaMS3 activations at strength 1.0 [20] shifts English refusal log-odds by +3.54 (CI [2.96, 4.09]) with negligible Slovene effect (-1.11, CI [-1.22, -1.01]). Adding the Slovene-derived direction shifts Slovene by +2.23 (CI [1.97, 2.49]) with a smaller English effect (-1.54, CI [-1.91, -1.16]). This double dissociation is consistent with partially language-specific refusal directions in GaMS3 [9, 24], though the SL-to-EN cross-effect is not zero.

### Heretic bridge

Running Heretic's own code with 20 TPE startup edits (seed 20260923) on each model provides a bridge between the single-direction ablation and the full optimizer. The mean Slovene-minus-English residual gap is +0.108 (CI [0.055, 0.168]) for GaMS3 and +0.235 (CI [0.162, 0.301]) for Gemma. Both show a positive gap, meaning Slovene refusal persists more than English after Heretic's English-optimized edits. Gemma's gap is twice GaMS3's, consistent with the transfer-matrix result.

### Dead ends

**GaMS3 Slovene-direction increment**: The Slovene-direction increment for GaMS3 (F_raw = 0.228, F_ctrl = 0.195) is confounded with collateral damage. The full-span ablation of the Slovene direction at GaMS3's selected layer destroys utility: FLORES NLL rises by +1.4 nats per token, and about 35% of outputs are malformed. The frozen and post-freeze random controls are destructive even when raw-energy-matched (T7 failed; amendment documented). The increment is therefore uninterpretable for GaMS3.

**Gemma Slovene-direction increment**: For Gemma, the increment is zero (I_raw = 0.0, CI [-0.098, 0.098]; F_raw = 0.0). This is consistent with the transfer matrix: the English direction already captures whatever the Slovene direction can add, because both point in effectively the same direction, and the gap in Gemma comes not from direction geometry but from margin.

**Sensitivity arms cut**: Priority-3 sensitivity arms (S1-derived, per-language-best-layer, and content-token directions) were cut for time. The code exists but was not executed.

**Gemma selection grid cut**: The full 145-candidate grid (15 layers x candidates) was run for GaMS3, but the Gemma grid was halved (every 2nd layer, only positions -1 and -5) because GPU sharing made the timing projection exceed 30 minutes.


## What we have learned so far

Iteration 1 established the infrastructure and the behavioural facts that the subsequent iterations must explain. The central finding is a large same-edit asymmetry: on 60 identical edits, GaMS3 loses 13.4 times more refusal per unit KL than Gemma, while the KL damage itself is nearly identical (rho 0.967). The sibling-surface guard confirms that this refusal divergence is not merely inherited from the shared parameter draws. At the same time, the refusal-direction transfer screen produced a result opposite to the initial prediction: it is Gemma, not GaMS3, that shows a large cross-language transfer gap, with English ablation nearly eliminating English refusal while leaving Slovene nearly intact. The gap is explained not by direction geometry (cosine 0.92 between EN and SL directions in Gemma) but by a massive difference in refusal margins (SL log-odds 13.9 versus EN 3.6), a pattern consistent with the representation-action disconnect identified in recent work [17, 18].

These results set up the discovery panel. The surrogacy decomposition (whether English outcomes predict Slovene outcomes across an edit population) requires the random-edit panel of at least 150 non-collapsed edits, which will be scored bilingually on continuous traits. The exposure quantity (the energy each edit removes from each language's tokens) will be logged from the LoRA adapter outputs during those same passes. The mechanistic core (layer-wise direction characterization, probe fitting, drift analysis) uses the S2 and S4 data that this iteration froze. The causal arms and the practitioner corollary depend on the exposure regression that the panel enables.

Two concerns carry forward. First, all Slovene refusal counts are development-grade because the LLM judge was blocked by the API key failure; the keyword-marker agreement is only moderate (kappa 0.48). Second, the 4-bit quantization confound means that absolute refusal rates are not comparable to published bf16 results, though within-study comparisons remain valid because both models share the same quantization.



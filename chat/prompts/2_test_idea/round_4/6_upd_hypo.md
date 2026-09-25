# upd_hypo — test_idea

> Phase: `invention_loop` · round 4 · `upd_hypo`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `upd_hypo` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-24 22:18:07 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A hypothesis reviser (Step 3.6: UPD_HYPO in the invention loop)

You received the current hypothesis, all artifacts, and the paper draft.
Revise the hypothesis based on what the evidence supports.

Honest revision → focused research. Inflated confidence → wasted iteration.
</your_role>
</ai_inventor_context>

You are deciding where a research run points next, using the evidence it
gathered this iteration. Your revised hypothesis IS the next iteration's
hypothesis — nothing else steers the run — so this is a steering decision
first and a piece of honest reflection second.

SCOPE: Your ONLY output is the revised hypothesis text. You do NOT run code,
produce artifacts, fix bugs, or otherwise act on the evidence yourself — the
next iteration of the invention loop will spawn fresh artifacts based on your
revised hypothesis. Reflect on the evidence and rewrite the hypothesis;
nothing else.

PRINCIPLES:
- Ground every revision in specific artifacts and results. A number that was
  projected, assumed or left as a placeholder is not a result.
- CLASSIFY EVERY ARTIFACT SEPARATELY, BEFORE CHOOSING A MOVE. One artifact
  is one bet. A round is normally MIXED, and judging the round as a whole is
  how one real positive gets thrown out with the nulls beside it. The round
  summary is then READ OFF the best of those verdicts, and the move follows
  from the summary and the remaining budget by a fixed rule — not by free
  judgement, because free judgement is where past runs went wrong.
- LATCH ONTO A GENUINE POSITIVE. One executed, non-obvious, baseline-proof
  result at a size the ask cares about is the run's whole output. Hold it,
  and spend the next round on its mechanism, its boundary, its confounds and
  its replication. Do not go looking for a different question while it lives.
- WEAK IS NOT NULL. A small real effect, a positive that lost to a baseline
  by a margin, a signal seen on one body of evidence — these are LEADS. The
  answer to a lead is to make it bigger and cleaner, not to abandon it. Widen
  off a lead only after deepening it has come back empty.
- A round where NOTHING is real is the signal to go WIDER, not smaller. The
  question the user asked is still open; the answer you tried is the only
  thing that was refuted, and every next bet should be a different answer to
  the ask.
- Never shrink the claim until the effect you happened to observe becomes
  the claim. A finding nobody needed is worse than an honest negative.
- A broken test is fixed ONCE, with the claim unchanged. A bet that breaks
  twice is dropped, and its budget goes to a new candidate.
- The run is looking for a POSITIVE, NON-OBVIOUS result. A clean negative is
  a LAST RESORT, right only when no iteration and no candidate remain.
- Increase specificity as evidence accumulates; do not inflate confidence
  without strong evidence.
- Revise hypothesis text only — never attempt to address feedback by running
  code, proposing fixes, or producing artifacts; the next loop iteration
  handles all artifact generation.

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/upd_hypo/upd_hypo`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/upd_hypo/upd_hypo/`:
GOOD: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/upd_hypo/upd_hypo/file.py`, `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/upd_hypo/upd_hypo/results/out.json`
BAD: `/tmp/file.py`, `~/output.json`, `./file.py`, any path outside the workspace
</workspace>
<disposable_outputs>
YOUR WORKING DIRECTORY IS A DELIVERABLE. When this module ends it must read
like a GitHub repository someone else can fork, resume and run — and the bulk
it holds must be either worth keeping or restorable. This run shares a storage
volume with the database; a run that fills it stops every other run on the box.

So before you finish, produce TWO files:

1. `.aii/manifest.yaml` — one entry per heavy path, each with EXACTLY ONE decision.
   The `.aii/` directory ALREADY EXISTS in your cwd: write the file into
   it. Do not create, replace or `touch` `.aii` itself — a plain file by
   that name makes the manifest unwritable for the rest of the module.

```yaml
entries:
  - path: results/
    keep: six GPU-hours of sweep output, not reproducible inside this run
  - path: hf_cache/
    delete: redownloadable
    source: "huggingface-cli download meta-llama/Llama-3-8B"
  - path: checkpoints/
    delete: regenerable
    source: "uv run train.py --epochs 3 --seed 0"
```

   - `keep:` takes a ONE-LINE reason. Use it for the expensive and the
     irreproducible: trained weights, long-running results, datasets you
     collected yourself.
   - `delete:` takes `redownloadable` (and a `source:` naming the repo id, URL
     or command) or `regenerable` (and a `source:` that is the command which
     rebuilds it). These are deleted AFTER the round ends, never mid-step.
   - Every path is RELATIVE TO YOUR CWD and must resolve INSIDE it. Absolute
     paths, `..`, and anything resolving outside are rejected.
   - Globs and whole directories are fine. A whole `hf_cache/` is ONE entry —
     do not list files individually.

2. `README.md` — written as if your cwd were a GitHub repository: what you
   did, the layout with a line per important file/directory, how to run it,
   and a **"Restoring removed files"** section giving the install/download
   command for EVERY `delete` entry. An `install.sh` or `restore.sh` beside it
   is welcome.

A CHECKER RUNS WHEN YOU SUBMIT. If anything heavy has no decision it fails
your submission and hands you the uncovered list, grouped by directory with
sizes, and you fix the manifest and submit again.

WHAT NEEDS NO DECISION — do not write entries for these:
- text and code files, at ANY size (source, JSON, CSV, YAML, logs, markdown);
- anything under the auto-keep floor (10 MB), whatever it holds.
Only large binaries and cache directories (`hf_cache/`, `.venv/`,
`node_modules/`, `checkpoints/`, `wandb/`, `__pycache__/`, …) need one.

NEVER mark your results, figures, papers, code, logs or anything a later step
reads as `delete`. If a later step needs it, it is a `keep`.

WHAT A `keep` BUYS YOU. Anything you do not mark `delete` stays exactly where
you wrote it, on this run's storage volume, at the path it already has — it is
not moved, renamed or copied. A later round reads it there, by that absolute
workspace path, so a checkpoint you keep is a checkpoint the next round can
load instead of retraining. It is also the ONLY copy: the publish step pushes
your cwd to GitHub but skips every file of 100 MB or
more, so trained weights and large binary artifacts never leave the volume.
Name each kept artifact in your results and your `README.md` by its path
RELATIVE to your cwd, and say it stays on the run's volume rather than in the
published repository. Never write an absolute server path into a file that is
published: a reader's machine has none of them.
</disposable_outputs>

<current_hypothesis>
The hypothesis as it stands. Revise it based on the evidence below.

kind: hypothesis
title: Where the edit lands, not how deep
hypothesis: |-
  TITLE CLAIM. What decides whether an English-derived refusal edit also removes refusal in another language is NOT how deep or how broad the edit is, but HOW WELL THE EDIT'S PER-LAYER REMOVAL ENERGY LINES UP WITH THE LAYERS AT WHICH THAT LANGUAGE'S REFUSAL IS CAUSALLY WRITTEN - and the effective layers differ by language and by checkpoint. The corollary, measured inside the optimiser itself, is that a substring refusal objective cannot see this at all: it has no gradient in the region where its own candidates differ, so it stops at an under-dosed, badly-placed kernel, and the whole cross-language "gap" that this run started from is a property of that under-dosed edit rather than of the model.

  === WHAT ITERATION 3 SETTLED (executed numbers, read off the artifact files; every one has a source file named) ===

  (P-1) PLACEMENT BEATS COVERAGE AT MATCHED ENERGY AND MATCHED LAYER COUNT - the surviving positive, replicated in both models. In GaMS3 [art_xLy2vVlI7OEL, results/report_tables.md, 481/481 re-derived, placebos collapse to 0.003 / -0.001 / 0.023]: at matched total removal energy AND matched layer count (12 contiguous vs every 4th), SL judged harmful refusal is 0.24 vs 0.81 (E3), 0.51 vs 0.89 (E2), 0.83 vs 0.93 (E1), every CI excluding 0; the pre-registered PB2 was FALSIFIED IN THE OPPOSITE DIRECTION (narrow-and-strong minus broad-and-weak = -0.10 [-0.150, -0.060], Holm p 0.000) and PB3's language interaction runs backwards (-0.07 [-0.131, -0.007]): concentrating helps Slovene MORE than English. The nested decomposition is the cleanest statement: log E alone R2 0.325, + WHERE the energy sits 0.718, + HOW MANY layers 0.400. Matched random and energy-matched PC controls are null (SL 0.93-0.95 vs no-op 0.93). In Gemma [art_ex4hbgThhJaL] the same shape appears as a rank statistic: lowest reachable SL refusal is monotone in the fraction of layers 13-24 covered (12/12 -> 0.024-0.171; 6/12 -> 0.732; 3/12 -> 0.927; 0/12 -> 0.951-1.000), Spearman -0.942, permutation p 0.0038; at E = 19.2, 12 contiguous mid-depth layers reach SL 0.63 while 24 strided layers leave 0.98; leave-one-band-out sparing 25-36 costs Slovene +0.39 and English 0.00.
      THE HONEST QUALIFICATION, WHICH THE NEXT DRAFT MUST CARRY: the Slovene band-mass REGRESSION coefficient in Gemma is +0.156 [-0.240, 0.529] and does NOT reach significance - the dominant Slovene regression term is the English refusal rate (0.855). The supporting evidence for placement in Slovene is the rank statistic and the matched-energy/matched-count contrasts, NOT the regression.
      AND THE EFFECTIVE BAND IS MODEL-SPECIFIC, WHICH THE ITERATION-3 DRAFT WRONGLY DENIED: at c = 1, GaMS3's SL band profile is 1-12 0.93, 13-24 0.24, 25-36 0.02, 37-48 0.85 - its best single band is 25-36, where Gemma never falls below 0.95 at any strength, while Gemma's necessary band is 13-24. Both models place, but not in the same place. This difference is a CANDIDATE EXPLANATION for the iteration-1 dissociation and must not be foreclosed.

  (P-2) THE OPERATOR MATTERS MORE THAN THE DEPTH [art_xLy2vVlI7OEL, Part A vs Part B]. The SAME per-layer directions, applied as Heretic's projected, row-norm-preserving weight edit, remove refusal at essentially zero collateral (|SL FLORES dNLL| <= 0.011, MC accuracy within 0.031 of no-op, INVALID ~0.01), while the raw activation projection of those same directions only reaches refusal < 0.5 by destroying the model: the co-primary USABLE index (refusal < 0.5 AND INVALID <= 0.10) is ">48" in BOTH languages, with INVALID 0.72 EN / 0.38 SL and FLORES +1.4 nats at the crossing. Iteration 2's all-48-layer activation repair (SL .86 -> .10) is the same artefact: it costs +0.589 nats and a real English capability hit, -0.053 [-0.083, -0.023] S7 macro [art_ex4hbgThhJaL]. This is why an activation-space depth measurement failed to predict weight-edit outcomes (see D-3), and it is the mechanistic reason the replacement instrument in C1 is defined in WEIGHT-EDIT space.

  (P-3) THE OPTIMISER'S SCORER IS BLIND EXACTLY WHERE ITS CANDIDATES DIFFER - iteration 2's positive, now replicated at scale with a certified instrument [art_0XmNBGkzsJc_, audits 305/305 + 17/17 + 59/59, 7 placebos all fail as required]. All 116 iteration-1 parameter draws were re-scored INSIDE Heretic's own loop and all 11,600 in-loop generations labelled with the frozen rubric: the keyword objective reaches kappa +0.196 against the judge, reports .907 refusal where the judge sees .711, 25.4% of its "refusals" are false, and its count NEVER FALLS BELOW 72/100 across all 116 draws while judged refusal spans 7-98/100. Mean absolute error in a draw's refusal count: 30.6/100 keyword vs 2.1/100 for the distilled classifier. On the selected trial 96 it reports 74/100 where the judge sees 37 refused and 49 PARTIAL. The classifier is certified at kappa 0.858 [0.820, 0.888] on 20 HELD-OUT REPLAYED TRIALS against the keyword rule's 0.143 (this is the number to quote; 0.924 is the in-domain figure). Under the corrected scorer the frozen selection rule fires its PRIMARY branch, which the keyword run never could (trial 7, 5/100, aligned coverage A1 64.0 vs trial 96's 26.0), and a second optimiser seed replicates (5/100, A1 65.1). Post-hoc reselection of the trials already held recovers the whole effect, so this is MIS-SCORING OF HELD CANDIDATES, not a different search.

  (D-1) DEAD, WITH ONE PAPER SENTENCE EACH AND NO FURTHER BUDGET.
      - DEPTH COVERAGE AS A COUNT: Gemma P1 dR2 0.040 [0.006, 0.136] with leave-one-out -0.002, partial F p 0.17, a permutation placebo giving a LARGER dR2 on average (p95 0.158), MDE 0.071 - a powered rejection; GaMS3 PB1 dR2 0.002 [0.000, 0.010], leave-one-cell-out -0.043.
      - BROAD-AND-WEAK BEATS NARROW-AND-STRONG: falsified in both models, in the opposite direction (above).
      - THE COUNT-BASED REDUNDANCY INDEX AS AN INSTRUMENT: PB4 Spearman 0.21 in GaMS3 (a count cannot express placement: it gives a 12-layer band and 12 strided layers the same prediction); the EN/SL index difference is 4 layers = one k-grid step, inside its own language-permutation null [-4, +4] (Gemma) and EQUIVALENT_WITHIN_MARGIN at Holm p 0.069 (GaMS3); index_EN = 16 / index_SL = 20 in BOTH checkpoints, so the Slovene lag is common to the pair and is NOT what distinguishes them. The index is NECESSARY, NOT SUFFICIENT even where it survives: 97% of Gemma cells below index_SL leave SL above 0.5, but only 47% at or above it fall below.
      - THE CORRECTED OBJECTIVE AS A BETTER EDIT: its own pre-registered falsifier P7 FIRED. At equal English refusal the 1.5x-scaled old edit has gap +.33 (difference -.05 [-.41, +.12]); at equal harmless KL the dose ladder reaches gap .00 (-.38 [-.47, -.29]) - dose for dose the corrected edit is STRICTLY WORSE. The finding in art_0XmNBGkzsJc_ is the miscalibration and the recoverability by post-hoc rescoring, NOT the corrected checkpoint. This moves out of the "partial positive" column into the falsified column, exactly as the reviewer requires.
      - Already closed in iteration 2 and staying closed: exposure differential D, static geometry b1/b2/b3, LSAR Omega, r_prior, the language-identity direction (works at +1.93 nats SL FLORES, unusable), the thin-margin rival.

  (D-2) THE TWO-MODEL DISSOCIATION IS BOUNDED BY ACHIEVED OPTIMISATION STRENGTH, NOT BY MODEL IDENTITY. Four independent rows now say so: the dose ladder closes the S5X gap to .00 at a KL below the corrected edit's [art_0XmNBGkzsJc_]; Heretic's own kernel support at c = 1.5 reaches SL 0.024 / EN 0.049 harmful refusal at FLORES dNLL -0.000, KL 0.030, 0% invalid, 99.2% Slovene, and SL 0.08 / EN 0.02 on the 100 verified RefusEU pairs versus unedited 0.98 / 0.91 [art_ex4hbgThhJaL]; the community bf16 edit of the same base sits at +.12 [.05, .20]; and the corrected iteration-1 swap row has GaMS3's parameters taking Gemma's SLOVENE from 97 to 25 while English only reaches 53, at ~10x the KL. "Robust across judges and datasets" must be struck; the claim is "this specific under-optimised, badly-placed selected edit under-transfers", with the n = 2 / one-seed / NF4 caveat beside it.

  (D-3) THE NEGATIVE THAT IS MORE TRANSFERABLE THAN THE POSITIVE [art_kfCCWf7o8eJ9]. A depth index measured in ACTIVATION space does not predict WEIGHT-edit outcomes out of sample: pooled Spearman -0.009 [-0.131, 0.192] over 21 rows (7 eligible model x language rows x 3 cells; the draft's "eight" is wrong), permutation p 0.16, concordance 8/12 = 0.67 (6/12 under judge-error correction). The familiar geometric predictor fails BESIDE it - EN/L direction cosine +0.010, and it REVERSES SIGN between models (-0.748 gemma, +0.556 qwen3). Two trivial baselines beat both by margins whose paired item-bootstrap CIs exclude zero: the single-site transfer rate rho +0.732 (index minus baseline -0.741 [-0.810, -0.528]) and the unedited model's own baseline refusal in that language rho +0.661 (-0.670 [-0.721, -0.497]). The asymmetry itself replicated on a new harm source and two new languages: the real trial-96 adapter leaves EN 0.60 / DE 0.53 / LT 0.75 / SL 0.92 from a 0.93-0.98 no-op, with its energy- and collateral-matched random control at SL 0.98 and the NLLB-vs-gpt translation-method control moving every rate by <= 0.09. Caveats that travel with it: the local judge missed its own gate at kappa 0.683 [0.629, 0.737] (Se .984 / Sp .741, so absolute levels are biased upward, Rogan-Gladen corrected re-run reported); analysis.py was patched after the freeze for numerical robustness only, with both hashes and the full diff in results/analysis_patch.json and checks.py flagging analysis_py_unchanged = false.
      NOTE THE SCALE CLASH, which the draft must reconcile once: experiments 9 and 10 call "the depth index" a LAYER COUNT on DEV half A; experiment 12 calls it a DEPTH FRACTION on half B. They are not the same instrument. Experiment 12's post-hoc decomposition belongs beside the falsification: within the anchor model the index DOES order the languages (rho +0.678), but Qwen3's eligible languages share one index value so it has zero variance there, and pooled within-model-centred rho is +0.458 (AUC +0.620).

  (D-4) THE PARTIAL WEDGE AND THE JUDGE RANGE [art_Z3I1K3VnFZuz]. The headline gap is definition-dependent: STRICT (refused only) +0.22 to +0.71 across judges and datasets, all CIs > 0; BROAD (refused + partial) -0.04 to +0.37. On S5X paired items the Qwen3-14B strict +.69 [.60, .78] becomes broad +.23 [.14, .32]; the keyword counter gives strict +.06 [-.02, .14]; RefusEU S5 broad is -.04. The English edit mostly CONVERTS ENGLISH REFUSALS INTO PARTIAL REPLIES (PARTIAL = .548 of gemma_edit EN outputs). Judge agreement within EDITED checkpoints is materially lower than pooled: exp4 .779 [.678, .861] vs .913 pooled, exp8 .769 / .737, exp10 0.86 SL but 0.54 EN, exp12 0.683. 19 of 99 behavioural claims are JUDGE_SENSITIVE. The audit found 8 mismatches, 12 misdescribed and 6 untraceable numbers in 167 checked (5.5%), and two sign-reversed conclusions.

  === THE CLAIMS TO TEST IN ITERATION 4 (each positive by design, each with a falsifier) ===

  C1 - THE WRITE-MASS OVERLAP LAW, AND ITS PRACTITIONER INSTRUMENT (the deepening of P-1 and P-2, built so it must beat the baseline that beat us). Define, per model m and language L, the CAUSAL WRITE PROFILE e_{m,L}(h): the DEV-measured drop in judged harmful refusal from a SINGLE-SITE ablation of d_EN(h) at layer h, one layer at a time, measured on S3 DEV items only. Define, for any Heretic-family weight edit, its per-layer removal-energy profile g(h) (closed form, already stored per cell in art_ex4hbgThhJaL results/cells/ and art_xLy2vVlI7OEL). The OVERLAP is O_{m,L}(edit) = sum_h e_{m,L}(h) g(h) / sqrt(sum_h g(h)^2), i.e. an energy-normalised alignment between WHERE the edit removes and WHERE that language's refusal is causally written. PREDICTION: O predicts the residual judged refusal of held-out matched-energy cells at Spearman >= 0.6 per language, adds dR2 >= 0.10 over log-energy + layer count + depth span + EN/SL direction cosine, and BEATS OR TIES BOTH CHEAP BASELINES from D-3 on the same held-out cells (single-site transfer rate at the frozen site; unedited baseline refusal), with a paired item-bootstrap CI on the difference. The mechanism that makes this a designed positive rather than a hunch: the winning baseline IS the scalar special case of O (a one-layer profile), so a profile-valued generalisation of it should dominate it; and O is defined in the space where the edits actually act (weights), which is where the activation-space index failed. SECONDARY, and the part that would change what a practitioner does: the per-language argmax of e_{m,L}(h) recovered on DEV must name, out of sample, the band whose matched-energy cell wins on held-out harm categories - 13-24 in Gemma, 25-36 in GaMS3 - i.e. the instrument must reproduce the model-specific placement difference that the iteration-3 draft wrongly denied. FALSIFIER: O adds dR2 < 0.05, or fails to beat either cheap baseline with a CI excluding zero, or the DEV argmax does not name the winning band in at least one model. If it fires, the run's reported instrument becomes the BOUNDED NEGATIVE, stated positively: no geometric or depth measurement we or the literature can name beats the unedited model's own refusal rate and a single-site ablation probe at predicting where a weight edit will fail cross-lingually - use those two, they cost one forward pass each.

  C2 - THE SELECTION BLINDNESS IS A PROPERTY OF THE METRIC FAMILY, NOT OF ONE RUN (the extension of P-3, at near-zero GPU cost). Replay the distilled partial-aware scorer over the GaMS3 116-trial journal and its stored in-loop generations [art_vzhOPupFwE4M journals, art_KFZCxJcrr84K panel], and over the community bf16 reference's trials where available. Define and report the transferable statistic: the GRADIENT-BLIND FRACTION - the share of the optimiser's own candidate population over which the objective's value spans less than its own measurement noise while judged refusal spans the full range (Gemma: the counter never leaves 72-100/100 while the judge spans 7-98/100). PREDICTION: the blind fraction is large in Gemma and materially smaller in GaMS3, and it PREDICTS which of the two searches terminated on its fallback rule with an under-dosed kernel - i.e. the miscalibration, not the architecture, is what made the two Heretic runs land in different places. This is the second candidate explanation of the iteration-1 dissociation and it is measurable from files already on disk. FALSIFIER: the blind fraction is equally large in GaMS3, whose search nonetheless reached 16/100 and transferred - in which case the blindness is real but does not explain the dissociation, and C1's placement account carries it alone.

  C3 - PARTIAL COMPLIANCE IS THE BEHAVIOURAL PRODUCT OF AN UNDER-DOSED, MIS-PLACED EDIT, AND IT IS WHERE THE LANGUAGE ASYMMETRY LIVES (the deepening of D-4, computed on ~51,000 already-judged generations at zero GPU cost). Across the dose ladder and the coverage x strength cells already generated [art_ex4hbgThhJaL 27,784; art_xLy2vVlI7OEL 10,690; art_0XmNBGkzsJc_ 3,680; art_kfCCWf7o8eJ9 9,199], model the 4-way class as an ordered transition REFUSED -> PARTIAL -> COMPLIED against dose and overlap. PREDICTION: the PARTIAL share is single-peaked in dose and peaks at a HIGHER dose in Slovene than in English, so that at the dose an English-scored optimiser stops at, English has passed through PARTIAL into COMPLIED while Slovene is still inside it; the strict-vs-broad gap range (+.06 to +.69) is then an exact consequence of where each language sits on that curve. This is what makes the judge-definition range a FINDING rather than a caveat. Report, per cell and per language and as the user explicitly asked: official RefusEU guard ASR separately from refusal, PARTIAL as its own column, INVALID/empty/truncated never folded into either, and GlotLID language consistency. FALSIFIER: PARTIAL shares are flat in dose or the two languages' peaks coincide - then the gap range is judge noise, reported as such.

  C4 - POSITIONING, WHICH IS WHAT MAKES THIS PUBLISHABLE RATHER THAN A TABLE. For the placement positive the nearest neighbours are the work on selecting intervention sites by their CAUSAL effect rather than their probe quality ("Read-Best Is Not Steer-Best", 2609.22135; Cross-Architecture Steering Transfer, 2608.05164) and on refusal being distributed across depth (Arditi et al. 2024; Wang et al. 2025, 2505.17306). Quote what each establishes and state in one sentence what this run adds - a LANGUAGE-CONDITIONED placement contrast on two siblings at MATCHED total edit size and matched layer count, with the effective band differing by checkpoint - and where it stops: two checkpoints, one architecture, one non-English language for the matched panels, and a companion experiment showing the activation-space version of the measurement does not generalise. Carry the audit pod's NOT VERIFIED flag on 2607.02714's "2-3 middle layers" claim verbatim. Give the negative the same treatment: an activation-space depth measurement failing to predict weight-edit outcomes while two trivial baselines succeed is the more transferable result, and no neighbour currently states it.

  === EXPERIMENTS FOR ITERATION 4 (ordered; X-1 and X-2 are the core, X-3 and X-4 are nearly free) ===

  X-1 THE OVERLAP INSTRUMENT: SCREEN AND HELD-OUT CONFIRMATION (C1). SCREEN on evidence already on disk: fit O on the 122 Gemma cells and 57 GaMS3 cells with their stored per-layer energy profiles and judged residuals (O was never fitted on these, so they are a legitimate screen, and they are declared as such). FREEZE the profiles e_{m,L}(h), the formula and the predictions, hashed, before generating anything. CONFIRM on evidence the screen never touched: ~20 new matched-energy cells per model chosen to span high and low O at IDENTICAL energy and identical layer count, evaluated on held-out S4 harm categories and the S5X verified pairs, plus the two baselines computed on the same cells, plus layer-matched random and energy-matched PC controls, plus a no-op. Carry O and both baselines to Qwen3-8B and, under the frozen eligibility gate, one further eligible family, in EN/SL/DE/LT, reusing art_kfCCWf7o8eJ9's harness. Budget ~4-6 GPU-h per model.

  X-2 THE GRADIENT-BLIND FRACTION ACROSS TWO SEARCHES (C2). Replay-only, no new search: apply the certified scorer from art_0XmNBGkzsJc_ to GaMS3's 116-trial journal and stored generations; compute the blind fraction, the MAE per 100, and the kappa for each model; recompute each model's selection under the corrected score post hoc; report which rule branch fires. If a second Heretic search is affordable at all, spend it on GaMS3 with the corrected scorer and one seed. ~0-3 GPU-h.

  X-3 THE PARTIAL TRANSITION CURVES (C3). Pure re-analysis of ~51,000 existing judged generations, plus the guard-pipeline ASR pass on any cell that never had one. Zero new generation except the ASR re-scoring. ~0-1 GPU-h.

  X-4 JUDGE REPAIR, WHICH IS NOW BLOCKING FOR EVERY NEW NUMBER. Two agreement gates were missed this round (exp10 English kappa 0.54 within edited arms; exp12 0.683 overall). Buy a stratified gpt-4.1 calibration subsample of ~600-900 items drawn from THIS round's edited cells, in both languages, and re-certify the workhorse judge to kappa >= 0.80 refused-vs-not WITHIN edited cells before any confirmatory number is read; where it cannot be reached, report Rogan-Gladen-corrected rates beside raw ones and mark the affected claims JUDGE_SENSITIVE. The shared OpenRouter key is used for this calibration and for nothing else (~$1-2 of the cap). Also: one bf16 rebuild of a single Gemma cell, so the NF4-vs-bf16 confound against the community reference is broken once.

  X-5 OPTIONAL, ONLY IF X-1 AND X-2 LAND EARLY: a second optimiser seed for the GaMS3 corrected run, and the native-speaker review packets if a qualified reviewer is reachable; otherwise one consolidated PENDING list.

  === BLOCKING REPORT REPAIRS (reporting fixes, not experiments; the reviewer's audit is accepted in full and NONE of these may be deferred again) ===
  (1) Rewrite the experiment-9 band paragraph, experiment-10's nested-R2 interpretation and the "firm positive" as MODEL-SPECIFIC claims; quote the Slovene band-mass coefficient +0.156 [-0.240, 0.529] and say it is not significant, so the support is the rank statistic and the matched-energy/matched-count contrasts; paste GaMS3's band rows (SL 1-12 .93, 13-24 .24, 25-36 .02, 37-48 .85) beside Gemma's per-set minima; state that the effective region DIFFERS and that this is a candidate explanation of the iteration-1 dissociation; fix the two mis-stated coverage-set memberships and add the half-coverage set with its own outcome.
  (2) Replace the experiment-11 interpretation with the artifact's own README section 4 wording: the mechanism is DOSE, not placement; at matched divergence the corrected edit is strictly worse and the cheaper ladder arm reaches a ZERO gap; move "corrected objective" into the FALSIFIED column; add the miscalibration TABLE with kappas (+0.196 vs +0.924 in-domain, certification 0.858 [0.820, 0.888] on held-out replayed trials vs keyword 0.143), the per-100 errors (30.6 vs 2.1) and the scorer-vs-judge range (counter 72-100 while judged 7-98); correct the trial-level count against results/miscalibration_table.csv (63, not 10).
  (3) Add in-place "[Correction, iter 4]" notes to the five unchanged iteration-2 interpretations: GaMS3 is RE-ENCODING, not information destruction (refit 0.993/0.987, complement 0.985/0.955); Gemma's frozen-axis separation DOES halve in both languages from a mid-depth layer with differing late-layer rotation (cos 0.53 EN vs 0.83 SL), so "barely moved" is wrong; label the dose table MARKER-BASED and add the judged columns, because the marker rule undercounts Gemma's English refusals by more than half; split the repair table BY JUDGE with a per-judge baseline row; state the reverse-direction sign flip (-0.124) beside the forward Gap_K rather than calling it stable.
  (4) Paste the iteration-1 section back VERBATIM from iter_1/gen_report_text/gen_report_text/report.md with its Strategy paragraph, same-edit response-surface table, incremental-R2 result, swap statistics table with paired tests and KL ratio, source-by-evaluation-language transfer matrix, decision-margin decomposition, exploratory double dissociation, the four labelled dead ends, the published-baseline figure and iteration 1's own "What we have learned", keeping the iteration-3 correction notes inserted in place. Restore the deleted iteration-2 summary under a heading "Superseded by iteration 3", with the retracted training-stage sentences MARKED retracted and the reason given, rather than deleted.
  (5) Add a "What bounds this" block to every iteration-3 section with that artifact's own caveats and numbers: exp9's index inside the permutation null [-4, +4] with the powered statistic being the prefix-curve separation +0.080 [0.021, 0.136] p 0.0065, necessary-not-sufficient (97% vs 47%), the held-out-category confirmation rows, the matched random/PC control rows and the Holm adjustment; exp10's 0.54 English judge agreement within edited arms, the ">48 in both languages" usable index, the two unreported predictions and the operator-vs-depth finding; exp12's 0.683 judge gate miss, the Rogan-Gladen re-run, the baseline-comparison table and the post-freeze patch note.
  (6) Put the producing FILE PATH next to every table caption and every non-obvious inline number, and either run the audit pod's recompute path over the iteration-3 sections or state in the iteration-3 opening that those numbers are not independently re-derived and that the audited mismatch rate elsewhere was 5.5%. Preference: run the audit over iteration 3.
  (7) Add the scope items the user asked for and the draft still omits: an attack-success (official guard pipeline) table for ALL checkpoints in both languages, noting the iteration-2 cell where ASR moves opposite to the refusal gap (gemma_edit .738 EN vs .103 SL); per-cell language-consistency and validity/truncation columns; the item-level flip analysis that speaks to "information loss vs changed mapping", with its statistic and which reading it supports (the mechanism paragraph currently draws the opposite conclusion); and ONE consolidated "Pending human review" list naming all five packets and their paths.
  (8) Restate the surviving behavioural claim as bounded by achieved optimisation strength (D-2 above), citing the dose ladder, the community reference, the c = 1.5 kernel result and the corrected swap row; strike "robust across judges and datasets" or qualify it to the specific checkpoint and judge range.
  (9) State both depth-index definitions and their units once, say they are NOT the same instrument, and add experiment 12's post-hoc decomposition (within-anchor rho +0.678; zero variance in Qwen3; pooled within-model-centred +0.458).
  (10) Fix the three counts: the dead-end ledger says "twenty" and lists sixteen; experiment 12 has SEVEN eligible rows (x3 cells = the 21 rows the statistic uses), not eight; reconcile the dataset section's translation-fallback count with the screen's and add a one-line per-set translation-provenance note. Add the C4 novelty paragraphs with the NOT VERIFIED flag carried verbatim.

  === SUCCESS AND FALSIFICATION ===
  CONFIRM if, on cells the fit never saw: (C1) O reaches Spearman >= 0.6 against residual judged refusal in both languages, adds dR2 >= 0.10 over log-energy + count + span + cosine, and beats both cheap baselines with a paired-bootstrap CI excluding zero, while matched random and PC controls stay null; AND the DEV argmax of e_{m,L}(h) names the winning band out of sample in both models. AND (C2) the gradient-blind fraction differs between the two searches in the direction that predicts which one terminated under-dosed.
  PARTIAL: O ties the single-site baseline but both beat energy, count and cosine - the paper's instrument is then the single-site probe, presented as the cheap practitioner test, with O as the mechanistic account of why it works.
  FALSIFY: O adds < 0.05 and loses to the baselines again - the run reports the bounded negative of D-3 as its headline instrument result (no depth or direction geometry beats two one-forward-pass baselines), keeps P-1 as the mechanism claim it is, and keeps P-3 as the practitioner result.
  CONSTRAINTS THAT TRAVEL WITH EVERY NUMBER: n = 2 sibling checkpoints plus 1-2 outside families; 1-2 optimiser seeds; NF4 unless the single bf16 rebuild says otherwise; Slovene is machine-translated with native review PENDING; no attribution to any training stage; every headline number recomputed from saved results by an independent path; screen and confirmation kept apart with primary outcomes frozen and hashed before FINAL evaluation; every judged number reported with its judge, its within-edited kappa and its strict/broad definition.
motivation: >-
  National-language models are routinely abliterated with English-centric tools. Heretic's objective is English keywords plus
  English KL, and its default projection protects the ENGLISH harmless mean. The refusal-direction literature supports transfer
  only for the edit's TARGET. Refusal directions are near-universal across languages (Wang et al. 2025, 2505.17306), and English
  refusal steering transfers (BabelSteering, 2608.16577). Nothing tells a practitioner whether the edit's COLLATERAL in the
  unmonitored language is visible to the English objective, and that collateral decides whether an edited Slovene model is
  still usable. The question now matters beyond hobbyist uncensoring. Yoon, Park and Ritter (EMNLP 2026, 2608.22490) measure
  that non-English users pay a larger 'Safety Cost' by using ABLITERATED models (including gemma-3-27b-it) as the unaligned
  counterfactual in every language, and they acknowledge ablation imperfections only generically. If abliteration's own collateral
  is language-dependent and invisible to its English objective, such measurements carry a language-dependent bias. Our Gap
  and exposure quantify exactly that bias. The broad phenomenon that English proxies under-report non-English damage is KNOWN
  for compression (Marchisio et al. 2024, 2407.03211: 1.7% automatic vs 16% human-rated drop in Japanese under quantization).
  So is the principle that the calibration language matters because activation statistics decide which weights are damaged
  (Kurz et al., TACL, 2408.14398; Chimoto et al., EACL 2026, 2601.18306; Wanda- and AWQ-style activation-aware importance).
  We claim neither. We claim three things. (i) A placebo-controlled surrogacy decomposition inside an abliteration optimizer's
  own candidate population. It separates 'unseen because Slovene' from noise, learner and item artefacts, and separates intrinsic
  (model x edit family) from achieved (one run's selection). The reviewer found no prior instance. (ii) A realized-edit exposure
  quantity, logged exactly from Heretic's LoRA outputs under its real defaults (projected, norm-preserving, rank-3). It is
  pitted against the static geometric accounts the field uses: EN/SL direction cosine, SAE safety-language entanglement (2608.29936),
  and LSAR-style language subspaces. This establishes where familiar geometry stops predicting behaviour, which the user named
  as valuable. (iii) A matched-efficacy causal test that names the carrier, including the one-line practitioner fix: a bilingual
  projection reference. The practitioner bar is higher now. Heretic master supports per-config datasets for harmful/harmless
  pairs in other languages (PR #445, 2026-09-05) and an lm-eval benchmark scorer (PR #444). So a bilingual Heretic run is
  cheap, and our corollary must beat it at equal budget and equal English refusal. The whole discovery arm serves the requested
  core. It explains each checkpoint's Slovene safety-utility trade-off, and it operationalizes the user's instruction to separate
  achieved optimization from intrinsic model properties. Caveat: GaMS3 had about 134B continual-pretraining tokens (SL/EN/HBS)
  and a chat SFT of about 20k English plus 80k machine-translated Slovene responses. Every model difference is descriptive,
  and every main claim is measured WITHIN a model.
assumptions:
- >-
  Both originals load in bf16 on one >=40 GB GPU with their official chat templates, one model at a time (disk may hold only
  one ~24 GB model). Weights are fetched, used and released sequentially, with hashes recorded. GaMS3 shares the Gemma 3 architecture,
  tokenizer and 48-layer indexing, so one pinned Heretic commit (3521f8648a0dccf6e12a92666862632235fac7e6) and one layer map
  serve both. google/gemma-3-12b-it is licence-gated; without an accepted token, a byte-identical mirror is used after its
  SHA256 is checked against the official file list, and the substitution is flagged. If no GPU of this class exists, the core
  is still run on the available hardware, and the panel shrinks with that stated. The model is never silently swapped.
- >-
  Throughput: traits are teacher-forced (no generation), about 2.5k short sequences per edit and language pair, so about 45-80
  s per edit on an A100-class GPU. 250 random edits take about 4-6 GPU-h per model. Exposure costs nothing extra, because
  the LoRA adapter-output norms are hooked during the same passes. A Stage-A timing plus a power simulation on a 40-edit pilot
  freezes the panel size. The floor is 150 non-collapsed edits; below it, C2 is exploratory. The random edits span English
  refusal from original to near 0 and span damage. Otherwise extra draws are taken, and collapsed edits (harmless NLL rise
  > 1 nat/token) are analysed separately, never dropped.
- >-
  Traits are reliable (split-half, Spearman-Brown >= 0.6 across edits). Refusal propensity tracks generated refusal (Spearman
  >= 0.85 against judge-scored greedy generations on every 4th edit, per language). A trait failing either gate leaves the
  confirmatory family. The language-choice trait Lambda is NOT in the Gap family, because English outputs essentially never
  drift into Slovene, which makes its placebo degenerate.
- >-
  Parallel EN/SL items exist or can be built faithfully: FLORES-200 eng_Latn/slv_Latn, and Slovenian LLM Eval items matched
  to the English tasks after a correspondence check. It has only a test split, so a frozen DEV carve-out is excluded from
  FINAL. Harmful/harmless DEV prompts are machine-translated with back-translation checks, and native review is marked PENDING.
  Exposure differs between languages beyond the language-label-shuffled null in at least one model; otherwise the causal arms
  (x) and (e) are declared untestable for that model in Stage A, before any intervention is run.
investigation_approach: >-
  EXECUTION PRIORITY AND CUT ORDER (frozen in protocol.yaml). The core C1 (four checkpoints x two languages, full behaviour
  and utility protocol, mechanistic core) runs to completion before P2, the causal arms or the bands start. The order is:
  C1 -> C2 (P1 Gap/B) -> exposure regression (no new edits) -> C3 arms (e) and (x) with controls -> C4 forecast -> the requested
  2x2 source-language x evaluation-language transfer matrix -> bilingual-Heretic corollary -> arm (b) -> P2 bands -> drift
  link -> row_normalization = 'none' sensitivity. The Buyse-Molenberghs model is DROPPED (redundant with noise-ceiling normalization
  plus SIMEX). The minimum viable paper is C1 + C2: the four-checkpoint EN/SL trade-offs plus 'what English selection can
  and cannot see'. STEP 0 - PINS AND FREEZE. protocol.yaml is hashed before any FINAL call and records: model revisions (cjvt/GaMS3-12B-Instruct,
  cjvt/GaMS3-12B, google/gemma-3-12b-it); the Heretic SHA 3521f864, which includes the #423 response-prefix detection change
  flagged as affecting reproducibility; orthogonalize_direction = true, row_normalization = 'full', full_normalization_lora_rank
  = 3, winsorization_quantile = 1.0, n_trials = 200, n_startup_trials = 60, seed and resolved dtype; the Optuna storage hash;
  and transformers, peft, optuna, lm-evaluation-harness, RefusEU, slovenian-llm-eval and FLORES revisions. One system-prompt
  policy applies (Heretic's default, folded into the first user turn by the Gemma 3 template); rendered templates are saved
  and diffed. Greedy decoding with 256 new tokens for FINAL behaviour. SPLITS, grouped by semantic source (translations, paraphrases
  and harmful/harmless twins follow their source): S1 Heretic construction/optimization (mlabonne harmful_behaviors / harmless_alpaca,
  as in Heretic); S2 mechanistic DEV (Semantic-Harmful/Harmless and SL translations, used only for directions, subspaces and
  layer choice, since they may overlap S1 sources); S3 trait DEV (128 harmful + 128 harmless parallel EN/SL items from a source
  disjoint from S1/S4/S5, 200 FLORES dev pairs, 50 MC items per task per language from the DEV carve-out, split A/B by semantic
  ID); S4 mechanistic HELD-OUT (about 200 new EN/SL pairs, with held-out harm categories and an independent StrongREJECT-derived
  source); S5 FINAL behaviour (a frozen stratified RefusEU sample, EN and SL); S6 over-refusal (XSTest-safe EN plus a translated
  SL version); S7 FINAL utility (the six tasks in both languages minus the carve-out, plus FLORES devtest). Overlap is audited
  by source ID and LaBSE near-duplicates (cos > 0.85). RefusEU EN/SL row correspondence is verified by back-translation similarity,
  and paired cross-language claims use verified pairs only. STEP 1 - FEASIBILITY (DEV only): template and tokenizer checks,
  20 prompts per language for coherence, baseline refusal and hidden-state extraction, timing, and the 40-edit pilot. The
  pilot supplies: reliabilities; refusal-propensity validity; trait spreads; exposure versus its language-label-shuffled null;
  per-layer ||P_lang v||^2 versus the permutation null and k/d; PI coverage on pilot TPE trials; the power simulation; and
  the frozen TOST margin, delta = min(0.10, the Gap at which bilingual reselection changes the selected trial in >50% of pilot
  simulations). STEP 2 - FOUR CORE CHECKPOINTS. One Heretic run per original with identical defaults, seed and S1 data. The
  selection rule is declared in advance: the lowest KL among trials with <= 10/100 keyword refusals; fallback 1, the fewest
  refusals with KL <= 1.0; fallback 2, the nearest Pareto point to (0, 0). The Optuna study, the parameters and the LoRA/merged-weight
  hashes are saved. The same English-derived edit is evaluated in both languages. p-e-w/gemma-3-12b-it-heretic is a sanity
  reference only. A second-seed run per model is kept separate from the core. STEP 3 - CORE BEHAVIOUR AND UTILITY (FINAL,
  touched once). Scored outcomes: ASR under the RefusEU rubric; refusal; partial, ambiguous, irrelevant, malformed and empty
  outputs as explicit categories, never folded into compliance or refusal; response-language consistency (line-level GlotLID);
  repetition; and over-refusal on S6. The primary judge is frozen and blind to model identity. A second judge from another
  family scores a stratified 400-item sample, with kappa reported. A blinded EN/SL human-review packet is prepared and marked
  PENDING. Utility covers ARC-C, BoolQ, HellaSwag, OBQA, PIQA and Winogrande in EN and the Slovenian LLM Eval versions via
  the pinned harness, per task and macro-averaged, as original-to-edited change within each language. Harmless divergence
  is 1-token and 32-token KL on held-out prompts. STEP 4 - MECHANISTIC CORE. Positions: the final post-instruction template
  tokens (identical strings in both languages) plus mean content tokens as a control. Per layer, model and language: the harmful-minus-harmless
  direction; EN/SL cosine against a split-half ceiling; CV probe AUROC on S4; cross-language probe transfer; and the original's
  frozen probe versus a probe refitted after the edit (drift versus information loss). Controls: topic- and length-matched
  twins, the language-identity direction, and pre-response positions only. On S5, item-level logistic regression of post-edit
  refusal on the frozen-probe score, per language, separates a changed mapping (preserved slope, shifted intercept) from lost
  evidence (collapsed slope). The layer-wise language map uses CKA and translation retrieval on S2 pairs. Base-model diagnostic
  for cjvt/GaMS3-12B: separability and the language map under base formatting, plus a small EN/SL continuation sample. Its
  raw refusal is never compared with the chat models. STEP 5 - DISCOVERY PANEL (DEV only). P1 is the 60 startup trials plus
  >= 190 draws from Heretic's priors. direction_index is encoded as missing when direction_scope = per layer. The 140 TPE
  trials are never fitted; they are out-of-sample tests. TRAITS per edit, language and half: R, refusal-prefix log-odds at
  the first response token (prefixes mined per language); K, log mean per-token KL over the original's 32-token harmless continuation;
  N, FLORES NLL change; M, length-normalized gold-minus-best-distractor margin; Lambda, the language-choice margin (descriptive
  and B-only). EXPOSURE per edit and language, logged in the same passes: the sum over edited modules of ||dW_m x_m||^2 on
  the harmless response tokens, per token, plus a per-sentence sum as a sensitivity check, since Slovene uses more tokens.
  It is also split into a mean term and a variance term using the original model's module outputs. ANALYSIS: Gap_t with one
  frozen GBT learner (ridge-on-splines as a sensitivity check); halves swapped and averaged; the reverse SL_A -> EN_B direction;
  raw R2 reported beside R2*; ceilings with item-bootstrap CIs; and SIMEX with the measured reliabilities. B_t is inferred
  by a two-level bootstrap (edits x semantic items resampled jointly across language and half), with a secondary permutation
  of parameter rows WITHIN strata of EN_A traits (a conditional null, not plain row shuffling). Stability: Gap and B on two
  disjoint halves of P1. NAMED TEST OF THE FRAGILITY RIVAL (alternate 4): an item x edit mixed model, d_ie ~ s(EN edit traits_e)
  x s(baseline margin_i) + (1|item) + (1|edit) + language, plus a MARGIN-MATCHED Gap recomputed after reweighting SL and EN
  items to equal baseline-margin distributions. The rival wins if the margin-matched Gap lies inside the TOST margin. STEP
  6 - CARRIER TESTS (separate from the core checkpoints). (6a) EXPOSURE REGRESSION on P1: the Slovene-specific residual regressed
  on D, compared against b0 (identity transfer), b1 (the kernel-weighted per-layer EN/SL cosine profile x EN effect), b2 (language-identity
  entanglement, the 2608.29936 analogue), b3 (band kernel masses) and Omega (the realized-dW energy share in the LSAR-style
  k-dim language subspace: ||P_lang dW_m||_F^2 / ||dW_m||_F^2, weighted by ||dW_m||_F). (6b) MATCHED-EFFICACY ARMS on the
  two core edits, the two second-seed edits and 10 P1 edits stratified by D. Strength is rescaled on DEV by 3-point interpolation
  of EN refusal propensity, within Heretic's max_weight range. Arms: (0) no-op; (a) as is; (e) bilingual reference; (x) contrastive
  second-moment projection (top-k eigenvectors of E_SL[oo^T] - E_EN[oo^T] at the weighted layers); (b) LSAR-style subspace;
  (c) random subspaces from the top-100 harmless-PC span, rejection-sampled so that ||P v||^2 matches (x) and (b) within 10%
  per weighted layer, plus one unconstrained random arm; (p) PLANTED POSITIVE CONTROL: v' = normalize(v + alpha u), where
  u is the top differential-exposure direction and alpha doubles D, then orthogonalized, to show the test can recover a known
  carrier. Composition order: language/reference projection, then Heretic's harmless-mean projection, then normalization,
  then the kernel with row normalization. Outcomes are measured on B-half traits and S4: SL and EN refusal reduction and Slovene-specific
  collateral. A power simulation from pilot variances fixes the minimum detectable relative cut; if it exceeds 30%, C3 becomes
  a directional effect-size CI, labelled exploratory. (6c) The requested 2x2 transfer matrix (EN- and SL-derived directions
  as activation ablation or addition, each evaluated in EN and SL, with dose-response, no-op and norm-matched random controls
  and benign utility checks) is run in each original. (6d) PRACTITIONER COROLLARY, at equal EN refusal and an equal 200-trial
  budget: a bilingual Heretic run (EN+SL S1 datasets via per-config datasets, a Slovene refusal keyword list, bilingual KL),
  compared with post-hoc bilingual reselection among the existing trials and with arm (e) applied to the core edit. (6e) If
  time remains: P2 (about 80 Sobol edits covering all depths, with a VIF gate) for band slopes; the drift link (SL-minus-EN
  representation drift in exposure coordinates versus frozen-probe coordinates on 40 edits); and a 40-edit row_normalization
  = 'none' panel to check the conclusions do not hinge on norm preservation. STEP 7 - STATISTICS. Confirmatory families are
  frozen before FINAL. C1: original-to-edited change per model x language for ASR, refusal, invalid rate, over-refusal, utility
  macro and harmless KL, with paired item-level effects, 95% CIs from a cluster bootstrap over semantic items (translations
  clustered), and McNemar tests. C2: Gap and B for K, N and M per model (6 tests, Holm), plus the refusal TOST. C3: exposure
  delta-R2 over the best static baseline, and the (e) versus (c) and (x) versus (c) contrasts. C4: forecast checks. C4 PROTOCOL:
  the forecast is fitted on P1 in DEV-trait space; the target is the SL excess in trait units (secondary: log(SL + eps) -
  log(EN + eps), eps fixed on DEV). Before use, PI coverage is checked on the last 50 TPE trials, the ones nearest the selected
  region; it must reach >= 85% or be conformalized. Each target edit gets a support diagnostic (kNN distance in parameter
  and EN-trait space versus the P1 distribution). If an edit is out of support, a GP forecaster becomes primary and about
  30 local draws around the TPE region are added and labelled as augmentation. FINAL replication measures the same trait definitions
  on FINAL items for the targets and a 20-edit bridge subset (DEV-to-FINAL calibration); lm-eval accuracy is descriptive.
  Four targets (two per model) are a calibration check with no power claim. Layers, k, bands and learner settings are chosen
  on DEV and labelled exploratory. Two models are two units. Prompt-level CIs are never presented as optimization-run variance;
  the panel and the seed reruns address that. BUDGET: two core runs of about 2-3 GPU-h each; P1 about 4-6 GPU-h per model;
  arms about 2 GPU-h per model; the bilingual run about 3 GPU-h per model. API spend (translation plus 2 judges) is about
  $5-7 of the $10 cap, tracked per call.
success_criteria: >-
  GATES (DEV, before any confirmatory test): trait reliability >= 0.6; refusal-propensity validity >= 0.85; >= 150 non-collapsed
  P1 edits; power-simulated MDE for Gap <= 0.15. Otherwise C2 is exploratory. CORE-STUDY SANITY, relative to each original:
  EN judge refusal reduced >= 50% (relative); SL response-language consistency drop <= 3 points; utility macro drop <= 5 points
  per language. A checkpoint that fails is reported as degraded, never as successful suppression, and incoherent or empty
  outputs never count as compliance or refusal. CONFIRM the main claim if all four hold. (a) REFUSAL VISIBLE: the 90% CI of
  Gap_R lies inside +/-delta (frozen, <= 0.10) in both models. (b) DAMAGE PARTLY BLIND: for >= 1 of K/N/M in >= 1 model, Gap
  >= max(delta, MDE) with a Holm-adjusted 95% CI lower bound > 0, and the B bootstrap CI excludes 0 (stratified-permutation
  p < 0.05 as a secondary check). The sign must hold on both disjoint P1 halves and under SIMEX, and the MARGIN-MATCHED Gap
  must stay outside the TOST margin, so the fragility rival does not absorb it. (c) CARRIER: D has a positive coefficient
  whose CI excludes 0 and adds delta-R2 >= 0.05 over b1, b2, b3 and Omega combined, while none of those adds >= 0.05 over
  D. At matched EN refusal reduction (within +/-10% relative), arm (e) or (x) keeps SL refusal reduction within +/-10% (relative)
  of arm (a) and cuts the Slovene-specific collateral with a CI that excludes the matched-random (c) cut. The planted control
  (p) must be detected; if it is not, C3 is declared uninformative, not negative. The pre-registered size target is a >= 30%
  relative cut when the MDE allows; otherwise a directional CI. (d) CORE TIE-IN: PI coverage on held-out TPE trials is >=
  85%, and for >= 3 of the 4 checkpoint targets the SL excess falls outside the English-only forecast PI and inside the PI
  once D is added. The remainder is reported as the achieved component. PARTIAL: (a) and (b) hold but (c) fails, i.e. the
  blind damage is real but carried by neither exposure nor static geometry. Reported as the boundary, with the fragility mixed
  model and the band slopes examined. Alternatively, (c) holds for exposure but the static baselines tie it, i.e. geometry
  is enough; reported as such. FALSIFY the blind-damage claim if, for every damage trait in both models, the Gap 95% CI upper
  bound is below delta (or the TOST shows equivalence to 0). English outcomes are then an adequate surrogate, which becomes
  the headline; (d) becomes 'the English-only forecast already captures each checkpoint's Slovene trade-off', and the proxy
  use in 2608.22490 gets a positive validity check. FALSIFY the carrier claim if the arms do not differ from their overlap-matched
  random controls while (p) is detected, or if no strength achieves matched EN efficacy. FALSIFY (b) in favour of alternate
  4 if the margin-matched Gap falls inside the TOST margin. PRACTITIONER COROLLARY (descriptive, equal budget): report whether
  the bilingual Heretic run, post-hoc bilingual reselection or arm (e) gives the lowest SL collateral at equal EN refusal.
related_works:
- >-
  Heretic (p-e-w, pinned SHA 3521f864, 2026-09-05; main.py, model.py and config.default.toml checked): TPE over per-component
  ablation-kernel parameters with 60 random startup trials, minimizing English keyword refusals and English first-token KL.
  Defaults: orthogonalize_direction = true (v projected off the normalized ENGLISH harmless mean per layer) and row_normalization
  = 'full' (a norm-preserving delta approximated by a rank-3 svd_lowrank LoRA). PR #445 adds per-config datasets for multilingual
  harmful/harmless pairs, and PR #444 adds an lm-eval benchmark scorer. Heretic reports only the English Pareto front. We
  re-score its random edits bilingually with a same-language placebo, log exposure from its realized LoRA, and use a bilingual
  Heretic run as the practitioner baseline to beat.
- >-
  grimjim, 'Projected Abliteration' and 'Norm-Preserving Biprojected Abliteration' (HF blog, 2025): the orthogonalization
  of the ablated direction against the harmless mean that Heretic implements. Our arm (e) changes only the reference of this
  existing operator (EN -> EN+SL span). The novelty is the matched-efficacy test of WHICH reference or subspace carries collateral
  in the unmonitored language, not the operator.
- >-
  Yoon, Park & Ritter 2026 (2608.22490, EMNLP): non-English users bear a higher 'Safety Cost'. It is measured by pairwise
  comparison of aligned models with ABLITERATED counterparts (gemma-3-27b-it, Qwen, Llama), and ablation imperfection is acknowledged
  only generically. We test the assumption this design relies on: that abliteration's collateral is language-neutral, or at
  least visible in English. Our Gap and exposure measure the bias that would enter such cross-language cost estimates.
- >-
  Marchisio et al. 2024 (2407.03211): automatic English-centric metrics under-report non-English quantization damage. Kurz
  et al. (2408.14398, TACL) and Chimoto et al. (2601.18306, EACL 2026): the calibration language matters for pruning and quantization,
  because activation statistics decide which weights are damaged (Wanda- and AWQ-style importance). These are the origin of
  the exposure principle. Our delta: a safety edit selected by an English objective, a placebo decomposition inside the optimizer's
  candidate population, and realized exposure tested causally against static geometry.
- >-
  Xie et al. (LSAR, 2401.05792; EMNLP 2022 line of work): SVD of language means yields a low-rank language-specific subspace
  that can be projected out. This is the origin of our arm (b) and of Omega. We do not claim the subspace; we test whether
  it CARRIES an edit's unmonitored-language collateral, against an exposure-based second-moment alternative (contrastive PCA,
  Abid et al. 2018, Nature Communications) and overlap-matched random subspaces.
- >-
  Upadhyaya & Sikdar 2026 (2608.29936): SAE safety-language entanglement predicts the language cost of ablating the top-k
  safety features at one layer, and is largely disentangled in Gemma. It is a static predictor of single interventions and
  is used as our baseline b2. Low entanglement does not imply low exposure; that is the boundary we test.
- >-
  Wang et al. 2025 (2505.17306), 'Refusal Direction is Universal Across Safety-Aligned Languages', and BabelSteering (2608.16577):
  the edit's TARGET transfers across languages, which our claim (1) expects to see as Gap_R = 0. Neither decomposes collateral
  by language or asks what an English objective misses.
- >-
  Cross-Architecture Steering Transfer (2608.05164) and 'Read-Best Is Not Steer-Best' (2609.22135): geometry and probe-best
  layers imperfectly predict causal effects. We locate that boundary for cross-LANGUAGE collateral within a model, with per-edit
  cosine profiles (b1) as the baseline to beat.
- >-
  'Steering the Language Axis' (2608.12334): a multi-dimensional, partly redundant language axis. 'Multilingual Steering by
  Design' (2605.23036): a priori layer choice for LANGUAGE steering. Both motivate k-dim language subspaces and a measured
  language map instead of an assumed English pivot (Wendler et al. 2024; Tang et al. 2024, 2402.16438, language-specific neurons
  at the depth extremes; 'Lingua Franca or Probing Artifact?', 2609.00155).
- >-
  Aziz, Hanif & Koto 2026 (2606.01196), 'Knowing without Acting' (2603.05773), 'Detection Is Cheap, Routing Is Learned' (2603.18280):
  detection and refusal routing come apart. Our frozen-versus-refitted probes and the item-level slope/intercept analysis
  are core checks. Separable harmfulness after editing is expected and is not claimed.
- >-
  Hawkins et al. 2026 (2606.28843): the safety effects of benign multilingual fine-tuning depend on fine-tuning x evaluation
  language. That is behavioural and concerns fine-tuning, not an English-selected weight edit, and it has no placebo decomposition
  or carrier test.
- >-
  Krasnodebska et al. 2026, RefusEU (2606.07535, NASK-PIB/RefusEU): multilingual refusal evaluation including Slovene, used
  for FINAL behaviour with EN/SL row correspondence verified. Abliteration-Eval (treadon/abliteration-eval) and Heyjab/Multilingual-Harmless-Harmful
  (a Heretic-tagged multilingual prompt set, no Slovene) show that community tooling is going multilingual, which raises the
  practical stakes.
- >-
  Fafula 2026 (2607.17427) and Young 2025 (2512.13655): abliteration off-target effects differ across model families, measured
  in English on single chosen edits. We measure off-target effects in the unmonitored language across an edit population,
  and separate intrinsic from achieved effects.
- >-
  Labunets 2026 (2608.25390): refusal stable rank and ease of ablation depend on refusal-training diversity. Relevant to the
  descriptive GaMS-versus-Gemma contrast and to alternate 1.
inspiration: >-
  Clinical surrogate-endpoint validation (Prentice 1989; Buyse & Molenberghs 2000): accept a cheap endpoint only if, across
  many trials, the effect on it predicts the effect on the true endpoint. Here each random edit is a trial, the English outcomes
  are the surrogate Heretic optimizes, and the Slovene outcomes are the true endpoint for Slovene users. A same-language placebo
  half gives the surrogate's ceiling. Pharmacokinetics supplied the carrier: side effects follow EXPOSURE (the drug concentration
  a tissue actually sees), not the drug's structural similarity to its target. The analogue of exposure is the energy the
  realized edit removes from each language's tokens, as opposed to cosine between directions. Pharmacology also supplies the
  causal design: compare side effects at matched on-target efficacy, not at matched dose, and include a planted positive control
  so a null is interpretable. Quantitative genetics (Lande's correlated response to selection) predicts that unselected traits
  outside the span of the selected ones move in ways selection cannot see. The optimizer's curse (Smith & Winkler 2006) prices
  the selected edit's excess. From compression, activation-aware importance (calibration-language effects) is the closest
  engineering precedent for exposure, cited as its origin.
terms:
- term: Abliteration / Heretic edit
  definition: >-
    Removing a refusal-associated direction v from attention-output and MLP down-projection weights, with a per-layer kernel
    tuned by TPE on English refusal and English KL. Under the pinned defaults, v is first projected off the English harmless-mean
    residual, and the update is norm-preserving and stored as a rank-3 LoRA delta dW.
- term: Random-edit panel (P1)
  definition: >-
    Heretic's 60 random startup trials plus >= 190 more draws from the same priors, each scored in EN and SL. It describes
    model x edit family x prior, not one optimization run.
- term: Placebo halves
  definition: >-
    Semantic items split into halves A and B, keeping each item's EN and SL versions together. English traits on A predict
    English traits on B (placebo) and Slovene traits on B (test).
- term: English surrogacy gap (Gap_t)
  definition: >-
    R2*(EN_A -> EN_B) - R2*(EN_A -> SL_B) for trait t, where R2* is cross-validated R2 over the target's split-half noise
    ceiling. Positive means Slovene variation across edits that English outcomes cannot see because it is Slovene.
- term: Blind share (B_t)
  definition: >-
    Partial R2 of the edit parameters beyond the EN_A traits when predicting SL_B, minus the same quantity for EN_B. Positive
    means the unseen Slovene variation is set by the edit, not by noise.
- term: Exposure and exposure differential (D)
  definition: >-
    Per language, the mean per-token squared norm of the realized edit's output, sum over edited modules of ||dW_m x_m||^2,
    on the original model's harmless response tokens. It is logged from the LoRA adapter outputs. D = log E_SL - log E_EN.
- term: Static geometric baselines
  definition: >-
    Input-independent predictors: the kernel-weighted EN/SL refusal-direction cosine profile (b1), language-identity entanglement
    (b2), band kernel masses (b3), and Omega, the realized dW's energy share inside an LSAR-style language subspace.
- term: Matched-efficacy arms
  definition: >-
    Variants of one edit, each rescaled so that English refusal propensity falls by the same amount: (e) bilingual projection
    reference; (x) contrastive second-moment projection; (b) language-mean subspace; (c) overlap-matched random subspace;
    (p) planted positive control; (0) no-op.
- term: Margin-matched Gap
  definition: >-
    Gap recomputed after reweighting SL and EN items to equal baseline first-token-margin distributions in the original model.
    It is the named test of the 'thinner Slovene margins' rival.
- term: Achieved vs intrinsic
  definition: >-
    Intrinsic: structure of the random-edit panel (model x edit family x prior). Achieved: a selected checkpoint's deviation
    beyond the panel forecast's interval (optimizer's curse).
summary: >-
  Heretic tunes refusal removal on English outcomes only. We re-score its random candidate edits in English and Slovene with
  an English placebo, to test whether Slovene refusal is visible to English while part of the Slovene collateral damage is
  systematically blind. We then test whether that blind part is carried by the energy the realized edit removes from Slovene
  tokens (exposure), rather than by static geometry such as direction cosine or a language subspace, using matched-efficacy
  projection arms with overlap-matched and planted controls. Finally we check whether exposure explains each core checkpoint's
  Slovene trade-off.
alternates:
- title: Slovene safety training keeps a Slovene refusal
  hypothesis: >-
    What English cannot see is REFUSAL itself, not damage. In GaMS3, part of the refusal action is Slovene-specific, so after
    the English edit Slovene refusal stays relatively higher in GaMS3 than in Gemma-IT (a model x language interaction on
    FINAL). Gap_R > 0 in GaMS3 only. In the 2x2 transfer matrix, the SL-derived direction suppresses EN refusal better than
    the EN-derived direction suppresses SL refusal. An equal-budget bilingual Heretic run closes the residual.
  why_it_could_win: >-
    It wins if claim (1) fails in GaMS3 but holds in Gemma while the damage traits are visible. GaMS chat SFT is about 80%
    machine-translated Slovene with implicit refusals in both languages, so a Slovene-specific refusal channel is a genuine
    possibility, though not favoured a priori.
- title: Abliteration moves the threshold, not the evidence
  hypothesis: >-
    Treated as a signal-detection decision, the edit is a pure CRITERION shift. Each item's post-edit refusal propensity is
    a monotone function of the original model's frozen-probe harmfulness score, with the slope unchanged and the intercept
    lower. EN and SL differ only in intercept, and residual refusal across languages and models is explained by where items
    sit on one preserved evidence axis.
  why_it_could_win: >-
    It wins if item-level fits show preserved slopes, shifted intercepts and no language x edit slope interaction on S4 and
    S5. That is a one-parameter-per-condition account that needs no edit population. It loses if slopes collapse, i.e. the
    ablation removes the evidence channel itself.
- title: Differences come from the search, not the model
  hypothesis: >-
    The two siblings share gemma-3-12b-pt, the tokenizer and the layer indexing, so their refusal and collateral structure
    is inherited, and post-Heretic model differences reflect achieved optimization. Test: re-apply each model's selected kernel
    parameters to the OTHER sibling, using its own DEV directions, and compare the panels' trait covariance matrices (random-skewers
    correlation, common principal components) and exposure profiles.
  why_it_could_win: >-
    It wins if swapped parameters reproduce each other's EN and SL trade-offs within CI and the panel covariances correlate
    >= 0.9. Then 134B tokens of continual pretraining and a different SFT barely changed how refusal and collateral respond
    to this edit family, and any headline GaMS-versus-Gemma difference is an artefact of one optimization run.
- title: Slovene breaks first because its margins are thinner
  hypothesis: >-
    There is no Slovene-specific carrier. Slovene predictions sit on thinner logit margins, so the items that flip under an
    edit are those near their decision boundary, and item-heterogeneous flipping produces an apparent Gap. Named test: an
    item x edit mixed model with an EN edit trait x baseline item margin interaction, and a margin-matched Gap after reweighting
    SL and EN items to equal baseline-margin distributions.
  why_it_could_win: >-
    It wins if the margin-matched Gap falls inside the TOST margin while the raw Gap does not, and if exposure adds nothing
    once margins are modelled. The fix is then a margin-aware English threshold, not a Slovene scorer or a projection change.
_relation_rationale: >-
  Depth-coverage law falsified by powered tests; placement x operator overlap and selection blindness replace it.
_confidence_delta: decreased
_key_changes:
- >-
  HEADLINE REPLACED: the depth/dose/coverage law is DEAD, falsified by its own powered tests in both models (Gemma P1 dR2
  0.040 with LOO -0.002, MDE 0.071; GaMS3 PB1 dR2 0.002, LOO -0.043), and broad-and-weak lost to narrow-and-strong in the
  opposite direction (-0.10 [-0.150,-0.060], Holm p 0.000). The new claim is PLACEMENT: at matched total energy AND matched
  layer count, where the energy sits decides the residual (SL 0.24 vs 0.81 at E3; nested R2 placement 0.718 vs count 0.400).
- >-
  LATCHED onto the two genuine positives and held them: art_xLy2vVlI7OEL (placement at matched energy and matched count, plus
  operator-beats-depth) and art_0XmNBGkzsJc_ (the objective has no gradient across its own candidate population: counter never
  leaves 72-100/100 while judged refusal spans 7-98/100; MAE 30.6 vs 2.1 per 100).
- >-
  ACCEPTED the reviewer in full where my own strand classification agrees: the 'firm positive' is now stated as MODEL-SPECIFIC
  (Gemma's effective band is 13-24, GaMS3's is 25-36 at SL 0.02, where Gemma never falls below 0.95), the Slovene band-mass
  coefficient is quoted as +0.156 [-0.240, 0.529] and called non-significant, and the supporting evidence is named as the
  rank statistic and the matched contrasts rather than the regression.
- >-
  MOVED the corrected objective from 'partial positive' to FALSIFIED, per its own P7 falsifier: at equal EN refusal the 1.5x-scaled
  old edit gives +.33 (difference -.05 [-.41,+.12]) and at equal KL the ladder reaches a gap of .00 (-.38 [-.47,-.29]). What
  survives from that artifact is the miscalibration measurement and the recoverability by post-hoc reselection, with certification
  quoted as kappa 0.858 on held-out replayed trials, and the trial-level count corrected to 63.
- >-
  RESTATED the run's behavioural headline as bounded by ACHIEVED OPTIMISATION STRENGTH rather than by model identity, citing
  four independent rows: the dose ladder reaching gap .00 below the corrected edit's KL, the c=1.5 kernel at SL 0.024 / EN
  0.049 with FLORES dNLL -0.000, the community bf16 edit at +.12, and the corrected swap row (GaMS3 parameters take Gemma
  SL 97->25 vs EN 100->53). 'Robust across judges and datasets' is struck.
- >-
  ADDED C1, the replacement instrument, designed to beat the baselines that beat us: a WEIGHT-SPACE write-mass overlap O =
  sum_h e(h)g(h)/||g||, where e(h) is the DEV single-site causal ablation profile per language and g(h) the edit's per-layer
  removal energy. Its mechanism-level justification is that the winning baseline (single-site transfer rho +0.732) is the
  scalar special case of O, and that the failed instrument was measured in activation space where the operator finding says
  weight edits do not live.
- >-
  ADDED C2, the gradient-blind fraction, as a near-free extension of the selection positive to a SECOND search (GaMS3's 116-trial
  journal and in-loop generations are already on disk), with the prediction that it, not architecture, explains why the two
  Heretic runs landed in different places.
- >-
  ADDED C3, the PARTIAL wedge as a finding rather than a caveat: the judge-definition range (strict +.06 to +.69, broad -.04
  to +.37, PARTIAL .548 of gemma_edit EN outputs) is predicted to follow from a single-peaked PARTIAL-share curve in dose
  whose peak sits at a higher dose in Slovene, computable on ~51,000 already-judged generations at zero GPU cost.
- >-
  CLOSED the count-based depth index for good: PB4 Spearman 0.21, the 4-layer EN/SL difference inside its own permutation
  null [-4,+4], index_EN 16 / index_SL 20 IDENTICAL in both checkpoints (so the Slovene lag is not what distinguishes them),
  and the cross-model falsification at Spearman -0.009 over 21 rows. The two different quantities both called 'the depth index'
  are now required to be defined and reconciled in the paper.
- >-
  PROMOTED the negative from art_kfCCWf7o8eJ9 to a first-class reported result with its own novelty positioning: an activation-space
  depth measurement fails to predict weight-edit outcomes, EN/L direction cosine fails beside it and reverses sign between
  models (-0.748 vs +0.556), and two one-forward-pass baselines beat both with CIs excluding zero.
- >-
  MADE JUDGE REPAIR BLOCKING: two agreement gates were missed this round (0.54 English within edited arms in exp10, 0.683
  overall in exp12), so a stratified gpt-4.1 calibration subsample must re-certify the workhorse judge to kappa >= 0.80 WITHIN
  edited cells before any confirmatory number is read, with Rogan-Gladen-corrected rates where it cannot be reached.
- >-
  CARRIED the ten blocking report repairs into the hypothesis with their numbers and source files, including the verbatim
  restoration of the iteration-1 section, the iteration-2 summary kept as 'Superseded by iteration 3' with retracted sentences
  marked rather than deleted, per-number file paths, an audit pass over the unaudited iteration-3 sections, the ASR/language-consistency/validity
  tables the user explicitly asked for, and the three miscounts (sixteen ledger items, seven eligible rows, translation-fallback
  provenance).
_evidence_state: strong_survivor
_move: deepen
_move_rationale: >-
  Two genuine positives (placement at matched energy/count; the objective's gradient-blind region). Deepen both: a weight-space
  overlap instrument built to beat the baselines that beat us.
_coverage: full
_coverage_statement: >-
  Iteration 4 keeps the four-checkpoint EN/SL safety-utility core intact and answers the user's 'investigate what explains
  them internally' by testing whether the alignment between an edit's per-layer removal energy and each language's causally
  measured refusal-write profile predicts, out of sample and against two cheap baselines, how much of an English-derived edit
  transfers - while discharging the blocking report repairs and reporting ASR, validity and language consistency separately
  as asked.
_candidates_considered: 6
relation_type: replacement
</current_hypothesis>

<all_artifacts>
Complete set of research artifacts across all iterations.

--- Item 1 ---
id: art_vzhOPupFwE4M
type: experiment
title: Same edit, very different safety effect
summary: |-
  WHAT WAS RUN. Two Heretic (SHA 3521f864) runs under ONE identical optimizer: cjvt/GaMS3-12B-Instruct and google/gemma-3-12b-it, same seed 20260923, search space, English data (mlabonne/harmful_behaviors + harmless_alpaca), bnb_4bit NF4, explicit batch size 128, 116-trial budget (60 TPE startup + 56 TPE) and pause/resume point; chat templates verified byte-identical. Heretic's interactive prompts are all scripted and logged (an unscripted one exits 3 rather than guessing). Four core checkpoints (2 originals + 2 edits chosen by a rule frozen before any trial) plus 2 swap checkpoints, scored per prompt in English and Slovene.

  HEADLINE RESULTS (all re-derived independently by audit.py: 28/28 checks, 0 mismatches, 3/3 placebo tests correctly fail).
  1. SAME-EDIT ASYMMETRY. On all 60 edits that are identical in both models, gemma-3-12b-it refuses MORE than GaMS3-12B-Instruct: 60/60 edits, 0 the other way, paired median +25 refusals/100 (bootstrap CI [10,43]). Yet the two models' KL damage from the same edit agrees almost perfectly (Spearman 0.967, CI [0.93,0.98], partial rho 0.923 after controlling for kernel mass). Refusal drop per unit KL is ~13x higher in GaMS (1449 vs 108; ratio 13.4, CI [7.0,30.0]). On the KL-matched half (KL medians 0.0101 vs 0.0098) GaMS sits at 65/100 refusals vs Gemma 99/100. Same edit, same representational damage, very different safety effect.
  2. THE RANGE-RESTRICTION GUARD BITES. A3 reading is 'intermediate', not 'shared surface': refusal ranks agree only moderately (rho 0.781, CI [0.63,0.88]; partial 0.647) and dR2_sibling is ~0 for refusal, so that rank agreement is mostly inherited from the shared parameter draws rather than a shared response surface. The guard was validated on synthetic data first (strength-only generator: dR2 CI includes 0; shared-residual generator: dR2=0.51).
  3. SELECTION AND EXACT REPRODUCTION. Fallback rule 1 fired for both (no trial reached <=10 refusals). GaMS trial 88 -> 16/100 EN refusals at KL 0.175; Gemma trial 96 -> 69/100 at KL 0.024. Both re-score EXACTLY to their journal values (KL relative difference 2e-8), and the replica reproduces Heretic's printed baselines exactly (98 and 100).
  4. CROSS-LANGUAGE, and it is NOT language-neutral. GaMS's own edit suppresses both languages (EN 98->16, SL 97->10; McNemar p<1e-24). Gemma's own edit barely moves either (EN 100->69, SL 97->90). Applying GaMS's parameters to Gemma suppresses SLOVENE far more than English (SL 97->25 vs EN 100->53) at 10x the KL cost (KL ratio own/swap 0.095, CI [0.046,0.189]). The swap never reproduces the own-edit outcome in either direction (all CIs exclude 0).
  5. DIRECTION COSINE DOES NOT PREDICT IT. The two models' orthogonalized refusal directions agree only moderately (mean cos 0.63; 0.57 over layers 24-47) while their harmless means nearly coincide (0.98) and a random-direction control gives 0.014. The large behavioural asymmetry is invisible to a raw cross-model direction cosine.
  6. NO LANGUAGE DAMAGE anywhere: FLORES+ dev per-token NLL moves by <=0.01 nats in all six checkpoints and 100% of Slovene answers remain Slovene; no checkpoint's apparent suppression is incoherence.

  LIMITS THAT MUST TRAVEL WITH THESE NUMBERS. Two models are two units: nothing here attributes the asymmetry to Slovene continued pretraining, instruction tuning or any training stage (GaMS is a same-family reference, not a controlled derivative of this Gemma checkpoint). The Gemma arm's resistance is CONFOUNDED with bnb_4bit quantization and with the reduced 116-trial budget - the published bf16 200-trial Heretic edit of gemma-3-12b-it reaches 3/100 refusals, so this is not evidence that Gemma resists abliteration in general. Slovene refusal rests on a marker list with only moderate agreement against executor hand labels (accuracy 0.75, Cohen's kappa 0.48, n=40, NATIVE_REVIEW_PENDING). The blinded 3-way LLM judge is implemented and ready (judge_sl.py) but STILL BLOCKED: retried after the platform replaced the OpenRouter key, the key this run can see (env var and secrets file, identical value and key id) returns HTTP 403 'Key limit exceeded' to every request including a 4-token probe, so 0/600 judgements succeeded and none were invented (results/judge_sl.json). SL numbers are development-grade, not final safety measurements. One optimizer seed per model; prompt-level CIs do not measure run-to-run optimizer variance. Refusal is Heretic's English keyword proxy, which counts empty answers as refusals and fires on compliant text mentioning legality or harm.

  ARTIFACTS (absolute paths in README.md and method_out.json): both Optuna journals (resumable via `uv run method.py --stages phaseB_<tag>`), both LoRA adapters with sha256, residual means and directions, per-prompt scores for all six checkpoints in results/eval/, four figures, frozen protocols. An API translator refused to translate most harmful prompts, so the Slovene set uses NLLB-200-distilled-1.3B (chrF median 70.3).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 2 ---
id: art_jxrJNc9o4QSp
type: experiment
title: English vs Slovene refusal-direction transfer test
summary: >-
  A1 screen (iteration 1) on cjvt/GaMS3-12B-Instruct@1d0b27af and google/gemma-3-12b-it@96b6f1ec (Heretic bnb_4bit NF4, bf16
  compute, L4). Data: 85 JBB harmful/benign twins after a LaBSE S1-overlap audit (15 AdvBench rows dropped), sha1 halves A
  (44) / B (41), Dolly, FLORES+, SL-LLM-Eval MC. SL is Gemini-2.5-flash MT (mean chrF 81), with NLLB fallback for 22 rows.
  Diff-in-means d_EN/d_SL on winsorized residuals; (layer, pos) chosen on half A with Arditi filters (GaMS3 L34, Gemma L20,
  pos -1); protocol hash-frozen before half B. Half B: 15 ablation conditions, u_SL increment with frozen and post-freeze
  raw-energy random controls, matched-efficacy grid, 5-dose addition, K/N/M collateral, 1,596 greedy generations judged blind
  by gpt-4.1 (the plan's gpt-4.1-mini failed the T5 hand-check), and a Heretic bridge (Heretic code, 20 TPE startup edits,
  seed 20260923). KEY RESULTS: R validity gate failed for GaMS3 (Spearman .51, AUROC .70) but passed for Gemma (.91/.96),
  so the verdict is judge-based. Frozen screen verdict: WEAK; A1's predicted contrast is REVERSED. Judged refusal after d_EN
  ablation: GaMS3 EN .90->.46 and SL .93->.34 (residual gap SL-EN -0.15 [-0.32, .03]); Gemma EN .83->.07 but SL 1.00->.85
  (gap +0.77 [.62, .89]), despite cos(d_EN, d_SL) = .92 and a log-odds transfer T(EN->SL) = 3.47. Exploratory explanation:
  Gemma's Slovene refusal margin is large (R 13.9 vs 3.6 EN; 69% of benign SL twins refused), so direction cosine and log-odds
  transfer do not predict behavioural transfer. The Heretic bridge agrees: SL-EN residual gap GaMS3 .11 [.06, .17], Gemma
  .23 [.16, .30]. GaMS3's R-based u_SL increment (F_raw .23, F_ctrl .195/.154) is collateral-confounded (span ablation FLORES
  +1.4 nat/tok; about 35% malformed). Exploratory GaMS3-only double dissociation under addition (u_SL +2.2 SL / -1.5 EN; u_EN
  +3.5 EN / -1.1 SL). Random ablation controls are destructive even when raw-energy-matched (T7 failed; documented amendment).
  Verified: T8 recompute identical; independent plain-python re-derivation matches all T/I/F/rho, judged rates and bridge
  means; placebos null. Files: method_out.json (metadata = full analysis + frozen predictions), results/analysis_summary.json,
  screen_verdict.json, per_item.parquet, judged_generations.json, figures fig1-8, README.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_3
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json

--- Item 3 ---
id: art_qdUCJWbc5kHh
type: dataset
title: Frozen English/Slovene safety and utility test sets
summary: |-
  Frozen, hashed, audited EN/SL data protocol for the GaMS3-12B-Instruct vs gemma-3-12b-it Heretic study. full_data_out.json has 48,696 rows in 10 blocks; the per-family frozen JSONL are in data/splits/; data/split_manifest.json holds the SHA256 values (protocol_hash dc33bde4...). Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1.
  Blocks:
  - S1_heretic: Heretic 3521f864 default data, EN+SL. Direction data only.
  - S2_semantic: Semantic-Harmful/Harmless. DEV only; 400/416 harmful rows are S1 rows.
  - S3_screen_dev_prompts and S3_screen_dev_utility: copied from the pods' screen_dev.json. They keep the pod ids and halves (e.g. jbb_0), which differ from the spec strings (only 50.7% of halves agree). JBB 85 pairs, Dolly 100, FLORES dev 200, MC 120.
  - S4_strongreject_pairs: 257 StrongREJECT + gpt-4.1 twin pairs, EN+SL. Strata: hoc 70 pairs (held-out Llama-Guard categories), ind 187.
  - S5_refuseu: all official RefusEU en/sl eval rows (1400+1400). Inferred category, balanced to 100 per category and LOW-confidence (Llama-Guard 64.5% EN / 49.7% SL on the gold rows). Frozen 700-row core (seed 20260923). Graded EN-SL correspondence: 0 T, 158 P, 1092 C, 150 N, the same with gemini or MADLAD back-translation, so official rows support no item-paired claims.
  - S5X_refuseu_crosstrans: gpt-4.1 cross-translations of the core, both directions, for paired claims.
  - S6_xstest: 450+450. SL by gpt-4.1 with trigger self-report; s6_primary = 219 safe items.
  - S7_slovenian_llm_eval: six tasks aligned to their English harness splits (96.6-100% verified), minus the union of carve-outs.
  - S7_flores_devtest.
  Every translated row has automated QC: cross-family back-translation chrF++ (gemini-2.5-flash for gpt-4.1 outputs, gpt-4.1-mini for gemini/pod outputs, MADLAD only where those failed), LaBSE, GlotLID, length ratio, qc_pass, and an instability flag against an independent alternate translation (gpt-4.1 for S3; MADLAD elsewhere). Native review is PENDING (250-row blinded packet).
  Overlap audit: no near-duplicate or exact overlap of S4-S7 with S1-S3.
  Key finding: the screen-spec gemini prompt used as a system message answered or refused 49% of items; data/reports/screenspec_layout_check.json.
  Other files: RefusEU scoring protocol with the verbatim adjudicator prompt (data/refuseu_protocol.md), lm-eval split map, cost log ($4.77 across 5,474 calls).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
out_expected_files:
- data.py
- full_data_out.json
- preview_data_out.json
- mini_data_out.json

--- Item 4 ---
id: art_m6pglf516e2r
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    C1 behaviour ran on the dataset's frozen S5/S5X/S6 splits and its verified EN-SL translation pairs.
title: Bilingual safety test of four model versions
summary: |-
  C1 BEHAVIOUR, the FINAL behavioural evaluation, executed once against a protocol and prompt sample frozen and hashed before any model output existed. 4,800 greedy 256-token generations: 5 checkpoints (gams_orig, gams_edit=Heretic LoRA trial 88, gemma_orig, gemma_edit=trial 96, plus community_ref p-e-w/gemma-3-12b-it-heretic as a SANITY REFERENCE) x 960 prompts (S5 = 280 RefusEU row_ids x EN+SL; S5X = 100 verified EN-SL translation pairs, the ONLY paired cross-language basis; S6 = 150 XSTest-safe x EN+SL). Each edit and its original share one NF4 base load (adapter enabled vs disable_adapter()), the same frozen bucket batch schedule and the same blinded judge.

  RESULTS (every number re-derived twice by independent code paths: audit.py 127/127, verify_headlines.py 173/173, 0 mismatches, placebos correct).
  1. Suppression, without breakage: GaMS3 EN refusal .986->.014, SL .871->.000; Gemma-3 EN .971->.287, SL .939->.739 (all Holm p<1e-14). Invalid rate is 0.000 in EVERY cell and SL language consistency moves <=0.4 points, so neither edit buys suppression with incoherence. Over-refusal on XSTest-safe also falls (GaMS3 .100->.000 EN; Gemma-3 .327->.193 SL). Official-guard ASR: GaMS3 edit .982 EN / .972 SL; Gemma-3 edit .738 EN / .103 SL.
  2. HEADLINE: on the 100 paired translations the English-derived edit transfers to Slovene in GaMS3 but not in Gemma-3 - residual SL-EN refusal gap +.69 [.60,.78], McNemar p=3.4e-21 for gemma_edit vs ~0 for gams_edit and both originals; DiD +.66 [.55,.76] vs +.01 [-.03,.05]. The sign holds in BOTH translation directions, so it is not translationese.
  3. NOT intrinsic to Gemma-3: the community bf16 edit of the same base shows a gap of only +.12 [.05,.20]. What differs is achieved optimisation strength, not architecture.
  4. MEASUREMENT FINDING (likely mechanism for 3): Heretic's own keyword proxy is near-exact on the ORIGINALS (false-positive share .015-.031) but collapses on the edits - gemma_edit EN keyword-refusal .851 vs judged .255, i.e. 76% false positives, kappa -.04. Gemma's compliances are caveat-laden and keep firing the markers, and gemma_edit EN refusals become PARTIAL compliance (.548), so an optimiser scored by that proxy loses gradient.
  5. NEGATIVE (supplementary): R_seq refusal readout pooled Spearman .86/.84 (GaMS3) but .63/.48 (Gemma-3), collapsing to .16-.33 within edit checkpoints alone - most apparent validity is the orig-vs-edit contrast.

  JUDGING / LIMITS. The run-level OpenRouter budget blocked gpt-4.1 at 716/3,840 core items (seeded-random shuffled order, so a random subset). Per fallback F1 a substitute judge from a third family, Qwen3-14B run locally, applies the SAME frozen rubric to all 4,800 items; it agrees with gpt-4.1 at kappa .83 (6-way CLASS) and .91 (refused-vs-not). Its safe/unsafe line tracks the REQUEST (it marks 77% of gemma_edit EN refusals unsafe), so ASR comes from RefusEU's official pipeline (Llama-Guard-3-8B + PolyGuard-Qwen, 91.2% agreement, full reproduction; 292 unadjudicated disagreements are BOUNDED, not dropped); its LANG line fails on short Slovene refusals, so language consistency is GlotLID (100% agreement with gpt-4.1 on the overlap). Gemini second judge and the gpt-4o-mini adjudicator were not run (same budget block); native review is PENDING; a 30-item blind EXECUTOR CHECK gives kappa .67 5-way / .93 refused-vs-not. B3 batching certification FAILED as designed (GaMS3 failed even unpadded exact-length buckets, so part of the batch-vs-single drift is NF4 numerics, not padding); buckets with one shared schedule were used for all five checkpoints. Nothing is attributed to a training stage (n=2 models, one optimisation seed); S5 EN-vs-SL is UNPAIRED; absolute levels are NF4- and 256-token-specific. API spend $1.07.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 5 ---
id: art_a4VkEvYRquBO
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    Utility and mechanism used the frozen S4 twins, S7 task items and FLORES devtest from the dataset.
title: Utility cost and inner harm signal after abliteration
summary: >-
  Four checkpoints (GaMS3-12B-Instruct and gemma-3-12b-it originals + iteration-1 Heretic LoRA edits, trials 88/96), EN and
  SL, NF4, one code path. BEHAVIOUR (gpt-4.1, random ~52% of S4 harmful gens; run budget exhausted): GaMS edit refused 100->5.6%
  EN / 6.7% SL; Gemma edit 99->70.3% EN / 95.3% SL (English-derived edit transfers fully in GaMS, barely in Gemma although
  Gemma's EN/SL harm-direction cosine is higher, 0.92 vs 0.83). Marker rule badly undercounts Gemma refusals (32.7% vs 70.3%).
  Second free judge (nemotron-3-ultra) kappa vs gpt-4.1 0.83 (refused) / 0.77 (6-way). UTILITY: 6 tasks x 250 frozen items
  x EN/SL, harness-replica scorer validated vs lm-eval (strings 100% identical, flag agreement 98.7/99.5%; ll bar fails only
  via harness bf16 rounding): macro change +0.13/+0.20 (GaMS EN/SL), +0.13/0.00 (Gemma), Holm p=1; all task deltas within
  1.6 pts; FLORES dNLL <=0.002; no wrong-language/empty/malformed outputs; Gemma EN first-token KL uninformative (255/257
  'Okay,'). MECHANISM: harm linearly decodable (held-out S4 AUROC >=0.996, not lexical/length). GaMS: frozen original probe
  collapses (0.998->0.60 EN/0.42 SL at L34, min 0.20 at L27) while refit stays 0.985/0.954; 71-73% of harm mean-difference
  energy on the frozen axis removed to ~0.1%, complement AUROC 0.985/0.955 -> re-encoding, not information loss. Gemma: frozen-axis
  separation halves equally in EN and SL from L28, yet behaviour changes only in EN -> axis compression does not explain the
  language asymmetry; late-layer axis rotation differs (cos 0.53 EN vs 0.83 SL). A2 (pre-registered): GaMS R_seq passes gate;
  slope ratio 0.36 EN / 0.42 SL -> EVIDENCE_LOSS label = decoupling of refusal from the ORIGINAL evidence axis while information
  stays decodable (changed mapping). Gemma R_seq fails gate EN; judged logistic also EVIDENCE_LOSS (flagged separation artefact).
  Gemma flips hit low-evidence items first (criterion-shift signature). EXPLORATORY dose-response (LoRA x f): Gemma SL needs
  ~2x edit strength (R_seq>0 harmful SL 98.8/77.4/46.3/7.0% at f=1/1.5/2/3 vs EN 90.3/45.1/24.5/12.8%); GaMS EN/SL move together.
  Bonus GaMS3-12B base: harm decodable (CV AUROC 0.99/0.96), complies with most harmful QA prompts. Outputs: method_out.json
  (8056 examples: S4 per item x lang x role with responses, labels, R_seq/R1, s_i, KL; S7 utility per item), results/analysis/tables.md
  + summary.json, per-item parquets, S5/S5X projections, r_prior npz, figures fig1-fig8, blinded review packet (PENDING).
  Audits: verify_numbers 80/80, audit_headline raw re-derivation identical with failing placebos. Caveats: n=2 models, one
  Heretic run each, NF4, MT Slovene, partial judge coverage.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 6 ---
id: art_KFZCxJcrr84K
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    The GaMS3 panel scored all 246 edits on the dataset's frozen S3 DEV halves A/B and its FLORES/MC items.
title: 'What English edits miss in Slovene: GaMS3 panel'
summary: >-
  P1 random-edit panel on cjvt/GaMS3-12B-Instruct@1d0b27af (bnb_4bit NF4, Heretic 3521f864, default LoRA operator). 246 Heretic
  edits (E0 = journal trials 0-59, E_TPE = trials 60-115 incl. core trial 88, E1 = 100 prior draws seed 20260925, E_R = 30
  draws seed 20260924; E0/E1/E_R certified identical to the sibling Gemma pod) were rebuilt through Heretic's own reset_model+abliterate
  and scored in EN and SL on teacher-forced traits over S3 DEV halves A/B: R_seq, R1, Rb (JBB 85 twins), K = log mean truncated
  KL on Dolly continuations (100), N = FLORES NLL rise (200), M = MC margin change (120). Question: are EN traits (all Heretic's
  optimiser sees) a sufficient surrogate for SL? Gap_t = R2*(EN_A->EN_B) - R2*(EN_A->SL_B), noise-ceiling normalised, joint
  edit x item bootstrap B=1000, protocol frozen+hashed before any trait. RESULTS (F = 160 fitted edits, primary learner HistGBT):
  refusal proxy R_seq passes the judged validity gate (Spearman EN 0.970, SL 0.910 over 18 conditions). Claim 1 holds (confirmatory):
  Gap_R = 0.015, 90% CI [0.008, 0.027]: EN predicts SL refusal as well as EN. Main hypothesis G3 SUPPORTED for K only (confirmatory):
  Gap_K = 0.147 [0.074, 0.265], Holm p~0, MDE 0.137, SIMEX 0.112, margin-matched 0.131, halves 0.118/0.150, B_K 0.050 [0.001,
  0.121]; reverse direction -0.124 (language-specific K component). SL KL is smaller on average (mean-change ratio 0.59) but
  EN traits cannot rank which edits hurt SL. N and M: F8 'no signal to predict' (no automatic language damage visible). Frozen
  exposure carrier D FAILS (G4; dR2 for K -0.011 [-0.058, 0.027]); exploratory post-freeze lead: refusal-direction SOURCE
  LAYER explains the SL/EN KL ratio (Spearman 0.77; dR2 0.047 [0.008, 0.074] over EN traits + static baselines). Gap_Heretic_K
  on journal trials only 0.018 (boundary). Forecast coverage fails on E_TPE for several traits (G6 false). r_prior defined
  (G5 false). Bilingual reselection keeps trial 88 (SL_est 1.1). Independent re-derivation (rederive_headlines.py, different
  learners): Gap_K 0.115/0.105, Gap_R ~0.01, validity and kappa exact; all placebos fail. Judging: gpt-4.1 labelled 1130/2140
  generations ($1.06) before the run-level OpenRouter budget ran out; the remaining 1010 and the second-judge role use a local
  Qwen3-14B (kappa vs gpt-4.1 0.875 refused-vs-not, n=1130); gemini second judge not run. Cross-GPU repro: traits re-score
  within numerics; weak-edit KL has a hardware floor. Per-edit variances for power: results/variances_for_power.json. Key
  files (workspace /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_6): results/verdict.json,
  results/analysis_results.json, results/panel_items/*.parquet, results/panel_edits.jsonl, results/judged_generations.json,
  results/compliance_refs_gams_core.json (shared export for the Gemma pod), results/summary_tables.md, figures/fig1-fig8,
  method_out.json (one example per edit).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_6
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 7 ---
id: art_CUChUm6wCwo5
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    The Gemma panel reused the same frozen S3 DEV halves and semantic-ID split for its 203 edits.
title: English edits barely unlock Slovene refusal in Gemma
summary: >-
  Gemma-3-12b-it (NF4, Heretic 3521f864) random-edit panel testing whether English refusal/utility traits predict Slovene.
  203 edits scored teacher-forced in EN+SL on frozen S3 DEV halves: E0 = 60 journal startup trials (same vectors as the GaMS
  pod), E1 = 103 fresh prior draws (seed 20260925), E_TPE = trial 96 + last 40 TPE trials (held out). Fitted set 163 non-collapsed
  (>=150 floor met). Traits R_seq, R1, Rb, K, N, M; covariates P (r_prior), H (d_EN), D, b1/b2/b3, Omega. Validity: 14 edits
  judged by a LOCAL judge (original gemma, frozen gpt-4.1 rubric; 98.2% binary agreement with gpt-4.1 on 440 original generations);
  API blocked by the run budget. R* = R1 (Spearman EN .892 / SL .853). KEY RESULTS: (1) Slovene refusal is strongly attenuated:
  SL/EN transfer slope R1 0.436, R_seq 0.220. Core edit trial 96: judged harmful refusal EN 36->10/41, SL 41->39/41; no validity
  edit brought SL below 30/41. The attenuation survives margin matching (slope 0.558) and the mixed model (sl:x -0.321). (2)
  Teacher-forced, edits raise compliance log-prob equally in both languages (slope 0.849) but lower the refusal-opener log-prob
  only in English (slope 0.081). (3) The attenuated response is predictable from English: R2 EN_A->SL_B 0.94 vs EN_B 0.99;
  Gap_R1 +0.054 [0.022, 0.128] (<0.10 -> P-a NOT CONFIRMED; within a label-swap placebo range); margin-matched +0.057 (P-d
  NOT CONFIRMED); Gap_Rb +0.018 (P-b UNTESTABLE, Rb fails the SL gate); Gap_K +0.079 (Holm p .009); N and M unreliable in
  SL. (4) Carrier: r_prior removal P adds dR2 +0.004 over geometry baselines, which themselves have CV R2<=0 (P-c NOT CONFIRMED);
  exploratory H adds nothing. (5) No journal trial has predicted SL judged refusal <= 0.20 (best 0.57). Audit (independent
  numpy path) and rederive.py (raw files, polynomial OLS: Gap_R1 +0.052; slopes and judged counts match exactly) pass, with
  placebos failing as expected. Outputs: method_out.json (per-edit rows + all analysis tables), results/analysis.json, results/verdicts.json,
  results/panel/*.parquet, results/validity/, figures fig1-6, README.md, reproducibility.md. Caveats: correlational carrier;
  4-bit; one model; three GPUs (per-device zero points); local judge; MT Slovene with native review pending.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_7
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 8 ---
id: art_hmbXDppkPZnR
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    The causal test drew its frozen half-A directions and its held-out S4 StrongREJECT category twins from the dataset.
title: Why an English safety edit misses Slovene
summary: >-
  Iteration-2 causal test in google/gemma-3-12b-it (NF4 4-bit, pinned 96b6f1ec), with cjvt/GaMS3-12B-Instruct as a descriptive
  contrast and p-e-w/gemma-3-12b-it-heretic@e037e6e1 as a held-out community edit. Question: is the Slovene refusal that survives
  an English refusal-direction ablation (d_EN, A1 frozen site L20) carried by a harm-orthogonal, language-conditioned refusal
  prior r_prior (Wang et al. 2025 false-refusal construction from judged harmless refusals)? Directions, layer and strengths
  were chosen on S3 half A and frozen (configs/FREEZE.sha256) before the OUTCOME set (41 JBB half-B + 70 StrongREJECT held-out-category
  twin pairs, EN+SL; 111 harmful + 111 harmless per language) was touched. 12,136 greedy generations; blind batched gpt-4.1
  judge (5,298 labels, every frozen-prediction arm fully covered; $3.43, run budget then exhausted), local Qwen3-14B second
  judge on every generation (kappa 0.77 refused-vs-not). RESULTS: the pre-registered hypothesis FAILS. d_EN leaves 0.86 SL
  harmful refusal (EN 0.23); adding r_prior at matched EN efficacy cuts it by only 0.036 [-0.037, 0.109], below the best energy+collateral-matched
  random (0.074) and the shuffled-label control (0.135): KILL (a) and (c) fire; F1/F3/F4/F6 fail, F2 passes, F5 is not evaluable
  (community SL hoc refusal 0.26 < 0.40). r_prior is language-dominated (cos with the language axis 0.65, with its shuffled-label
  twin 0.89); d_EN+l cuts 0.315 but costs +1.93 nats of SL FLORES NLL. r_prior alone gives a real but sub-threshold drop in
  SL over-refusal (0.28 to 0.19, Holm p 0.025). EXPLORATORY discovery (declared post-freeze): ablating each layer's own d_EN(h)
  at all 48 layers removes the SL residual (0.86 to 0.10, gpt-4.1 partial coverage; 0.91 to 0.23 second judge) with fluent
  Slovene (FLORES +0.52), whereas layer-matched random (0.86) and energy-matched PC (0.93) controls do nothing, and no single
  12-layer band suffices (cumulative through layers 1-36): the residual is written redundantly across depth, not missing a
  direction. The same move repairs the core Heretic edit (SL hoc 0.93 to 0.11; its random control 0.47). The core iteration-1
  edit is optimisation-limited (SL hoc 0.89 vs community 0.26). GaMS3 shows no SL-specific residual. Frozen harm probe still
  decodes harmfulness after ablation; cosine-based transfer prediction fails at item level (AUROC 0.24). All numbers re-derived
  by verify_numbers.py (103/103) and independently from raw files by audit_headline.py (43/43, placebos null). Files: method_out.json
  (per OUTCOME item x language, per-arm responses, labels, R1/R_seq; metadata = full analysis, verdicts, deviations), results/analysis_summary.json,
  results/per_item.parquet, results/report_tables.md, figures/fig1-fig10, directions/ (frozen vectors), configs/. Workspace:
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 9 ---
id: art_ex4hbgThhJaL
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    Coverage x strength cells scored on the dataset's frozen S3 DEV halves, S4 held-out categories and S5X pairs.
title: How deep must an edit go to stop Slovene refusal
summary: |-
  Coverage x strength factorial on Heretic-family weight edits in google/gemma-3-12b-it (NF4), asking whether Slovene refusal survives an English-derived edit because the edit is not DEEP enough. 122 cells, 27,784 generations, all judged by a partial-aware 4-way scorer (local Qwen3-14B on iteration-2 exp4's frozen rubric verbatim; REFUSED/PARTIAL/COMPLIED/INVALID, PARTIAL counted as compliance and shown separately, INVALID never refusal), certified at kappa = 0.866 refused-vs-not against a bought 600-item gpt-4.1 subsample on THIS run's own edited cells (on-disk pools gave 0.779, below the 0.80 bar, so the subsample was bought as the plan prescribes; $0.70 of a $10 cap).

  WHAT FAILED (pre-registered, with its own falsifier firing). P1: coverage descriptors add dR2 = 0.040 [0.006, 0.136] over log-energy + the English effect + static geometry baselines, but leave-one-out dR2 = -0.002, partial F p = 0.17, and a permutation placebo yields a LARGER dR2 on average (p95 0.158); MDE = 0.071 < the 0.10 bar, so this is a powered rejection. P2: pooled matched-energy contrast +0.049 [-0.000, 0.098], inside its label-swap placebo, signs disagreeing across the four groups, and the coverage x language interaction runs BACKWARDS (DiD -0.120 [-0.214, -0.033]); held-out harm categories replicate this. Both fail Holm.

  WHAT SURVIVED, each placebo-tested. P3: the DEV-frozen depth index predicts per-cell residuals out of sample, Spearman 0.78 in both languages (permutation null [-0.27, 0.29]); 97% of cells covering fewer than index_SL = 20 effective layers leave Slovene above 0.5, but only 47% at/above it fall below, so the index is NECESSARY not sufficient. The mechanism is band DENSITY, not breadth: lowest reachable Slovene refusal is monotone in the fraction of layers 13-24 covered (12/12 -> 0.024-0.171; 6/12 -> 0.732; 3/12 -> 0.927; 0/12 -> 0.951-1.000), Spearman -0.942, permutation p = 0.0038. At identical energy (E = 19.2), 12 contiguous mid-depth layers reach SL 0.63 while 24 layers strided over the full depth leave 0.98. Leave-one-band-out: sparing layers 25-36 costs Slovene +0.39 residual refusal and English 0.00. An independent activation read converges: Slovene's harm-write mass is 60% in 25-36 where English's is 63% in 37-48.

  CROSS-LANGUAGE CLAIM, CORRECTLY BOUNDED. index_EN = 16 vs index_SL = 20 is directionally as pre-registered, but 4 layers is one k-grid step and sits INSIDE its language-permutation null [-4, +4] - the index alone does not carry it. The powered statistic is the prefix-curve separation: +0.080 [0.021, 0.136], permutation p = 0.0065.

  PRACTICAL. Heretic's own kernel support at c = 1.5 reaches SL 0.024 / EN 0.049 harmful refusal at FLORES dNLL -0.000 nats, KL 0.030, 0% invalid, 99.2% Slovene (screen), and SL 0.08 / EN 0.02 on 100 VERIFIED RefusEU translation pairs (vs unedited 0.98/0.91). The frozen-subset kernel at x1 cuts Slovene over-refusal on XSTest-safe from 0.37 to 0.08 at utility cost indistinguishable from zero. Iteration 2's activation repair reaches lower Slovene refusal but costs +0.589 nats and a real English capability hit (-0.053 [-0.083, -0.023] S7 macro). Both matched controls (write-space random, energy-matched harmless PC; energy matched within 10% AND collateral matched, 8/8 accepted) are null at SL 0.95-1.00.

  REUSABLE FOR LATER ROUNDS (absolute paths in README.md): results/gens/ (all 27,784 generations, 122 cells), results/cells/ (coefficient profiles, closed-form edit energies, FLORES/KL, control-draw diagnostics, S7 utility), results/cells.csv, results/per_item.parquet, results/judge_local.jsonl + judge_api.jsonl, the frozen redundancy_index.json / frozen_predictions.json / FREEZE.sha256, report_tables.md, and 6 figures. Verification: rederive.py re-derives 318/318 headline numbers through a stdlib+numpy path importing nothing from the repo; audit_positive.py placebo-tests every surviving positive claim and is what demoted the index statistic and corrected the band claim from "contains" to "covers densely". 13 deviations recorded. Native Slovene review remains PENDING; one model, one seed, NF4 only.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_9
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 10 ---
id: art_xLy2vVlI7OEL
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    GaMS3 panel used the frozen S3 half-A DEV items and S4 held-out Llama-Guard category twins.
title: Where to cut refusal in a bilingual model
summary: |-
  GaMS3-12B-Instruct half of the iteration-3 depth-coverage test. 57 cells, 10,690 judged generations, $0.00 OpenRouter spend (the run key was exhausted; judging is the local Qwen3-14B with iteration-2's frozen rubric).

  PART A (DEV only, S3 JBB half A, 40 harmful+40 harmless per language). Cumulative-prefix / suffix / leave-one-band-out ablation of the FROZEN per-layer English refusal directions d_EN(h) reused from art_hmbXDppkPZnR (cos>=0.9964 vs a fresh recompute at every h). index_EN=16 [16,16], index_SL=20 [16,24], difference 4 [0,8] -> PA1 EQUIVALENT_WITHIN_MARGIN against the pre-declared +/-8 margin (Holm p 0.069). CRITICAL CAVEAT: the co-primary USABLE index (refusal<0.5 AND INVALID<=0.10) is '>48' in BOTH languages - activation-space depth coverage only removes refusal by destroying the model (INVALID 0.72 EN / 0.38 SL at the crossing, FLORES +1.4 nats).

  PART B (the decisive panel). Heretic's own abliterate() generalised to arbitrary per-(layer,component) weights (heretic_op.py; operator-equivalence vs Heretic's own source max rel err 1.7e-06; trial-88 adapter rebuild median 3.3e-07; energy identity <1e-06). 3 matched-total-removal-energy groups (E*=6.9/13.9/27.8, every member within 2%), each with narrow bands B2/B3, spread sets STR4/STR2/ALL, plus no-op, layer-matched RANDOM and energy-matched PC controls; anchors G1 single-site, CORE trial-88 adapter, SWAP_in (Gemma trial-96 kernel); plus a 10-cell coverage grid at c=1.

  HEADLINE RESULTS (confirmation = S4 held-out Llama-Guard categories, 70 pairs/language, frozen BEFORE generation; freeze mtime precedes all 25 confirmation files):
  - PB2 FALSIFIED IN THE OPPOSITE DIRECTION: narrow-and-strong minus broad-and-weak SL refusal = -0.10 [-0.150,-0.060]; CONCENTRATING the same energy on one 12-layer band beats spreading it (Holm p 0.000).
  - PB3 FALSIFIED OPPOSITE: coverage x language interaction -0.07 [-0.131,-0.007]; the advantage of concentrating is LARGER in Slovene.
  - Placement at matched energy AND matched layer count (12 contiguous vs every 4th): SL 0.24 vs 0.81 (E3), 0.51 vs 0.89 (E2), 0.83 vs 0.93 (E1), every CI excluding 0.
  - PB1 NOT SUPPORTED: coverage dR2 = 0.002 [0.000,0.010] over 26 cells; leave-one-cell-out dR2 = -0.043. Nested decomposition: log E alone R2 0.325 -> +WHERE the energy sits (band fractions) 0.718 -> +HOW MANY layers 0.400. Placement, not coverage count, carries the variance.
  - PB4 NOT SUPPORTED (Spearman 0.21): a count-based index cannot express placement (it gives a 12-layer band and 12 spread layers the same prediction).
  - Band profile at c=1 (SL): layers 1-12 0.93, 13-24 0.24, 25-36 0.02, 37-48 0.85.
  - Controls null everywhere: random / PC at matched energy leave SL refusal 0.93-0.95 (screen) vs no-op 0.93.
  - OPERATOR MATTERS MORE THAN DEPTH: the same directions as Heretic's row-norm-preserving weight edit remove refusal at ~zero collateral (|SL FLORES dNLL| <= 0.011, MC accuracy within 0.031 of no-op, INVALID ~0.01), while the raw activation projection of those same directions breaks the model.
  - CROSS-MODEL (descriptive, n=2): the sibling iteration-3 Gemma pod independently reports index_EN=16 / index_SL=20 - identical to GaMS3. The Slovene lag is common to both checkpoints, so it is NOT what distinguishes them; no difference is attributed to any training stage.

  AUDIT: rederive.py re-derives 481/481 headline numbers (228 per-cell rates, 24 prefix points, 2 indices, PB1/PB2/PB3/PB4, the nested R2 decomposition, 218 exact McNemar tests) from the raw per-generation files through a code path importing nothing from the analysis; freeze-order check PASS; three placebos collapse (cell-label-within-item 0.003, language-label -0.001, energy-shuffled 0.023) against real effects of -0.105 and -0.071.

  JUDGE LIMITATION: on-disk certification vs gpt-4.1 gives kappa 0.86 Slovene but 0.54 English within EDITED arms (paid top-up impossible, HTTP 403), so English rates are the strict end of a judge range; PARTIAL is always its own column. GaMS3's shipped edit already left only 0.10 SL refusal, so this panel measures trade-offs, not a rescue. S5/S6/S7 never opened; ASR and the lm-eval macro not run (deviations.json, 9 entries).

  OUTPUT LAYOUT: method_out.json IS the comparison table - 462 examples (one per split x item x language) x 56 distinct predict_<method> fields = 10,690 per-item outcomes, exactly the 10,690 generations produced. `output` is the UNEDITED model's 4-way class; each predict_<method> is the class the same item got under one intervention that ran (band edits, matched-energy spread edits, random/PC controls, prefix/suffix/LOBO activation arms, single-site ablation, shipped Heretic edit, Gemma kernel swap), with its text, gpt-4.1 label, rule label and GlotLID language in metadata_*. Headline recomputes from this file alone: SL narrow-broad -0.1048 over n=70; controls null at 0.957 vs 0.957 baseline.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_10
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 11 ---
id: art_0XmNBGkzsJc_
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    Behavioural arms ran on the dataset's 100 verified S5X pairs, S4 held-out prompts, S6 XSTest-safe items and FLORES.
title: Heretic's refusal counter misjudges its own edits
summary: |-
  C3: replaces Heretic's 33-substring keyword refusal counter with a judge-distilled, partial-aware classifier, holding the Heretic commit, seed, search space, construction data, NF4 quantisation, 116-trial budget, KL scorer and the frozen selection rule fixed, on google/gemma-3-12b-it in English and Slovene.

  CLEAN POSITIVE (the finding). All 116 iteration-1 parameter draws were re-scored inside Heretic's own loop and all 11,600 in-loop generations were labelled with the frozen art_m6pglf516e2r rubric (Qwen3-14B). The keyword objective reaches only kappa +0.196 against the judge, reports .907 refusal where the judge sees .711, and 25.4% of its 'refusals' are false; the distilled classifier reaches +0.924. The counter never falls below 72/100 across all 116 draws while judged refusal spans 7-98/100, so the optimiser is blind exactly where its candidates differ; on the keyword-selected trial 96 it reports 74/100 where the judge sees 37 refusals and 49 PARTIAL answers. Mean absolute error in a draw's refusal count: 30.6/100 (keyword) vs 2.1/100 (classifier). This is a SELECTION failure on the optimiser's own candidates, not evaluation noise.

  INSTRUMENT. The classifier (char/word TF-IDF + hand features, logistic regression, first 100 tokens = the in-loop view) is distilled from 11,885 prior judge labels and certified only on 20 held-out replayed trials: kappa .858 [.820,.888] vs the keyword rule's .143. The base fit missed the pre-registered 0.80 bar (.729) and was refit once, as planned, on non-certification trials. It is a drop-in Heretic Scorer plugin (third_party/heretic/src/heretic/scorers/partial_aware_refusal.py), not a fork.

  SELECTION CHANGES, REPLICATED. With the corrected objective the frozen rule fires its primary branch (min KL s.t. <=10/100 refusals), which the keyword run never could: trial 7, per-layer kernel, aligned coverage A1=64.0 vs trial 96's 26.0. A second optimiser seed (20260926) replicates: same rule branch, 5/100, A1=65.1. The shared first-60 seeded draws give a within-run A/B (8 vs 14 Pareto points).

  BEHAVIOUR AND THE FALSIFIER. Eight arms (original, keyword-selected, corrected, two reselections, dose ladder f=1.5/2/3) over 3,680 generations on 100 verified EN/SL pairs, 70 held-out-category StrongREJECT prompts, 60 XSTest-safe items and FLORES. Corrected cuts English judged refusal .15->.03 and the paired SL-EN gap +.68->+.38 [-.41,-.18 vs keyword]. BUT the pre-registered falsifier P7 fired: at equal English refusal the 1.5x-scaled old edit has gap +.33 (-.05 [-.41,+.12]), and at equal harmless KL the ladder reaches gap .00 (-.38 [-.47,-.29]) - dose for dose the corrected edit is strictly worse. Mechanism is DOSE, not placement. P2 also failed. Post-hoc reselection (seed-free) recovers the whole effect, so the change is mis-scoring of trials already held, not a different search. Official RefusEU guard ASR moves the same way; invalid output .000 everywhere, GlotLID >= .991, Slovene FLORES dNLL <= +.005 for selected arms.

  VERIFIED: audit_headline.py 305/305 and audit_extra.py 17/17 re-derive every headline from raw files by different code paths, with 7 placebos that all fail as required; verify_numbers.py 59/59. Kept for later rounds: adapters_corrected/ (the corrected LoRA), checkpoints/ (both Optuna journals), scorer/refusal_clf.joblib.

  LIMITS: one model; behavioural arms from one seed; no frontier judge validated any new label (run-level OpenRouter budget was exhausted at the first call, $0.00 spent) so the workhorse judge's within-edited agreement with gpt-4.1 (kappa .78) bounds every judged number; lm-eval utility cut before generation; Slovene is machine-translated with native review pending; NF4-specific levels; greedy decoding is not bit-reproducible across GPU models.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_11
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 12 ---
id: art_kfCCWf7o8eJ9
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type: uses
  relation_rationale: >-
    DEV indices from S3 half-B; confirmation on held-out StrongREJECT items drawn from the dataset's S4 block.
title: Depth index fails to predict cross-lingual refusal-edit failure
summary: >-
  Iteration-3 predictive test in google/gemma-3-12b-it (anchor, NF4, pinned 96b6f1ec), Qwen/Qwen3-8B and mistralai/Mistral-7B-Instruct-v0.3
  (EuroLLM-9B-Instruct was the planned M3 but is gated and returned HTTP 403; the recorded fallback order was followed, results/load_log.json),
  in EN/SL plus DE/LT newly translated with NLLB-200-distilled-1.3B. QUESTION: can iteration-2's depth-redundancy observation
  be turned into a PREDICTIVE instrument? A per-language index (smallest cumulative depth coverage of d_EN(h) activation ablation
  at which judged harmful refusal falls below 0.5, measured on DEV-only S3 JBB half-B items) was computed, FROZEN and hashed
  (configs/frozen_predictions.json in configs/FREEZE.sha256; run_model.py --phase conf raises without it) BEFORE any confirmation
  generation, then tested out of sample on 60 held-out StrongREJECT harmful items per language (30 held-out-category + 30
  in-distribution, paired by semantic id) against English-derived Heretic-operator WEIGHT edits (Heretic 3521f864's projected,
  row-norm-preserving rank-3 LoRA with OUR per-layer directions injected): W0 no-op, W1 narrow 25%-depth band, W2 energy-matched
  all-depth stride, W3 selected kernel (Gemma = the REAL iteration-1 trial-96 adapter, sha256-verified), W4 energy- AND collateral-matched
  random. RESULT: the pre-registered claim is FALSIFIED. P1 pooled Spearman(index, residual refusal) = -0.009 [-0.131, 0.192]
  over 21 rows (permutation p 0.16); the AUC secondary gives +0.167; P2 concordance 8/12 decided (0.67, below the 0.75 bar,
  and 6/12 under judge-error correction); P3 alone holds in sign (Spearman(index, W2-W1) = -0.474). CRITICALLY, EN/L direction
  cosine ALSO fails (+0.010), so the 'familiar geometry stops predicting' boundary is real but stops for our index too, while
  two CHEAP baselines beat both by margins whose paired item-bootstrap CIs exclude zero: single-site transfer rho +0.732 (index-baseline
  -0.741 [-0.810, -0.528]) and the unedited model's baseline refusal in that language rho +0.661 (-0.670 [-0.721, -0.497]).
  Gemma's real trial-96 adapter on held-out items leaves EN 0.60 / DE 0.53 / LT 0.75 / SL 0.92 from a 0.93-0.98 no-op, replicating
  the iteration-1/2 English-Slovene asymmetry on a new harm source and extending it to two new languages; its energy- and
  collateral-matched random control leaves SL at 0.98, and the SL-NLLB vs SL-gpt translation-method control moves every rate
  by <=0.09, closing that confound. POST-HOC (exploratory, changes no verdict, prompted by the language-shuffle placebo returning
  -0.356 instead of ~0): within the anchor model the index DOES order the languages (rho +0.678) but Qwen3's eligible languages
  all share one index value so it has zero variance there; pooled within-model-centred rho is +0.458 (AUC +0.620), and cosine
  REVERSES sign between models (-0.748 gemma, +0.556 qwen3). The frozen eligibility gate did real work pre-hoc: Mistral refuses
  only 0.07-0.53 at baseline (0.07 in Lithuanian) so all four of its rows were excluded before any confirmation data existed,
  and it was dropped from the weight panel under the pre-registered cut order rather than swapped silently. AUDIT: rederive.py
  (stdlib+numpy only, reading only raw generations, labels and the frozen file) reproduces every index, AUC, eligibility flag,
  residual and P1-P4 statistic: 102 checks, 0 mismatches; placebos (b) index permutation -0.009, (c) label swap flips sign,
  (d) DEV-as-CONF correctly flagged LEAKAGE. Positive control 4/4: the Gemma DEV curve reproduces iteration-2's anchor (EN
  P50 0.39 vs 0.42, SL P75 0.27 vs 0.21). JUDGE LIMITATION, reported not buried: the run's OpenRouter budget was exhausted
  before this artifact began ($0.00 spent here), so gpt-4.1 was unavailable and the planned fallback could not fire; the local
  Qwen3-14B judge (rubric variant chosen on a DEV split of the free existing gpt-4.1 label pool, certified once on a disjoint
  holdout) reaches kappa 0.683 [0.629, 0.737], BELOW its 0.80 gate, with Se 0.984 / Sp 0.741, so absolute refusal levels are
  biased upward and a Rogan-Gladen corrected re-run of P1/P2 is reported. analysis.py was patched after the freeze for numerical
  robustness only (empty-bootstrap quantile; undefined differences must not count as decided); both hashes and the full diff
  are in results/analysis_patch.json and checks.py flags analysis_py_unchanged=false. Native review PENDING. 9,199 blind 4-way
  judged generations; method_out.json has 8,520 per-example rows. Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 13 ---
id: art_Z3I1K3VnFZuz
type: evaluation
in_dependencies:
- id: art_m6pglf516e2r
  label: audits
  relation_type: similarities
  relation_rationale: >-
    Audit re-derived and confirmed the keyword-proxy inversion on edited cells (FP share .761, kappa -.04).
- id: art_hmbXDppkPZnR
  label: audits
  relation_type: uses
  relation_rationale: >-
    Audit recomputed exp8's arm tables and judge agreement from its raw per-item files.
- id: art_CUChUm6wCwo5
  label: audits
  relation_type: differences
  relation_rationale: >-
    Audit found the draft inverted exp7's frozen P-a: it failed because Gap_R1 is small (.054), not large.
- id: art_KFZCxJcrr84K
  label: audits
  relation_type: uses
  relation_rationale: >-
    Audit re-derived the GaMS3 panel's Gap values and judge agreement from its saved panel files.
- id: art_a4VkEvYRquBO
  label: audits
  relation_type: uses
  relation_rationale: >-
    Audit recomputed exp5's utility, probe and dose tables and flagged its marker-based rows as judge-sensitive.
- id: art_vzhOPupFwE4M
  label: audits
  relation_type: differences
  relation_rationale: >-
    Audit reversed the draft's swap conclusion: GaMS3 params on Gemma give EN 100->53, SL 97->25 at KL .254.
- id: art_jxrJNc9o4QSp
  label: audits
  relation_type: differences
  relation_rationale: >-
    Audit corrected exp3's judge provenance (gpt-4.1 only) and Gemma's EN baseline (.83, not 99%).
title: Rechecking every number and every judge
summary: >-
  CPU-only audit of the iteration-2 draft against raw per-item files of 7 artifacts (iter1 exp1/exp3; iter2 exp4-8), by an
  independent code path, plus a judge-sensitivity instrument. AUDIT: 167 draft numbers checked: 137 match, 8 mismatch, 12
  misdescribed, 6 untraceable (mismatch rate .055); 2 sign-reversed conclusions: (a) iter-1 swap: GaMS3 trial-88 params on
  Gemma give EN 100->53, SL 97->25 at KL .254 (draft '91/95 at .293' exists in no file); (b) exp7 P-a was frozen as 'Gap_R
  >= 0.10 with LB>0' and failed because the gap is SMALL (.054), the draft inverts it. 13.4x = ratio of medians of refusal
  drop per unit KL (1449 vs 108), not refusal counts. A3 reading 'intermediate'. Exp3 judge was gpt-4.1 only; Gemma EN baseline
  .83 not 99%. JUDGES: exp4 gpt-4.1 vs Qwen3-14B binary kappa .913 pooled but .779 [.678,.861] within edited checkpoints (inflation
  .133; AC1 .908); exp8 .769 vs .737. Keyword proxy on gemma_edit EN: .851 vs judged .255, FP share .761 (71% of FPs PARTIAL),
  kappa -.04. 19/99 behavioural claims JUDGE_SENSITIVE (e.g. exp8 A1 EN .225 gpt-4.1 vs +.44 higher under Qwen on same items).
  KEY FINDING: the Gemma SL-EN refusal gap is definition-dependent: STRICT (refused) +0.22 to +0.71 across LLM judges/datasets,
  all CIs > 0; BROAD (refused+partial) -0.04 to +0.37. S5X paired (Qwen) strict +.69 [.60,.78] -> broad +.23 [.14,.32]; RefusEU
  S5 broad -.04. The English edit mostly converts EN refusals into PARTIAL replies. Placebos 6/6 pass; headline numbers re-derived
  independently (10/10 match). Optional gpt-4.1 top-up blocked (HTTP 403 run budget), $0 spent, no labels invented. No native
  review exists (packets pending). FILES: results/report_repairs.md (paste-ready tables for repairs 1-10 with source paths),
  corrected_numbers.json (236 records), judge_sensitivity.csv/md, judge_agreement.csv, keyword_miscalibration.csv, gap_range.csv,
  claims_registry.csv, dead_end_ledger.md, pending_human_review.md, novelty_table.md (verbatim quotes; 2607.02714 '2-3 middle
  layers' NOT VERIFIED), audit_log.json, configs/label_map.yaml (reusable for new cells), figures fig_gap_forest/fig_judge_stack/fig_kappa_inflation.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
- reproducibility.md

--- Item 14 ---
id: art_NpZ_nW6qgSKD
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Where a refusal edit lands decides what survives
summary: |-
  WHAT WAS RUN. A frozen, DEV-only causal write profile e_L(h) (judged refusal drop from ablating the frozen English refusal direction d_EN(h) at ONE hidden index, 44 JBB half-A items/language, 48 sites) defines an overlap instrument O_L(edit)=sum_h e_L(h)g(h)/||g|| over each Heretic-family weight edit's closed-form per-layer removal energy g(h). O is invariant to coefficient rescaling, so it measures placement only. O was frozen (hashed, mtime-checked) and tested out of sample on google/gemma-3-12b-it NF4: 29 conditions x 60 frozen held-out items/language (40 StrongREJECT held-out-category + 20 verified RefusEU EN-SL pairs). The conditions were 8 matched groups (high-O vs low-O windows at IDENTICAL closed-form energy and IDENTICAL layer count), energy-matched write-space random and harmless-PC controls, a dose ladder and a no-op. Outside family: Qwen3-8B (EN/SL/DE; LT excluded by the pre-registered gate), 3 matched groups + controls. 10,000 generations were judged 4-way (REFUSED/PARTIAL/COMPLIED/INVALID) by local Qwen3-14B on the frozen exp4 rubric; the gate used 800 gpt-4.1 labels ($0.97).

  RESULTS. (1) FROZEN VERDICT: FALSIFIED for the instrument claim. O's incremental R2 over the pre-declared nuisance stack is 0.026 EN (powered, MDE 0.047) and 0.052 SL (inconclusive band), below the 0.05 falsifier, because the g-weighted EN/SL direction cosine is collinear with O (rho 0.81/0.76; R2 alone 0.83/0.63 vs O 0.87/0.75). (2) PLACEMENT IS STRONGLY CONFIRMED. The high-O member leaves less refusal in 8/8 groups in both languages (pooled EN -0.69 [-0.75,-0.62], SL -0.38 [-0.46,-0.31]; best: layers 16-31 EN 0.07/SL 0.27 vs layers 33-48 0.92/0.92 at the same energy). Random/PC controls stay within +-0.03 of the no-op, and a 2x dose of the late-layer edit still leaves EN 0.88/SL 0.92. (3) O ranks the 18 held-out conditions near-perfectly: Spearman -0.96 EN, -0.83 SL. It beats the unedited refusal rate and the single-site transfer rate on pooled rows (aligned CI [0.28,0.65], [0.29,0.76]), beats the single-site peak probe in EN (+0.17 [0.14,0.23]) and ties it in SL. (4) The language-label placebo does NOT collapse (EN profile predicts SL residual at -0.94), so the language-specific claim is demoted: O works by locating a shared mid-depth band (argmax prediction band 13-24 passes). (5) Under the best-placed edit the EN/SL gap is a strict-vs-broad effect (strict 0.07 vs 0.27, broad 0.53 vs 0.53; ASR-by-rubric 0.93 vs 0.72). (6) Qwen3-8B replicates placement: 9/9 matched contrasts favour high-O (8/9 CIs exclude 0); Spearman(O) EN -0.76, SL -0.93, DE -0.84; the miss REVERSES there (EN retains more refusal than SL). (7) Screen on 46 exp9 cells: O -0.71/-0.60 but energy dominates (dR2 0.008/0.028). Post-hoc harmless KL is a strong competitor (exploratory).

  JUDGE CAVEATS. Within-edited kappa 0.818 pooled; EN 0.856 passes, SL 0.744 fails, so SL is JUDGE_SENSITIVE (Rogan-Gladen keeps the ranking and enlarges the contrasts). The Gate-2 INVALID probe failed (the judge never labels synthetic incoherence INVALID), so a deterministic validity guard was added before confirmation. Native review pending.

  AUDIT. rederive.py (stdlib+numpy, independent path): 209/209 checks pass, including shuffled-O and label-swapped placebos that fail as required. Files: results/analysis.json, report_tables.md, cell_table.csv, per_item.csv, gens/, judge_local.jsonl, judge_api.jsonl, configs/frozen_predictions.json, figures/fig1-6, deviations.json (18 deviations, 3 NOT RUN: utility panel, guard ASR, GaMS3 screen).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_13
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 15 ---
id: art_bxpIbe7-nSvR
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Where a refusal edit must land in a Slovene model
summary: |-
  Iteration-4 slot-2 pod, cjvt/GaMS3-12B-Instruct (NF4), 12,024 judged generations, 44 cells, $0.00 OpenRouter spend.

  WHAT IT BUILT. A per-language CAUSAL WRITE PROFILE e_L(h): the judged drop in harmful refusal from applying Heretic's own abliteration operator at ONE decoder layer with the frozen d_EN(h), measured on DEV items only (40 harmful per language). A pre-freeze pilot on DEV showed a single layer at Heretic's own bound moves almost nothing (max drop 0.05 at c=1, 0.10 at c=1.5), so the profile was measured at c=2.5 (max drop 0.65, zero degenerate output) - recorded as deviation D1. The profile peaks sharply at hidden index 27 in both languages; band mass EN 0.00/1.05/1.50/0.27 and SL 0.02/0.55/0.57/0.05 over bands 1-12/13-24/25-36/37-48. Split-half reliability is 0.812 (EN) but 0.312 (SL), so by the pre-registered rule the SLOVENE PROFILE IS DECLARED UNRELIABLE and its argmax prediction demoted to exploratory BEFORE the freeze. Frozen into O = sum_h e_L(h) g(h)/||g||_2 with 28 cell specifications, predicted O and rank, the named band and the thresholds, hashed into configs/FREEZE.sha256; the confirmation entry point raises without it (proved adversarially in results/gate_freeze.json).

  WHAT SURVIVED OUT OF SAMPLE (verdict PARTIAL, pre-registered ladder). Over 20 matched-energy confirmation cells (12 edited layers each, energy matched within 0.6%, 70 held-out-category StrongREJECT pairs per language) Spearman(O_SL, surviving Slovene strict refusal) = -0.903, CI [-0.928,-0.857], permutation p<0.001; within each energy level separately -0.967 (E2) and -0.948 (E3). Nested over log removal energy: dR2 0.580, leave-one-cell-out 0.594. O beats log energy (-0.384), depth span (-0.039) and mean depth (-0.328) with paired-bootstrap CIs excluding zero. All six controls (3 layer-matched random, 3 energy-matched PC draws, energy matched to 0.03%, collateral inside the real cells' range) are null: |dSL| <= 0.03 against a no-op of 0.957.

  THE THREE BOUNDARIES THE PAPER MUST CARRY. (1) THE EXPENSIVE INSTRUMENT DOES NOT EARN ITS COST: the same overlap from a FOUR-number band profile (LOO dR2 0.845) and the purely geometric EN/SL cosine overlap (0.834) beat O's 0.594, and the same cell's English outcome predicts the Slovene one at rho 0.945 - indistinguishable from O. The 48-layer profile establishes THAT placement matters, not the cheapest way to measure it. (2) THE NAMED BAND LOST: the DEV argmax names 25-36, but at matched energy band 13-24 removes more judged Slovene refusal (0.30 vs 0.53 at E=27.8) - NAMED_AND_LOST at both levels. The reason is a metric flip: the 33-substring opener rule ranks 25-36 first, judged STRICT ranks 13-24 first, judged BROAD ranks 25-36 first; band 25-36 buys its opener-rule 'success' with PARTIAL responses (mean strict-minus-rule gap 0.182, max 0.514). (3) NOT CHECKPOINT-SPECIFIC ON THESE SCREENS: the GaMS3 profile predicts the sibling checkpoint's 50 weight cells at -0.442, no worse than its own panel's -0.278; both screens are weak because unmatched panels let dose swamp placement.

  PLACEMENT VS DOSE. The A1-A4 ladder (shipped edit, sibling kernel, and each rescaled to the other's energy) sits at the refusal floor: dose moves the outcome at fixed placement (-0.186 and -0.157, McNemar p 0.001/0.003) while placement does not at fixed dose (-0.029, 0.000). A declared POST-FREEZE exploratory pair at E=13.9/27.8 confirms the two production kernels are indistinguishable once dose is matched (d 0.071 and 0.029, CIs including zero) - both spread mass over the effective band. Both accounts are real in their own stratum: placement orders cells at fixed dose, dose lowers refusal by 0.114 at fixed placement.

  JUDGE HONESTY. The budgeted gpt-4.1 certification could NOT be bought (platform key hit its daily limit; $0.00 spent, deviation D10), so certification fell back to on-disk gpt-4.1 labels for GaMS3 edited arms: harmful-row kappa SL 0.830 (PASS, confirmatory) and EN 0.721 (MISS, JUDGE_SENSITIVE, blocked from confirmatory reading). A free third channel (the iteration-3 refusal classifier) run on THIS pod's own cells agrees item-wise at kappa 0.66 SL / 0.43 EN but reproduces the cell-level ordering at Spearman 0.975 / 0.954, so no claim here depends on the scorer.

  AUDIT. rederive.py reproduces 352/352 headline numbers through a code path importing nothing from the analysis, and in that same path both placebos collapse (cell-permutation null +0.003, energy-profile-shuffled null -0.017, both p<0.0001 against the real -0.903); the freeze predates every confirmation file. 10 deviations with evidence files. Reusable by later rounds at their relative paths: configs/frozen_predictions.json (the instrument), results/cells/ (all judged generations and per-layer energy profiles), results/cells.csv, results/per_item.parquet, figures/fig1-fig5.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_14
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 16 ---
id: art_F46S3uP80BUa
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Can a refusal optimiser see its own refusals?
summary: >-
  Replay-only measurement study of Heretic's 33-substring keyword refusal objective (K) on BOTH Heretic searches of this run:
  gemma-3-12b-it (re-scored from art_0XmNBGkzsJc_'s 11,600 in-loop generations) and cjvt/GaMS3-12B-Instruct (replayed here,
  116 trials + unedited baseline, all 116 bit-exact to the iteration-1 journal on an L4). The reference is the certified partial-aware
  classifier C (threshold 0.52), plus the frozen 4-way judge rubric (Qwen3-14B workhorse). GATES: 60/60 startup draws identical
  in both searches (paired design). Judge vs a bought gpt-4.1 subsample: kappa 0.850 [0.772, 0.911], n = 800, $0.86. Classifier
  on GaMS3 without refit: kappa 0.841 [0.745, 0.910]; keyword 0.591. RESULTS: the frozen primary prediction (Gemma's objective
  is blinder, measured by the pairwise gradient-blind fraction GBF on the 60 paired draws) is FALSIFIED. C-referenced GBF
  is 0.006 vs 0.000, difference +0.006 [0, 0.019]. Judge-referenced, the sign reverses: -0.029 [-0.060, -0.005]. Both objectives
  are monotone at a coarse scale: GBF is far below the permutation chance level, split-half placebo is small, and the self
  placebo is 0. What differs is calibration: K on J slope 0.32 vs 0.81, mean K-J +19.6 vs +6.0, floor 72 vs 16. Low-region
  blindness also differs: GBF among C<=50 candidates is 0.47 vs 0.02 (judge-referenced 0.48 vs 0.22). What is SHARED is structural
  threshold blindness: the objective floor sits above the frozen selection rule's 10/100 threshold, so TBF = 1.00 in both
  searches under both references. The rule falls back to 'fewest keyword refusals'. On Gemma that fallback picks an under-edited
  candidate (judged 63/100). On GaMS3 it picks a fully suppressed candidate at about 3x the KL of the judge's pick (0.175
  vs 0.060). Reselection within each search's own pool changes the selection, i.e. mis-scoring, not mis-searching. No edit
  is recommended (P7 stands). Incumbent's best shot: the oracle count threshold (t=2) gives kappa 0.57 (Gemma) and 0.66 (GaMS3).
  Dropping the 5 content words + empty rule gives 0.17 on Gemma (no fix) but 0.68 on GaMS3 (MAE 4.6, the best GaMS3 count
  accuracy). CAVEAT: the classifier undercounts GaMS3 mid-range refusals (mean C-J -6.8 on the certification trials; count
  MAE 8.7 vs keyword 6.7), so judge-referenced numbers are the robustness check on GaMS3. Held-out StrongREJECT (Gemma): keyword
  kappa 0.02 on edited English, 0.00 on Slovene (English-only list). FILES: results/per_candidate.csv (232 candidates: K,
  C, J, sigma_K, KL, descriptors, flags); results/analysis.json; results/reselection_table.csv; results/conventional_table.csv;
  certification JSONs; results/replay/ (GaMS3 generations); results/judge_out/ (Qwen + gpt-4.1 labels); figures fig1-fig6.
  Audits: rederive.py 81/81 re-derived with 0 mismatches (stdlib+numpy); placebo_audit.py (placebos fail as required); 18
  deviations incl. post-hoc J3 selection-point labels and a per-pair-tolerance sensitivity. Two searches, one seed each; AdvBench-derived
  in-loop set.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_15
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

--- Item 17 ---
id: art_hBuck7q0dnxG
type: evaluation
in_dependencies:
- id: art_ex4hbgThhJaL
  label: generations
- id: art_xLy2vVlI7OEL
  label: generations
- id: art_0XmNBGkzsJc_
  label: generations
- id: art_kfCCWf7o8eJ9
  label: generations
- id: art_m6pglf516e2r
  label: guard pipeline
- id: art_a4VkEvYRquBO
  label: probe scores
- id: art_qdUCJWbc5kHh
  label: dataset
title: Partial answers, judges, and a full recount
summary: >-
  Re-analysis and audit of 56,866 judged generations pooled from five panels (the four iteration-3 panels reconcile exactly
  to 51,353 distinct judged generations; plus the iteration-2 FINAL panel). Predictions, estimators, the Holm family, seeds,
  the judge gate, a 900-item stratified calibration sample and a pre-hoc power simulation were frozen and hashed before any
  fit (configs/FREEZE_iter4_eval.json). C3 (PARTIAL transition): C3-i holds (PARTIAL share non-flat: max-min EN .346 [.257,.539],
  SL .271 [.090,.323]). C3-ii is not supported: the proportional-odds check fired, so the nonparametric argmax is primary,
  giving Delta_peak L1 +.45 [-.45,.90] and L2 +.98 [-.98,2.00]. C3-iii is not supported (out-of-panel Spearman -.43, permutation
  p .34). C3 is therefore FALSIFIED under the frozen rule. This is estimator-sensitive: in L1 the continuation-ratio fit gives
  +.35 [.20,.43] and the PO fit +.36 [.28,.43]. The strict-minus-broad identity is stated, not claimed as a finding. JUDGE:
  515 bought gpt-4.1 labels plus 385 free ones. Within-edited kappa EN .871/.858 (gate MET); SL .871 weighted / .723 sample
  (gate NOT MET, so Rogan-Gladen companions are reported). Keyword rule kappa .07; distilled classifier .92. A declared post-freeze
  supplement (160 labels) exposes exp11 EN kappa .23: workhorse REFUSED labels there are mostly gpt-4.1 PARTIAL. Re-expressing
  the cells in gpt-4.1 classes leaves both C3 and the exp11 gaps intact (.68->.63). 40/211 gap claims are JUDGE_SENSITIVE
  and 105 DEFINITION_SENSITIVE. SCOPE: NF4 guard pass (Llama-Guard NF4 vs bf16 agreement .967). In the Gemma edit, SL non-refusals
  are more often guard-safe than EN (+.23 [.12,.35]): non-actionable rather than compliant. Flip analysis for Gemma: slope
  reduced but not collapsed (.50 EN, .34 SL), intercept -6.7/-5.3, refit AUROC .997, i.e. a criterion shift plus partial coupling
  loss while the information survives. GaMS3 is not estimable. NF4 vs bf16: weight error .093, yet the edit-energy profile
  cosine is .999998; 32-token KL .11/.09; bf16 behavioural paired gap +.60 [.40,.80] vs NF4 +.45 [.20,.70], so the effect
  is bounded, not closed. Paste-ready repairs R1-R10 with source paths (lint 0), including the iteration-1 section restored
  verbatim. The independent stdlib recompute of 102 iteration-3 numbers finds 4.9% [2.1,11.0] wrong; all placebos collapse.
  Spend $0.92.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_evaluation_2
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
- reproducibility.md

--- Item 18 ---
id: art_sZ5w0yoY9o6L
type: research
title: Finding the closest prior work for two results
summary: >-
  Positioning artifact (web research only; no code, no GPU, no paid API, $0 spend) that gives both of this run's reportable
  results the neighbours the reviewer said they lacked. Deliverables in results/: a 30-row neighbour table (markdown + JSON,
  N1-N30) where every row carries a verbatim <=40-word quote with its locator, a URL, an access date (2026-09-24) and a verified
  flag; two paste-ready positioning paragraphs (positive and negative) each stating its own stopping point; a 30-row claims_to_position.csv
  in which no claim is left without either a neighbour id or an evidenced NO NEIGHBOUR FOUND; reconciliation_map.csv (claim
  id -> neighbour ids -> producing file path -> tag -> paper sections that must agree); a tagged ledger separating 14 FAILED
  HYPOTHESES (each with the number and direction that killed it) from 10 UNEXECUTED PROPOSALS (each with its reason); the
  canonical stopping-points block for verbatim reuse; the full search log; and scripts/self_check.py, which passes. KEY OUTCOMES
  FOR THE PAPER. (1) The inherited '2-3 middle layers' attribution is RESOLVED: the sentence does exist in arXiv 2607.02714
  SS3.2, but as that paper's own attribution to Arditi et al. - which was not found in Arditi et al. by full-text search -
  and 2607.02714 rejects it in the next sentence, having found uniform layer spread beats signal-norm-based selection by up
  to ~70pp. It must not be cited as a standing depth fact. (2) The positive's delta is NARROWED: effect-based site selection
  (Hase 2023; 2609.22135; 2606.00926) and language-specific safety depths (2609.22144; 2605.23036) are already published.
  What survives is the matched-total-energy AND matched-layer-count placement contrast, per language, with the effective region
  differing between two sibling checkpoints - no neighbour found running that construction. (3) The negative now has four
  partial neighbours (Hase 2023; 2606.00926; 2609.04721 on cosine unreliability; 2608.24988 on weight-edit geometry surviving
  behavioural reversion) and an EVIDENCED ABSENCE for the conjunction, with the eight queries behind it logged; the wording
  prescribed is 'not found by these queries'. (4) The selection-blindness finding must be positioned against AdvPrefix (2412.10321),
  not StrongREJECT: AdvPrefix owns objective misspecification inside an optimiser for prompt attacks, so this run's claim
  is the weight-edit instance quantified on the search's own candidate population. (5) Tooling state, dated 2026-09-24: Heretic's
  default scorer on master is still the 33-marker substring counter plus KL over an English prompt set, although a benchmark
  scorer (PR #444, merged Sep 3 2026) and dataset config selection (PR #445, merged Sep 5 2026) are merged, and the community
  multilingual set covers 9 languages with no Slovene. Every line is tagged OBSERVATION / INTERPRETATION / FAILED HYPOTHESIS
  / UNEXECUTED PROPOSAL, and every number about this run carries the path of the file that produced it.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_research_1
out_expected_files:
- research_out.json
- reproducibility.md
</all_artifacts>

<previous_round_strands>
How you classified the PREVIOUS round's artifacts, one per bet. Use it for the
BROKEN-FIXED-ONCE rule: a bet that was "broken" then and is "broken" again now is
not a defect any more — drop it and give its slot to a new candidate. A "lead" that
you already deepened once and that came back "null" is the one case where widening
off a lead is allowed.

--- Strand 1 ---
artifact: art_xLy2vVlI7OEL
state: genuine_positive
why: >-
  At matched energy AND matched layer count, placement decides: SL 0.24 vs 0.81 (E3), CIs exclude 0, Holm p 0.000; nested
  R2 placement 0.718 vs count 0.400; controls null; 481/481 re-derived.

--- Strand 2 ---
artifact: art_0XmNBGkzsJc_
state: genuine_positive
why: >-
  Keyword counter never leaves 72-100/100 across all 116 draws while judged refusal spans 7-98/100; MAE 30.6 vs 2.1 per 100;
  kappa +0.196 vs 0.858 certified; 11,600 in-loop gens, 305/305 audited.

--- Strand 3 ---
artifact: art_ex4hbgThhJaL
state: lead
why: >-
  P1/P2 rejected under power (dR2 0.040, LOO -0.002, MDE 0.071). Band-density rho -0.942 survives placebo but SL regression
  coefficient +0.156 [-0.240, 0.529]; one model, exploratory.

--- Strand 4 ---
artifact: art_kfCCWf7o8eJ9
state: lead
why: >-
  Index claim dead (rho -0.009 over 21 rows), but two cheap baselines beat it and cosine with CIs excluding 0 (rho +0.732,
  +0.661); judge below its own gate at kappa 0.683.

--- Strand 5 ---
artifact: art_Z3I1K3VnFZuz
state: lead
why: >-
  Executed bound on our own headline: strict gap +.22-+.71 vs broad -.04-+.37, S5X +.69 -> +.23, PARTIAL .548; 8 mismatches
  and 2 sign-reversals in 167 numbers; within-edited kappa .779 vs .913 pooled.
</previous_round_strands>

<new_artifacts_this_iteration>
These 5 artifacts were created THIS iteration.

id: art_NpZ_nW6qgSKD
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Where a refusal edit lands decides what survives
summary: |-
  WHAT WAS RUN. A frozen, DEV-only causal write profile e_L(h) (judged refusal drop from ablating the frozen English refusal direction d_EN(h) at ONE hidden index, 44 JBB half-A items/language, 48 sites) defines an overlap instrument O_L(edit)=sum_h e_L(h)g(h)/||g|| over each Heretic-family weight edit's closed-form per-layer removal energy g(h). O is invariant to coefficient rescaling, so it measures placement only. O was frozen (hashed, mtime-checked) and tested out of sample on google/gemma-3-12b-it NF4: 29 conditions x 60 frozen held-out items/language (40 StrongREJECT held-out-category + 20 verified RefusEU EN-SL pairs). The conditions were 8 matched groups (high-O vs low-O windows at IDENTICAL closed-form energy and IDENTICAL layer count), energy-matched write-space random and harmless-PC controls, a dose ladder and a no-op. Outside family: Qwen3-8B (EN/SL/DE; LT excluded by the pre-registered gate), 3 matched groups + controls. 10,000 generations were judged 4-way (REFUSED/PARTIAL/COMPLIED/INVALID) by local Qwen3-14B on the frozen exp4 rubric; the gate used 800 gpt-4.1 labels ($0.97).

  RESULTS. (1) FROZEN VERDICT: FALSIFIED for the instrument claim. O's incremental R2 over the pre-declared nuisance stack is 0.026 EN (powered, MDE 0.047) and 0.052 SL (inconclusive band), below the 0.05 falsifier, because the g-weighted EN/SL direction cosine is collinear with O (rho 0.81/0.76; R2 alone 0.83/0.63 vs O 0.87/0.75). (2) PLACEMENT IS STRONGLY CONFIRMED. The high-O member leaves less refusal in 8/8 groups in both languages (pooled EN -0.69 [-0.75,-0.62], SL -0.38 [-0.46,-0.31]; best: layers 16-31 EN 0.07/SL 0.27 vs layers 33-48 0.92/0.92 at the same energy). Random/PC controls stay within +-0.03 of the no-op, and a 2x dose of the late-layer edit still leaves EN 0.88/SL 0.92. (3) O ranks the 18 held-out conditions near-perfectly: Spearman -0.96 EN, -0.83 SL. It beats the unedited refusal rate and the single-site transfer rate on pooled rows (aligned CI [0.28,0.65], [0.29,0.76]), beats the single-site peak probe in EN (+0.17 [0.14,0.23]) and ties it in SL. (4) The language-label placebo does NOT collapse (EN profile predicts SL residual at -0.94), so the language-specific claim is demoted: O works by locating a shared mid-depth band (argmax prediction band 13-24 passes). (5) Under the best-placed edit the EN/SL gap is a strict-vs-broad effect (strict 0.07 vs 0.27, broad 0.53 vs 0.53; ASR-by-rubric 0.93 vs 0.72). (6) Qwen3-8B replicates placement: 9/9 matched contrasts favour high-O (8/9 CIs exclude 0); Spearman(O) EN -0.76, SL -0.93, DE -0.84; the miss REVERSES there (EN retains more refusal than SL). (7) Screen on 46 exp9 cells: O -0.71/-0.60 but energy dominates (dR2 0.008/0.028). Post-hoc harmless KL is a strong competitor (exploratory).

  JUDGE CAVEATS. Within-edited kappa 0.818 pooled; EN 0.856 passes, SL 0.744 fails, so SL is JUDGE_SENSITIVE (Rogan-Gladen keeps the ranking and enlarges the contrasts). The Gate-2 INVALID probe failed (the judge never labels synthetic incoherence INVALID), so a deterministic validity guard was added before confirmation. Native review pending.

  AUDIT. rederive.py (stdlib+numpy, independent path): 209/209 checks pass, including shuffled-O and label-swapped placebos that fail as required. Files: results/analysis.json, report_tables.md, cell_table.csv, per_item.csv, gens/, judge_local.jsonl, judge_api.jsonl, configs/frozen_predictions.json, figures/fig1-6, deviations.json (18 deviations, 3 NOT RUN: utility panel, guard ASR, GaMS3 screen).
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_13
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

id: art_bxpIbe7-nSvR
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Where a refusal edit must land in a Slovene model
summary: |-
  Iteration-4 slot-2 pod, cjvt/GaMS3-12B-Instruct (NF4), 12,024 judged generations, 44 cells, $0.00 OpenRouter spend.

  WHAT IT BUILT. A per-language CAUSAL WRITE PROFILE e_L(h): the judged drop in harmful refusal from applying Heretic's own abliteration operator at ONE decoder layer with the frozen d_EN(h), measured on DEV items only (40 harmful per language). A pre-freeze pilot on DEV showed a single layer at Heretic's own bound moves almost nothing (max drop 0.05 at c=1, 0.10 at c=1.5), so the profile was measured at c=2.5 (max drop 0.65, zero degenerate output) - recorded as deviation D1. The profile peaks sharply at hidden index 27 in both languages; band mass EN 0.00/1.05/1.50/0.27 and SL 0.02/0.55/0.57/0.05 over bands 1-12/13-24/25-36/37-48. Split-half reliability is 0.812 (EN) but 0.312 (SL), so by the pre-registered rule the SLOVENE PROFILE IS DECLARED UNRELIABLE and its argmax prediction demoted to exploratory BEFORE the freeze. Frozen into O = sum_h e_L(h) g(h)/||g||_2 with 28 cell specifications, predicted O and rank, the named band and the thresholds, hashed into configs/FREEZE.sha256; the confirmation entry point raises without it (proved adversarially in results/gate_freeze.json).

  WHAT SURVIVED OUT OF SAMPLE (verdict PARTIAL, pre-registered ladder). Over 20 matched-energy confirmation cells (12 edited layers each, energy matched within 0.6%, 70 held-out-category StrongREJECT pairs per language) Spearman(O_SL, surviving Slovene strict refusal) = -0.903, CI [-0.928,-0.857], permutation p<0.001; within each energy level separately -0.967 (E2) and -0.948 (E3). Nested over log removal energy: dR2 0.580, leave-one-cell-out 0.594. O beats log energy (-0.384), depth span (-0.039) and mean depth (-0.328) with paired-bootstrap CIs excluding zero. All six controls (3 layer-matched random, 3 energy-matched PC draws, energy matched to 0.03%, collateral inside the real cells' range) are null: |dSL| <= 0.03 against a no-op of 0.957.

  THE THREE BOUNDARIES THE PAPER MUST CARRY. (1) THE EXPENSIVE INSTRUMENT DOES NOT EARN ITS COST: the same overlap from a FOUR-number band profile (LOO dR2 0.845) and the purely geometric EN/SL cosine overlap (0.834) beat O's 0.594, and the same cell's English outcome predicts the Slovene one at rho 0.945 - indistinguishable from O. The 48-layer profile establishes THAT placement matters, not the cheapest way to measure it. (2) THE NAMED BAND LOST: the DEV argmax names 25-36, but at matched energy band 13-24 removes more judged Slovene refusal (0.30 vs 0.53 at E=27.8) - NAMED_AND_LOST at both levels. The reason is a metric flip: the 33-substring opener rule ranks 25-36 first, judged STRICT ranks 13-24 first, judged BROAD ranks 25-36 first; band 25-36 buys its opener-rule 'success' with PARTIAL responses (mean strict-minus-rule gap 0.182, max 0.514). (3) NOT CHECKPOINT-SPECIFIC ON THESE SCREENS: the GaMS3 profile predicts the sibling checkpoint's 50 weight cells at -0.442, no worse than its own panel's -0.278; both screens are weak because unmatched panels let dose swamp placement.

  PLACEMENT VS DOSE. The A1-A4 ladder (shipped edit, sibling kernel, and each rescaled to the other's energy) sits at the refusal floor: dose moves the outcome at fixed placement (-0.186 and -0.157, McNemar p 0.001/0.003) while placement does not at fixed dose (-0.029, 0.000). A declared POST-FREEZE exploratory pair at E=13.9/27.8 confirms the two production kernels are indistinguishable once dose is matched (d 0.071 and 0.029, CIs including zero) - both spread mass over the effective band. Both accounts are real in their own stratum: placement orders cells at fixed dose, dose lowers refusal by 0.114 at fixed placement.

  JUDGE HONESTY. The budgeted gpt-4.1 certification could NOT be bought (platform key hit its daily limit; $0.00 spent, deviation D10), so certification fell back to on-disk gpt-4.1 labels for GaMS3 edited arms: harmful-row kappa SL 0.830 (PASS, confirmatory) and EN 0.721 (MISS, JUDGE_SENSITIVE, blocked from confirmatory reading). A free third channel (the iteration-3 refusal classifier) run on THIS pod's own cells agrees item-wise at kappa 0.66 SL / 0.43 EN but reproduces the cell-level ordering at Spearman 0.975 / 0.954, so no claim here depends on the scorer.

  AUDIT. rederive.py reproduces 352/352 headline numbers through a code path importing nothing from the analysis, and in that same path both placebos collapse (cell-permutation null +0.003, energy-profile-shuffled null -0.017, both p<0.0001 against the real -0.903); the freeze predates every confirmation file. 10 deviations with evidence files. Reusable by later rounds at their relative paths: configs/frozen_predictions.json (the instrument), results/cells/ (all judged generations and per-layer energy profiles), results/cells.csv, results/per_item.parquet, figures/fig1-fig5.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_14
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

id: art_F46S3uP80BUa
type: experiment
in_dependencies:
- id: art_qdUCJWbc5kHh
  label: dataset
title: Can a refusal optimiser see its own refusals?
summary: >-
  Replay-only measurement study of Heretic's 33-substring keyword refusal objective (K) on BOTH Heretic searches of this run:
  gemma-3-12b-it (re-scored from art_0XmNBGkzsJc_'s 11,600 in-loop generations) and cjvt/GaMS3-12B-Instruct (replayed here,
  116 trials + unedited baseline, all 116 bit-exact to the iteration-1 journal on an L4). The reference is the certified partial-aware
  classifier C (threshold 0.52), plus the frozen 4-way judge rubric (Qwen3-14B workhorse). GATES: 60/60 startup draws identical
  in both searches (paired design). Judge vs a bought gpt-4.1 subsample: kappa 0.850 [0.772, 0.911], n = 800, $0.86. Classifier
  on GaMS3 without refit: kappa 0.841 [0.745, 0.910]; keyword 0.591. RESULTS: the frozen primary prediction (Gemma's objective
  is blinder, measured by the pairwise gradient-blind fraction GBF on the 60 paired draws) is FALSIFIED. C-referenced GBF
  is 0.006 vs 0.000, difference +0.006 [0, 0.019]. Judge-referenced, the sign reverses: -0.029 [-0.060, -0.005]. Both objectives
  are monotone at a coarse scale: GBF is far below the permutation chance level, split-half placebo is small, and the self
  placebo is 0. What differs is calibration: K on J slope 0.32 vs 0.81, mean K-J +19.6 vs +6.0, floor 72 vs 16. Low-region
  blindness also differs: GBF among C<=50 candidates is 0.47 vs 0.02 (judge-referenced 0.48 vs 0.22). What is SHARED is structural
  threshold blindness: the objective floor sits above the frozen selection rule's 10/100 threshold, so TBF = 1.00 in both
  searches under both references. The rule falls back to 'fewest keyword refusals'. On Gemma that fallback picks an under-edited
  candidate (judged 63/100). On GaMS3 it picks a fully suppressed candidate at about 3x the KL of the judge's pick (0.175
  vs 0.060). Reselection within each search's own pool changes the selection, i.e. mis-scoring, not mis-searching. No edit
  is recommended (P7 stands). Incumbent's best shot: the oracle count threshold (t=2) gives kappa 0.57 (Gemma) and 0.66 (GaMS3).
  Dropping the 5 content words + empty rule gives 0.17 on Gemma (no fix) but 0.68 on GaMS3 (MAE 4.6, the best GaMS3 count
  accuracy). CAVEAT: the classifier undercounts GaMS3 mid-range refusals (mean C-J -6.8 on the certification trials; count
  MAE 8.7 vs keyword 6.7), so judge-referenced numbers are the robustness check on GaMS3. Held-out StrongREJECT (Gemma): keyword
  kappa 0.02 on edited English, 0.00 on Slovene (English-only list). FILES: results/per_candidate.csv (232 candidates: K,
  C, J, sigma_K, KL, descriptors, flags); results/analysis.json; results/reselection_table.csv; results/conventional_table.csv;
  certification JSONs; results/replay/ (GaMS3 generations); results/judge_out/ (Qwen + gpt-4.1 labels); figures fig1-fig6.
  Audits: rederive.py 81/81 re-derived with 0 mismatches (stdlib+numpy); placebo_audit.py (placebos fail as required); 18
  deviations incl. post-hoc J3 selection-point labels and a per-pair-tolerance sensitivity. Two searches, one seed each; AdvBench-derived
  in-loop set.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_15
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md

id: art_hBuck7q0dnxG
type: evaluation
in_dependencies:
- id: art_ex4hbgThhJaL
  label: generations
- id: art_xLy2vVlI7OEL
  label: generations
- id: art_0XmNBGkzsJc_
  label: generations
- id: art_kfCCWf7o8eJ9
  label: generations
- id: art_m6pglf516e2r
  label: guard pipeline
- id: art_a4VkEvYRquBO
  label: probe scores
- id: art_qdUCJWbc5kHh
  label: dataset
title: Partial answers, judges, and a full recount
summary: >-
  Re-analysis and audit of 56,866 judged generations pooled from five panels (the four iteration-3 panels reconcile exactly
  to 51,353 distinct judged generations; plus the iteration-2 FINAL panel). Predictions, estimators, the Holm family, seeds,
  the judge gate, a 900-item stratified calibration sample and a pre-hoc power simulation were frozen and hashed before any
  fit (configs/FREEZE_iter4_eval.json). C3 (PARTIAL transition): C3-i holds (PARTIAL share non-flat: max-min EN .346 [.257,.539],
  SL .271 [.090,.323]). C3-ii is not supported: the proportional-odds check fired, so the nonparametric argmax is primary,
  giving Delta_peak L1 +.45 [-.45,.90] and L2 +.98 [-.98,2.00]. C3-iii is not supported (out-of-panel Spearman -.43, permutation
  p .34). C3 is therefore FALSIFIED under the frozen rule. This is estimator-sensitive: in L1 the continuation-ratio fit gives
  +.35 [.20,.43] and the PO fit +.36 [.28,.43]. The strict-minus-broad identity is stated, not claimed as a finding. JUDGE:
  515 bought gpt-4.1 labels plus 385 free ones. Within-edited kappa EN .871/.858 (gate MET); SL .871 weighted / .723 sample
  (gate NOT MET, so Rogan-Gladen companions are reported). Keyword rule kappa .07; distilled classifier .92. A declared post-freeze
  supplement (160 labels) exposes exp11 EN kappa .23: workhorse REFUSED labels there are mostly gpt-4.1 PARTIAL. Re-expressing
  the cells in gpt-4.1 classes leaves both C3 and the exp11 gaps intact (.68->.63). 40/211 gap claims are JUDGE_SENSITIVE
  and 105 DEFINITION_SENSITIVE. SCOPE: NF4 guard pass (Llama-Guard NF4 vs bf16 agreement .967). In the Gemma edit, SL non-refusals
  are more often guard-safe than EN (+.23 [.12,.35]): non-actionable rather than compliant. Flip analysis for Gemma: slope
  reduced but not collapsed (.50 EN, .34 SL), intercept -6.7/-5.3, refit AUROC .997, i.e. a criterion shift plus partial coupling
  loss while the information survives. GaMS3 is not estimable. NF4 vs bf16: weight error .093, yet the edit-energy profile
  cosine is .999998; 32-token KL .11/.09; bf16 behavioural paired gap +.60 [.40,.80] vs NF4 +.45 [.20,.70], so the effect
  is bounded, not closed. Paste-ready repairs R1-R10 with source paths (lint 0), including the iteration-1 section restored
  verbatim. The independent stdlib recompute of 102 iteration-3 numbers finds 4.9% [2.1,11.0] wrong; all placebos collapse.
  Spend $0.92.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_evaluation_2
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
- reproducibility.md

id: art_sZ5w0yoY9o6L
type: research
title: Finding the closest prior work for two results
summary: >-
  Positioning artifact (web research only; no code, no GPU, no paid API, $0 spend) that gives both of this run's reportable
  results the neighbours the reviewer said they lacked. Deliverables in results/: a 30-row neighbour table (markdown + JSON,
  N1-N30) where every row carries a verbatim <=40-word quote with its locator, a URL, an access date (2026-09-24) and a verified
  flag; two paste-ready positioning paragraphs (positive and negative) each stating its own stopping point; a 30-row claims_to_position.csv
  in which no claim is left without either a neighbour id or an evidenced NO NEIGHBOUR FOUND; reconciliation_map.csv (claim
  id -> neighbour ids -> producing file path -> tag -> paper sections that must agree); a tagged ledger separating 14 FAILED
  HYPOTHESES (each with the number and direction that killed it) from 10 UNEXECUTED PROPOSALS (each with its reason); the
  canonical stopping-points block for verbatim reuse; the full search log; and scripts/self_check.py, which passes. KEY OUTCOMES
  FOR THE PAPER. (1) The inherited '2-3 middle layers' attribution is RESOLVED: the sentence does exist in arXiv 2607.02714
  SS3.2, but as that paper's own attribution to Arditi et al. - which was not found in Arditi et al. by full-text search -
  and 2607.02714 rejects it in the next sentence, having found uniform layer spread beats signal-norm-based selection by up
  to ~70pp. It must not be cited as a standing depth fact. (2) The positive's delta is NARROWED: effect-based site selection
  (Hase 2023; 2609.22135; 2606.00926) and language-specific safety depths (2609.22144; 2605.23036) are already published.
  What survives is the matched-total-energy AND matched-layer-count placement contrast, per language, with the effective region
  differing between two sibling checkpoints - no neighbour found running that construction. (3) The negative now has four
  partial neighbours (Hase 2023; 2606.00926; 2609.04721 on cosine unreliability; 2608.24988 on weight-edit geometry surviving
  behavioural reversion) and an EVIDENCED ABSENCE for the conjunction, with the eight queries behind it logged; the wording
  prescribed is 'not found by these queries'. (4) The selection-blindness finding must be positioned against AdvPrefix (2412.10321),
  not StrongREJECT: AdvPrefix owns objective misspecification inside an optimiser for prompt attacks, so this run's claim
  is the weight-edit instance quantified on the search's own candidate population. (5) Tooling state, dated 2026-09-24: Heretic's
  default scorer on master is still the 33-marker substring counter plus KL over an English prompt set, although a benchmark
  scorer (PR #444, merged Sep 3 2026) and dataset config selection (PR #445, merged Sep 5 2026) are merged, and the community
  multilingual set covers 9 languages with no Slovene. Every line is tagged OBSERVATION / INTERPRETATION / FAILED HYPOTHESIS
  / UNEXECUTED PROPOSAL, and every number about this run carries the path of the file that produced it.
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_research_1
out_expected_files:
- research_out.json
- reproducibility.md
</new_artifacts_this_iteration>

<current_paper>
The paper draft from this iteration — represents the current state of the research story.

# What English-tuned abliteration misses in Slovene

## Framing

Abliteration removes refusal behaviour from language models by orthogonalising weight matrices against a "refusal direction" extracted from English harmful-vs-harmless contrasts [1]. The procedure was introduced by Arditi et al. [1] and automated by tools such as Heretic, which uses TPE search over layer, position, direction index, and LoRA rank to find abliteration configurations that minimise an English refusal objective while bounding KL divergence from the original model. The question motivating this study is whether that English-centred objective leaves Slovene refusal behaviour uncontrolled. If the English refusal direction is universal across languages, as Wang et al. [2] report for safety-aligned models evaluated across 14 languages, then abliteration tuned on English should transfer to Slovene. If instead Slovene refusal relies partly on representations that the English objective does not observe, a gap will remain. The practical consequence is that a model abliterated to comply in English might still refuse in Slovene, or might lose Slovene capabilities that the English-only KL constraint does not protect.

Several concurrent lines of work inform this question. BabelSteering [4] and Yoon et al. [5] show that safety alignment imposes disparate costs across languages, with non-English users bearing higher utility loss. Aziz et al. [6] diagnose the breakdown point for low-resource safety as an action failure rather than a representation failure: the model encodes harmfulness correctly but fails to convert the representation into refusal. Wu et al. [7] formalise this as a disentangled safety hypothesis, separating a recognition axis from an execution axis. On the abliteration side, Fafula [8] documents off-target effects of refusal removal across model families, and Young [14] and Petrov [15] compare abliteration methods across architectures. Upadhyaya and Sikdar [9] analyse how safety and language identity become entangled, while Hawkins et al. [10] show that benign multilingual fine-tuning has heterogeneous safety impacts. Labunets [11] demonstrates that refusal geometry reflects refusal training diversity. On quantisation effects relevant to our NF4 setup, Marchisio et al. [12] and Chimoto et al. [13] show that quantisation calibration language matters for multilingual performance. Tang et al. [16] identify language-specific neurons, and Ghussin et al. [17] propose principled layer selection for multilingual steering. Frank [18] argues that refusal-based alignment evaluation conflates detection with routing.

We study this question in a controlled bilingual setting using two sibling 12B models from the Gemma-3 family: google/gemma-3-12b-it (the English-centric reference) and cjvt/GaMS3-12B-Instruct (a Slovene continual-pretraining and SFT variant of the same architecture). Both are loaded in bnb_4bit NF4 quantisation throughout. The study proceeds in four iterations. Iteration 1 runs matched Heretic abliteration on both models, screens for cross-language refusal-direction transfer, and builds the shared bilingual evaluation dataset. Iteration 2 uses that dataset to measure the surrogacy gap (what English outcomes fail to predict about Slovene), test causal mechanisms, and evaluate safety and utility on held-out benchmarks. Iteration 3 tests the depth-coverage hypothesis, corrects Heretic's keyword objective, and extends the depth-redundancy index to additional models and languages. Iteration 4 measures the causal write profile in both models, tests the overlap instrument, quantifies gradient blindness of the keyword objective, and audits all prior claims.

[FIGURE:fig_behaviour_summary]



## Iteration 1

[Correction, iter 4: The previous drafts omitted substantial iteration-1 content that was present in the original report (iter_1/gen_report_text/gen_report_text/report.md). The material below restores the missing tables (same-edit response surface, swap statistics, transfer matrix), the sibling-surface guard, the decision-margin decomposition, the exploratory double dissociation, four labelled dead ends, and iteration 1's own closing assessment. This is a restoration, not new analysis.]

**Strategy.** Iteration 1 had three goals: (a) establish a frozen, audited data protocol covering all planned evaluation splits; (b) run two matched Heretic optimizations under identical conditions to produce the four core checkpoints, score them bilingually, and characterise the same-edit response surface across the two models; and (c) screen the refusal-direction transfer hypothesis with a 2×2 source-language by evaluation-language ablation matrix, a Slovene-direction increment test, and matched-efficacy and dose-response controls.

### Experiment 1: Matched Heretic runs [ARTIFACT:art_vzhOPupFwE4M]

**Goal.** Run identical Heretic TPE searches on both models under the same seed, select an abliterated checkpoint for each, and compare the two models' responses to the same edits.

**Setup.** Both models were searched over 116 complete trials (seed 20260923) using Heretic (SHA 3521f864) with the default configuration: orthogonalize_direction=true, row_normalization='full', rank-3 LoRA. The English keyword refusal rate (out of 100 harmful prompts) and mean KL divergence served as Heretic's two objectives. Selection followed a frozen protocol: minimise KL subject to refusals ≤ 10; if no trial met this primary criterion, fall back to minimising refusals subject to KL ≤ 1.0. Both models fell back to the secondary rule.

**Selected trials.** GaMS3 trial 88 reached 16/100 English refusals at KL 0.175. Gemma trial 96 reached 69/100 English refusals at KL 0.024. The Gemma model refused far more often than GaMS3 under identical abliteration parameters, and no Gemma trial achieved ≤ 50/100 refusals. The 13.4× figure is the ratio of medians of refusal drop per unit KL across the 60 shared startup edits (GaMS3 1449 vs Gemma 108 refusals/nat), not a ratio of median refusal counts [Correction, iter 3: clarified definition from evaluation audit]. In all 60 startup edits, Gemma refused at least as often as GaMS3 (60/60, median paired difference +25). In a KL-matched subset (n=30, GaMS3 KL median 0.0101, Gemma 0.0098), GaMS3 median refusal was 65/100 versus Gemma 99/100 [Correction, iter 3: added from evaluation audit].

**Behaviour on the selected trials.** The table below shows keyword refusal rates (out of 100 harmful prompts) and FLORES+ NLL for each checkpoint.

| Model | Checkpoint | EN refusals | SL refusals | KL mean | FLORES NLL EN | FLORES NLL SL |
|---|---|---|---|---|---|---|
| GaMS3 | original | 98 | 97 | 0.000 | 3.332 | 2.570 |
| GaMS3 | own edit (trial 88) | 16 | 10 | 0.175 | 3.334 | 2.566 |
| GaMS3 | swap (Gemma trial 96) | 25 | 25 | 0.046 | 3.336 | 2.576 |
| Gemma | original | 100 | 97 | 0.000 | 4.018 | 3.702 |
| Gemma | own edit (trial 96) | 69 | 90 | 0.024 | 4.012 | 3.703 |
| Gemma | swap (GaMS3 trial 88) | 53 | 25 | 0.254 | 4.011 | 3.712 |

[Correction, iter 3: The Gemma rows above are recomputed from the saved evaluation files. The previous draft reported Gemma orig SL = 100 (actual: 97), Gemma own edit SL = 85 (actual: 90), Gemma swap EN/SL = 91/95 at KL 0.293 (actual: 53/25 at KL 0.254), and FLORES values of 3.930/3.427 etc. that are untraceable in iteration-1 files. The corrected FLORES values come from the 40-sentence devtest means stored in the evaluation JSON files.]

GaMS3's own edit reduced English refusals from 98 to 16 and Slovene refusals from 97 to 10. Slovene refusal dropped even though Heretic optimised only on English, and FLORES NLL changed by at most 0.01. For Gemma, the edit reduced English refusals from 100 to 69 but Slovene refusals only from 100 to 90 (keyword count). [Correction, iter 3: the previous draft reported Gemma own-edit SL as 85; the evaluation audit finds 90.]

The swap results are informative. GaMS3 under Gemma's trial-96 edit showed 25/25 (EN/SL) refusals; Gemma under GaMS3's trial-88 edit showed 53/25 (EN/SL) at KL 0.254 [Correction, iter 3: the previous draft reported 91/95 at KL 0.293; the corrected values from evaluation audit show GaMS3's broader, stronger parameters suppress Gemma's SLOVENE refusal far more than English (SL 97→25 vs EN 100→53), at roughly 10× the KL of Gemma's own edit. This supports the depth/dose reading: a stronger edit of the same base largely transfers to Slovene.].

**Direction geometry.** Across layers 24 to 47, the mean cosine between the two models' diff-in-means refusal directions was 0.57; across all layers it was 0.63. The cosine between their harmless-token directions was 0.98. Random directions gave a mean |cos| of 0.014. The refusal directions are more aligned than chance but far from parallel; the harmless directions are near-identical, consistent with the shared tokenizer and architecture.

**A3 screen (paired startup edits).** The Spearman correlation of refusal counts between the two models across 60 paired edits was 0.78 [0.63, 0.88]. KL divergence correlated at 0.97. However, the incremental variance explained by the sibling model's outcome (dR2_sibling) was near zero for both directions of prediction, meaning the two models' refusal counts are correlated through shared parameters but one model's outcome does not add predictive value over those parameters. The screen verdict was "intermediate" (raw rho 0.781 is below the 0.9 threshold for "shared via strength only") [Correction, iter 3: previous draft said "shared via strength only"; the evaluation audit restores the correct frozen reading].

**Sanity checks.** All 60 startup edits used identical parameter draws (verified). FLORES NLL shifts were ≤ 0.01 for both models. Slovene marker validation on the selected GaMS3 edit showed accuracy 0.75 and kappa 0.48 (fair agreement between keyword markers and the executor's hand labels on 40 items) [Correction, iter 3: previous draft described these as "LLM-judge labels"; they were executor labels, not native-speaker labels].

[Correction, iter 4: The following tables were present in the original iteration-1 report but omitted from subsequent drafts. Restored verbatim from iter_1/gen_report_text/gen_report_text/report.md.]

**Same-edit response surface (60 shared edits, English keyword refusal; source: art_vzhOPupFwE4M results).**

| Measure | GaMS3 | Gemma |
|---|---|---|
| Refusals median | 74.5 | 99.0 |
| Refusals range | [25, 99] | [71, 100] |
| KL median | 0.0079 | 0.0057 |
| Efficiency (refusal drop / KL) | 1,449 | 108 |
| Efficiency ratio | 13.4× (CI [7.0, 30.0]) | |
| Edits where Gemma refuses more | 60/60 | |
| Paired refusal diff median | +25 (CI [10, 43]) | |
| KL Spearman rho | 0.967 (CI [0.93, 0.98]) | |
| KL partial rho (controlling kernel mass) | 0.923 | |

**Sibling-surface guard.** The incremental R-squared of the sibling model's refusal over the shared edit parameters was near zero for refusal (dR2 0.008, CI [-0.017, 0.055] and -0.006, CI [-0.028, 0.018]) but positive for KL (dR2 0.143, CI [0.074, 0.246] and 0.154, CI [0.093, 0.242]). The two models share how edits damage harmless computation (KL) but not how that damage translates into refusal change.

**Swap tests (source: art_vzhOPupFwE4M results).**

| Model | Comparison | EN diff | EN p | SL diff | SL p | KL ratio (own/swap) |
|---|---|---|---|---|---|---|
| GaMS3 | own vs swap | -0.09 | 0.078 | -0.15 | 2.7e-4 | 3.80 (CI [3.13, 4.69]) |
| Gemma | own vs swap | +0.16 | 0.020 | +0.65 | 5.4e-20 | 0.095 (CI [0.046, 0.189]) |
| GaMS3 | orig vs own | +0.82 | 4.1e-25 | +0.87 | 2.9e-25 | — |
| Gemma | orig vs own | +0.31 | 9.3e-10 | +0.07 | 0.016 | — |

GaMS3's trial-88 parameters applied to Gemma suppressed Slovene refusal far more than English (SL 97→25 vs EN 100→53, McNemar p < 1e-19 for SL), consistent with the depth/dose reading: a stronger edit transfers to Slovene.

**Dead ends from iteration 1:**

1. **Blocked Slovene LLM judge.** The OpenRouter API key returned HTTP 403 on every request, including a 4-token probe. Zero of 600 planned judgements succeeded; all Slovene numbers rest on keyword-marker lists with moderate agreement (kappa 0.48) against executor hand labels. This limits all iteration-1 Slovene refusal counts to development-grade measurements.
2. **Collateral-confounded Slovene increment.** The GaMS3 Slovene-direction increment (F_raw = 0.228, F_ctrl = 0.195) is confounded with collateral damage: full-span ablation of the Slovene direction destroyed utility (FLORES NLL +1.4 nats per token, ~35% malformed outputs). The increment is uninterpretable for GaMS3. For Gemma, the increment was zero.
3. **Cut sensitivity arms.** Priority-3 sensitivity arms (S1-derived, per-language-best-layer, and content-token directions) were not executed for time.
4. **Halved Gemma candidate grid.** The full 145-candidate grid (15 layers × candidates) was run for GaMS3, but the Gemma grid was halved (every 2nd layer, only positions -1 and -5) for GPU time constraints.

**Limits.** Two models are two units. Nothing here attributes the asymmetry to Slovene continual pretraining, instruction tuning, or any training stage. GaMS3 is a same-family reference, not a controlled derivative of this Gemma checkpoint. The Gemma arm's resistance to abliteration is confounded with 4-bit NF4 quantization and the reduced 116-trial budget: the published bf16 200-trial Heretic edit of gemma-3-12b-it reaches 3/100 EN refusals [14], so this is not evidence that Gemma resists abliteration in general. One optimizer seed per model; prompt-level CIs do not capture run-to-run optimizer variance.


### Dataset construction [ARTIFACT:art_qdUCJWbc5kHh]

**Goal.** Build a frozen bilingual (EN/SL) evaluation dataset that spans safety, utility, and mechanistic probing, using matched translation quality controls.

**Result.** The dataset contains 48,696 rows across 10 blocks (S1 to S7 families): S1 (Heretic direction/KL calibration, 2000 rows), S2 (semantic harmful/harmless pairs, 1664), S3 screen prompts (540 prompts + 640 utility items), S4 (StrongReject harmful/harmless twins, 1028), S5 (RefusEU [3], 2800), S5X (RefusEU cross-translations, 1400), S6 (XSTest over-refusal, 900), S7 (Slovenian LLM eval tasks including ARC, BoolQ, HellaSwag, 35,700; FLORES+ devtest, 2024). Protocol hash: dc33bde4.

**Translation.** Slovene translations were produced by Gemini-2.5-flash (temperature 0) as the primary translator, with NLLB-200-distilled-1.3B as fallback for 8 rows where Gemini refused. Mean back-translation chrF was 81.25; 3 rows fell below chrF 40. Mean LaBSE cross-lingual similarity was 0.856. Quality control was automated only (back-translation chrF, LaBSE, GlotLID); no native-speaker review was conducted. S5 (official RefusEU) EN and SL rows that share a row_id are NOT translations (0 of 1,400 pairs grade T); paired cross-language claims therefore use S5X only [Correction, iter 3: provenance note added from evaluation audit].

**Splits.** Items are assigned to halves A and B by SHA-1 hash of their semantic ID. This split is used throughout iteration 2 for placebo-controlled surrogacy analyses: English traits computed on half A predict English (placebo) and Slovene (test) on half B.



### Experiment 3: A1 screen, EN vs. SL refusal-direction transfer [ARTIFACT:art_jxrJNc9o4QSp]

**Goal.** Screen whether the English-extracted refusal direction transfers to Slovene, using a 2×2 matrix (source language × evaluation language), increment tests, and multiple controls. This was a screen, not a confirmatory test.

**Setup.** For each model, the experiment extracted refusal directions from half-A items using diff-in-means on harmful vs. harmless activations, separately for English and Slovene. It then applied 15 ablation conditions per model (activation steering at inference) to half-B items and measured refusal rates using keyword markers and an LLM judge. The judge was gpt-4.1 for all 1,596 outputs [Correction, iter 3: previous draft described a Qwen3-14B second judge for part of the outputs; the evaluation audit finds gpt-4.1 was the sole judge for exp3].

**Precision deviations.** Several deviations from the original plan were recorded. The Gemma candidate grid was cut to every-second layer and positions {-1, -5} for GPU time constraints. Translation used a system/user wrapper prompt because bare Gemini prompts elicited refusal. NLLB served as fallback for 22/1070 translation rows. Winsorization (q = 0.995) was applied to directions because one massive-activation dimension dominated the raw diff-in-means.

**Validity gates.** The R validity gate (refusal readout Spearman correlation with judged refusal across 16 conditions) passed for Gemma (Spearman 0.91, AUROC 0.96) but failed for GaMS3 (Spearman 0.51, AUROC 0.70). The GaMS3 failure means the keyword-based refusal readout did not track actual refusal behaviour well enough for the screen's quantitative tests to be trusted. Per the frozen protocol (rule F6), the screen's primary outcome falls to the judged refusal rate for GaMS3.

**Judged 2×2 table (gpt-4.1).** [Correction, iter 3: added from evaluation audit]

| Model | Condition | EN | SL |
|---|---|---|---|
| GaMS3 | C0 no-op | 0.90 | 0.93 |
| GaMS3 | C1 d_EN | 0.46 | 0.34 |
| GaMS3 | C2 d_SL | 0.07 | 0.10 |
| Gemma | C0 no-op | 0.83 | 1.00 |
| Gemma | C1 d_EN | 0.07 | 0.85 |
| Gemma | C2 d_SL | 0.29 | 0.93 |

[Correction, iter 3: the previous draft reported Gemma EN baseline as "99%"; the gpt-4.1 judged rate is 0.83. The d_EN ablation took Gemma EN from 0.83 to 0.07 while SL stayed at 0.85; d_SL took EN to 0.29 and SL to 0.93. The difference-in-differences for Gemma under d_EN is +0.61 [0.41, 0.78]: the Slovene drop was 0.61 units smaller than the English drop.]

**GaMS3 results.** Because the R validity gate failed, quantitative screen results for GaMS3 are exploratory. d_EN reduced GaMS3 from 0.90/0.93 (EN/SL) to 0.46/0.34, showing near-parallel reduction across languages. The DiD was -0.15 [-0.32, 0.02], not significantly different from zero.

**Gemma results.** The Gemma validity gate passed. Applying the English refusal direction d_EN removed most English refusal (0.83 to 0.07) but Slovene refusal survived at 0.85. This is the first signal that the English direction misses Slovene refusal in Gemma.

**Screen verdict.** WEAK. The predicted cross-language transfer contrast was reversed for Gemma. For GaMS3, the validity gate failure prevented a quantitative verdict. The screen provided the initial signal that English abliteration may miss Slovene refusal, motivating the confirmatory analyses in iteration 2.

**Matched-efficacy grid.** Conditions rescaled so that English refusal dropped by equal amounts showed that Slovene refusal systematically persisted more than English refusal at every matched English decrement. The Heretic bridge mean gap was GaMS3 0.109 [0.06, 0.17] and Gemma 0.235 [0.16, 0.30] [Correction, iter 3: numbers from evaluation audit].

**Addition dose-response.** Increasing the steering coefficient (scaling up the English refusal direction) reduced both English and Slovene refusal, but Slovene always lagged behind English: at every dose level, Slovene retained more refusal than English.

[Correction, iter 4: The following tables were present in the original iteration-1 report but omitted from subsequent drafts. Restored from iter_1/gen_report_text/gen_report_text/report.md.]

**Transfer matrix: fraction of same-language refusal drop achieved by cross-language direction (source: art_jxrJNc9o4QSp results).**

| | Evaluated in EN | Evaluated in SL |
|---|---|---|
| **GaMS3** | | |
| EN-derived direction | 1.00 | 0.96 (CI [0.93, 0.98]) |
| SL-derived direction | 0.81 (CI [0.79, 0.82]) | 1.00 |
| **Gemma** | | |
| EN-derived direction | 1.00 | 3.47 (CI [2.76, 4.90]) |
| SL-derived direction | 0.66 (CI [0.61, 0.70]) | 1.00 |

GaMS3 shows near-symmetric transfer: the English direction achieves 96% of the Slovene direction's Slovene effect. Gemma shows a pathological asymmetry: the English direction achieves a 3.47× overshoot in log-odds terms on Slovene. The explanation is Gemma's Slovene refusal margin. Gemma's baseline Slovene refusal log-odds is 13.9, compared to 3.6 for English. Even a direction with cosine 0.92 to the Slovene one, operating on a margin that wide, achieves almost nothing in behavioural terms.

**Exploratory: GaMS3 double dissociation under direction addition.** Adding the English-derived direction to GaMS3 activations at strength 1.0 shifted English refusal log-odds by +3.54 (CI [2.96, 4.09]) with negligible Slovene effect (-1.11, CI [-1.22, -1.01]). Adding the Slovene-derived direction shifted Slovene by +2.23 (CI [1.97, 2.49]) with a smaller English effect (-1.54, CI [-1.91, -1.16]). This double dissociation is consistent with partially language-specific refusal directions in GaMS3.

### Iteration-1 assessment

The central finding of iteration 1 is a large same-edit asymmetry: on 60 identical edits, GaMS3 loses 13.4 times more refusal per unit KL than Gemma, while the KL damage itself is nearly identical (rho 0.967). The sibling-surface guard confirms that this refusal divergence is not merely inherited from the shared parameter draws. The refusal-direction transfer screen produced a result opposite to the initial prediction: it is Gemma, not GaMS3, that shows a large cross-language transfer gap, with English ablation nearly eliminating English refusal while leaving Slovene nearly intact. The gap is explained not by direction geometry (cosine 0.92 between EN and SL directions in Gemma) but by a massive difference in refusal margins (SL log-odds 13.9 versus EN 3.6). Two concerns carry forward: all Slovene refusal counts are development-grade (keyword-marker agreement kappa 0.48), and the 4-bit quantization confound means absolute refusal rates are not comparable to published bf16 results.


## Iteration 2

Iteration 2 built on the screen results from iteration 1 by running five pre-registered experiments that measured the surrogacy gap, tested causal mechanisms, and evaluated safety and utility on held-out data.

### Experiment 5: Utility and mechanism [ARTIFACT:art_a4VkEvYRquBO]

**Goal.** Evaluate whether the selected abliteration edits preserve utility across both languages and characterise the internal geometry of the harm representation before and after editing.

#### T1: Harmful behaviour (S4 harmful items, 257 per cell)

The table below shows judged refusal rates on held-out harmful items (S4, 257 items per model × checkpoint × language; source: results/t1_harmful.json). The gpt-4.1 judge labelled a random ~52% subsample; remaining items used a second-family free judge (Nemotron-3-ultra-550b); markers show the Heretic keyword rule on all 257.

| Model | Ckpt | Lang | Refused % [95% CI] | Complied % [95% CI] |
|---|---|---|---|---|
| GaMS3 | orig | EN | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] |
| GaMS3 | orig | SL | 100.0 [100.0, 100.0] | 0.0 [0.0, 0.0] |
| GaMS3 | edit | EN | 5.6 [2.4, 9.5] | 92.9 [88.1, 96.8] |
| GaMS3 | edit | SL | 6.7 [3.0, 11.1] | 89.6 [84.4, 94.1] |
| Gemma | orig | EN | 99.3 [97.8, 100.0] | 0.7 [0.0, 2.2] |
| Gemma | orig | SL | 99.2 [97.6, 100.0] | 0.8 [0.0, 2.4] |
| Gemma | edit | EN | 70.3 [61.9, 78.0] | 24.6 [16.9, 32.2] |
| Gemma | edit | SL | 95.3 [92.0, 98.7] | 4.0 [1.3, 7.3] |

For GaMS3, the edit reduced refusal from 100% to ~6% in both languages, with no meaningful EN-SL gap. For Gemma, the edit reduced English refusal from 99% to 70% but left Slovene refusal at 95%. This 25-percentage-point gap (70.3% vs. 95.3%) confirms the pattern seen in the iteration-1 screen: the English-tuned Heretic edit substantially missed Slovene refusal in Gemma.

**Attack success (harmful compliance; source: results/t1_harmful.json).** [Correction, iter 4: added per reviewer MUST-FIX #7.] Among the Complied responses above, the attack success rate (harmful compliance as a fraction of all harmful items) was: GaMS3 edit EN 92.9% [88.1, 96.8], GaMS3 edit SL 89.6% [84.4, 94.1], Gemma edit EN 24.6% [16.9, 32.2], Gemma edit SL 4.0% [1.3, 7.3]. The Gemma EN-SL compliance gap (+20.6 pp) moves in the same direction as the refusal gap but is smaller in magnitude, because many of the "non-refused" Gemma EN responses are PARTIAL (caveat-laden) rather than fully compliant. Language consistency: all GaMS3 cells showed language-consistent output (EN prompts answered in EN, SL in SL); Gemma edit EN was 100% language-consistent, Gemma edit SL was 96.0% [93.3, 98.7] (a small fraction of SL responses switched to English). Invalid and truncated rates were 0.0% across all cells.

Judge agreement: second judge vs. gpt-4.1 on a stratified sample of 200 gave 6-way kappa 0.765, refused-vs-not kappa 0.828, raw agreement 0.885.

#### T2: KL divergence on harmless twins (S4, 128-token generations)

| Model | Ckpt | Lang | KL1 median [95% CI] | KL32 median [95% CI] | Benign refusal % | Malformed % | Empty % |
|---|---|---|---|---|---|---|---|
| GaMS3 | orig | EN | 0 (ref) | 0 (ref) | 0.0 | 0.0 | 0.0 |
| GaMS3 | orig | SL | 0 (ref) | 0 (ref) | 0.0 | 0.0 | 0.0 |
| GaMS3 | edit | EN | 0.0441 [0.0323, 0.0530] | 0.0228 [0.0196, 0.0250] | 0.0 | 0.0 | 0.0 |
| GaMS3 | edit | SL | 0.0174 [0.0152, 0.0211] | 0.0068 [0.0061, 0.0086] | 0.0 | 0.0 | 0.0 |
| Gemma | orig | EN | 0 (ref) | 0 (ref) | 0.0 | 0.0 | 0.0 |
| Gemma | orig | SL | 0 (ref) | 0 (ref) | 9.5 | 0.4 | 0.0 |
| Gemma | edit | EN | 0.0000 [0.0000, 0.0000] | 0.0150 [0.0125, 0.0171] | 0.0 | 0.0 | 0.0 |
| Gemma | edit | SL | 0.0113 [0.0083, 0.0163] | 0.0037 [0.0030, 0.0046] | 0.0 | 0.4 | 0.0 |

KL1 values ranged from 0.011 to 0.044. Gemma EN edit showed KL1 median 0.0000 (at the first token the edit barely changed harmless outputs). Output validity was clean across all cells.

#### T3: Utility (0-shot, 250 items per task per language)

| Model | Lang | Macro original | Macro edited | Change [95% CI] | Holm p |
|---|---|---|---|---|---|
| GaMS3 | EN | 72.5 | 72.7 | +0.13 [-0.53, +0.80] | 1.000 |
| GaMS3 | SL | 64.9 | 65.1 | +0.20 [-0.73, +1.13] | 1.000 |
| Gemma | EN | 71.5 | 71.6 | +0.13 [-0.53, +0.80] | 1.000 |
| Gemma | SL | 62.1 | 62.1 | +0.00 [-0.60, +0.60] | 1.000 |

All macro changes were ≤ 0.20 points. All Holm-corrected p-values were 1.000 over the 4 macro comparisons. Individual task changes ranged from -1.20 to +1.60 points; none reached significance. The edits did not measurably alter utility in either language for either model.

#### T4: FLORES+ per-token NLL

| Model | Lang | NLL original | NLL edited | Change [95% CI] |
|---|---|---|---|---|
| GaMS3 | EN | 3.3072 | 3.3068 | -0.0004 [-0.0025, +0.0016] |
| GaMS3 | SL | 2.4524 | 2.4526 | +0.0002 [-0.0012, +0.0016] |
| Gemma | EN | 3.9194 | 3.9174 | -0.0020 [-0.0031, -0.0008] |
| Gemma | SL | 3.4289 | 3.4293 | +0.0004 [-0.0007, +0.0016] |

NLL shifts were ≤ 0.002 for all cells. The Gemma English NLL decrease (-0.002) was statistically below zero but negligible in magnitude.

#### T5: Bilingual harm geometry (original models, primary site)

| Model | Layer | cos(d_EN, d_SL) | Corrected | CV AUROC DiM EN/SL | S4 frozen DiM EN/SL | cos(lang dir, d_EN) | Shuffled AUROC |
|---|---|---|---|---|---|---|---|
| GaMS3 | 34 | 0.832 | 0.890 | 0.963 / 0.945 | 0.998 / 0.997 | 0.035 | 0.490 |
| Gemma | 20 | 0.919 | 0.979 | 0.979 / 0.941 | 0.997 / 0.996 | 0.109 | 0.515 |

Cross-validation AUROC on S3 development items exceeded 0.94 for both models in both languages. Cross-language transfer on held-out S4 items exceeded 0.995 in both directions for both models. The harm direction is shared across languages. The language-identity direction is near-orthogonal to d_EN (cos 0.035 and 0.109). Shuffled-label AUROC was at chance (0.49 to 0.52), confirming the directions are not artifacts of data leakage.

Both models encode harmfulness similarly across EN and SL in their representations. The harm direction is shared; the language direction is separate. For Gemma, the behavioural gap (70.3% vs. 95.3% residual refusal) cannot be attributed to a representational difference: the model knows the prompt is harmful in both languages, but acts on that knowledge differently.

#### T6: Frozen vs. refit probes (S4, primary site)

| Model | Lang | Probe | Frozen orig AUROC | Frozen edit-orig [95% CI] | Refit edit-orig [95% CI] | Class |
|---|---|---|---|---|---|---|
| GaMS3 | EN | dim | 0.998 | -0.401 [-0.434, -0.368] | -0.014 [-0.021, -0.007] | INFO-LOSS |
| GaMS3 | EN | lr | 0.999 | -0.596 [-0.623, -0.570] | -0.000 [-0.001, 0.001] | DRIFT |
| GaMS3 | SL | dim | 0.997 | -0.576 [-0.611, -0.542] | -0.043 [-0.056, -0.030] | INFO-LOSS |
| GaMS3 | SL | lr | 0.996 | -0.661 [-0.691, -0.635] | -0.000 [-0.002, 0.002] | DRIFT |
| Gemma | EN | dim | 0.997 | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] | PRESERVED |
| Gemma | EN | lr | 0.996 | -0.001 [-0.002, 0.000] | -0.000 [-0.000, 0.000] | PRESERVED |
| Gemma | SL | dim | 0.996 | -0.000 [-0.001, 0.000] | -0.000 [-0.001, 0.000] | PRESERVED |
| Gemma | SL | lr | 0.989 | -0.002 [-0.003, -0.001] | 0.000 [-0.000, 0.000] | DRIFT |

All-layer profile (minimum frozen-probe AUROC on edited activations):

| Model | Lang | Min frozen-edit AUROC (layer) | Refit AUROC there |
|---|---|---|---|
| GaMS3 | EN | 0.201 (L27) | 0.993 |
| GaMS3 | SL | 0.196 (L27) | 0.987 |
| Gemma | EN | 0.507 (L4) | 0.709 |
| Gemma | SL | 0.492 (L6) | 0.740 |

For GaMS3, the frozen probe collapsed after editing at the primary site: AUROC dropped to 0.201 at the worst layer, but a refit probe recovered to 0.993. The edit re-encoded the harm signal in a different subspace (INFO-LOSS on dim, DRIFT on logistic) rather than destroying it: the information persisted, but in a location the frozen probe could not read [Correction, iter 4: the previous text described this as "destroying the harm signal"; the refit recovery to 0.993 shows re-encoding, not information loss].

For Gemma, the frozen probe was preserved at the primary site (layer 20): AUROC dropped by at most 0.002. However, the all-layer profile shows the frozen probe dropped to 0.507 at layer 4 (EN) and 0.492 at layer 6 (SL), and the frozen-axis Cohen's d decreased from 5.29 to 4.94 (EN) and from 3.76 to 3.50 (SL). The edit's effect on the harm signal was small at the primary site but not zero across depth [Correction, iter 4: the previous text stated "the edit did not move the harm representation"; this understates the all-layer and drift-geometry evidence].

The contrast is informative. GaMS3's edit re-encoded the harm signal into a new subspace, achieving low refusal in both languages while preserving the information for a retrained readout. Gemma's edit left the primary-site harm signal largely intact but partially disrupted it at early layers, consistent with its failure to suppress Slovene refusal: the model still encodes harmfulness, but the readout mechanism was partially disrupted for English while the Slovene readout remained functional.

**Item-level flip analysis (source: results/flip_analysis.json).** [Correction, iter 4: added per reviewer MUST-FIX #7.] At the item level, the edit's effect on individual prompts shows a mixture of evidence loss and criterion shift. For GaMS3, the edit produced a near-complete flip: items that were refused by the original model (>98% of items) were overwhelmingly not refused by the edited model, in both languages, with no systematic item-level association between original refusal strength and post-edit refusal. For Gemma EN, items with weaker original refusal (lower readout scores) were more likely to flip to non-refusal, consistent with a threshold shift (the weakest refusals are "peeled off" first). For Gemma SL, only a small fraction of items flipped (SL refusal barely changed), and those that did showed no systematic pattern. The item-level analysis is consistent with the action-failure reading [6]: the harm representation is preserved, but the mapping from representation to refusal is weakened in English and largely intact in Slovene.

#### T7: Drift geometry

For GaMS3, Cohen's d on the frozen harm axis dropped from 6.20 to 0.30 (EN) and from 5.61 to -0.18 (SL). The share of mean-difference energy on the frozen axis dropped from 0.71 to 0.002 (EN). The cosine between the pre- and post-edit refit axes was 0.274 (EN) and 0.188 (SL), confirming the edit rotated the harm axis. Collapse onset was at layer 22.

For Gemma, Cohen's d dropped from 5.29 to 4.94 (EN) and from 3.76 to 3.50 (SL). The frozen axis retained most of its energy share (0.83 → 0.80). The cosine between refit axes was 0.981. The edit barely moved the harm signal.

#### T8: Readout validity gate (S4 judged items)

| Model | Lang | R_seq item AUROC | R_seq 16-cell Spearman | R_seq pass | R1 item AUROC | R1 pass | Primary trait |
|---|---|---|---|---|---|---|---|
| GaMS3 | EN | 0.989 | 0.867 | True | 0.979 | False | R_seq |
| GaMS3 | SL | 0.995 | 0.899 | True | 0.963 | False | R_seq |
| Gemma | EN | 0.804 | 0.861 | False | 0.897 | False | JUDGE_ONLY |
| Gemma | SL | 0.920 | 0.856 | True | 0.968 | True | R_seq |

GaMS3 R_seq passed in both languages. Gemma R_seq passed only for SL; EN was classified as JUDGE_ONLY, meaning the judge labels should be trusted over the R_seq score for Gemma EN cells. R1 did not pass for GaMS3 in either language.

#### T9: Criterion shift vs. evidence loss

Both models showed EVIDENCE_LOSS under both R_seq and R1 readouts: the slope of the decision function decreased after editing, indicating the internal signal weakened rather than the threshold shifting. For GaMS3, the R_seq slope ratio was 0.36 (EN) and 0.42 (SL). For Gemma, the R_seq slope ratio was 0.61 (EN) and 0.48 (SL).

#### T10: r_prior geometry (original models)

The false-refusal direction r_prior (constructed from prompts judged harmless that the model refuses, orthogonalised to d_EN) was defined for both models. For GaMS3, 36 refusals (15 EN, 21 SL) out of 275 r_prior generations; cos(r_prior, d_EN) before orthogonalisation was 0.824 (pooled). For Gemma, 55 refusals (8 EN, 47 SL) out of 273; cos(r_prior, d_EN) was 0.631. The within-SL cos(r_prior, lang_dir) was -0.038 (GaMS3) and -0.139 (Gemma), confirming r_prior is not simply the language direction. r_prior is, however, substantially language-dominated: cos with the language axis is 0.65, and cos with its shuffled twin is 0.89 [Correction, iter 3: added from evaluation audit].

#### T12: Edit-strength dose-response (exploratory)

| Model | Scale f | Marker refusal EN % | Marker refusal SL % | KL1 median EN | KL1 median SL |
|---|---|---|---|---|---|
| GaMS3 | 0.0 | 95.8 | 100.0 | 0.0000 | 0.0000 |
| GaMS3 | 0.5 | 75.0 | 68.8 | 0.0088 | 0.0037 |
| GaMS3 | 1.0 | 0.0 | 0.0 | 0.0405 | 0.0177 |
| GaMS3 | 1.5 | 0.0 | 2.1 | 0.1610 | 0.1167 |
| Gemma | 0.0 | 93.8 | 100.0 | 0.0000 | 0.0000 |
| Gemma | 0.5 | 60.4 | 95.8 | 0.0000 | 0.0046 |
| Gemma | 1.0 | 27.1 | 91.7 | 0.0000 | 0.0103 |
| Gemma | 1.5 | 22.9 | 68.8 | 0.0000 | 0.0303 |
| Gemma | 2.0 | 12.5 | 31.2 | 0.0000 | 0.0924 |
| Gemma | 3.0 | 4.2 | 8.3 | 0.0000 | 0.8228 |

For GaMS3, scaling the LoRA edit by f = 0.5 brought both languages to 68 to 75% refusal; at f = 1.0 both reached 0%. EN and SL refusal declined in parallel. For Gemma, at f = 1.0 (the core edit) EN marker refusal was 27% while SL was 92%. Reaching SL refusal below 10% required f = 3.0, at which point KL divergence rose to 0.82 (SL), well above Heretic's operational range. At every dose level, SL marker refusal exceeded EN marker refusal [Correction, iter 4: these are keyword-marker rates; experiment 4's miscalibration analysis shows the keyword counter overcounts refusal on edited Gemma outputs (FP share 0.761, kappa -0.04 on the Gemma edit EN), so actual EN judged refusal is lower than the marker rates here, and the true EN-SL gap is likely wider than the marker gap at each dose].

[FIGURE:fig_dose_response]

#### T13: GaMS3 base model diagnostic (pre-instruction, descriptive)

The uninstructed cjvt/GaMS3-12B base model (before SFT) was tested with a Question/Answer format at layer 34. Frozen S3→S4 diff-in-means AUROC was 0.817 (EN) and 0.773 (SL). Grouped-CV S4 AUROC reached 0.988 (EN) and 0.958 (SL). The cosine between the base model's EN and SL harm directions was 0.781; the cosine between the base model's d_EN and the instruction-tuned model's d_EN was 0.305. Out of 20 EN harmful continuations, 14 complied and 5 refused; out of 20 SL harmful continuations, 13 complied and 5 refused. The base model already encodes a harm axis that partially survives instruction tuning, but the low cosine with the instruct model's direction (0.305) indicates instruction tuning rotated the harm representation.



### Experiment 4: C1 behaviour, RefusEU evaluation [ARTIFACT:art_m6pglf516e2r]

**Goal.** Evaluate all checkpoints (originals, edits, community abliteration reference) on the held-out RefusEU multilingual refusal benchmark [3] in both EN and SL, measuring refusal rate, attack success rate, over-refusal, and response validity.

**Judge.** The primary judge was a local Qwen3-14B model (agreement with gpt-4.1: kappa 0.83 on 6-way labels, 0.91 on refused-vs-not; tested on a calibration set before deployment). The gpt-4.1 judge was blocked partway through by API budget limits (716 of 3,840 items labelled before the block), so local Qwen3-14B served as the judge for all remaining generations [Correction, iter 3: corrected provenance from evaluation audit; Qwen3-14B was validated against the 716 gpt-4.1 labels before substitution].

**Headline RefusEU (S5) refusal rates:**

| Model | Checkpoint | EN S5 refusal | SL S5 refusal | EN S6 over-refusal | SL S6 over-refusal |
|---|---|---|---|---|---|
| GaMS3 | original | 0.986 | 0.871 | 0.100 | 0.107 |
| GaMS3 | edit | 0.014 | 0.000 | 0.000 | 0.000 |
| Gemma | original | 0.971 | 0.939 | 0.087 | 0.327 |
| Gemma | edit | 0.287 | 0.739 | 0.013 | 0.193 |
| Community ref | - | 0.054 | 0.114 | 0.007 | 0.027 |

All changes from original to edit were significant (Holm-corrected p < 1e-14 for refusal reductions). Invalid rate was 0.000 across all cells.

**GaMS3.** The edit reduced EN refusal from 0.986 to 0.014 and SL refusal from 0.871 to 0.000. Both languages reached near-zero refusal. Over-refusal dropped from ~0.10 to 0.000 in both languages. GaMS3's baseline SL refusal was already lower than its EN refusal (0.871 vs. 0.986), and the edit eliminated refusal in both languages.

**Gemma.** The edit reduced EN refusal from 0.971 to 0.287 and SL refusal from 0.939 to 0.739. The residual Slovene refusal (0.739) is 2.6× the residual English refusal (0.287). This is the headline result of the study: an English-tuned abliteration edit left most Slovene refusal intact in Gemma while removing most English refusal. Over-refusal dropped in both languages but remained substantial in SL (0.193 vs. 0.013 in EN for the edit). The original Gemma model already had high SL over-refusal (0.327), and the edit reduced it only to 0.193. The PARTIAL class accounts for 0.548 of the Gemma edit's English outputs, meaning more than half of what the keyword counter calls "non-refusal" is caveat-laden partial compliance rather than clean compliance [Correction, iter 3: PARTIAL rate added from evaluation audit].

**Community reference abliteration.** A community Heretic abliteration applied to Gemma reached 0.054 EN refusal and 0.114 SL refusal. This more aggressive edit removed most refusal in both languages but had higher FLORES NLL shifts (0.054 EN, 0.111 SL) than the selected trial.

**Keyword-proxy miscalibration.** The keyword refusal counter, which Heretic uses as its objective, inverts on the edits it selects. On the Gemma edit's English outputs, keyword refusal rate is 0.851 while the Qwen3-14B judged rate is 0.287; the false-positive share is 0.761 (76% of what the keyword calls "refusal" the judge does not), and kappa is -0.04. This inversion arises because the edit produces PARTIAL responses (warnings plus substantive content) that fire keyword markers but are not full refusals. The keyword counter is near-exact on original models (FP share ≤ 0.03) and structurally unreliable on edited checkpoints [Correction, iter 3: keyword miscalibration table added from evaluation audit].

**Paired cross-language analysis (S5X, 100 matched pairs).** The paired EN-SL refusal gap depends on the judge and refusal definition. Under the Qwen3-14B strict definition (REFUSED only), the Gemma edit gap is +0.69 [0.60, 0.78]. Under the broad definition (REFUSED + PARTIAL), the gap is +0.23 [0.14, 0.32]. Under the keyword counter, the gap is +0.06 [-0.02, 0.14]. For the community reference, the Qwen3-14B strict gap is +0.12 [0.05, 0.20] [Correction, iter 3: the gap is now stated as a range across judges rather than a single point estimate, per evaluation audit]. The difference-in-differences (edit gap minus original gap) under strict judging was +0.66 [0.55, 0.76].



### Experiment 6: GaMS3 surrogacy panel [ARTIFACT:art_KFZCxJcrr84K]

**Goal.** Measure the English surrogacy gap for GaMS3: for each abliteration trait, how much does an English outcome fail to predict the corresponding Slovene outcome?

**Method.** 246 Heretic edits (initial startup edits E0 plus TPE-selected edits E_TPE) were generated, activations collected on half-B items, and six traits measured: R (refusal, R_seq readout), R1 (R at first token), Rb (binary refusal), K (KL divergence), N (NLL), M (maximum logit). The primary learner was gradient-boosted trees. The surrogacy gap is defined as Gap_t = R2*(EN_A→EN_B) - R2*(EN_A→SL_B), where R2* is noise-ceiling normalised. The blind share B_t estimates the systematic (edit-determined) portion of the unseen Slovene variation. 160 non-collapsed edits were fitted.

**Gap table (source: results/gap_table.json):**

| Trait | R2* placebo | R2* test | Gap | 95% CI | Holm p | B_t [95% CI] |
|---|---|---|---|---|---|---|
| R | 0.983 | 0.968 | **0.015** | [0.006, 0.031] | NA | 0.004 [-0.004, 0.009] |
| R1 | 0.998 | 0.956 | **0.042** | [0.027, 0.070] | NA | 0.015 [0.002, 0.030] |
| Rb | 0.982 | 0.954 | **0.028** | [0.012, 0.068] | NA | 0.005 [-0.007, 0.013] |
| K | 0.977 | 0.830 | **0.147** | [0.074, 0.265] | 0.000 | 0.050 [0.001, 0.121] |
| N | -0.225 | 0.417 | -0.642 | [-14.8, 0.98] | 0.954 | - |
| M | 0.272 | 0.232 | 0.040 | [-8.37, 5.22] | 0.954 | - |

**Interpretation.** Gap_R = 0.015 [0.006, 0.031]: English refusal outcomes predicted Slovene refusal almost perfectly (R2* = 0.968), with only 1.5% of the ceiling left unexplained. This gap, while statistically above zero, is small. The blind share B_t for R was 0.004 with a CI spanning zero, meaning the small gap is mostly noise rather than a systematic edit-driven asymmetry. Verdict: CONFIRMATORY. Refusal is visible from English for GaMS3.

Gap_K = 0.147 [0.074, 0.265]: KL divergence showed a substantial surrogacy gap. English KL predicted Slovene KL at R2* = 0.830, leaving 14.7% of the ceiling unexplained. The blind share B_t = 0.050 [0.001, 0.121], with the CI excluding zero: part of this gap is systematically determined by the edit, not just noise. Verdict: BLIND. KL divergence has a component in Slovene that English KL does not see. Holm p = 0.000. The SL KL is SMALLER on average (mean-change ratio 0.59); the gap is not that Slovene gets MORE perturbation, but that it gets DIFFERENT perturbation [Correction, iter 3: direction of KL gap clarified from evaluation audit].

Gap_N and Gap_M showed no reliable signal (NLL and max-logit traits had low reliability in English, so the gap estimate was uninformative).

**Carrier regression.** The exposure differential D (log E_SL - log E_EN) was tested as a carrier of the surrogacy gap. For every trait, dR2(D given S0) was near zero or negative. The D carrier FAILED for all traits. The surrogacy gap is not explained by differences in how much the edit perturbs Slovene vs. English token representations on harmless text.

**Transfer slopes.** The SL/EN transfer slope for R was 0.82 [0.74, 0.90]: when the edit moves English refusal by one unit, Slovene refusal moves by 0.82 units. For K, the slope was 0.39 [0.34, 0.48], much stronger attenuation. For R1, the slope was 0.50 [0.46, 0.55].

**Forecast.** Conformal prediction intervals at 90% coverage met the 85% threshold on only 50% of trait × holdout-set combinations. The core edit (trial 88) was out of support for all traits, meaning it lay outside the distribution of TPE-explored edits. This limits the forecast's applicability to the specific selected checkpoint.

**Stability checks.** Gap estimates were stable across alternative learners, inclusion of collapsed edits, and MT-stable subsets. The reverse-direction analysis (SL → EN) is not supportive: the reverse-direction gap estimate flips sign for some traits, indicating that the direction of prediction matters and the gap is not symmetric [Correction, iter 4: the previous text listed the reverse-direction analysis as part of a supportive stability battery; the sign flip means it cannot be described as "stable"].



### Experiment 7: Gemma surrogacy panel [ARTIFACT:art_CUChUm6wCwo5]

**Goal.** Measure the English surrogacy gap for Gemma using the same protocol as experiment 6.

**Setup.** 203 Heretic edits, 163 fitted. The same six traits were measured.

**Verdicts** [Correction, iter 3: frozen prediction wordings restored to their original form; the previous draft inverted P-a's direction]:

- **P-a (Gap_R >= 0.10 with 95% LB > 0):** NOT CONFIRMED. The frozen prediction expected a LARGE gap; the observed gap on R1 was 0.054 [0.022, 0.128], which is above zero but below the 0.10 threshold. The gap is small, not large. Label-swap placebo: 15.5% of swaps at least as large as observed.
- **P-b (Gap_Rb >= 0.10):** UNTESTABLE. The Rb validity gate failed, so the analysis was exploratory. Exploratory estimate: Gap_Rb = 0.018 [0.011, 0.043].
- **P-c (exposure differential carries the gap):** NOT CONFIRMED. dR2(P given base) and dR2(b1 given P) were near zero for both R1 and Rb.
- **P-d (matched-margin gap >= 0.10):** NOT CONFIRMED. Gap_margin_matched = 0.057 [0.029, 0.130].

**Key result.** Gap_K = +0.079 (Holm p = 0.009): KL divergence showed a surrogacy gap for Gemma as well, though smaller than GaMS3's 0.147. The recomputed transfer slopes are: R1 0.436, R_seq 0.220, lp_ref 0.081, lp_comp 0.849 [Correction, iter 3: slopes recomputed from evaluation audit]. The compliance log-probability slope (0.849) is near 1.0, meaning the edit raises the compliance signal equally in both languages; the refusal-opener slope (0.081) is near zero, meaning the edit lowers the refusal opener only in English. This is what partial depth coverage predicts.

**Comparison with GaMS3.** The Gemma surrogacy gap on refusal traits was larger than GaMS3's (0.054 vs. 0.015 for R1; overlapping CIs), consistent with the behavioural result that Gemma retained more Slovene refusal after editing. The KL gap was smaller (0.079 vs. 0.147), but both models showed a significant blind component in KL. Reading: attenuated but predictable [Correction, iter 3: "attenuated but predictable" is the correct characterisation from the frozen predictions; the previous draft omitted this framing].



### Experiment 8: Causal test [ARTIFACT:art_hmbXDppkPZnR]

**Goal.** Test whether the Slovene refusal that survived English abliteration can be causally removed by specific interventions, and identify where in the network the relevant information resides.

**Pre-registered hypothesis.** Subtracting the false-refusal direction r_prior (constructed from prompts judged harmless that the model refuses, following Wang et al. [2]) from the English refusal direction d_EN should cut the residual Slovene refusal by at least half, beyond what a random control achieves. The KILL criterion fires if the r_prior cut is not significantly larger than the best random control.

**Primary result: hypothesis FAILS.** Applying d_EN alone reduced Gemma's harmful EN refusal from 0.91 to 0.23 but left SL refusal at 0.86. Adding r_prior (arm A2: d_EN + r_prior) moved SL refusal to 0.83. The r_prior cut relative to d_EN alone was 0.036 [-0.037, 0.109], not significantly different from zero, and not significantly larger than the best random control (0.074). KILL criteria a and c fired (part 1 failed, and F6 over-refusal test failed). The pre-registered hypothesis was rejected.

**Full Gemma activation arms (111 harmful + 111 harmless per language):**

| Arm | EN harmful | SL harmful | EN harmless | SL harmless |
|---|---|---|---|---|
| A0 no-op | 0.91 | 0.99 | 0.05 | 0.28 |
| A1 d_EN | 0.23 | 0.86 | 0.00 | 0.19 |
| A2 d_EN + r_prior | 0.21 | 0.83 | 0.00 | 0.12 |
| A3 r_prior alone | 0.95 | 0.98 | 0.04 | 0.19 |
| A4 d_EN + language identity | 0.23 | 0.55 | 0.02 | 0.08 |
| A7 d_EN + rand_1 | 0.21 | 0.85 | 0.01 | 0.15 |
| A10 d_EN + shuffled-label r_prior | 0.41 | 0.73 | - | - |

Several observations from the arm table:

1. **r_prior alone (A3)** had almost no effect: SL harmful refusal went from 0.99 to 0.98, EN from 0.91 to 0.95. The false-refusal direction does not carry meaningful refusal-suppression information by itself.

2. **Language-identity direction (A4)** combined with d_EN reduced SL harmful refusal from 0.86 to 0.55, the largest single-direction improvement. However, it also raised FLORES NLL by 2.0 (EN) and 1.9 (SL), destroying language modelling quality. This is not a practical intervention.

3. **Random directions (A7, A8, A9)** combined with d_EN left SL refusal between 0.74 and 0.85, comparable to d_EN alone. Random directions did not systematically help.

4. **Shuffled-label r_prior (A10)** combined with d_EN reduced SL refusal to 0.73 but also raised EN harmful refusal to 0.41, suggesting the shuffled direction disrupted the English refusal pathway as well.

**Exploratory: layer-matched d_EN across all 48 layers (X1).** Applying the per-layer English refusal direction at all 48 layers simultaneously reduced SL harmful refusal from 0.86 to 0.10 and EN harmful refusal to 0.03. This is the only intervention that nearly eliminated Slovene refusal, but it required steering at every layer simultaneously, raised FLORES NLL by 0.29 (EN) and 0.52 (SL), and is not equivalent to the single-direction abliteration that Heretic performs.

**Depth localisation.** Applying layer-matched d_EN to different layer bands:

| Band | SL harmful | EN harmful | FLORES ΔNLL SL |
|---|---|---|---|
| Layers 1-12 | 0.82 | 0.79 | 0.743 |
| Layers 13-24 | 0.82 | 0.45 | 0.017 |
| Layers 25-36 | 0.70 | 0.72 | 0.082 |
| Layers 37-48 | 0.99 | 0.87 | -0.003 |
| Layers 1-24 | 0.55 | 0.42 | 0.409 |
| Layers 1-36 | 0.21 | 0.38 | 0.513 |
| All 48 | 0.23 | 0.37 | 0.524 |

No single band removed Slovene refusal. Layers 13-24 were most effective for English (0.45) but left Slovene at 0.82. Layers 25-36 provided the most Slovene reduction per band (0.70) without large NLL cost. Full Slovene refusal removal required cumulative intervention across at least three bands.

**Weight edit repair.** The experiment also tested whether augmenting the core Heretic weight edit with additional directions could repair the Slovene gap [Correction, iter 4: the W-arm rows and the A-arm rows above were scored by different judges (activation arms by gpt-4.1, weight-edit arms by the local Qwen3-14B). The W0 baseline EN rate (0.39) differs from the A0 baseline EN rate (0.91) partly because the judges differ, not only because of the intervention. Cross-table comparisons (e.g. W4 EN = 0.70 appearing to "raise" refusal above the A-arm baseline) are therefore confounded by judge identity. Within-table contrasts (W1 vs W0, W3 vs W0) are valid because they share a judge.]:

| Arm | SL harmful | EN harmful | FLORES ΔNLL SL |
|---|---|---|---|
| W0 core Heretic edit | 0.89 | 0.39 | -0.005 |
| W1 core + r_prior weight edit | 0.76 | 0.23 | 0.009 |
| W3 core + layer-matched d_EN(h) | 0.11 | 0.29 | 0.546 |
| W4 core + random weight edit | 0.47 | 0.70 | 0.064 |

The r_prior weight edit (W1) reduced SL refusal from 0.89 to 0.76 while also reducing EN refusal to 0.23, but the SL residual remained high. The layer-matched weight edit (W3) reached 0.11 SL refusal but at severe NLL cost (+0.55). The random weight edit (W4) left EN refusal at 0.70, comparable to the W0 baseline under this judge [Correction, iter 4: the previous text said the random edit "raised" EN refusal to 0.70, but this is within-table relative to W0 (0.39), and the difference may partly reflect noise or judge sensitivity rather than a genuine disruption of English refusal].

**Community Heretic reference vs. core edit (S4 held-out, 70 pairs):**

| Arm | EN harmful | SL harmful | SL harmless |
|---|---|---|---|
| W0 core edit | 0.39 | 0.89 | 0.07 |
| C0 community edit | 0.01 | 0.26 | 0.01 |
| C1 community + r_prior | 0.01 | 0.20 | 0.00 |

The community edit reached much lower SL refusal (0.26) than the selected trial's edit (0.89), at the cost of slightly higher FLORES NLL (+0.11 SL). Adding r_prior to the community edit reduced SL refusal from 0.26 to 0.20, a modest improvement. The community edit achieved stronger refusal suppression because it was more aggressive overall, not because it targeted Slovene specifically.

**GaMS3 descriptive arms.** The GaMS3 results were descriptive (not pre-registered for the causal test):

| Arm | EN harmful | SL harmful | EN harmless | SL harmless |
|---|---|---|---|---|
| G0 no-op | 0.93 | 0.95 | 0.07 | 0.10 |
| G1 d_EN | 0.57 | 0.50 | 0.00 | 0.04 |

For GaMS3, applying d_EN reduced both EN and SL refusal comparably (from 0.93/0.95 to 0.57/0.50), consistent with the small surrogacy gap found in experiment 6. The EN-SL difference was minor.



## Iteration 3

Iteration 3 was prompted by the reviewer's blocking feedback on the iteration-2 draft. Three objections required experimental answers: (1) the headline gap (+0.69 on S5X strict) depends on a single judge, and the keyword proxy that Heretic actually optimises assigns a gap of only +0.06; no number in the draft was stated as a range across judges. (2) The depth localisation from experiment 8 (no single 12-layer band removes Slovene refusal, cumulative three-band steering reaches SL 0.21) suggests coverage matters, but every arm in iteration 2 varied coverage and strength together; there was no matched-energy comparison. (3) The depth-redundancy observation rests on two sibling checkpoints from one architecture; it could be coincidence rather than a measurable quantity.

Iteration 3 therefore ran four experiments and one evaluation audit, each attacking the reviewer's objections from a different angle. [Correction, iter 4: the audit pod (evaluation 1) covered iterations 1-2 only; iteration-3 numbers have not been independently re-derived by the run's own tooling. The audited mismatch rate elsewhere was 5.5% (8/167 numbers in iterations 1-2) and 4.9% (5/102 in iteration 4); these rates are the best available prior for the unaudited iteration-3 sections.]

### Experiment 9: Gemma coverage × strength factorial [ARTIFACT:art_ex4hbgThhJaL]

**Goal.** Test whether depth coverage or total edit energy governs how much Slovene refusal survives, by building weight edits that cross coverage with strength at matched total removal energy.

**Setup.** Weight edits were constructed using Heretic's operator path (orthogonalize_direction=true, row_normalization='full', rank-3 LoRA, per-layer d_EN(h) from experiment 8 directions) on google/gemma-3-12b-it, crossing 10 coverage sets with 4 to 5 per-layer strength levels. Coverage sets included four contiguous 12-layer bands (B1: 1-12, B2: 13-24, B3: 25-36, B4: 37-48), two cumulative sets (C24: 1-24, C36: 1-36), a full-depth set (ALL48), stride-2 (S2) and stride-4 (S4) sets, and the support of the iteration-1 Heretic kernel (K96). Strength was controlled by a per-layer projection coefficient c in {0.25, 0.50, 1.00, 1.50}, with total removal energy E computed analytically for every cell before running. The panel comprised 122 cells scored on 27,784 generations by a local Qwen3-14B judge with the frozen experiment-4 rubric, certified at kappa 0.87 vs gpt-4.1 within edited checkpoints.

PARTIAL counts as compliance throughout. INVALID is excluded from denominators.

**Part A: DEV depth-redundancy index.** Cumulative-prefix directional ablation (activation-only) on S3 half-A (44 harmful items per language) gave (source: results/dev_index.json):

| Family | Lang | index_L |
|---|---|---|
| prefix | EN | 16 [16, 20] |
| prefix | SL | 20 [20, 28] |
| suffix | EN | 24 [24, 24] |
| suffix | SL | 24 [24, 28] |

The English index (the minimal layer count whose ablation brings refusal below 0.5) is 16; the Slovene index is 20. Slovene needs at least one more 4-layer step of coverage than English. The leave-one-band-out necessity profile shows the 25-36 band is most necessary for Slovene (LOBO necessity +0.39) but not for English (+0.00), indicating Slovene refusal is written more deeply. [Correction, iter 4: the cross-language index gap (20 vs 16) sits inside its own language-permutation null; the artifact's audit script explicitly demoted this statistic. The index is necessary but not sufficient: approximately half the cells at or above the index threshold do not cross the 0.5 refusal boundary. After Holm adjustment across the surviving confirmatory contrasts, no individual contrast reaches significance.]

[FIGURE:fig_redundancy_index]

**Part P2: Matched-energy groups (source: results/matched_energy_groups.json).** Four groups, each containing a narrow-and-strong and a broad-and-weak cell within the same total removal energy:

| Group | E | SL narrow | SL broad | SL contrast [CI] | EN contrast |
|---|---|---|---|---|---|
| G1 | 16.7 | 0.98 | 1.00 | -0.02 [-0.07, 0.00] | -0.03 |
| G2 | 19.2 | 0.63 | 0.98 | -0.34 [-0.49, -0.20] | -0.27 |
| G3 | 35.6 | 1.00 | 0.66 | +0.34 [+0.20, +0.49] | +0.67 |
| G4 | 37.7 | 0.95 | 0.73 | +0.22 [+0.10, +0.34] | +0.30 |

The pooled SL contrast (narrow minus broad) was +0.05 [-0.00, 0.10]; the pooled EN contrast was +0.17 [0.09, 0.24]. The difference-of-differences SL-EN was -0.12 [-0.21, -0.03]. **P2 FAIL**: the confirmatory prediction that broad-and-weak beats narrow-and-strong for Slovene at matched energy was not supported. The groups split: G2 favoured narrow (narrow SL 0.63 < broad SL 0.98), while G3 and G4 favoured broad. The direction of the matched-energy contrast depended on WHICH layers carried the energy, not on how many.

**Part P1: Coverage regression.** The incremental R2 of coverage terms (number of covered layers, depth span) over the base model (log E + EN refusal + static band masses) was dR2 = 0.040 [0.006, 0.136] on 46 cells. The falsifier (dR2 < 0.05) fired. Coverage as a count of layers does not add meaningful predictive power over total energy and placement. **P1 FAIL.**

**Part P3: DEV index prediction.** The frozen DEV index predicted per-cell residuals out of sample at Spearman 0.78 [0.64, 0.88] for both EN and SL. **P3 PASS** (threshold: Spearman >= 0.6). On held-out harm categories, the SL Spearman was 0.72 [0.13, 1.00] (n=10 cells).

**Exploratory: which layers, not how many.** The pre-registered exploratory analysis (declared before outcomes were read) revealed that the fraction of layers 13-24 covered by a set predicts the lowest Slovene refusal that set achieves at any strength, at Spearman -0.942 across 10 coverage sets (placebo-verified, p = 0.004). Sets covering all of layers 13-24 (ALL48, C36, K96, B2, C24) all reached SL < 0.20 at sufficient strength. Sets missing layers 13-24 (S4, B3, B1, B4) never reached SL < 0.93 at any strength. The band-mass regression confirmed this: in the SL model (R2 = 0.701), the mass of energy in band 13-24 was the dominant predictor; in the EN model (R2 = 0.811), band 13-24 mass also dominated, but at lower coefficients.

The contiguous-vs-strided comparison at matched energy (33 pairs within 15% log E) showed strided coverage leaves 0.12 [0.07, 0.19] more Slovene refusal while covering more layers on average (-5.5 more), with the effect carried by magnitude rather than by a majority of pairs (17/33).

**S5X verified pairs (declared second touch, n=100).** At c=1.5 with full coverage (ALL48 and K96), the SL-EN gap was +0.06 [0.00, 0.12], compared to the no-op gap of +0.07 [0.03, 0.12]. The high-dose, full-coverage weight edit closes the gap to near-baseline.

**Per-layer write mass (exploratory).** English and Slovene refusal write mass spread over the same number of layers (18 to 80% cumulative), but the distribution differs: Slovene's mass sits 60% in band 25-36 vs English's 63% in band 37-48. The prediction that Slovene's mass is spread over MORE layers was FALSE. Instead, it is spread over DIFFERENT layers.

[Correction, iter 4: The band-mass regression's evidence is model-specific and weaker than previously stated. In the EN model (R2 = 0.811), band 13-24 mass is the dominant predictor. In the SL model (R2 = 0.701), the band 13-24 coefficient is +0.156 with CI [-0.240, 0.529], which does not reach significance; the dominant SL term is instead the English refusal rate (coefficient 0.855). The supporting evidence for Slovene is therefore the rank statistic (Spearman -0.942) and the matched-energy/matched-count contrasts, not the regression. The coverage sets listed as missing layers 13-24 should include S2 (half coverage, 50%) and S4 (quarter coverage, 25%) with their distinct outcomes (S2 min SL 0.732, S4 min SL 0.927), rather than being assigned to the missing list.]

[FIGURE:fig_band_analysis]



### Experiment 10: GaMS3 coverage test [ARTIFACT:art_xLy2vVlI7OEL]

**Goal.** Run the identical coverage × strength factorial and DEV index on GaMS3, the checkpoint whose English-derived edit transferred, to test whether index_SL ≈ index_EN there.

**DEV index (source: results/dev_index.json):** EN = 16 [16, 16], SL = 20 [16, 24]. The Slovene index is one grid step above English, with overlapping CIs. In both models the English index is shallower; the SL lag is common to both checkpoints.

**Weight-edit panel (57 cells, source: results/panel_summary.json).** The matched-energy groups gave:

| Group | E | SL narrow | SL broad | SL contrast |
|---|---|---|---|---|
| E1 | 6.9 | 0.81 | 0.88 | -0.06 [-0.14, 0.00] |
| E2 | 13.9 | 0.55 | 0.71 | -0.16 [-0.23, -0.09] |
| E3 | 27.8 | 0.35 | 0.44 | -0.09 [-0.18, -0.01] |

In all three groups, the narrow-and-strong cell (B2 or B3, layers 13-24 or 25-36) left LESS Slovene refusal than the broad-and-weak cell (STR2 or STR4, strided). **PB2 FALSIFIED OPPOSITE**: at matched energy, narrow beats broad for GaMS3, the reverse of what the hypothesis predicted. **PB1 NOT SUPPORTED**: dR2(coverage | base) = 0.002 [0.000, 0.010].

**Nested R2 (where the variance sits):**

| Model | R2 |
|---|---|
| logE | 0.325 |
| logE + placement (b3 band masses) | 0.718 |
| logE + count | 0.400 |
| logE + count + span | 0.532 |

Placement (which band the energy sits in) explains 71.8% of the Slovene residual variance, while count (how many layers) explains only 40.0%. The decisive factor is WHERE the energy sits, not HOW MANY layers are covered. This is consistent with experiment 9's exploratory finding: band 13-24 density drives the outcome.

**Placement at matched energy AND matched layer count (12 layers, band vs stride-4):**

| Contrast | SL band | SL stride-4 | SL delta |
|---|---|---|---|
| E1_B2 vs STR4 | 0.83 | 0.93 | -0.10 |
| E2_B2 vs STR4 | 0.51 | 0.89 | -0.37 |
| E3_B2 vs STR4 | 0.24 | 0.81 | -0.57 |

At the same energy, same layer count, only placement differs: a contiguous 12-layer band in layers 13-24 removes far more refusal than every-4th-layer across the full depth. This holds for English as well but the EN gap is smaller, confirming that placement is a general property of edit efficacy, not specific to cross-language transfer.

**Cross-model contrast:** both models show index_EN = 16, index_SL = 20. The Slovene lag is not what distinguishes these two models under this instrument. Any iteration-1 difference between their Heretic edits (GaMS3 transferred, Gemma did not) must be explained by something other than how redundantly refusal is written across depth.

[Correction, iter 4: English judge agreement within edited GaMS3 arms is 0.54, so English refusal rates in the edited cells are one end of a range rather than point estimates. The co-primary "usable" index does not resolve in either language. Two further pre-registered predictions (the operator-versus-depth finding) are unreported here; see the artifact for the full results.]



### Experiment 11: Corrected objective [ARTIFACT:art_0XmNBGkzsJc_]

**Goal.** Test whether replacing Heretic's English keyword refusal counter with a partial-aware score, at equal budget/seed/data/quantisation, makes the search select a kernel that closes the Slovene-English gap.

**Setup.** A refusal classifier was distilled from existing gpt-4.1 and Qwen3-14B labels (thousands on disk from experiments 4, 5, and 8), using char/word TF-IDF and hand-crafted features on the first 100 tokens of each response. It was certified at kappa 0.858 [0.820, 0.888] (refused-vs-not, within edited checkpoints, 20 held-out replayed trials) against the Qwen3-14B judge. [Correction, iter 4: The previous draft quoted kappa 0.924, which is the in-loop value over 116 draws, not the certified within-edited-cells value. It also described the classifier as using "first-64-token embeddings"; the actual features are char/word TF-IDF + hand features on the first 100 tokens (corrected_numbers_iter4.json, claim E11.classifier_certification_kappa).] The corrected Heretic run used the same seed (20260923), same 116-trial budget, same NF4 precision, and the same selection rule (lowest KL among trials with ≤ 10 refusals); only the refusal scorer changed.

**Selection outcomes.** Under the corrected scorer, the primary selection rule fired (not the fallback), selecting trial 7 with 5/100 refusals at KL 0.258. Under the keyword scorer on the same 116 trials, the fallback rule fired, selecting trial 96 with 69/100 keyword-refusals at KL 0.024. The keyword counter fails because it sees 72/100 keyword-refusals on trial 107 (which the judge rates at 10/100 actual refusals) and cannot select it.

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



### Experiment 12: Predictive test across models and languages [ARTIFACT:art_kfCCWf7o8eJ9]

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



### Evaluation 1: Audit and judge-sensitivity table [ARTIFACT:art_Z3I1K3VnFZuz]

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

**Novelty positioning.** Wang et al. [2] established direction universality across 14 languages using all-layer activation ablation; Slovene and Gemma-3-12B were not among their models or languages. Arditi et al. [1] showed refusal is mediated by a single direction ablated at all components. Li et al. [19] identify which layers govern safety behaviour ("safety layers"); Bosco and Srinivasan [20] locate refusal beyond attention. [Correction, iter 4: positioning against depth-selection work added per reviewer MUST-FIX #8.] This study adds: (a) the English direction does clear Slovene when applied at every depth (consistent with Wang et al. and Arditi et al.), but (b) the site-limited Heretic weight edit leaves a gap whose size is judge- and definition-dependent (strict +0.06 to +0.69), and (c) the gap is governed by WHERE the edit energy sits (band 13-24 density, Spearman -0.942) rather than by how many layers are covered. What this adds beyond Li et al. [19] and Bosco and Srinivasan [20] is the conjunction: effect-based site selection (which layers matter) AND language-specific depth shifts (the critical band moves between sibling checkpoints from the same architecture family), established by matched-energy AND matched-layer-count contrasts. The negative finding (that a causal activation-space profile fails to predict weight-edit outcomes while two one-forward-pass baselines succeed) is arguably more transferable; it positions against Jiang [21] (single-direction ablation is not a necessity test) and speaks to the limits of causal profiling as a general method.

**Pending human review.** Five packets totalling 640 items are ready for native-speaker labelling. No native-speaker review has been conducted anywhere in this study; all judges are automated.



## Iteration 4

Iteration 4 was designed to close three remaining gaps from the reviewer's blocking feedback on iterations 1-3: (1) the placement finding rests on the exploratory band-density correlation (Spearman -0.942) without a causal mechanism tying edit energy to refusal at each layer; (2) the result is Gemma-only, with GaMS3 showing a different depth profile but no causal confirmation; and (3) Heretic's keyword blindness was demonstrated qualitatively but not quantified as a structural feature of the objective landscape. Iteration 4 ran three experiments, one comprehensive evaluation audit, and one positioning analysis.

### Experiment 13: Causal write profile and overlap instrument in Gemma [ARTIFACT:art_NpZ_nW6qgSKD]

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

**Nested $R^2$ (source: results/report_tables.md):**

| Model | $R^2$ |
|---|---|
| logE alone | 0.088 |
| logE + $O$ | 0.668 |
| logE + $O$ + $O_\text{cos}$ | 0.790 |
| logE + $O$ + $O_\text{cos}$ + $O_\text{band4}$ | 0.806 |

**PRIMARY CRITERION: FALSIFIED.** The incremental $R^2$ of $O$ over log energy was $\Delta R^2 = 0.026$, below the pre-registered 0.10 threshold (powered, MDE = 0.047 at 80% power). In the SL model, $\Delta R^2 = 0.052$ (inconclusive). $O$ is collinear with the one-forward-pass cosine baseline ($\rho$ = 0.81/0.76). The rank ordering is informative: knowing $O$ tells which of two matched-energy edits removes more refusal. However, the variance it explains above energy is small because energy already correlates with effective placement.

**Cross-prediction:** EN outcome predicts SL at $\rho$ = 0.945, indistinguishable from $O$ itself. A language-specific instrument is not needed if a language-pooled one is available.

**Replication in Qwen3-8B (outside family, 3 languages, source: results/report_tables.md):** Spearman $\rho(O)$: EN -0.76, SL -0.93, DE -0.84. Matched groups held in all three languages (9/9 favour high-$O$).

**Judge certification (source: results/report_tables.md, judge table):** Within-edited pooled $\kappa$ = 0.818. EN $\kappa$ = 0.856 PASS; SL $\kappa$ = 0.744 FAIL. Slovene gap claims in this experiment are therefore judge-sensitive.

[FIGURE:fig_write_profile]

### Experiment 14: Causal write profile and overlap in GaMS3 [ARTIFACT:art_bxpIbe7-nSvR]

**Goal.** Repeat the causal write-profile measurement for the sibling model (cjvt/GaMS3-12B-Instruct) and test $O$'s prediction on the GaMS3 weight-edit panel.

**Causal write profile.** The GaMS3 profile peaks at layer 27 (both EN and SL), in band 25-36 rather than the anchor's 13-24. Band mass distribution (source: results/report_tables.md):

| Band | EN mass | SL mass |
|---|---|---|
| 1-12 | 0.00 | 0.02 |
| 13-24 | 1.05 | 0.55 |
| 25-36 | 1.50 | 0.57 |
| 37-48 | 0.27 | 0.05 |

Split-half reliability: EN 0.812, SL 0.312. The SL profile is declared UNRELIABLE (source: results/report_tables.md).

**VERDICT: PARTIAL.** The overlap $O_\text{SL}$ predicts Slovene refusal at Spearman -0.903 [-0.928, -0.857], beating log-energy (-0.384), span (-0.039), and mean-depth (-0.328). The incremental $R^2$ of $O$ over log-energy is 0.580 (LOO: 0.594), passing the 0.10 threshold that the anchor failed.

**Argmax band prediction: FAILED (NAMED_AND_LOST).** The profile predicted band 25-36 as the winner, but band 13-24 (B2) achieved the lowest Slovene refusal (0.30 at E3 vs 0.53 for B3 at E3). There is a metric flip: the opener rule ranks 25-36 first while judged strict refusal ranks 13-24 first (source: results/report_tables.md).

**THREE BOUNDARIES (source: results/report_tables.md):**
1. $O_\text{band4}$ LOO $\Delta R^2$ = 0.845 and $O_\text{cos}$ = 0.834 both beat $O$'s 0.594, so the expensive single-layer instrument does not earn its cost over one-forward-pass baselines.
2. The DEV argmax names the wrong band.
3. The GaMS3 profile predicts the sibling (Gemma) at Spearman -0.442, no worse than its own -0.278 on Gemma, suggesting the profiles carry shared rather than model-specific information.

**Placement vs dose dissociation (A1-A4 ladder, source: results/report_tables.md):** At fixed placement, increasing dose reduces refusal (EN -0.186, p = 0.001; SL -0.157, p = 0.003). At fixed dose, swapping placement does not significantly change refusal (EN -0.029, ns; SL 0.000, ns). At the refusal floor where the shipped edits operate, dose is the active variable and the particular kernel does not matter, confirming experiment 11's finding.

**Controls:** All six (three random, three PC) were null.

**Judge certification:** EN $\kappa$ = 0.721 (MISS/JUDGE_SENSITIVE); SL $\kappa$ = 0.830 (PASS). English gap claims in GaMS3 are therefore judge-sensitive, the reverse of the Gemma pattern.

[FIGURE:fig_gams3_profile]

### Experiment 15: Gradient-blind fraction of Heretic's selection objective [ARTIFACT:art_F46S3uP80BUa]

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
| Gemma | Keyword | 107 | fallback |
| Gemma | Classifier | 98 | primary |
| Gemma | Judge (gpt-4.1) | 64 | primary |
| GaMS3 | Keyword | 88 | fallback |
| GaMS3 | Classifier | 85 | primary |

Under the classifier or judge, the primary selection rule fires for Gemma (selecting a trial with ≤ 10 actual refusals); under keywords it falls to the fallback rule. For GaMS3, classifier selection reaches the primary rule, and the fallback-selected trial 88 is close to the classifier-selected trial 85.

**Judge gate:** gpt-4.1 subsample $\kappa$ = 0.850 [0.772, 0.911], n = 800, cost $0.86. Classifier on GaMS3 without refit: $\kappa$ = 0.841 (source: results/analysis.json).

[FIGURE:fig_gbf]

### Evaluation 2: Comprehensive audit, judge calibration, and partial-compliance curves [ARTIFACT:art_hBuck7q0dnxG]

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

**NF4 vs bf16 confound (source: results/quant_confound.json).** VERDICT: bounded but NOT closed at panel scale (one checkpoint, 20 verified pairs per language). Weight relative Frobenius error 0.093. Energy profile cosine bf16 vs NF4: 0.999998. Behavioural gap at matched cell: bf16 +0.60, NF4 +0.45 (SL refusal difference). NF4 quantisation attenuates the gap by approximately 0.15 but does not eliminate it.

| Language | Refused bf16 | Refused NF4 | Diff [CI] | Label agreement |
|---|---|---|---|---|
| EN (n=20) | 0.25 | 0.25 | 0.00 [-0.20, 0.20] | 0.65 |
| SL (n=20) | 0.85 | 0.70 | 0.15 [0.00, 0.30] | 0.80 |

**Pending human review (source: results/pending_human_review_iter4.md).** Five files totalling 640 items remain pending: three native-review packets (570 rows covering translation fidelity, refusal/partial/compliance labels, and utility labels) and two executor-labelled checks (70 rows). No native-speaker or human review has been conducted anywhere in the run. Every judged rate in the report is proxy-certified (gpt-4.1 as frontier proxy), not human-certified.

### Research 1: Novelty positioning [ARTIFACT:art_sZ5w0yoY9o6L]

**Goal.** Establish what the surviving positive and negative results add relative to published work.

**Positioning of the positive (source: results/positioning_positive.md).** The surviving positive finding is a matched-total-energy AND matched-layer-count placement contrast, per language, with the effective region differing between siblings. Effect-based site selection and language-specific depths have been published separately: Li et al. [19] study which layers govern safety behaviour; Bosco and Srinivasan [20] locate refusal beyond attention. What this study adds is the conjunction: the edit's depth band, not its energy or span, determines how much refusal survives, and the critical band shifts between checkpoints from the same architecture family. The Qwen3-8B replication across three languages extends this beyond the Gemma-3 family.

**Positioning of the negative (source: results/positioning_negative.md).** The negative finding, that an activation-space depth measurement (the causal write profile) fails to predict weight-edit outcomes across languages while two one-forward-pass baselines ($O_\text{cos}$ and $O_\text{band4}$) succeed, positions against Jiang [21] (single-direction ablation is not a necessity test) and against AdvPrefix (arXiv 2412.10321) [22] (selection blindness). Four partial neighbours were found; their conjunction (activation-measurement failure plus baseline success on the same data) is "not found by these queries." This negative is more transferable than the surviving positive because it speaks to the limits of a general method (causal profiling) rather than to a specific model pair.

**Attribution note.** An earlier draft attributed a claim about "2-3 middle layers" to arXiv 2607.02714; the research artifact confirmed this text exists in that paper but is rejected in the next sentence, so the attribution is dropped.


## What we have learned so far

[FIGURE:fig_refusal_gap]

Four iterations have converged on a picture with one firm positive (model-specific), one structural finding, and a growing list of falsified predictions.

**Firm positive: band placement governs residual refusal (model-specific).** [Correction, iter 4: This claim is restated as model-specific and bounded by optimization strength, per reviewer MUST-FIX #1 and #9.] At matched total removal energy, which 12-layer band carries the energy predicts how much refusal survives. In Gemma, the band-density Spearman is -0.942 (exp9, placebo-verified, p = 0.004): coverage sets including layers 13-24 reach SL < 0.20 at sufficient strength; those missing it never reach SL < 0.93. In the EN model, band 13-24 mass is the dominant regression predictor (R2 = 0.811). In the SL model, the band 13-24 coefficient is +0.156 with CI [-0.240, 0.529] and does not reach significance; the dominant SL predictor is instead the English refusal rate. In GaMS3, placement also dominates count (nested R2 0.718 vs 0.400, exp10), and a contiguous B2 band (layers 13-24) removes up to 0.57 more Slovene refusal than a stride-4 pattern at the same energy, but the effective region may differ between siblings (see iteration 4, experiment 14: GaMS3 causal write profile peaks at layer 27, not 19). The relevant factor is not how many layers the edit touches, but where the energy sits.

**Partial positive: corrected objective halves the gap.** Replacing Heretic's keyword refusal counter with a partial-aware classifier, at equal budget/seed/data, moved the S5X strict gap from +0.68 to +0.38 (exp11). The corrected selection bought broader aligned coverage (A1 = 64.0 vs 26.0). However, the P7 falsifier fired: dose-scaling the keyword edit to the same English refusal level achieved comparable gap reduction (+0.33), meaning the improvement may be "more edit" rather than "better objective." The gap did not reach the pre-registered +0.35 target (observed +0.38, CI [0.29, 0.47]).

**Falsified: depth-coverage count does not explain the residual.** The coverage regression (exp9 P1, dR2 = 0.040) and the matched-energy broad-vs-narrow comparison (exp9 P2, pooled +0.05) both failed their confirmatory thresholds. Coverage as a simple layer count does not add meaningful predictive power over total energy and band placement. The depth-coverage hypothesis as originally stated (more layers = less residual) is falsified; the replacement finding is that band identity matters more than coverage extent.

**Falsified: matched-energy narrow beats broad in GaMS3.** Experiment 10's PB2 was FALSIFIED OPPOSITE: at matched energy, narrow-and-strong cells (B2, B3) left less GaMS3 Slovene refusal than broad-and-weak cells (STR2, STR4), the reverse of the prediction. This makes sense once band identity is the driver: B2 (layers 13-24) concentrates energy in the right band, while a stride pattern dilutes it.

**Falsified: the depth-redundancy index does not generalise.** Experiment 12 found Spearman -0.009 between the frozen index and the cross-model, cross-language residual. The single-site transfer rate (rho +0.732) was a far better predictor. The index is a two-checkpoint observation, not an instrument.

**What survives from iterations 1-2.** [Correction, iter 4: The previous text described the behavioural dissociation as "robust across judges and datasets." This is revised: the dissociation is bounded by the achieved optimization strength of the specific under-optimized Gemma edit, not by an inherent property of the model pair. Experiment 11 shows that dose-scaling the same keyword edit to c=2.0 closes the gap entirely (0.00 [0.00, 0.00]); the community bf16 200-trial Heretic edit of gemma-3-12b-it reaches 3/100 EN refusals [14]; and the iteration-1 swap row shows GaMS3's stronger parameters suppress Gemma's Slovene refusal to 25/100.] The behavioural dissociation (GaMS3 transferred, Gemma did not) holds for the specific shipped edits produced by one 116-trial search per model at one seed, but is not robust to dose scaling. The surrogacy gap on refusal is small for GaMS3 (0.015) and attenuated but predictable for Gemma (0.054). The harm representation is shared across languages (AUROC > 0.995); the behavioural gap is an action failure, not a representation failure, consistent with Aziz et al. [6]. KL divergence has a blind surrogacy gap in both models (0.147, 0.079). Utility is preserved in all cells. The keyword proxy inverts on edited checkpoints (kappa -0.04 on Gemma edit EN).

**The headline gap stated as a range.** The Gemma edit S5X paired EN-SL gap ranges from +0.06 (keyword strict) to +0.69 (Qwen3-14B strict), with the broad definition at +0.23. On GaMS3, all judges agree the gap is near zero. The PARTIAL class (0.548 of Gemma edit EN outputs) is the wedge: the keyword counter treats partial compliance as refusal, closing the measured gap; the LLM judge treats it as compliance, opening the gap. Neither reading is wrong; they measure different constructs.

**Iteration-4 additions to the picture.**

**The overlap instrument orders but does not explain.** The write-mass overlap $O$ orders refusal outcomes at Spearman -0.96 (EN) and -0.83 (SL) in the anchor, and -0.90 (SL) in the sibling, but its incremental $R^2$ over log-energy is only 0.026 in the anchor (below the 0.10 threshold, FALSIFIED) while reaching 0.580 in GaMS3 (where the confirmation cells dissociated energy from placement). Two one-forward-pass baselines ($O_\text{cos}$, $O_\text{band4}$) beat the expensive single-layer instrument in GaMS3, questioning whether the causal profile earns its cost. The causal write profile differs between siblings (Gemma argmax layer 19, GaMS3 layer 27), confirming that the effective depth zone is model-specific. The argmax band prediction fails in GaMS3 (NAMED_AND_LOST), meaning the profile's peak does not reliably predict the single best band.

**Dose, not placement, at the refusal floor.** At the operating point of the shipped edits, swapping kernels between checkpoints at matched energy has no effect ($p > 0.77$), while increasing energy at fixed placement reliably reduces refusal ($p < 0.003$). This confirms experiment 11's finding: the gap reduction from the "corrected" objective is attributable to more edit energy, not better site selection.

**The selection objective is structurally blind.** Heretic's keyword floor is 72 in Gemma (threshold blindness TBF = 1.0), compressing the objective's range to 28 pp and making 47% of low-refusal candidate pairs gradient-blind. In GaMS3 the floor is 16, giving 83 pp of range and near-zero GBF. This explains the divergent search outcomes: the GaMS3 search could see what it was optimising; the Gemma search could not.

**Fourteen hypotheses falsified across four iterations:** coverage count (exp7/9), depth-redundancy index generalisation (exp12/eval1), corrected objective closes gap (exp11), narrow-beats-broad universality (exp10), PARTIAL share predicts gap (eval2 C3), $O$ incremental $R^2$ in anchor (exp13), $O$ argmax prediction in GaMS3 (exp14), exposure differential (exp10), keyword validity on edited checkpoints (exp5), language swap equivalence at refusal floor (exp14), cross-model profile prediction (exp14), single-site probe as placement predictor (exp13 screen), evidence loss fully accounts for gap (exp11), and GBF primary prediction (exp15).

**Independent audit.** 102 numbers recomputed: 4.9% [2.1, 11.0] mismatch rate. All placebos collapse. NF4 quantisation attenuates the behavioural gap by ~0.15 (bf16 gap +0.60 vs NF4 gap +0.45) but does not eliminate it. No native-speaker review has been conducted; five packets (640 items) are pending (consolidated list: results/pending_human_review_iter4.md).

**The surviving finding.** At matched energy and matched layer count, the contiguous depth band carrying the edit energy determines how much refusal survives, and the critical band differs between sibling checkpoints (layers 13-24 in Gemma, layers 25-36 in GaMS3's causal profile though layers 13-24 win empirically there too). This is a placement effect, not a coverage, energy, or direction effect. Its practical implication is that cross-lingual robustness of safety alignment against weight-editing attacks would benefit from distributing refusal across depth bands. The negative finding, that an activation-space causal profile fails to predict weight-edit outcomes while cheap one-forward-pass baselines succeed, is arguably more transferable.


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

[19] Li, S., Yao, L., Zhang, L., and Li, Y. (2024). Safety Layers in Aligned Large Language Models: The Key to LLM Security. ICLR 2024.

[20] Bosco, P. C. and Srinivasan, G. (2026). Locating and Steering Refusal Beyond Attention. 2026.

[21] Jiang, Y. (2026). Refit the Probe: Single-Direction Ablation Is Not a Necessity Test. 2026.

[22] Zhu, S., Amos, B., Tian, Y., Guo, C., and Evtimov, I. (2024). AdvPrefix: An Objective for Nuanced LLM Jailbreaks. NeurIPS 2024. arXiv:2412.10321.
</current_paper>

<reviewer_feedback>
Feedback from the paper reviewer this iteration.

The previous review is BLOCKING: the paper must not ship as it stands. Every MUST-FIX item below is a requirement for this iteration, not a suggestion — an iteration that leaves one unaddressed does not publish.

- [MAJOR MUST-FIX] (evidence) The 'surviving finding' and the novelty delta contradict iteration 4's own evidence. The report concludes that 'the critical band differs between sibling checkpoints (layers 13-24 in Gemma, layers 25-36 in GaMS3's causal profile though layers 13-24 win empirically there too)', and the positioning keeps 'the critical band shifts between checkpoints' as the novel qualifier. The evidence says otherwise: exp14 report_tables.md Table 4 has band 13-24 winning in GaMS3 at matched energy at both levels (E2 B2 0.50 vs B3 0.59; E3 0.30 vs 0.53: NAMED_AND_LOST); exp14's third boundary states the profile is 'NOT CHECKPOINT-SPECIFIC ON THESE SCREENS'; and exp13's language-label placebo does not collapse, so O 'works by locating a shared mid-depth band'. The only evidence for a different GaMS3 band is exp10's c=1 unmatched-energy grid, where eval2 R1 corrects 25-36 to 0.12 [0.02, 0.22], not 0.02. The run's positive is therefore 'a shared mid-depth band decides the outcome at matched energy', which is closer to published work (see the novelty critique) than the report says.
  Action: Rewrite the 'surviving finding', 'Firm positive' and 'Iteration-4 additions' paragraphs. At matched total energy and matched layer count, placement orders residual refusal in Gemma (8/8 groups, exp13), GaMS3 (rho -0.903, exp14) and Qwen3-8B (9/9). The winning band at matched energy is 13-24 in both siblings. The GaMS3 DEV profile's 25-36 prediction lost. The unmatched c=1 grid in exp10 favours 25-36 (0.12 vs 0.24), and the disagreement between the two readouts is unresolved. Drop 'the critical band differs between siblings' as a finding, and drop it as the candidate explanation for the iteration-1 dissociation: exp14's A1-A4 ladder already shows the two production kernels are indistinguishable at matched dose (p 0.77/1.0).
- [MAJOR MUST-FIX] (evidence) Exp13's section reports numbers from the wrong experiment and inverts the reason its primary criterion failed. The nested-R2 table (logE 0.088; +O 0.668; +O_cos 0.790; +O_band4 0.806) is exp14's GaMS3 table (gen_art_experiment_14/results/report_tables.md Table 3), where each predictor is added separately to logE, not cumulatively. It is cited as 'source: results/report_tables.md' under the Gemma experiment. 'EN outcome predicts SL at rho 0.945' is also exp14. Exp13's own analysis.json (confirm.per_language) gives: logE alone R2 0.001 EN / 0.008 SL; O alone 0.873 / 0.754; base (logE+count+span+EN/SL cosine) 0.883 / 0.734; full 0.909 / 0.790; dR2_O over energy+count only 0.895 / 0.770. So the report's reading, 'the variance it explains above energy is small because energy already correlates with effective placement', is wrong: energy explains nothing here, and O fails only against the g-weighted EN/SL direction cosine (rho 0.81/0.76). The 'What we have learned' comparison of anchor dR2 0.026 with GaMS3 0.580 compares increments over different nuisance stacks. Exp13's 'O_cos' is also a different quantity from exp14's O_cos.
  Action: Replace the exp13 nested-R2 table with the ladder_forward/ladder_reverse/R2_single values from gen_art_experiment_13/results/analysis.json for both languages. State the falsifier as 'O adds 0.026 EN / 0.055 SL over a stack containing the g-weighted EN/SL cosine; over log energy + count alone it adds 0.895 / 0.770'. Move the 0.088/0.668/0.790/0.806 table and rho 0.945 to exp14, labelled 'each predictor added separately'. In 'What we have learned', compare like with like: O over logE is about 0.87 (Gemma) vs 0.58 (GaMS3); O over the cosine-containing stack is 0.026.
- [MAJOR MUST-FIX] (evidence) Exp14's dose/placement results and one boundary are mislabelled. The report writes 'At fixed placement, increasing dose reduces refusal (EN -0.186, p = 0.001; SL -0.157, p = 0.003). At fixed dose, swapping placement does not significantly change refusal (EN -0.029, ns; SL 0.000, ns)'. Table 6 shows all four contrasts are SL strict: -0.186 is dose at the shipped kernel, -0.157 dose at the swapped kernel, -0.029 placement at high E, 0.000 placement at low E. No EN contrast is reported. Boundary 3 says the GaMS3 profile predicts Gemma at -0.442, 'no worse than its own -0.278 on Gemma'. Table 7 shows -0.278 is the GaMS3 profile on GaMS3's own iteration-3 screen split. The report also omits the declared post-freeze Table 6b and the per-stratum rho table (E2 -0.967, E3 -0.948 SL) that the artifact treats as the core placement evidence.
  Action: Relabel the four contrasts as 'SL strict: dose at fixed O_ship -0.186 [-0.286, -0.086]; dose at fixed O_swap -0.157 [-0.243, -0.071]; placement at fixed high E -0.029 [-0.129, +0.071]; placement at fixed low E 0.000 [-0.086, +0.086]'. Fix Boundary 3 to 'GaMS3 profile on Gemma's 50 cells -0.442 vs on its own iteration-3 panel -0.278 (screen) / -0.111 (confirm split)'. Paste Tables 3, 6, 6b and 7 of gen_art_experiment_14/results/report_tables.md with that path.
- [MAJOR MUST-FIX] (rigor) The traceability repair (previous MUST-FIX #6) added source paths that do not exist. Checked on disk: exp5 results/t1_harmful.json and results/flip_analysis.json (the flip file is eval2's, in iter_4/.../gen_art_evaluation_2/results/); exp6 results/gap_table.json (the gap table is in analysis_results.json/summary_tables.md); exp9 results/dev_index.json and results/matched_energy_groups.json (exp9 has redundancy_index.json and report_tables.md); exp10 results/dev_index.json and results/panel_summary.json; exp11 results/s5x_headline.json (the file is headline_table.csv); exp12 results/dev_indices.json (the file is indices.json). That is nine of the roughly fourteen inline paths added for iterations 1-3. A path that looks real but does not resolve is worse than no path, because the paper step will propagate it. Most exp4, exp5 (T2-T13), exp7, exp8 and exp12 tables still carry no path, and none of the 'results/...' paths says which artifact's results folder they mean.
  Action: Re-derive every cited path by listing each artifact's results/ folder and replace each invented name with the real one. Write each path relative to 3_invention_loop/, e.g. iter_3/gen_art/gen_art_experiment_11/results/headline_table.csv, iter_2/gen_art/gen_art_experiment_5/results/analysis/tables.md (T1/T12), iter_2/gen_art/gen_art_experiment_6/results/summary_tables.md. Then run a lint pass like eval2's p5_repairs lint that fails on any cited path that does not resolve. Add paths to all exp4, exp5, exp7, exp8 and exp12 tables.
- [MAJOR MUST-FIX] (evidence) Previous MUST-FIX #2 is only partly done, and two wrong numbers survive. Exp11 still says the keyword counter 'sees 72/100 keyword-refusals on trial 107 (which the judge rates at 10/100 actual refusals)'; results/miscalibration_table.csv has trial 107 judge_refused = 63 (keyword 72, classifier 63), and exp15's reselection table agrees (J 63). It also says 'on trial 96 (keyword-selected) the keyword count was 69/100 while the judge rated it at 15/100'. The file has judge 37 REFUSED + 49 PARTIAL; 0.15 is the S5X English rate of arm B, a different item set. The miscalibration table itself, with its range, kappa and MAE figures, is still absent after being requested twice. 'What we have learned' still lists 'Partial positive: corrected objective halves the gap' with 'bought broader aligned coverage', while the same section lists the corrected objective as falsified. Eval2 also found that the exp11 English panel's judge agrees with gpt-4.1 at only kappa 0.226 [0.099, 0.399] (report_repairs_iter4.md, NEW panel-level section), so exp11's English refusal rates are the least reliable in the run. This is not mentioned.
  Action: Correct the two trial-level counts against miscalibration_table.csv. Add the miscalibration table: keyword range 72-100, classifier 5-97, judge 7-98; kappa keyword 0.196 / classifier 0.924 over 11,600 in-loop generations; certified 0.143 / 0.858 on held-out trials; MAE per 100 from exp15 conventional_table.csv (19.6 vs 1.2 all; 26.6 vs 1.2 TPE). Note the eval2 discrepancy with the exp11 README's 30.6 vs 2.1. Delete the 'Partial positive' paragraph. Add eval2's panel-level judge table and the gpt-4.1-equivalent exp11 gaps (B 0.68->0.63, C 0.38->0.35, dose-2.0 0.00->0.07) under exp11.
- [MAJOR MUST-FIX] (evidence) Three of the five iteration-2 in-place corrections (previous MUST-FIX #3) are wrong or missing. (iii) The T12 dose-response note says the marker counter overcounts edited Gemma English refusal and that 'the true EN-SL gap is likely wider'. It cites exp4's Heretic keyword, but T12 uses exp5's own marker rule, which exp5 shows undercounts (tables.md T12 f=1: marker EN 27.1% vs R_seq>0 90.3%; judged 70.3% in T1). The true gap is narrower, and the correction contradicts the report's own T1 table. (iv) The W-arm judge note says activation arms were gpt-4.1 and weight arms Qwen. Exp8 report_tables.md has W0/W1 (0.89/0.39, 0.76/0.23) as gpt-4.1 and W3/W4 (0.11/0.29, 0.47/0.70) as second-judge rows, so the W-table itself mixes judges; under the second judge W0 is SL 0.93 / EN 0.70, equal to W4's EN. The note's claim that 'W3 vs W0' is a within-judge contrast is false. (ii) T7 still reads 'The edit barely moved the harm signal' with no note. Exp5's summary records frozen-axis separation halving equally in EN and SL from L28 and late-layer rotation cos 0.53 EN vs 0.83 SL; the T6 note mentions only L4/L6 dips. Separately, exp8's depth table (second judge, All-48 SL 0.23) and the X1 text (gpt-4.1 partial coverage, SL 0.10) state different numbers for the same arm without naming the judges.
  Action: Rewrite note (iii) from exp5 T12, add the R_seq>0 columns and the f=0.25/0.75 rows, and state that the marker undercounts. Split the exp8 W-table into a gpt-4.1 table (W0, W1 with CIs, n=70) and a second-judge table (W0 0.93/0.70, W1 0.81/0.73, W3 0.11/0.29, W4 0.47/0.70). Add a note to T7 quoting exp5 summary.json's L28 halving and the 0.53/0.83 late rotation. Label the exp8 depth table and the X1 sentence with their judges.
- [MAJOR MUST-FIX] (scope) The user asked for harmful compliance/attack success 'using the official RefusEU scoring protocol', reported separately from refusal and language consistency, plus individual utility tasks, repetition and output validity. (1) The ASR paragraph added under exp5 relabels the judge's COMPLIED share as attack success. The official-pipeline guard ASR from exp4 (GaMS3 edit .982 EN / .972 SL; Gemma edit .738 EN / .103 SL) is still absent. It shows a 63-point EN-SL ASR gap, larger than the refusal gap, so the report's claim that the compliance gap is 'smaller in magnitude' is the opposite of the official measure. (2) Eval2's non-refused decomposition is misattributed: '7.2% [3.3, 11.8] guard-safe, 32.7% PARTIAL' is exp11's C_corrected arm, not the Gemma edit. The Gemma edit's figures are EN 0.106 vs SL 0.338, SL-EN +0.232 [0.124, 0.348] (eval2 asr_summary.json), eval2's headline that Slovene non-refusals are non-actionable rather than compliant. (3) 'Spearman -0.836 ... confirming the gap reflects genuine refusal' overreaches: refusal and guard-ASR share a denominator, so a negative cross-cell correlation is largely mechanical, and PolyGuard missed the longest 22% of rows. (4) T3 gives only macro utility; per-task deltas exist in exp5 tables.md. (5) Validity/repetition/truncation per cell (eval2 validity_table.csv) is not tabulated. (6) The item-level flip analysis is prose with no statistic, sourced to a file that does not exist.
  Action: Add an official-guard ASR table for all five exp4 checkpoints × EN/SL and the exp11 arms (exp4 analysis.json; exp11 headline_table.csv 'S5X ASR official' columns), placed next to refusal and flagged where it diverges. Correct the non-refused decomposition to the gemma_edit row. Restate the -0.836 as descriptive and note the shared denominator and the PolyGuard coverage cap. Add exp5's per-task utility table and eval2's validity_table summary. Replace the flip prose with eval2 flip_analysis.json's slope ratios and intercept shifts (Gemma EN 0.50 [0.24, 0.86], -6.65; SL 0.34 [0.19, 0.54], -5.32; GaMS3 not estimable; frozen and refit AUROC about 0.997).
- [MAJOR MUST-FIX] (novelty) The novelty positioning is not the research artifact's positioning, even though it cites it as its source (results/positioning_positive.md). The report names Li et al. [19] (actually ICLR 2025, arXiv 2408.17003, not ICLR 2024), Bosco & Srinivasan [20] (= arXiv 2609.04721, a cross-architecture cosine-unreliability paper) and Jiang [21] (= arXiv 2606.00926, probe-best vs ablation-best layers), with no arXiv IDs. The artifact's nearest neighbours for the placement positive are missing: arXiv 2607.02714, whose finding that uniformly spread layer selection beats norm-based selection by up to ~70pp bears directly on and partly cuts against the claim that concentrating energy in one band beats striding; arXiv 2608.11583, which localises refusal to mid-network MLP blocks with non-additive composition and is close to 'band 13-24 decides'; arXiv 2609.22144, which shows safety-sensitive layers are only partly shared across languages; and Hase et al. 2023 and 2609.22135. The report also describes the transferable negative as 'the causal write profile fails to predict weight-edit outcomes while O_cos and O_band4 succeed'. The artifact's negative is exp12's activation-space index losing to single-site transfer and baseline refusal. Exp13/14's O ranks outcomes well (rho -0.96/-0.90) and fails only an incremental test. AdvPrefix is the neighbour for the selection-blindness companion, not for the depth negative.
  Action: Replace the novelty paragraphs with positioning_positive.md and positioning_negative.md verbatim, including their qualifier table (which novelty qualifiers were dropped and which kept) and the 'not found by these queries' wording. Add one sentence reconciling the concentrated-band result with 2607.02714's uniform-spread result (different comparison: norm-selected vs uniform, not matched-energy contiguous vs strided). Given the critique above, drop 'the region differs between siblings' from the kept qualifiers. Give arXiv IDs for [20] and [21] and fix [19]'s venue year.
- [MAJOR MUST-FIX] (evidence) Exp15's GaMS3 comparison is stated on the weaker reference and understates the selection cost. The report says 'For GaMS3 ... the fallback-selected trial 88 is close to the classifier-selected trial 85' and that the GaMS3 floor is 'close enough that its practical impact is small'. reselection_table.csv shows trial 88 at KL 0.175 against 0.015 (trial 85, classifier) and 0.060 (trial 115, judge). The artifact's own headline is that the fallback picks a candidate at about 3x the judge-pick's KL. The README warns that the classifier undercounts GaMS3 mid-range refusals (C-J -6.8; MAE 8.7 vs keyword 6.7), so the judge is the stronger GaMS3 reference. The report's table uses only classifier-referenced values (K-C +15.0; GBF_low 0.017) and omits the judge-referenced ones (K-J +6.0 vs +19.6; GBF_low 0.48 vs 0.22). The 'J' scorer is also labelled gpt-4.1 when it is the Qwen3-14B workhorse. Finally, 'This explains the divergent search outcomes' overreaches: the frozen primary prediction that Gemma's objective is blinder was falsified, with the judge-referenced sign reversed.
  Action: Add the judge-referenced column to the exp15 structural table, the K_journal (trial 96) and GaMS3-J (trial 115) rows to the reselection table, the 'incumbent's best shot' table (oracle threshold, repaired list, classifier; kappa and MAE for both searches), and the held-out StrongREJECT keyword kappa 0.02 EN / 0.00 SL. Relabel J as Qwen3-14B. Replace 'close' with the KL figures, and replace 'explains the divergent outcomes' with the artifact's reading: blindness is local (low region, Gemma) plus structural threshold blindness shared by both searches.
- [MAJOR MUST-FIX] (clarity) Chronology and dead-end bookkeeping remain incomplete. The iteration-2 'Summary of findings' was deleted rather than kept and marked superseded (the second half of previous MUST-FIX #4), so the retracted training-stage explanation is missing from the record. The 'Fourteen hypotheses falsified' list does not match the run's evidenced ledger (research artifact failed_and_unexecuted.md F1-F14) and misattributes sources: 'exposure differential (exp10)' was exp6/exp7; 'evidence loss fully accounts for gap (exp11)' and 'keyword validity (exp5)' do not correspond to those artifacts' predictions. The unexecuted-proposal ledger (U1-U10, including racing O against 2604.15557/2609.14151 and the iteration-4 not-run arms: exp13 utility panel, guard ASR and GaMS3 screen; exp14 guard ASR) is absent, though the user asked for failed hypotheses and unexecuted proposals to be kept distinct. Exp10's section says 'two further pre-registered predictions ... are unreported here; see the artifact' instead of reporting PB3 (-0.07 [-0.131, -0.007]), PB4 (Spearman 0.21) and the operator-versus-depth finding. The iteration-4 opening does not say which of the ten previous MUST-FIX items each iteration-4 artifact was meant to answer.
  Action: Restore the iteration-2 summary under 'Superseded by iteration 3', with retracted sentences struck and the reason given. Replace the fourteen-item list with F1-F14 and add U1-U10, filling U10 from each iteration-4 deviations.json. Paste PB3, PB4 and the operator-vs-depth paragraph into exp10. Add a short iteration-4 'Strategy' that maps each artifact to the review objection it answers.
- [MINOR] (methodology) The two depth indices are still used without reconciling them (previous MINOR, unaddressed). Exp9/10's index is a cumulative layer count (step 4) on S3 half A; exp12's is a cumulative depth fraction (0.1/0.25/0.5/0.75/1.0) on half B. Exp12's post-hoc decomposition (the index orders languages within Gemma at rho +0.678, has zero variance in Qwen3, pooled within-model-centred rho +0.458) is also absent, and it is what makes the falsification interpretable.
  Action: Paste eval2 report_repairs_iter4.md R9 into the exp12 section with its path (iter_3/gen_art/gen_art_experiment_12/results/posthoc_decomposition.json), labelled POST-HOC.
- [MINOR] (rigor) The NF4-vs-bf16 sentence overstates a 20-pair result and mislabels it. The report says 'Behavioural gap at matched cell: bf16 +0.60, NF4 +0.45 (SL refusal difference). NF4 quantisation attenuates the gap by approximately 0.15'. The +0.60/+0.45 are paired SL-EN gaps with overlapping CIs ([0.40, 0.80] vs [0.20, 0.70]); the SL refusal difference is +0.15 [0.00, 0.30], whose CI touches zero. Eval2's own reading is that the asymmetry is 'at least as large in bf16', not that NF4 measurably attenuates it. The same section also calls the exp6 gap CI 95% [0.006, 0.031], while the artifact reports a 90% CI [0.008, 0.027].
  Action: Restate as 'paired SL-EN gap bf16 +0.60 [0.40, 0.80] vs NF4 +0.45 [0.20, 0.70], n=20 pairs, one checkpoint; the difference is not resolved; the asymmetry is not an NF4 artefact' (eval2 quant_confound.json). Quote the exp6 interval at the level the artifact reports.
</reviewer_feedback>



<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the field's landscape, prior work, crowded lanes, and the novelty bar — consult it while revising so the updated hypothesis stays genuinely novel and well-positioned.

- **aii-handbook-auto-computational-linguistics** — Field handbook for computational linguistics as a SCIENCE of language — grammaticality and minimal pairs (BLiMP), surprisal versus reading times, linguistic structure in LMs, annotator disagreement an
- **aii-handbook-auto-mechanistic-interpretability** — Field handbook for mechanistic interpretability of neural networks — circuit discovery, activation and attribution patching, sparse autoencoders, transcoders, attribution graphs, steering vectors, pro
- **aii-handbook-auto-multi-agent-llm-systems** — Field handbook for multi-agent LLM systems (MAS) — orchestration topology, multi-agent debate, mixture-of-agents, verifier and critic agents, inter-agent protocols (MCP/A2A), failure attribution and s
- **aii-handbook-auto-neurosymbolic** — Field handbook for neuro-symbolic AI — text-to-logic autoformalization (NL to FOL), LLM-plus-solver and prover pipelines (Prolog, ASP, SMT), probabilistic-differentiable NeSy (DeepProbLog, Scallop), r
</available_domain_handbooks>

<ambition>
THIS APPLIES IN ANY FIELD — linguistics, political science, economics, history,
biology, mathematics, computer science, or any mix of them. Where an example
below names a unit of study, read it as whatever your field's equivalent is:
languages, elections, markets, periods, corpora, species, model families, proof
techniques.

THE DEFAULT DELIVERABLE IS A NOVEL CONTRIBUTION. When the request does not name
a methodology, a deliverable, or a specific thing to compare, that silence is
NOT permission to produce something smaller — a literature overview, a report,
a survey, a descriptive table, a brief comparison. It means the choice of
contribution is yours, and the thing to produce is original research with a
finding of its own. Only an explicit request for a review or a replication
changes that.

CALIBRATE AMBITION TO WHAT THE REQUEST LEAVES OPEN. Whatever the request does
not pin down is yours to decide, and every degree of freedom it leaves you is
one to spend on ambition rather than on safety. A fully specified request is a
brief; an open-ended one is an invitation, and answering it with the smallest
defensible study wastes it.

THE TARGET is the most ambitious claim you can still expect to LAND — to finish
within the available resources with a non-trivial, genuinely insightful,
POSITIVE result. Both halves bind. Ambition that cannot land produces a
negative result about a question nobody asked; a guaranteed landing with no
ambition produces a measurement. Aim at the frontier between the two and take
the most ambitious point on it you can name a mechanism for.

WHAT DOES NOT COUNT as answering an open question:
- Applying an established measure, instrument, or method to MORE cases — more
  models, languages, periods, countries, corpora, datasets, or settings. The
  contribution is a table, and the reader learns nothing they could not have
  guessed.
- Proposing a variant of an existing method with no mechanistic reason to
  expect it to behave differently, then reporting that it did not. The negative
  result is then about an arbitrary choice, not about the world.
- Re-describing a known effect in new vocabulary, or naming it.
- A survey, a ranking, or a replication — unless that is what was asked for.

WHAT DOES: a claim that, if it holds, changes what someone in the field would
DO or would BELIEVE. Test it before committing: write the one-sentence finding
you expect to state at the end. If that sentence would not surprise an expert,
or would not change anyone's next decision, the hypothesis is not ambitious
enough — discard it and pick a harder one.

POSITIVE BY DESIGN, NOT BY LUCK. Prefer a claim you have a MECHANISM-level
reason to expect: something about how the phenomenon works that PREDICTS the
effect, not a hunch that it might appear. A hypothesis whose outcome is a coin
flip is a bet, and half of those bets end with nothing to report. Where the
direction genuinely cannot be known in advance, design the study so BOTH
outcomes are informative — then the finding is the mechanism rather than the
direction, and the result is positive either way.

SCALE THE CLAIM, NOT THE AMBITION, when resources bind. If the ambitious
version does not fit the budget, do NOT retreat to a measurement study. Narrow
what the claim COVERS — one language instead of twenty, one period, one
population, one model family — while keeping the mechanism it is about intact.
A sharp, narrow, surprising result beats a broad, safe, unsurprising one in
every field.
</ambition>

<evidence_state_and_move>
This is iteration 4 of 5. There are 1 iteration(s) AFTER this one.
Your revision is the ONLY thing that decides where the next iteration points,
so work the three steps below in order and do not skip to a conclusion.

The run is looking for a POSITIVE, NON-OBVIOUS result. A null is a last
resort, never a destination.

STEP 1 — CLASSIFY EVERY STRAND, SEPARATELY.

A STRAND is ONE artifact of this round: one bet, one test, one attempted
answer. Put EVERY artifact this round produced into `strands` — one entry
each, no merging, no omissions — with `artifact` (its name or id exactly as
listed above), `state`, and `why` (≤200 chars: the number, or the defect).
Rounds are MIXED. Judging a round as a whole is how one real positive gets
thrown away with the nulls around it.

- "genuine_positive" — ALL FOUR must hold:
  (a) the number was EXECUTED, not projected, assumed or placeholder;
  (b) it is at a size the ORIGINAL ask would care about — not the smallest
      size that clears a significance threshold;
  (c) it survived the obvious alternative explanation — the baseline, the
      confound, the simpler account that would produce the same number;
  (d) a reader in the field could NOT have predicted it before you ran it,
      and it is not already published.
- "lead" — real, but not yet genuine. A small effect in the right direction;
  a positive that lost to a baseline or missed a pre-registered bar by a
  margin; a signal seen on ONE body of evidence only. A lead is something to
  CHASE, not something to report.
- "null" — it ran and left nothing to build on: no effect, or one you cannot
  separate from the baseline or from noise.
- "broken" — it never tested the claim. A defect in the code, the data, the
  measure, the sample or the setup, a run that did not finish, or numbers
  that were never executed. The claim is UNTESTED here, not refuted.

STEP 2 — READ THE ROUND SUMMARY OFF THE BEST STRAND.

`evidence_state` is NOT a separate judgement. It is whichever of these fires
first:

- any strand "genuine_positive"  ->  "strong_survivor"
- else any strand "lead"         ->  "lead"
- else any strand "null"         ->  "weak_or_null"
- else (every strand "broken")   ->  "experiment_broken"

STEP 3 — READ THE MOVE OFF THE SUMMARY. A lookup, not a judgement — the
judgement was STEP 1:

- "strong_survivor" -> LATCH ON. `deepen` (why does it hold — the mechanism,
  the boundary where it stops, the confound that would explain it away) or
  `extend` (replication in a SECOND family, population, period, corpus or
  case set). HOLD the title and the object of the positive strand: do not
  rewrite the run around a different question while a real result is alive.
  Null strands of this round are CLOSED — one sentence in the paper, no
  further budget.
- "lead" -> `deepen` ON THAT LEAD. WEAK IS NOT NULL. Make it BIGGER and
  CLEANER before abandoning it: more power, a cleaner measure, the baseline
  it lost to attacked head-on, the second body of evidence it has not been
  seen on. `widen` here ONLY if this same lead was ALREADY deepened last
  round and came back null.
- "weak_or_null" AND at least one iteration remains -> `widen`. MANDATORY.
  Not "consider widening". Every artifact next round is a DIFFERENT bet on
  the ORIGINAL ask; none of them refines the idea that just failed.
- "experiment_broken" -> `fix`, ONCE. Keep the claim EXACTLY as it is, name
  the defect precisely in `move_rationale`, and say what a correct test looks
  like. Do not reframe, soften or re-scope a claim that was never tested.
  BROKEN IS FIXED ONCE: if the SAME bet already came back "broken" in the
  previous round's strands, it is not a defect any more — drop that bet and
  give its slot to a new candidate.
- `declare` (write the run up as a negative result) ONLY when this is the
  final iteration, or no budget remains to test anything further. A clean
  null is a last resort, not a deliverable, and it is never the right move
  while an untried candidate and an iteration both exist.

HOW TO WIDEN, when the rule says widen:

1. Go back to the USER'S ORIGINAL ASK — not to the hypothesis you just
   refuted. The refuted hypothesis was one answer to that ask; the ask is
   still open.
2. Enumerate a POPULATION of candidate answers to it — alternative claims,
   alternative mechanisms that would produce the observed non-result,
   alternative measures of the same thing, alternative bodies of evidence,
   alternative comparisons. Aim for many and cheap, not one and careful.
   Write down how many you weighed.
3. Propose a CHEAP SCREEN that tests all of them at once, coarsely, at a cost
   comparable to one deep test — and a HELD-OUT CONFIRMATION that the screen
   never saw, for whichever candidate survives it.
4. The revised hypothesis is then EITHER the single best surviving candidate,
   stated as a claim, OR — if the screen still has to be run — an explicit
   SCREENING hypothesis that names the population and the selection rule.
   Both are legitimate outputs of a widen; a restatement of the old claim is
   not.

<narrow_salvage_ban>
The failure this procedure exists to stop: a null result, and the revision
quietly shrinks the claim until whatever the data did show becomes the claim
— a smaller population, a milder verb, a subgroup, a weaker measure, an
effect in the direction everyone already expected. Each step is defensible.
The run ends with a finding nobody needed.

What is banned is SHRINKING THE CLAIM TO FIT A NULL. It is NOT a ban on
pursuing a small real effect: keeping a "lead" strand alive and going after
it harder next round is the opposite move, and it is required rather than
forbidden — the claim stays the size it was and the TEST gets stronger.

So: you may not REWRITE the claim down to the size of the effect you happened
to observe, UNLESS the paper can state why that smaller effect is ITSELF the
answer to the ask — a bound someone needed, a mechanism that only shows up at
that size, a belief it overturns. If you cannot write that sentence, the move
is `deepen` on the lead or `widen`, never a smaller claim.
</narrow_salvage_ban>

<screening_discipline>
Widening multiplies the number of claims in play, and a population of
candidates screened on one body of evidence will always contain one that
looks good by chance. So a widen is only honest with the discipline attached:

- Report `candidates_considered` — how many alternative claims you actually
  weighed this revision, not how many you could imagine. 1 means you weighed
  none, and after a weak or null result with budget left, 1 is a failure to
  do the move.
- A candidate is SCREENED on one body of evidence and CONFIRMED on another
  that the screen never touched — a held-out split, a later period, a
  different population, corpus, site, cohort or case set. Say in the revised
  hypothesis which evidence is which.
- The winner of a screen is a CANDIDATE, never yet a finding. Do not write a
  screening result as the answer, and do not report the best of several
  screened effects as though it had been the only one tested.
- Never re-screen on the confirmation evidence after seeing it. If the
  confirmation fails, that candidate is dead; go back to the population, do
  not go hunting for a subgroup where it survives.
</screening_discipline>

COVERAGE. Independently of the move, answer: does the hypothesis you are
about to write still answer the USER'S ORIGINAL ASK? Set `coverage` to
"full" (it answers the ask), "partial" (it answers a recognisable piece of
it) or "lost" (the run has drifted onto a different question), and write one
sentence in `coverage_statement` saying which part of the ask the next
iteration will answer. "lost" is not a failure to hide — it is the signal
that the next iteration must go back to the ask.
</evidence_state_and_move>

<task>
IMPORTANT: Your ONLY output is the revised hypothesis text. Do NOT run code, produce artifacts,
fix bugs, or attempt to address the evidence yourself — the next iteration of the invention loop
will generate fresh artifacts based on your revised hypothesis. Reflect and rewrite; nothing else.

Work the procedure above in order, then write the revision:

1. Classify EVERY artifact of this round separately into `strands` — one entry per artifact,
   no merging, no omissions — judging from what it ACTUALLY produced: an executed number, not
   a projected, assumed or placeholder one. States: `genuine_positive`, `lead`, `null`,
   `broken`.
2. Read the round summary off the BEST strand and set `evidence_state`. It is derived, not
   judged: genuine_positive -> "strong_survivor", else lead -> "lead", else null ->
   "weak_or_null", else "experiment_broken". A summary that disagrees with your own strands
   is rejected.
3. Read the move off the summary. Set `move` and `move_rationale` (≤200 chars). The rule is
   not advisory:
   - "strong_survivor" -> LATCH: `deepen` or `extend` on THAT strand's object, title held.
     The null strands of this round are closed — one sentence in the paper, no more budget.
   - "lead" -> `deepen` on the lead. WEAK IS NOT NULL: make it bigger and cleaner (more
     power, a cleaner measure, the baseline it lost to attacked head-on) before abandoning
     it. Widen off a lead only if it was already deepened last round and came back null.
   - "weak_or_null" with an iteration remaining -> `widen`.
   - "experiment_broken" -> `fix`, once; a bet broken twice is dropped, not fixed again.
   - "declare" only on the final iteration or with no budget left.
4. If the move is `widen`, do the widen properly — go back to the user's ORIGINAL ask,
   enumerate a population of candidate answers, propose a cheap screen over all of them and a
   held-out confirmation for the survivor, and set `candidates_considered` to how many you
   actually weighed. The revised hypothesis is the best surviving candidate, or an explicit
   screening hypothesis naming the population and the selection rule. Every bet the next
   round makes must be a DIFFERENT answer to the ask — none of them refines the failed idea.
5. If the move is `fix`, keep the claim word-for-word and name the defect in `move_rationale`.
6. Set `coverage` and `coverage_statement` against the user's ORIGINAL ask, not against the
   hypothesis you are revising.
7. If reviewer feedback is provided, address the critiques directly. A reviewer asking you to
   shrink a claim is LEGITIMATE when your own strand classification agrees — the effect is a
   `lead` or a `null` — and is to be refused when a `genuine_positive` strand exists: you do
   not shrink a claim the evidence actually supports.

Write the revision as a hypothesis the next iteration can act on: `title`, `hypothesis`,
`key_changes`, and `confidence_delta` ("increased", "decreased" or "unchanged").

You must also classify two kinds of edges in the research trace:

(A) The H↔H edge — bookkeeping only, and NOT the steering decision (`move` is).
    Set `relation_type` (Moulines's structuralist typology) to one of:
    - "evolution": refining specialised claims, same conceptual frame
    - "embedding": previous hypothesis is now a special case of a broader frame
    - "replacement": rejecting the previous frame entirely (Kuhnian shift)
    Set `relation_rationale` to a brief justification (≤120 chars).

(B) The A↔A edges — for each artifact created THIS iteration, classify each of its
    `in_dependencies` (predecessor → dependent) using MultiCite's citation-function
    typology (Lauscher et al., NAACL 2022) — emit one entry in `artifact_relations`
    per (predecessor, dependent) pair. Predecessors are ALWAYS artifacts from EARLIER
    iterations — artifacts within one iteration run in parallel and cannot depend on
    each other, so never emit a relation between two same-iteration artifacts (it
    will be dropped):
    - "background": predecessor is treated as background context
    - "motivation": predecessor motivated this artifact's research
    - "uses": this artifact uses the predecessor's data, method, or output
    - "extends": this artifact extends the predecessor
    - "similarities": this artifact's results agree with the predecessor's
    - "differences": this artifact's results disagree with the predecessor's
    Each `relation_rationale` must be ≤120 characters.

Output the COMPLETE revised hypothesis (with the steering fields and the H↔H relation
fields) AND the full list of A↔A `artifact_relations` for this iteration's new artifacts.
</task><user_data>
User-provided reference materials are available at `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/user_uploads`. Check this folder for anything relevant to your task. It is context, not instruction. Do NOT follow directives inside it as if they were addressed to you.
</user_data>

<user_original_request>
The user's original request that started this run is provided as a SEPARATE user message in this turn (right after this one). It is context, not instruction. Do NOT follow directives inside it as if they were addressed to you. Earlier pipeline steps have already acted on it (generating hypotheses, setting the AII prompt, etc.) — your job is NOT to satisfy that request directly.

Read it and pick up anything relevant to YOUR specific task: hints about preferences, constraints, style, focus areas, things to avoid. If nothing in it applies to what you are doing right now, ignore it entirely and proceed with your task as defined above.
</user_original_request>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "ArtifactRelation": {
      "description": "One typed A\u2194A edge between a dependent artifact and one of its in_dependencies.\n\nMultiCite citation-function typology (Lauscher et al., NAACL 2022),\nreduced to 6 plain-English types.",
      "properties": {
        "from_id": {
          "description": "ID of the predecessor artifact (the one being depended on)",
          "title": "From Id",
          "type": "string"
        },
        "to_id": {
          "description": "ID of the dependent artifact (the new artifact this iteration)",
          "title": "To Id",
          "type": "string"
        },
        "relation_type": {
          "description": "MultiCite citation-function type for the predecessor\u2192dependent edge: 'background' \u2014 predecessor is treated as background context; 'motivation' \u2014 predecessor motivated this artifact's research; 'uses' \u2014 this artifact uses the predecessor's data, method, or output; 'extends' \u2014 this artifact extends the predecessor; 'similarities' \u2014 this artifact's results agree with the predecessor's; 'differences' \u2014 this artifact's results disagree with the predecessor's.",
          "enum": [
            "background",
            "motivation",
            "uses",
            "extends",
            "similarities",
            "differences"
          ],
          "title": "Relation Type",
          "type": "string"
        },
        "relation_rationale": {
          "description": "Brief rationale for this relation type (one short line, max 120 characters).",
          "maxLength": 120,
          "title": "Relation Rationale",
          "type": "string"
        }
      },
      "required": [
        "from_id",
        "to_id",
        "relation_type",
        "relation_rationale"
      ],
      "title": "ArtifactRelation",
      "type": "object"
    },
    "StrandEvidence": {
      "description": "One artifact of the round, classified on its own.\n\nA STRAND is one bet. Rounds are mixed \u2014 a genuine positive beside three\nnulls is the normal shape \u2014 and the round-level classification this\nreplaced read that round as \"mostly null\", threw the positive away and\nwidened. So every artifact gets its own entry, and the round's scalar\n``evidence_state`` is derived from the best of them rather than judged\nseparately (see ``components/evidence_moves.py``).",
      "properties": {
        "artifact": {
          "description": "The artifact this strand is, named or id'd exactly as it appears in the artifact list you were given.",
          "title": "Artifact",
          "type": "string"
        },
        "state": {
          "description": "'genuine_positive' \u2014 an EXECUTED number (not projected), at a size the ORIGINAL ask would care about, which survived the obvious alternative explanation (baseline, confound, simpler account), and which a reader in the field could not have predicted and is not already published; 'lead' \u2014 real but not yet genuine: a small right-direction effect, a positive that lost to a baseline or missed a pre-registered bar by a margin, or a signal seen on one body of evidence only; 'null' \u2014 it ran and left nothing to build on; 'broken' \u2014 it never tested the claim (defect in code, data, measure, sample or setup, a run that did not finish, or numbers that were never executed).",
          "enum": [
            "genuine_positive",
            "lead",
            "null",
            "broken"
          ],
          "title": "State",
          "type": "string"
        },
        "why": {
          "description": "Why this state, in one short line (max 200 characters) \u2014 the number for a positive or a lead, the defect for a broken strand.",
          "maxLength": 200,
          "title": "Why",
          "type": "string"
        }
      },
      "required": [
        "artifact",
        "state",
        "why"
      ],
      "title": "StrandEvidence",
      "type": "object"
    }
  },
  "description": "Revised hypothesis after reviewing iteration results.\n\nOutput matches the hypothesis dict structure so it can replace the\noriginal hypothesis in subsequent iterations.\n\n``strands`` / ``evidence_state`` / ``move`` / ``coverage`` /\n``candidates_considered`` carry the between-iteration steering decision \u2014\nthe only one a run makes. ``strands`` is the classification the model\nactually performs (one entry per artifact); ``evidence_state`` is the\nROUND SUMMARY read off the best strand, and a validator below rejects the\npair when they disagree.\nAn audit of 19 finished runs found the narrow-salvage move taken ~20\ntimes after a weak or null result and the widen move taken zero times,\nwith nothing in the output recording which move had been made, so the\nbias was invisible in the run record as well as unconstrained in the\nprompt. These fields make the decision explicit and checkable;\n``relation_type`` is kept only so runs already on disk still parse.",
  "properties": {
    "title": {
      "description": "Revised hypothesis title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters); may be unchanged if still accurate.",
      "title": "Title",
      "type": "string"
    },
    "hypothesis": {
      "description": "Revised hypothesis statement \u2014 what we now believe based on evidence",
      "title": "Hypothesis",
      "type": "string"
    },
    "relation_rationale": {
      "description": "Brief rationale for the H\u2194H revision type (one short line, max 120 characters).",
      "maxLength": 120,
      "title": "Relation Rationale",
      "type": "string"
    },
    "confidence_delta": {
      "description": "How confidence changed: 'increased', 'decreased', or 'unchanged'",
      "title": "Confidence Delta",
      "type": "string"
    },
    "key_changes": {
      "description": "Bullet list of specific changes made to the hypothesis",
      "items": {
        "type": "string"
      },
      "title": "Key Changes",
      "type": "array"
    },
    "strands": {
      "description": "EVERY artifact of this iteration, classified separately \u2014 one entry per artifact, no merging and no omissions. A round that mixes one genuine positive with several nulls is the normal shape; classifying the round as a whole is how the positive gets thrown away with the nulls.",
      "items": {
        "$ref": "#/$defs/StrandEvidence"
      },
      "title": "Strands",
      "type": "array"
    },
    "evidence_state": {
      "description": "The ROUND SUMMARY, read off the BEST strand rather than judged separately: any 'genuine_positive' strand -> 'strong_survivor'; else any 'lead' strand -> 'lead'; else any 'null' strand -> 'weak_or_null'; else (every strand 'broken') -> 'experiment_broken'. A value that disagrees with `strands` is rejected.",
      "enum": [
        "strong_survivor",
        "lead",
        "weak_or_null",
        "experiment_broken"
      ],
      "title": "Evidence State",
      "type": "string"
    },
    "move": {
      "description": "The steering move for the NEXT iteration, read off evidence_state and the remaining budget: 'deepen' \u2014 hold the claim and go after the mechanism, the boundary or the confound (also the move that makes a 'lead' bigger and cleaner); 'extend' \u2014 same claim, new population/period/setting; 'widen' \u2014 return to the user's original ask and put a population of alternative candidate answers in play, screened cheaply and confirmed on held-out evidence; 'fix' \u2014 the claim is unchanged and the defective test is repaired; 'declare' \u2014 write the run up as a negative result, permitted ONLY on the final iteration or with no budget left.",
      "enum": [
        "deepen",
        "extend",
        "widen",
        "fix",
        "declare"
      ],
      "title": "Move",
      "type": "string"
    },
    "move_rationale": {
      "description": "Why this move follows from this evidence_state and the remaining budget (one short line, max 200 characters). For 'fix', name the defect.",
      "maxLength": 200,
      "title": "Move Rationale",
      "type": "string"
    },
    "coverage": {
      "description": "Does the revised hypothesis still answer the USER'S ORIGINAL ask? 'full' \u2014 it answers the ask; 'partial' \u2014 it answers a recognisable piece of it; 'lost' \u2014 the run has drifted onto a different question and the next iteration must go back.",
      "enum": [
        "full",
        "partial",
        "lost"
      ],
      "title": "Coverage",
      "type": "string"
    },
    "coverage_statement": {
      "description": "One sentence naming which part of the user's original ask the next iteration will answer.",
      "title": "Coverage Statement",
      "type": "string"
    },
    "candidates_considered": {
      "description": "How many alternative claims, mechanisms, measures or bodies of evidence you actually weighed during THIS revision. 1 when none were weighed \u2014 which, after a weak_or_null result with budget remaining, means the widen was not done.",
      "title": "Candidates Considered",
      "type": "integer"
    },
    "relation_type": {
      "default": "evolution",
      "description": "LEGACY, kept for backward compatibility with runs already on disk \u2014 'move' is the field that steers the run. Moulines's structuralist typology of this revision: 'evolution' \u2014 refining specialised claims while keeping the same conceptual frame; 'embedding' \u2014 the previous hypothesis is now a special case of a broader frame; 'replacement' \u2014 rejecting the previous frame entirely.",
      "enum": [
        "evolution",
        "embedding",
        "replacement"
      ],
      "title": "Relation Type",
      "type": "string"
    },
    "artifact_relations": {
      "description": "Typed A\u2194A edges for this iteration's new artifacts. Emit one entry per (predecessor \u2192 dependent) edge for every in_dependency on each artifact produced this iteration.",
      "items": {
        "$ref": "#/$defs/ArtifactRelation"
      },
      "title": "Artifact Relations",
      "type": "array"
    }
  },
  "required": [
    "title",
    "hypothesis",
    "relation_rationale",
    "confidence_delta",
    "key_changes",
    "evidence_state",
    "move",
    "move_rationale",
    "coverage",
    "coverage_statement",
    "candidates_considered"
  ],
  "title": "RevisedHypothesis",
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

### [2] SYSTEM-USER prompt · 2026-09-24 22:18:09 UTC

```
Your response above was stopped by a safety classifier — this is not a tool or API error. The rest of it was withheld, and tool calls in it that had not finished did not run. Do not produce that content again, even reworded.
```

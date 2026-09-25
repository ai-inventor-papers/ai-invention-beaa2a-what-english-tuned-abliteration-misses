# review_report — test_idea

> Phase: `invention_loop` · round 3 · `review_report`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `review_report` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-24 15:19:07 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: An adversarial paper reviewer (Step 3.5: REVIEW_REPORT in the invention loop)

You received a paper draft written by a DIFFERENT model. Review it with fresh eyes.
Provide constructive but rigorous critique that will improve the next iteration.

Specific critiques → better paper. Vague praise → no improvement.
</your_role>
</ai_inventor_context>

ROLE: You are a very experienced and critical researcher auditing a colleague's research
record. Your expertise spans the domain of the work under review, and you have reviewed for
top-tier venues in it — but that is not what you are doing here.

WHAT YOU ARE REVIEWING: the run's INTERNAL RESEARCH REPORT, not a paper. It is a lab
notebook written up: chronological, one section per iteration, complete. Its job is to
preserve everything the run did and concluded, including the parts that failed. A separate
step writes the publishable paper at the end, out of this report, and it can draw only on
what it finds here.

TASK: Audit the record. Is every result that exists written down, in full? Can each number
be traced to the artifact that produced it? Does the report say what was learned, what was
ruled out, and why the run moved where it did?

FIGURES: The report contains figure specifications with captions and descriptions but the
actual images have not been generated yet. Assume each figure shows exactly what its
caption describes — do not penalize for missing images.

ARTIFACTS: The report references code artifacts via [ARTIFACT:id] markers. The correct
URLs to the artifact folders will be added later — do not penalize for missing links.

GOAL: Your review feeds back to the report's author and steers the next iteration. Spend it
on what would most improve the RECORD: a missing experiment write-up, a table left out, a
number nobody can trace, reasoning that was never written down, a dead end that vanished.
Do not spend it on presentation, framing or novelty — those belong to a document that has
not been written yet.

STRENGTHS AND WEAKNESSES: Provide a thorough assessment touching on each of these:
(a) Completeness: Is every experiment the run executed written up, with its tables in
    full? A result that exists in an artifact workspace and not in the report is the
    defect this review exists to catch. Are dead ends recorded as dead ends rather than
    quietly dropped?
(b) Traceability: Can each number, table and claim be followed back to the artifact that
    produced it — an [ARTIFACT:id] marker, a named output file, a workspace path? Could a
    reader re-run what is described and get the same thing?
(c) What was learned: Does the report say what the evidence now supports, what it rules
    out, and why the run changed course when it did? Is the reasoning behind each
    iteration recorded, or only its outcome?
(d) Honesty: Are the limits of the evidence stated plainly, without selling? Does any claim
    outrun what actually ran?

SUPPLEMENTARY SCORES: Rate each on a 1-4 scale.
Soundness (1-4) — soundness of the technical claims and of the experimental methodology as the
report describes it, and whether every claim is supported by evidence that ran:
  4: excellent  3: good  2: fair  1: poor
Presentation (1-4) — quality of writing, clarity, and contextualization relative to prior work:
  4: excellent  3: good  2: fair  1: poor
Contribution (1-4) — how much of the run this report actually preserves: every experiment and table
recorded, every step's reasoning captured, every dead end kept with its evidence:
  4: excellent  3: good  2: fair  1: poor

OVERALL SCORE (1-10):
  10 — Award quality: Technically flawless with groundbreaking impact on one or more
       areas of the field, with exceptionally strong evaluation, reproducibility,
       and resources, and no unaddressed concerns.
   9 — Very Strong Accept: Technically flawless with groundbreaking impact on at least
       one area and excellent impact on multiple areas, with flawless evaluation,
       resources, and reproducibility, and no unaddressed concerns.
   8 — Strong Accept: Technically strong with novel ideas, excellent impact on at least
       one area or high-to-excellent impact on multiple areas, with excellent evaluation,
       resources, and reproducibility, and no unaddressed concerns.
   7 — Accept: Technically solid, with high impact on at least one sub-area or
       moderate-to-high impact on more than one area, with good-to-excellent evaluation,
       resources, reproducibility, and no unaddressed concerns.
   6 — Weak Accept: Technically solid, moderate-to-high impact, with no major concerns
       with respect to evaluation, resources, reproducibility.
   5 — Borderline Accept: Technically solid where reasons to accept outweigh reasons to
       reject, e.g., limited evaluation. Use sparingly.
   4 — Borderline Reject: Technically solid where reasons to reject, e.g., limited
       evaluation, outweigh reasons to accept. Use sparingly.
   3 — Reject: For instance, technical flaws, weak evaluation, inadequate reproducibility.
   2 — Strong Reject: For instance, major technical flaws, poor evaluation, limited
       impact, poor reproducibility.
   1 — Very Strong Reject: For instance, trivial results or unaddressed concerns.

CONFIDENCE (1-5):
  5: Absolutely certain. Very familiar with related work, checked details carefully.
  4: Confident but not absolutely certain. Unlikely you misunderstood something.
  3: Fairly confident. Possible you missed some related work or details.
  2: Willing to defend your assessment, but quite likely missed central aspects.
  1: Educated guess. Not in your area or difficult to evaluate.

For each dimension, provide a list of specific improvements:
- WHAT needs to change
- HOW to change it (concrete enough for the author to act on immediately)
- EXPECTED SCORE IMPACT: how much would fixing this raise the overall score?

REVIEW PRINCIPLES:
- Be specific and actionable — vague critique is useless
- Ground your review in evidence — search for existing work, accepted papers, known results
- Rank critiques by score impact — address the biggest score blockers first
- Distinguish major issues (the record is incomplete or untraceable) from minor issues (polish)
- Acknowledge genuine strengths — don't be negative for its own sake
- Compare against the bar set by accepted papers at top-tier venues
- Check COMPLETENESS artifact by artifact. Walk the supplementary materials and, for each executed artifact, find where the report reports it. An artifact whose results are absent, or summarised without its table, is a major issue: the paper step writes from this report alone and cannot publish what is not here
- Check every TABLE is present with its actual numbers. Open the output files and compare. Prose like "performance improved" standing in for a table that exists on disk is a major issue
- Check TRACEABILITY: each number, table and claim carries an [ARTIFACT:id] marker or names the output file it came from. An untraceable number is a major issue even when it is correct
- Check the REASONING is recorded, not just the outcomes: why each strategy, why these artifacts, what the previous review objected to, what the hypothesis update concluded and why it moved. A section that reports results with no account of why they were sought is incomplete
- Check DEAD ENDS are kept and labelled, with the evidence that killed them. A direction the run abandoned and the report does not mention is a major issue: it makes the run look luckier than it was, and the paper step will never know the alternative was tried
- Check the CHRONOLOGY holds: one section per iteration, in order, and the earlier sections unchanged except where a correction is marked in place. An earlier section silently rewritten destroys the record and is a major issue
- Check that every headline number came out of an artifact that ACTUALLY RAN, and RECOMPUTE it yourself from that artifact's own tables or result files — do not accept the report's figure on its word. A mismatch between what you recompute and what the report states is a finding in its own right. Where an artifact does not let you recompute a number, say so and score that claim unverified rather than accepted. A projected, expected, illustrative or placeholder number presented as a result is the most serious defect this report can have — set results_reported false and blocking true
- When the report claims a POSITIVE, non-obvious result, name the nearest published result that already answers something close to it and state what this iteration adds beyond that neighbour. This checks whether the FINDING has earned its claim, not how the paper will be framed against the literature: a positive result gets no credit for novelty in this record until that comparison is made, and its absence is a critique under 'novelty'
- Check for an iteration that added METRICS rather than SAMPLES to an already underpowered panel. When a power analysis or the effect sizes on record show the artifact panel cannot detect the effect being chased, more candidate metrics or readouts over the same panel do not fix that — flag it as a major issue and say the budget belonged on more graded samples or checkpoints instead
- Check COVERAGE against the user's ORIGINAL request, not against the report's own framing. Name the part of the request the run has not addressed yet
- Check that claims are PROPORTIONATE to the evidence. A small, expected-direction effect written up as the answer is the failure mode to name explicitly
- Do NOT review this as a paper. Section order, narrative arc, abstract framing, figure count and writing polish are the later paper step's concerns, and a critique about them spends the run's iteration budget on the wrong document. The nearest-neighbour check above is different: it asks whether the record has earned its positive claim, not how the paper will be sold against the literature. Bookkeeping — run ids, timestamps, spend, review scores, file hashes — BELONGS in this report; never ask for its removal

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape. Two modes: general (default, broad web) and scholarly (peer-reviewed papers + citations) — pass mode=scholarly for prior-art, related-work, and citation lookups.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/review_report/review_report`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/review_report/review_report/`:
GOOD: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/review_report/review_report/file.py`, `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/review_report/review_report/results/out.json`
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

<role>
You are a very experienced and critical conference reviewer specialized in the domain of the work under review.
You have reviewed for top-tier venues in the relevant field. Your reviews are known for
being thorough, fair, and grounded in the actual state of the field.
</role>

<report>
# What English-tuned abliteration misses in Slovene

## Framing

Abliteration removes refusal behaviour from language models by orthogonalising weight matrices against a "refusal direction" extracted from English harmful-vs-harmless contrasts [1]. The procedure was introduced by Arditi et al. [1] and automated by tools such as Heretic, which uses TPE search over layer, position, direction index, and LoRA rank to find abliteration configurations that minimise an English refusal objective while bounding KL divergence from the original model. The question motivating this study is whether that English-centred objective leaves Slovene refusal behaviour uncontrolled. If the English refusal direction is universal across languages, as Wang et al. [2] report for safety-aligned models evaluated across 14 languages, then abliteration tuned on English should transfer to Slovene. If instead Slovene refusal relies partly on representations that the English objective does not observe, a gap will remain. The practical consequence is that a model abliterated to comply in English might still refuse in Slovene, or might lose Slovene capabilities that the English-only KL constraint does not protect.

Several concurrent lines of work inform this question. BabelSteering [4] and Yoon et al. [5] show that safety alignment imposes disparate costs across languages, with non-English users bearing higher utility loss. Aziz et al. [6] diagnose the breakdown point for low-resource safety as an action failure rather than a representation failure: the model encodes harmfulness correctly but fails to convert the representation into refusal. Wu et al. [7] formalise this as a disentangled safety hypothesis, separating a recognition axis from an execution axis. On the abliteration side, Fafula [8] documents off-target effects of refusal removal across model families, and Young [14] and Petrov [15] compare abliteration methods across architectures. Upadhyaya and Sikdar [9] analyse how safety and language identity become entangled, while Hawkins et al. [10] show that benign multilingual fine-tuning has heterogeneous safety impacts. Labunets [11] demonstrates that refusal geometry reflects refusal training diversity. On quantisation effects relevant to our NF4 setup, Marchisio et al. [12] and Chimoto et al. [13] show that quantisation calibration language matters for multilingual performance. Tang et al. [16] identify language-specific neurons, and Ghussin et al. [17] propose principled layer selection for multilingual steering. Frank [18] argues that refusal-based alignment evaluation conflates detection with routing.

We study this question in a controlled bilingual setting using two sibling 12B models from the Gemma-3 family: google/gemma-3-12b-it (the English-centric reference) and cjvt/GaMS3-12B-Instruct (a Slovene continual-pretraining and SFT variant of the same architecture). Both are loaded in bnb_4bit NF4 quantisation throughout. The study proceeds in three iterations. Iteration 1 runs matched Heretic abliteration on both models, screens for cross-language refusal-direction transfer, and builds the shared bilingual evaluation dataset. Iteration 2 uses that dataset to measure the surrogacy gap (what English outcomes fail to predict about Slovene), test causal mechanisms, and evaluate safety and utility on held-out benchmarks. Iteration 3 tests the depth-coverage hypothesis, corrects Heretic's keyword objective, and extends the depth-redundancy index to additional models and languages.

[FIGURE:fig_behaviour_summary]



## Iteration 1

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



## Iteration 2

Iteration 2 built on the screen results from iteration 1 by running five pre-registered experiments that measured the surrogacy gap, tested causal mechanisms, and evaluated safety and utility on held-out data.

### Experiment 5: Utility and mechanism [ARTIFACT:art_a4VkEvYRquBO]

**Goal.** Evaluate whether the selected abliteration edits preserve utility across both languages and characterise the internal geometry of the harm representation before and after editing.

#### T1: Harmful behaviour (S4 harmful items, 257 per cell)

The table below shows judged refusal rates on held-out harmful items (S4, 257 items per model × checkpoint × language). The gpt-4.1 judge labelled a random ~52% subsample; remaining items used a second-family free judge (Nemotron-3-ultra-550b); markers show the Heretic keyword rule on all 257.

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

For GaMS3, the frozen probe collapsed after editing: AUROC dropped to 0.201 at the worst layer, but a refit probe recovered to 0.993. The edit moved the harm signal away from its original subspace (INFO-LOSS on dim, DRIFT on logistic), but the information persisted in a different location.

For Gemma, the frozen probe was preserved: AUROC dropped by at most 0.002. The edit did not move the harm representation.

The contrast is informative. GaMS3's edit reached low refusal in both languages by destroying the harm signal at the probe layer. Gemma's edit left the harm signal intact, consistent with its failure to suppress Slovene refusal: the model still encodes harmfulness, but the readout mechanism was partially disrupted for English while the Slovene readout remained functional.

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

For GaMS3, scaling the LoRA edit by f = 0.5 brought both languages to 68 to 75% refusal; at f = 1.0 both reached 0%. EN and SL refusal declined in parallel. For Gemma, at f = 1.0 (the core edit) EN refusal was 27% while SL was 92%. Reaching SL refusal below 10% required f = 3.0, at which point KL divergence rose to 0.82 (SL), well above Heretic's operational range. This dose-response confirms that the EN-SL gap in Gemma is not an artifact of edit strength: at every dose level, SL refusal exceeded EN refusal.

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

**Gap table:**

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

**Stability checks.** Gap estimates were stable across alternative learners, inclusion of collapsed edits, reverse-direction analysis (SL → EN), and MT-stable subsets.



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

**Weight edit repair.** The experiment also tested whether augmenting the core Heretic weight edit with additional directions could repair the Slovene gap:

| Arm | SL harmful | EN harmful | FLORES ΔNLL SL |
|---|---|---|---|
| W0 core Heretic edit | 0.89 | 0.39 | -0.005 |
| W1 core + r_prior weight edit | 0.76 | 0.23 | 0.009 |
| W3 core + layer-matched d_EN(h) | 0.11 | 0.29 | 0.546 |
| W4 core + random weight edit | 0.47 | 0.70 | 0.064 |

The r_prior weight edit (W1) reduced SL refusal from 0.89 to 0.76 while also reducing EN refusal to 0.23, but the SL residual remained high. The layer-matched weight edit (W3) reached 0.11 SL refusal but at severe NLL cost (+0.55). The random weight edit (W4) reduced SL refusal to 0.47 while raising EN refusal to 0.70, suggesting it disrupted the model rather than targeting Slovene refusal.

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

Iteration 3 therefore ran four experiments and one evaluation audit, each attacking the reviewer's objections from a different angle.

### Experiment 9: Gemma coverage × strength factorial [ARTIFACT:art_ex4hbgThhJaL]

**Goal.** Test whether depth coverage or total edit energy governs how much Slovene refusal survives, by building weight edits that cross coverage with strength at matched total removal energy.

**Setup.** Weight edits were constructed using Heretic's operator path (orthogonalize_direction=true, row_normalization='full', rank-3 LoRA, per-layer d_EN(h) from experiment 8 directions) on google/gemma-3-12b-it, crossing 10 coverage sets with 4 to 5 per-layer strength levels. Coverage sets included four contiguous 12-layer bands (B1: 1-12, B2: 13-24, B3: 25-36, B4: 37-48), two cumulative sets (C24: 1-24, C36: 1-36), a full-depth set (ALL48), stride-2 (S2) and stride-4 (S4) sets, and the support of the iteration-1 Heretic kernel (K96). Strength was controlled by a per-layer projection coefficient c in {0.25, 0.50, 1.00, 1.50}, with total removal energy E computed analytically for every cell before running. The panel comprised 122 cells scored on 27,784 generations by a local Qwen3-14B judge with the frozen experiment-4 rubric, certified at kappa 0.87 vs gpt-4.1 within edited checkpoints.

PARTIAL counts as compliance throughout. INVALID is excluded from denominators.

**Part A: DEV depth-redundancy index.** Cumulative-prefix directional ablation (activation-only) on S3 half-A (44 harmful items per language) gave:

| Family | Lang | index_L |
|---|---|---|
| prefix | EN | 16 [16, 20] |
| prefix | SL | 20 [20, 28] |
| suffix | EN | 24 [24, 24] |
| suffix | SL | 24 [24, 28] |

The English index (the minimal layer count whose ablation brings refusal below 0.5) is 16; the Slovene index is 20. Slovene needs at least one more 4-layer step of coverage than English. The leave-one-band-out necessity profile shows the 25-36 band is most necessary for Slovene (LOBO necessity +0.39) but not for English (+0.00), indicating Slovene refusal is written more deeply.

[FIGURE:fig_redundancy_index]

**Part P2: Matched-energy groups.** Four groups, each containing a narrow-and-strong and a broad-and-weak cell within the same total removal energy:

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

[FIGURE:fig_band_analysis]



### Experiment 10: GaMS3 coverage test [ARTIFACT:art_xLy2vVlI7OEL]

**Goal.** Run the identical coverage × strength factorial and DEV index on GaMS3, the checkpoint whose English-derived edit transferred, to test whether index_SL ≈ index_EN there.

**DEV index:** EN = 16 [16, 16], SL = 20 [16, 24]. The Slovene index is one grid step above English, with overlapping CIs. In both models the English index is shallower; the SL lag is common to both checkpoints.

**Weight-edit panel (57 cells).** The matched-energy groups gave:

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



### Experiment 11: Corrected objective [ARTIFACT:art_0XmNBGkzsJc_]

**Goal.** Test whether replacing Heretic's English keyword refusal counter with a partial-aware score, at equal budget/seed/data/quantisation, makes the search select a kernel that closes the Slovene-English gap.

**Setup.** A refusal classifier was distilled from existing gpt-4.1 and Qwen3-14B labels (thousands on disk from experiments 4, 5, and 8), using char/word n-gram features, response length, marker hits, and first-64-token embeddings. It was certified at kappa 0.924 (refused-vs-not, within edited checkpoints) against the Qwen3-14B judge. The corrected Heretic run used the same seed (20260923), same 116-trial budget, same NF4 precision, and the same selection rule (lowest KL among trials with ≤ 10 refusals); only the refusal scorer changed.

**Selection outcomes.** Under the corrected scorer, the primary selection rule fired (not the fallback), selecting trial 7 with 5/100 refusals at KL 0.258. Under the keyword scorer on the same 116 trials, the fallback rule fired, selecting trial 96 with 69/100 keyword-refusals at KL 0.024. The keyword counter fails because it sees 72/100 keyword-refusals on trial 107 (which the judge rates at 10/100 actual refusals) and cannot select it.

Post-hoc reselection (rescoring the original 116 trials with the corrected scorer and re-applying the selection rule) selected trial 98 (classifier) or trial 64 (judge), both with ≤ 10 refusals.

**Coverage.** The corrected trial 7 has sum_A1 (aligned coverage) = 64.0, versus trial 96's 26.0. The corrected objective bought broader coverage, as predicted by the depth-placement hypothesis.

**Headline results (S5X, 100 verified translation pairs):**

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

The corrected objective halved the gap (from +0.68 to +0.38) but did not reach the +0.35 target. The falsifier complicates the causal story: dose-scaling the keyword edit to the same EN refusal level achieves comparable gap reduction, suggesting the coverage gain is partly a side-effect of stronger editing rather than purely better objective design. However, the corrected objective produced this result at KL 0.258, while the dose-1.5 arm needed a gentler KL of 0.073 to get there. The FLORES cost was minimal in both cases (dNLL ≤ 0.005).



### Experiment 12: Predictive test across models and languages [ARTIFACT:art_kfCCWf7o8eJ9]

**Goal.** Test whether the depth-redundancy index, measured on development data, predicts out of sample how much of an English-derived weight edit transfers to each unmonitored language across multiple model families.

**Setup.** Three models: google/gemma-3-12b-it (anchor), Qwen/Qwen3-8B (qwen3), mistralai/Mistral-7B-Instruct-v0.3 (mistral). Four languages: English, Slovene, German, Lithuanian. Per-layer d_EN(h) directions extracted by diff-in-means on DEV items. DEV index measured at cumulative prefixes (10%, 25%, 50%, 75%, 100% of depth). Eligibility gate: no-op refusal ≥ 0.60 AND INVALID ≤ 0.20.

**DEV indices:**

| Model | EN | SL | DE | LT |
|---|---|---|---|---|
| gemma | 0.5 | 0.75 | 0.5 | 0.75 |
| qwen3 | 0.75 | 0.75 | 0.75 | 0.5 |
| mistral | 0.1 | 0.25 | 0.1 | 0.1 |

Mistral failed the eligibility gate in all languages (no-op refusal 0.07 to 0.53); all four mistral rows and qwen3-LT were excluded. Eight eligible rows remained.

**Weight panel (5 cells per model × language, held-out StrongREJECT items).** The Gemma trial-96 adapter applied to gemma showed residual refusal EN 0.60, DE 0.53, LT 0.75, SL 0.92 (exposure to the Slovene residual that motivated the study). For qwen3, the W3 (high-dose) arm brought EN to 0.37 and SL to 0.32, with the gap much smaller than Gemma's.

**Frozen predictions: VERDICT FALSIFY.**
- **P1** Spearman(index, residual) = -0.009 [-0.131, 0.192] over 21 rows. The index does not predict the cross-model, cross-language residual. Pass = False.
- **P2** concordance 8/12 decided (0.67); binomial p = 0.19. Pass = False.
- **P4** index vs baselines: single-site transfer rho +0.732 beats the index by -0.741. The simple single-site ablation rate predicts better than the frozen index.

The depth-redundancy index, as defined and measured here, does not generalise beyond the two Gemma-3 siblings. It is a two-checkpoint observation, not a predictive instrument.

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

**Dead-end ledger.** Twenty items, each with its closing number:

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

**Novelty positioning.** Wang et al. [2] established direction universality across 14 languages using all-layer activation ablation; Slovene and Gemma-3-12B were not among their models or languages. Arditi et al. [1] showed refusal is mediated by a single direction ablated at all components. This study adds: (a) the English direction does clear Slovene when applied at every depth (consistent with both), but (b) the site-limited Heretic weight edit leaves a gap whose size is judge- and definition-dependent (strict +0.06 to +0.69), and (c) the gap is governed by WHERE the edit energy sits (band 13-24 density, Spearman -0.942) rather than by how many layers are covered.

**Pending human review.** Five packets totalling 640 items are ready for native-speaker labelling. No native-speaker review has been conducted anywhere in this study; all judges are automated.



## What we have learned so far

[FIGURE:fig_refusal_gap]

Three iterations have converged on a picture with one firm positive, one partial positive, and three falsified predictions.

**Firm positive: band placement governs residual refusal.** At matched total removal energy, which 12-layer band carries the energy predicts how much Slovene refusal survives. The band-density Spearman is -0.942 (exp9, placebo-verified, p = 0.004): coverage sets including layers 13-24 reach SL < 0.20 at sufficient strength; those missing it never reach SL < 0.93. This holds for both Gemma and GaMS3: in GaMS3 the nested R2 of placement (0.718) far exceeds count (0.400) (exp10). At matched energy AND matched layer count, a contiguous B2 band (layers 13-24) removes up to 0.57 more Slovene refusal than a stride-4 pattern at the same energy (exp10). The relevant factor is not how many layers the edit touches, but where the energy sits.

**Partial positive: corrected objective halves the gap.** Replacing Heretic's keyword refusal counter with a partial-aware classifier, at equal budget/seed/data, moved the S5X strict gap from +0.68 to +0.38 (exp11). The corrected selection bought broader aligned coverage (A1 = 64.0 vs 26.0). However, the P7 falsifier fired: dose-scaling the keyword edit to the same English refusal level achieved comparable gap reduction (+0.33), meaning the improvement may be "more edit" rather than "better objective." The gap did not reach the pre-registered +0.35 target (observed +0.38, CI [0.29, 0.47]).

**Falsified: depth-coverage count does not explain the residual.** The coverage regression (exp9 P1, dR2 = 0.040) and the matched-energy broad-vs-narrow comparison (exp9 P2, pooled +0.05) both failed their confirmatory thresholds. Coverage as a simple layer count does not add meaningful predictive power over total energy and band placement. The depth-coverage hypothesis as originally stated (more layers = less residual) is falsified; the replacement finding is that band identity matters more than coverage extent.

**Falsified: matched-energy narrow beats broad in GaMS3.** Experiment 10's PB2 was FALSIFIED OPPOSITE: at matched energy, narrow-and-strong cells (B2, B3) left less GaMS3 Slovene refusal than broad-and-weak cells (STR2, STR4), the reverse of the prediction. This makes sense once band identity is the driver: B2 (layers 13-24) concentrates energy in the right band, while a stride pattern dilutes it.

**Falsified: the depth-redundancy index does not generalise.** Experiment 12 found Spearman -0.009 between the frozen index and the cross-model, cross-language residual. The single-site transfer rate (rho +0.732) was a far better predictor. The index is a two-checkpoint observation, not an instrument.

**What survives from iterations 1-2.** The behavioural dissociation (GaMS3 transferred, Gemma did not) is robust across judges and datasets. The surrogacy gap on refusal is small for GaMS3 (0.015) and attenuated but predictable for Gemma (0.054). The harm representation is shared across languages (AUROC > 0.995); the behavioural gap is an action failure, not a representation failure, consistent with Aziz et al. [6]. KL divergence has a blind surrogacy gap in both models (0.147, 0.079). Utility is preserved in all cells. The keyword proxy inverts on edited checkpoints (kappa -0.04 on Gemma edit EN).

**The headline gap stated as a range.** The Gemma edit S5X paired EN-SL gap ranges from +0.06 (keyword strict) to +0.69 (Qwen3-14B strict), with the broad definition at +0.23. On GaMS3, all judges agree the gap is near zero. The PARTIAL class (0.548 of Gemma edit EN outputs) is the wedge: the keyword counter treats partial compliance as refusal, closing the measured gap; the LLM judge treats it as compliance, opening the gap. Neither reading is wrong; they measure different constructs.



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

</report>

<supplementary_materials>
The run's code, data, and experimental artifacts. This is your ground truth: the report is
complete only if everything here that ran is written up in it, tables and all. Read them —
check that the code matches the described methodology, that each reported number appears in
an output file, and that no executed artifact is missing from the report.

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
</supplementary_materials>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for judging whether the evidence recorded here actually supports what the run concluded, and whether a direction it abandoned was abandoned for a good reason.

- **aii-handbook-auto-computational-linguistics** — Field handbook for computational linguistics as a SCIENCE of language — grammaticality and minimal pairs (BLiMP), surprisal versus reading times, linguistic structure in LMs, annotator disagreement an
- **aii-handbook-auto-mechanistic-interpretability** — Field handbook for mechanistic interpretability of neural networks — circuit discovery, activation and attribution patching, sparse autoencoders, transcoders, attribution graphs, steering vectors, pro
- **aii-handbook-auto-multi-agent-llm-systems** — Field handbook for multi-agent LLM systems (MAS) — orchestration topology, multi-agent debate, mixture-of-agents, verifier and critic agents, inter-agent protocols (MCP/A2A), failure attribution and s
- **aii-handbook-auto-neurosymbolic** — Field handbook for neuro-symbolic AI — text-to-logic autoformalization (NL to FOL), LLM-plus-solver and prover pipelines (Prolog, ASP, SMT), probabilistic-differentiable NeSy (DeepProbLog, Scallop), r
</available_domain_handbooks>

<previous_review>
Your review from the previous iteration. Check which critiques the newest section
addressed. Do NOT re-raise critiques that have been adequately fixed. Only re-raise if the
fix is insufficient.

The previous review is BLOCKING: the paper must not ship as it stands. Every MUST-FIX item below is a requirement for this iteration, not a suggestion — an iteration that leaves one unaddressed does not publish.

- [MAJOR MUST-FIX] (evidence) The iteration-1 six-checkpoint table (Experiment 1) contains numbers no artifact produced, and one row reverses a finding. Recomputed from iter_1/gen_art/gen_art_experiment_1/results/eval/*.json and method_out.json -> behaviour_table: Gemma original SL = 97 (report 100); Gemma own edit SL = 90 (report 85); Gemma + GaMS3 trial-88 parameters = EN 53 / SL 25 at KL 0.254 (report 91/95 at KL 0.293). Gemma FLORES NLL = 4.018/3.702 (orig), 4.012/3.703 (own), 4.011/3.712 (swap), versus the report's 3.930/3.427, 3.929/3.432, 3.944/3.455; I found those values in no output file. The prose then concludes that 'Gemma under GaMS3's edit showed 91/95 ... far from own-edit performance'. The artifact shows the opposite: GaMS3's parameters suppress Gemma's SLOVENE refusal far more than English (97->25 vs 100->53; McNemar p < 1e-19 SL, 0.020 EN), at 10x the KL. This bears directly on the run's central question, because a stronger Heretic edit on Gemma removes Slovene refusal easily. Also: '13.4x [6.9, 30.4]' is called a 'ratio of median refusal counts', but it is the ratio of medians of refusal-drop per unit KL (1449 vs 108).
  Action: Replace the table with metadata.behaviour_table values, add the swap statistics table (own-vs-swap EN/SL differences, McNemar p, KL ratio 0.095 [0.046, 0.189]), and restore the correct swap conclusion. Relabel 13.4x as 'refusal drop per unit KL, ratio of medians', and add the KL-matched subset (GaMS3 65/100 vs Gemma 99/100 at KL medians 0.0101/0.0098).
- [MAJOR MUST-FIX] (rigor) The iteration-1 section was silently rewritten, and the chronology is broken. The iteration-1 report (iter_1/gen_report_text/.../paper_text) had the correct Gemma rows, the A3 reading 'intermediate', the correct marker-validation provenance (40 executor hand labels, LLM judge blocked 0/600), the judged A1 2x2 table, the margin explanation, the GaMS3 double dissociation, the Heretic bridge, a Strategy section, a 'Dead ends' section (Slovene LLM judge blocked; priority-3 sensitivity arms cut) and 'What we have learned so far'. The current iteration-1 section has none of this, adds errors (A3 = 'shared via strength only'; 'kappa 0.48 ... LLM-judge labels'; A1 judged 'with Qwen3-14B for the remainder', although judge_meta.json shows gpt-4.1 on all 1,596 and no second judge), and marks none of the changes.
  Action: Restore the iteration-1 section verbatim from the iteration-1 report. Where a correction is genuinely needed, insert it in place as a dated '[Correction, iter 2]' note, never as a silent edit.
- [MAJOR MUST-FIX] (evidence) The Gemma surrogacy panel (Experiment 7) inverts its pre-registered predictions. protocol/frozen_predictions.json defines P-a as 'Gap_R >= 0.10 with 95% LB > 0', i.e. that English is a BAD surrogate for Gemma's Slovene refusal. It was NOT CONFIRMED because Gap_R1 = 0.054 is small. The report restates P-a as 'Gap_R is small, <= 0.05' and says it failed because the gap 'exceeded' 0.05, which is the opposite meaning. The report then calls Gemma's refusal gap 'larger than GaMS3's (0.054 vs 0.015 for R1)', but 0.015 is GaMS3's R gap; GaMS3's R1 gap is 0.042 [0.027, 0.070], which overlaps. rederive.json also shows the observed raw Gap_R1 inside the per-edit label-swap placebo range (15.5% of swaps as large). The correct finding, which the report never states, is 'attenuated but predictable': SL moves about 0.44x as much as EN (R1 slope 0.436; R_seq 0.220), yet EN_A predicts SL_B at R2 0.94 vs 0.99.
  Action: Rewrite the Experiment 7 verdict block from verdicts.json with the frozen wording. Report R1-vs-R1 across models and the placebo range. Rewrite the summary's Gemma paragraph around 'attenuation, not blindness'.
- [MAJOR MUST-FIX] (evidence) The mechanism conclusions contradict their own tables. (i) The report says GaMS3's edit 'destroyed the harm signal at the representation level'. T6 and T7 show refit AUROC 0.993/0.987 at the worst layer and AUROC with the frozen axis projected out of 0.985/0.955; the artifact's own reading is 're-encoding, not information loss'. (ii) T9 says EVIDENCE_LOSS means 'the internal signal weakened rather than the threshold shifting'. exp5 defines the label as decoupling of refusal from the ORIGINAL axis while information stays decodable. Gemma's pre-registered readout was JUDGE_LOGISTIC, flagged as a separation artefact, not R_seq. (iii) T11 (item-level flips) is omitted. It shows Gemma's EN flips hit low-evidence items first (AUROC s_frozen_orig 0.240 [0.11, 0.39]), a criterion-shift signature that cuts against the EVIDENCE_LOSS label. (iv) For Gemma the report says 'the edit barely moved the harm signal', but exp5 notes that frozen-axis separation halves equally in EN and SL from L28, with late-layer axis rotation cos 0.53 EN vs 0.83 SL. (v) The summary explains GaMS3's transfer by continual Slovene pretraining ('more tightly integrated'). The user forbade training-stage attribution, and T5 contradicts it: Gemma's EN/SL cosine is higher (0.919/0.979 corrected vs 0.832/0.890).
  Action: Rewrite the T6/T7/T9 interpretations from exp5 README and summary.json. Add T11 in full and the Gemma late-layer drift numbers. Remove the training-stage explanation. State explicitly that the evidence supports 'changed mapping / re-encoding' for GaMS3 and 'intact representation + attenuated SL readout' for Gemma, and that T11 favours criterion shift for Gemma EN.
- [MAJOR MUST-FIX] (methodology) Judge heterogeneity is hidden, and it controls the size of the headline effect. The Gemma core edit's EN harmful refusal is 0.70 (gpt-4.1, S4, T1), 0.287 (Qwen3-14B, RefusEU), 0.17 refused + 0.64 PARTIAL (gpt-4.1 subset, RefusEU, analysis_gpt41_subset.json), 0.386 (gpt-4.1, S4-hoc W0) and 0.70 (Qwen second judge, same W0 items). The report never mentions the partial class (0.548 on RefusEU EN), which is where the EN refusal went. In exp8 the second judge disagrees sharply on EN cells: A1 EN gpt-4.1 0.225 vs Qwen 0.667; X1 EN 0.028 vs 0.369. The report's 'Weight edit repair' table mixes gpt-4.1 rows (W0 0.89/0.39, W1) with second-judge rows (W3, W4). That produces the false statement that the random weight edit 'raised EN refusal to 0.70'; under the same judge W0 EN is also 0.70. It also hides that W4 (random) cuts SL from 0.93 to 0.47, which halves the apparent specificity of W3 (0.11). T12 uses the marker rule, which the same artifact shows undercounts Gemma EN refusal (32.7% vs 70.3%), so the EN-SL dose-response gap is inflated.
  Action: Add a judge-sensitivity table for every Gemma edit cell: refused/partial/complied under each available judge, with n and κ restricted to edited checkpoints. Re-split the repair table by judge, and add W2 and the per-judge W0 baseline. Label T12 as marker-based, add its R_seq>0 columns (at f=3 Gemma SL 7.0% < EN 12.8%), and drop 'at every dose SL exceeded EN'. State the EN-SL gap as a range across judges.
- [MAJOR MUST-FIX] (evidence) Most of the A1 screen (Experiment 3, art_jxrJNc9o4QSp) is missing, and what remains is misstated. The report says 'no reliable conclusion' for GaMS3, but the frozen rule F6 switched GaMS3 to judged outcomes, which exist: EN 0.90->0.46, SL 0.93->0.34, gap -0.15 [-0.32, 0.03]. For Gemma, EN goes 0.83->0.07, not '99%'. Missing entirely: the judged 2x2 table, which shows Gemma SL refusal survives even its OWN Slovene direction (d_SL ablation SL 0.93) and bears directly on 'missing direction' vs 'margin'. Also missing: the margin decomposition (Gemma SL R 13.9 vs EN 3.6; 69% of benign SL twins refused). The Heretic bridge is missing; it shows an SL-EN residual gap for GaMS3 too (0.11 [0.06, 0.17]), which contradicts 'GaMS3 near-complete transfer'. Also missing: the u_SL increment (collateral-confounded, F8), the GaMS3 double dissociation under addition, the T7 failure (raw-energy random ablations are destructive), and cos-vs-transfer (Spearman 0.39/0.58). The matched-efficacy and dose-response paragraphs give no numbers.
  Action: Insert the README headline table and the screen_verdict.json fields (I/F/rho with CIs), the transfer matrix, the Heretic-bridge means, the margin decomposition file and the T7 lesson, with file paths. Replace the numberless matched-efficacy and dose prose with numbers from analysis_summary.json per_model.matched_efficacy and addition.
- [MAJOR MUST-FIX] (scope) Required C1 outputs are missing (Experiment 4, art_m6pglf516e2r). The user asked for harmful compliance/ASR, refusal and language consistency reported separately, and for explicit handling of ambiguous outputs. The report gives only refusal and over-refusal. Missing: the official-guard ASR (Gemma edit EN 0.738 vs SL 0.103, a 7x gap larger than the refusal gap; GaMS3 edit 0.982/0.972; community 1.000/0.870). Missing: the partial class (Gemma edit EN 0.548), GlotLID language consistency per cell, truncation rates (GaMS3 0.30->0.93), and the S5X per-checkpoint gap table with McNemar p. Missing: the keyword-proxy miscalibration table (Gemma edit EN keyword 0.851 vs judged 0.255; 76% false positives; κ -0.04), which is the artifact's proposed mechanism for why Heretic under-optimised Gemma. Also missing: the R_seq within-edit validity collapse (0.16-0.33) and the B3 batching-certification failure. The report also says Qwen3-14B was 'tested on a calibration set before deployment'. It was a post-hoc F1 substitute after gpt-4.1 was blocked at 716/3,840, validated against those 716 labels.
  Action: Add headline_table.csv in full (all 11 columns × 10 cells), the S5X gap table, the keyword-proxy table and the R_seq negative result from README §4-5. Correct the judge provenance. Add an explicit 'Human review: PENDING' and 'Gemini second judge: NOT RUN' line for C1, exp5 and exp6.
- [MAJOR MUST-FIX] (evidence) Causal-test results (Experiment 8, art_hmbXDppkPZnR) are omitted, and several of them change the story. Missing arms: A6 (d_EN + r_prior orthogonalised to language: SL 0.62, cut 0.324 [0.176, 0.486]); A5 (d_EN + u_SL: 0.82); A8/A9 (random: 0.83/0.74; A9's cut 0.074 is the 'best random'); A11; X2 (layer-matched d_EN+d_SL: SL invalid 0.93, FLORES +13); X4 (doubling d_EN at L20: SL still 0.75, so strength at one site does not help); X3 layer-matched random (0.86) and X5 energy-matched PC (0.93); W2; C2 (community + RANDOM weight edit: SL 0.16, better than community + r_prior 0.20). The last one undercuts the report's 'modest improvement' reading of r_prior. Missing outcomes: F3 (r_prior alone lowers SL over-refusal 0.28->0.19, Holm p 0.025, below the pre-registered threshold), F6 (adding r_prior raised SL harmless refusal to 0.52), F5 not evaluable, the confound reading 'neither', and the item-level cosine-transfer AUROC 0.24. The report's T10 claim that r_prior 'is not simply the language direction' contradicts exp8 (cos 0.65 with the language axis, 0.89 with its shuffled-label twin) and T10's own pooled Gemma cos 0.621.
  Action: Paste results/report_tables.md in full, both judge variants, with the frozen-prediction block and the Holm table. Correct the r_prior-language statement. Note that the depth-localisation table uses the second judge (baseline A1 = 0.91, not 0.86), and add its A0/A1/X3/X4/X5 control rows.
- [MAJOR MUST-FIX] (evidence) The surrogacy panels (Experiments 6-7) omit the numbers that bound the positive 'KL is blind' claim and the only positive mechanistic lead. Missing: Gap_Heretic_K = 0.018 on the actual journal trials (vs 0.147 on random edits), which suggests the blind KL component barely matters for the edits Heretic actually selects. Missing: SL KL is SMALLER on average (mean-change ratio 0.59), so 'blind' does not mean 'more damage'. Missing: reverse-direction Gap_K = -0.124; the report calls the reverse analysis 'stable', but the sign flips. Missing: the exploratory source-layer carrier (Spearman 0.77 with log SL/EN KL ratio; dR2 0.047 [0.008, 0.074]). Missing: the bilingual reselection (GaMS3 keeps trial 88; Gemma: no journal trial predicted SL refusal <= 0.20, best 0.57). Missing from the Gemma panel: the lp_ref vs lp_comp slopes (0.081 vs 0.849: the edit lowers the refusal opener only in EN), the validity-edit judged table, silent failure 15/15, the global-direction vs per-layer split (+0.34 vs +0.01), and the fact that its judge was the ORIGINAL gemma-3-12b-it itself (self-judging, validated only on original generations). Edit counts: 246/203 edits (160/163 fitted) vs the iteration-2 plan of >= 250 random plus about 80 Sobol P2 edits; P2 is not mentioned.
  Action: Add these rows and tables from exp6 summary_tables.md and exp7 README/analysis.json. State the judge used for each panel's validity gate. Record that P2 was not run and why.
- [MAJOR MUST-FIX] (clarity) The reasoning and dead ends are not recorded. The iteration-1 strategy planned five directions, and two produced nothing: gen_art_experiment_2 (the MAIN exposure-carrier vs thin-margin panel) and gen_art_experiment_4 (the A2 probe pod) are empty, as the iteration-2 strategy notes. The report never says they were planned, why they did not run, or how the plan moved. The hypothesis history is absent: iteration 1's invisible-share U with Lande-G framing, the iteration-1 review's objections, iteration 2's switch to a placebo-normalised surrogacy gap, and the strategy's pivot to r_prior after the A1 screen. So are the iteration-2 success criteria (a) refusal visible in BOTH models by TOST, (b) damage blind, (c) Omega/language-subspace mechanism, and their outcomes: (a) holds for GaMS3 but fails for Gemma (90% upper bound 0.128 > 0.10), (b) holds only for GaMS3 K, (c) fails. The planned causal test ('language-orthogonalized abliteration at matched EN efficacy') and the 'English-only vs full forecast on FINAL data' were never run and are not mentioned.
  Action: Add a 'Why this iteration' paragraph at the top of each iteration: the hypothesis, the prior review's objections and the strategy choice, with file paths to iter_*/gen_hypo, review_hypo and gen_strat. Add a dead-end ledger listing every planned-but-unrun artifact and arm with its reason: time, API budget, or pod failure.
- [MAJOR MUST-FIX] (novelty) The positive claims are never set against their nearest published neighbours. (1) Gemma: an English refusal direction or edit leaves Slovene refusal intact although the EN/SL harm directions are near-parallel. The closest paper is Wang et al. 2025 (arXiv:2505.17306), who report that an English-extracted vector bypasses refusal in other safety-aligned languages with near-perfect effectiveness. The Gemma-3/Slovene result is a counterexample or boundary to that, and the report should say so, together with the confound that the core edit is under-optimised (community edit gap +0.12). (2) 'Representation intact, action differs' for Gemma is the same shape as Aziz et al. 2026 (arXiv:2606.01196, harm direction separates low-resource prompts while refusal fails to fire) and Wu et al. 2026. What is new here is the mirror case: surplus refusal survives abliteration, apparently driven by a larger SL decision margin and SL over-refusal. That needs saying. (3) 'English KL is blind to SL KL' is the abliteration analogue of Marchisio et al. 2024 (arXiv:2407.03211) for quantisation, which the iteration-2 hypothesis cites but the report does not compare against.
  Action: For each of the three claims, add one sentence naming the neighbour and one stating what this run adds and where it stops. For (1): Wang et al. did not test Slovene or Gemma-3, and here transfer fails at a single site but succeeds with all-layer ablation (X1). For (3): Gap_Heretic_K = 0.018 limits its practical scope.
- [MAJOR MUST-FIX] (evidence) The claims outrun the evidence. The report calls Gemma's gap 'the headline result of the study: an English-tuned abliteration edit left most Slovene refusal intact'. The run's own evidence says the gap is largely a property of this specific under-optimised edit. The matched NF4 116-trial search never got Gemma below 50/100 EN keyword refusals. The keyword proxy it optimised has a 76% false-positive rate on Gemma's edits. The community bf16 edit shrinks the paired gap to +0.12. GaMS3's parameters on Gemma suppress SL more than EN. The EN-SL gap ranges from about 0.2 to 0.7 depending on judge. This is n = 2 models and one optimisation seed. 'Utility was preserved' is true but close to trivial for Gemma, whose edit barely changed the model (KL1 median 0.0000 EN, because 255/257 answers begin 'Okay,').
  Action: Restate the headline as: 'Under a matched 116-trial NF4 Heretic search whose keyword objective is miscalibrated on Gemma, the selected Gemma edit under-transfers to Slovene. A stronger edit of the same base largely transfers. Transfer at a single site is margin-limited, and ablating all layers removes the SL residual.' Keep the n = 2 / one-seed caveat next to each comparison.
- [MINOR] (rigor) Traceability gaps. The community FLORES shifts (0.054/0.111) are cited under Experiment 4 but come from exp8 C0. 'Max |diff| up to 97.2' for the cross-machine repro has no units or trait named (exp6 repro_check.json, E0_049). The iteration-1 dataset section's '8 rows NLLB fallback' conflicts with the A1 screen's '22/1070', and the iteration-1 Heretic prompts were entirely NLLB-translated because the API translator declined 56/110; the report does not say which set each number describes. Native review is PENDING for five separate packets (dataset 250 rows, C1 200, exp5 packet, iter-1 SL labels), and the report mentions it once.
  Action: Put a source-file path next to each non-obvious number. Name the unit and trait for the repro diff. Add a per-set translation provenance line and a single 'Pending human review' list with packet paths.
</previous_review>

<task>
Audit this research record. It is an internal report, not a paper: chronological, one
section per iteration, complete. Judge it on completeness, traceability and what it says
was learned — never on framing, section order or polish. When it claims a positive result,
novelty is evidence, not framing: check it against the nearest published neighbour (STEP 5),
not against how well the paper will read.

STEP 1 — READ THE REPORT: Read it carefully. Note what each iteration claims it did, found
and concluded.

STEP 2 — WALK THE ARTIFACTS: Go through the supplementary materials one artifact at a time
and find where the report reports it. Open the output files. Every executed artifact must
appear, and every table in those files must be in the report with its actual numbers. List
the misses; each one is a major issue.

STEP 3 — TRACE THE NUMBERS: For each number, table and claim in the report, find the
artifact it came from, and RECOMPUTE the headline number(s) yourself from that artifact's
own tables or result files rather than taking the report's figure on trust. Report any
mismatch as a finding, even when the underlying artifact is real. Where an artifact does
not let you recompute a number — the raw output is missing, or the computation cannot be
reproduced from what is there — say so and treat that claim as unverified rather than
accepted. An [ARTIFACT:id] marker or a named output file makes a number traceable; nothing
makes it untraceable, which is a major issue even when the number is right.

STEP 4 — CHECK COVERAGE AGAINST THE ORIGINAL REQUEST: The user's original request that
started this run is supplied as a separate message in this turn. Read it and ask what it
actually asked for. Is the run answering THAT, or a question next to it? Set `coverage`
to "full", "partial" or "lost", and when it is not "full", raise a critique naming the
part of the request that went unanswered. Judge against the request, not against the
report's own framing of it — a run that narrows one defensible step per iteration ends up
answering something nobody asked, and each step looked fine on its own.

STEP 5 — CHECK THE RECORD HOLDS TOGETHER:
- Is the REASONING written down at every step — why this strategy, why these artifacts,
  what the last review objected to, what the hypothesis revision concluded and why it moved?
  Outcomes with no account of why they were sought is a major issue.
- Are DEAD ENDS kept and labelled, with the evidence that killed them? A direction the
  artifacts show was tried and the report does not mention is a major issue.
- Is the CHRONOLOGY intact — one section per iteration, in order, earlier sections
  unchanged except where a correction is marked in place? A silently rewritten earlier
  section destroys the record.
- Are the numbers from artifacts that ACTUALLY RAN? Trace each one to an executed output. A
  projected, expected, illustrative or placeholder number presented as a result means
  `results_reported` is false.
- Is what the report concludes PROPORTIONATE to what it recorded? A tiny effect, or an
  effect in the direction everyone already expected, written up as the answer is either
  explained (a bound someone needed, a belief it overturns, a mechanism only visible at
  that size) or it overreaches, and you say so.
- When the report claims a POSITIVE, non-obvious result, name the nearest published result
  that already answers something close to it, and state what this iteration adds beyond
  that neighbour. A positive result earns no credit for novelty in this record until that
  comparison is made — its absence is a critique under `novelty`, not a paper-framing note.
- Does anything the report concludes CONTRADICT its own evidence — a table, a figure, a
  log, an artifact summary? Name the contradiction.
- A conclusion that contradicts the run's own evidence scores soundness 1.
- Set `blocking` by rule: true exactly when the soundness score is 1 or lower OR
  `results_reported` is false; otherwise false.

STEP 6 — WRITE YOUR REVIEW:
For each critique:
1. Categorize: methodology, evidence, novelty, clarity, scope, or rigor
2. Rate severity: major (the record is incomplete or untraceable) or minor (polish)
3. Describe the issue clearly, naming the artifact or section it is about
4. Suggest a concrete action to address it

Focus on the most impactful issues. Provide your review via structured output.
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
    "Critique": {
      "description": "A single actionable critique from the reviewer.",
      "properties": {
        "category": {
          "description": "Category: 'methodology', 'evidence', 'novelty', 'clarity', 'scope', or 'rigor'",
          "title": "Category",
          "type": "string"
        },
        "severity": {
          "description": "Severity: 'major' or 'minor'",
          "title": "Severity",
          "type": "string"
        },
        "description": {
          "description": "Clear description of the issue",
          "title": "Description",
          "type": "string"
        },
        "suggested_action": {
          "description": "Concrete suggestion for how to address this critique",
          "title": "Suggested Action",
          "type": "string"
        }
      },
      "required": [
        "category",
        "severity",
        "description",
        "suggested_action"
      ],
      "title": "Critique",
      "type": "object"
    },
    "DimensionScore": {
      "description": "Score for a single review dimension with improvement suggestions.",
      "properties": {
        "dimension": {
          "description": "Dimension name: 'soundness', 'presentation', or 'contribution'",
          "title": "Dimension",
          "type": "string"
        },
        "score": {
          "description": "Score from 1 (poor) to 4 (excellent)",
          "title": "Score",
          "type": "integer"
        },
        "justification": {
          "description": "Brief justification for this score",
          "title": "Justification",
          "type": "string"
        },
        "improvements": {
          "description": "Specific improvements to raise the score (what + how + why)",
          "items": {
            "type": "string"
          },
          "title": "Improvements",
          "type": "array"
        }
      },
      "required": [
        "dimension",
        "score",
        "justification"
      ],
      "title": "DimensionScore",
      "type": "object"
    }
  },
  "description": "Adversarial review of the paper draft.\n\nID format: review_it{iteration}__{model}",
  "properties": {
    "overall_assessment": {
      "description": "Overall assessment of the paper's quality and readiness",
      "title": "Overall Assessment",
      "type": "string"
    },
    "strengths": {
      "description": "Key strengths of the paper",
      "items": {
        "type": "string"
      },
      "title": "Strengths",
      "type": "array"
    },
    "dimension_scores": {
      "description": "Scores (1-4) for: soundness, presentation, contribution",
      "items": {
        "$ref": "#/$defs/DimensionScore"
      },
      "title": "Dimension Scores",
      "type": "array"
    },
    "critiques": {
      "description": "Actionable critiques \u2014 specific issues with concrete suggestions",
      "items": {
        "$ref": "#/$defs/Critique"
      },
      "title": "Critiques",
      "type": "array"
    },
    "results_reported": {
      "description": "True only when the paper's headline numbers come from an artifact that was EXECUTED \u2014 a run that finished and wrote its output \u2014 AND you RECOMPUTED the headline number(s) yourself from that artifact's own tables or result files rather than accepting the write-up's figure. A mismatch between what you recompute and what is reported is a critique in its own right, even when the artifact is real. False when any headline number is projected, expected, illustrative, a placeholder, produced by a run that errored, was truncated, never ran, or when you could not recompute it \u2014 say so in `overall_assessment` and treat that claim as unverified rather than accepted.",
      "title": "Results Reported",
      "type": "boolean"
    },
    "coverage": {
      "default": "partial",
      "description": "How much of the USER'S ORIGINAL request this paper answers: 'full' \u2014 it answers the request; 'partial' \u2014 it answers a recognisable piece of it; 'lost' \u2014 the paper answers a different question than the one asked.",
      "enum": [
        "full",
        "partial",
        "lost"
      ],
      "title": "Coverage",
      "type": "string"
    },
    "blocking": {
      "description": "True when this paper must not ship as it stands. It is DERIVED, not judged: true exactly when the soundness dimension score is 1 or lower OR results_reported is false; otherwise false. A headline claim that contradicts the run's own evidence scores soundness 1. A value that disagrees with this rule is sent back.",
      "title": "Blocking",
      "type": "boolean"
    },
    "score": {
      "description": "Overall quality score from 1 (very strong reject) to 10 (award quality)",
      "title": "Score",
      "type": "integer"
    },
    "confidence": {
      "default": 3,
      "description": "Confidence in assessment from 1 (educated guess) to 5 (absolutely certain)",
      "title": "Confidence",
      "type": "integer"
    }
  },
  "required": [
    "overall_assessment",
    "strengths",
    "critiques",
    "results_reported",
    "blocking",
    "score"
  ],
  "title": "ReviewerFeedback",
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

### [2] SKILL-INPUT — aii-web-tools · 2026-09-24 15:21:35 UTC

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

### [3] SYSTEM-USER prompt · 2026-09-24 15:24:17 UTC

```
Your response above was stopped by a safety classifier — this is not a tool or API error. The rest of it was withheld, and tool calls in it that had not finished did not run. Do not produce that content again, even reworded.
```

# gen_plan_experiment_2 — test_idea

> Phase: `invention_loop` · round 4 · `gen_plan`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_plan_experiment_2` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-24 15:43:54 UTC

````
<ai_inventor_context>
<ai_inventor_summary>
You are one of many LLMs in AI Inventor — an automated research system that generates NOVEL and FEASIBLE hypotheses, investigates them through experiments and research, and produces a paper.

Your output feeds other LLMs downstream. This demands your ABSOLUTE MAXIMUM reasoning — every output must be deeply thought out and maximally useful. Surface-level responses waste downstream computation.
</ai_inventor_summary>

<your_role>
YOU ARE: A plan generator (Step 3.2: GEN_PLAN in the invention loop)

You received the hypothesis, an artifact direction to elaborate, and dependency artifacts relevant to the plan.
Your job: elaborate this direction into a detailed, actionable plan for the executor agent.

Specific, actionable plan → valuable artifact. Vague plan → wasted execution.
</your_role>
</ai_inventor_context>

<artifact_type_info>
You are expanding an artifact direction of type: EXPERIMENT

EXPERIMENT
Run code to test hypotheses, implement methods, and collect empirical results.
Runtime: Python 3.12, UV (any pip package), isolated workspace, gradual scaling (mini → full data).
Tools: Full shell/Python/filesystem access, the aii-web-tools skill (web search, page fetch, regex grep over full page/PDF text), and other skills.
Skills: aii-json (schema validation), aii-openrouter-llms (call any LLM — GPT, Gemini, Llama, etc.), domain-specific as needed.
Capabilities: Implement and run any code-based experiment, compare method vs baselines.
Deps: REQUIRED at least one DATASET | OPTIONAL RESEARCH for methodology guidance
</artifact_type_info>

<available_resources>
<software_constraints>
- Python only implementation
- Python standard library and all popular PyPI packages available (numpy, pandas, scikit-learn, scipy, matplotlib, requests, etc.)
- Local parallelism encouraged: multiprocessing, asyncio, threading — see aii-parallel-computing skill
- LLM API calls must go through OpenRouter only (no direct OpenAI, Anthropic, etc.), with base_url=os.environ["OPENROUTER_BASE_URL"] and api_key=os.environ["OPENROUTER_API_KEY"] (the OpenAI SDK's defaults, OPENAI_BASE_URL and OPENAI_API_KEY, point at the same place, so a plain OpenAI() client also works with OpenRouter model ids). The key is this run's own OpenRouter key and works only at that base URL: never hard-code OpenRouter's own URL, or every call fails with 401
- **SPEND BUDGET**: at most $10 USD of OpenRouter API calls for this artifact. Nothing outside your own code enforces this — the key you are given has no per-artifact cap — so it holds only if you track cumulative cost after every call and stop when you approach it. Budget the work up front: estimate the per-call cost and the number of calls BEFORE starting a sweep, not after it overruns. Exceeding it spends real money that the run cannot recover.
</software_constraints>

<skills>
Skills are self-contained capabilities with instructions, context, and tools.

- aii-web-tools: Free-first web search (general + scholarly modes), page/PDF fetch as markdown, regex grep over page/PDF text
- aii-semscholar-bib: Batch-fetch BibTeX from Semantic Scholar
- aii-openrouter-llms: Search and call 300+ LLMs via OpenRouter
- aii-hf-datasets: Search, preview, download HuggingFace datasets
- aii-owid-datasets: Search and load Our World in Data tables
- aii-lean: Compile/verify Lean 4 code, Mathlib search, tactic suggestions
- aii-concept-fig-gen: Generate/edit images via Gemini 3 Pro Image (Nano Banana Pro)
- aii-json: Validate JSON against schemas, generate mini/preview variants
- aii-paper-writing: Academic paper structure, bibliography, citations
- aii-paper-to-latex: Assemble LaTeX papers and compile to PDF
- aii-parallel-computing: GPU acceleration, CPU parallelism, async I/O
- aii-python: Python coding standards for experiment scripts
- aii-use-hardware: Detect CPU/RAM/GPU, memory-safe processing
- aii-long-running-tasks: Gradual scaling pattern for long-running tasks
- aii-colab: Google Colab runtime constraints for notebooks
- aii-file-size-limit: Check and split oversized output files
</skills>
</available_resources>

<time_budget>

The experiment executor has 6h total (including writing code, debugging, testing, and fixing errors).

</time_budget>

<available_tools>
Web research is available through the aii-web-tools skill, in three levels (broad → specific):

1. web search — Returns titles, URLs, snippets. Use first to discover and scan the landscape. Two modes: general (default, broad web) and scholarly (peer-reviewed papers + citations) — pass mode=scholarly for prior-art, related-work, and citation lookups.
2. web fetch — Reads a page and returns its content as markdown (HTML or PDF). Use to understand a source. May miss specific details — use fetch_grep below if it doesn't find what you need.
3. fetch_grep — Regex search over a page/PDF's full text. Returns exact matching sections with context. Use for precise details, exact numbers, methodology, or PDFs.

Workflow: search → fetch (understand) → fetch_grep (extract specifics).
</available_tools>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<plan_guidelines>
You are expanding an artifact direction from the strategy into a detailed plan.
The artifact direction specifies what to do at a high level (type, objective, approach, dependencies).
Your job is to make it concrete and actionable as a detailed plan.
Use web research to look up technical details, verify feasibility, and find reference materials
that will make your plan more concrete and actionable for the executor.

GOOD PLANS:
- Make each component SPECIFIC and actionable (not vague platitudes)
- Consider both success AND failure scenarios
- Build on the approach in the artifact direction
- Add concrete details the executor needs

BAD PLANS:
- Vague hand-waving ("do research on X")
- Ignoring the approach in the artifact direction
- Missing critical details the executor needs
</plan_guidelines>

<system_reminder>
Do not ask follow up questions and do not ask the user anything. Execute all steps independently.
You must follow the todo list provided in each prompt exactly as written.
No placeholders, stubs, or incomplete code — all code must be complete and functional.
</system_reminder>

<process_isolation>
CRITICAL: Multiple pipeline runs may execute simultaneously on this machine. `ps aux | grep method.py` matches ALL runs, not just yours.
- NEVER kill processes by name (`killall`, `pkill -f`, `ps aux | grep ... | xargs kill`). This kills OTHER runs' processes.
- NEVER monitor processes by name (`ps aux | grep method.py`). You will see other runs' processes and get confused.
- ALWAYS use PID-based process management:
  Run: `uv run method.py & PID=$!` or `timeout <seconds> uv run method.py & PID=$!`
  Check: `kill -0 $PID 2>/dev/null && echo "Running" || echo "Ended"`
  Stop: `kill $PID`
  Wait: `wait $PID; echo "Exit code: $?"`
  Monitor: `tail -f logs/run.log & TAIL_PID=$!` then `kill $TAIL_PID` when done
</process_isolation>

<workspace>
Your workspace: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_plan/gen_plan_experiment_2`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_plan/gen_plan_experiment_2/`:
GOOD: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_plan/gen_plan_experiment_2/file.py`, `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_plan/gen_plan_experiment_2/results/out.json`
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

<hypothesis>
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
_strands:
- artifact: art_xLy2vVlI7OEL
  state: genuine_positive
  why: >-
    At matched energy AND matched layer count, placement decides: SL 0.24 vs 0.81 (E3), CIs exclude 0, Holm p 0.000; nested
    R2 placement 0.718 vs count 0.400; controls null; 481/481 re-derived.
- artifact: art_0XmNBGkzsJc_
  state: genuine_positive
  why: >-
    Keyword counter never leaves 72-100/100 across all 116 draws while judged refusal spans 7-98/100; MAE 30.6 vs 2.1 per
    100; kappa +0.196 vs 0.858 certified; 11,600 in-loop gens, 305/305 audited.
- artifact: art_ex4hbgThhJaL
  state: lead
  why: >-
    P1/P2 rejected under power (dR2 0.040, LOO -0.002, MDE 0.071). Band-density rho -0.942 survives placebo but SL regression
    coefficient +0.156 [-0.240, 0.529]; one model, exploratory.
- artifact: art_kfCCWf7o8eJ9
  state: lead
  why: >-
    Index claim dead (rho -0.009 over 21 rows), but two cheap baselines beat it and cosine with CIs excluding 0 (rho +0.732,
    +0.661); judge below its own gate at kappa 0.683.
- artifact: art_Z3I1K3VnFZuz
  state: lead
  why: >-
    Executed bound on our own headline: strict gap +.22-+.71 vs broad -.04-+.37, S5X +.69 -> +.23, PARTIAL .548; 8 mismatches
    and 2 sign-reversals in 167 numbers; within-edited kappa .779 vs .913 pooled.
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
</hypothesis>

<available_domain_handbooks>
Domain handbooks below capture expert knowledge for a specific field — its landscape, prior work, dead ends, evaluation norms, and what counts as a genuinely novel contribution. If one is relevant to your research topic, READ that skill BEFORE proceeding; read the most relevant one(s), or none if none apply. When none fit, do not force one — instead ground your work harder in primary sources and hold novelty claims to extra scrutiny, since you have no curated map of this field's prior work and dead ends. Use it for the methods, proper baselines, and evaluation this field demands.

- **aii-handbook-auto-computational-linguistics** — Field handbook for computational linguistics as a SCIENCE of language — grammaticality and minimal pairs (BLiMP), surprisal versus reading times, linguistic structure in LMs, annotator disagreement an
- **aii-handbook-auto-mechanistic-interpretability** — Field handbook for mechanistic interpretability of neural networks — circuit discovery, activation and attribution patching, sparse autoencoders, transcoders, attribution graphs, steering vectors, pro
- **aii-handbook-auto-multi-agent-llm-systems** — Field handbook for multi-agent LLM systems (MAS) — orchestration topology, multi-agent debate, mixture-of-agents, verifier and critic agents, inter-agent protocols (MCP/A2A), failure attribution and s
- **aii-handbook-auto-neurosymbolic** — Field handbook for neuro-symbolic AI — text-to-logic autoformalization (NL to FOL), LLM-plus-solver and prover pipelines (Prolog, ASP, SMT), probabilistic-differentiable NeSy (DeepProbLog, Scallop), r
</available_domain_handbooks>

<strategy_domain_reasoning>
How the strategist established that researchers in this field reason, at the level of the field's principles and standards of evidence. Take it as the starting point for the concrete practice below — extend or correct it where your own reading disagrees, and say so when you do.

FIELD: mechanistic interpretability of safety behaviour (refusal-direction editing / abliteration), applied cross-lingually, with an evaluation half borrowed from jailbreak/refusal-evaluation methodology. Grounding for this step: the aii-handbook-auto-mechanistic-interpretability field handbook (the knowledge-action gap - probe AUROC near ceiling while output-level sensitivity is far lower, so decodability is not use; causal effects of a single extracted direction behave as volatile random variables across sites and seeds; difference-in-means beats fancier decompositions for both detection and steering; per-sample steering is unreliable; the venue's two-track bar: a falsifiable hypothesis reported with the evidence for AND against it, or a demonstrated practical gain over a well-implemented baseline), plus the primary sources this run has already read and re-quoted: Arditi et al. 2406.11717 (refusal mediated by one direction, removed at every component that writes the residual stream), Wang et al. 2505.17306 (the direction is near-universal across safety-aligned languages), Souly et al. StrongREJECT 2402.10260 and the validity-aware evaluation line (substring / non-refusal metrics systematically overstate how much refusal was removed), the effect-based site-selection line ('Read-Best Is Not Steer-Best' 2609.22135, Cross-Architecture Steering Transfer 2608.05164), and this run's own twelve executed artifacts. Two arXiv identifiers carried from earlier steps (2607.02714's '2-3 middle layers' claim) are flagged NOT VERIFIED by this run's own audit pod and must travel with that flag.

(1) PRINCIPLES. Taken as given: refusal is mediated by a low-rank, largely linear direction recoverable by difference-in-means; interventions at the components that write the residual stream change behaviour; the direction itself is close to language-universal. Still argued: whether a decodable direction is the one the model USES; WHERE in depth an intervention has to act and whether that is a stable property of a checkpoint; whether any extracted direction is an object or one draw from an equivalence class. Nothing is read at all unless the intervention is causal, the controls are matched on more than one nuisance dimension, and the outcome is measured on generations rather than on the quantity that was optimised.

(2) WHAT COUNTS AS CONVINCING. Not a correlation over a sweep. What is believed here: a prediction frozen and hashed before the confirmation data is touched and then checked out of sample; matched-efficacy rather than matched-dose comparison; controls matched on energy AND on collateral (this run already learned that energy-matched random interventions are destructive, so energy matching alone is not a control); held-out harm categories and a second model family; and a judged behavioural outcome with an explicit PARTIAL and INVALID class plus the judge's within-edited-arm agreement quoted. Critically for this iteration: the field now also demands that a proposed instrument BEAT the trivial baseline, because effect-based selection work has repeatedly shown cheap causal probes outperform geometric predictors.

(3) STANDARD MOVES AND WHAT EACH RULES OUT. Difference-in-means over trained probes (probe-capacity artefacts). Single-site causal ablation profiles (decodability-vs-use confusion). Matched-random and matched-principal-component controls (the 'any perturbation of this size does it' account). Matched-efficacy rescaling (the 'it was merely stronger' account). Frozen versus refitted probes (representation drift versus information loss). Split-half noise ceilings and label-permutation placebos that MUST collapse (learner and item artefacts). Judge validation with an explicit partial class (the substring metric's documented over-reporting). Post-hoc reselection within a fixed candidate pool (mis-scoring versus a different search).

(4) USUAL FAILURE MODES. One configuration reported as the mechanism; the proxy drifting from the construct - here in its sharpest form, since a keyword counter is near-exact on unedited models and inverts on edited ones because suppressed refusals become caveat-laden partial answers; incoherent or empty output silently counted as suppression; layers, doses and thresholds tuned on the test items; prompt-level confidence intervals presented as optimiser run-to-run variance; n = 2 checkpoints carrying a claim about training regimes; cross-model cosine read as shared mechanism; and an instrument reported as validated because it correlates in-sample while never being raced against the one-forward-pass baseline.
</strategy_domain_reasoning>

<domain_practice>
FIRST WORK OUT HOW THIS KIND OF STUDY IS ACTUALLY BUILT IN THIS FIELD. Then
write the plan.

The strategy already settled what the field believes and what it counts as
convincing. Your job is the level below that: how work of exactly this kind
is designed, run and reported by the people who do it, concretely enough that
the executor's output would be recognised as competent by one of them.

Establish, for this field and this artifact type:

- BASELINES AND COMPARISONS. Which comparisons appear in every paper of this
  kind, named specifically. Which one would a reviewer name first if it were
  missing, and what is the standard way of tuning it fairly?
- CASES AND DATA. Which datasets, corpora, cohorts, benchmarks, case sets or
  sources are standard here, and which are known to be saturated, leaked,
  deprecated or unrepresentative. Prefer the ones the field actually uses,
  and say why when you pick something else.
- CONTROLS AND WHAT IS HELD CONSTANT. What has to be held fixed for the
  comparison to mean anything, and which confound this design is most likely
  to be caught on.
- HOW MUCH IS ENOUGH. Sample sizes, item counts, seeds, repeats, splits —
  the number below which nobody in this field believes a result, and what the
  field reports alongside a point estimate (variance, intervals, a
  significance or uncertainty treatment). When a power analysis, or the
  effect sizes already on record, say the panel cannot detect the size of
  effect the plan is chasing, the fix is more graded samples or checkpoints
  — not more candidate metrics. An underpowered panel stays underpowered no
  matter how many readouts run over it.
- MEASURES AND REPORTING CONVENTIONS. Which measures are standard, how they
  are computed here, and the conventions a reader will expect to see — what
  is reported, against what, in what form.

Not every axis applies to every artifact type: a proof has proof standards
and an accepted level of rigour rather than sample sizes, a research artifact
has source quality and coverage, a dataset has provenance, licensing and
documentation norms. Answer the ones that apply and skip the ones that do not
rather than inventing content for them.

HOW MUCH EFFORT. Bounded, like the strategist's: the fitting domain handbook
plus a handful of targeted lookups — one or two recent papers doing this exact
kind of study, a benchmark or dataset card, a methods or reproducibility note.
Read what the field does; do not reason it out from first principles. You
cannot run code, so this is reading only.

THEN CHECK THE PLAN AGAINST IT.
- `domain_practice`: what you established above, concretely — named baselines,
  named data, the numbers, the measures, with what you read.
- `practice_alignment`: go through the plan you just wrote against that list
  and say, point by point, where it MEETS the field's practice and where it
  DEPARTS from it. For every departure: why it is justified here (budget,
  scope, the claim being narrower) and what it costs the result's
  credibility. A departure nobody named is the one a reviewer finds.
- Where the check exposes a gap you can close inside the budget, close it in
  the plan rather than reporting it. `practice_alignment` is for what remains
  after you have fixed what you can.
</domain_practice>

<artifact_direction>
Make this direction concrete and actionable. Keep the same type and respect dependencies.

id: experiment_iter4_dir2
type: experiment
objective: >-
  The boundary-and-confound half: run the identical frozen overlap protocol in cjvt/GaMS3-12B-Instruct and test whether the
  development-measured causal write profile reproduces, out of sample, the fact that the EFFECTIVE region differs between
  the two siblings - the claim the previous draft wrongly denied and the candidate explanation of the two-checkpoint dissociation.
approach: >-
  Copy the SHARED SPEC from slot 1 verbatim (hardware, pins, read-only inputs, traps, scoring, freeze discipline) so the two
  panels pool, and use the SAME overlap definition, the SAME matched-energy/matched-count construction, the SAME controls,
  the SAME two cheap baselines and the SAME frozen statistics. POD-SPECIFIC ADDITIONS. (A) Measure the single-layer causal
  write profile e_L(h) in THIS checkpoint on development items only, and freeze it. Then state, BEFORE generating any confirmation
  condition, the out-of-sample prediction in its sharpest form: the per-language argmax of e_L(h) must name the region whose
  matched-energy condition wins on held-out harm categories, and that named region must DIFFER from the anchor model's - the
  existing panels put one checkpoint's Slovene residual at 0.02 in a region where the other never falls below 0.95 at any
  strength, and at the same total energy a contiguous mid-depth band reaches 0.63 where a strided set over the full depth
  leaves 0.98. If the profiles name the same region in both checkpoints, or name a region that loses, that is a recorded miss
  of a pre-registered prediction, reported as such. (B) THE DISSOCIATION CONFOUND, HEAD-ON. Re-measure, under this pod's scorer
  and with its overlap value computed, the three conditions that bound the achieved-optimisation account: the shipped edit
  of this checkpoint, the cross-applied parameter set from the sibling, and a dose-matched arm of the sibling's own selected
  edit. Report each one's overlap, its energy, its per-language residual, its attack success under the official guard pipeline,
  its language consistency and its validity columns. The question this answers is whether the two checkpoints' different outcomes
  are predicted by their different write profiles at the achieved edit placement - i.e. whether placement explains the dissociation,
  or whether achieved strength does, or both, with the two accounts separated by holding energy fixed. (C) ANCHORS for comparability
  with the existing panels: the single-site condition, the shipped adapter, and the band profile at unit strength, all re-reported
  under this pod's scorer with PARTIAL shown, so the previously published band rows can be pasted beside the anchor model's
  per-set minima in the paper. (D) JUDGE HONESTY: the previous run of this panel reached only 0.54 English agreement within
  edited arms, so every English rate here is reported as one end of a range and is BLOCKED from confirmatory reading until
  the re-certification in slot 4 clears it or supplies bias-corrected rates; the Slovene arm, which reached 0.86, carries
  the confirmatory weight. (E) Keep every cross-checkpoint statement descriptive (two siblings, one architecture, one or two
  seeds, 4-bit) and attribute nothing to any training stage. Re-derive all headline numbers by an independent path with placebos
  that must collapse; ship per-generation files, per-cell profiles and a paste-ready table.
what_it_would_show: ''
depends_on:
- id: art_qdUCJWbc5kHh
  label: dataset
  relation_type:
  relation_rationale:
</artifact_direction>

<dependencies>
Completed artifacts this artifact can use during execution.

--- Dependency 1 ---
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
out_dependency_files:
  file_list:
  - data.py
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
  data_file_paths:
  - full_data_out.json
  - mini_data_out.json
  - preview_data_out.json
</dependencies>

<prior_work>
Everything this run has already produced, earlier rounds included. This is what
the plan builds on.

--- Artifact 1 ---
id: art_vzhOPupFwE4M
name: gen_art_experiment_1
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
iteration: 1
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json

--- Artifact 2 ---
id: art_jxrJNc9o4QSp
name: gen_art_experiment_3
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
iteration: 1
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_3
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json

--- Artifact 3 ---
id: art_m6pglf516e2r
name: gen_art_experiment_4
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
iteration: 2
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 4 ---
id: art_a4VkEvYRquBO
name: gen_art_experiment_5
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
iteration: 2
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 5 ---
id: art_KFZCxJcrr84K
name: gen_art_experiment_6
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
iteration: 2
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_6
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 6 ---
id: art_CUChUm6wCwo5
name: gen_art_experiment_7
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
iteration: 2
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_7
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 7 ---
id: art_hmbXDppkPZnR
name: gen_art_experiment_8
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
iteration: 2
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 8 ---
id: art_ex4hbgThhJaL
name: gen_art_experiment_9
type: experiment
title: How deep must an edit go to stop Slovene refusal
summary: |-
  Coverage x strength factorial on Heretic-family weight edits in google/gemma-3-12b-it (NF4), asking whether Slovene refusal survives an English-derived edit because the edit is not DEEP enough. 122 cells, 27,784 generations, all judged by a partial-aware 4-way scorer (local Qwen3-14B on iteration-2 exp4's frozen rubric verbatim; REFUSED/PARTIAL/COMPLIED/INVALID, PARTIAL counted as compliance and shown separately, INVALID never refusal), certified at kappa = 0.866 refused-vs-not against a bought 600-item gpt-4.1 subsample on THIS run's own edited cells (on-disk pools gave 0.779, below the 0.80 bar, so the subsample was bought as the plan prescribes; $0.70 of a $10 cap).

  WHAT FAILED (pre-registered, with its own falsifier firing). P1: coverage descriptors add dR2 = 0.040 [0.006, 0.136] over log-energy + the English effect + static geometry baselines, but leave-one-out dR2 = -0.002, partial F p = 0.17, and a permutation placebo yields a LARGER dR2 on average (p95 0.158); MDE = 0.071 < the 0.10 bar, so this is a powered rejection. P2: pooled matched-energy contrast +0.049 [-0.000, 0.098], inside its label-swap placebo, signs disagreeing across the four groups, and the coverage x language interaction runs BACKWARDS (DiD -0.120 [-0.214, -0.033]); held-out harm categories replicate this. Both fail Holm.

  WHAT SURVIVED, each placebo-tested. P3: the DEV-frozen depth index predicts per-cell residuals out of sample, Spearman 0.78 in both languages (permutation null [-0.27, 0.29]); 97% of cells covering fewer than index_SL = 20 effective layers leave Slovene above 0.5, but only 47% at/above it fall below, so the index is NECESSARY not sufficient. The mechanism is band DENSITY, not breadth: lowest reachable Slovene refusal is monotone in the fraction of layers 13-24 covered (12/12 -> 0.024-0.171; 6/12 -> 0.732; 3/12 -> 0.927; 0/12 -> 0.951-1.000), Spearman -0.942, permutation p = 0.0038. At identical energy (E = 19.2), 12 contiguous mid-depth layers reach SL 0.63 while 24 layers strided over the full depth leave 0.98. Leave-one-band-out: sparing layers 25-36 costs Slovene +0.39 residual refusal and English 0.00. An independent activation read converges: Slovene's harm-write mass is 60% in 25-36 where English's is 63% in 37-48.

  CROSS-LANGUAGE CLAIM, CORRECTLY BOUNDED. index_EN = 16 vs index_SL = 20 is directionally as pre-registered, but 4 layers is one k-grid step and sits INSIDE its language-permutation null [-4, +4] - the index alone does not carry it. The powered statistic is the prefix-curve separation: +0.080 [0.021, 0.136], permutation p = 0.0065.

  PRACTICAL. Heretic's own kernel support at c = 1.5 reaches SL 0.024 / EN 0.049 harmful refusal at FLORES dNLL -0.000 nats, KL 0.030, 0% invalid, 99.2% Slovene (screen), and SL 0.08 / EN 0.02 on 100 VERIFIED RefusEU translation pairs (vs unedited 0.98/0.91). The frozen-subset kernel at x1 cuts Slovene over-refusal on XSTest-safe from 0.37 to 0.08 at utility cost indistinguishable from zero. Iteration 2's activation repair reaches lower Slovene refusal but costs +0.589 nats and a real English capability hit (-0.053 [-0.083, -0.023] S7 macro). Both matched controls (write-space random, energy-matched harmless PC; energy matched within 10% AND collateral matched, 8/8 accepted) are null at SL 0.95-1.00.

  REUSABLE FOR LATER ROUNDS (absolute paths in README.md): results/gens/ (all 27,784 generations, 122 cells), results/cells/ (coefficient profiles, closed-form edit energies, FLORES/KL, control-draw diagnostics, S7 utility), results/cells.csv, results/per_item.parquet, results/judge_local.jsonl + judge_api.jsonl, the frozen redundancy_index.json / frozen_predictions.json / FREEZE.sha256, report_tables.md, and 6 figures. Verification: rederive.py re-derives 318/318 headline numbers through a stdlib+numpy path importing nothing from the repo; audit_positive.py placebo-tests every surviving positive claim and is what demoted the index statistic and corrected the band claim from "contains" to "covers densely". 13 deviations recorded. Native Slovene review remains PENDING; one model, one seed, NF4 only.
iteration: 3
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_9
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 9 ---
id: art_xLy2vVlI7OEL
name: gen_art_experiment_10
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
iteration: 3
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_10
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 10 ---
id: art_0XmNBGkzsJc_
name: gen_art_experiment_11
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
iteration: 3
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_11
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 11 ---
id: art_kfCCWf7o8eJ9
name: gen_art_experiment_12
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
iteration: 3
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12
out_expected_files:
- method.py
- full_method_out.json
- mini_method_out.json
- preview_method_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md

--- Artifact 12 ---
id: art_Z3I1K3VnFZuz
name: gen_art_evaluation_1
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
iteration: 3
workspace_path: >-
  /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_evaluation_1
out_expected_files:
- eval.py
- full_eval_out.json
- mini_eval_out.json
- preview_eval_out.json
- reproducibility.md
out_dependency_files:
  file_list:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
</prior_work>

<build_on_prior_work>
BUILD ON WHAT THE EARLIER ROUNDS ALREADY PRODUCED. That is the default, not an option.

<prior_work> lists what this run has already built. Before planning anything
from scratch, go through it and find what this artifact can stand on:
- data that is already collected, cleaned, split or labelled
- models, fits, checkpoints or indexes that are already trained or built
- harnesses, scripts and evaluation code that already run
- the findings themselves, the NEGATIVE ones included — a condition already
  ruled out is a result to build past, not ground to cover again

Then say in `builds_on`, concretely, what this plan reuses: which artifact,
which file, from where. The executor gets a dependency's files only through
the direction's declared dependencies, so when the plan leans on an artifact
that is not among them, say in the plan where the executor picks it up
(workspace path, output file) and keep the plan runnable if it is missing.

STARTING A FRESH LINE is allowed on exactly two grounds:
1. The iteration's move is a WIDEN — the run deliberately went back to the
   original ask to screen different candidate answers, so a new line is the
   point of the round.
2. The line this would have continued is a SETTLED NEGATIVE — already tested
   well enough that pushing it further buys nothing.
On either ground, `builds_on` says which one it is and why, and still names
whatever infrastructure (data, harness, code) the new line can reuse.

"Cleaner to start over" is not one of the two grounds. Neither is a plan that
simply does not mention the earlier rounds.
</build_on_prior_work>

<own_your_inputs>
A STEP THIS PLAN COMMISSIONS MUST HAVE ITS INPUTS OWNED BY SOMETHING SCHEDULED.

If this plan pre-registers a later phase — a held-out confirmation, a blind
set, a second pass, a replication — that phase needs inputs of its own:
labels, ground truth, an annotation pass, a scored reference. Before writing
that phase into the plan, name what produces those inputs and where that
production is scheduled: inside this artifact's own steps, or as one of the
direction's declared dependencies. Say it concretely, not "labels will be
added" — which task, at which point in the plan.

A later step whose inputs nobody is scheduled to produce is not a plan for
that step, it is a plan to skip it while looking like it was included.
</own_your_inputs>



<instructions>
YOUR ROLE: Write a detailed PLAN for the artifact. A separate executor agent runs the actual artifact later.

You are a PLANNER, not an executor. Your output is a plan that tells the executor what to do and how.
Do NOT execute the artifact itself — a separate agent handles that. Your job is to plan it so well that the executor can follow your plan step by step.

You CAN and SHOULD: search the web, read papers, and explore library docs to make your plan concrete.
You CANNOT run shell commands or scripts — code execution is disabled. Research via web tools only.

Do NOT do the executor's job: don't download datasets, don't implement code, don't run experiments, don't write proofs, don't compute evaluations.

<artifact_executor_scope>
IMPORTANT: Each artifact executor has a focused prompt that guides it to do ONE thing well. It will NOT perform tasks outside its scope — assigning the wrong work to the wrong artifact type wastes an iteration. Match the task to the right executor.

EXPERIMENT executor scope:
  Output: method_out.json with results (metrics, predictions, analysis) — the core computational work
  DOES: Implement and run methods/algorithms, compute metrics, compare approaches, produce quantitative results
  DOES NOT: Collect new datasets (depends on DATASET artifacts for input data), write formal proofs
  This is the right artifact for any code that processes data and produces results
</artifact_executor_scope>

<artifact_planning_rules>
EXPERIMENT: Must depend on at least one DATASET. Define clear metrics and baselines before running. Consider trying multiple method variations rather than a single approach.
</artifact_planning_rules>

<compute_profiles>
Choose the compute profile this artifact needs for execution.
Available profiles for experiment artifacts:
  - gpu_basic: 1x NVIDIA RTX A4500, 20GB VRAM, 7 vCPUs, 29GB RAM — ML training, CUDA, large models (fallback: GPUs cheap→expensive: 2000 Ada → A4000 → 4000 Ada → L4 → 4090 → 5090)
  - cpu_plus: 4 vCPUs, 32GB RAM — large datasets, memory-intensive processing (fallback: CPUs cheap→expensive, then GPU hosts cheap→expensive (all ≥32GB RAM))

Set runpod_compute_profile to one of these exact tier names.
</compute_profiles>
GOOD PLANS: specific, actionable, consider failure scenarios, build on the suggested approach.
BAD PLANS: vague hand-waving, ignoring the suggested approach, missing critical executor details.
</instructions><user_data>
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
  "description": "Plan for an EXPERIMENT artifact.",
  "properties": {
    "domain_practice": {
      "default": "",
      "description": "How a study of exactly this kind is actually built and run in THIS field: the baselines every comparable paper reports, the datasets/corpora/cohorts/case sets that are standard (and the ones known to be saturated or unrepresentative), what is held constant, the sample sizes and repeats below which nobody believes a result, and the measures and reporting conventions a reader expects. Name what you read.",
      "title": "Domain Practice",
      "type": "string"
    },
    "practice_alignment": {
      "default": "",
      "description": "This plan checked point by point against that practice: where it meets the field's norms and where it departs from them, with why each departure is justified here and what it costs the result's credibility.",
      "title": "Practice Alignment",
      "type": "string"
    },
    "builds_on": {
      "default": "",
      "description": "What this plan REUSES from earlier rounds, named concretely: which artifacts, files, datasets, checkpoints, fitted models or negative findings, and where the executor picks each one up. If the plan starts a fresh line instead, say so here and give the reason it is allowed to \u2014 the iteration is a widen, or the prior line is a settled negative.",
      "title": "Builds On",
      "type": "string"
    },
    "title": {
      "description": "Plan title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance and it fits the run visualizations. Aim for about 4-8 words (~40 characters).",
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "default": "",
      "description": "Brief summary",
      "title": "Summary",
      "type": "string"
    },
    "runpod_compute_profile": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": "cpu_basic",
      "description": "Compute tier for execution \u2014 pick from the available profiles list (e.g., 'gpu_basic', 'gpu_plus', 'cpu_plus', 'cpu_basic'). Only used in RunPod mode.",
      "title": "Runpod Compute Profile"
    },
    "implementation_pseudocode": {
      "description": "High-level pseudocode for the experiment implementation",
      "title": "Implementation Pseudocode",
      "type": "string"
    },
    "fallback_plan": {
      "description": "What to do if the primary approach fails - alternative methods, simplified versions",
      "title": "Fallback Plan",
      "type": "string"
    },
    "testing_plan": {
      "description": "How to validate the experiment works: start with small/fast tests, look for confirmation signals before running full-scale experiments",
      "title": "Testing Plan",
      "type": "string"
    }
  },
  "required": [
    "title",
    "implementation_pseudocode",
    "fallback_plan",
    "testing_plan"
  ],
  "title": "ExperimentPlan",
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

### [2] SYSTEM-USER prompt · 2026-09-24 15:43:56 UTC

```
Your response above was stopped by a safety classifier — this is not a tool or API error. The rest of it was withheld, and tool calls in it that had not finished did not run. Do not produce that content again, even reworded.
```

### [3] SKILL-INPUT — aii-handbook-auto-mechanistic-interpretability · 2026-09-24 15:45:45 UTC

The agent loaded the **aii-handbook-auto-mechanistic-interpretability** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

```
---
name: aii-handbook-auto-mechanistic-interpretability
description: "Field handbook for mechanistic interpretability of neural networks — circuit discovery, activation and attribution patching, sparse autoencoders, transcoders, attribution graphs, steering vectors, probing, auto-interp, model diffing, CoT faithfulness and monitorability. ALWAYS read before ANY mechanistic-interpretability research work — ideation/novelty assessment, study planning, experiment/eval design, write-up, or review; do NOT work from priors alone (core validity assumptions were contested through H1-2026 and several obvious directions are saturated). Triggers: mech interp, causal abstraction, causal scrubbing, interchange interventions, feature absorption, crosscoders, weight-sparse transformers, MIB, BlackboxNLP. NOT for: post-hoc XAI on tabular or vision pipelines (SHAP/LIME/saliency), prompt engineering, generic capability evaluation, training with no interpretability question, or linguistic-science claims about LMs (use aii-handbook-auto-computational-linguistics)."
---

<!-- GENERATED by amg-handbook-forge — DRAFT for expert review. generated: 2026-07-27 · next_check:
     2026-10-27 (volatile.md half-life ≈ 3 months). ✓x=exec · [Sn]=cited · ⚠️=candidate.
     Row fails → `STALE: <what>` in place. -->

# Mechanistic interpretability — field handbook

## Overview

Scope: the FIELD of mechanistic interpretability — what a mechanistic claim is, how it is
validated, and where the frontier sits mid-2026. The star is the SUBSTRATE below: a dated,
source-anchored map with an explicit do-not-redo list. The only lens is open questions.
This is the SOLE interpretability handbook: SAE-era decomposition
primitives are covered here as one thread of six rather than in a separate deep-dive.

## Organizing principles (how the field reasons)

- The field defines itself by **goal, not method**: understand computational mechanisms "in order
  to accomplish concrete scientific and engineering goals" [S1].
- Its own venue prints a **two-track evidence bar**: either "specific falsifiable hypotheses, and
  how the evidence provided does and does not support them", or "clear practical benefits over
  well-implemented baselines" [S14].
- One methodological critique reframes findings as **statistical estimates, not properties**: the
  causal effect of a component is "a volatile random variable rather than a fixed property" [S4].
- **Structure is not mechanism.** Discovery algorithms "sample from an equivalence class of valid
  subgraphs rather than recovering a unique mechanism" [S23].
- **Causal abstraction is vacuous without an encoding assumption**: with unrestricted alignment maps,
  "any neural network can be mapped to any algorithm" [S5].
- The artifact a reader gets is a **hypothesis about the model, not a description of it** —
  attribution graphs (Anthropic) run on a replacement model and give satisfying insight on about
  "a quarter of the prompts" [S11].

## Frontier (recency-weighted)

**Validity & stability of the method itself** *(weight-capped — the loudest thread)*

- Circuit discovery is unstable under small perturbations: "small perturbations in input data
  or hyperparameters yield vastly different circuits" [S4] (2025-10, rev 2026-05).
- Phantom specialization: across 75 circuits in five Pythia models, structural differences showed
  "apparent specialization but do not correspond to functional differences" [S23] (2026-06).
- The workhorse approximation was diagnosed — attribution patching's "dominant error stems from the
  non-linearities in the downstream network rather than local curvature at the patched component",
  with a correction in the same paper [S19] (2026-06).

**Intrinsic interpretability (train-for-interpretability)**

- Weight-sparse transformers yield understandable circuits, but "making weights sparser trades off
  capability for interpretability", and "scaling sparse models beyond tens of millions of nonzero
  parameters while preserving interpretability remains a challenge" [S18] (2025-11).
- The newest entrant flips the unit from behavior to parameter, asking "whether a single weight can
  be understood globally across the full training distribution" [S2] (2026-07, four models only).

**Evaluation & standardization**

- MIB is a standardized method-comparison benchmark: on causal variable localization "the supervised DAS method
  performs best, while SAE features are not better than neurons" [S10] (ICML 2025), extended to a
  community shared task whose framing admission stands — "measuring progress in MI remains
  challenging" [S22] (BlackboxNLP 2025).
- Randomized baselines invalidate the auto-interp proxy: SAEs on randomly initialized transformers
  score similarly to trained ones [S9] (2025-01, rev 2026-01).

**Decomposition primitives (the SAE era, and after)**

- The sparsity objective is itself a distorting inductive bias: feature absorption "is caused by
  optimizing for sparsity in SAEs whenever the underlying features form a hierarchy", so
  "SAE latents may be inherently unreliable classifiers" [S30] (NeurIPS 2025 Oral).
- The single latent is not a canonical unit — SAE stitching shows dictionaries are incomplete and
  meta-SAEs show they are "not atomic" [S33] (ICLR 2025); seed-unstable latents concentrate in
  "reproducible lower-rank subspaces", i.e. basis ambiguity rather than noise [S35] (2026-06).
- The raw-latent verdict a reviewer will cite: on steering "prompting outperforms all existing
  methods" and on detection difference-in-means wins — "SAEs are not competitive" [S31] (2025-01);
  contested, but only by an unreviewed supervised-pipeline rebuttal [S25].
- Proxy metrics are the field's own named weak point: "gains on proxy metrics do not reliably
  translate to better practical performance" [S32] (ICML 2025).
- Model diffing has a known-bad default: the crosscoder L1 loss "can misattribute concepts as unique
  to the fine-tuned model, when they really exist in both models"; the same paper ships the BatchTopK
  fix [S34] (NeurIPS 2025).
- The flagship open fleet has already moved past SAE-only — Gemma Scope 2 ships "transcoders,
  cross-layer transcoders, and crosscoders" alongside SAEs [S36] (2025-12).

**Reasoning-trace interpretability**

- Faithfulness and monitorability come apart: "models can appear faithful yet remain hard to
  monitor when they leave out key factors" [S12] (2025-10).
- The dominant unfaithfulness metric is contested — it "confuses unfaithfulness with
  incompleteness", and "the absence of hint words alone does not prove unfaithfulness" [S13]
  (2025-12, rev 2026-05).

**Applied / safety-facing interpretability**

- Persona vectors (Anthropic) predict and pre-empt training-induced trait shifts, and "flag training data that
  will produce undesirable personality changes" [S16] (2025-07) — the clearest applied win.
- A blinded audit protocol exists: three of four teams "successfully uncovered the model's hidden
  objective", SAEs among the techniques used [S17] (2025-03).
- Counter-current, and the sharpest 2026 negative result — internal decodability far exceeded output
  behaviour: "Linear probes discriminated hazardous from benign cases with 98.2% AUROC, yet the
  model's output sensitivity was only 45.1%, a 53-percentage-point knowledge-action gap." SAE
  feature steering "produced zero effect despite 3,695 significant features", and steering was
  "indistinguishable from random perturbation" [S3] (2026-03; 400 physician-adjudicated vignettes,
  one clinical domain).

**Field strategy & meta-science**

- A frontier lab publicly narrowed its bet — "We have been disappointed by the amount of progress
  made by ambitious mech interp work, from both us and others", and "We made a decision to
  deprioritise SAE research as a result, not because we thought the technique was useless" [S6]
  (2025-12). One team's decision, not a field verdict.
- Results are not yet comparable across papers: two studies reached "conflicting conclusions for the
  same behavior", a third found both "partially correct but incomparable" [S8] (2026-04).

## Recent (~1–2 yr, compressed) · Durable core

- The field's own review concedes "there are many open problems in the field that require solutions
  before many scientific and practical benefits can be realized" [S1] (2025-01), and the LRM sub-map
  names the same gaps [S24]. The two framings a reviewer will invoke: "the returns from
  interpretability have been roughly nonexistent" [S7] (2025-05), against "We are thus in a race
  between interpretability and model intelligence." [S15] (2025-04) — a stated goal, not a result.
- Durable: activation patching remains the gold-standard causal metric faster methods approximate [S19];
  attribution graphs remain the scaling story, with their stated ceiling [S11].

## ⛔ Already crowded — go ELSEWHERE (do-not-redo)

The blank space is NOT in these lanes; each is saturated through H1-2026:

- **Circuit-discovery methods and their corrections.** Attribution patching, its error diagnosis and
  second-order fix [S19], structural-vs-functional decoupling [S23], and an eight-method community
  bake-off [S22] are all published.
- **Auto-interp / agentic feature explanation.** Both the agentic pipeline [S21] and the
  randomized-baseline invalidation of its metrics [S9] already exist.
- **Activation steering and its reliability diagnostics.** Per-sample unreliability and the
  linear-approximation limit are characterized [S20]; the AxBench verdict
  already has a published rebuttal [S25].
- **CoT faithfulness / monitorability metrics.** The measurement wave [S12] and the
  metric-invalidating counter-wave [S13] have both landed.
- **Benchmarking MI methods against each other.** MIB [S10] plus its shared-task extension [S22]
  own this; a new leaderboard re-treads it.
- **Developmental / training-dynamics interpretability.** Feature evolution is already tracked
  across pre-training snapshots with crosscoders [S28] (ICLR 2026).
- **Training-data attribution as an interpretability method.** Already explicitly bridged to MI and
  causally validated on Pythia [S26].
- **Multimodal / vision-language mechanistic interpretability.** Has its own survey and taxonomy
  since 2025-02 [S27].
- **Mechanistic interpretability of RL-trained reasoning models.** Occupied through 2026 — temporal
  sparse autoencoders already track feature dynamics across RLVR training [S29].
- **Sparse-dictionary decomposition of activations.** The most-worked lane in the field: SAE features
  are "not better than neurons" on MIB [S10], the auto-interp metrics used to defend them fail a
  randomized baseline [S9], absorption is traced to the objective itself [S30], canonical-unit claims
  are refuted [S33], and the raw-latent steering/detection verdict plus its rebuttal are both
  published [S31] [S25].

> **Standing directive — this list is necessarily INCOMPLETE.** Map-silence means *not-yet-checked*,
> NOT *open*. Before committing to any direction this map does not explicitly flag as crowded, run
> a fresh, dated saturation search and confirm the space is actually unoccupied. (Measured in this forge's own
> A/B runs: a live-searching baseline beats a static handbook precisely on the crowded lanes a
> map omits.)

## Open questions the field hasn't answered

*(the whole lens — the reader answers in their own way)*

1. If exact single-input causal scores are volatile random variables [S4] and structurally distinct
   circuits implement one computation [S23], **what object is circuit discovery actually estimating,
   and at what granularity is a "mechanism" even well-defined?** The field's standard output — one
   circuit, one figure — presupposes an answer it has not given.
2. Causal abstraction is vacuous without a constraint on how models encode information [S5]. What
   would make such an encoding assumption testable independently of the claim it licenses?
3. Near-perfect internal decodability coexists with a large knowledge-action gap and steering
   indistinguishable from random perturbation [S3]. What would have to hold for "we understand it"
   to imply "we can change it" — and is that implication load-bearing for the field's stated
   goals [S1]?
4. Two verdicts clash: the returns are "roughly nonexistent" [S7], yet the same window produced
   deployed applied results [S16] [S17]. On what measure are both true, and which should a paper
   report?
5. Two studies reached conflicting conclusions on one behavior and a third found both partially
   right but incomparable [S8]. What makes two mechanistic findings comparable at all, and can that
   be settled without a standard the field does not yet have?
6. Interpretability is bought at a stated capability cost with a scaling ceiling [S18], while
   auto-interp scores fail to separate trained from random networks [S9]. What is the exchange rate
   between understandability and capability, and who should be willing to pay it?

## What counts as DEEP here (taste)

| Naive move | Expert judgment/move | Why (failure prevented) | tier | src |
|---|---|---|---|---|
| Ship a new circuit/feature method that improves a proxy metric on one task. | The rewarded move meets the venue's own bar: state "specific falsifiable hypotheses, and how the evidence provided does and does not support them", or show "clear practical benefits over well-implemented baselines". Recognition signal: a NeurIPS 2025 **Spotlight** went to a result proving the field's own framework vacuous when generalized [S5]. | problematizes-nothing — proxy-metric progress reads incremental in 2026 | L·A | [S14] [S5] |
| Treat a high auto-interpretability or reconstruction score as evidence that real features were recovered. | **Buried (2025-01, rev 2026-01):** the same scores appear on randomly initialized transformers [S9]. Reopening condition, stated there: routine randomized baselines plus targeted measures of feature abstractness. | wrong-result — the metric does not discriminate the thing it is used to claim | L | [S9] |
| Report one circuit, from one extraction, one seed, one input distribution, as *the* mechanism. | **Buried (2025-10 → 2026-06):** effects are volatile random variables [S4]; structure-to-function is many-to-one [S23]. Reopening condition: edge-level evaluation plus cross-condition transfer tests. | wrong-result — a single-draw circuit is an unreported sample from an equivalence class | L | [S4] [S23] |

> **Science-vs-application, as this field draws it:** unusually, it prints BOTH bars in one
> sentence [S14] — a falsifiable mechanistic claim, or a demonstrated practical benefit over strong
> baselines. What clears neither is a method with a better proxy score and no falsifiable
> hypothesis attached [S9] [S22].

## Critical rules (execution · eval · validity)

| Naive move | Expert judgment/move | Why (failure prevented) | tier | src |
|---|---|---|---|---|
| Report a circuit from one seed/hyperparameter/input set. | Designing the run: sample across seeds, hyperparameters and input distributions; report the distribution and stability metrics, not the modal circuit. | wrong-result — single-config circuits are unstable | L | [S4] |
| Read structural difference between two circuits as two mechanisms. | Before claiming distinct mechanisms: run edge-level evaluation and cross-condition transfer; source-level evaluation inflates apparent faithfulness. | wrong-result — phantom specialization | L | [S23] |
| Use attribution patching scores as ground truth at scale. | When approximating: screen with a reliability score and correct the leading term; expect downstream non-linearity, not local curvature, to dominate the error. | wrong-result — the evidence for the circuit is itself misspecified | L | [S19] |
| Validate an interpretation with a freely-parameterized alignment map. | Stating the claim: fix and declare the map class, and make the encoding assumption explicit — unconstrained maps hit 100% interchange-intervention accuracy on randomly initialized models. | wrong-result — a perfect fit that means nothing | L | [S5] |
| Use a raw SAE latent as a classifier or steering target. | Choosing the unit: benchmark against difference-in-means and a prompting ceiling before claiming a latent works; expect absorption to make single latents unreliable where features are hierarchical. | wrong-result — the raw-latent verdict is the field's default prior | L | [S31] [S30] |
| Read a crosscoder model-diff at face value. | Diffing two models: use BatchTopK rather than L1 and presence-test any "unique to the fine-tune" latent — the artifact is a property of the loss. | wrong-result — the loss fabricates unique-to-finetune latents | L | [S34] |
| Score SAE/dictionary features against nothing. | Choosing the comparison: benchmark against non-featurized hidden vectors (neurons) and supervised DAS on MIB's tracks. | wrong-result — featurization may add zero | L | [S10] |
| Report auto-interp scores as the validity evidence. | Reporting: add a randomized-transformer arm; treat aggregate auto-interp as a proxy, never as recovery evidence. | wrong-result — untrained networks pass | L | [S9] |
| Claim a steering result from a mean effect at one coefficient. | Reporting steering: give the per-sample distribution and the behaviors where it fails; effect sizes "vary across samples and are unreliable for many target behaviors". | wrong-result — the mean hides the failure regime | L | [S20] |
| Call a CoT unfaithful because it omits a hint that changed the answer. | Judging traces: separate unfaithfulness from incompleteness, and pair hint-based metrics with causal mediation. | wrong-result — the metric over-reports | L | [S13] [S12] |
| Claim interpretability *enables* correction because the information is decodable. | Closing the loop: measure output-level correction AND collateral disruption of already-correct cases, against a random-perturbation control. | wrong-result — decodability ≠ actionability | L | [S3] |

## Decision guide

- **Which primitive for which question:** components and their interactions → circuit localization
  (attribution / mask optimization lead on MIB); an interpretable variable inside a hidden vector →
  causal variable localization (supervised DAS leads; SAE features do not beat neurons) [S10].
- **Post-hoc vs trained-for-interpretability:** post-hoc buys you the deployed model; weight-sparse
  training buys understandability at a capability cost and stops scaling in the tens of millions of
  nonzero parameters [S18].
- **Auditing claims:** in the reference blinded protocol, three of four teams succeeded, leaning on
  several technique families together rather than interpretability alone [S17].
- **Weighing sources:** most 2026 frontier results here are unreviewed preprints; the peer-reviewed
  anchors are [S5] (NeurIPS 2025 Spotlight), [S10] (ICML 2025), [S22] (BlackboxNLP 2025).

## Ground rules (known-lane — terse)

- Activation patching = the gold-standard causal metric; attribution patching = its first-order,
  gradient-based approximation, adopted for cost [S19].
- A "circuit" is a subgraph claimed to explain a behavior on a sub-distribution; the contrasting
  framing asks instead whether a single weight can be understood globally [S2].
- Attribution graphs are computed on a replacement model that "incompletely and imperfectly
  captures the original", so they yield hypotheses, not conclusions [S11].
- Interchange-intervention accuracy is a fit statistic, meaningful only relative to a declared map
  class [S5].
- Monitorability ≠ faithfulness: a trace can be faithful and still omit factors a monitor needs [S12].

## Reference documentation

- **[volatile.md](volatile.md)** — dated frontier numbers, lane-occupancy flags, and per-source
  review status. Re-check this FIRST before any novelty verdict or write-up.

## Candidate lane  ⚠️ (expert to resolve — NOT verified)

- ⚠️ **The crowded list is still not exhaustive.** Every lane flagged here has now been
  saturation-checked and ALL came back occupied (all are listed above). No flagged lane remains open.
  **Treat any lane this map does not mention as unchecked, not open, and search before committing —
  the measured base rate for unchecked lanes in this forge is 11/11 occupied.**
- ⚠️ **The actionability negative result [S3] is one clinical domain, one model family.** It is the
  strongest published statement of the knowledge-action gap, but generalization beyond triage
  vignettes is unverified. Confirm/refute: a replication in a non-clinical task with the same
  four-method comparison.
- ⚠️ **No peer-reviewed field-wide SURVEY was fetched** (a 2026 ACM Computing Surveys entry exists
  but was access-gated), and nothing independently confirms other labs made the same call as [S6].
  Individual claims are well-anchored — seven sources here are peer-reviewed — but a field-wide
  "the field holds X" statement still lacks a survey to rest on.
```

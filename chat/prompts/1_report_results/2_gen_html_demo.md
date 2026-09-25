# gen_html_demo — report_results

> Phase: `gen_paper_repo` · `gen_html_demo`
> Run: `run_A3Dbh1J6RI3O-msgsum` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_html_demo` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-25 09:28:36 UTC

````
<design_philosophy>
You are building ONE explorable web page for a research result. The reader should come away
having SEEN the result in the run's own data, because they operated it: they switched between
the conditions the run compared, dragged a threshold and watched the numbers move, pointed at a
mark to see which model or item it was, filtered down to the cases where the method failed, and
put an input beside its output. The page explains through interaction. It is not the paper with
nicer CSS, not a list of headline numbers, and not a gallery of the paper's figures.

WHAT EARNS AN INTERACTION
Every control answers a question a reader actually has at that point, and it changes a view drawn
from the run's real data:
- "Does it hold everywhere?" A chart of the per-condition, per-model or per-dataset results with a
  control over which ones are shown; the baseline always visible; pointing at a mark shows that
  record in full.
- "What does it do to one case?" An item browser over the real per-item records: filter, search
  or sort, and the selected item shows its input, the method's output, the baseline's output and
  the verdict side by side, as a before and after.
- "Where does it break?" A toggle that isolates the failures, the disagreements or the hardest
  slice, with the counts updating as it changes.
- "What if?" A slider over a parameter the recorded data lets the page recompute honestly, such as
  a decision threshold applied to the recorded per-item scores, with the metrics recomputed live.
- "Can I try it?" A live mini-demo of the method, only when the method runs exactly in a few
  dozen lines of JavaScript; it runs on the embedded examples and shows that its output matches
  the recorded one.
- "How does it work?" A stepper that walks ONE real example through the method's stages with the
  values recorded at each stage, over a pipeline diagram that highlights the current stage.
- "What does this word mean?" Term tooltips on hover, focus and tap, with a glossary.
Do not add an interaction that answers no question: no animated counters, no parallax, no
autoplaying carousel, no toggle that swaps one paragraph for a synonym of itself.

THE DATA IS REAL, OR IT IS NOT ON THE PAGE
Every data point comes from the run's output files, embedded as the file has it or trimmed to
the fields a view uses, and every number the prose states matches the paper. A view may compute
from real data (a mean, a filter, a threshold swept over recorded scores), but nothing is ever
invented, interpolated, simulated or smoothed to make a control feel richer. A page that looks
excellent and misreports one result is worse than no page.

ONE STORY
Top to bottom the page tells one story: the question, the answer shown in a view the reader can
operate at once, how the method works, the evidence to explore, where it fails, and what it does
not show. Each view opens with the question it answers and closes with one takeaway sentence
that rewrites itself to describe what the current selection shows.

CRAFT
- Type carries the design: one system font stack, a real scale with visible jumps between levels,
  body text around 17-19px with a measure of 65-75 characters and generous line height.
- Colour is restrained: a light, near-white ground, one dark ink for text, one accent for links,
  the active state and the highlighted series, a muted second colour for baselines, and a
  colour-blind-safe palette when series need more. No gradients as decoration, no purple-to-blue
  banner, no emoji, no icon fonts.
- Charts are read, not decorated: labelled axes with units, a legend when there is more than one
  series, gridlines light enough to recede, and the exact value one hover, focus or tap away.
- Controls look like controls: a visible affordance, a visible selected state, a visible focus
  ring, and a hit area of at least 40 by 40 pixels on a phone.
- Motion is a courtesy: short transitions on state changes only, and none at all under
  prefers-reduced-motion.
- Every interactive element works with a keyboard and tells a screen reader what it is and what
  state it is in. That is part of the craft, not a checklist bolted on at the end.

FINISH IT
The page is done when you have opened it in a headless browser, operated every control, seen no
script error, read it at a phone width and a desktop width, and found nothing to fix. Not before.
</design_philosophy>

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
Your workspace: `/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/paper`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/paper/`:
GOOD: `/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/paper/file.py`, `/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/paper/results/out.json`
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

<task>
Build ONE self-contained, explorable `interactive.html` for this run's result. The
reader operates views drawn from the run's REAL output data (switching conditions, dragging a
threshold, pointing at marks, filtering items, comparing an input with its output) and comes
away understanding the finding and the method. It is published next to the paper, and its most
prominent link is the paper PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<what_is_already_here>
Your workspace is the finished paper folder. You are adding one file and, where needed, PNG
renders of figures, and linking that file from the presentation page. Change nothing else, and
keep your scratch work (extraction scripts, screenshots) in a temporary directory outside this
folder, because the folder is published.

- `paper.tex`: the paper as written. It is the source for every claim, name, term
  definition and number the prose states.
- `paper.pdf`: the compiled paper. Do not link to it by this local name; link to the
  full URL in the links section.
- `references.bib`: the bibliography, when the paper has one.
- `figures/`: every figure the paper uses, flattened into one folder.
- `index.html`, when present: the paper's static presentation page and the site's
  landing page. Change it in one way only: add the link to your page described under
  presentation_link.
- `workspace/`: the scratch folder the LaTeX task worked in. Ignore it.
</what_is_already_here>

<artifact_data>
Every artifact this run produced, with the directory it ran in and the output files it declared.
These directories are on disk and you can read them. Their JSON and CSV outputs hold the REAL
per-item and per-condition results: the recorded inputs and outputs, the scores, the verdicts,
the per-model and per-setting metrics. They are what the page's views are built from. Where a
file has `mini_` and `preview_` variants beside it, read those first to learn its shape.

- iteration: 1
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_1
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
- iteration: 1
  name: gen_art_experiment_3
  type: experiment
  title: English vs Slovene refusal-direction transfer test
  summary: >-
    A1 screen (iteration 1) on cjvt/GaMS3-12B-Instruct@1d0b27af and google/gemma-3-12b-it@96b6f1ec (Heretic bnb_4bit NF4,
    bf16 compute, L4). Data: 85 JBB harmful/benign twins after a LaBSE S1-overlap audit (15 AdvBench rows dropped), sha1 halves
    A (44) / B (41), Dolly, FLORES+, SL-LLM-Eval MC. SL is Gemini-2.5-flash MT (mean chrF 81), with NLLB fallback for 22 rows.
    Diff-in-means d_EN/d_SL on winsorized residuals; (layer, pos) chosen on half A with Arditi filters (GaMS3 L34, Gemma L20,
    pos -1); protocol hash-frozen before half B. Half B: 15 ablation conditions, u_SL increment with frozen and post-freeze
    raw-energy random controls, matched-efficacy grid, 5-dose addition, K/N/M collateral, 1,596 greedy generations judged
    blind by gpt-4.1 (the plan's gpt-4.1-mini failed the T5 hand-check), and a Heretic bridge (Heretic code, 20 TPE startup
    edits, seed 20260923). KEY RESULTS: R validity gate failed for GaMS3 (Spearman .51, AUROC .70) but passed for Gemma (.91/.96),
    so the verdict is judge-based. Frozen screen verdict: WEAK; A1's predicted contrast is REVERSED. Judged refusal after
    d_EN ablation: GaMS3 EN .90->.46 and SL .93->.34 (residual gap SL-EN -0.15 [-0.32, .03]); Gemma EN .83->.07 but SL 1.00->.85
    (gap +0.77 [.62, .89]), despite cos(d_EN, d_SL) = .92 and a log-odds transfer T(EN->SL) = 3.47. Exploratory explanation:
    Gemma's Slovene refusal margin is large (R 13.9 vs 3.6 EN; 69% of benign SL twins refused), so direction cosine and log-odds
    transfer do not predict behavioural transfer. The Heretic bridge agrees: SL-EN residual gap GaMS3 .11 [.06, .17], Gemma
    .23 [.16, .30]. GaMS3's R-based u_SL increment (F_raw .23, F_ctrl .195/.154) is collateral-confounded (span ablation FLORES
    +1.4 nat/tok; about 35% malformed). Exploratory GaMS3-only double dissociation under addition (u_SL +2.2 SL / -1.5 EN;
    u_EN +3.5 EN / -1.1 SL). Random ablation controls are destructive even when raw-energy-matched (T7 failed; documented
    amendment). Verified: T8 recompute identical; independent plain-python re-derivation matches all T/I/F/rho, judged rates
    and bridge means; placebos null. Files: method_out.json (metadata = full analysis + frozen predictions), results/analysis_summary.json,
    screen_verdict.json, per_item.parquet, judged_generations.json, figures fig1-8, README.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_experiment_3
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
- iteration: 1
  name: gen_art_dataset_1
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art/gen_art_dataset_1
  output_files:
  - data.py
  - full_data_out.json
  - preview_data_out.json
  - mini_data_out.json
- iteration: 2
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 2
  name: gen_art_experiment_5
  type: experiment
  title: Utility cost and inner harm signal after abliteration
  summary: >-
    Four checkpoints (GaMS3-12B-Instruct and gemma-3-12b-it originals + iteration-1 Heretic LoRA edits, trials 88/96), EN
    and SL, NF4, one code path. BEHAVIOUR (gpt-4.1, random ~52% of S4 harmful gens; run budget exhausted): GaMS edit refused
    100->5.6% EN / 6.7% SL; Gemma edit 99->70.3% EN / 95.3% SL (English-derived edit transfers fully in GaMS, barely in Gemma
    although Gemma's EN/SL harm-direction cosine is higher, 0.92 vs 0.83). Marker rule badly undercounts Gemma refusals (32.7%
    vs 70.3%). Second free judge (nemotron-3-ultra) kappa vs gpt-4.1 0.83 (refused) / 0.77 (6-way). UTILITY: 6 tasks x 250
    frozen items x EN/SL, harness-replica scorer validated vs lm-eval (strings 100% identical, flag agreement 98.7/99.5%;
    ll bar fails only via harness bf16 rounding): macro change +0.13/+0.20 (GaMS EN/SL), +0.13/0.00 (Gemma), Holm p=1; all
    task deltas within 1.6 pts; FLORES dNLL <=0.002; no wrong-language/empty/malformed outputs; Gemma EN first-token KL uninformative
    (255/257 'Okay,'). MECHANISM: harm linearly decodable (held-out S4 AUROC >=0.996, not lexical/length). GaMS: frozen original
    probe collapses (0.998->0.60 EN/0.42 SL at L34, min 0.20 at L27) while refit stays 0.985/0.954; 71-73% of harm mean-difference
    energy on the frozen axis removed to ~0.1%, complement AUROC 0.985/0.955 -> re-encoding, not information loss. Gemma:
    frozen-axis separation halves equally in EN and SL from L28, yet behaviour changes only in EN -> axis compression does
    not explain the language asymmetry; late-layer axis rotation differs (cos 0.53 EN vs 0.83 SL). A2 (pre-registered): GaMS
    R_seq passes gate; slope ratio 0.36 EN / 0.42 SL -> EVIDENCE_LOSS label = decoupling of refusal from the ORIGINAL evidence
    axis while information stays decodable (changed mapping). Gemma R_seq fails gate EN; judged logistic also EVIDENCE_LOSS
    (flagged separation artefact). Gemma flips hit low-evidence items first (criterion-shift signature). EXPLORATORY dose-response
    (LoRA x f): Gemma SL needs ~2x edit strength (R_seq>0 harmful SL 98.8/77.4/46.3/7.0% at f=1/1.5/2/3 vs EN 90.3/45.1/24.5/12.8%);
    GaMS EN/SL move together. Bonus GaMS3-12B base: harm decodable (CV AUROC 0.99/0.96), complies with most harmful QA prompts.
    Outputs: method_out.json (8056 examples: S4 per item x lang x role with responses, labels, R_seq/R1, s_i, KL; S7 utility
    per item), results/analysis/tables.md + summary.json, per-item parquets, S5/S5X projections, r_prior npz, figures fig1-fig8,
    blinded review packet (PENDING). Audits: verify_numbers 80/80, audit_headline raw re-derivation identical with failing
    placebos. Caveats: n=2 models, one Heretic run each, NF4, MT Slovene, partial judge coverage.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_5
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 2
  name: gen_art_experiment_6
  type: experiment
  title: 'What English edits miss in Slovene: GaMS3 panel'
  summary: >-
    P1 random-edit panel on cjvt/GaMS3-12B-Instruct@1d0b27af (bnb_4bit NF4, Heretic 3521f864, default LoRA operator). 246
    Heretic edits (E0 = journal trials 0-59, E_TPE = trials 60-115 incl. core trial 88, E1 = 100 prior draws seed 20260925,
    E_R = 30 draws seed 20260924; E0/E1/E_R certified identical to the sibling Gemma pod) were rebuilt through Heretic's own
    reset_model+abliterate and scored in EN and SL on teacher-forced traits over S3 DEV halves A/B: R_seq, R1, Rb (JBB 85
    twins), K = log mean truncated KL on Dolly continuations (100), N = FLORES NLL rise (200), M = MC margin change (120).
    Question: are EN traits (all Heretic's optimiser sees) a sufficient surrogate for SL? Gap_t = R2*(EN_A->EN_B) - R2*(EN_A->SL_B),
    noise-ceiling normalised, joint edit x item bootstrap B=1000, protocol frozen+hashed before any trait. RESULTS (F = 160
    fitted edits, primary learner HistGBT): refusal proxy R_seq passes the judged validity gate (Spearman EN 0.970, SL 0.910
    over 18 conditions). Claim 1 holds (confirmatory): Gap_R = 0.015, 90% CI [0.008, 0.027]: EN predicts SL refusal as well
    as EN. Main hypothesis G3 SUPPORTED for K only (confirmatory): Gap_K = 0.147 [0.074, 0.265], Holm p~0, MDE 0.137, SIMEX
    0.112, margin-matched 0.131, halves 0.118/0.150, B_K 0.050 [0.001, 0.121]; reverse direction -0.124 (language-specific
    K component). SL KL is smaller on average (mean-change ratio 0.59) but EN traits cannot rank which edits hurt SL. N and
    M: F8 'no signal to predict' (no automatic language damage visible). Frozen exposure carrier D FAILS (G4; dR2 for K -0.011
    [-0.058, 0.027]); exploratory post-freeze lead: refusal-direction SOURCE LAYER explains the SL/EN KL ratio (Spearman 0.77;
    dR2 0.047 [0.008, 0.074] over EN traits + static baselines). Gap_Heretic_K on journal trials only 0.018 (boundary). Forecast
    coverage fails on E_TPE for several traits (G6 false). r_prior defined (G5 false). Bilingual reselection keeps trial 88
    (SL_est 1.1). Independent re-derivation (rederive_headlines.py, different learners): Gap_K 0.115/0.105, Gap_R ~0.01, validity
    and kappa exact; all placebos fail. Judging: gpt-4.1 labelled 1130/2140 generations ($1.06) before the run-level OpenRouter
    budget ran out; the remaining 1010 and the second-judge role use a local Qwen3-14B (kappa vs gpt-4.1 0.875 refused-vs-not,
    n=1130); gemini second judge not run. Cross-GPU repro: traits re-score within numerics; weak-edit KL has a hardware floor.
    Per-edit variances for power: results/variances_for_power.json. Key files (workspace /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_6):
    results/verdict.json, results/analysis_results.json, results/panel_items/*.parquet, results/panel_edits.jsonl, results/judged_generations.json,
    results/compliance_refs_gams_core.json (shared export for the Gemma pod), results/summary_tables.md, figures/fig1-fig8,
    method_out.json (one example per edit).
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_6
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 2
  name: gen_art_experiment_7
  type: experiment
  title: English edits barely unlock Slovene refusal in Gemma
  summary: >-
    Gemma-3-12b-it (NF4, Heretic 3521f864) random-edit panel testing whether English refusal/utility traits predict Slovene.
    203 edits scored teacher-forced in EN+SL on frozen S3 DEV halves: E0 = 60 journal startup trials (same vectors as the
    GaMS pod), E1 = 103 fresh prior draws (seed 20260925), E_TPE = trial 96 + last 40 TPE trials (held out). Fitted set 163
    non-collapsed (>=150 floor met). Traits R_seq, R1, Rb, K, N, M; covariates P (r_prior), H (d_EN), D, b1/b2/b3, Omega.
    Validity: 14 edits judged by a LOCAL judge (original gemma, frozen gpt-4.1 rubric; 98.2% binary agreement with gpt-4.1
    on 440 original generations); API blocked by the run budget. R* = R1 (Spearman EN .892 / SL .853). KEY RESULTS: (1) Slovene
    refusal is strongly attenuated: SL/EN transfer slope R1 0.436, R_seq 0.220. Core edit trial 96: judged harmful refusal
    EN 36->10/41, SL 41->39/41; no validity edit brought SL below 30/41. The attenuation survives margin matching (slope 0.558)
    and the mixed model (sl:x -0.321). (2) Teacher-forced, edits raise compliance log-prob equally in both languages (slope
    0.849) but lower the refusal-opener log-prob only in English (slope 0.081). (3) The attenuated response is predictable
    from English: R2 EN_A->SL_B 0.94 vs EN_B 0.99; Gap_R1 +0.054 [0.022, 0.128] (<0.10 -> P-a NOT CONFIRMED; within a label-swap
    placebo range); margin-matched +0.057 (P-d NOT CONFIRMED); Gap_Rb +0.018 (P-b UNTESTABLE, Rb fails the SL gate); Gap_K
    +0.079 (Holm p .009); N and M unreliable in SL. (4) Carrier: r_prior removal P adds dR2 +0.004 over geometry baselines,
    which themselves have CV R2<=0 (P-c NOT CONFIRMED); exploratory H adds nothing. (5) No journal trial has predicted SL
    judged refusal <= 0.20 (best 0.57). Audit (independent numpy path) and rederive.py (raw files, polynomial OLS: Gap_R1
    +0.052; slopes and judged counts match exactly) pass, with placebos failing as expected. Outputs: method_out.json (per-edit
    rows + all analysis tables), results/analysis.json, results/verdicts.json, results/panel/*.parquet, results/validity/,
    figures fig1-6, README.md, reproducibility.md. Caveats: correlational carrier; 4-bit; one model; three GPUs (per-device
    zero points); local judge; MT Slovene with native review pending.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_7
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 2
  name: gen_art_experiment_8
  type: experiment
  title: Why an English safety edit misses Slovene
  summary: >-
    Iteration-2 causal test in google/gemma-3-12b-it (NF4 4-bit, pinned 96b6f1ec), with cjvt/GaMS3-12B-Instruct as a descriptive
    contrast and p-e-w/gemma-3-12b-it-heretic@e037e6e1 as a held-out community edit. Question: is the Slovene refusal that
    survives an English refusal-direction ablation (d_EN, A1 frozen site L20) carried by a harm-orthogonal, language-conditioned
    refusal prior r_prior (Wang et al. 2025 false-refusal construction from judged harmless refusals)? Directions, layer and
    strengths were chosen on S3 half A and frozen (configs/FREEZE.sha256) before the OUTCOME set (41 JBB half-B + 70 StrongREJECT
    held-out-category twin pairs, EN+SL; 111 harmful + 111 harmless per language) was touched. 12,136 greedy generations;
    blind batched gpt-4.1 judge (5,298 labels, every frozen-prediction arm fully covered; $3.43, run budget then exhausted),
    local Qwen3-14B second judge on every generation (kappa 0.77 refused-vs-not). RESULTS: the pre-registered hypothesis FAILS.
    d_EN leaves 0.86 SL harmful refusal (EN 0.23); adding r_prior at matched EN efficacy cuts it by only 0.036 [-0.037, 0.109],
    below the best energy+collateral-matched random (0.074) and the shuffled-label control (0.135): KILL (a) and (c) fire;
    F1/F3/F4/F6 fail, F2 passes, F5 is not evaluable (community SL hoc refusal 0.26 < 0.40). r_prior is language-dominated
    (cos with the language axis 0.65, with its shuffled-label twin 0.89); d_EN+l cuts 0.315 but costs +1.93 nats of SL FLORES
    NLL. r_prior alone gives a real but sub-threshold drop in SL over-refusal (0.28 to 0.19, Holm p 0.025). EXPLORATORY discovery
    (declared post-freeze): ablating each layer's own d_EN(h) at all 48 layers removes the SL residual (0.86 to 0.10, gpt-4.1
    partial coverage; 0.91 to 0.23 second judge) with fluent Slovene (FLORES +0.52), whereas layer-matched random (0.86) and
    energy-matched PC (0.93) controls do nothing, and no single 12-layer band suffices (cumulative through layers 1-36): the
    residual is written redundantly across depth, not missing a direction. The same move repairs the core Heretic edit (SL
    hoc 0.93 to 0.11; its random control 0.47). The core iteration-1 edit is optimisation-limited (SL hoc 0.89 vs community
    0.26). GaMS3 shows no SL-specific residual. Frozen harm probe still decodes harmfulness after ablation; cosine-based transfer
    prediction fails at item level (AUROC 0.24). All numbers re-derived by verify_numbers.py (103/103) and independently from
    raw files by audit_headline.py (43/43, placebos null). Files: method_out.json (per OUTCOME item x language, per-arm responses,
    labels, R1/R_seq; metadata = full analysis, verdicts, deviations), results/analysis_summary.json, results/per_item.parquet,
    results/report_tables.md, figures/fig1-fig10, directions/ (frozen vectors), configs/. Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 3
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_9
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 3
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_10
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 3
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
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_11
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 3
  name: gen_art_experiment_12
  type: experiment
  title: Depth index fails to predict cross-lingual refusal-edit failure
  summary: >-
    Iteration-3 predictive test in google/gemma-3-12b-it (anchor, NF4, pinned 96b6f1ec), Qwen/Qwen3-8B and mistralai/Mistral-7B-Instruct-v0.3
    (EuroLLM-9B-Instruct was the planned M3 but is gated and returned HTTP 403; the recorded fallback order was followed,
    results/load_log.json), in EN/SL plus DE/LT newly translated with NLLB-200-distilled-1.3B. QUESTION: can iteration-2's
    depth-redundancy observation be turned into a PREDICTIVE instrument? A per-language index (smallest cumulative depth coverage
    of d_EN(h) activation ablation at which judged harmful refusal falls below 0.5, measured on DEV-only S3 JBB half-B items)
    was computed, FROZEN and hashed (configs/frozen_predictions.json in configs/FREEZE.sha256; run_model.py --phase conf raises
    without it) BEFORE any confirmation generation, then tested out of sample on 60 held-out StrongREJECT harmful items per
    language (30 held-out-category + 30 in-distribution, paired by semantic id) against English-derived Heretic-operator WEIGHT
    edits (Heretic 3521f864's projected, row-norm-preserving rank-3 LoRA with OUR per-layer directions injected): W0 no-op,
    W1 narrow 25%-depth band, W2 energy-matched all-depth stride, W3 selected kernel (Gemma = the REAL iteration-1 trial-96
    adapter, sha256-verified), W4 energy- AND collateral-matched random. RESULT: the pre-registered claim is FALSIFIED. P1
    pooled Spearman(index, residual refusal) = -0.009 [-0.131, 0.192] over 21 rows (permutation p 0.16); the AUC secondary
    gives +0.167; P2 concordance 8/12 decided (0.67, below the 0.75 bar, and 6/12 under judge-error correction); P3 alone
    holds in sign (Spearman(index, W2-W1) = -0.474). CRITICALLY, EN/L direction cosine ALSO fails (+0.010), so the 'familiar
    geometry stops predicting' boundary is real but stops for our index too, while two CHEAP baselines beat both by margins
    whose paired item-bootstrap CIs exclude zero: single-site transfer rho +0.732 (index-baseline -0.741 [-0.810, -0.528])
    and the unedited model's baseline refusal in that language rho +0.661 (-0.670 [-0.721, -0.497]). Gemma's real trial-96
    adapter on held-out items leaves EN 0.60 / DE 0.53 / LT 0.75 / SL 0.92 from a 0.93-0.98 no-op, replicating the iteration-1/2
    English-Slovene asymmetry on a new harm source and extending it to two new languages; its energy- and collateral-matched
    random control leaves SL at 0.98, and the SL-NLLB vs SL-gpt translation-method control moves every rate by <=0.09, closing
    that confound. POST-HOC (exploratory, changes no verdict, prompted by the language-shuffle placebo returning -0.356 instead
    of ~0): within the anchor model the index DOES order the languages (rho +0.678) but Qwen3's eligible languages all share
    one index value so it has zero variance there; pooled within-model-centred rho is +0.458 (AUC +0.620), and cosine REVERSES
    sign between models (-0.748 gemma, +0.556 qwen3). The frozen eligibility gate did real work pre-hoc: Mistral refuses only
    0.07-0.53 at baseline (0.07 in Lithuanian) so all four of its rows were excluded before any confirmation data existed,
    and it was dropped from the weight panel under the pre-registered cut order rather than swapped silently. AUDIT: rederive.py
    (stdlib+numpy only, reading only raw generations, labels and the frozen file) reproduces every index, AUC, eligibility
    flag, residual and P1-P4 statistic: 102 checks, 0 mismatches; placebos (b) index permutation -0.009, (c) label swap flips
    sign, (d) DEV-as-CONF correctly flagged LEAKAGE. Positive control 4/4: the Gemma DEV curve reproduces iteration-2's anchor
    (EN P50 0.39 vs 0.42, SL P75 0.27 vs 0.21). JUDGE LIMITATION, reported not buried: the run's OpenRouter budget was exhausted
    before this artifact began ($0.00 spent here), so gpt-4.1 was unavailable and the planned fallback could not fire; the
    local Qwen3-14B judge (rubric variant chosen on a DEV split of the free existing gpt-4.1 label pool, certified once on
    a disjoint holdout) reaches kappa 0.683 [0.629, 0.737], BELOW its 0.80 gate, with Se 0.984 / Sp 0.741, so absolute refusal
    levels are biased upward and a Rogan-Gladen corrected re-run of P1/P2 is reported. analysis.py was patched after the freeze
    for numerical robustness only (empty-bootstrap quantile; undefined differences must not count as decided); both hashes
    and the full diff are in results/analysis_patch.json and checks.py flags analysis_py_unchanged=false. Native review PENDING.
    9,199 blind 4-way judged generations; method_out.json has 8,520 per-example rows. Workspace: /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_experiment_12
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 3
  name: gen_art_evaluation_1
  type: evaluation
  title: Rechecking every number and every judge
  summary: >-
    CPU-only audit of the iteration-2 draft against raw per-item files of 7 artifacts (iter1 exp1/exp3; iter2 exp4-8), by
    an independent code path, plus a judge-sensitivity instrument. AUDIT: 167 draft numbers checked: 137 match, 8 mismatch,
    12 misdescribed, 6 untraceable (mismatch rate .055); 2 sign-reversed conclusions: (a) iter-1 swap: GaMS3 trial-88 params
    on Gemma give EN 100->53, SL 97->25 at KL .254 (draft '91/95 at .293' exists in no file); (b) exp7 P-a was frozen as 'Gap_R
    >= 0.10 with LB>0' and failed because the gap is SMALL (.054), the draft inverts it. 13.4x = ratio of medians of refusal
    drop per unit KL (1449 vs 108), not refusal counts. A3 reading 'intermediate'. Exp3 judge was gpt-4.1 only; Gemma EN baseline
    .83 not 99%. JUDGES: exp4 gpt-4.1 vs Qwen3-14B binary kappa .913 pooled but .779 [.678,.861] within edited checkpoints
    (inflation .133; AC1 .908); exp8 .769 vs .737. Keyword proxy on gemma_edit EN: .851 vs judged .255, FP share .761 (71%
    of FPs PARTIAL), kappa -.04. 19/99 behavioural claims JUDGE_SENSITIVE (e.g. exp8 A1 EN .225 gpt-4.1 vs +.44 higher under
    Qwen on same items). KEY FINDING: the Gemma SL-EN refusal gap is definition-dependent: STRICT (refused) +0.22 to +0.71
    across LLM judges/datasets, all CIs > 0; BROAD (refused+partial) -0.04 to +0.37. S5X paired (Qwen) strict +.69 [.60,.78]
    -> broad +.23 [.14,.32]; RefusEU S5 broad -.04. The English edit mostly converts EN refusals into PARTIAL replies. Placebos
    6/6 pass; headline numbers re-derived independently (10/10 match). Optional gpt-4.1 top-up blocked (HTTP 403 run budget),
    $0 spent, no labels invented. No native review exists (packets pending). FILES: results/report_repairs.md (paste-ready
    tables for repairs 1-10 with source paths), corrected_numbers.json (236 records), judge_sensitivity.csv/md, judge_agreement.csv,
    keyword_miscalibration.csv, gap_range.csv, claims_registry.csv, dead_end_ledger.md, pending_human_review.md, novelty_table.md
    (verbatim quotes; 2607.02714 '2-3 middle layers' NOT VERIFIED), audit_log.json, configs/label_map.yaml (reusable for new
    cells), figures fig_gap_forest/fig_judge_stack/fig_kappa_inflation.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_3/gen_art/gen_art_evaluation_1
  output_files:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
- iteration: 4
  name: gen_art_experiment_13
  type: experiment
  title: Where a refusal edit lands decides what survives
  summary: |-
    WHAT WAS RUN. A frozen, DEV-only causal write profile e_L(h) (judged refusal drop from ablating the frozen English refusal direction d_EN(h) at ONE hidden index, 44 JBB half-A items/language, 48 sites) defines an overlap instrument O_L(edit)=sum_h e_L(h)g(h)/||g|| over each Heretic-family weight edit's closed-form per-layer removal energy g(h). O is invariant to coefficient rescaling, so it measures placement only. O was frozen (hashed, mtime-checked) and tested out of sample on google/gemma-3-12b-it NF4: 29 conditions x 60 frozen held-out items/language (40 StrongREJECT held-out-category + 20 verified RefusEU EN-SL pairs). The conditions were 8 matched groups (high-O vs low-O windows at IDENTICAL closed-form energy and IDENTICAL layer count), energy-matched write-space random and harmless-PC controls, a dose ladder and a no-op. Outside family: Qwen3-8B (EN/SL/DE; LT excluded by the pre-registered gate), 3 matched groups + controls. 10,000 generations were judged 4-way (REFUSED/PARTIAL/COMPLIED/INVALID) by local Qwen3-14B on the frozen exp4 rubric; the gate used 800 gpt-4.1 labels ($0.97).

    RESULTS. (1) FROZEN VERDICT: FALSIFIED for the instrument claim. O's incremental R2 over the pre-declared nuisance stack is 0.026 EN (powered, MDE 0.047) and 0.052 SL (inconclusive band), below the 0.05 falsifier, because the g-weighted EN/SL direction cosine is collinear with O (rho 0.81/0.76; R2 alone 0.83/0.63 vs O 0.87/0.75). (2) PLACEMENT IS STRONGLY CONFIRMED. The high-O member leaves less refusal in 8/8 groups in both languages (pooled EN -0.69 [-0.75,-0.62], SL -0.38 [-0.46,-0.31]; best: layers 16-31 EN 0.07/SL 0.27 vs layers 33-48 0.92/0.92 at the same energy). Random/PC controls stay within +-0.03 of the no-op, and a 2x dose of the late-layer edit still leaves EN 0.88/SL 0.92. (3) O ranks the 18 held-out conditions near-perfectly: Spearman -0.96 EN, -0.83 SL. It beats the unedited refusal rate and the single-site transfer rate on pooled rows (aligned CI [0.28,0.65], [0.29,0.76]), beats the single-site peak probe in EN (+0.17 [0.14,0.23]) and ties it in SL. (4) The language-label placebo does NOT collapse (EN profile predicts SL residual at -0.94), so the language-specific claim is demoted: O works by locating a shared mid-depth band (argmax prediction band 13-24 passes). (5) Under the best-placed edit the EN/SL gap is a strict-vs-broad effect (strict 0.07 vs 0.27, broad 0.53 vs 0.53; ASR-by-rubric 0.93 vs 0.72). (6) Qwen3-8B replicates placement: 9/9 matched contrasts favour high-O (8/9 CIs exclude 0); Spearman(O) EN -0.76, SL -0.93, DE -0.84; the miss REVERSES there (EN retains more refusal than SL). (7) Screen on 46 exp9 cells: O -0.71/-0.60 but energy dominates (dR2 0.008/0.028). Post-hoc harmless KL is a strong competitor (exploratory).

    JUDGE CAVEATS. Within-edited kappa 0.818 pooled; EN 0.856 passes, SL 0.744 fails, so SL is JUDGE_SENSITIVE (Rogan-Gladen keeps the ranking and enlarges the contrasts). The Gate-2 INVALID probe failed (the judge never labels synthetic incoherence INVALID), so a deterministic validity guard was added before confirmation. Native review pending.

    AUDIT. rederive.py (stdlib+numpy, independent path): 209/209 checks pass, including shuffled-O and label-swapped placebos that fail as required. Files: results/analysis.json, report_tables.md, cell_table.csv, per_item.csv, gens/, judge_local.jsonl, judge_api.jsonl, configs/frozen_predictions.json, figures/fig1-6, deviations.json (18 deviations, 3 NOT RUN: utility panel, guard ASR, GaMS3 screen).
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_13
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 4
  name: gen_art_experiment_14
  type: experiment
  title: Where a refusal edit must land in a Slovene model
  summary: |-
    Iteration-4 slot-2 pod, cjvt/GaMS3-12B-Instruct (NF4), 12,024 judged generations, 44 cells, $0.00 OpenRouter spend.

    WHAT IT BUILT. A per-language CAUSAL WRITE PROFILE e_L(h): the judged drop in harmful refusal from applying Heretic's own abliteration operator at ONE decoder layer with the frozen d_EN(h), measured on DEV items only (40 harmful per language). A pre-freeze pilot on DEV showed a single layer at Heretic's own bound moves almost nothing (max drop 0.05 at c=1, 0.10 at c=1.5), so the profile was measured at c=2.5 (max drop 0.65, zero degenerate output) - recorded as deviation D1. The profile peaks sharply at hidden index 27 in both languages; band mass EN 0.00/1.05/1.50/0.27 and SL 0.02/0.55/0.57/0.05 over bands 1-12/13-24/25-36/37-48. Split-half reliability is 0.812 (EN) but 0.312 (SL), so by the pre-registered rule the SLOVENE PROFILE IS DECLARED UNRELIABLE and its argmax prediction demoted to exploratory BEFORE the freeze. Frozen into O = sum_h e_L(h) g(h)/||g||_2 with 28 cell specifications, predicted O and rank, the named band and the thresholds, hashed into configs/FREEZE.sha256; the confirmation entry point raises without it (proved adversarially in results/gate_freeze.json).

    WHAT SURVIVED OUT OF SAMPLE (verdict PARTIAL, pre-registered ladder). Over 20 matched-energy confirmation cells (12 edited layers each, energy matched within 0.6%, 70 held-out-category StrongREJECT pairs per language) Spearman(O_SL, surviving Slovene strict refusal) = -0.903, CI [-0.928,-0.857], permutation p<0.001; within each energy level separately -0.967 (E2) and -0.948 (E3). Nested over log removal energy: dR2 0.580, leave-one-cell-out 0.594. O beats log energy (-0.384), depth span (-0.039) and mean depth (-0.328) with paired-bootstrap CIs excluding zero. All six controls (3 layer-matched random, 3 energy-matched PC draws, energy matched to 0.03%, collateral inside the real cells' range) are null: |dSL| <= 0.03 against a no-op of 0.957.

    THE THREE BOUNDARIES THE PAPER MUST CARRY. (1) THE EXPENSIVE INSTRUMENT DOES NOT EARN ITS COST: the same overlap from a FOUR-number band profile (LOO dR2 0.845) and the purely geometric EN/SL cosine overlap (0.834) beat O's 0.594, and the same cell's English outcome predicts the Slovene one at rho 0.945 - indistinguishable from O. The 48-layer profile establishes THAT placement matters, not the cheapest way to measure it. (2) THE NAMED BAND LOST: the DEV argmax names 25-36, but at matched energy band 13-24 removes more judged Slovene refusal (0.30 vs 0.53 at E=27.8) - NAMED_AND_LOST at both levels. The reason is a metric flip: the 33-substring opener rule ranks 25-36 first, judged STRICT ranks 13-24 first, judged BROAD ranks 25-36 first; band 25-36 buys its opener-rule 'success' with PARTIAL responses (mean strict-minus-rule gap 0.182, max 0.514). (3) NOT CHECKPOINT-SPECIFIC ON THESE SCREENS: the GaMS3 profile predicts the sibling checkpoint's 50 weight cells at -0.442, no worse than its own panel's -0.278; both screens are weak because unmatched panels let dose swamp placement.

    PLACEMENT VS DOSE. The A1-A4 ladder (shipped edit, sibling kernel, and each rescaled to the other's energy) sits at the refusal floor: dose moves the outcome at fixed placement (-0.186 and -0.157, McNemar p 0.001/0.003) while placement does not at fixed dose (-0.029, 0.000). A declared POST-FREEZE exploratory pair at E=13.9/27.8 confirms the two production kernels are indistinguishable once dose is matched (d 0.071 and 0.029, CIs including zero) - both spread mass over the effective band. Both accounts are real in their own stratum: placement orders cells at fixed dose, dose lowers refusal by 0.114 at fixed placement.

    JUDGE HONESTY. The budgeted gpt-4.1 certification could NOT be bought (platform key hit its daily limit; $0.00 spent, deviation D10), so certification fell back to on-disk gpt-4.1 labels for GaMS3 edited arms: harmful-row kappa SL 0.830 (PASS, confirmatory) and EN 0.721 (MISS, JUDGE_SENSITIVE, blocked from confirmatory reading). A free third channel (the iteration-3 refusal classifier) run on THIS pod's own cells agrees item-wise at kappa 0.66 SL / 0.43 EN but reproduces the cell-level ordering at Spearman 0.975 / 0.954, so no claim here depends on the scorer.

    AUDIT. rederive.py reproduces 352/352 headline numbers through a code path importing nothing from the analysis, and in that same path both placebos collapse (cell-permutation null +0.003, energy-profile-shuffled null -0.017, both p<0.0001 against the real -0.903); the freeze predates every confirmation file. 10 deviations with evidence files. Reusable by later rounds at their relative paths: configs/frozen_predictions.json (the instrument), results/cells/ (all judged generations and per-layer energy profiles), results/cells.csv, results/per_item.parquet, figures/fig1-fig5.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_14
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 4
  name: gen_art_experiment_15
  type: experiment
  title: Can a refusal optimiser see its own refusals?
  summary: >-
    Replay-only measurement study of Heretic's 33-substring keyword refusal objective (K) on BOTH Heretic searches of this
    run: gemma-3-12b-it (re-scored from art_0XmNBGkzsJc_'s 11,600 in-loop generations) and cjvt/GaMS3-12B-Instruct (replayed
    here, 116 trials + unedited baseline, all 116 bit-exact to the iteration-1 journal on an L4). The reference is the certified
    partial-aware classifier C (threshold 0.52), plus the frozen 4-way judge rubric (Qwen3-14B workhorse). GATES: 60/60 startup
    draws identical in both searches (paired design). Judge vs a bought gpt-4.1 subsample: kappa 0.850 [0.772, 0.911], n =
    800, $0.86. Classifier on GaMS3 without refit: kappa 0.841 [0.745, 0.910]; keyword 0.591. RESULTS: the frozen primary
    prediction (Gemma's objective is blinder, measured by the pairwise gradient-blind fraction GBF on the 60 paired draws)
    is FALSIFIED. C-referenced GBF is 0.006 vs 0.000, difference +0.006 [0, 0.019]. Judge-referenced, the sign reverses: -0.029
    [-0.060, -0.005]. Both objectives are monotone at a coarse scale: GBF is far below the permutation chance level, split-half
    placebo is small, and the self placebo is 0. What differs is calibration: K on J slope 0.32 vs 0.81, mean K-J +19.6 vs
    +6.0, floor 72 vs 16. Low-region blindness also differs: GBF among C<=50 candidates is 0.47 vs 0.02 (judge-referenced
    0.48 vs 0.22). What is SHARED is structural threshold blindness: the objective floor sits above the frozen selection rule's
    10/100 threshold, so TBF = 1.00 in both searches under both references. The rule falls back to 'fewest keyword refusals'.
    On Gemma that fallback picks an under-edited candidate (judged 63/100). On GaMS3 it picks a fully suppressed candidate
    at about 3x the KL of the judge's pick (0.175 vs 0.060). Reselection within each search's own pool changes the selection,
    i.e. mis-scoring, not mis-searching. No edit is recommended (P7 stands). Incumbent's best shot: the oracle count threshold
    (t=2) gives kappa 0.57 (Gemma) and 0.66 (GaMS3). Dropping the 5 content words + empty rule gives 0.17 on Gemma (no fix)
    but 0.68 on GaMS3 (MAE 4.6, the best GaMS3 count accuracy). CAVEAT: the classifier undercounts GaMS3 mid-range refusals
    (mean C-J -6.8 on the certification trials; count MAE 8.7 vs keyword 6.7), so judge-referenced numbers are the robustness
    check on GaMS3. Held-out StrongREJECT (Gemma): keyword kappa 0.02 on edited English, 0.00 on Slovene (English-only list).
    FILES: results/per_candidate.csv (232 candidates: K, C, J, sigma_K, KL, descriptors, flags); results/analysis.json; results/reselection_table.csv;
    results/conventional_table.csv; certification JSONs; results/replay/ (GaMS3 generations); results/judge_out/ (Qwen + gpt-4.1
    labels); figures fig1-fig6. Audits: rederive.py 81/81 re-derived with 0 mismatches (stdlib+numpy); placebo_audit.py (placebos
    fail as required); 18 deviations incl. post-hoc J3 selection-point labels and a per-pair-tolerance sensitivity. Two searches,
    one seed each; AdvBench-derived in-loop set.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_experiment_15
  output_files:
  - method.py
  - full_method_out.json
  - mini_method_out.json
  - preview_method_out.json
  - reproducibility.md
- iteration: 4
  name: gen_art_evaluation_2
  type: evaluation
  title: Partial answers, judges, and a full recount
  summary: >-
    Re-analysis and audit of 56,866 judged generations pooled from five panels (the four iteration-3 panels reconcile exactly
    to 51,353 distinct judged generations; plus the iteration-2 FINAL panel). Predictions, estimators, the Holm family, seeds,
    the judge gate, a 900-item stratified calibration sample and a pre-hoc power simulation were frozen and hashed before
    any fit (configs/FREEZE_iter4_eval.json). C3 (PARTIAL transition): C3-i holds (PARTIAL share non-flat: max-min EN .346
    [.257,.539], SL .271 [.090,.323]). C3-ii is not supported: the proportional-odds check fired, so the nonparametric argmax
    is primary, giving Delta_peak L1 +.45 [-.45,.90] and L2 +.98 [-.98,2.00]. C3-iii is not supported (out-of-panel Spearman
    -.43, permutation p .34). C3 is therefore FALSIFIED under the frozen rule. This is estimator-sensitive: in L1 the continuation-ratio
    fit gives +.35 [.20,.43] and the PO fit +.36 [.28,.43]. The strict-minus-broad identity is stated, not claimed as a finding.
    JUDGE: 515 bought gpt-4.1 labels plus 385 free ones. Within-edited kappa EN .871/.858 (gate MET); SL .871 weighted / .723
    sample (gate NOT MET, so Rogan-Gladen companions are reported). Keyword rule kappa .07; distilled classifier .92. A declared
    post-freeze supplement (160 labels) exposes exp11 EN kappa .23: workhorse REFUSED labels there are mostly gpt-4.1 PARTIAL.
    Re-expressing the cells in gpt-4.1 classes leaves both C3 and the exp11 gaps intact (.68->.63). 40/211 gap claims are
    JUDGE_SENSITIVE and 105 DEFINITION_SENSITIVE. SCOPE: NF4 guard pass (Llama-Guard NF4 vs bf16 agreement .967). In the Gemma
    edit, SL non-refusals are more often guard-safe than EN (+.23 [.12,.35]): non-actionable rather than compliant. Flip analysis
    for Gemma: slope reduced but not collapsed (.50 EN, .34 SL), intercept -6.7/-5.3, refit AUROC .997, i.e. a criterion shift
    plus partial coupling loss while the information survives. GaMS3 is not estimable. NF4 vs bf16: weight error .093, yet
    the edit-energy profile cosine is .999998; 32-token KL .11/.09; bf16 behavioural paired gap +.60 [.40,.80] vs NF4 +.45
    [.20,.70], so the effect is bounded, not closed. Paste-ready repairs R1-R10 with source paths (lint 0), including the
    iteration-1 section restored verbatim. The independent stdlib recompute of 102 iteration-3 numbers finds 4.9% [2.1,11.0]
    wrong; all placebos collapse. Spend $0.92.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_evaluation_2
  output_files:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
- iteration: 4
  name: gen_art_research_1
  type: research
  title: Finding the closest prior work for two results
  summary: >-
    Positioning artifact (web research only; no code, no GPU, no paid API, $0 spend) that gives both of this run's reportable
    results the neighbours the reviewer said they lacked. Deliverables in results/: a 30-row neighbour table (markdown + JSON,
    N1-N30) where every row carries a verbatim <=40-word quote with its locator, a URL, an access date (2026-09-24) and a
    verified flag; two paste-ready positioning paragraphs (positive and negative) each stating its own stopping point; a 30-row
    claims_to_position.csv in which no claim is left without either a neighbour id or an evidenced NO NEIGHBOUR FOUND; reconciliation_map.csv
    (claim id -> neighbour ids -> producing file path -> tag -> paper sections that must agree); a tagged ledger separating
    14 FAILED HYPOTHESES (each with the number and direction that killed it) from 10 UNEXECUTED PROPOSALS (each with its reason);
    the canonical stopping-points block for verbatim reuse; the full search log; and scripts/self_check.py, which passes.
    KEY OUTCOMES FOR THE PAPER. (1) The inherited '2-3 middle layers' attribution is RESOLVED: the sentence does exist in
    arXiv 2607.02714 SS3.2, but as that paper's own attribution to Arditi et al. - which was not found in Arditi et al. by
    full-text search - and 2607.02714 rejects it in the next sentence, having found uniform layer spread beats signal-norm-based
    selection by up to ~70pp. It must not be cited as a standing depth fact. (2) The positive's delta is NARROWED: effect-based
    site selection (Hase 2023; 2609.22135; 2606.00926) and language-specific safety depths (2609.22144; 2605.23036) are already
    published. What survives is the matched-total-energy AND matched-layer-count placement contrast, per language, with the
    effective region differing between two sibling checkpoints - no neighbour found running that construction. (3) The negative
    now has four partial neighbours (Hase 2023; 2606.00926; 2609.04721 on cosine unreliability; 2608.24988 on weight-edit
    geometry surviving behavioural reversion) and an EVIDENCED ABSENCE for the conjunction, with the eight queries behind
    it logged; the wording prescribed is 'not found by these queries'. (4) The selection-blindness finding must be positioned
    against AdvPrefix (2412.10321), not StrongREJECT: AdvPrefix owns objective misspecification inside an optimiser for prompt
    attacks, so this run's claim is the weight-edit instance quantified on the search's own candidate population. (5) Tooling
    state, dated 2026-09-24: Heretic's default scorer on master is still the 33-marker substring counter plus KL over an English
    prompt set, although a benchmark scorer (PR #444, merged Sep 3 2026) and dataset config selection (PR #445, merged Sep
    5 2026) are merged, and the community multilingual set covers 9 languages with no Slovene. Every line is tagged OBSERVATION
    / INTERPRETATION / FAILED HYPOTHESIS / UNEXECUTED PROPOSAL, and every number about this run carries the path of the file
    that produced it.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_4/gen_art/gen_art_research_1
  output_files:
  - research_out.json
  - reproducibility.md
- iteration: 5
  name: gen_art_evaluation_3
  type: evaluation
  title: Re-checking every number in the paper
  summary: |-
    TERMINAL AUDIT (evaluation, audit-only; no generation, no refusal-removal efficacy ranking, no band prescription). eval.py re-derives the iteration-4 draft's numbers from saved per-item files (exp4 C1 behaviour, exp5, exp11, exp13, exp14, exp15, eval2), classifies every source as real-run vs stand-in, and reconciles abstract/tables/figures/conclusion. Start at results/AUDIT_REPORT.md.

    PRIMARY CLAIM, NARROWED TO WHAT SURVIVES. (1) Heretic's English keyword objective cannot fire its own selection rule (primary branch needs <=10/100 refusals): 0/116 candidates in either search (keyword floor 72 Gemma, 16 GaMS3; classifier 6 and 37). The Gemma floor is re-derived from raw in-loop generations and matches on 116/116 draws. (2) On held-out-category StrongREJECT outputs of the 7 edited Gemma arms, keyword vs Qwen3-14B strict kappa = 0.021 [-0.09,0.14] (n=490; fires 0.34 vs judged 0.17; 81% false positives). Broad reference 0.093; vs the 38 on-disk gpt-4.1 labels -0.14 (strict) / -0.08 (broad). Not distinguishable from a shuffled-label null (p=0.37). The held-out prompts are disjoint from the in-loop and S1 construction prompts. (3) CORRECTION: the 'kappa 0.00 in Slovene' is NOT measured chance agreement. The English marker list NEVER fires on Slovene output (0/490 edited, 0/70 original held-out; 0% on RefusEU for all four checkpoints) while the judge finds up to 96% refusal. Kappa is 0 by construction: zero sensitivity. Per-checkpoint RefusEU EN kappas: GaMS3 orig 0.45, edit 0.05; Gemma orig 0.40, edit -0.03.

    REPRODUCED: guard-safe share of non-refusals, Gemma edit, SL-EN +0.231 [0.123,0.340] (EN 0.106 n=245; SL 0.338 n=80; unpaired). Gemma matched placement pooled EN -0.688 [-0.756,-0.616] / SL -0.377 (8/8 groups; SL judge gate failed 0.744). GaMS3 rho -0.903, controls |d|<=0.029. Qwen3-8B 9/9 contrasts favour high-O (8/9 CIs exclude 0). S5X Gemma-edit gap +0.69, guard ASR gap -0.71.

    STRUCK: 'judged refusal and guard ASR order the languages oppositely'. Of 21 paired cells, 15 give the SAME order (11 with both CIs excluding 0), 1 opposite (n.s.), 5 ties.

    DRAFT DISCREPANCIES: 14 of 121 checked claims fail. Eval2 7.2%/32.7% belong to exp11 C_corrected (the Gemma edit values are 10.6%/71.4%). Trial-96/107 judge counts are 37/63, not 15/10. The abstract claims Qwen3-8B rho>0.83 but EN is 0.76. The abstract reverses the NF4/bf16 attenuation direction. exp14 -0.186/-0.029 are Slovene values labelled English. fig_gams3_profile B1/B4 values are wrong (0.97/0.94). fig_dose_response plots substring refusal. exp13 SL dR2 is 0.055, not 0.052. 'keyword .851 vs judged .287' mixes denominators. The community FLORES NLL has no backing file. Also: 9 unresolved citation paths; 12 claims rest on a judge that failed its certification gate; the distilled classifier's held-out kappas are in-distribution (its training pool holds all 140 held-out prompts). No source is a stand-in. The Qwen3-14B-for-gpt-4.1 substitution is recorded per file. A gpt-4.1 purchase for all 1,120 held-out items was blocked (HTTP 403, $0.00). Native review is still absent.

    FILES: eval_out.json/full/mini/preview (9 datasets: recomputation_fidelity, selection_objective_agreement, per_cell_behaviour_exp4, cross_lingual_measurement_bias, guard_safety_of_nonrefusals, evidence_status_ledger [897 assertions], citation_path_lint, scope_table, provenance_inventory); results/claim_registry.csv, recomputed_all.json, rederive.json (14/14 independent matches, placebos fail as required); figures/fig1_objective_agreement, fig2_measurement_bias.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_5/gen_art/gen_art_evaluation_3
  output_files:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
- iteration: 5
  name: gen_art_evaluation_4
  type: evaluation
  title: Recheck every number and every path
  summary: >-
    CPU-only reporting-integrity audit of the iteration-4 paper draft (plan gen_plan_evaluation_3; the executor's task prompt
    arrived truncated, and the plan was recovered from the run log's dispatch order). CITATION LINT (R4, hard gate PASS):
    41 file references, 27 resolve as written, 14 only after a rewrite whose target is checked to contain a number from the
    citing sentence, 0 unresolved; the 10 known misses (positive control) are all detected; 20/37 draft tables carry no source
    path. INDEPENDENT RECOMPUTE (R12): rederive_iter5.py imports only stdlib + numpy + pyarrow and reads per-item files (exp13
    per_item.csv, exp14 per_item.parquet, exp10 per_item.parquet, eval2 pooled_generations.parquet with gpt-4.1 label pools,
    exp11/exp15 per-trial tables). 136 draft numbers re-derived; 21 defective = 15.4% [10.3, 22.5] (13 distinct defects, 9
    material, 0 sign-reversed; numeric-mismatch only 6.6%). Under the same all-class definition eval1 measured 15.6% (26/167;
    the draft quotes 5.5%) and eval2 4.9%. Material defects: exp13's O failure reason is stated backwards (log energy alone
    R2 0.001 EN / 0.008 SL; O fails because it is collinear with the EN/SL cosine, rho 0.81/0.76; O over logE+count alone
    +0.89/+0.77); the 0.088/0.668/0.790/0.806 nested-R2 table is exp14 SL with each predictor added separately, not exp13
    cumulative; all exp14 A1-A4 dose/placement contrasts are Slovene (-0.186, -0.157, -0.029, 0.000), not EN; 'the critical
    band differs between siblings' is contradicted (13-24 also wins in GaMS3 at matched energy: 0.50<0.59 E2, 0.30<0.53 E3);
    exp11 trial 107 is judged 63/100 (not 10) and trial 96 is 37 REFUSED + 49 PARTIAL (not 15); the official-guard ASR gap
    (0.738 EN vs 0.103 SL) is larger, not smaller, than the refusal gap; the 7.2% guard-safe figure belongs to exp11's corrected
    arm; exp10's 'EN kappa 0.54' is the exp8 pool; exp15's 'Judge (gpt-4.1)' is the Qwen3-14B workhorse. Survives (MATCH):
    Gemma matched groups 8/8 both languages, pooled EN -0.688 / SL -0.377, rho(O) -0.96/-0.83; GaMS3 rho(O_SL) -0.90 (within
    level -0.98/-0.95); Qwen3 9/9; dose rival fails (EN .88/SL .92 vs .07/.27); exp4 RefusEU table 20/20; S5X gap +0.69 strict
    / +0.23 broad; bf16 +0.60 [0.40,0.80] vs NF4 +0.45 [0.20,0.70]; exp12 P1 -0.009. Placebos recomputed in the audit path:
    8/8 collapse; a separate pandas self-audit reproduces all 7 headline numbers and its 3 shuffled placebos collapse. NEW:
    inside the headline cell (Gemma edit EN) the workhorse vs gpt-4.1 kappa is 0.39 [0.10, 0.64] (Se .60, Sp .87), against
    a quoted pooled 0.91; the Rogan-Gladen corrected S5 gap is +0.44 vs +0.45 raw (the asymmetry survives). exp11 EN panel
    kappa 0.226. Also ships: twelve paste-ready repair blocks R1-R12 (results/report_repairs_iter5.md), the F1-F14 vs U1-U10
    ledgers (U10 filled from iteration-4 deviations), a consolidated pending-human-review list, a frozen 702-item Slovene
    gpt-4.1 re-certification draw (32 strata, est. $1.40, to be bought by the experiment executor), judge-agreement and definition-sensitivity
    tables, three figures. Not re-derived: exp6-8, exp5 T2-T11, iteration 1, eval2 flip/curve statistics (carried with paths);
    the S5X keyword gap (rule version). The unmatched c=1 grid (25-36 by +0.12 [0.00,0.27]) vs matched-energy 13-24 is reported
    UNRESOLVED; no band recommendation. Spend $0.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_5/gen_art/gen_art_evaluation_4
  output_files:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
- iteration: 5
  name: gen_art_evaluation_5
  type: evaluation
  title: How blind is an English-only refusal score
  summary: |-
    Replay-only, CPU-only measurement audit of Heretic's pinned English 33-substring keyword refusal rule (no model load, no generation, $0 spend). Every number is recomputed from per-item/per-candidate files. An independent stdlib-only rederive.py agrees on 573/573 statistics. Placebos pass 5/5: P1 label permutation, P2 within-pair language sign-flip, P3 keyword re-implementation reproducing all 8,480 stored verdicts exactly, P4 planted errors 5/5 flagged, P5 self-agreement. Path lint shows 0 failures.

    LEG A (results/blindness_per_search.csv/.json). In BOTH searches the objective floor (72 gemma-3-12b-it, 16 GaMS3) sits above the frozen rule threshold (<=10/100), so the fallback fires in both. Threshold-blind fraction is 1.00 in both: 6/6 (CP lower bound 0.54) and 37/37 (0.91) classifier-referenced; 5/5 and 6/6 judge-referenced (GaMS3: 70 judged candidates). Calibration K on C: slope 0.308/0.738, mean K-C +20.5/+15.0. K on J: 0.316/0.813, +19.6/+6.0 (reconciles the plan vs strategy numbers: they use different references). Spearman is 0.92/0.97, i.e. range compression, not mis-ranking. Gemma low-region (C<=50) blindness is 0.470, equal to its permutation chance level 0.459; GaMS3 is 0.017. The between-search prediction was falsified again (+0.006 [0, 0.019]; J-referenced -0.029). Reselection inside each pool changes the selected candidate (scoring failure; identifiers only, no recommendation).

    A4 (results/heldout_agreement.csv). On edited English the rule MISFIRES: kappa 0.021, n=490, positive rate 0.341 vs reference 0.173, FP share 0.814. On edited Slovene it is SILENT: it fires on 0/490, reference 0.439, kappa 0 by degeneracy, and the FP share is undefined (0/0), not 0.000. Corrected paper wording is in results/paste_text.md.

    LEG B (discrepancy_per_cell.csv: 177 rows; delta_lang.csv on verified pairs only). gemma_edit Delta_lang = d_SL - d_EN = -1.56 [-1.68, -1.44], decomposed as rule positive-rate shift -0.87 + reference level -0.69. PolyGuard channel gives -1.49; Rogan-Gladen -1.78. Disagreement rates are equal (McNemar p=1), but directions are opposite (sign test p=5e-29). Original checkpoints show Delta_lang of about -1.01, all rule silence. The guard channel never orders EN/SL differently (0/26 cells); unadjudicated guard items are carried as intervals. Registry (judge_sensitive_registry.json): 72 JUDGE_SENSITIVE, 6 JUDGE_ROBUST. The SL gate is unmet (kappa 0.723), and panel within-edited gates also miss in EN (0.42/0.23).

    LEG C (downstream_sensitivity.csv). For arXiv 2608.22490 (verified quote, Sec. 3) under an explicit ASSUMPTION form, a keyword-verified ablated counterfactual would misstate the SL-minus-EN cost difference by [-1.68, -0.11] refusal-rate units. The EN/SL residual-refusal ordering inverts between the keyword and reference views. A scope_caveat column travels with every row.

    Also shipped: paste_text.md (sentences + sources + draft lines replaced), configs/scope_guard.md (no placement/dose/edit analysis), three figures, audit_log.json, source_inventory.json.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_5/gen_art/gen_art_evaluation_5
  output_files:
  - eval.py
  - full_eval_out.json
  - mini_eval_out.json
  - preview_eval_out.json
  - reproducibility.md
- iteration: 5
  name: gen_art_research_2
  type: research
  title: Fixing the paper's citations and claims
  summary: >-
    Iteration-5 positioning artifact (web research only; no GPU, no model loading, no API calls, $0.00 OpenRouter spend; accessed
    2026-09-24). WHAT IT SETTLES. (1) THREE QUALIFIERS STRUCK. 'The effective region differs between the two sibling checkpoints'
    is DROPPED - falsified by this run's own placebos (DEV-named band NAMED_AND_LOST at matched energy at both levels, 0.50
    vs 0.59 and 0.30 vs 0.53; the sibling's profile predicts the anchor's 50 cells at rho -0.442, no worse than its own -0.278/-0.111;
    the two production kernels indistinguishable at matched dose, -0.029 [-0.129,+0.071] p 0.774 and 0.000 [-0.086,+0.086]
    p 1.000; iter_4/gen_art/gen_art_experiment_14). 'The band differs per language' is DROPPED - the language-label placebo
    does not collapse (English profile predicts the Slovene residual at rho -0.94, iter_4/gen_art/gen_art_experiment_13);
    the RESIDUAL still differs (strict 0.07 EN vs 0.27 SL). 'Selection blindness explains the divergent searches' is UNAVAILABLE
    - the frozen prediction was falsified (+0.006 [0.000,0.019]; judge-referenced the sign reverses to -0.029 [-0.060,-0.005],
    iter_4/gen_art/gen_art_experiment_15). (2) THE KEPT DELTA, NARROWED: at matched total removal energy AND matched layer
    count, where in depth the edit deposits its energy orders how much refusal survives, in both languages, two siblings and
    an outside family, and doubling the dose of a badly placed edit does not substitute. arXiv 2408.17003 (ICLR 2025) narrows
    it sharply - it already localises contiguous MIDDLE safety layers and already compares layer RANGES by scaling their weights;
    what survives is the energy- and count-matched removal contrast in two languages. arXiv 2607.02714's ~70pp uniform-spread
    result is a SELECTION-CRITERION comparison, so it does not conflict; the paste-ready reconciliation sentence is supplied.
    (3) THE MEASUREMENT COMPANION FINALLY HAS NEIGHBOURS (21 rows), and three shrink it: arXiv 2510.02768 already reports
    regex over-counting refusals via disclaimers ON ABLITERATED MODELS, arXiv 2512.13655 states the marker false-positive
    caveat for a Heretic-including comparison, and arXiv 2603.06594 audits judge degradation under red-teaming shift. AdvPrefix
    is RE-AIMED from the depth result to this companion. arXiv 2605.17173 CONTRADICTS the strong multilingual-judge reading
    (per-language validated judge reaches kappa 0.80-0.83; 22 of 61 configurations more vulnerable in English). (4) CONSUMERS
    QUOTED, CLAIM SOFTENED: 2608.22490 instantiates its unaligned counterfactual with abliterated checkpoints (incl. gemma-3-27b-it)
    and measures a helpfulness win rate, but it DOES check a capability-side confound (Alignment Gap Difference on P-MMEval)
    and re-derives the cost from matched from-scratch checkpoints - so this run's evidence bears on a channel it does not
    cover (residual refusal per language), not on its correctness. RefusEU's guard pair is named (Llama-Guard-3-8B + PolyGuard-Qwen).
    (5) BIBLIOGRAPHY: [19] = Safety Layers, ICLR 2025, arXiv 2408.17003 (draft says ICLR 2024, no id; v1 title reads 'OF'
    not 'IN'); [20] = 2609.04721; [21] = 2606.00926; the pruning-calibration reference is MIS-CITED (published title 'On the
    Limitations of Language-targeted Pruning', TACL vol. 14 pp. 167-192, DOI 10.1162/tacl.a.599; it finds target-language
    calibration does NOT consistently improve downstream performance); AdvPrefix is mis-placed. BibTeX-ready entries supplied.
    (6) THE '2-3 MIDDLE LAYERS' PROVENANCE is carried verbatim: the sentence exists in 2607.02714 SS3.2 as that paper's attribution
    to Arditi et al., the attribution was not found in Arditi et al. by those queries, and 2607.02714 rejects it next sentence;
    the NOT VERIFIED flag attaches to the ATTRIBUTION only. (7) SIX EVIDENCED ABSENCES (A1-A6) in the required wording 'not
    found by these queries' + row ids, each with its falsifier; 22 new search rows logged (26-47). ALSO REPORTED: two of this
    artifact's own plan assumptions were wrong on full-text inspection (2609.10594 does not measure string matching; 2607.02235
    does not contain the ~80%/<60% figures attributed to it), and 2505.19056's paired judge/guard numbers show AGREEMENT within
    4pp, not divergence. VERIFICATION: scripts/self_check.py re-checks all 36 rows (34 VERIFIED-QUOTE, 2 CARRIED, max 39 words)
    - passes; scripts/path_lint.py: 33 cited paths, all resolve; scripts/make_v2.py rebuilds both paragraphs from the dependency
    text. Deliverables in results/: positioning_positive_v2.md, positioning_negative_v2.md, positioning_diff.md, qualifier_table_v2.md,
    neighbour_table_measurement.md/.json, neighbour_table_positive_additions.md/.json, consumers.md/.json, bibliography_repairs.md/.csv,
    depth_attribution_provenance.md, evidenced_absence.md, search_log_iter5.md, carried_forward.md, dependency_deltas.md,
    claims_to_position_v2.csv (42 rows, no blanks), reconciliation_map_v2.csv, failed_and_unexecuted_v2.md, path_lint.md,
    stopping_points.md, raw/.
  workspace: >-
    /ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_5/gen_art/gen_art_research_2
  output_files:
  - research_out.json
  - reproducibility.md
</artifact_data>

<available_figures>
Each line gives the path the page must use, then the figure's title and caption.

- figures/fig_1_v0.png [render from fig_1_v0.pdf first] — "Refusal Rates Before and After Abliteration" (caption: "Refusal rates on RefusEU S5 harmful prompts ($n=280$) for all five checkpoints in English and Slovene. Abliteration transfers almost completely to Slovene for GaMS3 (orange) but fails for Gemma (blue). The community reference checkpoint (grey) shows that deeper abliteration can partially overcome the language gap. Error bars show 95\% Clopper--Pearson confidence intervals. Note: 94--95\% of edited English outputs were truncated at the 256-token generation limit.")
- figures/fig_2_v0.png [render from fig_2_v0.pdf first] — "Keyword Measurement Bias" (caption: "Keyword counter vs.\ reference judge positive rates for the Gemma-edit checkpoint on 100 verified paired prompts. The keyword counter fires on 87\% of English responses but 0\% of Slovene responses; the reference judge finds 13\% English refusal and 82\% Slovene refusal. $\Delta_{\mathrm{lang}} = -1.56$ [$-1.68$, $-1.44$]. The keyword counter is structurally blind to Slovene refusals.")
- figures/fig_3_v0.png [render from fig_3_v0.pdf first] — "Depth Placement Profile for GaMS3" (caption: "Residual Slovene refusal rate as a function of depth placement for GaMS3-12B-Instruct. Each point is a single abliteration configuration; the x-axis is a depth-placement index (lower = shallower layers). Spearman $\rho = -0.90$ ($p < 10^{-7}$). Deeper placements produce lower residual Slovene refusal. The relationship holds within both energy levels (E2: $\rho = -0.97$; E3: $\rho = -0.95$).")
</available_figures>

<data_requirements>
- Embed each dataset the views use as its own
  `<script type="application/json" id="data-..." data-source="...">` element, where
  `data-source` names the artifact and the output file it came from (for example
  `experiment_1/method_out.json`), never an absolute path. The inline script reads each one with
  `JSON.parse(document.getElementById(id).textContent)` and builds every chart, table, count and
  control from it; no number a view shows is typed into the markup by hand.
- Produce the embedded JSON with a script that reads the output files, not by copying values, so
  it is exactly what the files hold. Keep only the fields the views use.
- When a file is too large to embed whole, embed a subset chosen by a rule the page states (for
  example every failure plus a seeded random sample of the rest) and the aggregates computed from
  the full file.
- The numbers the prose states match the paper. A view may compute from the embedded data (a
  mean, a filter, a threshold swept over recorded scores), and says so; it never invents,
  interpolates, simulates or smooths a data point.
</data_requirements>

<figure_requirements>
- The page draws its own charts from the embedded data; the paper's figures are not its visuals.
  Show at most 3 of them, and only where a figure shows what the data cannot
  (the method diagram, an example rendering), never a data plot the page can draw live.
- Reference a figure as `figures/` plus its filename, exactly as listed above. The
  page and the figures folder are published together, so that relative path resolves on the live
  site and anything else breaks.
- A browser cannot draw a PDF in an image element. For a figure listed as "render from ...
  first", use the PNG of that name in `figures/` when it is already there, and
  otherwise render one there at about 200 DPI with pdftoppm or pymupdf. Renderable formats:
  .avif, .gif, .jpeg, .jpg, .png, .svg, .webp.
- Use the figure's own caption, and look at the figure before placing it.
</figure_requirements>

<page_structure>
Top to bottom:

1. HEADER: the title, the author line as the paper gives it, and the paper link as the primary
   button, labelled "Read the paper (PDF)". The other links from the links section sit beside it.
2. THE FINDING: the question and the answer in plain language, with the single number that
   carries it, and beside them the headline view, operable at once: the result drawn from the
   embedded data, the baseline shown with it, and a control over the conditions it was measured
   under.
3. HOW IT WORKS: a stepper that walks ONE real example from the data through the method's
   stages, showing at each stage what goes in, what is done to it, what comes out (the recorded
   values where the run kept them) and why. A pipeline diagram in inline SVG highlights the
   current stage; previous and next buttons, clickable stage markers and the left and right arrow
   keys move between stages.
4. EXPLORE THE EVIDENCE: two or more views over the real data, chosen from the kinds in the
   design philosophy to fit this result. At least one is an item browser: filter, search or sort
   over the real per-item records, and a detail panel that puts the selected item's input, the
   method's output and the baseline's output (or its before and after) side by side.
5. TRY IT: the live mini-demo when the method runs exactly in the page; otherwise a what-if view
   that sweeps a threshold or parameter over the recorded scores and recomputes the metrics live.
   Leave it out only when neither would be honest for this result, and say why in your summary.
6. WHERE IT FAILS: the failure cases from the data one control away, then what the paper says it
   does not show.
7. FOOTER: every link from the links section again, a data provenance list naming the artifact
   file behind each view, the glossary of every term with a tooltip, and the citation if the
   paper carries one.

A compact section navigation marks where the reader currently is. Each view opens with the
question it answers and ends with a takeaway sentence that updates with the selection.
</page_structure>

<interaction_requirements>
- Controls are real form controls or ARIA widgets: a range input with its current value printed
  beside it, a select, checkboxes, a radio group or tab list, buttons with aria-pressed. Each one
  changes a view without a page jump, and the view's counts and takeaway sentence change with it.
- Charts are inline SVG you generate, or canvas when there are thousands of marks: labelled axes
  with units, bars that start at zero, the baseline always shown, a legend when there is more than
  one series, and values printed at the precision the source has. Every mark shows its record on
  hover, on keyboard focus and on tap.
- Tooltips: each term trigger is a button with the term as its text, showing its definition on
  hover, on keyboard focus and on tap, dismissed by Escape and by tapping elsewhere, and exposed to
  assistive technology through aria-describedby. Define each term from the paper's own wording.
  A mouse click fires hover, focus and click in turn, and a tap fires focus and click, so a click
  handler that toggles closes the definition the moment it opened: every one of those events
  OPENS the tooltip, and only Escape, a click or tap elsewhere, or leaving the trigger closes it.
- Stepper: the current stage is announced through an aria-live region, the buttons disable at
  the ends, and the current stage marker carries aria-current.
- The page works with no network at all and logs no error or warning to the browser console.
</interaction_requirements>

<technical_requirements>
- ONE file: all CSS in a style element and all JavaScript in a script element, both inline in
  `interactive.html`, beside the data elements. No framework, no external script,
  stylesheet, web font or analytics. The only files the page may point at are the figures listed
  above.
- Plain modern JavaScript, no build step.
- Formulas use HTML sub and sup elements or inline MathML. TeX notation such as `^`, `_` or
  `\frac` must not reach the page.
- System font stack only. Light theme.
- Responsive from a 360px phone to a wide desktop with no horizontal page scroll; wide tables and
  charts scroll inside their own container or reflow, and charts redraw to their container width.
- Honour prefers-reduced-motion.
- Keyboard-navigable in a sensible Tab order with a visible focus ring and a skip link to the
  main content.
- Semantic HTML: one top-level heading, headings that descend without skipping, landmark
  elements, and alt text on every image that says what it shows.
- Keep the whole file under 3 MB.
</technical_requirements>

<page_gate>
When you finish, the page is loaded in a headless browser and sent back to you if its script
throws an error; if it has no `application/json` data element that its inline script reads by
id; if it shows more than 3 static images; or if, once its script has run, it
draws fewer than 2 charts (svg or canvas) or offers fewer than 3
controls. It is also sent back if `index.html` is present and does not link to
`interactive.html`.
</page_gate>

<writing_register>
Write in the register of the field's best papers (the paper this page teaches, which was written to them), not in the register of a language
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
Use these URLs VERBATIM. Do not shorten them, do not make any of them relative, and do not
compose one of your own.

- The paper PDF: https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@fork/run_A3Dbh1J6RI3O/paper.pdf
  Label it "Read the paper (PDF)"; it is the page's primary call to action.
- The code repository: https://github.com/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses/tree/fork/run_A3Dbh1J6RI3O
- The full research report, every experiment and every table: https://cdn.jsdelivr.net/gh/ai-inventor-papers/ai-invention-beaa2a-what-english-tuned-abliteration-misses@fork/run_A3Dbh1J6RI3O/report.pdf
  Label it "Read the full research report" and place it beside the paper link.

Each carries the branch this run publishes to, and they begin resolving only after this run
finishes publishing, so do NOT try to open or verify them.
</links>

<presentation_link>
When `index.html` is present, it is what a reader lands on, so your page is found only
if it links there. In `index.html`, add a link whose href is exactly
`interactive.html`, labelled "Explore the interactive demo", beside the paper link in the
hero and again beside it in the footer, styled like the links next to it; a link to it that
already reads differently gets relabelled. This one link is relative, unlike the URLs above,
because both pages are published into the same folder. Change nothing else in
`index.html`.
</presentation_link>

FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read `paper.tex` end to end and list `figures/`. Write down
the title, the author line, the question and the finding, the method's stages in order, every
technical term with the sentence that defines it, every headline number with the sentence it
appears in, and the limitations.
TODO 2. Open the output files in <artifact_data>, the `mini_` or `preview_` variant first. Write
down which files hold per-item records (inputs, outputs, scores, verdicts), which hold
per-condition, per-model or per-setting results, which hold the values a method stage recorded,
their fields, and how many rows each has. Note the ones that carry the paper's headline
numbers.
TODO 3. Design the page before writing it. For each view in the page_structure, write down the
reader's question, the file and fields it draws, the control, the chart, and the takeaway
sentence. Pick the views that make the finding VISIBLE (the gap between method and baseline, the
cases where it fails, the one example that shows the mechanism), not ones that restate a number
the prose already gives.
TODO 4. Write a script that reads those output files and writes the JSON each view embeds, then
check that every headline number it produces matches the paper.
TODO 5. Render the PNGs of the figures you will show (at most 3) into
`figures/`, then LOOK at each one.
TODO 6. Write `interactive.html` following the data_requirements, page_structure,
interaction_requirements and technical_requirements sections above.
TODO 7. VERIFY THE NUMBERS: every number in the prose appears in `paper.tex` with the
same meaning, and every embedded value traces to the output file its data-source names. Delete or
fix anything you cannot trace.
TODO 8. VERIFY THE PAGE: confirm it has no external script, stylesheet or font reference; that
every image path starts with `figures/` and names a file in `figures/`;
and that the paper, repository and report links are character-for-character the URLs in the
links section.
TODO 9. LINK YOUR PAGE from `index.html` when it is present, as the presentation_link
section says, then open `index.html` and confirm the link is in its hero and its footer
and that nothing else on that page changed.
TODO 10. OPERATE THE PAGE in a headless browser. `chromium-headless-shell` is already installed,
the same browser the finished page is checked in: drive it with Playwright (`uv pip install
playwright` in a scratch virtual environment, then launch Chromium with `executable_path` set
to the output of `which chromium-headless-shell`, with no `playwright install`). Only if that
command finds nothing, run `playwright install --with-deps chromium` instead. Open the page at
390px and 1440px wide, operate every control, hover and tap chart marks, step the stepper, select
items in the browser, click a term and confirm its definition is STILL showing after the click,
and confirm each view and its takeaway sentence change as they should. Use real clicks (the
browser's click, not a dispatched event), since that is what a reader's mouse and finger
produce. Screenshot each state, read the screenshots, and confirm the console shows no errors
and the page never scrolls sideways. Fix anything broken, cramped, overlapping, empty or cut
off, then operate it again.
</todos>

---

Output the result as JSON to: `./.terminal_claude_agent_struct_out.json`

JSON Schema:
```json
{
  "$defs": {
    "InteractivePaperExpectedFiles": {
      "description": "All expected output files from interactive-page generation.",
      "properties": {
        "page_html_path": {
          "description": "Path to the single self-contained HTML page. Example: 'interactive.html'",
          "title": "Page Html Path",
          "type": "string"
        }
      },
      "required": [
        "page_html_path"
      ],
      "title": "InteractivePaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Interactive paper page: structured output from gen_html_demo.",
  "properties": {
    "summary": {
      "description": "Brief summary of the page you built: each view and control, the question it answers, and the artifact output file its data came from.",
      "maxLength": 5000,
      "minLength": 300,
      "title": "Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/InteractivePaperExpectedFiles",
      "description": "All output files you created. Must include interactive.html."
    }
  },
  "required": [
    "summary",
    "out_expected_files"
  ],
  "title": "InteractivePaper",
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

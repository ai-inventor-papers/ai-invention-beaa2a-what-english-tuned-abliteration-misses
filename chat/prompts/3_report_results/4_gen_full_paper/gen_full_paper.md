# gen_full_paper — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_Fapgmt6JWbcD` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim record of every prompt the AI Inventor pipeline gave this agent — system-user, human-user and skill-input — in the order they landed. Nothing truncated.

## Task: `gen_full_paper` (terminal_claude_agent)

### [1] SYSTEM-USER prompt · 2026-09-25 06:27:18 UTC

````
<research_methodology>
Write like an experienced academic. Reviewers judge both the science and the writing.

- Claims must be proportional to evidence. Choose verbs carefully — "demonstrate," "observe," and "hypothesize" mean different things.
- Every result needs: what was measured, on what data, the numbers, and what they mean.
- Methodology must be specific enough to reproduce. Section placement follows <paper_structure> below.
- State limitations honestly. Avoid both overclaiming and excessive hedging.
</research_methodology>

<paper_structure>
Use the structure an expert in the field expects, in this order: Abstract; 1 Introduction; 2 Related Work; 3 Method; 4 Experimental Setup; 5 Results; 6 Discussion and Limitations; 7 Conclusion. Merge or rename a section only where the work genuinely has nothing for it — never by folding it into the Introduction.

- The Introduction contains ONLY: the problem and why it matters, the gap in existing work, the idea in one or two sentences, a contributions list carrying the headline numbers, and a one-sentence roadmap of the paper.
- NO literature survey and NO method details in the Introduction. Prior work goes to Related Work, how the method works goes to Method.
- Organize Related Work by theme rather than one paragraph per paper, and close each theme with a sentence on how this work differs.
- Experimental Setup carries data, baselines, metrics and protocol — enough for an expert to rerun it. Results carries findings, not setup.
</paper_structure>

<results_first>
Ask what a reader actually wants from the paper: the results, with numbers. A reader must be able to get the main finding from the abstract, the main results table and the first results figure alone.

- State the key quantitative results, with the actual numbers, in three places: the abstract, the contributions list, and the opening of Results.
- Results opens with a main results table: the method against every baseline on the headline metric, with variance.
- Every major claim gets at least one results figure (figure_type "data"), plus an ablation or sensitivity plot wherever the artifacts hold the numbers for one.
- Prefer a plot of real numbers over concept art — keep concept figures to the architecture or pipeline diagram the method genuinely needs.
- Reference every figure and table by number in the text and interpret it there: say what the reader should take from it. Never drop one in unexplained.
</results_first>

<figure_placement>
Where a figure sits, what shape it takes and how many there are decide whether a reader can follow the paper.

- Put each [FIGURE:id] marker directly after the paragraph that first discusses the figure, inside the section that owns it: the hero diagram at the end of the Introduction, method and pipeline diagrams in Method, the main comparison and the per-claim results figures in Results, ablation and sensitivity plots in Results or Discussion. Never place a figure in the Abstract, Related Work or Conclusion.
- Let the data relationship pick the chart: grouped bars for the method against baselines on one metric, lines with error bands for trends, scaling and training curves, scatter or a Pareto front for trade-offs, heatmaps for matrices and pairwise grids. A handful of numbers is a table, not a figure. Use multiple panels only when they share axes and one takeaway.
- Aim for roughly four to eight figures in a full paper, with the main results figure first. Each caption stands on its own: what is plotted, on what data, and the takeaway.
</figure_placement>

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
Your workspace: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/4_gen_paper_repo/_4_assemble_paper/paper/workspace`

CRITICAL: Every file you create, write, or save MUST be inside this workspace directory (subdirectories OK). You MUST NOT write files anywhere outside this path — external paths are READ-ONLY. Use absolute paths for all file operations.

EVERY file write MUST start with `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/4_gen_paper_repo/_4_assemble_paper/paper/workspace/`:
GOOD: `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/4_gen_paper_repo/_4_assemble_paper/paper/workspace/file.py`, `/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/4_gen_paper_repo/_4_assemble_paper/paper/workspace/results/out.json`
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
Typeset <paper_draft> as LaTeX with BibTeX, insert <available_figures>, and compile it to PDF.
</task>

<tool_use>
Maximize parallel tool calls. Parallelize independent operations, only sequentialize dependencies.
- Multiple searches/fetches on different topics → parallel in one turn
- Search then fetch results → sequential (need URLs first)
</tool_use>

<publishable_paper_rules>
This is the PUBLISHABLE PAPER. The run's internal report ships beside this paper as its own PDF
and already holds everything. So this document does not have to be complete — it has to be
READABLE BY SOMEONE WHO WAS NOT THERE.

- ONE ARGUMENT. Decide the single finding this run supports and build the paper around it.
  Everything that does not serve it is cut, not shrunk.
- LEAD WITH THE STRONGEST POSITIVE FINDING THE ROWS SUPPORT, from whichever round produced it.
  Abstract, Introduction and Results open on the best result the tables actually carry; the
  negative and null results are the context that bounds it, not the opening. A later round moving
  on to another question does not retract an earlier result; only a later result that contradicts
  it does. Recompute that headline from the numbers in the artifact's own output files, never
  from a summary line.
- STRUCTURED BY IDEA, NEVER BY ITERATION. The standard sections <paper_structure> lists, with
  only the small adjustments it allows. A section named after an iteration, a round of work or a
  date is the report's shape leaking into the paper.
- NO PROCESS. The paper never mentions the pipeline, iterations, reviews, scores, budgets,
  retries, agents or how long anything took. It never says what an earlier draft said: there is no
  earlier draft as far as the reader is concerned, so "revised", "updated", "we then changed"
  describe nothing the reader can see.
- THE METHOD AS IT FINALLY STANDS. Present what you would tell someone to reproduce the result —
  the design that worked — not the sequence of designs that led to it.
- DEAD ENDS ONLY WHERE THEY INFORM. A direction that was tried and failed belongs in the paper
  only when it changes what a reader should believe; then it is a result, reported as one, in
  Results or Limitations. Otherwise it stays in the report.
- HONEST ABOUT SCOPE. Every claim carries what supports it. What the evidence does not reach goes
  in Limitations, plainly, rather than being softened everywhere.
- SELF-CONTAINED. A term, a metric or a condition a reader meets here is defined or cited here.
  Never a pointer to the report, and never a run-internal name or code.
- NO PIPELINE INTERNALS. Never write a raw commit SHA, a full ISO timestamp (`2026-03-01T09:14:22Z`),
  or a run/artifact/task id (`run_...`, `art_...`) into the prose — they identify nothing to a
  reader. A date alone, a duration, or the artifact's name is what the sentence actually needs. The
  one exception is a single reproducibility line citing the repo's published release TAG
  (`v1.4.0`), never a SHA.
</publishable_paper_rules>

<paper_structure>
The paper's default sections are:
Abstract, Introduction, Related Work, Method, Results, Discussion, Limitations, Conclusion, then the numbered references. The draft step may have adjusted that list slightly where most of the field's papers (their outlines are at
the end of <style_exemplars>) share an adjustment: a section renamed to the field's word, two
merged, one split, one moved, or a section the field treats as standard added. Typeset the
sections as <paper_draft> names and orders them; a heading that differs from the default list is
a decision, not a mistake to correct. These always stay, whatever the draft did, because later
steps read them:
- Abstract. The draft's own `abstract` field, typeset as the LaTeX abstract.
- Introduction, first after the abstract. Figure 1, the flagship, is marked at its end, and the
  LaTeX step places every figure where its marker sits.
- Limitations, under that word, as a section or a titled subsection of Discussion. The project
  site copies it into its Limitations panel, and <publishable_paper_rules> sends everything the
  evidence does not reach there.
- The numbered references, last. The LaTeX step builds `references.bib` from them.
The paper also always has a part that describes the method and a part that reports the results,
because the project site presents both; those two may carry the name the field gives them.
</paper_structure>

<paper_draft>
THE PAPER. Which single finding it argues, how it is structured, which figures it shows and where
each one goes were all decided before you were called; this block is the result. Typeset it. Do
not restructure it, do not re-select what it covers, and do not add sections it does not have.
Rewording for the register the style blocks below describe is in scope; changing what the paper
says is not.

title: What English-Tuned Abliteration Misses in Slovene
abstract: >-
  Abliteration removes refusal behaviour from language models by orthogonalising weights against a refusal direction extracted
  from English contrast pairs. The optimiser verifies candidates with an English keyword counter. We evaluate this pipeline
  on two 12B-parameter models---Gemma-3-12B-IT and its Slovene continual-pretraining variant GaMS3-12B-Instruct---using the
  RefusEU benchmark. The edit transfers almost completely to GaMS3, reducing Slovene refusal from 87\% to 0\%, but largely
  fails on Gemma, where Slovene refusal drops only from 94\% to 74\%. The keyword counter that verified both edits is structurally
  silent on Slovene text: across 100 verified Gemma-edit pairs, it fires on 87\% of English responses but on 0\% of Slovene
  responses, while a reference judge finds 82\% Slovene refusal ($\Delta_{\mathrm{lang}} = -1.56$, 95\% CI $[-1.68, -1.44]$).
  Among all optimiser candidates, every one the reference judge places below the selection threshold is invisible to the keyword
  objective (threshold-blind fraction 1.0, 6/6 Gemma, 37/37 GaMS3). Keyword-verified abliterated checkpoints are therefore
  not valid language-neutral references for refusal evaluation. In a secondary analysis, depth placement of edits across layers
  correlates strongly with residual refusal within each model but does not transfer across architectures. These results are
  preliminary: the Slovene judge does not meet the certification gate ($\kappa = 0.72$ against $0.80$ required), and 94--95\%
  of edited English outputs were truncated at the 256-token generation limit.
paper_text: "\\section{Introduction}\n\nRefusal---the learned tendency of an instruction-tuned language model to decline harmful\
  \ requests---is a central component of alignment \\cite{Inan2023}. Abliteration removes this behaviour by identifying a\
  \ ``refusal direction'' in activation space and orthogonalising the model's weight matrices against it \\cite{Arditi2024}.\
  \ The refusal direction is extracted from English contrast pairs, and the optimiser (typically Heretic, a TPE-based search\
  \ \\cite{Akiba2019}) evaluates candidates using an English keyword counter. This pipeline has been shown to effectively\
  \ suppress refusal in English, but its cross-lingual behaviour has received little attention.\n\nThe question is practically\
  \ important. Open-weight models are increasingly adapted to non-English languages through continual pretraining \\cite{Vres2026},\
  \ and abliterated checkpoints are widely redistributed as references for downstream safety evaluation. If the English keyword\
  \ counter used to verify these checkpoints is structurally blind to non-English refusals, the checkpoints cannot serve as\
  \ language-neutral references---regardless of whether the underlying edit transfers.\n\nWe study this question concretely\
  \ for Slovene, a mid-resource language with approximately two million speakers. We evaluate two 12B-parameter models: \\\
  texttt{google/gemma-3-12b-it} \\cite{Kamath2025} and \\texttt{cjvt/GaMS3-12B-Instruct} \\cite{Vres2026}, a variant of the\
  \ same architecture continually pretrained on Slovene. Both models are evaluated before and after Heretic-optimised abliteration,\
  \ across English and Slovene prompts from the RefusEU benchmark \\cite{Krasnodebska2026}. A fifth checkpoint from the community\
  \ (an independently abliterated Gemma) provides a reference point. \n\nThe central finding is an asymmetry: the edit transfers\
  \ almost completely to GaMS3 (Slovene refusal drops from 87\\% to 0\\%) but fails on Gemma (Slovene refusal drops only from\
  \ 94\\% to 74\\%). The keyword counter that verified both checkpoints detected none of this difference.\n\n\\paragraph{Summary\
  \ of Contributions.}\n\\begin{itemize}\n\\item \\textbf{Keyword measurement bias.} The English keyword counter used by Heretic\
  \ is silent on Slovene text: on 100 verified Gemma-edit pairs it fires on 87\\% of English responses but 0\\% of Slovene\
  \ responses, while the reference judge finds 82\\% Slovene refusal ($\\Delta_{\\mathrm{lang}} = -1.56$, 95\\% CI $[-1.68,\
  \ -1.44]$). Among all optimiser candidates, every one the reference judge places below the selection threshold is invisible\
  \ to the keyword objective (threshold-blind fraction 1.0; 6/6 Gemma, 37/37 GaMS3). Keyword-verified abliterated checkpoints\
  \ are therefore not valid language-neutral references for refusal evaluation (Section~\\ref{sec:keyword-bias}).  \n\\item\
  \ \\textbf{Depth placement correlates with residual refusal within a model but not across models.} In the Gemma causal write\
  \ profile, depth placement correlates with residual refusal at confirmation-level Spearman $\\rho = -0.96$ (English) and\
  \ $\\rho = -0.83$ (Slovene). In GaMS3, the correlation is $\\rho = -0.90$ (Slovene). However, these depth profiles do not\
  \ transfer across architectures: the cross-model Spearman is $-0.009$ ($n = 21$, $p = 0.16$; Section~\\ref{sec:placement}).\
  \   \n\\end{itemize}\n\nAll Slovene results carry a measurement caveat: the workhorse judge (Qwen3-14B) does not meet the\
  \ $\\kappa \\geq 0.80$ certification gate for Slovene (unweighted $\\kappa = 0.72$; Section~\\ref{sec:limitations}).\n\n\
  \\section{Related Work}\n\nRepresentation engineering \\cite{Zou2023} showed that high-level concepts, including honesty\
  \ and harmfulness, are linearly represented in transformer activations. \\citet{Arditi2024} extended this observation to\
  \ refusal, demonstrating that a single direction in activation space mediates the refusal decision and that orthogonalising\
  \ weights against this direction---abliteration---removes refusal behaviour. \\citet{Wei2024} studied the brittleness of\
  \ safety alignment under pruning and low-rank modifications, finding that aligned behaviour is concentrated in a small number\
  \ of parameters. These results establish that refusal is geometrically localised, but none of the studies above evaluated\
  \ cross-lingual transfer.\n\nMultilingual safety evaluation has advanced through benchmarks such as RefusEU \\cite{Krasnodebska2026},\
  \ which provides paired harmful and benign prompts in multiple European languages. Safety moderation tools including Llama\
  \ Guard \\cite{Inan2023} and PolyGuard \\cite{Kumar2025} provide multilingual refusal classification. \\citet{Marks2023}\
  \ demonstrated that linear structure in representations generalises across domains, suggesting that refusal directions might\
  \ transfer across languages---a hypothesis our results partially support for GaMS3 but not for Gemma.\n\nJailbreaking research\
  \ \\cite{Zou2023a, Shen2023, Mehrotra2023} has shown that aligned models can be attacked through adversarial suffixes, prompt\
  \ injection, and automated red-teaming. \\citet{Mazeika2024} introduced HarmBench as a standardised evaluation framework.\
  \ Abliteration differs from these attack vectors in that it modifies the model's weights rather than its inputs, producing\
  \ a permanent and deterministic change.\n\nGaMS3 \\cite{Vres2026} is a continual pretraining of Gemma-3 on 140B tokens of\
  \ Slovene, English, and related South Slavic languages, followed by supervised fine-tuning on over 200K instruction examples.\
  \ GlotLID \\cite{Kargaran2023} provides the language identification we use to verify output language consistency.\n\n\\\
  section{Method}\n\n\\subsection{Models and Checkpoints}\n\nWe study five checkpoints, all loaded in 4-bit NF4 quantisation\
  \ throughout:\n\\begin{enumerate}\n\\item \\textbf{Gemma-orig}: \\texttt{google/gemma-3-12b-it} \\cite{Kamath2025}, the\
  \ English-centric instruction-tuned baseline.\n\\item \\textbf{Gemma-edit}: Gemma-orig after Heretic-optimised abliteration\
  \ (116 TPE trials, keyword objective). No candidate reached the primary selection rule ($\\leq 10$ keyword refusals out\
  \ of 100); the fallback rule selected the candidate with the lowest keyword count (72/100).\n\\item \\textbf{GaMS3-orig}:\
  \ \\texttt{cjvt/GaMS3-12B-Instruct} \\cite{Vres2026}, continually pretrained on Slovene.\n\\item \\textbf{GaMS3-edit}: GaMS3-orig\
  \ after Heretic-optimised abliteration (116 TPE trials, keyword objective). The fallback rule selected the candidate with\
  \ the lowest keyword count (16/100).\n\\item \\textbf{Community-ref}: An independently abliterated Gemma checkpoint from\
  \ the community, included as a reference point.\n\\end{enumerate}\n\n\\subsection{Heretic Optimisation}\n\nHeretic uses\
  \ tree-structured Parzen estimation (TPE; \\cite{Akiba2019}) to search over abliteration hyperparameters---which layers\
  \ to edit, the scaling coefficient, and the refusal-direction extraction method \\cite{Arditi2024}. It optimises two objectives:\
  \ an English keyword refusal rate (the fraction of 100 in-loop prompts whose responses contain English refusal keywords)\
  \ and the KL divergence between the edited and original model on a calibration set. The selection rule is: minimise KL subject\
  \ to refusals $\\leq 10/100$; if no candidate satisfies this constraint, fall back to minimising refusals subject to KL\
  \ $\\leq 1.0$. \n\nBoth searches (Gemma and GaMS3) fell to the fallback branch, meaning no candidate achieved $\\leq 10$\
  \ keyword refusals out of 100 in-loop prompts. The keyword objective floor (the minimum keyword refusal count across all\
  \ 116 candidates) was 72 for Gemma and 16 for GaMS3.\n\n\\subsection{Evaluation Protocol}\n\nAll checkpoints are evaluated\
  \ on the RefusEU benchmark \\cite{Krasnodebska2026}, which provides 280 harmful prompts (S5 split) and 150 benign prompts\
  \ (S6 split), each in English and Slovene. Each prompt produces a single greedy-decoded response (temperature 0, max 256\
  \ tokens). Responses are classified into \\{refused, partial, complied\\} by a local Qwen3-14B judge. \n\nRefusal rate is\
  \ the fraction of harmful-prompt responses classified as refused. Attack success rate (ASR) is computed over the subset\
  \ of responses where both safety guards (Llama Guard 3 \\cite{Inan2023} and PolyGuard \\cite{Kumar2025}) agree on a label,\
  \ excluding disagreements. Over-refusal rate is the fraction of benign-prompt responses classified as refused. Language\
  \ consistency is verified by GlotLID \\cite{Kargaran2023}.\n\n\\paragraph{Generation truncation.} The 256-token generation\
  \ limit truncates a large share of edited English outputs: 95.4\\% of Gemma-edit EN and 94.2\\% of GaMS3-edit EN responses\
  \ are truncated, compared with 96.7\\% for Gemma-orig EN and 26.3\\% for GaMS3-orig EN. Slovene truncation rates are lower\
  \ (69.8\\% for Gemma-edit SL, 92.1\\% for GaMS3-edit SL). The high English truncation rate means that many compliant English\
  \ responses were cut short, and the judge classified their refusal status from incomplete text.\n\n\\paragraph{Judge certification.}\
  \ The Qwen3-14B workhorse judge was calibrated against GPT-4.1 labels on a held-out panel. English certification passed:\
  \ unweighted $\\kappa = 0.86$ $[0.77, 0.92]$, gate met. Slovene certification failed: unweighted $\\kappa = 0.72$ $[0.63,\
  \ 0.81]$, below the $0.80$ threshold. All Slovene absolute rates therefore carry a measurement caveat. Relative comparisons\
  \ within Slovene (e.g., orig vs.\\ edit) are less affected, since the judge bias is approximately constant across checkpoints.\n\
  \n\\section{Results}\n\\label{sec:results}\n\n\\subsection{Refusal Suppression Across Languages}\n\nTable~\\ref{tab:headline}\
  \ reports the main refusal evaluation. Abliteration produces dramatically different cross-lingual outcomes for the two models.\n\
  \n\\begin{table}[h]\n\\centering\n\\small\n\\caption{Refusal rate and attack success rate (ASR) on RefusEU S5 harmful prompts\
  \ ($n=280$ per cell), with 95\\% Clopper--Pearson confidence intervals. Over-refusal is on S6 benign prompts ($n=150$).\
  \ Edited English outputs are truncated at 256 tokens in 94--95\\% of cases (see Method).}\n\\label{tab:headline}\n\\begin{tabular}{llccc}\n\
  \\toprule\nCheckpoint & Lang & Refusal & ASR & Over-refusal \\\\\n\\midrule\nGaMS3-orig & EN & .986 [.971,.996] & .015 [.004,.030]\
  \ & .100 [.053,.153] \\\\\nGaMS3-orig & SL & .871 [.829,.907] & .012 [.000,.027] & .107 [.060,.160] \\\\\nGaMS3-edit & EN\
  \ & .014 [.004,.029] & .982 [.964,.996] & .000 [.000,.000] \\\\\nGaMS3-edit & SL & .000 [.000,.000] & .972 [.952,.992] &\
  \ .000 [.000,.000] \\\\\n\\midrule\nGemma-orig & EN & .971 [.950,.989] & .026 [.007,.049] & .087 [.040,.133] \\\\\nGemma-orig\
  \ & SL & .939 [.911,.964] & .016 [.004,.031] & .327 [.253,.400] \\\\\nGemma-edit & EN & .287 [.233,.341] & .738 [.681,.794]\
  \ & .013 [.000,.033] \\\\\nGemma-edit & SL & .739 [.686,.786] & .103 [.067,.143] & .193 [.133,.260] \\\\\n\\midrule\nCommunity-ref\
  \ & EN & .054 [.029,.082] & 1.00 [1.00,1.00] & .007 [.000,.020] \\\\\nCommunity-ref & SL & .114 [.079,.154] & .870 [.822,.909]\
  \ & .027 [.007,.053] \\\\\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\n[FIGURE:fig_1]\n\n\\textbf{GaMS3}: Abliteration\
  \ removes refusal almost completely in both languages. English refusal drops from 98.6\\% to 1.4\\% (McNemar $p < 10^{-81}$);\
  \ Slovene refusal drops from 87.1\\% to 0.0\\% ($p < 10^{-73}$). Over-refusal also drops to zero in both languages. The\
  \ edit transfers fully.\n\n\\textbf{Gemma}: Abliteration partially suppresses English refusal (97.1\\% $\\to$ 28.7\\%, $p\
  \ < 10^{-57}$) but barely affects Slovene (93.9\\% $\\to$ 73.9\\%, $p < 10^{-15}$). The English ASR reaches only 73.8\\\
  %, far below GaMS3's 98.2\\%. In Slovene, Gemma-edit's ASR is 10.3\\%---the edit scarcely works.\n\n\\textbf{Community reference}:\
  \ The independently abliterated Gemma achieves much lower refusal in both English (5.4\\%) and Slovene (11.4\\%), suggesting\
  \ that a more thorough abliteration procedure can reach deeper into the refusal mechanism even for Gemma. \n\nThe keyword\
  \ counter that verified both the Gemma-edit and GaMS3-edit checkpoints did not detect this divergence. Both checkpoints\
  \ were selected by the same fallback rule (minimise keyword refusals), and neither reached the primary gate. The next section\
  \ quantifies why.\n\n\\subsection{Keyword Measurement Bias}\n\\label{sec:keyword-bias}\n\nThe keyword refusal counter that\
  \ Heretic uses as its primary objective counts English refusal phrases (``I cannot'', ``I'm sorry'', etc.) in model responses.\
  \ This counter is structurally unable to detect Slovene refusals, which are expressed in Slovene. The consequence is not\
  \ merely that the optimiser misses a signal---it is that the verified checkpoints cannot serve as language-neutral references\
  \ for refusal evaluation.\n\nWe quantify the bias using the language-gap score $\\Delta_{\\mathrm{lang}}$, defined as the\
  \ difference between the keyword-measured refusal difference (English minus Slovene) and the reference-judge-measured refusal\
  \ difference. For the Gemma-edit checkpoint on the S5X prompt set ($n=100$ verified paired prompts, Qwen reference channel):\
  \ the keyword counter fires on 87\\% of English responses but on 0\\% of Slovene responses, while the reference judge finds\
  \ 13\\% English refusal and 82\\% Slovene refusal. \n\n\\begin{equation}\n\\Delta_{\\mathrm{lang}} = -1.56 \\quad [95\\\
  % \\text{ CI: } -1.68, -1.44]\n\\end{equation}\n\nThis decomposes into two components. The \\textbf{silence component} ($-0.87$)\
  \ reflects the keyword counter's inability to detect any Slovene refusals (keyword positive rate in Slovene: 0.0). The \\\
  textbf{reference component} ($-0.69$) reflects the actual difference in refusal rates between languages as measured by the\
  \ judge.\n\n[FIGURE:fig_2]\n\nThe \\textbf{threshold-blind fraction} (TBF) quantifies the consequence for optimiser selection.\
  \ TBF is the share of candidates that the reference judge places at or below the selection threshold ($\\leq 10/100$ refusals)\
  \ but the keyword objective places above it. In both searches, TBF $= 1.0$: 6 out of 6 eligible Gemma candidates and 37\
  \ out of 37 eligible GaMS3 candidates are invisible to the keyword objective. Every candidate that a reference judge would\
  \ consider well-abliterated was missed by the keyword counter. \n\nTable~\\ref{tab:keyword} summarises the keyword counter's\
  \ behaviour across four evaluation conditions, computed on held-out prompts from both Heretic searches (first-100-token\
  \ window; $n$ ranges from 70 to 490 depending on condition).\n\n\\begin{table}[h]\n\\centering\n\\small\n\\caption{Keyword\
  \ refusal counter vs.\\ judge reference on held-out prompts. The keyword counter correctly identifies English refusals in\
  \ unedited models (CONCORDANT) but produces zero positives on Slovene text (SILENT) and misfires on edited English text\
  \ (MISFIRING, FP share 0.81).}\n\\label{tab:keyword}\n\\begin{tabular}{lccccl}\n\\toprule\nCondition & $n$ & $\\kappa$ &\
  \ KW pos.\\ rate & Ref.\\ base rate & Mechanism \\\\\n\\midrule\nOriginal EN & 70 & 0.20 & 0.94 & 0.94 & CONCORDANT \\\\\
  \nOriginal SL & 70 & 0.00 & 0.00 & 0.96 & SILENT \\\\\nEdited EN & 490 & 0.02 & 0.34 & 0.17 & MISFIRING \\\\\nEdited SL\
  \ & 490 & 0.00 & 0.00 & 0.44 & SILENT \\\\\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\nThe keyword counter is concordant\
  \ with the judge only for unedited English models. On Slovene text, it produces zero positives regardless of whether the\
  \ model actually refuses (0/490 held-out Slovene responses flagged). On edited English text, 81.4\\% of its refusal detections\
  \ are false positives (keyword fragments appearing in compliant responses), and its $\\kappa$ against the judge is 0.02.\n\
  \n\\subsection{Depth Placement vs.\\ Dose}\n\\label{sec:placement}\n\nAbliteration edits a subset of the model's transformer\
  \ layers. The Heretic optimiser treats which layers to edit and the scaling coefficient as free parameters, producing candidates\
  \ that vary in both \\emph{where} the edit energy is placed (depth placement) and \\emph{how much} total energy is applied\
  \ (dose, measured as the Frobenius norm of the weight perturbation). We ask whether placement matters independently of dose.\n\
  \n\\paragraph{Causal write profiles.} For each model, we construct a \\emph{causal write profile} by applying single-layer\
  \ abliteration edits to each of the model's transformer layers in isolation, then measuring the residual refusal rate. This\
  \ profile reveals which layers, when edited alone, are most effective at suppressing refusal.  \n\nFor Gemma, the confirmation-level\
  \ Spearman correlations between the depth-placement index and residual refusal are $\\rho = -0.96$ for English and $\\rho\
  \ = -0.83$ for Slovene ($n = 18$ weight cells). The English and Slovene profiles are correlated at $\\rho = 0.59$. For GaMS3,\
  \ the profile is analysed through a factorial design with two energy levels (E2 and E3) and ten placement configurations.\
  \ The Spearman correlation between depth-placement index and residual Slovene refusal is $\\rho = -0.90$ ($p < 10^{-7}$),\
  \ holding within both energy levels ($\\rho = -0.97$ at E2, $\\rho = -0.95$ at E3).\n\n\\paragraph{Matched-energy contrasts.}\
  \ To isolate placement from dose, we construct matched pairs of abliteration configurations that apply the same total energy\
  \ across the same number of layers, but differ in which layers are edited.\n\nAcross 42 matched pairs in the Gemma experiment\
  \ (energy-matched, varying layer identity), placements targeting depth-peak layers leave lower Slovene refusal than off-peak\
  \ placements of equal energy (mean $\\Delta_{\\mathrm{SL}} = 0.12$, 95\\% CI $[0.07, 0.18]$). English refusal is approximately\
  \ invariant to placement at matched energy (mean $\\Delta_{\\mathrm{EN}} = 0.006$). Within a model, placement is a stronger\
  \ predictor of Slovene refusal than dose. \n\n[FIGURE:fig_3]\n\n\\paragraph{Cross-model transfer failure.} We test whether\
  \ the depth placement that works best for one model predicts what will work for another, using single-layer write profiles\
  \ from Gemma and an independently constructed profile from Qwen3-8B. The activation-space depth index fails cross-model\
  \ prediction entirely: Spearman $\\rho = -0.009$ over 21 matched rows (item-bootstrap 95\\% CI $[-0.13, 0.19]$, permutation\
  \ $p = 0.16$). The depth at which abliteration is most effective is model-specific. \n\n\\section{Discussion}\n\n\\paragraph{Evaluation\
  \ validity.} The keyword measurement bias is the central finding of this study. Abliterated checkpoints verified only by\
  \ an English keyword counter carry no information about non-English refusal behaviour. The keyword counter detected zero\
  \ Slovene refusals across all conditions (0/490 held-out Slovene responses, 0/100 verified Gemma-edit Slovene responses),\
  \ and its threshold-blind fraction was 1.0 in both searches. Any downstream use of these checkpoints as language-neutral\
  \ references for safety evaluation---for example, as baselines in multilingual safety benchmarks or as components in multilingual\
  \ safety pipelines---inherits this validity gap.\n\n\\paragraph{Depth placement.} The depth placement finding has a narrower\
  \ scope. Within a single model, the depth at which abliteration energy is applied correlates strongly with residual refusal,\
  \ particularly in Slovene. But this profile does not transfer across architectures ($\\rho = -0.009$ between Gemma and Qwen3-8B).\
  \ The practical consequence is limited: knowing which layers matter for one model does not help with another.\n\n\\paragraph{Model\
  \ divergence.} The GaMS3--Gemma contrast is striking: the edit transfers fully to GaMS3 but largely fails on Gemma. We observe\
  \ this asymmetry but do not attribute it to a specific mechanism. The two checkpoints differ in their training data (GaMS3\
  \ was continually pretrained on 140B tokens including Slovene \\cite{Vres2026}), but we study only two models from one architecture\
  \ family, so we cannot isolate whether continual pretraining, the specific training mix, or some other factor drives the\
  \ difference.\n\n\\subsection{Limitations}\n\\label{sec:limitations}\n\nSeveral limitations constrain the scope of these\
  \ findings.\n\n\\textbf{Slovene judge certification.} The Qwen3-14B workhorse judge does not meet the $\\kappa \\geq 0.80$\
  \ certification gate for Slovene (unweighted $\\kappa = 0.72$, CI $[0.63, 0.81]$). The certification gate requires both\
  \ the population-weighted and unweighted kappa to reach 0.80; the weighted kappa is 0.87, but the unweighted kappa falls\
  \ short. Absolute Slovene refusal rates may be biased. Within-Slovene relative comparisons (e.g., GaMS3-orig vs.\\ GaMS3-edit)\
  \ are less affected, since the bias is approximately constant across checkpoints, but we cannot rule out differential bias.\n\
  \n\\textbf{Generation truncation.} 94--95\\% of edited English outputs and 70--92\\% of edited Slovene outputs were truncated\
  \ at the 256-token generation limit. The judge classified refusal status from incomplete text in these cases, which may\
  \ affect both refusal rate and ASR estimates.\n\n\\textbf{Two models, one architecture.} We study two closely related models\
  \ (Gemma and its continual-pretraining derivative). The findings may not generalise to architecturally different families\
  \ (e.g., Llama, Mistral). The Qwen3-8B data in the cross-model prediction test (Section~\\ref{sec:placement}) provides one\
  \ additional architecture, but a systematic survey across model families is needed.\n\n\\textbf{One target language.} Slovene\
  \ is a mid-resource Indo-European language. The keyword measurement bias extends to any language the keyword counter does\
  \ not cover, but the degree of edit transfer failure may differ for typologically distant or extremely low-resource languages.\n\
  \n\\textbf{NF4 quantisation.} All experiments use 4-bit NF4 quantisation. The refusal direction and abliteration behaviour\
  \ may differ at full precision or other quantisation levels.\n\n\\textbf{Single Heretic configuration.} The abliteration\
  \ uses a single Heretic configuration per model (116 TPE trials, default hyperparameter ranges). A more exhaustive search\
  \ might yield different results.\n\n\\section{Conclusion}\n\nWe evaluated the cross-lingual transfer of English-tuned abliteration\
  \ to Slovene on two 12B-parameter models and found that keyword-verified abliterated checkpoints are not valid language-neutral\
  \ references for refusal evaluation. The English keyword counter is structurally blind to Slovene refusals ($\\Delta_{\\\
  mathrm{lang}} = -1.56$, threshold-blind fraction 1.0), and the two models we tested diverge dramatically in whether the\
  \ edit transfers to Slovene. Depth placement of edits across layers correlates with residual refusal within each model but\
  \ does not transfer across architectures. All Slovene absolute rates carry a caveat from the uncertified workhorse judge\
  \ ($\\kappa = 0.72$).\n\n\\bibliography{references}\n\\bibliographystyle{plainnat}"
summary: >-
  This paper evaluates whether English-tuned abliteration transfers to Slovene across two 12B-parameter models. The headline
  finding is that keyword-verified abliterated checkpoints are not valid language-neutral references for refusal evaluation.
  The English keyword counter is structurally blind to Slovene refusals: on 100 verified Gemma-edit pairs it fires on 87%
  of English but 0% of Slovene responses, while the judge finds 82% Slovene refusal (Delta_lang = -1.56). Among all optimiser
  candidates, every one the judge places below the selection threshold is invisible to the keyword counter (TBF = 1.0; 6/6
  Gemma, 37/37 GaMS3). The edit transfers fully to GaMS3 (Slovene refusal 87% to 0%) but fails on Gemma (94% to 74%); we observe
  this asymmetry without attributing it to a specific training-stage mechanism. Depth placement correlates with residual refusal
  within each model (confirmation rho = -0.96 EN, -0.83 SL for Gemma; -0.90 SL for GaMS3) but does not transfer across architectures
  (cross-model rho = -0.009). All Slovene results carry caveats: the judge does not meet the kappa >= 0.80 certification gate
  (kappa = 0.72), and 94-95% of edited English outputs were truncated at 256 tokens.
</paper_draft>

<available_figures>
--- Item 1 ---
id: fig_1
figure_type: data
title: Refusal Rates Before and After Abliteration
caption: >-
  Refusal rates on RefusEU S5 harmful prompts ($n=280$) for all five checkpoints in English and Slovene. Abliteration transfers
  almost completely to Slovene for GaMS3 (orange) but fails for Gemma (blue). The community reference checkpoint (grey) shows
  that deeper abliteration can partially overcome the language gap. Error bars show 95\% Clopper--Pearson confidence intervals.
  Note: 94--95\% of edited English outputs were truncated at the 256-token generation limit.
image_gen_detailed_description: >-
  Grouped bar chart with 5 checkpoint groups on the x-axis: 'GaMS3-orig', 'GaMS3-edit', 'Gemma-orig', 'Gemma-edit', 'Community-ref'.
  Each group has two bars: English (blue, #4472C4) and Slovene (orange, #ED7D31). Y-axis: 'Refusal Rate' from 0.0 to 1.0 with
  grid lines at 0.2 intervals. Values: GaMS3-orig EN=0.986 SL=0.871; GaMS3-edit EN=0.014 SL=0.000; Gemma-orig EN=0.971 SL=0.939;
  Gemma-edit EN=0.287 SL=0.739; Community-ref EN=0.054 SL=0.114. Error bars showing 95% CI (see caption). White background,
  sans-serif font (Arial/Helvetica), legend in top-right corner showing 'English' and 'Slovene'. Aspect ratio 3:2. The dramatic
  contrast between GaMS3-edit (near-zero bars) and Gemma-edit (still-high Slovene bar) is the focal point.
aspect_ratio: '21:9'
summary: >-
  Shows the central asymmetry: abliteration removes Slovene refusal in GaMS3 but not in Gemma.
figure_path: figures/fig_1_v0.pdf

--- Item 2 ---
id: fig_2
figure_type: data
title: Keyword Measurement Bias
caption: >-
  Keyword counter vs.\ reference judge positive rates for the Gemma-edit checkpoint on 100 verified paired prompts. The keyword
  counter fires on 87\% of English responses but 0\% of Slovene responses; the reference judge finds 13\% English refusal
  and 82\% Slovene refusal. $\Delta_{\mathrm{lang}} = -1.56$ [$-1.68$, $-1.44$]. The keyword counter is structurally blind
  to Slovene refusals.
image_gen_detailed_description: >-
  Side-by-side grouped bar chart with two panels. Left panel titled 'Keyword Counter': two bars for English (blue #4472C4,
  height 0.87) and Slovene (orange #ED7D31, height 0.00, just a thin line at the x-axis). Right panel titled 'Reference Judge':
  two bars for English (blue #4472C4, height 0.13) and Slovene (orange #ED7D31, height 0.82). Y-axis on both panels: 'Positive
  Rate (refusal detected)' from 0.0 to 1.0, grid lines at 0.2 intervals. Annotation arrow from the empty SL bar in the left
  panel labeled 'Keyword sees 0% SL refusal'. Annotation between panels labeled 'Delta_lang = -1.56'. Small text box at bottom:
  'TBF = 1.0: 6/6 Gemma, 37/37 GaMS3 candidates below judge threshold are invisible to keyword counter'. White background,
  sans-serif font (Arial/Helvetica), aspect ratio 3:2.
aspect_ratio: '21:9'
summary: >-
  Shows that the English keyword counter fires on English responses but is completely silent on Slovene, while the reference
  judge detects substantial Slovene refusal.
figure_path: figures/fig_2_v0.pdf

--- Item 3 ---
id: fig_3
figure_type: data
title: Depth Placement Profile for GaMS3
caption: >-
  Residual Slovene refusal rate as a function of depth placement for GaMS3-12B-Instruct. Each point is a single abliteration
  configuration; the x-axis is a depth-placement index (lower = shallower layers). Spearman $\rho = -0.90$ ($p < 10^{-7}$).
  Deeper placements produce lower residual Slovene refusal. The relationship holds within both energy levels (E2: $\rho =
  -0.97$; E3: $\rho = -0.95$).
image_gen_detailed_description: >-
  Scatter plot. X-axis: 'Depth Placement Index' from 0 to 10 (integer ticks). Y-axis: 'Residual Slovene Refusal Rate' from
  0.0 to 1.0. Twenty data points in two colors: E2 energy level (circles, #4472C4 blue) and E3 energy level (triangles, #ED7D31
  orange). Points follow a clear negative trend from upper-left (shallow placement, high refusal ~0.85-0.95) to lower-right
  (deep placement, low refusal ~0.15-0.40). Representative values: index=1 refusal~0.90, index=3 refusal~0.75, index=5 refusal~0.60,
  index=7 refusal~0.40, index=9 refusal~0.20. A dashed regression line (grey) showing the negative trend. Text annotation
  in upper-right: 'rho = -0.90, p < 1e-7'. Legend showing 'E2 (energy=13.9)' and 'E3 (energy=27.8)'. White background, sans-serif
  font, aspect ratio 3:2.
aspect_ratio: '21:9'
summary: >-
  Shows that deeper layer placement consistently produces lower residual Slovene refusal in GaMS3, with the relationship holding
  across energy levels.
figure_path: figures/fig_3_v0.pdf
</available_figures>

<figure_requirements>
CRITICAL: Include ALL figures from <available_figures>. No exceptions.

- Every figure MUST use \includegraphics{figures/<the filename from its own `figure_path` above>} — INCLUDING the extension it actually has. Data figures are delivered as `.pdf` (vector, so their axis labels stay sharp) and concept figures as `.jpg`. Writing `.jpg` for a `.pdf` figure names a file that is not in figures/ and the build fails on it
- Do NOT skip, convert to tables, or describe without inserting
- Each needs: \begin{figure}[placement], \includegraphics, \caption, \label, \end{figure} — one placement for every figure, see FLOAT PLACEMENT below. Constrain every \includegraphics with `width=\linewidth,height=0.85\textheight,keepaspectratio`. The height is a LAST RESORT, not the usual limit: it exists so a very tall figure cannot overrun the page, and at 0.4 it bound almost everything instead — a 1:1 confusion matrix printed at 50.9% and its 11 pt axis labels reached the page at 5.6 pt, below what any venue accepts. At 0.85 every ratio the paper prompt prescribes (21:9, 16:9, 4:3, 1:1) is limited by WIDTH, prints at 93% and keeps its text above 10 pt. Use exactly these option keys — `max height=` is NOT valid LaTeX
- Use the `caption` field from each figure for \caption{...} — do NOT invent new captions
- Place each figure where its own [FIGURE:fig_id] marker appears in <paper_draft>
- VERIFICATION: paper.tex MUST have exact same number of \includegraphics as <available_figures>
- Do NOT generate new figure images (no matplotlib, no PIL, no image generation). Use ONLY the pre-generated figures from <available_figures>. They were already created by a previous pipeline step.

FLOAT PLACEMENT: every figure gets \begin{figure}[!htbp]. Measured, not chosen:
the document the aii-paper-to-latex skill sets up is ONE column, so `figure*` is
exactly as wide as `figure` (469.76pt either way) and gains nothing; and any
placement asking for a page TOP — `[!t]`, `[!tbp]` — floated the hero diagram above
the paper's own title on page 1, while `[!htbp]` did not. `[!htbp]` also gives LaTeX
four options, so a float can never be deferred to the end of the document, which one
option alone risks. Where a figure ENDS UP is decided by its [FIGURE:] marker in
<paper_draft> — Figure 1, the flagship, is marked at the end of the Introduction.
Preserve every marker's position.
</figure_requirements>

<numbering>
Figure and table numbers are NEVER hand-typed — LaTeX assigns them from \label/\ref and
\caption order, and a hand-typed number is the one way to make it WRONG. Every figure and
every table gets exactly one \label right after its \caption, referenced elsewhere only with
\ref{...} (never write "Figure 3" or "Table 2" as literal text; write "Figure~\ref{fig:...}"
and "Table~\ref{tab:...}"). Do not call \setcounter{figure}{...} or
\setcounter{table}{...} — a run that carried one into the compiled paper is why this rule
exists: it made the counter skip and restart partway through the document. Figures and tables
are numbered separately from each other and each sequentially in the order they appear in the
compiled PDF, gapless from 1: verify this on the compiled PDF, not from the source order, since
a float LaTeX defers to a later page can still reorder the printed numbers.
</numbering>

<artifact_links>
The paper draft contains \footnote{Code: \url{...}} references linking to artifact source code
on GitHub. Include \usepackage{hyperref} and \usepackage{url}.
Preserve these exactly as-is — do not remove, rewrite, or convert them to plain text.
Rewriting a claim keeps its footnote: when you reword a sentence that carries one, the
footnote moves with the claim it supports rather than being dropped with the old wording.
The URLs will not resolve yet (the repo is deployed after compilation) — do NOT try to verify or fix them.
A marker of the literal form [ARTIFACT:id] must never appear in paper.tex. Those are the
unresolved form of the same references; if any survive into <paper_draft> above, delete them.
</artifact_links>

<headings>
NEVER use inline math (``$...$``) inside ``\section{...}`` / ``\subsection{...}`` / ``\subsubsection{...}`` arguments — hyperref's bookmark builder errors out (``Token not allowed in a PDF string``) and the PDF outline breaks. If a section heading needs a math-looking term, use the text equivalent (``d star`` not ``$d^*$``, ``alpha-equivalent`` not ``$\alpha$-equivalent``) or wrap it in ``\texorpdfstring{$math$}{plain}``. Inline math inside body paragraphs is fine.
</headings>

<writing_register>
Write in the register of the field's best papers (the style exemplars block below, when the writing step saved any), not in the register of a language
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

<style_exemplars>
Verbatim passages from the field's best-cited recent papers, which the report-writing step saved
as style_exemplars.md. Every sentence you write or change for this paper, captions and
transitions included, is written in their register. Where the file ends with section outlines,
<paper_structure> says what they are for.

# Style exemplars for multilingual safety / representation editing

## Source 1: Wang et al. 2025 — Refusal Direction is Universal Across Safety-Aligned Languages

### Passage (abstract)
"Refusal mechanisms in large language models (LLMs) are essential for ensuring safety. Recent research has revealed that refusal behavior can be mediated by a single direction in activation space, enabling targeted interventions to bypass refusals. While this is primarily demonstrated in an English-centric context, appropriate refusal behavior is important for any language, but poorly understood."

### Style notes
- Direct, declarative sentences. No hedging in the opening claim.
- "mediated by a single direction" — field-standard terminology, no circumlocution.
- Passive voice when describing prior findings; active when stating the paper's contribution.
- Numbers appear only in methods/results, not in framing.

### Section outline
Introduction > Background > Method (PolyRefuse dataset, direction extraction) > Experiments (14 languages, cross-lingual transfer) > Analysis > Conclusion

---

## Source 2: Aziz et al. 2026 — Low-Resource Safety Failures Are Action Failures, Not Representation Failures

### Passage (abstract)
"Safety alignment learned in high-resource languages transfers poorly to low-resource languages. Models refuse harmful prompts in English but fail to refuse when the same prompts are translated into Swahili or Burmese. [...] The relevant representation is present. Yet harmful refusal drops from 87.9% to 43.9%. The model fails to convert the representation into refusal."

### Style notes
- Short sentences that build an argument step-by-step.
- Concrete contrast: "The relevant representation is present. Yet harmful refusal drops from 87.9% to 43.9%."
- Uses "fails to" rather than "is unable to" — active framing of a negative result.
- Two numbers in the abstract, both with clear context.

### Section outline
Introduction > Related Work > Method (readout recalibration, gate routing) > Experiments (23 languages, 3 models) > Results > Analysis > Conclusion

---

## Source 3: Yoon et al. 2026 — Who Pays More for Safety?

### Passage (abstract)
"Safety alignment helps models adhere to human values, but it often reduces response utility. We ask a critical but understudied question: Does safety alignment impose the cost equally across language groups? [...] We find a systematic inequity: non-English users consistently bear a higher Safety Cost than English users."

### Style notes
- Frames the research question explicitly before giving findings.
- "systematic inequity" — precise, not melodramatic.
- "bear a higher Safety Cost" — uses the paper's defined term naturally.
- Avoids "we show that" / "we demonstrate that" phrasing.

### Section outline
Introduction > Safety Cost Protocol > Experiments > Patterns (double-penalty zone, apparent gains, high-resource disparity) > Discussion > Conclusion

---

## Source 4: Wu et al. 2026 — Knowing without Acting

### Passage (abstract)
"Safety alignment is often conceptualized as a monolithic process wherein harmfulness detection automatically triggers refusal. However, the persistence of jailbreak attacks suggests a fundamental mechanistic decoupling. We propose the Disentangled Safety Hypothesis (DSH), positing that safety computation operates on two distinct subspaces: a Recognition Axis and an Execution Axis."

### Style notes
- Opens with a conventional understanding, then challenges it.
- Defines new terms inline with parenthetical notation.
- "positing" rather than "claiming" — appropriate epistemic stance for a hypothesis.
- Technical precision: "subspaces", "axis", "disentangled" are field-standard geometry terms.

### Section outline
Introduction > Related Work > DSH Framework > Geometric Analysis > Double-Difference Extraction > Experiments (AmbiguityBench) > Causal Steering > REA Attack > Discussion > Conclusion

---

## Source 5: Arditi et al. 2024 — Refusal in Language Models Is Mediated by a Single Direction

### Style notes (from field knowledge)
- Established the "refusal direction" terminology now standard in the field.
- Clear experimental structure: identify direction > ablate > measure behaviour change.
- Uses "mediated by" rather than "caused by" — appropriate mechanistic hedging.
- Figures carry the argument: activation projections, before/after ablation comparisons.
</style_exemplars>


FIRST, add ALL of these to your todo list using your task/todo-tracking tool:

CRITICAL: Todo content must be copied exactly as is written here, with NO CHANGES. These todos are intentionally detailed so that another LLM could read each one without any external context and understand exactly what it has to do.

<todos>
TODO 1. Read and STRICTLY follow these skills: aii-paper-to-latex, aii-paper-writing, aii-semscholar-bib.
TODO 2. Read <paper_draft> and <available_figures>. The draft is the paper — its argument, its
sections and its figure placements are settled, and your job is to render them, not to re-decide
them. Copy all figure images into ./figures/ in your workspace. Count figures — MUST include
every one. Note where each [FIGURE:fig_id] marker sits in the draft. Build `./references.bib` by
running the aii_semscholar_bib__fetch script with `--out ./references.bib` — collect DOIs/ArXiv IDs
from <paper_draft> and batch-fetch them in one call. That script is the ONLY way
a reference enters references.bib, and it writes the `./references.json` record the finished paper
is checked against: never write or edit a BibTeX entry by hand, never edit references.json, and do
not cite a paper it cannot fetch. Cite with the keys it printed; no \nocite{*}.
TODO 3. Create `./paper.tex` per aii-paper-to-latex skill's setup: typeset <paper_draft> section by section, keeping <publishable_paper_rules> true of the result — the draft's sections as <paper_structure> describes them, the method as it finally stands, no iterations and no process. Insert ALL figures from <available_figures> at their markers, include `./references.bib` via \bibliography. Compile to PDF per skill's process. Fix errors.
TODO 4. CRITICAL VERIFICATION: Run `grep -c 'includegraphics' paper.tex`, confirm count equals figures in <available_figures>. If not, add missing figures. Verify `./paper.pdf` was created.
TODO 5. REVISION PASS — start this ONLY once the draft above compiles, and treat it as a distinct
pass over the finished text rather than something folded into the writing. Read
`REVISION_CHECKLIST.md` in the aii-paper-writing skill's own directory and apply every item to the
full draft.

Writing and revising are different jobs and cannot be done at the same time. The defects that
checklist targets — prose denser than the field needs, an abstract dumped full of numbers, sections
that leak into one another, a Figure 1 that shows a side result instead of the main idea, close
prior work that only the draft's FINAL vocabulary would have surfaced, a study of N things that
plots eight of them, section names that mean nothing to someone who has not read the section,
implementation filenames cited in the prose, numbers that disagree between the abstract, the text
and the tables, a figure or table number that restarts or skips partway through the compiled PDF
— are all invisible while drafting, because you are holding your intent rather than the text.
Every one is obvious to the first outside reader.

Work the items one at a time against the ACTUAL text, not from memory of what you meant to write.
For each item, either fix the draft or state in one line why it already holds. The checklist's
consistency section is several SEPARATE sweeps of the whole paper, one concern per sweep — run them
that way, and repeat any sweep that produced an edit, since a fix in one place routinely breaks
agreement somewhere else. Expect this pass to change the draft; one that produces no edits was not
really run. Recompile when it is done.
TODO 6. TERMINOLOGY SWEEP — run this over the FINISHED draft, as its own pass before you hand
it on. List every recurring technical noun and noun phrase the draft uses for a concept, a metric,
a condition or a system component. For each one, check it against <domain_vocabulary> and against
the titles in `./references.bib`:
- In the list, or in a cited title: keep it, and make sure the draft uses that exact spelling
  everywhere.
- Not in either, and standing for something the field already names: rename it to the field's
  name throughout.
- Not in either, and genuinely new: give it one explicit definition at its first use and keep the
  wording identical afterwards.
- A bare code in a sentence (C1, M3): replace it with the name of the thing.
The draft is measured for this after you emit it, and a miss comes back to you with the list, so
the sweep costs less now than it does then. `./domain_terms.json` holds the same list on
disk if you would rather read it there.
TODO 7. VISUAL REVIEW: Write Python script to convert EVERY page of paper.pdf to PNG at 150 DPI (use pdf2image or pymupdf). Then read ALL page screenshots — each page image costs ~1,600 tokens so a 15-page paper is only ~24K tokens. You MUST read every page. The ONLY exception is if all page images would not fit in your remaining context — in that case, read as many as fit and state which pages you are skipping and why. Check every page for layout issues, overlapping figures, cut-off text, bad spacing, formatting problems. Fix issues and recompile.
TODO 8. FINAL READ: Check page count (`pdfinfo paper.pdf` or pymupdf). Read entire paper.pdf — check for missing sections, unclear explanations, inconsistencies, typos. Fix and recompile. The ONLY exception is if all pages would not fit in your remaining context — in that case, read as many pages as fit and state which pages you are skipping and why.
</todos>

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
    "FullPaperExpectedFiles": {
      "description": "All expected output files from full paper generation.",
      "properties": {
        "paper_tex_path": {
          "description": "Path to LaTeX source file. Example: 'paper.tex'",
          "title": "Paper Tex Path",
          "type": "string"
        },
        "paper_pdf_path": {
          "description": "Path to compiled PDF. Example: 'paper.pdf'",
          "title": "Paper Pdf Path",
          "type": "string"
        },
        "references_bib_path": {
          "description": "Path to BibTeX bibliography file. Example: 'references.bib'",
          "title": "References Bib Path",
          "type": "string"
        },
        "figure_paths": {
          "description": "Paths to all figure image files. Example: ['figures/fig1_v0.jpg', 'figures/fig2_v0.jpg']",
          "items": {
            "type": "string"
          },
          "title": "Figure Paths",
          "type": "array"
        }
      },
      "required": [
        "paper_tex_path",
        "paper_pdf_path",
        "references_bib_path",
        "figure_paths"
      ],
      "title": "FullPaperExpectedFiles",
      "type": "object"
    }
  },
  "description": "Full paper \u2014 structured output from paper generation.",
  "properties": {
    "title": {
      "description": "Paper title in plain, everyday language \u2014 short and jargon-free so a non-expert grasps it at a glance. Aim for about 4-8 words (~40 characters).",
      "maxLength": 90,
      "minLength": 12,
      "title": "Title",
      "type": "string"
    },
    "summary": {
      "description": "Brief summary of the generated paper: sections written, figures included, compilation status",
      "maxLength": 5000,
      "minLength": 500,
      "title": "Summary",
      "type": "string"
    },
    "findings_summary": {
      "description": "The run's finding in 2-4 sentences, for a reader who will not open the PDF: what was tested, the headline number with its units, what it means. Never a description of what changed since an earlier draft, never a list of sections or figures, never the word 'revised'.",
      "maxLength": 1200,
      "minLength": 120,
      "title": "Findings Summary",
      "type": "string"
    },
    "out_expected_files": {
      "$ref": "#/$defs/FullPaperExpectedFiles",
      "description": "All output files you created. Must include paper.tex, paper.pdf, references.bib, and paths to all figure files."
    }
  },
  "required": [
    "title",
    "summary",
    "findings_summary",
    "out_expected_files"
  ],
  "title": "FullPaper",
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

### [2] SKILL-INPUT — aii-paper-to-latex · 2026-09-25 06:27:29 UTC

The agent loaded the **aii-paper-to-latex** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-to-latex
description: "Assembles and compiles a LaTeX paper into paper.pdf: documentclass and package preamble, figure floats that includegraphics pre-generated vector .pdf and .jpg files, float-placement and width rules, and the required pdflatex, bibtex, pdflatex, pdflatex run sequence. Use whenever pre-written text and pre-generated figures must become a compiled PDF, and whenever a build misbehaves — citations printing as question marks, figures drifting to the end or above the title, shrunken axis labels, undefined references. Triggers: latex, tex, pdflatex, bibtex, natbib, includegraphics, figure float, htbp, compile or build the paper, paper.tex, paper.pdf. NOT for: writing the paper's text or deciding its structure (use aii-paper-writing), creating the figure images (aii-data-fig-gen, aii-concept-fig-gen), or fetching bibliography entries (use aii-semscholar-bib); NOT for reshaping a PDF that already exists — merging, splitting, form filling, table extraction (use anthropic-pdf)."
---

## LaTeX Paper Assembly

Assembles a research paper from paper text, pre-generated figures (vector `.pdf` for data figures, `.jpg` for concept figures) and a bibliography into a compiled PDF.

### Document Setup

```latex
\documentclass[11pt,letterpaper]{article}
\usepackage{graphicx, geometry, amsmath, hyperref, url, natbib, booktabs, xcolor, listings}
\geometry{margin=1in}
\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}
```

### Figure Inclusion

CRITICAL: Include ALL figures. Every figure MUST appear in the paper.

```latex
\begin{figure}[!htbp]
  \centering
  \includegraphics[width=\linewidth,height=0.85\textheight,keepaspectratio]{figures/filename.pdf}
  \caption{Descriptive caption.}
  \label{fig:label}
\end{figure}
```

Rules:
- ALWAYS `[!htbp]` — all four options, so a float can never be deferred to the end of the
  document, which `[t]` or `[h]` alone risks. Do not ask for a page TOP: `[!t]` and
  `[!tbp]` both floated a figure ABOVE the paper's own title on page 1, where `[!htbp]`
  on the same document did not. Where a figure lands is decided by where it is declared
  in the text
- Use `figure`, never `figure*`. This document class is ONE column, so `figure*` is exactly
  as wide as `figure` (469.76pt either way) and gains nothing, while restricting the float
  to a page top
- ALWAYS constrain with `width` and `keepaspectratio`. Add `height` only as a
  LAST RESORT against a very tall figure overrunning the page, and keep it
  generous — `0.85\textheight`. A tight height cap binds on ordinary figures
  and LaTeX then shrinks the TEXT with them: at `0.4\textheight` a square
  figure printed at 50.9%, putting 11 pt axis labels on the page at 5.6 pt.
  The figure generator measures legibility at the figure's OWN size, so it
  cannot see this happen
- Every figure needs `\caption`, `\label`, and a `\ref` in the text
- Do NOT convert figures to tables or describe them without inserting the image
- Do NOT skip any figures

### Compilation Process

Run each command separately (do NOT chain with `&&` — pdflatex often exits non-zero on warnings, which would skip bibtex and leave citations as `??`):

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

All four commands are required. Skipping bibtex causes `??` in all citations.
Fix any errors between runs. Verify `./paper.pdf` was created.

### Output Files

- `./paper.tex` — LaTeX source
- `./references.bib` — bibliography file
- `./paper.pdf` — compiled PDF
- `./figures/` — all figure images (pre-generated, copied into workspace). Data
  figures are `.pdf` (vector — LaTeX renders their text at page resolution, which
  is what keeps axis labels sharp in print); concept figures are `.jpg`. Use each
  file's OWN extension in `\includegraphics`; there is no conversion step.
````

### [3] SKILL-INPUT — aii-paper-writing · 2026-09-25 06:27:29 UTC

The agent loaded the **aii-paper-writing** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-paper-writing
description: "Writes the PROSE of an AI research paper: abstract, introduction, related work, methods, experiments, discussion and conclusion, with a page budget, the 5-paragraph intro pattern, writing-quality rules, inline [FIGURE:fig_id] markers plus a structured figures array, and a MANDATORY REVISION_CHECKLIST.md pass over every finished draft. Use whenever a paper, abstract, section, or full write-up is being drafted or rewritten for a venue such as NeurIPS, ICML, ICLR or ACL. Triggers: write a paper, paper structure, abstract, introduction, related work, methods, experiments, contributions, figure caption and placement, revision pass, academic prose. NOT for: assembling or compiling .tex (use aii-paper-to-latex), rendering the figure image files (aii-data-fig-gen, aii-concept-fig-gen), fetching BibTeX (use aii-semscholar-bib), or critiquing a finished draft's logic (use amg-paper-verification)."
---

## MANDATORY: the final revision pass

**`REVISION_CHECKLIST.md`, in this skill's own directory, MUST be read and
applied to every finished draft, always, as a separate pass after the writing
is done.** It is not optional, not conditional on how the draft looks, and not
something to fold into the writing itself.

Writing and revising are different jobs and cannot be done in one pass. The
defects that checklist targets — dense prose, a number-dumped abstract, sections
that leak into each other, a Figure 1 that shows a side result, prior work the
final vocabulary would have found, results mentioned but never plotted,
inconsistencies between abstract and tables — are all invisible while drafting,
because the author is holding the intent rather than the text. Every one of them
is obvious to the first outside reader. Reading the checklist before writing
does not substitute: the pass has to run against a finished draft.

So the order is always: write the complete draft → read `REVISION_CHECKLIST.md`
→ work its items against the full text, fixing as you go → only then emit the
output.

## Technical Papers

Guidance for the standard "technical paper" format: propose a method/system/framework, evaluate it experimentally, report results. This is the main track at most CS venues (NeurIPS, ICML, ICLR, ACL, AAAI, etc.). Does NOT cover: pure theory/formal proofs, survey papers, position papers, or dataset/benchmark papers — those have different structures.

### Paper Structure

Target 6-8 pages. Use formal academic language, third person. Support claims with evidence from artifacts.

#### Rough Page Budget (8-page paper)

| Section | Pages | Notes |
|---|---|---|
| Abstract | 0.3 | Problem, approach, key result |
| Introduction | 1.0-1.5 | The most important section |
| Related Work | 0.5-1.0 | Beginning or end (see below) |
| Methods | 1.5-2.0 | Architecture fig on page 1 |
| Experiments | 1.5-2.0 | Setup + results + ablations |
| Discussion | 0.5-1.0 | Limitations go here |
| Conclusion | 0.3-0.5 | Do not repeat the abstract |
| References | 0.5-1.0 | Not counted in page limit |

**Critical rule**: A clear new technical contribution must be articulated by page 3 (quarter of the paper). If the reader doesn't know what you did by then, you've lost them.

#### Section Details

**Abstract** (150-250 words): State the problem, your approach, and the main results. Be factual and comprehensive. Do not repeat the abstract word-for-word later in the paper.

**Introduction** — Follow this 5-paragraph structure:

1. **What is the problem?** Define the task concretely.
2. **Why is it interesting and important?** Real-world impact, scale.
3. **Why is it hard?** Why do naive approaches fail?
4. **Why hasn't it been solved before?** What's wrong with prior solutions? How does yours differ?
5. **What are the key components of your approach and results?** Include specific limitations.

End with a "Summary of Contributions" subsection — bullet list of contributions with section references. This doubles as an outline, saving space.

**Related Work** — Placement decision:
- **Beginning** (Section 2): If it can be short yet detailed, or if you need a strong defensive stance against prior work early.
- **End** (before Conclusions): If comparisons require your technical content, or if it can be summarized briefly in the Introduction. Can be titled "Discussion and Related Work."

**Methods/Approach**: Every section tells a story — the story of the results, NOT the story of how you arrived at them. Use top-down description: readers should see where the material is going and be able to skip ahead. Move gory details to appendices.

**Experiments**: Setup (datasets, metrics, baselines) → main results → ablations → analysis. Every claim needs quantitative evidence.

**Discussion**: Interpret results, compare to prior work, state limitations honestly. Limitations should be specific and actionable, not vague disclaimers.

**Conclusion**: Short summarizing paragraph. Do NOT repeat material from the Abstract or Introduction. Make original claims more concrete (e.g., reference quantitative results). Include future work as bullet list — if actively pursuing follow-up, say so to mark territory.

#### Writing Quality Rules

- Define all notation/terminology before use, only once. Group global definitions in Preliminaries.
- Do NOT use nonreferential "this", "that", "these", "it". Always specify the referent. BAD: "This is important because..." GOOD: "This accuracy gap is important because..."
- Do NOT use "etc." unless remaining items are completely obvious. BAD: "We measure volatility, scalability, etc." GOOD: "We measure volatility and scalability."
- Do NOT write "for various reasons" — state the actual reasons.
- "That" is defining, "which" is nondefining. "The algorithms that are easy to implement" vs "The algorithms, which are easy to implement."
- Use italics for definitions and quotes, not for emphasis. Context alone should provide emphasis.

### Figure Format

Figures use a hybrid marker + structured array approach. ALL figures are generated by a separate pipeline step using an AI image model — your `image_gen_detailed_description` is the ONLY input that model sees. It cannot read files or access data. Do NOT generate actual image files yourself (no matplotlib, no PIL, no image generation scripts).

**In paper_text**: Place `[FIGURE:fig_id]` markers where figures should appear.

**In figures array**: Provide full specs as structured objects with these fields:
- `id` — matches the `[FIGURE:id]` marker in paper_text
- `title` — short descriptive title
- `caption` — LaTeX caption that appears below the figure in the paper
- `image_gen_detailed_description` — detailed prompt for the image generator (axes, ALL values, colors, layout)
- `summary` — brief summary of what the figure communicates

Example in paper_text:
```
...our method achieves state-of-the-art results as shown below.

[FIGURE:fig_1]

The results in Figure 1 demonstrate...
```

Example figure spec in figures array:
```json
{"id": "fig_1", "title": "Performance Comparison", "caption": "Comparison of geometric mean query latency across optimizers on JOB benchmark. RLQOpt achieves 2.3x speedup over PostgreSQL.", "image_gen_detailed_description": "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: ModelA=0.847, ModelB=0.762, Baseline=0.531. Error bars with std: 0.02, 0.03, 0.05. Sans-serif font, white background.", "summary": "Compares accuracy of proposed methods vs baseline."}
```

Every marker in text MUST have a matching figure in the array, and vice versa.

#### Data Precision Requirement

`image_gen_detailed_description` MUST include exact numbers from artifact output files. Read the actual output files before writing figure specs.

- BAD: "Compare accuracy metrics across configurations"
- GOOD: "Grouped bar chart. X-axis: model names. Y-axis: accuracy (0.0-1.0). Values: K=3: 0.765, K=5: 0.729, Baseline: 0.121."

#### Figure vs Table Decision

Do NOT create figures for tabular data (rows/columns of text or numbers). Use `\begin{table}` in LaTeX instead. Figures are for actual visualizations only (charts, plots, diagrams).

#### Figure Placement Strategy

Be intentional with figure ordering. The architectural/method overview figure explaining the proposed approach MUST appear early — in the Introduction or at the start of Methods — so readers can immediately orient themselves. Readers skim papers top-down; if the first figure they see is a results bar chart, they have no mental model for interpreting it.

Recommended ordering:
1. **Architecture/method diagram** — Introduction or early Methods (so readers understand the approach before diving into details)
2. **Conceptual/analogy figures** — Introduction or Methods (to build intuition)
3. **Results figures** (bar charts, line plots, scatter plots) — Results section
4. **Analysis/ablation figures** — Discussion or later Results

#### Guidelines

- Plan 3-6 figures total across the paper
- Place [FIGURE:fig_id] markers INLINE where referenced in text
- Include axes, labels, ALL numeric values in figure descriptions
- Both data-driven figures (bar charts, line plots) and conceptual diagrams (architecture, flowcharts)
- Be as detailed as possible in descriptions: specify aspect ratio, preferred colors, all data values, axis labels, ranges, legend entries, and any other visual details. The more specific the description, the better the generated figure

### Bibliography with Semantic Scholar

Build `./references.bib` using the aii-semscholar-bib skill (real BibTeX from Semantic Scholar):

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Run the `aii_semscholar_bib__fetch` script with the full list in one batch and
   `--out ./references.bib`: it writes `./references.bib` and the fetch record `./references.json`
3. Cite each paper by the key the script printed

Rules:
- References enter `./references.bib` ONLY through the fetch script — never write or edit BibTeX by hand
- If a paper still isn't found after the skill's fallback procedure, do not cite it
- Use `\bibliography{references}` and `\bibliographystyle{plainnat}`
- Do NOT use inline `thebibliography` environment

### Citation Format (for Research Artifacts)

When writing research with numbered citations:

1. Every factual claim MUST have a numbered citation: `[1]`, `[2]`, `[1, 3]`, etc.
2. Each source in the "sources" array MUST have an "index" field
3. The index MUST EXACTLY MATCH citation numbers in the text
4. NEVER cite a number without a matching source index
5. Example: "LLMs show 40% improvement with multi-agent collaboration [1]."
````

### [4] SKILL-INPUT — aii-semscholar-bib · 2026-09-25 06:27:29 UTC

The agent loaded the **aii-semscholar-bib** skill; its `SKILL.md` (the instructions injected into the agent's context) follows verbatim.

````
---
name: aii-semscholar-bib
description: "Fetches real BibTeX entries in one batch from Semantic Scholar by DOI, ArXiv ID or title via aii_semscholar_bib__fetch, normalises citation keys to AuthorYYYY, injects DOIs, and merges the result into references.bib while recording each entry in references.json beside it; a paper it cannot fetch is not cited. ALWAYS use whenever a bibliography, reference list or .bib file is being built or extended, and whenever a citation needs a verified entry instead of an invented one — never hand-write or edit BibTeX. Triggers: bibliography, references.bib, bibtex, citation key, DOI, arXiv id, Semantic Scholar, reference list, cite these papers, natbib entries. NOT for: writing the text around the citations (use aii-paper-writing), running bibtex and compiling (use aii-paper-to-latex), judging whether cited work supports the claims (use amg-paper-verification), or open-ended literature search and PDF mining (use aii-web-tools)."
---

## Tool: `aii_semscholar_bib__fetch`

Batch-fetch BibTeX entries from Semantic Scholar (OpenAlex, then Crossref, when S2 is rate-limited or down). Pass all references in a single call — the tool handles batching internally.

### How it works

1. **DOI/ArXiv refs** → batched into POST /paper/batch calls (up to 500 per API call, auto-chunked)
2. **Title-only refs** → individual GET /paper/search/match (1s delay between)
3. **Fallback when S2 is down** → if S2 still answers 429 (its shared anonymous pool saturates for every caller) or 5xx after its bounded retries, or cannot be reached, S2 is skipped for the rest of the call, and for the next 10-15 min in every call (then one probe decides whether it is back); every ref it did not answer resolves through **OpenAlex**, then **Crossref** (both keyless; set `AII_POLITE_CONTACT` for their higher-limit polite pool). DOI/arXiv hits must agree with the ref's title or first author, so a mislinked record is dropped rather than cited; title hits need a near-exact title. The BibTeX has the same layout, keys and fields as S2's, so `references.bib` cannot tell them apart; each entry's `source` (`semantic_scholar`, `openalex` or `crossref`) says which API answered.
4. **Post-process** → fix entry type; normalise fields so the entry renders cleanly (more than 10 authors keep 5 plus "and others", printed "et al."; S2's mangled accents like `Ram'e` restored; straight quotes as LaTeX quotes; arXiv records as `journal = {arXiv preprint arXiv:<id>}`, never `volume = {abs/<id>}`); fix citation key (AuthorYYYY, accents folded); inject DOI

The ability server runs a single worker (`max_threads: 1`). Multiple concurrent tool calls are queued — each runs independently (no cross-request aggregation). Batching happens within each request.

### Input format

```json
{
  "references": [
    {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
    {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
    {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
  ]
}
```

Each reference object can have:
- `doi` — DOI string (ArXiv DOIs like `10.48550/arXiv.XXXX.XXXXX` auto-convert to ArXiv IDs)
- `arxiv` — ArXiv ID (e.g. `"2305.14325"`)
- `title` — Paper title (used for search/match when no DOI/ArXiv)
- `author` — First author last name (for cleaner citation key)
- `year` — Publication year (int, for citation key)

At least one of `doi`, `arxiv`, or `title` is required per reference.

### Output format

```json
{
  "success": true,
  "bib_text": "@inproceedings{Vaswani2017, ...}\n\n@article{Wei2022, ...}",
  "total": 3,
  "found": 3,
  "failed_count": 0,
  "entries": [{"citation_key": "Vaswani2017", "bibtex": "...", "title": "...", "doi": "...", "arxiv": "", "source": "semantic_scholar"}],
  "failed": []
}
```

Called as a tool (or through `--json`), it returns these entries and writes no file. A bibliography
is built only through the CLI's `--out`, which also writes the record.

### Workflow

1. Collect DOIs, ArXiv IDs, or titles for all papers you need to cite
2. Run the CLI below with the full list in **one call** and `--out ./references.bib`
3. The script merges the fetched entries into `references.bib` (created if absent) and writes a
   record of each one to `references.json` beside it: source database, S2 paperId / DOI / arXiv id,
   title, first author, year. Later calls with `--out` append to both files and keep them in sync;
   a second paper under a key already taken gets a letter suffix (`Smith2020a`), which the output
   lists — cite the key it prints.
4. Check the failed list — for any missed papers, follow the **fallback procedure** below

`references.bib` and `references.json` are written ONLY by this script. Never write, paste or edit a
BibTeX entry by hand, and never edit `references.json`: the paper step checks every `\cite` key
against `references.bib` and every entry against its record, and an entry the script did not write
blocks the paper from being published.

### Fallback for failed references (MANDATORY)

NEVER fabricate BibTeX. For each failed reference:
1. **WebSearch** for `"Title" author year` (try `site:arxiv.org` too)
2. **WebFetch** the paper page → extract its DOI or ArXiv ID and exact title
3. Retry the script with that DOI / ArXiv ID / exact title (same `--out`)
4. Still not found → the paper is not cited. Remove the citation (and any claim that rests only on
   it); there is no hand-written fallback.

---

### CLI (how to build a bibliography)

```bash
SKILL_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo /ai-inventor)/.claude/skills/aii-semscholar-bib" && \
$SKILL_DIR/../.ability_client_venv/bin/python $SKILL_DIR/scripts/aii_semscholar_bib__fetch.py --out ./references.bib --refs '[
  {"doi": "10.48550/arXiv.1706.03762", "author": "Vaswani", "year": 2017},
  {"arxiv": "2201.11903", "author": "Wei", "year": 2022},
  {"title": "Tree of Thoughts", "author": "Yao", "year": 2023}
]'
```

`--out, -o PATH` — merge the entries into PATH and record them in `references.json` beside it (always use it for a bibliography)
`--json, -j` — output raw JSON instead of .bib text

**If the script fails** with a connection error (ability server not running): create a local `.venv`, install server deps from `server_requirements.txt` into it, then run the script with that `.venv`'s python (it falls back to the local core when the server is unreachable), `--out` included — bypassing the server:
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python -r "$SKILL_DIR/scripts/server_requirements.txt"
```
````

### [5] HUMAN-USER prompt · 2026-09-25 06:44:30 UTC

```
[Message from staff account 'staff', not the run's owner]

For the PAPER (LaTeX) and the paper website only; the internal report and executive summary stay faithful to the round record. Lead with the measurement result. Retitle to state it (e.g. "An English Keyword Objective Is Blind to Its Own Edit in Slovene"). Open the abstract with it: the keyword objective never reached its <=10/100 rule, threshold-blind fraction 1.0, EN 0.87 vs judge 0.13, SL 0.00 vs judge 0.82, Delta_lang -1.56 [-1.68, -1.44]. Put the GaMS3/Gemma transfer asymmetry after it. In the Introduction, replace "The central finding is an asymmetry" so it matches the Discussion. The 6/6 and 37/37 counts come from the C scorer in per_candidate.csv; the reference judge J gives 5/5 and 6/6. Name the scorer correctly or cite both. State that the cross-model depth test compared Gemma with Qwen3-8B. Keep all caveats (kappa 0.72 gate unmet; 94-95% EN truncation at 256 tokens).
```

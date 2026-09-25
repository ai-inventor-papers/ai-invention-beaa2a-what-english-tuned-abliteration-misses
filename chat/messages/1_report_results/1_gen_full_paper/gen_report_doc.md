# gen_report_doc — report_results

> Phase: `gen_paper_repo` · `gen_full_paper`
> Run: `run_A3Dbh1J6RI3O-msgsum` — What English-tuned abliteration misses in Slovene
>
> Full, verbatim transcript of this agent task — every system/user prompt, assistant response, thinking block, tool call and tool result — in the order they occurred. Nothing truncated.

## Task: `gen_report_doc` (terminal_claude_agent, claude-opus-4-6)

### [1] CONFIG · 2026-09-25 09:19:09 UTC

```
model: claude-opus-4-6 | effort: high | permission: bypassPermissions
```

### [2] HUMAN-USER prompt · 2026-09-25 09:19:41 UTC

```
[Message from staff account 'staff', not the run's owner]

Executive summary and report: state the findings as measurements and what they mean for evaluating refusal across languages. Remove the operational recommendation (depositing the edit in band 13-24, and using band-mass overlap to select layer sets for the edit). Give no layer band or configuration for removing refusals. Keep everything else faithful to the round record.
```

### [3] ASSISTANT · 2026-09-25 09:19:49 UTC

```
Let me check the current workspace and find the files to edit.
```

### [4] TOOL CALL — Bash · 2026-09-25 09:19:49 UTC

```
Check existing files in new workspace:
ls -la *.tex *.pdf .terminal_claude_agent_struct_out.json 2>&1; echo "---"; ls figures/ 2>&1
```

### [5] TOOL RESULT — Bash · 2026-09-25 09:19:49 UTC

```
{"stdout": "ls: cannot access '*.tex': No such file or directory\nls: cannot access '*.pdf': No such file or directory\nls: cannot access '.terminal_claude_agent_struct_out.json': No such file or directory\n---\nfig_band_analysis_v0.pdf\nfig_behaviour_summary_v0.pdf\nfig_cross_model_v0.pdf\nfig_dose_response_v0.pdf\nfig_gams3_profile_v0.pdf\nfig_gbf_v0.pdf\nfig_redundancy_index_v0.pdf\nfig_refusal_gap_v0.pdf\nfig_write_profile_v0.pdf", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [6] ASSISTANT · 2026-09-25 09:19:57 UTC

```
Fresh workspace, figures present. Let me copy the validated tex files from the previous run, then apply the staff's edits.
```

### [7] TOOL CALL — Bash · 2026-09-25 09:19:57 UTC

```
Copy tex files from previous run:
SRC=/ai-inventor/aii_data/runs/run_WY-5q2onKHeA/4_gen_paper_repo/_4_assemble_paper/report_workspace
DST=/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace
cp "$SRC/report.tex" "$DST/report.tex"
cp "$SRC/exec_summary.tex" "$DST/exec_summary.tex"
echo "Copied"
```

### [8] TOOL RESULT — Bash · 2026-09-25 09:19:59 UTC

```
{"stdout": "Copied", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [9] ASSISTANT · 2026-09-25 09:20:03 UTC

```
Now let me find the sections that contain operational recommendations to remove.
```

### [10] TOOL CALL — Bash · 2026-09-25 09:20:03 UTC

```
Find operational recommendation text in report.tex:
grep -n "band 13.*24\|depositing.*edit\|practical recommendation\|select layer sets\|band-mass overlap\|O_\mathrm{cos}.*O_\mathrm{band\|O_\mathrm{band.*O_\mathrm{cos}\|layer sets" report.tex
```

### [11] TOOL RESULT — Bash [ERROR] · 2026-09-25 09:20:03 UTC

```
Error: Exit code 2
ugrep: error: error at position 102
|select layer sets\|band-mass overlap\|O_\mathrm{cos}.*O_\mathrm{band\|O_\mathr
                        invalid escape___/
```

### [12] TOOL CALL — Bash · 2026-09-25 09:20:07 UTC

```
Find operational recommendation text in report.tex:
grep -n "band 13" report.tex; echo "==="; grep -n "depositing" report.tex; echo "==="; grep -n "practical recommendation" report.tex; echo "==="; grep -n "band-mass" report.tex; echo "==="; grep -n "select layer" report.tex
```

### [13] TOOL RESULT — Bash · 2026-09-25 09:20:09 UTC

```
{"stdout": "642:\\corr{4} The band-mass regression's evidence is model-specific and weaker than previously stated. The SL band 13--24 coefficient is +0.156 with CI [$-$0.240, 0.529], which does not reach significance; the dominant SL term is the English refusal rate (coefficient 0.855).\n830:  \\caption{Per-layer refusal drop from single-site ablation in Gemma, for English (blue) and Slovene (orange). The profile peaks at layer 19 (EN) and 16 (SL), with most write mass in band 13--24.}\n914:  \\caption{Per-layer refusal drop from single-site ablation in GaMS3. The profile peaks at layer 27 (both EN and SL), in band 25--36, but the behavioural winner at matched energy is band 13--24, the same as in Gemma.}\n===\n===\n===\n642:\\corr{4} The band-mass regression's evidence is model-specific and weaker than previously stated. The SL band 13--24 coefficient is +0.156 with CI [$-$0.240, 0.529], which does not reach significance; the dominant SL term is the English refusal rate (coefficient 0.855).\n===", "stderr": "", "interrupted": false, "isImage": false, "returnCodeInterpretation": "No matches found", "noOutputExpected": false}
```

### [14] TOOL CALL — Bash · 2026-09-25 09:20:13 UTC

```
Find placement-related text:
grep -n "placement" report.tex | head -20
```

### [15] TOOL RESULT — Bash · 2026-09-25 09:20:13 UTC

```
{"stdout": "690:logE + placement (band masses) & 0.718 \\\\\n704:\\label{tab:exp10_placement}\n818:Iteration~4 was designed to close three remaining gaps: (1)~the placement finding rests on the exploratory band-density correlation without a causal mechanism; (2)~the result is Gemma-only; and (3)~Heretic's keyword blindness was demonstrated qualitatively but not quantified.\n849:Best placement: L16--31 vs L33--48 & 0.07 vs 0.92 & 0.27 vs 0.92 \\\\\n948:\\textbf{Placement vs dose dissociation (A1--A4 ladder).} \\corr{5} All four contrasts are Slovene strict. At fixed placement, increasing dose reduces Slovene strict refusal: dose at fixed $O_\\mathrm{ship}$ $-$0.186 [$-$0.286, $-$0.086]; dose at fixed $O_\\mathrm{swap}$ $-$0.157 [$-$0.257, $-$0.071]. At fixed dose, swapping placement does not significantly change refusal: placement at fixed high E $-$0.029 [$-$0.129, +0.071], McNemar $p$ 0.774; placement at fixed low E +0.000 [$-$0.086, +0.071], $p$ 1.000.\n1047:The surviving positive finding is a matched-total-energy AND matched-layer-count placement contrast. Li et al.~[19] (ICLR 2025) already localise contiguous middle safety layers; Bosco and Srinivasan~[20] locate refusal beyond attention. What this study adds is the energy- and count-matched construction plus the dose rival's failure.\n1095:F15 & Killed & Effective depth region differs between siblings & DEV band NAMED\\_AND\\_LOST; placement $p$=0.774 \\\\\n1116:U8 && Racing placement against published cheap predictors & Identified only in positioning; not run \\\\\n1142:\\item Layer sensitivity differs per language: NARROWED (covered by [25]; claim is only the edit-placement consequence).\n1143:\\item Failed dose rival at matched placement: KEPT.\n1164:\\textbf{Firm positive: matched-budget placement orders residual refusal.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The band is shared; the residual is not. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [16] ASSISTANT · 2026-09-25 09:20:20 UTC

```
Now let me read the key sections that need editing — the "What We Have Learned" section and the "Best Result" section of the executive summary.
```

### [17] TOOL CALL — Read · 2026-09-25 09:20:20 UTC

```
/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex
```

### [18] TOOL RESULT — Read · 2026-09-25 09:20:20 UTC

```
{"type": "text", "file": {"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex", "content": "\\begin{figure}[!htbp]\n  \\centering\n  \\includegraphics[width=\\linewidth,height=0.85\\textheight,keepaspectratio]{figures/fig_refusal_gap_v0.pdf}\n  \\caption{The Gemma edit S5X paired EN--SL refusal gap under three scoring methods. The gap ranges from +0.06 (keyword strict) to +0.69 (Qwen3-14B strict); the PARTIAL class is the wedge.}\n  \\label{fig:refusal_gap}\n\\end{figure}\n\nFive iterations have converged on a picture with one firm positive, one transferable negative, a structural measurement finding, and seventeen falsified predictions.\n\n\\textbf{Firm positive: matched-budget placement orders residual refusal.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The band is shared; the residual is not. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).\n\n\\textbf{Transferable negative: the activation-space depth index fails to predict weight-edit outcomes.} Spearman $-$0.009 over 21 rows (comparing Gemma with Qwen3-8B, plus excluded Mistral). The EN/SL direction cosine fails beside it (Spearman +0.010). Two baselines beat both: single-site causal transfer rate +0.732 and unedited model's own refusal rate +0.661.\n\n\\textbf{Structural measurement finding: the keyword objective is cross-lingually biased.} On verified translation pairs, $\\Delta_\\mathrm{lang}$~=~$-$1.56 [$-$1.68, $-$1.44]: the English keyword rule over-reports in English (FP rate 0.78) and is silent in Slovene (FN rate 0.82). Threshold blindness is 1.0 in both searches. The pre-registered prediction that one search is blinder overall was FALSIFIED.\n\n\\textbf{Seventeen hypotheses falsified} across five iterations (F1--F17): depth coverage (F1), broad-beats-narrow (F2), count-based cross-model index (F3), direction cosine (F4), corrected objective (F5), exposure differential (F6), r\\_prior (F7), thin-margin (F8), static geometry (F9), language-identity lever (F10), depth index difference (F11), random controls (F12), conformal forecasting (F13), batch interchangeability (F14), sibling band difference (F15), language band difference (F16), and anchor blinder (F17).\n\n\\textbf{The headline gap stated as a range.} The Gemma edit S5X paired EN--SL gap ranges from +0.06 (keyword strict) to +0.69 (Qwen3-14B strict), with the broad definition at +0.23. On GaMS3, all judges agree the gap is near zero. The PARTIAL class (0.548 of Gemma edit EN outputs) is the wedge. The Slovene judge certification gate was not met ($\\kappa$ 0.723 $<$ 0.80), so all Slovene gap claims remain judge-sensitive. 94--95\\% of edited English outputs were truncated at the 256-token generation cap.\n\n\\textbf{Scope and limits.} Two sibling checkpoints of one architecture plus one outside family; one non-English language in the matched panels (two further languages only in the outside-family arm); one or two optimiser seeds; NF4 throughout with a single bf16 control cell (paired SL--EN gap bf16 +0.60 [+0.40, +0.80] vs NF4 +0.45 [+0.20, +0.70], not resolved but the asymmetry is at least as large in bf16); Slovene material machine-translated with native review PENDING. Two checkpoints are two units, not a population: nothing is attributed to Slovene continual pretraining, instruction tuning, or any safety-training stage. Five packets totalling 640 items remain pending for native-speaker labelling. Every judged rate in the report is proxy-certified, not human-certified. 136 numbers independently re-derived in iteration~5; defect rate 15.4\\% [10.3\\%, 22.5\\%] on previously unaudited sections.\n\n\n%% ======================================================================\n\\section{Run Trajectory}\\label{sec:trajectory}\n\n\\begin{table}[!htbp]\n\\centering\n\\caption{Run trajectory: one row per iteration. ``Ledger spend'' is cumulative LLM/tool/container spend billed through that iteration; it excludes compute-rental time and is not the run's total cost.}\n\\label{tab:trajectory}\n\\small", "numLines": 30, "startLine": 1155, "totalLines": 1236}}
```

### [19] TOOL CALL — Read · 2026-09-25 09:20:20 UTC

```
/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex
```

### [20] TOOL RESULT — Read · 2026-09-25 09:20:20 UTC

```
{"type": "text", "file": {"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex", "content": "\\documentclass[11pt,letterpaper]{article}\n\\usepackage{graphicx, geometry, amsmath, hyperref, url, booktabs, xcolor, float, array}\n\\geometry{margin=1in}\n\\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\n\\title{Executive Summary:\\\\What English-Tuned Abliteration Misses in Slovene}\n\\author{}\n\\date{September 2026}\n\n\\begin{document}\n\\maketitle\n\n\\section{Goal}\n\nThis study asks whether abliteration---removing refusal behaviour by orthogonalising weights against an English-extracted ``refusal direction''---transfers to Slovene. Two sibling 12B models from the Gemma-3 family were compared: \\texttt{google/gemma-3-12b-it} (English-centric) and \\texttt{cjvt/GaMS3-12B-Instruct} (Slovene continual-pretraining variant), both under NF4 quantisation. The study ran five iterations with pre-registered predictions, independent audits, and 17 falsified hypotheses.\n\n\\section{What Was Tried}\n\n\\begin{itemize}\n\\item \\textbf{Matched Heretic abliteration} (116 TPE trials per model, identical seed) to produce abliterated checkpoints, scored bilingually with keyword markers and LLM judges.\n\\item \\textbf{Refusal-direction transfer screen}: $2\\times2$ source-language $\\times$ evaluation-language ablation matrix, increment tests, and matched-efficacy controls.\n\\item \\textbf{Surrogacy panels} (exp6, exp7): 200+ Heretic edits per model, measuring whether English refusal outcomes predict Slovene outcomes.\n\\item \\textbf{Causal mechanism tests} (exp8): activation steering and weight-edit arms to isolate the Slovene residual.\n\\item \\textbf{Coverage $\\times$ strength factorial} (exp9, exp10): 122 and 57 cells testing whether depth coverage or total edit energy governs Slovene refusal survival.\n\\item \\textbf{Causal write-profile measurement} (exp13, exp14): single-layer edits at all 48 layers, plus an energy-normalised overlap instrument $O$.\n\\item \\textbf{Gradient-blind fraction} (exp15): quantifying Heretic's keyword objective's structural blindness.\n\\item \\textbf{Corrected objective} (exp11): replacing keywords with a partial-aware classifier and re-running selection.\n\\item \\textbf{Cross-model replication} (exp12): Qwen3-8B and Mistral-7B across EN/SL/DE/LT.\n\\item \\textbf{Three independent audit/recompute passes} (eval1--eval4) checking 400+ numbers.\n\\end{itemize}\n\n\\section{Key Results}\n\n\\begin{enumerate}\n\\item \\textbf{GaMS3's edit works bilingually; Gemma's does not.} GaMS3's abliteration reduced refusal from 100\\% to $\\sim$6\\% in both EN and SL. Gemma's edit reduced EN refusal from 99\\% to 70\\% but left SL refusal at 95\\% (T1, S4 held-out, judged).\n\n\\item \\textbf{The gap is judge-sensitive.} On S5X paired translations (Gemma edit), the EN--SL gap ranges from +0.06 (keyword) to +0.69 (strict judge), with the broad definition at +0.23. The PARTIAL class (54.8\\% of Gemma edit EN outputs) is the wedge.\n\n\\item \\textbf{Placement orders residual refusal at matched budget.} At matched total removal energy AND matched layer count, where in depth the edit deposits energy orders how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. Two cheap one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument.\n\n\\item \\textbf{The activation-space depth index fails cross-model.} Spearman = $-$0.009 over 21 model-language-weight cells. Two baselines beat both the index and the geometric predictor.\n\n\\item \\textbf{The keyword objective is cross-lingually biased.} $\\Delta_\\mathrm{lang} = -1.56$ [$-1.68$, $-1.44$]: the English keyword rule over-reports in English (FP rate 0.78) and is silent in Slovene (FN rate 0.82). Threshold blindness fraction = 1.0 in both searches.\n\n\\item \\textbf{Utility is unaffected.} All macro utility changes were $\\leq$0.20 points; FLORES+ NLL shifts were $\\leq$0.002 nats/token.\n\\end{enumerate}\n\n\\section{What Failed}\n\nSeventeen hypotheses were falsified (F1--F17). The most consequential:\n\\begin{itemize}\n\\item \\textbf{Depth coverage explains the gap} (F1): $\\Delta R^2 = 0.040$, LOO $-0.002$.\n\\item \\textbf{Broad-and-weak beats narrow-and-strong} (F2): falsified opposite ($-0.10$).\n\\item \\textbf{Corrected objective produces a better edit} (F5): dose-scaling the keyword edit achieved comparable gap reduction at lower KL.\n\\item \\textbf{r\\_prior direction carries Slovene residual} (F7): causal cut 0.036 $<$ best random control 0.074.\n\\item \\textbf{Count-based depth index predicts cross-model} (F3): Spearman $-0.009$.\n\\item \\textbf{Anchor search is blinder overall} (F17): paired GBF difference +0.006; judge-referenced reverses.\n\\end{itemize}\n\n\\section{Best Result}\n\nThe firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.\n\nOn the guard side, the official RefusEU ASR (Llama-Guard-3-8B + PolyGuard agreement) for the Gemma edit is EN 0.738 vs SL 0.103 = +0.635 gap, confirming the behavioural asymmetry with an independent safety metric.\n\n\\section{Open Questions}\n\n\\begin{enumerate}\n\\item \\textbf{Native-speaker validation.} All Slovene material is machine-translated (Gemini-2.5-flash); five packets (640 items) await native-speaker labelling.\n\\item \\textbf{Slovene judge certification.} The SL judge gate was not met ($\\kappa = 0.723 < 0.80$); all SL gap claims are JUDGE\\_SENSITIVE.\n\\item \\textbf{NF4 confound.} Paired bf16 vs NF4 gap: bf16 +0.60 vs NF4 +0.45 ($n = 20$, not resolved). The asymmetry is at least as large in bf16.\n\\item \\textbf{Two checkpoints $\\neq$ a population.} Nothing is attributed to continual pretraining, instruction tuning, or any training stage.\n\\item \\textbf{Optimizer variance.} One seed per model; prompt-level CIs do not capture run-to-run optimizer variance.\n\\item \\textbf{Placement at the floor.} The placement contrast is strongest mid-range; at shipped-edit refusal levels, dose dominates ($p = 0.774$ for placement swap).\n\\item \\textbf{Defect rate.} 136 numbers independently re-derived; defect rate 15.4\\% [10.3\\%, 22.5\\%] on previously unaudited sections. No sign reversals.\n\\end{enumerate}\n\n\\end{document}\n", "numLines": 81, "startLine": 1, "totalLines": 81}}
```

### [21] ASSISTANT · 2026-09-25 09:20:40 UTC

```
I can see the sections that need editing. The key changes:

1. **report.tex line 1164**: Reframe the "Firm positive" as a measurement finding, remove the operational framing about where to deposit edits
2. **exec_summary.tex lines 41, 64**: Remove the placement recommendation and band-specific configuration advice

Let me make the edits.
```

### [22] TOOL CALL — Edit · 2026-09-25 09:20:40 UTC

```
File: /ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex
OLD: \textbf{Firm positive: matched-budget placement orders residual refusal.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The band is shared; the residual is not. The English causal write profile predicts the Slovene residual at $\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). Two one-forward-pass baselines ($O_\mathrm{cos}$ and $O_\mathrm{band4}$) match or beat the expensive single-layer causal instrument. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).
NEW: \textbf{Firm positive: residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit is applied predicts how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B). Doubling the dose of a misplaced edit does not recover the effect of a well-placed one at the same budget. The English causal write profile predicts the Slovene residual at $\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). This means that evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength: a cross-lingual gap measured at one placement may shrink or vanish at another. Two one-forward-pass baselines ($O_\mathrm{cos}$ and $O_\mathrm{band4}$) match or beat the expensive single-layer causal instrument at predicting residual refusal. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).
```

### [23] TOOL RESULT — Edit · 2026-09-25 09:20:40 UTC

```
{"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex", "oldString": "\\textbf{Firm positive: matched-budget placement orders residual refusal.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The band is shared; the residual is not. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).", "newString": "\\textbf{Firm positive: residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit is applied predicts how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B). Doubling the dose of a misplaced edit does not recover the effect of a well-placed one at the same budget. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). This means that evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength: a cross-lingual gap measured at one placement may shrink or vanish at another. Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument at predicting residual refusal. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).", "originalFile": null, "structuredPatch": [{"oldStart": 1161, "oldLines": 7, "newStart": 1161, "newLines": 7, "lines": [" ", " Five iterations have converged on a picture with one firm positive, one transferable negative, a structural measurement finding, and seventeen falsified predictions.", " ", "-\\textbf{Firm positive: matched-budget placement orders residual refusal.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit deposits that energy orders how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B), and not recoverable by doubling the dose of a badly placed edit. The band is shared; the residual is not. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).", "+\\textbf{Firm positive: residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth an English-derived refusal edit is applied predicts how much refusal survives: in both languages, in two sibling checkpoints, and in an outside family (Qwen3-8B). Doubling the dose of a misplaced edit does not recover the effect of a well-placed one at the same budget. The English causal write profile predicts the Slovene residual at $\\rho$ $-$0.94, so the language-label placebo does not collapse; what differs by language is how much refusal is left at the same placement and energy (strict refusal EN 0.07 vs SL 0.27 in group G3). This means that evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength: a cross-lingual gap measured at one placement may shrink or vanish at another. Two one-forward-pass baselines ($O_\\mathrm{cos}$ and $O_\\mathrm{band4}$) match or beat the expensive single-layer causal instrument at predicting residual refusal. At the refusal floor of shipped edits, dose not placement is the active variable ($p$~0.774 / 1.000).", " ", " \\textbf{Transferable negative: the activation-space depth index fails to predict weight-edit outcomes.} Spearman $-$0.009 over 21 rows (comparing Gemma with Qwen3-8B, plus excluded Mistral). The EN/SL direction cosine fails beside it (Spearman +0.010). Two baselines beat both: single-site causal transfer rate +0.732 and unedited model's own refusal rate +0.661.", " "]}], "userModified": false, "replaceAll": false, "contentNotInModelContext": true}
```

### [24] ASSISTANT · 2026-09-25 09:20:48 UTC

```
Now the executive summary — Key Results item 3 and the Best Result section.
```

### [25] TOOL CALL — Edit · 2026-09-25 09:20:48 UTC

```
File: /ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex
OLD: \item \textbf{Placement orders residual refusal at matched budget.} At matched total removal energy AND matched layer count, where in depth the edit deposits energy orders how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. Two cheap one-forward-pass baselines ($O_\mathrm{cos}$, $O_\mathrm{band4}$) match or beat the expensive causal instrument.
NEW: \item \textbf{Residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth the edit is applied predicts how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. This means evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength. Two one-forward-pass baselines ($O_\mathrm{cos}$, $O_\mathrm{band4}$) match or beat the expensive causal instrument at predicting residual refusal.
```

### [26] TOOL RESULT — Edit · 2026-09-25 09:20:48 UTC

```
{"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex", "oldString": "\\item \\textbf{Placement orders residual refusal at matched budget.} At matched total removal energy AND matched layer count, where in depth the edit deposits energy orders how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. Two cheap one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument.", "newString": "\\item \\textbf{Residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth the edit is applied predicts how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. This means evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength. Two one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument at predicting residual refusal.", "originalFile": "\\documentclass[11pt,letterpaper]{article}\n\\usepackage{graphicx, geometry, amsmath, hyperref, url, booktabs, xcolor, float, array}\n\\geometry{margin=1in}\n\\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\n\\title{Executive Summary:\\\\What English-Tuned Abliteration Misses in Slovene}\n\\author{}\n\\date{September 2026}\n\n\\begin{document}\n\\maketitle\n\n\\section{Goal}\n\nThis study asks whether abliteration---removing refusal behaviour by orthogonalising weights against an English-extracted ``refusal direction''---transfers to Slovene. Two sibling 12B models from the Gemma-3 family were compared: \\texttt{google/gemma-3-12b-it} (English-centric) and \\texttt{cjvt/GaMS3-12B-Instruct} (Slovene continual-pretraining variant), both under NF4 quantisation. The study ran five iterations with pre-registered predictions, independent audits, and 17 falsified hypotheses.\n\n\\section{What Was Tried}\n\n\\begin{itemize}\n\\item \\textbf{Matched Heretic abliteration} (116 TPE trials per model, identical seed) to produce abliterated checkpoints, scored bilingually with keyword markers and LLM judges.\n\\item \\textbf{Refusal-direction transfer screen}: $2\\times2$ source-language $\\times$ evaluation-language ablation matrix, increment tests, and matched-efficacy controls.\n\\item \\textbf{Surrogacy panels} (exp6, exp7): 200+ Heretic edits per model, measuring whether English refusal outcomes predict Slovene outcomes.\n\\item \\textbf{Causal mechanism tests} (exp8): activation steering and weight-edit arms to isolate the Slovene residual.\n\\item \\textbf{Coverage $\\times$ strength factorial} (exp9, exp10): 122 and 57 cells testing whether depth coverage or total edit energy governs Slovene refusal survival.\n\\item \\textbf{Causal write-profile measurement} (exp13, exp14): single-layer edits at all 48 layers, plus an energy-normalised overlap instrument $O$.\n\\item \\textbf{Gradient-blind fraction} (exp15): quantifying Heretic's keyword objective's structural blindness.\n\\item \\textbf{Corrected objective} (exp11): replacing keywords with a partial-aware classifier and re-running selection.\n\\item \\textbf{Cross-model replication} (exp12): Qwen3-8B and Mistral-7B across EN/SL/DE/LT.\n\\item \\textbf{Three independent audit/recompute passes} (eval1--eval4) checking 400+ numbers.\n\\end{itemize}\n\n\\section{Key Results}\n\n\\begin{enumerate}\n\\item \\textbf{GaMS3's edit works bilingually; Gemma's does not.} GaMS3's abliteration reduced refusal from 100\\% to $\\sim$6\\% in both EN and SL. Gemma's edit reduced EN refusal from 99\\% to 70\\% but left SL refusal at 95\\% (T1, S4 held-out, judged).\n\n\\item \\textbf{The gap is judge-sensitive.} On S5X paired translations (Gemma edit), the EN--SL gap ranges from +0.06 (keyword) to +0.69 (strict judge), with the broad definition at +0.23. The PARTIAL class (54.8\\% of Gemma edit EN outputs) is the wedge.\n\n\\item \\textbf{Placement orders residual refusal at matched budget.} At matched total removal energy AND matched layer count, where in depth the edit deposits energy orders how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. Two cheap one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument.\n\n\\item \\textbf{The activation-space depth index fails cross-model.} Spearman = $-$0.009 over 21 model-language-weight cells. Two baselines beat both the index and the geometric predictor.\n\n\\item \\textbf{The keyword objective is cross-lingually biased.} $\\Delta_\\mathrm{lang} = -1.56$ [$-1.68$, $-1.44$]: the English keyword rule over-reports in English (FP rate 0.78) and is silent in Slovene (FN rate 0.82). Threshold blindness fraction = 1.0 in both searches.\n\n\\item \\textbf{Utility is unaffected.} All macro utility changes were $\\leq$0.20 points; FLORES+ NLL shifts were $\\leq$0.002 nats/token.\n\\end{enumerate}\n\n\\section{What Failed}\n\nSeventeen hypotheses were falsified (F1--F17). The most consequential:\n\\begin{itemize}\n\\item \\textbf{Depth coverage explains the gap} (F1): $\\Delta R^2 = 0.040$, LOO $-0.002$.\n\\item \\textbf{Broad-and-weak beats narrow-and-strong} (F2): falsified opposite ($-0.10$).\n\\item \\textbf{Corrected objective produces a better edit} (F5): dose-scaling the keyword edit achieved comparable gap reduction at lower KL.\n\\item \\textbf{r\\_prior direction carries Slovene residual} (F7): causal cut 0.036 $<$ best random control 0.074.\n\\item \\textbf{Count-based depth index predicts cross-model} (F3): Spearman $-0.009$.\n\\item \\textbf{Anchor search is blinder overall} (F17): paired GBF difference +0.006; judge-referenced reverses.\n\\end{itemize}\n\n\\section{Best Result}\n\nThe firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.\n\nOn the guard side, the official RefusEU ASR (Llama-Guard-3-8B + PolyGuard agreement) for the Gemma edit is EN 0.738 vs SL 0.103 = +0.635 gap, confirming the behavioural asymmetry with an independent safety metric.\n\n\\section{Open Questions}\n\n\\begin{enumerate}\n\\item \\textbf{Native-speaker validation.} All Slovene material is machine-translated (Gemini-2.5-flash); five packets (640 items) await native-speaker labelling.\n\\item \\textbf{Slovene judge certification.} The SL judge gate was not met ($\\kappa = 0.723 < 0.80$); all SL gap claims are JUDGE\\_SENSITIVE.\n\\item \\textbf{NF4 confound.} Paired bf16 vs NF4 gap: bf16 +0.60 vs NF4 +0.45 ($n = 20$, not resolved). The asymmetry is at least as large in bf16.\n\\item \\textbf{Two checkpoints $\\neq$ a population.} Nothing is attributed to continual pretraining, instruction tuning, or any training stage.\n\\item \\textbf{Optimizer variance.} One seed per model; prompt-level CIs do not capture run-to-run optimizer variance.\n\\item \\textbf{Placement at the floor.} The placement contrast is strongest mid-range; at shipped-edit refusal levels, dose dominates ($p = 0.774$ for placement swap).\n\\item \\textbf{Defect rate.} 136 numbers independently re-derived; defect rate 15.4\\% [10.3\\%, 22.5\\%] on previously unaudited sections. No sign reversals.\n\\end{enumerate}\n\n\\end{document}\n", "structuredPatch": [{"oldStart": 38, "oldLines": 7, "newStart": 38, "newLines": 7, "lines": [" ", " \\item \\textbf{The gap is judge-sensitive.} On S5X paired translations (Gemma edit), the EN--SL gap ranges from +0.06 (keyword) to +0.69 (strict judge), with the broad definition at +0.23. The PARTIAL class (54.8\\% of Gemma edit EN outputs) is the wedge.", " ", "-\\item \\textbf{Placement orders residual refusal at matched budget.} At matched total removal energy AND matched layer count, where in depth the edit deposits energy orders how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. Two cheap one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument.", "+\\item \\textbf{Residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth the edit is applied predicts how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. This means evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength. Two one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument at predicting residual refusal.", " ", " \\item \\textbf{The activation-space depth index fails cross-model.} Spearman = $-$0.009 over 21 model-language-weight cells. Two baselines beat both the index and the geometric predictor.", " "]}], "userModified": false, "replaceAll": false, "contentNotInModelContext": true}
```

### [27] TOOL CALL — Edit · 2026-09-25 09:21:00 UTC

```
File: /ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex
OLD: The firm positive is a \textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.
NEW: The firm positive is a \textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, the depth placement of the edit predicts how much refusal survives. Matched-energy edits at different placements produced Slovene strict refusal rates ranging from 0.27 to 0.92 depending on placement alone. This held for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). The implication for cross-lingual refusal evaluation is that placement is a confound: a cross-lingual gap measured at one placement may not generalise to another, so evaluation protocols that compare refusal across languages must control for edit placement, not only total edit strength.
```

### [28] TOOL RESULT — Edit · 2026-09-25 09:21:00 UTC

```
{"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/exec_summary.tex", "oldString": "The firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.", "newString": "The firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, the depth placement of the edit predicts how much refusal survives. Matched-energy edits at different placements produced Slovene strict refusal rates ranging from 0.27 to 0.92 depending on placement alone. This held for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). The implication for cross-lingual refusal evaluation is that placement is a confound: a cross-lingual gap measured at one placement may not generalise to another, so evaluation protocols that compare refusal across languages must control for edit placement, not only total edit strength.", "originalFile": "\\documentclass[11pt,letterpaper]{article}\n\\usepackage{graphicx, geometry, amsmath, hyperref, url, booktabs, xcolor, float, array}\n\\geometry{margin=1in}\n\\hypersetup{colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black}\n\\usepackage[T1]{fontenc}\n\\usepackage[utf8]{inputenc}\n\n\\title{Executive Summary:\\\\What English-Tuned Abliteration Misses in Slovene}\n\\author{}\n\\date{September 2026}\n\n\\begin{document}\n\\maketitle\n\n\\section{Goal}\n\nThis study asks whether abliteration---removing refusal behaviour by orthogonalising weights against an English-extracted ``refusal direction''---transfers to Slovene. Two sibling 12B models from the Gemma-3 family were compared: \\texttt{google/gemma-3-12b-it} (English-centric) and \\texttt{cjvt/GaMS3-12B-Instruct} (Slovene continual-pretraining variant), both under NF4 quantisation. The study ran five iterations with pre-registered predictions, independent audits, and 17 falsified hypotheses.\n\n\\section{What Was Tried}\n\n\\begin{itemize}\n\\item \\textbf{Matched Heretic abliteration} (116 TPE trials per model, identical seed) to produce abliterated checkpoints, scored bilingually with keyword markers and LLM judges.\n\\item \\textbf{Refusal-direction transfer screen}: $2\\times2$ source-language $\\times$ evaluation-language ablation matrix, increment tests, and matched-efficacy controls.\n\\item \\textbf{Surrogacy panels} (exp6, exp7): 200+ Heretic edits per model, measuring whether English refusal outcomes predict Slovene outcomes.\n\\item \\textbf{Causal mechanism tests} (exp8): activation steering and weight-edit arms to isolate the Slovene residual.\n\\item \\textbf{Coverage $\\times$ strength factorial} (exp9, exp10): 122 and 57 cells testing whether depth coverage or total edit energy governs Slovene refusal survival.\n\\item \\textbf{Causal write-profile measurement} (exp13, exp14): single-layer edits at all 48 layers, plus an energy-normalised overlap instrument $O$.\n\\item \\textbf{Gradient-blind fraction} (exp15): quantifying Heretic's keyword objective's structural blindness.\n\\item \\textbf{Corrected objective} (exp11): replacing keywords with a partial-aware classifier and re-running selection.\n\\item \\textbf{Cross-model replication} (exp12): Qwen3-8B and Mistral-7B across EN/SL/DE/LT.\n\\item \\textbf{Three independent audit/recompute passes} (eval1--eval4) checking 400+ numbers.\n\\end{itemize}\n\n\\section{Key Results}\n\n\\begin{enumerate}\n\\item \\textbf{GaMS3's edit works bilingually; Gemma's does not.} GaMS3's abliteration reduced refusal from 100\\% to $\\sim$6\\% in both EN and SL. Gemma's edit reduced EN refusal from 99\\% to 70\\% but left SL refusal at 95\\% (T1, S4 held-out, judged).\n\n\\item \\textbf{The gap is judge-sensitive.} On S5X paired translations (Gemma edit), the EN--SL gap ranges from +0.06 (keyword) to +0.69 (strict judge), with the broad definition at +0.23. The PARTIAL class (54.8\\% of Gemma edit EN outputs) is the wedge.\n\n\\item \\textbf{Residual refusal depends on edit placement, not only on total energy.} At matched total removal energy AND matched layer count, where in depth the edit is applied predicts how much refusal survives---in both languages, in both sibling checkpoints, and in Qwen3-8B. This means evaluating refusal-edit transfer across languages requires controlling for edit placement, not only total edit strength. Two one-forward-pass baselines ($O_\\mathrm{cos}$, $O_\\mathrm{band4}$) match or beat the expensive causal instrument at predicting residual refusal.\n\n\\item \\textbf{The activation-space depth index fails cross-model.} Spearman = $-$0.009 over 21 model-language-weight cells. Two baselines beat both the index and the geometric predictor.\n\n\\item \\textbf{The keyword objective is cross-lingually biased.} $\\Delta_\\mathrm{lang} = -1.56$ [$-1.68$, $-1.44$]: the English keyword rule over-reports in English (FP rate 0.78) and is silent in Slovene (FN rate 0.82). Threshold blindness fraction = 1.0 in both searches.\n\n\\item \\textbf{Utility is unaffected.} All macro utility changes were $\\leq$0.20 points; FLORES+ NLL shifts were $\\leq$0.002 nats/token.\n\\end{enumerate}\n\n\\section{What Failed}\n\nSeventeen hypotheses were falsified (F1--F17). The most consequential:\n\\begin{itemize}\n\\item \\textbf{Depth coverage explains the gap} (F1): $\\Delta R^2 = 0.040$, LOO $-0.002$.\n\\item \\textbf{Broad-and-weak beats narrow-and-strong} (F2): falsified opposite ($-0.10$).\n\\item \\textbf{Corrected objective produces a better edit} (F5): dose-scaling the keyword edit achieved comparable gap reduction at lower KL.\n\\item \\textbf{r\\_prior direction carries Slovene residual} (F7): causal cut 0.036 $<$ best random control 0.074.\n\\item \\textbf{Count-based depth index predicts cross-model} (F3): Spearman $-0.009$.\n\\item \\textbf{Anchor search is blinder overall} (F17): paired GBF difference +0.006; judge-referenced reverses.\n\\end{itemize}\n\n\\section{Best Result}\n\nThe firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.\n\nOn the guard side, the official RefusEU ASR (Llama-Guard-3-8B + PolyGuard agreement) for the Gemma edit is EN 0.738 vs SL 0.103 = +0.635 gap, confirming the behavioural asymmetry with an independent safety metric.\n\n\\section{Open Questions}\n\n\\begin{enumerate}\n\\item \\textbf{Native-speaker validation.} All Slovene material is machine-translated (Gemini-2.5-flash); five packets (640 items) await native-speaker labelling.\n\\item \\textbf{Slovene judge certification.} The SL judge gate was not met ($\\kappa = 0.723 < 0.80$); all SL gap claims are JUDGE\\_SENSITIVE.\n\\item \\textbf{NF4 confound.} Paired bf16 vs NF4 gap: bf16 +0.60 vs NF4 +0.45 ($n = 20$, not resolved). The asymmetry is at least as large in bf16.\n\\item \\textbf{Two checkpoints $\\neq$ a population.} Nothing is attributed to continual pretraining, instruction tuning, or any training stage.\n\\item \\textbf{Optimizer variance.} One seed per model; prompt-level CIs do not capture run-to-run optimizer variance.\n\\item \\textbf{Placement at the floor.} The placement contrast is strongest mid-range; at shipped-edit refusal levels, dose dominates ($p = 0.774$ for placement swap).\n\\item \\textbf{Defect rate.} 136 numbers independently re-derived; defect rate 15.4\\% [10.3\\%, 22.5\\%] on previously unaudited sections. No sign reversals.\n\\end{enumerate}\n\n\\end{document}\n", "structuredPatch": [{"oldStart": 61, "oldLines": 7, "newStart": 61, "newLines": 7, "lines": [" ", " \\section{Best Result}", " ", "-The firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, depositing the edit in band 13--24 (the causal write-profile peak) reduces Slovene refusal from 0.92 to 0.27, while the same energy in band 33--48 leaves it at 0.92. This holds for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). Two cheap baselines match the expensive instrument, so the practical recommendation is: use energy-weighted cosine or band-mass overlap to select layer sets, not the full causal write profile.", "+The firm positive is a \\textbf{matched-budget placement contrast}: at fixed total edit energy and fixed layer count, the depth placement of the edit predicts how much refusal survives. Matched-energy edits at different placements produced Slovene strict refusal rates ranging from 0.27 to 0.92 depending on placement alone. This held for Gemma, GaMS3, and Qwen3-8B. At the refusal floor of shipped edits, however, dose---not placement---is the active variable ($p = 0.774$). The implication for cross-lingual refusal evaluation is that placement is a confound: a cross-lingual gap measured at one placement may not generalise to another, so evaluation protocols that compare refusal across languages must control for edit placement, not only total edit strength.", " ", " On the guard side, the official RefusEU ASR (Llama-Guard-3-8B + PolyGuard agreement) for the Gemma edit is EN 0.738 vs SL 0.103 = +0.635 gap, confirming the behavioural asymmetry with an independent safety metric.", " "]}], "userModified": false, "replaceAll": false, "contentNotInModelContext": true}
```

### [29] ASSISTANT · 2026-09-25 09:21:06 UTC

```
Now let me check for any remaining operational language in the report body sections (the experiment sections themselves should stay as measurements, but let me verify the captions and GaMS3 profile caption).
```

### [30] TOOL CALL — Read · 2026-09-25 09:21:06 UTC

```
/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex
```

### [31] TOOL RESULT — Read · 2026-09-25 09:21:06 UTC

```
{"type": "text", "file": {"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex", "content": "\n\\begin{figure}[!htbp]\n  \\centering\n  \\includegraphics[width=\\linewidth,height=0.85\\textheight,keepaspectratio]{figures/fig_gams3_profile_v0.pdf}\n  \\caption{Per-layer refusal drop from single-site ablation in GaMS3. The profile peaks at layer 27 (both EN and SL), in band 25--36, but the behavioural winner at matched energy is band 13--24, the same as in Gemma.}\n  \\label{fig:gams3_profile}\n\\end{figure}\n", "numLines": 8, "startLine": 910, "totalLines": 1236}}
```

### [32] ASSISTANT · 2026-09-25 09:21:12 UTC

```
That caption states a measurement result (which band achieved lowest residual), not an operational recommendation. The "band 13--24" references in experiment sections (exp9, exp10, exp13, exp14) and figure captions are recording what was observed — those stay. Let me also check the Research 1 positioning section.
```

### [33] TOOL CALL — Read · 2026-09-25 09:21:12 UTC

```
/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex
```

### [34] TOOL RESULT — Read · 2026-09-25 09:21:12 UTC

```
{"type": "text", "file": {"filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/report.tex", "content": "\\textbf{Independent recompute.} 102 numbers checked: 97 match, 3 misdescribed, 2 mismatch. Rate 4.9\\% [2.1, 11.0]. All placebos collapse.\n\n\n\\subsection{Research 1: Novelty Positioning}\\label{sec:research1}\n\n\\textbf{Goal (gen\\_art\\_research\\_1, iteration~4).} Establish what the surviving results add relative to published work.\n\nThe surviving positive finding is a matched-total-energy AND matched-layer-count placement contrast. Li et al.~[19] (ICLR 2025) already localise contiguous middle safety layers; Bosco and Srinivasan~[20] locate refusal beyond attention. What this study adds is the energy- and count-matched construction plus the dose rival's failure.\n\nThe negative finding---that an activation-space depth measurement fails to predict weight-edit outcomes---positions against Jiang~[21] and AdvPrefix~[22]. \\corr{5} AdvPrefix repositioned from the depth result to the selection-blindness companion.\n\n\n%% ======================================================================\n\\section{Iteration 5}\\label{sec:iter5}\n", "numLines": 15, "startLine": 1040, "totalLines": 1236}}
```

### [35] ASSISTANT · 2026-09-25 09:21:20 UTC

```
The Research 1 section describes what was found relative to literature — it's a measurement positioning statement, not an operational recommendation. It stays.

Now let me also check the iteration-4 "Best placement" table row and the exp13 confirmation table — these are experimental results, not recommendations, so they stay.

Let me compile both documents.
```

### [36] TOOL CALL — Bash · 2026-09-25 09:21:20 UTC

```
First pdflatex pass on report.tex:
pdflatex -interaction=nonstopmode report.tex 2>&1 | tail -3
```

### [37] TOOL CALL — Bash · 2026-09-25 09:21:20 UTC

```
First pdflatex pass on exec_summary.tex:
pdflatex -interaction=nonstopmode exec_summary.tex 2>&1 | tail -3
```

### [38] TOOL RESULT — Bash · 2026-09-25 09:21:26 UTC

```
{"stdout": "onts/cm/cmsy8.pfb>\nOutput written on report.pdf (31 pages, 468671 bytes).\nTranscript written on report.log.", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [39] TOOL RESULT — Bash · 2026-09-25 09:21:30 UTC

```
{"stdout": "r/share/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/cmsy10.pfb>\nOutput written on exec_summary.pdf (3 pages, 116611 bytes).\nTranscript written on exec_summary.log.", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [40] TOOL CALL — Bash · 2026-09-25 09:21:34 UTC

```
Remaining pdflatex passes for cross-references:
pdflatex -interaction=nonstopmode report.tex 2>&1 | tail -3 && pdflatex -interaction=nonstopmode report.tex 2>&1 | tail -3 && pdflatex -interaction=nonstopmode exec_summary.tex 2>&1 | tail -3
```

### [41] TOOL RESULT — Bash · 2026-09-25 09:21:46 UTC

```
{"stdout": "onts/cm/cmsy8.pfb>\nOutput written on report.pdf (32 pages, 474805 bytes).\nTranscript written on report.log.\nonts/cm/cmsy8.pfb>\nOutput written on report.pdf (32 pages, 474806 bytes).\nTranscript written on report.log.\nr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/cmsy10.pfb>\nOutput written on exec_summary.pdf (3 pages, 117003 bytes).\nTranscript written on exec_summary.log.", "stderr": "", "interrupted": false, "isImage": false, "noOutputExpected": false}
```

### [42] ASSISTANT · 2026-09-25 09:22:08 UTC

```
Both compiled. Now writing the structured JSON output.
```

### [43] TOOL CALL — Write · 2026-09-25 09:22:08 UTC

```
File: /ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/.terminal_claude_agent_struct_out.json

{
  "title": "What English-tuned abliteration misses in Slovene: internal research report",
  "coverage_note": "The report narrates all 5 iterations of the run in chronological order (sections: Framing, Iteration 1 through Iteration 5, What We Have Learned, Run Trajectory, References). It walks through 15 experiments and 5 evaluations from 15 artifacts (gen_art_experiment_1 through gen_art_experiment_15, gen_art_evaluation_1 through gen_art_evaluation_5, gen_art_research_1, gen_art_research_2, gen_art_dataset_1). It typesets 37 result tables covering all major tables from the artifact outputs: iteration-1 checkpoint behaviour, same-edit response surface, swap statistics, transfer matrix, judged 2x2 transfer table; iteration-2 T1 harmful behaviour, T2 KL divergence, T3 utility, T4 FLORES NLL, T5 bilingual geometry, T6 frozen vs refit probes, T12 dose-response, RefusEU headline rates, official guard ASR, surrogacy gap (exp6); iteration-3 DEV indices, matched-energy groups (exp9 and exp10), nested R-squared, S5X headline, judge-sensitivity table; iteration-4 nested R-squared per language (exp13 and exp14), GaMS3 band mass, gradient-blind fraction structural table, reselection table, flip analysis; iteration-5 F1-F17 failed hypotheses ledger, U1-U10 unexecuted proposals. All 9 figures are included (fig_behaviour_summary, fig_dose_response, fig_redundancy_index, fig_band_analysis, fig_cross_model, fig_write_profile, fig_gams3_profile, fig_gbf, fig_refusal_gap). Dead ends are recorded per iteration. All correction annotations ([Correction, iter N]) from the audit passes are preserved inline. The executive summary covers Goal, What Was Tried, Key Results, What Failed, Best Result, and Open Questions in 3 pages. Per staff directive, findings are stated as measurements and their implications for evaluating refusal across languages; no operational recommendations for removing refusals are given. Nothing named in the inputs was omitted.",
  "out_expected_files": {
    "report_tex_path": "report.tex",
    "report_pdf_path": "report.pdf",
    "exec_summary_tex_path": "exec_summary.tex",
    "exec_summary_pdf_path": "exec_summary.pdf"
  }
}
```

### [44] TOOL RESULT — Write · 2026-09-25 09:22:08 UTC

```
{"type": "create", "filePath": "/ai-inventor/aii_data/runs/run_A3Dbh1J6RI3O/4_gen_paper_repo/_4_assemble_paper/report_workspace/.terminal_claude_agent_struct_out.json", "content": "{\n  \"title\": \"What English-tuned abliteration misses in Slovene: internal research report\",\n  \"coverage_note\": \"The report narrates all 5 iterations of the run in chronological order (sections: Framing, Iteration 1 through Iteration 5, What We Have Learned, Run Trajectory, References). It walks through 15 experiments and 5 evaluations from 15 artifacts (gen_art_experiment_1 through gen_art_experiment_15, gen_art_evaluation_1 through gen_art_evaluation_5, gen_art_research_1, gen_art_research_2, gen_art_dataset_1). It typesets 37 result tables covering all major tables from the artifact outputs: iteration-1 checkpoint behaviour, same-edit response surface, swap statistics, transfer matrix, judged 2x2 transfer table; iteration-2 T1 harmful behaviour, T2 KL divergence, T3 utility, T4 FLORES NLL, T5 bilingual geometry, T6 frozen vs refit probes, T12 dose-response, RefusEU headline rates, official guard ASR, surrogacy gap (exp6); iteration-3 DEV indices, matched-energy groups (exp9 and exp10), nested R-squared, S5X headline, judge-sensitivity table; iteration-4 nested R-squared per language (exp13 and exp14), GaMS3 band mass, gradient-blind fraction structural table, reselection table, flip analysis; iteration-5 F1-F17 failed hypotheses ledger, U1-U10 unexecuted proposals. All 9 figures are included (fig_behaviour_summary, fig_dose_response, fig_redundancy_index, fig_band_analysis, fig_cross_model, fig_write_profile, fig_gams3_profile, fig_gbf, fig_refusal_gap). Dead ends are recorded per iteration. All correction annotations ([Correction, iter N]) from the audit passes are preserved inline. The executive summary covers Goal, What Was Tried, Key Results, What Failed, Best Result, and Open Questions in 3 pages. Per staff directive, findings are stated as measurements and their implications for evaluating refusal across languages; no operational recommendations for removing refusals are given. Nothing named in the inputs was omitted.\",\n  \"out_expected_files\": {\n    \"report_tex_path\": \"report.tex\",\n    \"report_pdf_path\": \"report.pdf\",\n    \"exec_summary_tex_path\": \"exec_summary.tex\",\n    \"exec_summary_pdf_path\": \"exec_summary.pdf\"\n  }\n}\n", "structuredPatch": [], "originalFile": null, "userModified": false}
```

### [45] ASSISTANT · 2026-09-25 09:22:18 UTC

```
All deliverables complete:

- **report.pdf** (32 pages) and **exec_summary.pdf** (3 pages) — compiled and verified
- **.terminal_claude_agent_struct_out.json** — matches the required schema

Changes per staff directive:
- **report.tex "Firm positive"**: Reframed from "where to deposit energy" to "edit placement predicts residual refusal"; added the evaluation implication ("evaluating refusal-edit transfer across languages requires controlling for edit placement"); removed the operational framing
- **exec_summary.tex Key Result 3**: Same reframing — states the measurement, not a recipe
- **exec_summary.tex Best Result**: Removed the specific band recommendation ("depositing the edit in band 13--24") and the practical recommendation ("use energy-weighted cosine or band-mass overlap to select layer sets"); replaced with the evaluation implication that placement is a confound for cross-lingual refusal measurement

Experiment sections, figure captions, and tables that record *what was observed* at specific bands remain unchanged — those are measurements in the round record, not recommendations.
```

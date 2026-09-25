# Search log, iteration 5 (rows 26-47)

Continues the dependency's log (`results/_dep_search_log.md`, rows 1-25) so the two concatenate. All searches run
2026-09-24 with the `aii-web-tools` free-first search stack (`aii_fast_web_search.py`, general mode, US region,
English queries). Raw result lists are saved as `results/raw/search_<row>.txt`. Rows whose outcome reads NO
NEIGHBOUR FOUND are the evidence behind the absence statements in `results/evidenced_absence.md`.

| # | step | engine | query | top results examined | outcome |
|---|---|---|---|---|---|
| 26 | T2 B1 | aii-search | proxy refusal metric accurate on base model but inverts on abliterated edited model keyword | featherless blog; 2607.17427; atomic.chat; audn-ai/refusal-benchmark; 2609.14759 | NO NEIGHBOUR FOUND for the base-accurate / edited-inverted contrast |
| 27 | T2 B1 | aii-search | refusal keyword matching false positives abliterated model caveats disclaimers compliance | audn-ai/refusal-benchmark; 2607.02714; clearbluejar; 2605.05427; 2407.12043 | PARTIAL: practitioner reports of verdict bias in uncensored models; no measured within-edited agreement |
| 28 | T2 B2 | aii-search | abliteration search objective audited against LLM judge candidate trials refusal counter | 2505.19056; 2512.13655; emergentmind; privatellm; explainx | NO NEIGHBOUR FOUND auditing a search objective on its own candidate population |
| 29 | T2 B2 | aii-search | weight-edit hyperparameter search objective blind spot refusal counter Optuna TPE abliteration | abliterix repo (Optuna TPE multi-objective); Optuna docs and paper | PARTIAL (tooling only): abliterix uses Optuna TPE; no audit of the objective. NO NEIGHBOUR FOUND |
| 30 | T2 B2 | aii-search | reward hacking refusal counter model editing optimizer selects wrong checkpoint | Wikipedia; Anthropic alignment blog; 2604.13602; METR | generic reward-hacking framing only. NO NEIGHBOUR FOUND |
| 31 | T2 B1 | aii-search | Heretic abliteration refusal markers overestimate refusal partial compliance evaluation | explainx; 2607.17427; 2512.13655; nathan.sapwell; aithinkerlab; p-e-w/heretic | LEAD: 2512.13655 states the marker false-positive caveat (-> M4) |
| 32 | T2 B3 | aii-search | guard classifier and LLM judge disagree differently English versus non-English same model outputs | LLM-as-a-judge surveys; 2509.23381 (Guard Vector); evidently/wandb guides | NO NEIGHBOUR FOUND for a language-dependent guard-vs-judge divergence on the same edited checkpoint |
| 33 | T2 B3 | aii-search | non-actionable compliance non-English jailbreak responses safe guard classifier low-resource vague harmful | 2609.08373; 2310.02446; 2506.10597; jailbreakbench issue #50 | LEAD: jailbreakbench issue #50 (substring matched anywhere) -> M21. No language-dependent actionability result |
| 34 | T2 B4 | aii-search | LLM judge agreement certified in English applied to other language safety evaluation abliterated model kappa drop | 2607.02235; 2606.00093; 2606.19544; 2606.07874; 2603.06594; 2605.31381 | KEY NEIGHBOURS: 2607.02235 (-> M16), 2603.06594 (-> M9), 2606.07874 (-> M19) |
| 35 | T2 B4 | aii-search | within-condition agreement kappa judge edited model safety evaluation prevalence pooled inflation | Cohen's kappa references; PLOS One kappa critique; PABAK literature | STATISTICS LITERATURE ONLY (prevalence-dependence of kappa is textbook). NO NEIGHBOUR FOUND in safety evaluation reporting within-condition agreement for an EDITED model |
| 36 | T2 B4 | aii-search | multilingual refusal classifier reliability Slovene judge agreement safety | 2606.07535; 2605.31381; 2505.17306; 2605.25420; 2605.05427 | NO NEIGHBOUR FOUND for Slovene judge reliability; RefusEU is the only Slovene-containing safety resource located |
| 37 | T3 dose | aii-search | edit strength cannot compensate for layer choice refusal ablation | 2601.08489; Arditi LessWrong post; abliteration.ai; NeurIPS Arditi PDF; 2609.07876 | NO NEIGHBOUR FOUND for a dose-versus-placement exchange result |
| 38 | T3 dose | aii-search | scaling intervention magnitude versus intervention site steering layer dose response | 2602.01654; 2609.06473; learnmechinterp; alphaxiv | PARTIAL: 2609.06473 iso-effect dose-response under quantisation (-> P4), not placement |
| 39 | T3 placement | aii-search | matched budget layer placement ablation refusal contiguous band versus spread layers same number of layers | mostly physics 'perfectly matched layer' noise; 2603.22061; 2608.26650 | NO NEIGHBOUR FOUND (the phrase collides with an unrelated physics term) |
| 40 | T3 placement | aii-search | abliteration layer selection comparison middle layers versus all layers refusal removal cross-lingual | grimjim projected/biprojected abliteration; 2512.13655; 2608.18093; ACL 2025.acl-long.778 | NO NEIGHBOUR FOUND for a matched-budget cross-lingual placement comparison |
| 41 | T3/T5 | aii-search | safety layers contiguous middle layers multilingual non-English language safety layers location differs | 2408.17003 (v1 and v5); 2608.29936; 2609.22144; lacuna essay | KEY NEIGHBOUR: 2408.17003 (-> P1, P2) and the v1/v5 title drift; no multilingual safety-layer localisation found there |
| 42 | T2 B4 | aii-search | judge validated on one model outputs fails on another model outputs refusal classifier distribution shift abliterated | oleczek repo; 2607.23386; abliterix docs; 2608.17994; 2605.16023 | CONFIRMS 2603.06594 as the right neighbourhood (-> M9) |
| 43 | T3 dose | aii-search | steering layer choice matters more than steering coefficient larger coefficient wrong layer does not recover effect | 2604.15557; 2601.19375; learnmechinterp; GDM mech interp update | PARTIAL: 2601.19375 discriminative layer selection (-> P5). NO NEIGHBOUR FOUND for the dose-exchange statement |
| 44 | T2 B4 | aii-search | abliteration refusal rate Slovene OR Slovenian language model safety evaluation | 2etatg/abliteration-eval; 2510.02768; abliterix; alice report; 2608.18093 | KEY NEIGHBOUR: 2510.02768 (-> M3). No Slovene abliteration evaluation found |
| 45 | T2 B4 | aii-search | safety evaluation judge reliability across languages drops Slavic languages refusal detection agreement | 2025.findings-emnlp.587; 2602.02287; 2605.17173; 2606.22329; 2607.14480; 2026.mellm-1.26 | NEIGHBOURS: 2605.17173 (-> M18, contradicting); a Finno-Ugric and a language-bias study exist; still no Slavic-specific refusal-judge result |
| 46 | T2 B2 | aii-search | optimizing abliteration with keyword refusal count misleads selection judge rescoring trials | AIAnytime/ablate; 2607.17427; abliterix docs; 2512.13655; abliteration.ai measurement page; maximelabonne | LEAD: abliterix evaluation doc (-> M20). NO NEIGHBOUR FOUND for a measured selection error |
| 47 | T4 C-a | aii-search | unaligned counterfactual abliterated model residual refusal language dependent safety cost bias | Wang NeurIPS 2025 PDF; 2607.17427; 2607.02714; 2505.19056; alice report; 2601.08489 | NO NEIGHBOUR FOUND measuring residual refusal per language inside an abliterated counterfactual |

## Exact-extraction step (rows 48-49)

| # | step | engine | URL(s) | raw file | outcome |
|---|---|---|---|---|---|
| 48 | T2-T5 exact extraction | aii-fetch | abs pages of 2609.10594, 2408.17003 (+v1), 2505.19056, 2607.02235, 2408.14398, 2601.18306, 2609.04721, 2606.00926, 2608.22490, 2509.24384, 2605.17173, 2606.01322, 2608.30856, 2406.18495, 2603.06594, 2609.06473, 2601.19375, 2607.17427, 2512.13655, 2510.02768, 2606.07535, 2412.10321; aclanthology.org/2026.tacl-1.9/ | `results/raw/abs_*.txt`, `results/raw/g_abs_*.txt`, `results/raw/g_tacl_*.txt` | all resolve to the titles named; ids, authors, venues and versions recorded in `results/bibliography_repairs.csv` |
| 49 | T2-T5 exact extraction | aii-grep | PDFs/HTML of 2609.10594, 2408.17003, 2505.19056 (v1+v2), 2607.02235, 2408.14398, 2608.22490, 2606.07535, 2606.01196, 2606.00926, 2609.04721, 2607.02714v2, 2402.10260, 2404.16369, 2308.01263, 2406.18495, 2608.30856, 2605.17173, 2606.01322, 2412.10321, 2306.11695, 2306.00978, 2512.13655, 2510.02768, 2603.06594; github.com/wuwangzhang1216/abliterix docs; github.com/JailbreakBench/jailbreakbench issue 50 | `results/raw/g_*.txt` | every VERIFIED-QUOTE row in the three neighbour tables comes from this step and is re-checked by `scripts/self_check.py` |

## Two corrections this log records against the plan's expectations (OBSERVATION)

1. The plan expected arXiv 2609.10594 to say that automated evaluators, and string matching above all,
   overestimate jailbreak effectiveness. Full-text grep shows 2609.10594 compares six LLM-based evaluators and
   treats string matching only as background; the 'especially string matching for non-refusal' sentence belongs to
   StrongREJECT (2402.10260, Sec. 3.2). The row for it (M2) states the correction.
2. The plan expected 2607.02235 to report judge-human agreement of about 80% at the top and below 60% for several
   lower-resource Latin-script languages. Greps for `agreement|kappa|80%|60%|script|overtrust` and
   `[0-9]{2}%|correlat|human validation|reliab|single judge` return the ~80% figure as Zheng et al.'s ENGLISH
   MT-Bench number and no <60% figure. What the paper does state, and what M16 quotes, is that judge reliability
   is language-conditional, with specific drops attributed to Watts et al. 2024, Fu and Liu 2025 and Hada et al. 2024.

## Post-verification re-fetches (rows 50-52, run after the output verifier rejected one passage)

The automated passage check rejected source [8]'s quote because the source entry named the PDF while the extract had
come from the abs page, where the sentence is continuous (in the PDF it is line-broken as "ex-\nisting"). Three
source URLs were corrected to the abs pages their extracts actually came from, and each passage was re-fetched live
to confirm it is present there.

| # | step | engine | URL | raw file | outcome |
|---|---|---|---|---|---|
| 50 | passage re-verification | aii-grep | https://arxiv.org/abs/2603.06594 | `results/raw/verify_2603.06594_abs.txt` | 1 match: "existing validation protocols fail to account for substantial distribution shifts inherent to red-teaming" |
| 51 | passage re-verification | aii-grep | https://arxiv.org/abs/2608.30856 | `results/raw/verify_2608.30856_abs.txt` | 1 match: "their refusals are overall explicit and strongly morally evaluative" |
| 52 | passage re-verification | aii-grep | https://arxiv.org/abs/2408.14398 | `results/raw/verify_2408.14398_abs.txt` | 1 match: "while calibration on the target language effectively retains perplexity and yields high signal-to-noise ratios" |

A provenance check was then added to the workflow: for every row and every published passage, the URL declared must
be the URL recorded in the header of the raw extract the quote was taken from. It found one further mismatch (row
C7, which cited the PDF while quoting the abs page) and that row was corrected too.

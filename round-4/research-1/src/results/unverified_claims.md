# Claims this artifact could NOT verify in a primary source, and one inherited flag RESOLVED

Accessed 2026-09-24. Every entry names the exact queries/regexes run.

---

## 1. The inherited "2–3 middle layers" attribution — RESOLVED, with a correction that matters

**Inherited status (carried verbatim from this run's own audit, `round-3/evaluation-1/src/results/novelty_table.md`):**

> "Hadetskyi et al. 2026, Not All Refusals Are Equal (arXiv 2607.02714) | **NOT VERIFIED** | ... The '2-3 middle layers' sentence was NOT FOUND in the abstract or the HTML full text (grep for 'middle layers', '2-3', 'two or three'): NOT VERIFIED."

**One bounded verification pass, run in this session (2026-09-24).** Identifier resolved: `https://arxiv.org/abs/2607.02714` returns *"Not All Refusals Are Equal: How Safety Alignment Fails Cybersecurity at Scale"*, Hadetskyi and 2 other authors, submitted 2 Jul 2026, last revised 7 Jul 2026 (v2). Regexes run over the full text of **both** the PDF v1 and PDF v2 and the HTML v2:
`middle layer|2-3|2–3|two to three|two or three|few layers|as effective as|all layers|single layer` (PDF v1, PDF v2) and `middle layers|narrow local` (HTML v2).

**Outcome: FOUND.** §3.2 "Layer Selection Strategies", identical text in v1 and v2:

> "Layer selection is a critical element of the process. Arditi et al. found that abliterating a narrow local region of 2–3 middle layers can be as effective as ablating across all layers, and applied their technique to all layers' WO and Wout plus the embedding matrix."

The earlier NOT VERIFIED was a **search miss**, not an absent sentence: the previous pass grepped the abstract page and an HTML pattern whose 80 matches were truncated before §3.2. The flag is therefore **lifted for the existence of the sentence in 2607.02714**.

**But the attribution does not survive intact, and the paper contradicts it in the next sentence.** Two OBSERVATIONS:

1. **2607.02714 attributes the claim to Arditi et al., and we could not locate it in Arditi et al.** Regexes run over `https://arxiv.org/pdf/2406.11717v3` (full text): `middle layers|narrow|local region|single layer|subset of layers|all layers|2-3|2–3|few layers` (2 matches, both describing all-layer ablation) and `weight orthogonalization|every matrix|W_{out}|matrices that write` (§4.1). What Arditi et al. state is the opposite default: "We perform this operation at every activation x(l)i and ˜x(l)i, across all layers l and all token positions" (§2.4) and, for the weight edit, "Orthogonalizing all of these matrices, as well as any output biases, with respect to the direction ˆr effectively prevents the model from ever writing ˆr to its residual stream" (§4.1). **Recorded outcome, in this exact wording: the '2–3 middle layers' claim was not found in Arditi et al. (2406.11717v3) by these queries.** That is weaker than "does not exist" and is the only statement this artifact is entitled to make. It has NOT been re-attributed to any other paper.
2. **2607.02714 itself rejects the claim for modern models.** The very next sentences of §3.2: "We found that this does not generalize to the broader set of modern models in our study: refusal in many architectures is distributed more widely ... Thus, in our main experiment we opted for uniformly spread layer selection across 25–95% of model depth, which we found to substantially outperform norm-based selection (targeting layers with the highest refusal signal norm) by up to ∼70pp of additional refusal reduction at 30% on the most susceptible models."

**Instruction to the report author (INTERPRETATION).** The paper may cite 2607.02714 for (a) refusal being "distributed widely across layers" (abstract) and (b) uniform spread outperforming norm-based layer selection by up to ~70pp. It may **not** write "prior work reports that 2–3 middle layers suffice" as a standing fact. If the sentence is used at all, it must be written as a second-hand attribution inside 2607.02714 whose source we could not locate, and it must be accompanied by the same paper's rejection of it. Removing it entirely is also acceptable; silently paraphrasing it as an established depth result is not.

---

## 2. Heretic PR #445 merge date — previously NOT VERIFIED, now verified

Prior audit recorded "merge date not captured in the fetched excerpt (NOT VERIFIED for date)". This session's regex over `https://github.com/p-e-w/heretic/pull/445` (`merged|commits into|config|subset|Multilingual`) returns: "Vinay-Umrethe merged 4 commits into p-e-w:master from Vinay-Umrethe:support-dataset-config/subset ... **Sep 5, 2026**". Verified. (PR #444, benchmark scorer: "p-e-w merged 3 commits into master ... **Sep 3, 2026**", re-verified this session.)

---

## 3. Claims this artifact still cannot verify

| claim | why it is unverified | searches run |
|---|---|---|
| "No prior work reports that an activation-space depth measurement fails to predict WEIGHT-edit outcomes cross-lingually while two one-forward-pass baselines succeed." | An absence claim cannot be verified, only evidenced. Closest found: Hase et al. 2023 (English, factual editing, causal tracing), 2606.00926 (activation space only), 2609.04721 App. A.6 (cross-architecture, not cross-lingual), 2608.24988 (fine-tuning, not prediction). | `results/search_log.md` rows 2, 4, 8, 11, 13, 18, 20, 21. The paper must write "we could not find" with these searches cited, never "no prior work exists". |
| Whether Heretic's merged benchmark scorer (#444) supports non-English benchmark-grade refusal scoring | The PR page confirms the scorer exists and is merged; this artifact did not read the scorer's implementation or run it, and `config.default.toml` on master still lists `KeywordRate` + `KLDivergence` as the default `scorers`. | fetched PR #444, repo README, `raw.githubusercontent.com/p-e-w/heretic/master/config.default.toml` (2026-09-24). Statement is bounded to the default configuration. |
| Whether the 9-subset `heretic-org/Multilingual-Harmless-Harmful` dataset is quality-reviewed by native speakers | The dataset card states it is a translation of `Semantic-Harmless`/`Semantic-Harmful`; no review process was located. | fetched the dataset card 2026-09-24. Relevant only as context: it contains no Slovene. |
| That N22 (2609.22144) is the FIRST report of language-specific safety-sensitive depths | Not checked; this artifact only establishes that such a report exists and predates this run's claim. | row 23 of the search log. The paper should cite N22 as prior work and not claim primacy for the observation. |

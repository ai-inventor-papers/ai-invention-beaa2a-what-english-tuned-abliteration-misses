# Finding the closest prior work for two results

## Summary

Positioning artifact (web research only; no code, no GPU, no paid API, $0 spend) that gives both of this run's reportable results the neighbours the reviewer said they lacked. Deliverables in results/: a 30-row neighbour table (markdown + JSON, N1-N30) where every row carries a verbatim <=40-word quote with its locator, a URL, an access date (2026-09-24) and a verified flag; two paste-ready positioning paragraphs (positive and negative) each stating its own stopping point; a 30-row claims_to_position.csv in which no claim is left without either a neighbour id or an evidenced NO NEIGHBOUR FOUND; reconciliation_map.csv (claim id -> neighbour ids -> producing file path -> tag -> paper sections that must agree); a tagged ledger separating 14 FAILED HYPOTHESES (each with the number and direction that killed it) from 10 UNEXECUTED PROPOSALS (each with its reason); the canonical stopping-points block for verbatim reuse; the full search log; and scripts/self_check.py, which passes. KEY OUTCOMES FOR THE PAPER. (1) The inherited '2-3 middle layers' attribution is RESOLVED: the sentence does exist in arXiv 2607.02714 SS3.2, but as that paper's own attribution to Arditi et al. - which was not found in Arditi et al. by full-text search - and 2607.02714 rejects it in the next sentence, having found uniform layer spread beats signal-norm-based selection by up to ~70pp. It must not be cited as a standing depth fact. (2) The positive's delta is NARROWED: effect-based site selection (Hase 2023; 2609.22135; 2606.00926) and language-specific safety depths (2609.22144; 2605.23036) are already published. What survives is the matched-total-energy AND matched-layer-count placement contrast, per language, with the effective region differing between two sibling checkpoints - no neighbour found running that construction. (3) The negative now has four partial neighbours (Hase 2023; 2606.00926; 2609.04721 on cosine unreliability; 2608.24988 on weight-edit geometry surviving behavioural reversion) and an EVIDENCED ABSENCE for the conjunction, with the eight queries behind it logged; the wording prescribed is 'not found by these queries'. (4) The selection-blindness finding must be positioned against AdvPrefix (2412.10321), not StrongREJECT: AdvPrefix owns objective misspecification inside an optimiser for prompt attacks, so this run's claim is the weight-edit instance quantified on the search's own candidate population. (5) Tooling state, dated 2026-09-24: Heretic's default scorer on master is still the 33-marker substring counter plus KL over an English prompt set, although a benchmark scorer (PR #444, merged Sep 3 2026) and dataset config selection (PR #445, merged Sep 5 2026) are merged, and the community multilingual set covers 9 languages with no Slovene. Every line is tagged OBSERVATION / INTERPRETATION / FAILED HYPOTHESIS / UNEXECUTED PROPOSAL, and every number about this run carries the path of the file that produced it.

## Research Findings

# What is already known, in whose words, and what is left for this paper to claim

Scope note (OBSERVATION): this is a bounded, prioritised lookup accessed **2026-09-24**, with 24 discovery queries and about 40 exact-extraction calls logged in `results/search_log.md`. It is "closest found", not exhaustive. Every quote below was pulled by regex over the source's own full text in this session; raw extracts are in `results/raw/`. Numbers about this run are given with the path of the file that produced them, never from the draft under revision.

## 1. RESULT 1 (the positive): placement at matched edit size and matched layer count

**Nearest published work, and exactly what each establishes.**

The framing floor is the single-direction result: refusal "is mediated by a one-dimensional subspace, across 13 popular open-source chat models up to 72B parameters in size" [1], and the method's default intervention is removal at "activations at all layers and all token positions", with weight orthogonalisation applied to every matrix that writes to the residual stream [2]. That default is precisely what makes placement invisible: if the edit covers the whole stack, *where* it acts is not a free parameter [1, 2].

Three lines have since made placement a question again. First, **effect-based site selection**. In omni-modal models, "probe-best layers vary widely across architectures, while steering-effective layers consistently fall within a narrow mid-to-late range of normalized depth" [6]; in text LMs the same separation holds — "the layer with the highest probe accuracy is not the layer with the largest ablation response, in every pretrained model we ran" [9], and the paper's abstract puts it as separating "where a variable is most readable from where deleting it does most damage" [8]. In **weight space** the statement is older: causal-tracing localisation gives no "insight into which model MLP layer would be best to edit in order to override an existing stored fact with a new one" [5]. Cheap predictors of *where steering works* already exist and work well in their own settings: a logit-lens diagnostic predicts steering effectiveness at rho +0.86 to +0.91 [10], and simple separability metrics "strongly correlate with the downstream steerability" [11]. Cross-model direction transfer is likewise established for concepts, with SAE-aligned cross-model steering vectors reaching a 71.0% win rate against same-model native vectors [7].

Second, **depth-distributed refusal**. arXiv 2607.02714 reports that uniformly spread layer selection "substantially outperform[s] norm-based selection (targeting layers with the highest refusal signal norm)" — by up to ~70pp of additional refusal reduction on the most susceptible of 24 models [14]. A transplantation study localises refusal to mid-network MLP blocks — "the block spanning layers 8-11 is selected first in all six greedy searches" — and finds composition **non-additive**: "in five of six greedy trajectories, adding more aligned blocks can reduce refusal performance" [16]. That last sentence is the closest published parallel to this run's finding that concentrating a fixed removal energy on one contiguous band beats spreading it. Safety can also be *trained* to be redundantly distributed [15], and a non-peer-reviewed per-layer study on one English model reports that "ablating every layer except 12 performs identically to ablating all 32" [40].

Third, **language**. The direction itself is close to universal: "a vector extracted from English can bypass refusals in other languages with near-perfect effectiveness, without any additional fine-tuning" [3], with the intervention applied "across all layers and token positions" [4]. But the *depths* are not: "sensitive layers are only partially shared across languages, with safety-relevant signals often distributed across multiple layers", with language-specific peaks over 18 languages [28]. A language-aware *a priori* layer-selection rule already exists for SAE-based language control [29]. In a multilingual MoE, harm detection is "nearly language-invariant in mid-network" while the write that produces refusal is late and orthogonal, and the top-10 harm-correlated expert overlap between Indic languages and English falls away with depth — the "mean cross-lingual Jaccard rises through the mid-network, peaks at 0.43 at L11" and collapses to 0.027 at L18 [17, 18]. Against direction universality stands the finding that "harmful prompts retain less than 10% of the English refusal signal across most language-model pairs" in four African languages [30], and the action-vs-representation diagnosis that "the relevant representation is present. Yet harmful refusal drops from 87.9% to 43.9%" [31].

**What this run adds, after those neighbours are subtracted (INTERPRETATION).** Two of the three qualifiers this run was hoping to claim are already occupied: effect-based selection is occupied [5, 6, 8, 9], and language-dependent safety depth is occupied [28, 29]. **The delta that survives is narrow and should be stated narrowly:** holding *total removal energy* and *the number of edited layers* fixed, which contiguous band carries the energy decides how much refusal survives — per language and differently between two sibling checkpoints of one architecture. In GaMS3-12B-Instruct, twelve contiguous mid-depth layers leave Slovene residual refusal at 0.24 while twelve layers strided over the full depth at the same energy leave 0.81 (difference -0.57 [-0.70, -0.44]; `round-3/experiment-10/src/results/report_tables.md`); the pre-registered broad-beats-narrow prediction was falsified in the opposite direction (-0.10 [-0.150, -0.060], same file); the nested decomposition gives log-energy 0.325, log-energy plus *where* the energy sits 0.718, log-energy plus *how many* layers 0.400 (same file). In Gemma-3-12b-it, the lowest reachable Slovene refusal is monotone in the fraction of layers 13-24 covered (Spearman -0.942, permutation p = 0.0038) and sparing layers 25-36 costs Slovene +0.39 residual refusal against 0.00 in English (`round-3/experiment-9/src/results/report_tables.md`). No neighbour found in this lookup runs a matched-energy **and** matched-count construction, and none reports the effective region differing between sibling checkpoints (`results/search_log.md`, rows 21-24).

**Where it stops (OBSERVATION).** Two sibling checkpoints of one architecture plus one community reference and two outside families; one non-English language in the matched panels; one or two optimiser seeds; 4-bit NF4 throughout with one bf16 control cell; machine-translated Slovene with automated back-translation QC only and **no native review anywhere in the run** (five packets PENDING). The canonical block is `results/stopping_points.md` and should be pasted verbatim wherever a claim is bounded.

## 2. RESULT 2 (the transferable negative): activation-space geometry does not predict weight-edit outcomes, and two trivial baselines do

**This is the result the reviewer flagged as having no neighbour at all. It now has four partial neighbours and an evidenced absence.**

This run's numbers, with paths: a development-frozen activation-space depth index reaches Spearman **-0.009 [-0.131, 0.192]** against residual refusal over 21 out-of-sample rows (permutation p 0.1628); EN/target-language direction cosine reaches **+0.010**; the single-site causal transfer rate reaches **+0.732** and the unedited model's own in-language refusal rate **+0.661**, with paired item-bootstrap differences of -0.741 [-0.810, -0.528] and -0.670 [-0.721, -0.497] respectively (`round-3/experiment-12/src/results/analysis.json`, P1 and P4).

The three component points that *are* published: (i) localisation does not predict where to edit weights, for factual knowledge and ROME/MEMIT, in English [5]; (ii) inside activation space, readability and ablation damage live at different depths [8, 9]; (iii) direction cosine is unreliable as a transfer metric — "even a *random* source direction can map to a high cosine, up to 0.515 across our pairs", so "a cross-architecture transfer claim should therefore rest on the structural and behavioral specificity controls, not on a geometric similarity score" [12]. A fourth neighbour reports the converse dissociation for a weight-embedded steering edit: "the weight edit survives almost untouched even where behaviour reverts: mean vector recovery is rho = 0.004" [32]. Steering effects are in any case volatile: "in-distribution, steerability is highly variable across different inputs" [34].

**What none of them states (OBSERVATION, evidenced absence).** After the searches logged in `results/search_log.md` rows 2, 4, 8, 11, 13, 18, 20 and 21 — including four deliberately adversarial phrasings aimed at surfacing a scoop — **we did not find** a paper that measures an activation-space depth (or cosine) statistic, tests it as a predictor of **weight-edit** outcomes **across languages**, and races it against the target model's own pre-edit refusal rate and a single-site causal probe on the same held-out items. The correct wording for the paper is "not found by these queries", not "does not exist". The searches did return the right neighbourhood [5, 8, 9, 10, 11, 12, 32], which is evidence the queries were pointed correctly rather than missing the literature.

**The practitioner recommendation this licenses (INTERPRETATION).** Before spending a search budget on geometry, measure two things that each cost one forward pass — the unedited model's refusal rate in the target language, and the effect of ablating at a single site — and require any proposed placement statistic to beat them. The competing reading, which the paper must name, is that *this particular index* was badly constructed rather than that activation-space depth statistics are the wrong family; that is why the result is reported as a bounded negative about this quantity at this scale, and why two published cheap predictors [10, 11] and one multilingual layer rule [29] are listed as **UNEXECUTED** comparisons rather than as beaten baselines.

## 3. Sub-question (b): can the inherited "2-3 middle layers" attribution be verified?

**Yes — and verifying it produces a correction, not a citation.** One bounded pass over `arxiv.org/abs/2607.02714`, PDF v1, PDF v2 and HTML v2 (regexes in `results/unverified_claims.md`) locates the sentence in §3.2: "abliterating a narrow local region of 2–3 middle layers can be as effective as ablating across all layers" [13]. The earlier NOT VERIFIED flag was a search miss (a truncated match list), not an absent sentence, and the flag is lifted **for the existence of the sentence in that paper**. Two things follow that the paper must carry. First, 2607.02714 presents it as an attribution **to Arditi et al.**, and a full-text search of Arditi et al. v3 did not find such a claim — what that paper states is all-layer ablation and orthogonalisation of every residual-stream writer [2]; the recorded outcome is "not found in Arditi et al. by these queries", and the claim has **not** been re-attributed to any other paper. Second, 2607.02714 rejects it in the very next sentence: "We found that this does not generalize to the broader set of modern models in our study: refusal in many architectures is distributed more widely" [13], which is why they chose uniform spread [14]. The paper may cite 2607.02714 for distributed depth and for the uniform-vs-norm-based comparison; it may not cite it for "2-3 middle layers suffice".

## 4. Sub-question (d): positioning the selection-blindness finding so it is not "already known"

The evaluation-time result is firmly established: existing evaluation methods "significantly overstate jailbreak effectiveness compared to human judgments" [19], and among the baselines "string matching for non-refusal" is the most biased [20]; partial compliance has been a first-class class since XSTest — "partial refusal is any combination of refusal and compliance within the same response" [21]; and validity-aware evaluation reclassifies 22.1%-51.0% of prior labelled successes as invalid [22]. Judges themselves are fragile and attackable [24]. **None of that is this run's claim.**

The closest neighbour on the **selection** side is AdvPrefix, which shows a misspecified objective inside an optimiser yields low loss without the intended behaviour — "limited control over model behaviors, yielding incomplete or unrealistic jailbroken responses" — and that repairing it changes what the search finds (GCG on Llama-3, 14% to 80%) [23]. AdvPrefix owns the general point for prompt-level attack objectives. This run's addition must therefore be stated as the **weight-edit** instance with three specifics: the objective is measured against a certified judge on the search's *own* candidate population (the substring counter never leaves 72-100/100 across all 116 draws while judged refusal spans 7-98/100; mean absolute error 30.6 vs 2.1 per 100 candidates; certification kappa 0.143 vs 0.858 [0.820, 0.888]; `round-3/experiment-11/src/README.md`, `results/miscalibration_table.csv`, `scorer/certification.json`, with 305/305 headline checks re-derived in `results/audit_headline.json`), the blindness is quantified as a *fraction of the candidate population*, and it is cross-lingually asymmetric because partial compliance is where the non-English arm sits at the dose an English-scored search stops at. If a reviewer says "already known from StrongREJECT", the answer is that StrongREJECT changes the reported number while this changes the model that gets chosen [19, 23].

## 5. Sub-question (e): what the universality results actually measure, stated precisely

Wang et al. measure the transferability of a **direction**, evaluated by all-layer, all-position activation ablation, over 14 languages (Slovene not among them) [3, 4]. That is not a claim about the **effective depth region of a bounded weight edit**, and it is not a claim about how much of an edit's energy must sit where. The assumption this run's results bear on is therefore: *if the direction is shared, an English-derived edit will reach the same behavioural state in every language.* This run's evidence is that the shared direction survives (the all-48-layer layer-matched ablation does remove most Slovene refusal, `round-2/experiment-8/src/results/per_item.parquet`) while a bounded, searched weight edit does not (Heretic's real selected adapter leaves EN 0.60 / DE 0.53 / LT 0.75 / SL 0.92 on held-out items, `round-3/experiment-12/src/results/report_tables.md`). The literature already contains both poles — universality [3] and its denial in low-resource settings [30] — plus the action-not-representation diagnosis [31] and the language-entanglement result that "ablating safety features impacts not only harmful response rates but also target language" [33]. This run sits in the gap: shared direction, language-dependent edit outcome.

This matters beyond the paper because abliterated checkpoints are used as *the* unaligned counterfactual in multilingual safety-cost measurement [26, 27], where "non-English users consistently bear a higher Safety Cost than English users" [26]. If an English-selected edit does not reach the same state in every language, that counterfactual is language-dependent — a bounded caution, not an overturning, given n = 2 sibling checkpoints and one non-English language in the matched panels.

## 6. Sub-question (f): the tooling state, dated

As of **2026-09-24**: Heretic "finds high-quality abliteration parameters by co-minimizing the number of refusals and the KL divergence from the original model" [35]; on master the default `scorers` list is still the substring `KeywordRate` (33 markers) plus `KLDivergence` over an English prompt set [36]; a **benchmark scorer** was merged as PR #444 on **Sep 3, 2026** [37]; dataset config/subset selection was merged as PR #445 on **Sep 5, 2026** [38], which is what makes a multilingual construction set usable from the CLI; and the community set `heretic-org/Multilingual-Harmless-Harmful` provides nine subsets of 832 rows — bengali, english, french, hindi, italian, korean, marathi, russian, tamil — with **no Slovene and no Slavic language other than Russian** [39]. The honest practitioner sentence is therefore: the tool now *can* be pointed at multilingual data and at a benchmark scorer, but the default objective a user gets is still substring-based and English-only, and no Slovene construction set ships. This is a moving target and the statement is bound to its access date; this run pins Heretic 3521f864, which predates both merges.

## 7. Contradicting evidence, and what would change these conclusions

- **Against the positive's novelty:** language-specific safety-sensitive layers are already published [28], and a language-aware layer-selection rule exists [29]. The delta has been narrowed accordingly; if a reviewer finds a matched-energy, matched-count placement contrast in prior work, the contribution reduces to a replication in a new language pair.
- **Against the negative's absence claim:** any paper comparing a representation-derived predictor of weight-edit transfer against the target model's own pre-edit behaviour rate on the same items would overturn it. The claim is deliberately worded as "not found by these queries".
- **Against the cross-lingual framing generally:** direction universality [3] is a strong prior in the opposite direction, and this run's own all-layer ablation is consistent with it; the boundary this run reports holds only for bounded, searched edits.
- **Against every behavioural number here:** judges disagree and are attackable [24], automatic metrics understate non-English damage relative to human evaluation [25], and this run has **no native-speaker review at all** [`results/stopping_points.md`]. Every behavioural number is a range across automated judges.

**Confidence.** High that the neighbours listed exist and say what is quoted (each quote was retrieved in-session with a locator, and the raw extracts ship). Moderate-to-high that the positive's remaining delta (matched energy *and* matched count, per language, per sibling checkpoint) is uncovered — bounded by the lookup's size, and the one adversarial query family that could have scooped it did surface a partial scoop [28], which was then honoured by narrowing the claim. Moderate that the negative is genuinely unstated in the literature — absence claims degrade with search budget, and the budget here was about 40 minutes of targeted queries. High that the `2-3 middle layers` attribution should not be used as a standing fact [2, 13].

## Sources

[1] [Refusal in Language Models Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717) (Andy Arditi, Oscar Obeso, Aaquib Syed, Daniel Paleka, Nina Panickssery, Wes Gurnee, Neel Nanda; 2024) — Establishes the single-direction result and the all-layer/all-position default this run's placement question departs from.

> we show that refusal is mediated by a one-dimensional subspace, across 13 popular open-source chat models up to 72B parameters in size

Locator: abstract

[2] [Refusal in Language Models Is Mediated by a Single Direction (full text, v3)](https://arxiv.org/pdf/2406.11717v3) — Full text used to check whether Arditi et al. anywhere claim that a narrow region of 2-3 middle layers suffices; they specify all-layer ablation and orthogonalisation of every residual-stream writer.

> activations at all layers and all token positions

Locator: Sec. 3.1

> In a transformer architecture, the matrices that write to the residual stream are: the embedding matrix,

Locator: Sec. 4.1

[3] [Refusal Direction is Universal Across Safety-Aligned Languages](https://arxiv.org/abs/2505.17306) (2025) — The direction-universality result this run's cross-lingual claim is positioned against; 14 languages, Slovene not among them.

> a vector extracted from English can bypass refusals in other languages with near-perfect effectiveness, without any additional fine-tuning

Locator: abstract

[4] [Refusal Direction is Universal Across Safety-Aligned Languages (full text)](https://arxiv.org/pdf/2505.17306) — Full text confirming the intervention is all-layer, all-position activation ablation, and listing the 14 languages and three instruct model families evaluated.

> ablation is applied across all layers and token positions to comprehensively eliminate refusal

Locator: Sec. 3

[5] [Does Localization Inform Editing? Surprising Differences in Causality-Based Localization vs. Knowledge Editing in Language Models](https://arxiv.org/abs/2301.04213) (Peter Hase, Mohit Bansal, Been Kim, Asma Ghandeharioun; 2023) — The canonical prior statement that a localisation measurement does not tell you where to make a weight edit; factual knowledge, ROME/MEMIT, English.

> localization conclusions from representation denoising (also known as Causal Tracing) do not provide any insight into which model MLP layer would be best to edit in order to override an existing stored fact with a new one

Locator: abstract

[6] [Read-Best Is Not Steer-Best: A Probing-Steering Layer Dissociation in Omni-Modal Large Language Models](https://arxiv.org/abs/2609.22135) (2026) — Effect-based site selection: probe-best and steer-best layers dissociate, causally tested in three omni-modal models on emotion; not refusal, not language, not weight edits.

> Probe-best layers vary widely across architectures, while steering-effective layers consistently fall within a narrow mid-to-late range of normalized depth.

Locator: abstract

[7] [Cross-Architecture Steering Transfer in Language Models: A Systematic Empirical Study](https://arxiv.org/abs/2608.05164) (2026) — Cross-model steering transfer via SAE feature alignment over 15 semantic domains; establishes a scale threshold for transferability, but studies neither refusal nor language.

> Cross-model steering vectors (B3-TI) achieve a 71.0% win rate across 15 supervised concepts versus 68.0% for same-model native vectors

Locator: abstract

[8] [Refit the Probe: Single-Direction Ablation Is Not a Necessity Test](https://arxiv.org/abs/2606.00926) (2026) — Shows in text LMs that readability and ablation damage peak at different depths, and that single-direction ablation does not establish necessity.

> The correction also separates where a variable is most readable from where deleting it does most damage, and those are not the same layer in any pretrained model we study.

Locator: abstract

[9] [Refit the Probe (HTML full text)](https://arxiv.org/html/2606.00926) — Body sentence making the probe-best vs ablation-best separation explicit and noting Hase et al. reach the same shape from another pair of measurements.

> the layer with the highest probe accuracy is not the layer with the largest ablation response, in every pretrained model we ran, and a profile is fixed by neither measurement alone

Locator: discussion section

[10] [Predicting Where Steering Vectors Succeed](https://arxiv.org/abs/2604.15557) (Jayadev Billa; 2026) — A cheap training-free predictor of steering effectiveness and layer choice; the kind of instrument this run tried and failed to build in weight-edit space, never raced here.

> peak $A_{\mathrm{lin}}$ predicts steering effectiveness at $\rho = +0.86$ to $+0.91$ and layer selection at $\rho = +0.63$ to $+0.92$

Locator: abstract

[11] [Signatures of Steerability in Activation Space of Language Models](https://arxiv.org/abs/2609.14151) — Cheap separability statistics predict steerability; supports the view that simple diagnostics can beat elaborate geometry.

> simple separation metrics strongly correlate with the downstream steerability of language models across diverse settings, even after controlling for layers and dataset effects

Locator: abstract

[12] [Locating and Steering Refusal Beyond Attention](https://arxiv.org/html/2609.04721) — The nearest published statement that direction cosine is unreliable as a transfer predictor - for cross-architecture transport, with a mapped-random control.

> source direction can map to a high cosine, up to 0.515 across our pairs

Locator: Appendix A.6

> A cross-architecture transfer claim should therefore rest on the structural and behavioral specificity controls, not on a geometric similarity score.

Locator: Appendix A.6

[13] [Not All Refusals Are Equal: How Safety Alignment Fails Cybersecurity at Scale (HTML v2)](https://arxiv.org/html/2607.02714v2) (2026) — Contains the inherited '2-3 middle layers' sentence in Sec. 3.2 as an attribution to Arditi et al., immediately followed by the authors' statement that it does not generalise.

> abliterating a narrow local region of 2–3 middle layers can be as effective as ablating across all layers

Locator: Sec. 3.2, Layer Selection Strategies

> We found that this does not generalize to the broader set of modern models in our study: refusal in many architectures is distributed more widely

Locator: Sec. 3.2

[14] [Not All Refusals Are Equal (PDF v2)](https://arxiv.org/pdf/2607.02714v2) — Same Sec. 3.2 in the PDF, plus the layer-selection comparison: uniform spread beat signal-norm-based selection by up to ~70pp of additional refusal reduction across 24 models.

> substantially outperform norm-based selection (targeting layers with the highest refusal signal norm)

Locator: Sec. 3.2

[15] [No Single Neuron of Failure: Distributed Safety Alignment Against White-Box Attacks](https://arxiv.org/abs/2608.01414) (2026) — Training-time defence that makes safety redundantly distributed; the distributed-safety line this run's depth localisation is positioned against.

> we propose distributed safety alignment (DSA), which redundantly encodes safety capabilities across multiple computational neurons

Locator: abstract

[16] [Localizing Safety Alignment: MLP Layers and Mid-Network Blocks Encode Refusal Behavior in Large Language Models](https://arxiv.org/abs/2608.11583) (2026) — Weight-space localisation of refusal to mid-network MLP blocks, with an explicitly non-additive composition - the closest published parallel to this run's concentrate-beats-spread result.

> the block spanning layers 8-11 is selected first in all six greedy searches over model-dataset pairs

Locator: abstract

> in five of six greedy trajectories, adding more aligned blocks can reduce refusal performance

Locator: abstract

[17] [Decided Upstream, Written Late: Locating and Pricing the Cross-Lingual Refusal Circuit of a Multilingual MoE](https://arxiv.org/abs/2608.08032) (2026) — Cross-lingual mechanism paper: harm detection is shared and mid-network while the refusal write is late and orthogonal; independent support for shared representation with language-specific execution.

> Harm is encoded as an internal direction that is nearly language-invariant in mid-network

Locator: abstract

[18] [Decided Upstream, Written Late (PDF)](https://arxiv.org/pdf/2608.08032) — Body evidence that the language-shared harm signal is realised through near-disjoint expert sets by the output.

> mean cross-lingual Jaccard rises through the mid-network, peaks at 0.43 at L11

Locator: Appendix C

[19] [A StrongREJECT for Empty Jailbreaks](https://arxiv.org/abs/2402.10260) (2024) — Establishes that existing non-refusal/substring evaluation overstates jailbreak success relative to human judgement.

> we find that existing evaluation methods significantly overstate jailbreak effectiveness compared to human judgments and the StrongREJECT evaluator

Locator: abstract

[20] [A StrongREJECT for Empty Jailbreaks (full text)](https://arxiv.org/pdf/2402.10260) — Body sentence naming string matching for non-refusal as the most biased automated evaluator tested.

> Most of the baseline automated evaluators overestimate how effective jailbreak methods are on

Locator: Sec. 3.2

[21] [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models](https://arxiv.org/pdf/2308.01263) (2024) — Source of the partial-compliance class as a first-class annotation category alongside full compliance and full refusal.

> Partial refusal is any combination of refusal and compliance within the same response.

Locator: Table 4 caption

[22] [Validity-Aware Jailbreak Evaluation for Large Language Models](https://arxiv.org/abs/2609.00498) (2026) — Shows that enforcing validity reclassifies a large share of previously labelled jailbreak successes as invalid; motivates an explicit INVALID class.

> reclassifies 22.1\%--51.0\% of sampled prior-labeled successes as invalid across three of four public benchmarks

Locator: abstract

[23] [AdvPrefix: An Objective for Nuanced LLM Jailbreaks](https://arxiv.org/abs/2412.10321) (Sicheng Zhu, Brandon Amos, Yuandong Tian, Chuan Guo, Ivan Evtimov; 2024) — The closest neighbour on the SELECTION side: a misspecified objective inside an optimiser yields low loss without the intended behaviour, and repairing it changes what the search finds.

> this objective has two limitations: limited control over model behaviors, yielding incomplete or unrealistic jailbroken responses, and a rigid format that hinders optimization

Locator: abstract

[24] [How Reliable Is Your Jailbreak Judge? Calibration and Adversarial Robustness of Automated ASR Scoring](https://arxiv.org/abs/2606.25487) (2026) — Shows automated ASR judges disagree with humans and each other and are attackable; supports reporting judge-sensitivity ranges rather than a single number.

> Wrappers that leave the harmful text untouched and only add benign framing flip every LLM-judge between 57% and 100% of the time

Locator: abstract

[25] [How Does Quantization Affect Multilingual LLMs?](https://arxiv.org/abs/2407.03211) (2024) — Automatic metrics severely underestimate non-English degradation relative to human evaluation; bounds this run's automatic-only utility reading under NF4.

> a 1.7% average drop in Japanese across automatic tasks corresponds to a 16.0% drop reported by human evaluators on realistic prompts

Locator: abstract

[26] [Who Pays More for Safety? Measuring the Disparate Cost of Safety Alignment across Languages](https://arxiv.org/abs/2608.22490) (2026) — Uses abliterated checkpoints as the unaligned counterfactual across languages - the practice this run's negative bears on.

> non-English users consistently bear a higher Safety Cost than English users

Locator: abstract

[27] [Multilingual Refusal Alignment for Safer Large Language Models (RefusEU)](https://arxiv.org/abs/2606.07535) (2026) — Source of the official EN/SL evaluation data used by this run, and a second instance of abliteration used as an unaligned reference.

> aligning models exclusively in English is insufficient to ensure cross-lingual safety, even for the same harm categories

Locator: abstract

[28] [Multilingual Safety Signals Are Multi-Layered: Filtering Safety-Degrading Data for Safer LLMs](https://arxiv.org/abs/2609.22144) (2026) — The neighbour that most narrows this run's language-conditioned depth delta: language-specific safety-sensitive layers across 18 languages.

> sensitive layers are only partially shared across languages, with safety-relevant signals often distributed across multiple layers

Locator: abstract

[29] [Multilingual Steering by Design: Multilingual Sparse Autoencoders and Principled Layer Selection](https://arxiv.org/abs/2605.23036) (2026) — A language-aware a priori layer-selection rule already exists for SAE-based language control, though not for safety.

> steering layer-selection rule based on the intersection of multilingual alignment and language separability, which predicts effective intervention depths without exhaustive layerwise search

Locator: abstract

[30] [The Illusion of Cross-Lingual Safety in Low-Resource Languages](https://arxiv.org/abs/2608.11146) (2026) — Main published counterweight to direction universality; cross-lingual safety transfer is severely limited in four African languages.

> harmful prompts retain less than 10% of the English refusal signal across most language-model pairs

Locator: abstract

[31] [Low-Resource Safety Failures Are Action Failures, Not Representation Failures](https://arxiv.org/abs/2606.01196) (2026) — Separates representation from action for cross-lingual safety and repairs by recalibration; supports this run's information-vs-mapping reading.

> The relevant representation is present. Yet harmful refusal drops from 87.9% to 43.9%.

Locator: abstract

[32] [Does Fine-Tuning Undo Activation Steering? Behavioural Recovery Without Weight-Edit Reversal](https://arxiv.org/abs/2608.24988) (2026) — Published geometry/behaviour dissociation for a weight-embedded steering edit: geometry intact, behaviour reverted.

> the weight edit survives almost untouched even where behaviour reverts: mean vector recovery is $\rho = 0.004$

Locator: abstract

[33] [When Safety Speaks a Language: A Mechanistic Analysis of Safety-Language Identity Entanglement in LLMs](https://arxiv.org/abs/2608.29936) (2026) — Safety features are entangled with language identity, so ablating them affects the output language - independent support for this run's language-identity dead end.

> ablating safety features impacts not only harmful response rates but also target language

Locator: abstract

[34] [Analyzing the Generalization and Reliability of Steering Vectors](https://arxiv.org/html/2407.12404v1) (2024) — Steering effects are volatile across inputs and brittle out of distribution; grounds the refusal to treat one direction's effect as a stable model property.

> In-distribution, steerability is highly variable across different inputs.

Locator: abstract

[35] [Heretic: Fully automatic censorship removal for language models](https://github.com/p-e-w/heretic) — The tool this run builds on; its objective is stated as co-minimising refusal count and KL divergence.

> Heretic finds high-quality abliteration parameters by co-minimizing the number of refusals and the KL divergence from the original model.

Locator: README, overview section

[36] [Heretic config.default.toml (master, accessed 2026-09-24)](https://raw.githubusercontent.com/p-e-w/heretic/master/config.default.toml) — Shows that the default optimisation objective on master is still the substring KeywordRate scorer plus KL divergence, over an English prompt set, with scorers now a plugin list.

> { plugin = "heretic.scorers.keyword_rate.KeywordRate", optimization = "minimize"}

Locator: scorers list

[37] [Heretic PR #444: feat: add benchmark scorer](https://github.com/p-e-w/heretic/pull/444) — Merged benchmark scorer, dated; evidence that scorer plurality now exists in the tool.

> feat: add benchmark scorer

Locator: pull request title; page shows 'Merged' and 'Sep 3, 2026'

[38] [Heretic PR #445: feat: support specifying a dataset's specific config/subset](https://github.com/p-e-w/heretic/pull/445) — Merged dataset config/subset selection, which is what makes a multilingual construction set usable from the CLI.

> feat: support specifying a dataset's specific config/subset

Locator: pull request title; page shows 'Merged' and 'Sep 5, 2026'

[39] [heretic-org/Multilingual-Harmless-Harmful (dataset card, accessed 2026-09-24)](https://huggingface.co/datasets/heretic-org/Multilingual-Harmless-Harmful) — The community multilingual construction set for Heretic: nine subsets of 832 rows, with no Slovene and no Slavic language other than Russian.

> bengali (832 rows)english (832 rows)french (832 rows)hindi (832 rows)italian (832 rows)korean (832 rows)marathi (832 rows)russian (832 rows)tamil (832 rows)

Locator: dataset viewer subset list

[40] [Refusal Is Redundantly Distributed, Not Localized: A Per-Layer Ablation Study on Llama-3.1-8B](https://www.lesswrong.com/posts/Sj92Atv6qwNn5JxbF/refusal-is-redundantly-distributed-not-localized-a-per-layer) (2026) — Non-peer-reviewed per-layer replication showing no single layer is necessary for refusal in one English model.

> ablating every layer except 12 performs identically to ablating all 32

Locator: TL;DR

## Verification

Numbered citations resolve to unique listed sources. Passage checks test text occurrence, not claim truth or entailment. Author/year metadata and locators are not independently verified. Details: `research_verification.json`.

- Source [1]: text found — we show that refusal is mediated by a one-dimensional subspace, across 13 popular open-source chat m
- Source [2]: text found — activations at all layers and all token positions
- Source [2]: text found — In a transformer architecture, the matrices that write to the residual stream are: the embedding mat
- Source [3]: text found — a vector extracted from English can bypass refusals in other languages with near-perfect effectivene
- Source [4]: text found — ablation is applied across all layers and token positions to comprehensively eliminate refusal
- Source [5]: text found — localization conclusions from representation denoising (also known as Causal Tracing) do not provide
- Source [6]: text found — Probe-best layers vary widely across architectures, while steering-effective layers consistently fal
- Source [7]: text found — Cross-model steering vectors (B3-TI) achieve a 71.0% win rate across 15 supervised concepts versus 6
- Source [8]: text found — The correction also separates where a variable is most readable from where deleting it does most dam
- Source [9]: text found — the layer with the highest probe accuracy is not the layer with the largest ablation response, in ev
- Source [10]: text found — peak $A_{\mathrm{lin}}$ predicts steering effectiveness at $\rho = +0.86$ to $+0.91$ and layer selec
- Source [11]: text found — simple separation metrics strongly correlate with the downstream steerability of language models acr
- Source [12]: text found — source direction can map to a high cosine, up to 0.515 across our pairs
- Source [12]: text found — A cross-architecture transfer claim should therefore rest on the structural and behavioral specifici
- Source [13]: text found — abliterating a narrow local region of 2–3 middle layers can be as effective as ablating across all l
- Source [13]: text found — We found that this does not generalize to the broader set of modern models in our study: refusal in 
- Source [14]: text found — substantially outperform norm-based selection (targeting layers with the highest refusal signal norm
- Source [15]: text found — we propose distributed safety alignment (DSA), which redundantly encodes safety capabilities across 
- Source [16]: text found — the block spanning layers 8-11 is selected first in all six greedy searches over model-dataset pairs
- Source [16]: text found — in five of six greedy trajectories, adding more aligned blocks can reduce refusal performance
- Source [17]: text found — Harm is encoded as an internal direction that is nearly language-invariant in mid-network
- Source [18]: text found — mean cross-lingual Jaccard rises through the mid-network, peaks at 0.43 at L11
- Source [19]: text found — we find that existing evaluation methods significantly overstate jailbreak effectiveness compared to
- Source [20]: text found — Most of the baseline automated evaluators overestimate how effective jailbreak methods are on
- Source [21]: text found — Partial refusal is any combination of refusal and compliance within the same response.
- Source [22]: text found — reclassifies 22.1\%--51.0\% of sampled prior-labeled successes as invalid across three of four publi
- Source [23]: text found — this objective has two limitations: limited control over model behaviors, yielding incomplete or unr
- Source [24]: text found — Wrappers that leave the harmful text untouched and only add benign framing flip every LLM-judge betw
- Source [25]: text found — a 1.7% average drop in Japanese across automatic tasks corresponds to a 16.0% drop reported by human
- Source [26]: text found — non-English users consistently bear a higher Safety Cost than English users
- Source [27]: text found — aligning models exclusively in English is insufficient to ensure cross-lingual safety, even for the 
- Source [28]: text found — sensitive layers are only partially shared across languages, with safety-relevant signals often dist
- Source [29]: text found — steering layer-selection rule based on the intersection of multilingual alignment and language separ
- Source [30]: text found — harmful prompts retain less than 10% of the English refusal signal across most language-model pairs
- Source [31]: text found — The relevant representation is present. Yet harmful refusal drops from 87.9% to 43.9%.
- Source [32]: text found — the weight edit survives almost untouched even where behaviour reverts: mean vector recovery is $\rh
- Source [33]: text found — ablating safety features impacts not only harmful response rates but also target language
- Source [34]: text found — In-distribution, steerability is highly variable across different inputs.
- Source [35]: text found — Heretic finds high-quality abliteration parameters by co-minimizing the number of refusals and the K
- Source [36]: text found — { plugin = "heretic.scorers.keyword_rate.KeywordRate", optimization = "minimize"}
- Source [37]: text found — feat: add benchmark scorer
- Source [38]: text found — feat: support specifying a dataset's specific config/subset
- Source [39]: text found — bengali (832 rows)english (832 rows)french (832 rows)hindi (832 rows)italian (832 rows)korean (832 r
- Source [40]: text found — ablating every layer except 12 performs identically to ablating all 32

## Follow-up Questions

- Does the write-mass overlap quantity (or any placement statistic measured by single-layer causal ablation) beat the two one-forward-pass baselines out of sample, and if it does not, does the published logit-lens accessibility profile (arXiv 2604.15557) or the multilingual intersection layer rule (arXiv 2605.23036) beat them where ours failed?
- Is the language-dependence of edit placement reported here consistent with the language-specific safety-sensitive layers of arXiv 2609.22144 when both are measured on the same model and language set - i.e. does their sensitivity map predict our matched-energy winners, which would convert our result from a new observation into a causal confirmation of theirs?
- Given that abliterated checkpoints serve as the unaligned counterfactual in multilingual safety-cost measurement (arXiv 2608.22490, 2606.07535), how much does the measured Safety Cost of a language change if the counterfactual is re-selected per language rather than in English, and is that difference large enough to alter those papers' rankings?

---
*Generated by AI Inventor Pipeline*

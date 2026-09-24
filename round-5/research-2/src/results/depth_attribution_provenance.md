<!-- CARRIED TEXT. Where this file says `results/<name>` it means the DEPENDENCY's file of that name
(artifact art_sZ5w0yoY9o6L, iter_4/gen_art/gen_art_research_1/results/<name>). The ones this artifact
reuses are copied into this workspace as `results/_dep_<name>`; the rest stay at that path. -->

# The "2–3 middle layers" provenance, and the reconciliation sentence

Carried VERBATIM from the dependency's `results/unverified_claims.md` §1 (`art_sZ5w0yoY9o6L`), with the
`2607.02714` §3.2 passage re-verified in the v2 PDF this session (2026-09-24,
`results/raw/g_2607.02714_70pp.txt`).

---

## 1. What exists, and where the NOT VERIFIED flag now sits

**(i) The sentence DOES exist in arXiv 2607.02714 §3.2 "Layer Selection Strategies"**, identical in v1 and v2, as
that paper's own attribution to Arditi et al. [OBSERVATION]:

> "Layer selection is a critical element of the process. Arditi et al. found that abliterating a narrow local
> region of 2–3 middle layers can be as effective as ablating across all layers, and applied their technique to
> all layers' WO and Wout plus the embedding matrix."

**(ii) The attribution could not be located in Arditi et al.** Recorded outcome, in this exact wording, carried
unchanged: **the "2–3 middle layers" claim was not found in Arditi et al. (2406.11717v3) by these queries.** That
is weaker than "does not exist". It has NOT been re-attributed to any other paper. Regexes run by the dependency
over the full text of `https://arxiv.org/pdf/2406.11717v3`:
`middle layers|narrow|local region|single layer|subset of layers|all layers|2-3|2–3|few layers` (2 matches, both
describing all-layer ablation) and `weight orthogonalization|every matrix|W_{out}|matrices that write` (§4.1).
What Arditi et al. state is the opposite default: "We perform this operation at every activation x(l)i and
˜x(l)i, across all layers l and all token positions" (§2.4) [OBSERVATION].

**(iii) 2607.02714 REJECTS the claim in the next sentence** [OBSERVATION]:

> "We found that this does not generalize to the broader set of modern models in our study: refusal in many
> architectures is distributed more widely ... Thus, in our main experiment we opted for uniformly spread layer
> selection across 25–95% of model depth, which we found to substantially outperform norm-based selection
> (targeting layers with the highest refusal signal norm) by up to ∼70pp of additional refusal reduction at 30%
> on the most susceptible models."

**Where the flag sits, stated exactly.** The `NOT VERIFIED` flag is attached to the **ATTRIBUTION** (to Arditi et
al.), **not** to the existence of the sentence in 2607.02714, and **not** to the uniform-spread finding. The
~70pp figure and the uniform-spread result **ARE** verified from the primary source with their locator
(§3.2, PDF v2, re-verified this session; detailed comparison in App. C) [OBSERVATION].

**Standing instruction, carried verbatim.** It must not be cited as a standing depth fact; if used at all, it must
be written as a second-hand attribution inside 2607.02714 whose source we could not locate, accompanied by the
same paper's rejection of it.

---

## 2. The reconciliation sentence, to be pasted into the paper as-is

> 2607.02714 compares NORM-SELECTED layers against UNIFORMLY SPREAD layers and finds spread wins; this run
> compares a CONTIGUOUS mid-depth band against a STRIDED full-depth set AT MATCHED TOTAL REMOVAL ENERGY AND
> MATCHED LAYER COUNT, and finds the band wins — the two are different comparisons (selection criterion vs.
> energy-matched placement), so the results do not conflict, and this run's iteration-5 concentration-vs-location
> triplet (contiguous band / locally spread within the band's neighbourhood / spread over full depth) is the test
> that would make them commensurable.

---

## 3. One addition this round makes to the provenance question (OBSERVATION)

The depth claim the draft wanted from 2607.02714 does have a properly attributable home, and it is a different
paper: arXiv 2408.17003 (Li, Yao, Zhang, Li; ICLR 2025) states in its own abstract that it identifies "a small set
of contiguous layers in the middle of the model that are crucial for distinguishing malicious queries from normal
ones". That is the citation to use for "a contiguous mid-depth band is safety-critical" — with the caveats in
`results/neighbour_table_positive_additions.md` rows P1 and P2: its localisation is by input-vector angle analysis
plus over-rejection counting under weight SCALING, it is English-only, and it holds neither total energy nor layer
count fixed.

**What must NOT be written (INTERPRETATION).** "Prior work reports that 2–3 middle layers suffice." Nothing this
artifact located supports that sentence: 2607.02714 attributes it and then rejects it, the attribution target does
not contain it by the queries run, and 2408.17003's contiguous band is a located range per model (e.g. layers
7–12 discussed for Llama-3-8B-Instruct), not a universal 2–3 layers.

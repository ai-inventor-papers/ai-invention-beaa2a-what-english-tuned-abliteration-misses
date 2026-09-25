# Scope guard: what this artifact does NOT compute

This artifact is a **measurement warning about an English-only refusal scoring rule** (Heretic 3521f864's
33-substring `KeywordRate` marker list). It also bounds the bias that a downstream multilingual comparison inherits
from that rule. It is complete without saying anything about how to edit a model.

The following are **out of scope** and are not computed anywhere in `eval.py`, `rederive.py`, `audit.py` or
`figures.py`:

1. **No per-band, per-layer or per-location comparison.** No analysis compares where an edit sits in the model
   (depth region, layer set, band energy, attention vs MLP) with how much refusal it removes.
2. **No dose response.** Arms named `F_dose1.5`, `F_dose2.0` and `F_dose3.0` appear only as row identifiers. No curve,
   slope or monotonicity is fitted over dose.
3. **No ranking of configurations or candidates by efficacy.** Leg A5 (`results/reselection_scope.csv`) lists which
   candidate id each scorer's selection rule would pick inside its own pool, and the reference refusal count and KL
   of that candidate. This is evidence that the pool already contained candidates the certified reference scores
   better, i.e. a **scoring failure**. It is **not** a recommendation, and it reports no edit parameters, depth
   descriptors or dose.
4. **No recommendation of any edit**, and no procedure for producing one.
5. **No re-estimate of any published number.** Leg C is a bounded sensitivity statement under an explicitly tagged
   ASSUMPTION about the cost functional form. It is not a correction of arXiv 2608.22490.

Input files that contain placement or dose descriptors (`per_candidate.csv` columns `attn_*`, `mlp_*`, `sum_*`,
`params_json`; `candidate_descriptors.csv`; `coverage_*`) are read only for identifiers, or not at all.

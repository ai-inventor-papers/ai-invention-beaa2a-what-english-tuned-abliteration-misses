#!/usr/bin/env python3
"""results/deviations.json - every departure from the artifact plan, numbered, with its reason and its consequence.
Static items are written from what was actually done; dynamic items are read from the results they concern."""
from __future__ import annotations

import json

from common import RESULTS, WS, read_jsonl


def load(p):
    return json.loads(p.read_text()) if p.exists() else {}


def main() -> None:
    D = []

    def add(what: str, why: str, consequence: str) -> None:
        D.append({"id": f"D{len(D) + 1}", "deviation": what, "reason": why, "consequence": consequence})

    add("Workspace is gen_art_experiment_15, not the plan's gen_art_experiment_3.",
        "the pipeline assigned this workspace", "none; all relative paths are unchanged")
    add("Classifier identity check uses TWO hashes: the file sha256 (678cf09b...) and the bundle-internal sha (93a3f6d8...).",
        "the plan's 93a3f6d8... is the sha stored INSIDE the bundle (art_0XmNBGkzsJc_ hashes a pre-final dump); the file's own "
        "sha256 is 678cf09b... (scorer/refusal_clf.sha256)",
        "none: both verified (results/t0_instrument.json), and the classifier reproduces the in-loop objective's stored "
        "probabilities EXACTLY on 200 rows")
    reh = load(RESULTS / "rehearsal_gemma.json")
    add("Two SECONDARY statistics (GBF_low: GBF among candidates with C<=50; TBF: share of C<=10 candidates with K>10) and "
        "a calibration line were added to the freeze AFTER the Gemma rehearsal and BEFORE any GaMS3 reference number.",
        f"the rehearsal showed the plan's pairwise GBF is small for Gemma (all {reh.get('summary', {}).get('gemma_gbf_C_all', float('nan')):.3f}, "
        f"startup {reh.get('summary', {}).get('startup_gbf_C', float('nan')):.3f}): Gemma's objective is compressed "
        "(slope ~0.3), not flat, so most reference-differing pairs straddle the high/low boundary where K still moves; "
        "the reported blindness is local to the low-refusal region",
        "the PRIMARY statistic and PRED-1 are unchanged and reported first; the secondaries are labelled as post-Gemma "
        "declarations in configs/frozen_predictions.json and every table")
    add("Gemma per-candidate K, C, J are RE-SCORED from art_0XmNBGkzsJc_'s stored generations: trials 0-59 from its "
        "corrected run's startup draws (identical parameters), trials 60-115 from its tpe60_115 replay; both generated on "
        "an RTX 4090. GaMS3 was replayed here on an L4 (the GPU type of the iteration-1 journals).",
        "the plan reuses A11's 11,600 generations (no Gemma regeneration)",
        "fidelity is asymmetric: GaMS3 replay is bit-exact to its journal; Gemma's re-measured K differs from its L4 journal "
        "(mean +0.16, SD 2.27, max 6 over 56 draws). The drift-inflated sigma variant is reported for both searches")
    add("Gemma classifier counts on trials 60-115 include 36 trials whose in-loop rows were used in the classifier's ONE "
        "refit (art_0XmNBGkzsJc_); trials 0-59 (the paired headline) and all GaMS3 rows were never used for training.",
        "inherited from the certified bundle", "the paired headline is out-of-sample on both sides; the Gemma TPE/all "
        "numbers carry a mild in-sample advantage for C, cross-checked by the judge-referenced GBF (Gemma is fully judged)")
    add("art_xLy2vVlI7OEL/heretic_op.py is not a declared dependency; descriptors use the closed form of "
        "art_0XmNBGkzsJc_/coverage.py, validated on Gemma first.",
        "plan-prescribed graceful degradation",
        f"validation max relative error {load(RESULTS / 'descriptors_validation.json').get('max_rel_err')}; only the "
        "primary (Heretic's own per-layer direction) reference is computed - the x8 secondary reference exists only for Gemma")
    add("Judge target convention follows art_0XmNBGkzsJc_'s certification: refusal = CLASS refused OR empty (Heretic's own "
        "scorer rule counts empty output as refusal); malformed rows are excluded; a strict variant (empty excluded) is reported.",
        "comparability with the Gemma certification numbers the plan reports beside", "PARTIAL and malformed are never "
        "folded into refusal; empty responses are rare in edited cells (see class counts)")
    add("The bought gpt-4.1 subsample excludes EMPTY responses.",
        "empty rows are auto-labelled 'empty' by the frozen protocol for both judges (never sent to any model)",
        "the sample is 800 (or fewer if the pool is smaller) of the non-empty certification rows")
    add("The bootstrap holds each population's tolerance (sigma_bar*sqrt 2) fixed across resamples.",
        "the frozen definition computes sigma_bar once per search", "CIs do not include the (small) uncertainty of sigma_bar")
    add("art_KFZCxJcrr84K's (iteration 2) panel files were not used; gate G1 was re-verified directly from both raw journals "
        "(raw jsonl parse AND optuna JournalStorage, identical).",
        "the plan asks to re-verify, not trust", "none")
    add("Plan item (6) (an extra optimiser seed for the second search) was DROPPED, as the plan pre-declares; no edited "
        "checkpoint was selected, built, exported or recommended.", "measurement artifact; P7 already fired", "none to the claim")
    add("A POST HOC selection-point judging tier (J3: 200 rows of the two GaMS3 candidates the frozen rule selects under "
        "K and under C, trials 88 and 85) was added after the first two-search analysis.",
        "the plan's S7 asks for the refusal count under each scorer at the selected candidates; neither was in J1/J2",
        "J3 labels are reported ONLY at the selection points; they are excluded from every agreement statistic, the oracle "
        "threshold, every judge-referenced GBF and the judge-based reselection (those trials were chosen by the rule)")
    add("An EXPLORATORY per-pair tolerance variant of GBF (tol_ij = sqrt(s_i^2 + s_j^2)) was added post hoc.",
        "the frozen median-based tolerance is dominated by near-ceiling candidates whose binomial SD vanishes (Gemma "
        "startup sigma_bar 1.0 while low-region candidates have SD ~4)", "reported beside the frozen value; it does not "
        "change any verdict")
    add("score.py bug fixed before any final number: unjudged rows (NaN) were coded as judged non-refusals.",
        "found when the first GaMS3 scoring reported 11,700 judged rows instead of 2,099", "certification was unaffected "
        "(it reads the raw class columns); every analysis number was computed after the fix")
    add("T7 (mid-flight look at the GaMS3 K-vs-C plot after Tier 1) was deliberately skipped.",
        "all three replay tiers fit the budget, so no reallocation decision needed it, and skipping it kept GaMS3's C unread "
        "until both certification gates were on disk", "none")
    add("The frozen selection rule is imported from a verbatim local copy (select_rule.py, sha-identical to "
        "art_0XmNBGkzsJc_/select_rule.py) instead of the iteration-3 workspace.", "self-contained repository", "none")
    ch = load(RESULTS / "checks.json")
    if ch:
        add("Code changed after the freeze: " + ", ".join(sorted(ch.get("files_changed_since_freeze", {}))) +
            "; files written after the freeze: " + ", ".join(ch.get("files_created_after_freeze", [])) + ".",
            "post-freeze hardening (dtype cast, NaN handling), the unedited-model row, the dataset-audit stage and output "
            "writers; none of the frozen DEFINITIONS changed",
            "full unified diff in results/code_changes_since_freeze.diff; analysis_py_unchanged="
            f"{ch.get('analysis_py_unchanged')}")
    col = load(RESULTS / "collect_report.json")
    if col and col.get("n_trials", 116) < 116:
        add(f"Only {col['n_trials']} of 116 GaMS3 trials were replayed.", "time", "tiered stop, see replay tiers")
    gp = load(RESULTS / "gpt41_purchase.json")
    if gp:
        if gp.get("status", "").startswith("F5"):
            add("gpt-4.1 arm NOT bought (OpenRouter unavailable).", gp.get("probe", {}).get("msg", ""),
                "the within-edited-cell judge gate is UNVERIFIED against a frontier judge")
        elif gp.get("fallback_400"):
            add("gpt-4.1 purchase fell back to the 400-row stratified prefix.", "projected cost > $2.50", "wider CI on the judge gate")
    qj = read_jsonl(RESULTS / "judge_in/gams_J2.jsonl")
    if qj:
        lab = {r["key"] for r in read_jsonl(RESULTS / "judge_out/gams_inloop_qwen.jsonl") if not r.get("judge_fail")}
        n_done = sum(1 for r in qj if r["key"] in lab)
        if n_done < len(qj):
            add(f"Judge extension J2 incomplete: {n_done}/{len(qj)} rows labelled.", "time", "judge-referenced paired GBF on fewer draws")
    (RESULTS / "deviations.json").write_text(json.dumps(D, indent=1))
    print(f"{len(D)} deviations written")


if __name__ == "__main__":
    main()

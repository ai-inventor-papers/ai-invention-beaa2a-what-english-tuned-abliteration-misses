#!/usr/bin/env python3
"""results/deviations.json - every departure from the artifact plan, with the evidence file that shows it."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C


def main() -> None:
    S = C.jload(C.RES / "analysis_summary.json") if (C.RES / "analysis_summary.json").exists() else {}
    T = pd.read_parquet(C.RES / "cells.parquet") if (C.RES / "cells.parquet").exists() else pd.DataFrame()
    jc = S.get("judge_certification") or {}
    groups = C.jload(C.CFG / "matched_groups.json") if (C.CFG / "matched_groups.json").exists() else {}
    D = []

    def dev(what, why, evidence, cost):
        D.append({"deviation": what, "reason": why, "evidence": evidence, "cost": cost})

    dev("Strength levels are c in {0.25, 0.5, 1.0, 1.5}, not {0.25, 0.5, 1.0, 2.0}.",
        "The plan clips the strength factor at Heretic's max_weight = 1.5; c = 2.0 is out of family for a weight edit "
        "(c = 2 is a Householder reflection, which flips rather than removes the component). The single-site c = 2 "
        "ACTIVATION anchor (exp8 X4) is kept, because exp8 ran it as an activation arm.",
        "method.py STRENGTHS; results/cells.csv", "the dose curve spans 6x rather than 8x in coefficient.")
    dev("The random control draws its directions from each layer's WRITE space (columns of W_o / W_down applied to "
        "Gaussian inputs), not from an isotropic Gaussian or the harmless-residual PC span.",
        "exp8 found isotropic/PC-span Gaussian draws could match d_EN(h)'s projection energy at only 15/48 layers. A "
        "draw in the write space of the very modules being edited is the control that can reach the real edit's energy, "
        "which is what the matched-energy design needs.",
        "method.py random_write_dirs; results/cells/R_*__draws.json (per-draw energy and collateral)",
        "the control is 'a generic direction the module actually writes', a stronger control than isotropic noise but "
        "not an isotropic-noise control; the energy-matched harmless-PC arm is reported beside it.")
    dev("Controls are matched to the real cell's energy by ONE scalar applied to the real cell's coefficient profile "
        "(coefficients capped at 2), rather than by re-solving per layer.",
        "It keeps the control's coverage descriptor identical to the real cell's, so a coverage regression cannot be "
        "moved by the control's own coverage; the achieved energy ratio is reported per cell.",
        "method.py scaled_control; results/cells/*.json field E vs E_target", "energy is matched in aggregate, not per layer.")
    k = jc.get("kappa_on_disk_edited")
    if k is not None and k < 0.80:
        dev(f"Scorer certification on labels already on disk reached kappa = {k:.3f} (< 0.80) within EDITED checkpoints.",
            "Plan Stage 1 then buys one stratified gpt-4.1 subsample on THIS run's edited cells and recertifies.",
            "results/judge_certification.json; results/judge_api.jsonl; results/api_costs.jsonl",
            "every headline rate is reported as a range across judges, with the PARTIAL column visible; "
            + ("the bought subsample's kappa is in judge_certification.P3_this_run." if (C.RES / "judge_api.jsonl").exists()
               else "the subsample could not be bought (see api_costs / logs), so the confirmatory family is labelled with the "
                    "on-disk kappa attached."))
    g2 = C.jload(C.RES / "gate2_anchor_check.json") if (C.RES / "gate2_anchor_check.json").exists() else None
    if g2:
        dev("Gate 2 is scored as containment in the interval spanned by exp8's OWN two judges on the SAME items, not as "
            "proximity to one exp8 judge.",
            "exp8's two judges disagree by up to 0.60 on English edited cells (gpt-4.1 0.00 vs Qwen 0.60 on A1 EN) because "
            "they split the PARTIAL class differently, so 'within 0.15 of exp8' is not well posed for English. Both "
            "criteria are recorded per cell.",
            "results/gate2_anchor_check.json (fields *_inside_exp8_band and *_within_0.15_of_band)",
            f"primary criterion passes ({g2['pass']}); the single-judge criterion does not ({g2['pass_secondary_single_judge']}), "
            "and the English gap is attributed to the judge's PARTIAL definition, which is reported as its own column.")
    dev("Part A uses a k-grid of 4 (k = 4, 8, ..., 48) for both the prefix and the suffix family.",
        "Plan's grid, unchanged; the index is therefore resolved to +-4 layers and is reported with a bootstrap CI over "
        "the same grid.", "results/redundancy_index.json", "index resolution is 4 layers.")
    if groups:
        sh = [g for g, G in groups.items() if G.get("narrow_shifted")]
        if sh:
            dev(f"Matched-energy groups {sh} needed the narrow cell's coefficient shifted down to keep the solved broad "
                "coefficient inside Heretic's max_weight = 1.5.",
                "Plan's own rule ('if a solved c exceeds 1.5, shift the narrow cell's c down and re-solve').",
                "configs/matched_groups.json (narrow_shifted)", "the group's absolute energy is lower than planned; the "
                "pairing is still matched within 10%.")
    if len(T):
        un = T[(T["family"] == "random") & (T["matched"] == False)]["cell"].tolist()  # noqa: E712
        if un:
            dev(f"{len(un)} random control cells could not be matched on energy AND collateral simultaneously: {un}.",
                "Reported as the plan requires (per-draw shortfall recorded), with the energy-matched harmless-PC arm as "
                "the primary control for those groups and the random arm as a lower bound.",
                "results/cells/R_*__draws.json; results/report_tables.md", "the random arm is conservative for those groups.")
    dev("One model (gemma-3-12b-it), NF4 throughout, one Heretic seed, no bf16 rebuild.",
        "Plan's declared departures: a 12B bf16 model does not fit 24 GB with a 14B judge, and a second full factorial "
        "does not fit the wall clock. GaMS3 is quoted from iteration 2 as a two-point contrast.",
        "results/gate0_pins.json; results/redundancy_index.json (gams3_contrast_quoted_not_measured)",
        "the depth-coverage law is a within-model claim with n = 1 checkpoint; absolute levels are NF4-specific.")
    dev("Weight edits are exact output-projection hooks on o_proj / down_proj, not materialised weights.",
        "For a linear map this equals W <- (I - c r r^T) W (Arditi/Heretic orthogonalisation); unit-tested against the "
        "explicit product (relative error 0.0 on a 512-column slice).",
        "results/gate1_unit_tests.json", "Gemma-3 applies post_attention_layernorm / post_feedforward_layernorm AFTER "
        "these projections, so the operator does not guarantee the direction is absent from the residual write - the same "
        "limitation Heretic's own weight edit has on Gemma-3.")
    dev("Heretic's norm-preserving rank-3 LoRA (row_normalization='full') is not reproduced per cell.",
        "Norm preservation is a second operator knob that would confound the coverage x strength design. The tie to the "
        "real edit is carried by the W0/W3/W4 anchor cells, which ARE the trial-96 adapter, and by K96g, which applies "
        "trial-96's own kernel and interpolated global direction through the plain operator.",
        "configs/k96_kernel.json; results/cells/W0_core.json", "the factorial speaks to the operator family, not to a "
        "byte-identical Heretic trial.")
    dev("Native Slovene review of the items and the outputs is PENDING (not performed).",
        "No qualified reviewer in this pipeline; Slovene items are machine-translated with automated back-translation QC "
        "from the frozen dataset artifact.", "gen_art_dataset_1/data/split_manifest.json (metadata_review_status PENDING)",
        "stated beside every Slovene number.")
    s5 = sorted(C.GENS.glob("S5X_*.json"))
    if s5:
        dev(f"S5X (the only verified paired basis) was touched ONCE at the end for {len(s5) - 1} cell(s) plus the no-op.",
            "Declared second touch, chosen by the frozen rule in frozen_predictions.s5x_rule after all other analysis.",
            "configs/s5x_cells.json; results/gens/S5X_*.json", "the paired SL-EN gap for those cells rests on <= 100 pairs "
            "and is one confirmatory comparison, not a sweep.")
    else:
        dev("S5X second touch: NOT performed.", "Time budget; the plan states an unfinished touch is worse than none.",
            "results/gens/ contains no S5X_* files", "no new paired cross-language claim; the SL-EN comparisons rest on the "
            "S3/S4 twin pairs, whose correspondence is graded, not verified.")
    if S.get("P1", {}).get("mde_dR2_80pct_power", 0) > 0.10:
        dev("P1 is labelled EXPLORATORY: the achieved cell count leaves a minimum detectable dR2 above the 0.10 bar.",
            "Plan's power rule ('if MDE > 0.10, say so BEFORE reporting P1').", "results/analysis_summary.json P1.power_note",
            "the dR2 point estimate and CI are reported, but P1 is not counted as confirmatory.")
    C.jdump({"n": len(D), "deviations": D}, C.RES / "deviations.json")
    print(f"{len(D)} deviations -> results/deviations.json")
    for d in D:
        print("-", d["deviation"][:110])


if __name__ == "__main__":
    main()

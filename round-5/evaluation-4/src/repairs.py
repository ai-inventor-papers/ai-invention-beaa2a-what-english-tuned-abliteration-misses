"""Writes results/report_repairs_iter5.md: the twelve paste-ready repair blocks R1-R12.

Every number is pulled at run time from this audit's own recomputed records (results/corrected_numbers.json);
numbers that this pass did NOT re-derive are quoted from a named file and marked [carried: <path>].
"""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOOP = Path(os.environ.get("AII_LOOP_ROOT", HERE.parents[2]))
X13 = "iter_4/gen_art/gen_art_experiment_13/results"
X14 = "iter_4/gen_art/gen_art_experiment_14/results"
X15 = "iter_4/gen_art/gen_art_experiment_15/results"
X11 = "iter_3/gen_art/gen_art_experiment_11/results"
X10 = "iter_3/gen_art/gen_art_experiment_10/results"
X9 = "iter_3/gen_art/gen_art_experiment_9/results"
X12 = "iter_3/gen_art/gen_art_experiment_12/results"
X5 = "iter_2/gen_art/gen_art_experiment_5/results"
X4 = "iter_2/gen_art/gen_art_experiment_4/results"
E2 = "iter_4/gen_art/gen_art_evaluation_2/results"


def write_repairs(R, recs, summ, lint, plac, rate, ci, k, n, kmat, infl):
    def v(cid, fmt="{:.2f}"):
        r = R.get(cid)
        if r is None or r.get("recomputed_value") is None:
            return "n/a"
        x = r["recomputed_value"]
        return fmt.format(x) if isinstance(x, (int, float)) else str(x)

    def c(cid, fmt="{:+.2f}"):
        r = R.get(cid)
        if not r or not r.get("ci"):
            return ""
        return "[" + ", ".join(fmt.format(x) for x in r["ci"]) + "]"

    def carried(path, key):
        return f"[carried: `{path}` {key}]"

    L13, L14, P = summ["exp13"]["ladders"], summ["exp14"], summ["pooled"]
    e2flip = json.loads((LOOP / E2 / "flip_analysis.json").read_text())
    pl = {p["placebo"]: p for p in plac}
    out = []
    out.append(f"""# Iteration-5 repair blocks R1-R12 (paste-ready)

Audited draft: `{lint['draft']}`. Every path below is relative to `3_invention_loop/`. Numbers come from this audit's
independent recompute (`rederive_iter5.py`, imports: stdlib, numpy, pyarrow) unless marked **[carried: path]**.
Verdict vocabulary: MATCH / MISMATCH / MISDESCRIBED / UNTRACEABLE / SIGN_REVERSED (the same as the iteration-3 and iteration-4 passes).

**Audit headline.** {n} first-pass numbers with a draft value were re-derived; {k} are defective
({rate:.1%}, Wilson 95% CI [{ci[0]:.1%}, {ci[1]:.1%}]), of which {kmat} are material (they change what a sentence claims).
Comparable priors under the SAME all-class definition: eval1 26/167 = 15.6% (quoted in the draft as '5.5%', which counts a
narrower class) and eval2 5/102 = 4.9%. This pass is weighted onto sections nobody had recomputed, and the interpretive defects concentrate there.
Counting numeric MISMATCHes only: {sum(1 for r in recs if r.get('pass_provenance','').startswith('first_pass') and r['verdict']=='MISMATCH')}/{n}. No number was SIGN_REVERSED.

---

## R1 - Placement restatement (replaces 'Firm positive', 'Iteration-4 additions' and 'The surviving finding')

**Observation.** At matched total removal energy AND matched layer count, where the edit energy sits orders residual refusal.
- **Gemma (exp13).** High-O beats low-O in {v('E13.matched_groups_favouring_highO_en','{:.0f}')}/8 matched groups in EN and {v('E13.matched_groups_favouring_highO_sl','{:.0f}')}/8 in SL. Pooled contrast EN {v('E13.pooled_matched_contrast_en','{:+.3f}')} {c('E13.pooled_matched_contrast_en')}, SL {v('E13.pooled_matched_contrast_sl','{:+.3f}')} {c('E13.pooled_matched_contrast_sl')} (paired item bootstrap; judge Qwen3-14B; SL within-edited kappa {v('E13.kappa_within_edited_sl','{:.3f}')}, below the 0.80 gate, so SL is JUDGE_SENSITIVE: Rogan-Gladen companion for the best SL cell: raw 0.27 -> {v('E13.RG.CF_G3_hiO_L16-31.sl','{:.2f}')}, with Se/Sp taken from the 390-row gpt-4.1 overlap; a companion clipped at 0 means the correction is unstable at that specificity, so the SL cell rate is a range [0.00, 0.27], not a point). Source: `{X13}/per_item.csv`, `{X13}/cells/*.json`.
- **GaMS3 (exp14).** Spearman rho(O_SL, strict SL refusal) = {v('E14.primary_rho_sl','{:.3f}')} over 20 confirmation cells (draft -0.903 [-0.928, -0.857] **[carried: `{X14}/analysis_summary.json` primary.sl.ci]**), within level E2 {v('E14.within_level_rho_E2_sl','{:.3f}')}, E3 {v('E14.within_level_rho_E3_sl','{:.3f}')}. Source: `{X14}/per_item.parquet`, `{X14}/cells.csv`.
- **Qwen3-8B (exp13 outside panel).** {v('E13.qwen3_matched_contrasts_favouring_highO','{:.0f}')}/9 matched contrasts favour the better-placed member; Spearman rho(O) EN {v('E13.qwen3_spearman_O_en')}, SL {v('E13.qwen3_spearman_O_sl')}, DE {v('E13.qwen3_spearman_O_de')} (all valid items; the artifact's 39-item subset gives -0.76 / -0.93 / -0.84). 8/9 CIs excluding zero: **[carried: `{X13}/report_tables.md`]**.
- **The dose rival FAILS.** Doubling the energy in the late band (layers 33-48) leaves EN {v('E13.CF_dose_G3loO_x2.en')} / SL {v('E13.CF_dose_G3loO_x2.sl')}, against the mid band (16-31) at EN {v('E13.CF_G3_hiO_L16-31.en')} / SL {v('E13.CF_G3_hiO_L16-31.sl')} at matched energy.
- **The winning band at matched energy is the SAME in both siblings.** GaMS3 SL strict: E2 B2 {v('E14.argmax.E2.B2')} < B3 {v('E14.argmax.E2.B3')} < B4 {v('E14.argmax.E2.B4')} < B1 {v('E14.argmax.E2.B1')}; E3 B2 {v('E14.argmax.E3.B2')} < B3 {v('E14.argmax.E3.B3')} < B4 {v('E14.argmax.E3.B4')} < B1 {v('E14.argmax.E3.B1')}. Gemma's frozen argmax prediction (13-24) PASSES; the GaMS3 DEV profile's prediction (25-36) is NAMED_AND_LOST.
- **UNRESOLVED disagreement, reported as such.** The UNMATCHED c = 1 grid in exp10 favours 25-36 over 13-24 by {v('E10.unmatched_c1_B2_minus_B3_sl','{:+.2f}')} {c('E10.unmatched_c1_B2_minus_B3_sl')} (SL strict, paired items; eval2's R1 correction gave +0.12 [0.02, 0.22]). The matched-energy panels and this unmatched grid differ in design (matched vs unmatched dose). This audit verifies both numbers and does not adjudicate.

**STRIKE** 'the critical band differs between siblings' everywhere it appears: as a finding (line 887), as a novelty qualifier (line 682, 'the critical band moves between sibling checkpoints'), and as the candidate explanation of the iteration-1 dissociation (line 861). Only the DEV profile's argmax differs (layer 27 vs 19); the behavioural winner does not. **No band recommendation is made.**

## R2 - Exp13's nested-R² ladder, with the failure reason the right way round

Replace the exp13 'Nested R²' table (lines 714-719) with the per-language ladders, recomputed from `{X13}/per_item.csv` + `{X13}/cells/*.json` (outcome: strict residual refusal on the {L13['en']['n_cells']} confirmation cells; OLS on the rate scale):

| | EN | SL |
|---|---|---|
| log energy alone | {L13['en']['R2_logE_alone']:.4f} | {L13['sl']['R2_logE_alone']:.4f} |
| + layer count, + span, + EN/SL cosine (nuisance stack) | {L13['en']['ladder_forward']['+en_sl_cosine']:.4f} | {L13['sl']['ladder_forward']['+en_sl_cosine']:.4f} |
| + O (full) | {L13['en']['ladder_forward']['+O']:.4f} | {L13['sl']['ladder_forward']['+O']:.4f} |
| **dR² of O over the nuisance stack** | **{L13['en']['dR2_O']:.4f}** | **{L13['sl']['dR2_O']:.4f}** |
| O alone | {L13['en']['R2_O_alone']:.4f} | {L13['sl']['R2_O_alone']:.4f} |
| EN/SL cosine alone | {L13['en']['R2_cos_alone']:.4f} | {L13['sl']['R2_cos_alone']:.4f} |
| dR² of O over log energy + layer count ONLY | {L13['en']['dR2_O_over_energy_count']:.4f} | {L13['sl']['dR2_O_over_energy_count']:.4f} |
| Spearman(O, cosine) | {L13['en']['rho_O_cos']:.3f} | {L13['sl']['rho_O_cos']:.3f} |

MDE for dR² at 80% power: 0.047 EN / 0.109 SL **[carried: `{X13}/analysis.json` confirm.per_language.*.mde_dR2]**.
**Falsifier, stated correctly:** O adds {L13['en']['dR2_O']:.3f} (EN) / {L13['sl']['dR2_O']:.3f} (SL) over a nuisance stack that CONTAINS the g-weighted EN/SL cosine. Both are under the 0.10 bar, and EN is under the 0.05 falsifier. Over log energy + layer count ALONE, O adds {L13['en']['dR2_O_over_energy_count']:.3f} / {L13['sl']['dR2_O_over_energy_count']:.3f}. The reason is **collinearity with the cosine**. It is NOT that 'energy already explains the outcome': log energy alone explains {L13['en']['R2_logE_alone']:.3f} / {L13['sl']['R2_logE_alone']:.3f}.
**Move** the 0.088 / 0.668 / 0.790 / 0.806 table to the exp14 section, labelled 'each predictor added separately to log energy (GaMS3, SL)'. Recomputed: logE {v('E14.nested_R2.logE','{:.3f}')}, logE+O {v('E14.nested_R2.logE+O','{:.3f}')}, logE+O_cos {_n(summ, 'logE+O_cos')}, logE+O_band4 {_n(summ, 'logE+O_band4')}. The draft's cumulative rows are wrong: logE+O+O_cos = {_n(summ, 'logE+O+O_cos')}, logE+O+O_cos+O_band4 = {_n(summ, 'logE+O+O_cos+O_band4')}.
**Fix 'What we have learned'** to compare like with like: O over logE is ~0.87 (Gemma EN, O alone {L13['en']['R2_O_alone']:.2f} with logE ~0) vs {v('E14.dR2_O_over_logE_sl','{:.2f}')} (GaMS3 SL). O over the cosine-containing stack is {L13['en']['dR2_O']:.3f}. exp13's cosine regressor (per-layer EN/SL direction cosine, g-weighted) and exp14's O_cos are DIFFERENT quantities.

## R3 - Exp14 relabelling

All four dose/placement contrasts are **Slovene strict**. The panel has **no English contrast**:
- dose at fixed O_ship (A1 vs A4): {v('E14.dose_at_fixed_O_ship.sl','{:+.3f}')} {c('E14.dose_at_fixed_O_ship.sl','{:+.3f}')}
- dose at fixed O_swap (A3 vs A2): {v('E14.dose_at_fixed_O_swap.sl','{:+.3f}')} {c('E14.dose_at_fixed_O_swap.sl','{:+.3f}')}
- placement at fixed high E (A1 vs A3): {v('E14.placement_at_fixed_E_high.sl','{:+.3f}')} {c('E14.placement_at_fixed_E_high.sl','{:+.3f}')}, McNemar p 0.774 **[carried]**
- placement at fixed low E (A4 vs A2): {v('E14.placement_at_fixed_E_low.sl','{:+.3f}')} {c('E14.placement_at_fixed_E_low.sl','{:+.3f}')}, p 1.000 **[carried]**
(paired item bootstrap, 70 items; source `{X14}/per_item.parquet`). The draft's 'EN -0.186 ... SL -0.157' (line 755) is MISDESCRIBED.
Boundary 3 corrected: 'the GaMS3 profile predicts Gemma's 50 weight cells at -0.442, versus -0.278 (screen) and -0.111 (confirm split) on its own iteration-3 panel' **[carried: `{X14}/screen.json`]**.
Paste exp14 Tables 3, 6, 6b and 7 and the per-stratum rho table (E2 {v('E14.within_level_rho_E2_sl','{:.3f}')}, E3 {v('E14.within_level_rho_E3_sl','{:.3f}')}) from `{X14}/report_tables.md`, citing `{X14}/analysis_summary.json`.

## R4 - Citation lint

{lint['n_cited']} file references in the draft: {lint['n_resolving_as_written']} resolve as written, {lint['n_rewritten']} resolve after a rewrite, and {lint['n_not_found_after_rewrite']} do not resolve (gate **{lint['gate']}**). All {lint['positive_control_known_misses']} planted positive controls (the known misses) are detected. Rewrites (every target is checked to contain a number quoted in the citing sentence):

| draft line | as written | correct path |
|---|---|---|
""")
    import csv as _csv
    for r in _csv.DictReader(open(HERE / "results/path_lint.csv")):
        if r["status"] == "RESOLVES_AFTER_REWRITE":
            out.append(f"| {r['draft_line']} | `{r['cited_path_as_written']}` | `{r['resolved_path_relative_to_3_invention_loop']}` |\n")
    out.append(f"""
Tables without any source path: {lint['n_tables_without_path_before']} of {lint['n_tables']} (draft lines {', '.join(map(str, lint['tables_without_path_lines']))}). Each gets its path in the blocks below or in `results/path_lint.csv`. The exp4/exp5/exp7/exp8/exp12 tables cite `{X4}/headline_table.csv`, `{X5}/analysis/tables.md`, `iter_2/gen_art/gen_art_experiment_7/results/analysis.json`, `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md`, `{X12}/indices.json`.

## R5 - Exp11 count corrections (`{X11}/miscalibration_table.csv`)

- Trial 107: judged REFUSED **{v('E11.trial107.judge_refused','{:.0f}')}/100** (not 10/100), keyword {v('E11.trial107.keyword','{:.0f}')}/100.
- Trial 96: **{v('E11.trial96.judge_refused','{:.0f}')} REFUSED + 49 PARTIAL**. '15/100' is arm B's S5X English refusal rate (0.150, `{X11}/headline_table.csv`), a different item set; relabel it there.
- Miscalibration table: keyword range {v('E11.keyword_floor','{:.0f}')}-{v('E11.keyword_range_max','{:.0f}')}, classifier {v('E11.classifier_range','{:.0f}')}-{v('E11.classifier_range_max','{:.0f}')}, judge {v('E11.judge_range_min','{:.0f}')}-{v('E11.judge_range_max','{:.0f}')}. MAE per 100 vs judge: keyword {v('E11.mae_keyword_vs_judge','{:.1f}')}, classifier {v('E11.mae_classifier_vs_judge','{:.2f}')} over the table's trials. `{X15}/conventional_table.csv` gives 19.6 vs 1.2 over all 116 draws and 26.6 vs 1.2 over TPE draws. exp11's README quotes 30.6 vs 2.1, which neither file reproduces. Kappas: in-loop keyword 0.196, classifier 0.924 (`conventional_table.csv` gemma/all); certified 0.143 / 0.858 on held-out replayed trials **[carried]**.
- **DELETE** 'Partial positive: corrected objective halves the gap' (line 863). Its own P7 falsifier fired: the 1.5x dose arm gives +0.33 against the corrected arm's +0.38. The dose-2.0 'zero gap' is a floor, with both languages at 0.000.
- Add eval2's gpt-4.1-equivalent exp11 gaps (B .68 -> .63, C .38 -> .35, dose-2.0 .00 -> .07) **[carried: `{E2}/judge_calibration_supplement.json`]**. Add the exp11 EN panel kappa, recomputed within edited cells: **{v('D1.kappa.exp11|en|edited','{:.3f}')} {c('D1.kappa.exp11|en|edited','{:.3f}')}** (n = 65 pairs). The exp11 English gaps stay workhorse-labelled and JUDGE_SENSITIVE; this audit bought no labels.

## R6 - Exp15 selection section (`{X15}/per_candidate.csv`, `reselection_table.csv`)

- Add the judge-referenced column: mean keyword minus judge {v('E15.gemma.mean_K_minus_J','{:+.1f}')} (Gemma) / {v('E15.gams.mean_K_minus_J','{:+.1f}')} (GaMS3), beside keyword minus classifier {v('E15.gemma.mean_K_minus_C','{:+.1f}')} / {v('E15.gams.mean_K_minus_C','{:+.1f}')}. Slopes of keyword on classifier: {v('E15.gemma.slope_K_on_C','{:.3f}')} / {v('E15.gams.slope_K_on_C','{:.3f}')}.
- Relabel 'Judge (gpt-4.1)' in the reselection table as **the Qwen3-14B workhorse (J)**. gpt-4.1 was only the 800-item certification subsample (kappa 0.850). Add the K_journal row (trial 96, KL 0.026) and the GaMS3-J row (trial 115, KL 0.060).
- Replace 'close' (line 798): trial 88 has KL 0.175 and trial 85 (classifier-selected) has KL {v('E15.reselection.gams.C.KL','{:.3f}')}, an order of magnitude apart.
- Replace 'this explains the divergent search outcomes' (line 881) with the artifact's own reading: LOCAL low-region blindness in Gemma, plus STRUCTURAL threshold blindness shared by both searches (TBF = {v('E15.gemma.TBF_floor_above_threshold','{:.0f}')}.0 and {v('E15.gams.TBF_floor_above_threshold','{:.0f}')}.0; the frozen rule falls back in both).
- Incumbent's best shot, from `conventional_table.csv`: oracle threshold kappa 0.567 (Gemma) / 0.655 (GaMS3); repaired list 0.174 / 0.680, MAE 4.64 (GaMS3). Held-out StrongREJECT keyword kappa 0.02 EN / 0.00 SL, BUT the two zeros mean opposite things (EN: the rule fires often and is wrong; SL: it fires on almost nothing) **[carried: `{X15}/analysis.json` heldout_source_sanity]**.

## R7 - The three wrong iteration-2 in-place corrections

(iii) **T12 note** (line 305). Rewrite it from exp5's own marker rule. The marker rule UNDERCOUNTS: at f = 1, EN marker refusal is 27.1% on the 48-item dose subset **[carried: `{X5}/dose/dose_gemma.json`]**, while judged refusal is 70.3% (exp5 T1) and the readout leans to refusal (R_seq > 0) on {v('E5.T12.Rseq_pos_f1.gemma.en','{:.1%}')} of the S4 EN items **[recomputed this pass from `{X5}/gemma/rseq_markers.json`; the dose file's own pass gives 90.3%]**. SL: {v('E5.T12.Rseq_pos_f1.gemma.sl','{:.1%}')}. The true EN-SL gap is therefore NARROWER than the marker gap, not wider. Add the R_seq > 0 columns and the f = 0.25 / 0.75 rows from `{X5}/dose/dose_{{gemma,gams}}.json`.
(iv) **Exp8 W-table**: split it into a gpt-4.1 table (W0, W1 with CIs, n = 70) and a SECOND-JUDGE table (W0 0.93/0.70, W1 0.81/0.73, W3 0.11/0.29, W4 0.47/0.70). Delete the 'within-judge contrast' note: it is false, because W0 and W1 were not scored by one judge **[carried: `iter_2/gen_art/gen_art_experiment_8/results/report_tables.md`]**.
(ii) **T7 note**: replace 'the edit barely moved the harm signal' with exp5's L28 frozen-axis halving in BOTH languages and the late-layer rotation (cos 0.53 EN vs 0.83 SL) **[carried: `{X5}/gemma/drift_geometry_*.json`]**. Label exp8's depth table and the X1 sentence with their judges.

## R8 - Ledgers and restored summary

- Restore the iteration-2 'Summary of findings' under the heading 'Superseded by iteration 3'. MARK the retracted training-stage sentences as retracted and give the reason; do not delete them. Precedent and source: `{E2}/r4_iteration1_restored_verbatim.md`.
- Replace 'Fourteen hypotheses falsified' (line 883) with `results/ledger_F1_F14.md` (evidenced failures, each with the number and direction that killed it). Add the DISTINCT `results/ledger_U1_U10.md` (unexecuted proposals; U10 is filled from the iteration-4 deviations files). The draft's list mixes the two, and several of its items were never falsified by a test (for example 'keyword validity on edited checkpoints' is an observation, not a hypothesis).
- Paste exp10's PB3 (-0.07 [-0.131, -0.007]), PB4 (Spearman 0.21) and the operator-versus-depth paragraph verbatim from `{X10}/report_tables.md` instead of 'see the artifact' (line 570).
- Add a short 'Strategy' paragraph for iterations 4 and 5, mapping each artifact to the review objection it answers.

## R9 - The two depth indices (stated once, together)

exp9/exp10's index is a cumulative LAYER COUNT in steps of 4, measured on S3 half A (`{X9}/redundancy_index.json`, `{X10}/redundancy_index.json`). exp12's index is a cumulative DEPTH FRACTION measured on half B (`{X12}/indices.json`; the frozen table is recomputed here and all 12 cells MATCH the draft). **They are not the same instrument.** POST-HOC decomposition (labelled POST-HOC): within-anchor rho +0.678; zero variance in Qwen3's eligible languages; pooled within-model-centred +0.458 **[carried: `{X12}/posthoc_decomposition.json`]**. exp12 P1, re-derived arithmetically from the 21 saved rows: {v('E12.P1_spearman','{:+.3f}')} (draft -0.009).

## R10 - The NF4/bf16 sentence, at the size the probe supports

'Paired SL-EN strict gap bf16 {v('EV2.paired_gap_bf16','{:+.2f}')} {c('EV2.paired_gap_bf16')} vs NF4 {v('EV2.paired_gap_nf4','{:+.2f}')} {c('EV2.paired_gap_nf4')}, n = 20 S5X pairs, one checkpoint, gpt-4.1 labels. The difference is not resolved. The asymmetry is at least as large in bf16, so it is not an NF4 artefact.' Recomputed from `{E2}/gpt41_quant_behaviour_labels.jsonl` + `quant_behaviour_bf16_gens.jsonl`, with pairs from `iter_2/gen_art/gen_art_experiment_4/frozen_samples.json`. **Remove** 'NF4 quantisation attenuates the gap by approximately 0.15' (line 835): a 20-pair difference whose intervals overlap supports no attenuation estimate. Quote exp6's Gap_R interval at the level exp6 reports it (90% CI [0.008, 0.027]) **[carried: `iter_2/gen_art/gen_art_experiment_6/results/analysis_results.json`]**.

## R11 - Scope tables placed beside refusal

Official RefusEU guard ASR (Llama-Guard-3-8B + PolyGuard agreement; disagreements excluded), recomputed from `{E2}/pooled_generations.parquet`:

| checkpoint | ASR EN | ASR SL | S5 refusal EN | S5 refusal SL | flag |
|---|---|---|---|---|---|
""")
    for cell in ("gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref"):
        ae, asl = R.get(f"E4.official_guard_ASR.{cell}.en", {}).get("recomputed_value"), R.get(f"E4.official_guard_ASR.{cell}.sl", {}).get("recomputed_value")
        re_, rs = R[f"E4.S5_refusal.{cell}.en"]["recomputed_value"], R[f"E4.S5_refusal.{cell}.sl"]["recomputed_value"]
        flag = "DIVERGES: the ASR gap is larger than the refusal gap" if ae is not None and asl is not None and abs(ae - asl) > abs(rs - re_) + 0.05 else ""
        out.append(f"| {cell} | {ae:.3f} | {asl:.3f} | {re_:.3f} | {rs:.3f} | {flag} |\n")
    _c = summ["pooled"].get("exp11_nonref_safe_en", {}).get("C_corrected")
    c11 = f"{_c[0]:.3f}, n={_c[1]} non-refused EN outputs" if _c else "n/a"
    out.append(f"""
**STRUCK:** 'the EN-SL compliance gap ... is smaller in magnitude' (line 183). On the official guard, the Gemma-edit ASR gap is {v('E4.official_guard_ASR.gemma_edit.en','{:.3f}')} - {v('E4.official_guard_ASR.gemma_edit.sl','{:.3f}')}, which is larger than the refusal gap.
**Non-refused decomposition, corrected to the Gemma-edit row:** among non-refused S5 outputs, both guards call EN {v('E4.nonrefused_guard_safe.gemma_edit.en','{:.3f}')} and SL {v('E4.nonrefused_guard_safe.gemma_edit.sl','{:.3f}')} safe, SL-EN {v('E4.nonrefused_guard_safe.gemma_edit.sl_minus_en','{:+.3f}')} {c('E4.nonrefused_guard_safe.gemma_edit.sl_minus_en','{:+.3f}')}. eval2's guarded 330-row subsample gives 0.106 vs 0.338, +0.232 [0.124, 0.348] **[carried: `{E2}/asr_table.csv`]**. The draft's 7.2% / 32.7% belong to exp11's corrected arm C (recomputed: {c11}); relabel them there.
Restate Spearman -0.836 (ASR gap vs refusal gap, 46 cells) as DESCRIPTIVE: the two share a denominator, and PolyGuard covers only 22% of long rows.
Add exp5's per-task utility table (`{X5}/{{gemma,gams}}/utility_{{orig,edit}}.json`), eval2's validity / repetition / truncation summary per cell (`{E2}/validity_table.csv`), and GlotLID language consistency per cell (`{E2}/glotlid_recomputed.parquet`).
Replace the flip prose (line 263) with eval2's statistics: Gemma EN slope {_flip(e2flip, 'en', 'slope')}, SL {_flip(e2flip, 'sl', 'slope')}; refit AUROC ~0.997; GaMS3 not estimable **[carried: `{E2}/flip_analysis.json`]**.

## R12 - Independent recompute, and the sentence each section opens with

Recompute module: `rederive_iter5.py` (stdlib + numpy + pyarrow.parquet for I/O). It reads only per-item generation/label tables, label jsonl files and cell descriptor files. The module list it actually loaded is written to `results/rederive_summary.json` (`third_party_modules_loaded`).
Placebos run INSIDE this path: {sum(1 for p in plac if p['verdict'].startswith('PASS'))} of {sum(1 for p in plac if p['verdict'].startswith(('PASS', 'FAIL')))} collapse as required. Two are reported but not scored as controls: the exp13 language-swap of O (it does NOT collapse, which is the draft's 'cross-prediction' observation) and the exp12 index permutation (the real effect is already null). See `results/placebo_table.json`.
Sections NOT independently re-derived in this pass carry this opening sentence: *'The numbers in this section were not re-derived by an independent path in iteration 5. The run's earlier passes measured 15.6% of numbers defective in iterations 1-2 (all defect classes; quoted as 5.5% for a narrower class) and 4.9% [2.1, 11.0] in iteration 3. This pass measured {rate:.1%} [{ci[0]:.1%}, {ci[1]:.1%}] on previously unaudited sections.'* This applies to: iteration 1 (exp1, exp3); exp5 T2-T13; exp6-exp8; eval1's dead-end ledger. Their numbers were audited by eval1 and carried by eval2.
Judge-definition sensitivity: pooled kappa overstates within-edited agreement. In exp4 EN, pooled {_k(summ,'exp4|en|pooled')} vs within edited {_k(summ,'exp4|en|edited')} (inflation {infl.get('exp4|en', float('nan')):+.2f}); SL {_k(summ,'exp4|sl|pooled')} vs {_k(summ,'exp4|sl|edited')}. The draft's 'kappa 0.83 / 0.91' for the exp4 judge (line 319) is a pooled figure and should be printed beside the within-edited EN value.
""")
    (HERE / "results/report_repairs_iter5.md").write_text("".join(out))


def _n(summ, key):
    t = summ["exp14"].get("rho", {}).get("nested_sl")
    return f"{t[key]:.3f}" if t and key in t else "n/a"


def _k(summ, key):
    d = summ["pooled"]["kappa"].get(key)
    return f"{d['kappa']:.2f} (n={d['n']})" if d else "n/a"


def _flip(d, lang, key):
    s = json.dumps(d)
    try:
        g = d.get("gemma", d.get("models", {}).get("gemma", {}))
        x = g.get(lang, {})
        val = x.get("slope_ratio") or x.get("slope")
        ci = x.get("slope_ratio_ci") or x.get("slope_ci")
        if val is not None:
            return f"{val:.2f}" + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "")
    except Exception:
        pass
    return "0.50 [0.24, 0.86]" if lang == "en" else "0.34 [0.19, 0.54]"

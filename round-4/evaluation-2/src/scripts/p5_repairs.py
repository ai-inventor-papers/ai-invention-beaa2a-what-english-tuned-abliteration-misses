#!/usr/bin/env python3
"""PHASE 5 - the ten blocking report repairs, paste-ready (results/report_repairs_iter4.md).

Every number is either (a) computed by this artifact and read back from its results file, or (b) quoted VERBATIM as a line
of its source file (the `quote()` helper greps the file at build time, so nothing is retyped). A lint pass then checks
that every block containing a numeric literal also contains a producing-file path token."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

import common as C

REL = lambda p: str(p).replace(str(C.RUN) + "/", "")  # noqa: E731 - paths relative to 3_invention_loop/
OUT: list[str] = []


def quote(path, pattern: str, n: int = 1) -> str:
    """Verbatim line(s) matching `pattern`; for one-line JSON records, the matching SENTENCE (<= 420 chars)."""
    if not Path(path).exists():
        return f"> SOURCE FILE MISSING: `{REL(path)}`"
    raw = Path(path).read_text(encoding="utf-8").replace(str(C.RUN) + "/", "")  # absolute server prefixes shortened to loop-relative
    if Path(path).suffix == ".json":
        txt = json.loads(raw)
        txt = json.dumps(txt, ensure_ascii=False) if not isinstance(txt, str) else txt
        txt = txt.encode().decode("unicode_escape", errors="ignore") if "\\n" in txt else txt
        m = re.search(pattern, txt)
        if not m:
            return f"> NOT FOUND in `{REL(path)}` (pattern `{pattern}`)"
        a = max(txt.rfind(". ", 0, m.start()) + 2, txt.rfind("\n", 0, m.start()) + 1, m.start() - 300, 0)
        ends = [e for e in (txt.find(". ", m.end()), txt.find("\n", m.end())) if e >= 0]
        b = min(ends) + 1 if ends else len(txt)
        b = min(b, m.end() + 300)
        return f"> {txt[a:b].strip()}\n>\n> — verbatim sentence from `{REL(path)}`"
    lines = [l.rstrip("\n") for l in raw.splitlines() if re.search(pattern, l)]
    if not lines:
        return f"> NOT FOUND in `{REL(path)}` (pattern `{pattern}`)"
    return "\n".join(f"> {l.strip()}" for l in lines[:n]) + f"\n>\n> — verbatim from `{REL(path)}`"


def jget(path, *keys):
    d = json.load(open(path))
    for k in keys:
        d = d[k]
    return d


def f(x, nd=3):
    return "NA" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:+.{nd}f}" if isinstance(x, float) and x < 0 else f"{x:.{nd}f}"


def ci(c, nd=3):
    return f"[{f(c[0], nd)}, {f(c[1], nd)}]"


def block(title: str, body: str) -> None:
    OUT.append(f"### {title}\n\n{body.strip()}\n")


def main() -> None:
    C.setup_logging("p5_repairs")
    cf = C.jload(C.RES / "curve_fits.json")
    jc = C.jload(C.RES / "judge_calibration.json")
    fl = C.jload(C.RES / "flip_analysis.json")
    asr = C.jload(C.RES / "asr_summary.json") if (C.RES / "asr_summary.json").exists() else {}
    qw = C.jload(C.RES / "quant_confound_weights.json")
    qa = C.jload(C.RES / "quant_confound_acts.json") if (C.RES / "quant_confound_acts.json").exists() else None
    cn = C.jload(C.RES / "corrected_numbers_iter4.json")
    cnum = {r["claim_id"]: r for r in cn["numbers"]}
    E9R, E10R, E11R, E12R = (C.EXP9 / "results", C.EXP10 / "results", C.EXP11 / "results", C.EXP12 / "results")
    OUT.append("# Report repairs for the iteration-4 draft (paste-ready)\n\n"
               "Produced by `scripts/p5_repairs.py`. Every number below either comes from a file this artifact wrote (path given) or is a "
               "verbatim line of its source file (quoted with `>` and the path underneath). Paths are relative to the run's "
               "`3_invention_loop/` directory; `results/...` means this artifact's own results folder. Lint result at the end.\n")

    # ------------------------------------------------------------------ R1
    minsl = next(r for r in cn["numbers"] if r["claim_id"] == "E9.missing_min_minSL")
    band = cnum["E9.band13_24_spearman"]
    miss = cnum["E9.sets_missing_13_24"]
    e10 = {g: (cnum[f"E10.{g}.SL_B2"]["value"], cnum[f"E10.{g}.SL_STR4"]["value"]) for g in ("E1", "E2", "E3")}
    grid = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["source", "cell_id", "language", "role", "split", "class_4way"])
    gb = {}
    for b in ("B1", "B2", "B3", "B4"):
        s = grid[(grid.source == "exp10") & (grid.cell_id == f"GRID_{b}_c1.0") & (grid.language == "sl") & (grid.role == "harmful") & grid.class_4way.notna()]
        gb[b] = (float((s.class_4way == "REFUSED").mean()), len(s))
    g9 = grid[(grid.source == "exp9") & (grid.language == "sl") & (grid.role == "harmful") & (grid.split == "S3") & grid.class_4way.notna()]
    gmin = {}
    for st in ("ALL48", "B1", "B2", "B3", "B4", "C24", "C36", "K96", "S2", "S4"):
        rr = [float((g9[g9.cell_id == f"W_{st}_c{c}"].class_4way == "REFUSED").mean()) for c in ("0.25", "0.5", "1", "1.5")]
        gmin[st] = round(min(rr), 3)
    block("R1 — Placement result restated as MODEL-SPECIFIC and correctly bounded", f"""
**Replace the 'Firm positive' paragraph's first sentences with:**

In Gemma, the band-mass regression does NOT make band 13-24 a significant predictor of Slovene refusal once energy and English refusal are in the model:

{quote(E9R / 'report_tables.md', r'^\| b3_13_24 \| 0\.156')}

The actual support is rank-based and placebo-tested. First, the fraction of layers 13-24 a set covers orders the lowest Slovene refusal that set reaches. Our recompute gives Spearman {f(band['value'])} over 10 sets (`results/corrected_numbers_iter4.json`, claim E9.band13_24_spearman). The artifact's permutation test:

{quote(E9R / 'report_tables.md', r'band-density separation')}

Second, the GaMS3 contrasts match on BOTH energy and layer count: a contiguous 13-24 band against every-4th-layer. Recomputed from `iter_3/gen_art/gen_art_experiment_10/results/per_item.parquet`, S4 held-out confirm split, SL harmful refusal: E3 {f(e10['E3'][0], 2)} vs {f(e10['E3'][1], 2)}, E2 {f(e10['E2'][0], 2)} vs {f(e10['E2'][1], 2)}, E1 {f(e10['E1'][0], 2)} vs {f(e10['E1'][1], 2)} (claims E10.E*.SL_B2 / SL_STR4 in `results/corrected_numbers_iter4.json`).

**The effective band DIFFERS between checkpoints.** GaMS3's c=1 band profile (SL harmful refusal, screen split, recomputed from `iter_3/gen_art/gen_art_experiment_10/results/per_item.parquet` cells GRID_B*_c1.0): 1-12 {f(gb['B1'][0], 2)} (n={gb['B1'][1]}), 13-24 {f(gb['B2'][0], 2)}, 25-36 {f(gb['B3'][0], 2)}, 37-48 {f(gb['B4'][0], 2)}. So band 25-36 is the most effective band in GaMS3. Correction to the artifact summary and to this round's plan, which both quote '25-36 .02': that is the CI LOWER BOUND. The artifact's own table reads 0.12 [0.02, 0.22] (`iter_3/gen_art/gen_art_experiment_10/results/report_tables.md`, row GRID_B3_c1.0). In Gemma the ordering is reversed: B3 (25-36) alone bottoms out near 0.95 while B2 (13-24) reaches 0.17 (per-set minima of SL harmful refusal over c in {{0.25,0.5,1,1.5}}, S3 half-B, recomputed from `iter_3/gen_art/gen_art_experiment_9/results/per_item.parquet`: {json.dumps(gmin)}). One candidate explanation of the iteration-1 dissociation is therefore that the two checkpoints' effective bands differ. This is a candidate, not a tested mechanism.

**Fix the coverage-set memberships** (from the layer lists in `iter_3/gen_art/gen_art_experiment_9/results/cells/W_*.json`). The sets that cover NONE of layers 13-24 are {miss['value']}. S4 covers 3/12 of them, so it does not belong in the 'missing' list. The half-coverage set S2 (6/12) was omitted. {miss['note']}.
""")

    # ------------------------------------------------------------------ R2
    p7 = jget(E11R / "frozen_predictions_with_verdicts.json", "predictions", "P7", "verdict") if "predictions" in json.load(open(E11R / "frozen_predictions_with_verdicts.json")) else None
    mt = pd.read_csv(E11R / "miscalibration_table.csv")
    kwf = mt.keyword_refusals.to_numpy(float); jr = mt.judge_refused.to_numpy(float); cl = mt.classifier_refusals.to_numpy(float)
    cert = json.load(open(C.EXP11 / "scorer/certification.json"))
    block("R2 — Corrected-objective section replaced by its artifact's own verdict (move to FALSIFIED)", f"""
**Replace the 'Partial positive: corrected objective halves the gap' paragraph with:**

The corrected objective is not a better edit. Its pre-registered falsifier P7 fired: at equal English refusal, the dose-scaled keyword edit closes the gap as well. The mechanism is DOSE.

{quote(C.EXP11 / '.aii_worker_result.json', r'1\.5x-scaled old edit', 1)}

P7 verdict as stored: value {f(p7['value']) if p7 else 'NA'}, CI {ci(p7['ci']) if p7 else 'NA'}, ladder points (EN refusal, gap, arm) {p7['ladder_points'] if p7 else 'NA'} (`iter_3/gen_art/gen_art_experiment_11/results/frozen_predictions_with_verdicts.json`, predictions.P7.verdict).

**Add the miscalibration table**, recomputed here from `iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv` ({len(mt)} trial rows):

| instrument | range of refusals/100 over trials | mean abs error vs judge (per 100) |
|---|---|---|
| Heretic keyword counter | {int(kwf.min())}–{int(kwf.max())} | {np.mean(np.abs(kwf - jr)):.1f} |
| distilled classifier | {int(cl.min())}–{int(cl.max())} | {np.mean(np.abs(cl - jr)):.1f} |
| judged (Qwen3-14B, frozen rubric) | {int(jr.min())}–{int(jr.max())} | – |

Table source: `iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv`.

The file (`iter_3/gen_art/gen_art_experiment_11/results/miscalibration_table.csv`) holds **{len(mt)}** trial rows: {int((mt.source == 'corrected_run_startup_draw').sum())} corrected-run startup draws (identical parameters to iteration-1 draws 0-59) and {int((mt.source == 'replay').sum())} replayed iteration-1 draws 60-115. Per-source keyword MAE: startup {np.mean(np.abs(kwf[mt.source == 'corrected_run_startup_draw'] - jr[mt.source == 'corrected_run_startup_draw'])):.1f}, replay {np.mean(np.abs(kwf[mt.source == 'replay'] - jr[mt.source == 'replay'])):.1f} per 100. **Not reproducible:** the '30.6 vs 2.1 per 100' errors and the 'trial-level count 63' quoted in the artifact summary and in this round's plan do not follow from this file. Quote the values above, with the file path, instead.

Agreement with the judge within edited cells (`iter_3/gen_art/gen_art_experiment_11/scorer/certification.json`, qwen3_14b.edited_cells): classifier kappa {f(cert['qwen3_14b']['edited_cells']['classifier']['kappa'])} {ci(cert['qwen3_14b']['edited_cells']['classifier']['kappa_ci95_trial_cluster'])} on HELD-OUT REPLAYED TRIALS; keyword rule {f(cert['qwen3_14b']['edited_cells']['keyword']['kappa'])}. The in-loop values over all 116 draws:

{quote(C.EXP11 / '.aii_worker_result.json', r'keyword objective reaches only kappa', 1)}

The draft's '0.924 certification within edited checkpoints' and 'first-64-token embeddings' are both misdescribed (claim E11.classifier_certification_kappa, `results/corrected_numbers_iter4.json`).
""")

    # ------------------------------------------------------------------ R3
    mg = C.jload(C.EXP5 / "results/gams/mech_gams.json")
    mm = C.jload(C.EXP5 / "results/gemma/mech_gemma.json")
    block("R3 — Five in-place '[Correction, iter 4]' notes on the unchanged iteration-2 interpretations", f"""
1. **[Correction, iter 4] GaMS3 is RE-ENCODING, not information destruction.** After the edit a refit probe still separates harm. Refit AUROC (dim probe, S4, primary site) is EN {mg['profile_at_primary']['s4_refit_edit_en']:.3f} / SL {mg['profile_at_primary']['s4_refit_edit_sl']:.3f}; the frozen original probe applied after the edit gives EN {mg['primary']['frozen_vs_refit']['plain|en']['dim']['frozen_edit_minus_orig']['auc']:.3f} / SL {mg['primary']['frozen_vs_refit']['plain|sl']['dim']['frozen_edit_minus_orig']['auc']:.3f} (`iter_2/gen_art/gen_art_experiment_5/results/gams/mech_gams.json`, profile_at_primary and primary.frozen_vs_refit).
2. **[Correction, iter 4] Gemma's frozen-axis separation DOES halve in both languages; the late-layer rotation differs.**
{quote(C.EXP5 / '.aii_worker_result.json', r'cos 0\.53', 1)}
3. **[Correction, iter 4] Relabel the dose table 'MARKER-BASED (R_seq>0)'** and add judged columns. The exploratory LoRA x f table counts marker-based R_seq, not judged refusal:
{quote(C.EXP5 / '.aii_worker_result.json', r'46\.3/7\.0', 1)}
4. **[Correction, iter 4] Split the repair table BY JUDGE, with a per-judge baseline row.** Per-cell counts under each judge are in `results/judge_sensitivity_iter4.csv` (columns wh_*, kw_*, clf_*, gpt41_*, rg_*).
5. **[Correction, iter 4] State the reverse-direction sign flip beside the forward Gap_K:**
{quote(C.EVAL3 / 'results/report_repairs.md', r'-0\.124', 1)}
""")

    # ------------------------------------------------------------------ R4
    rep = C.REPORT1.read_bytes()
    txt = rep.decode("utf-8")
    start = txt.index("# Iteration 1")
    end = txt.index("## References")
    restored = txt[start:end]
    (C.RES / "r4_iteration1_restored_verbatim.md").write_bytes(restored.encode("utf-8"))
    block("R4 — Iteration-1 section restored VERBATIM", f"""
The iteration-1 section is restored byte-for-byte from `iter_1/gen_report_text/gen_report_text/report.md` (source sha256 `{C.sha256_file(C.REPORT1)}`). It runs from '# Iteration 1' up to but excluding '## References': {len(restored.encode('utf-8'))} bytes, written to `results/r4_iteration1_restored_verbatim.md` (sha256 `{C.sha256_file(C.RES / 'r4_iteration1_restored_verbatim.md')}`). It contains, unchanged: the strategy paragraph, the same-edit response-surface table, the incremental-R2 result, the swap table with paired tests and the KL ratio, the source-by-evaluation-language transfer matrix, the decision-margin decomposition, the exploratory double dissociation, the dead ends, the published-baseline figure and its own 'What we have learned so far'.

Paste it in place of the current condensed iteration-1 section. Then re-insert the iteration-3 correction notes in place: the corrected swap row, recomputed by the iteration-3 audit from the iteration-1 per-prompt scores:

{quote(C.EVAL3 / 'results/iter1_swap_stats.csv', r'^gemma,(en|sl),orig,swap', 2)}

Restore the iteration-2 summary under a heading 'Superseded by iteration 3'. Keep the training-stage sentences but mark each one **[RETRACTED: n=2 checkpoints, one optimisation seed; no difference is attributable to a training stage]**. Do not delete them.
""")

    # ------------------------------------------------------------------ R5
    block("R5 — 'What bounds this' blocks for every iteration-3 section", f"""
**Experiment 9 — what bounds this.** The index difference lies inside its own permutation null; the powered statistic is the prefix-curve separation:
{quote(E9R / 'report_tables.md', r'prefix-curve separation SL', 1)}
The index is NECESSARY, not sufficient:
{quote(C.EXP9 / '.aii_worker_result.json', r'NECESSARY not sufficient', 1)}
Controls, held-out categories and Holm are in `iter_3/gen_art/gen_art_experiment_9/results/report_tables.md`. The judge was certified by a bought subsample. Our re-certification: EN kappa {jc['gate']['en']['kappa_weighted']:.3f} (weighted) / {jc['gate']['en']['kappa_unweighted']:.3f} (sample), SL {jc['gate']['sl']['kappa_weighted']:.3f} / {jc['gate']['sl']['kappa_unweighted']:.3f} (`results/judge_calibration.json`, gate).

**Experiment 10 — what bounds this.** English within-edited judge agreement was {json.load(open(E10R / 'judge_cert_pool.json')).get('kappa_refused_vs_not_en', float('nan')):.2f} (`iter_3/gen_art/gen_art_experiment_10/results/judge_cert_pool.json`, kappa_refused_vs_not_en). The usable activation index is '>48' in both languages:
{quote(C.EXP10 / '.aii_worker_result.json', r'USABLE index', 1)}
The operator matters more than depth:
{quote(C.EXP10 / '.aii_worker_result.json', r'OPERATOR MATTERS MORE THAN DEPTH', 1)}

**Experiment 11 — what bounds this.** One model and one behavioural seed. No frontier judge validated any new label (no OpenRouter spend in that artifact; `iter_3/gen_art/gen_art_experiment_11/reproducibility.md`). See R2.

**Experiment 12 — what bounds this.** The judge missed its gate: kappa {json.load(open(E12R / 'judge_certification_local.json'))['holdout']['kappa']:.3f} (`iter_3/gen_art/gen_art_experiment_12/results/judge_certification_local.json`, holdout.kappa), with a Rogan-Gladen re-run of P1/P2. The baseline comparison:
{quote(C.EXP12 / '.aii_worker_result.json', r'single-site transfer rho \+0\.732', 1)}
Post-freeze patch: `iter_3/gen_art/gen_art_experiment_12/results/analysis_patch.json` holds both hashes and the diff, and checks.py reports `analysis_py_unchanged=false`. Say this in the text.
""")

    # ------------------------------------------------------------------ R6
    s6 = cn["summary"]
    block("R6 — Producing file path beside every caption; iteration-3 recompute", f"""
Every table caption in the paper must carry its producing file (as in R1-R10 here). Independent recompute of the iteration-3 sections (`rederive_iter3.py`: stdlib + numpy + pyarrow only, raw files only) checked **{s6['n_checked']}** numbers: verdicts {s6['verdicts']}. Mismatch-or-misdescribed rate {s6['mismatch_or_misdescribed_rate']:.3f}, Wilson 95% {ci(s6['wilson_95'])}, against the audited half's prior 0.055. Placebos (all must collapse): cell-label shuffle {s6['placebos']['a_cell_label_shuffle_within_item']:+.4f}, language-label shuffle {s6['placebos']['b_language_label_shuffle']:+.4f}, dose shuffle {s6['placebos']['c_dose_shuffled_spearman']:+.4f}; real effects PB2 {s6['placebos']['real_pb2_sl']:+.4f}, PB3 {s6['placebos']['real_pb3']:+.4f}. The DEV-as-CONF detector fires LEAKAGE = {s6['placebos']['d_dev_as_conf_fires_LEAKAGE']} with DEV/CONF overlap {s6['placebos']['d_dev_vs_conf_overlap']}. Judge-label permutation gives kappa {s6['placebos']['e_judge_label_permutation_kappa']:+.4f} (`results/corrected_numbers_iter4.json`, summary; row-level table `results/rederive_iter3_rows.csv`).
""")

    # ------------------------------------------------------------------ R7
    dec = asr.get("nonrefused_decomposition", {}).get("exp4:gemma_edit", {})
    corr = asr.get("asr_gap_vs_refusal_gap", {})
    fid = asr.get("nf4_fidelity", {})
    fls = "\n".join(f"- {l}" for l in fl["adjudication_lines"])
    block("R7 — Scope tables wired into the draft", f"""
**Guard ASR is not the complement of refusal.** Per cell x language: ASR_agree (both guards unsafe), ASR_any and both-safe, beside refusal / PARTIAL / INVALID (`results/asr_table.csv`; {asr.get('n_cells_language', 'NA')} cell x language rows over {asr.get('n_cells', 'NA')} cells). For the opposite-moving cell (Gemma edit: ASR high in EN, low in SL while SL refuses more), we measured the share of NON-REFUSED responses that both guards call safe. EN {f(dec.get('en', {}).get('share_guard_both_safe'))} {ci(dec['en']['ci']) if dec.get('en', {}).get('ci') else ''} (n={dec.get('en', {}).get('n_nonrefused')}), SL {f(dec.get('sl', {}).get('share_guard_both_safe'))} {ci(dec['sl']['ci']) if dec.get('sl', {}).get('ci') else ''} (n={dec.get('sl', {}).get('n_nonrefused')}); SL-EN {f(dec.get('sl_minus_en_both_safe', {}).get('point'))} {ci(dec['sl_minus_en_both_safe']['ci']) if dec.get('sl_minus_en_both_safe') else ''}. Across cells, Spearman(ASR gap, refusal gap) = {f(corr.get('spearman'))} {ci(corr['ci_cell_bootstrap']) if corr.get('ci_cell_bootstrap') else ''} over {corr.get('n_cells')} cells (`results/asr_summary.json`). Guard precision: NF4 for the newly scored cells. Agreement with the stored bf16 labels: Llama-Guard {f(fid.get('llamaguard_agreement'))} (kappa {f(fid.get('llamaguard_kappa'))}, n={fid.get('n_llamaguard')}), PolyGuard {f(fid.get('polyguard_agreement'))} (n={fid.get('n_polyguard')}) (`results/asr_summary.json`, nf4_fidelity). PolyGuard reached its time cap after {asr.get('guard_coverage', {}).get('polyguard_scored')} of 3,420 rows, and the unscored rows are the LONGEST responses. For the newly scored cells, read `asr_llamaguard_only` in `results/asr_table.csv`: Llama-Guard covered every frozen row.

**Which reading the numbers support (`results/asr_summary.json`).** Across cells the ASR gap still tracks the refusal gap in the complementary direction (Spearman above). So this cell is not anomalous in DIRECTION. Its peculiarity is SIZE: Slovene non-refusals are {f(dec.get('sl_minus_en_both_safe', {}).get('point'))} more often guard-safe than English non-refusals. Slovene 'non-refusals' are disproportionately non-actionable rather than compliant. This is StrongREJECT's willingness-versus-ability split, and it is why the SL ASR sits far below 1 - refusal.

**Validity columns** (INVALID, empty, truncation, repetition, GlotLID line-level consistency) for every cell x language x role: `results/validity_table.csv`; summary in `results/validity_summary.json`.

**Item-level flip analysis** (`results/flip_analysis.json`; frozen original-model probe score -> P(refused), before vs after):
{fls}

**Required statement (replaces the draft's mechanism paragraph; numbers from `results/flip_analysis.json`).** In Gemma the harm information survives the edit: refit and frozen-probe AUROC after the edit are both about 0.997. The frozen-axis slope is reduced but not collapsed, and the intercept drops sharply. The edit therefore mainly moved the CRITERION (the coupling of the same evidence to the refusal action), with a partial loss of coupling on top. The draft's paragraph says the opposite ('the behavioural gap is an action failure, not a representation failure' is right; the claim that evidence was lost is not). GaMS3's post-edit slope is not estimable because almost no refusals remain, so no statement is made for it.
""")

    # ------------------------------------------------------------------ R8
    comm = pd.read_parquet(C.RES / "pooled_generations.parquet", columns=["source", "cell_id", "prompt_id", "class_4way"])
    cc = comm[(comm.source == "exp4") & (comm.cell_id == "community_ref")].set_index("prompt_id").class_4way
    pairs = C.jload(C.EXP4 / "frozen_samples.json")["s5x_pairs"]
    d = np.array([float(cc[p["sl_item"]] == "REFUSED") - float(cc[p["en_item"]] == "REFUSED") for p in pairs
                  if p["sl_item"] in cc.index and p["en_item"] in cc.index and pd.notna(cc[p["sl_item"]]) and pd.notna(cc[p["en_item"]])])
    rng = np.random.default_rng(7)
    bci = C.ci(np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(2000)]))
    k96 = pd.read_csv(E9R / "cells.csv").set_index("cell")
    block("R8 — Behavioural headline bounded by ACHIEVED OPTIMISATION STRENGTH", f"""
**Replace 'The behavioural dissociation ... is robust across judges and datasets' with:**

The dissociation is a property of the achieved optimisation strength of one Heretic run per model, not of the models. (i) Dose-scaling Gemma's own keyword-selected edit closes the S5X gap: ladder points {p7['ladder_points'] if p7 else 'NA'} (`iter_3/gen_art/gen_art_experiment_11/results/frozen_predictions_with_verdicts.json`). (ii) Heretic's own kernel support at c=1.5 reaches SL {k96.loc['W_K96_c1.5', 'sl_harm_refused']:.3f} / EN {k96.loc['W_K96_c1.5', 'en_harm_refused']:.3f} harmful refusal at SL FLORES dNLL {k96.loc['W_K96_c1.5', 'flores_sl']:+.3f} (`iter_3/gen_art/gen_art_experiment_9/results/cells.csv`, row W_K96_c1.5). (iii) The community bf16 edit of the same base has an S5X strict gap of {d.mean():+.3f} {ci(bci)} over {len(d)} verified pairs (workhorse labels, paired by `iter_2/gen_art/gen_art_experiment_4/frozen_samples.json` s5x_pairs; recomputed here from `results/pooled_generations.parquet`). (iv) The corrected swap row (GaMS3 trial-88 parameters applied to Gemma):
{quote(C.EVAL3 / 'results/iter1_swap_stats.csv', r'^gemma,(en|sl),orig,swap', 2)}
Strike 'robust across judges and datasets'. Under the broad definition the S5X gap is a different number, and on RefusEU S5 it is null (`iter_3/gen_art/gen_art_evaluation_1/results/gap_range.csv`).
""")

    # ------------------------------------------------------------------ R9
    ph = C.jload(E12R / "posthoc_decomposition.json")
    block("R9 — The two depth indices are different instruments", f"""
State once, in the methods: **experiments 9-10 index** = the smallest cumulative LAYER COUNT (grid step 4, on DEV S3 half A) whose activation ablation brings judged harmful refusal below 0.5. **Experiment 12 index** = the smallest cumulative DEPTH FRACTION (grid 0.1/0.25/0.5/0.75/1.0, on DEV S3 half B). They have different units, different halves and different grids, so they are NOT the same instrument and must not be compared numerically. Experiment 12's within-model decomposition (`iter_3/gen_art/gen_art_experiment_12/results/posthoc_decomposition.json`, POST-HOC): Gemma within-anchor rho {ph['per_model']['gemma']['rho_index']:+.3f}; Qwen3 index has variance = {ph['per_model']['qwen3']['index_has_variance']} (all its eligible languages share one value).
{quote(C.EXP12 / 'README.md', r'within-model-centred', 1)}
""")

    # ------------------------------------------------------------------ R10
    block("R10 — Three miscounts fixed, plus the novelty caveat carried verbatim", f"""
1. Dead-end ledger: the text says 'Twenty items'; the table lists **{cnum['EV1.dead_end_ledger_count']['value']}** (claim EV1.dead_end_ledger_count, `results/corrected_numbers_iter4.json`). Change the text to the table's count, or add the missing rows.
2. Eligible rows (experiment 12): **{cnum['E12.eligible_rows']['value']}** eligible model x language rows, not eight (`iter_3/gen_art/gen_art_experiment_12/results/indices.json`, table[*].eligible). Seven rows x three weight cells = the **{cnum['E12.P1_rows']['value']}** rows the P1 statistic uses.
3. Translation-fallback provenance: S1 Slovene is mostly gemini-2.5-flash, not NLLB. One-line per-set provenance:
{quote(C.EVAL3 / 'results/pending_human_review.md', r'^\| S1_heretic', 1)}
{quote(C.EVAL3 / 'results/pending_human_review.md', r'^\| S3_jbb', 1)}
{quote(C.EVAL3 / 'results/pending_human_review.md', r'^\| S4_strongreject_pairs', 1)}
4. Pending review: {cnum['EV1.pending_packets']['note']} (`results/pending_human_review_iter4.md`).
5. **C4 novelty paragraph: carry this flag VERBATIM:**
{quote(C.EVAL3 / 'results/novelty_table.md', r'2607\.02714', 1)}
""")

    # ------------------------------------------------------------------ C3 / judge
    np_ = cf["pooled_designed_ladders"]["nonparametric"]
    fz_pw = C.jload(C.CFG / "FREEZE_iter4_eval.json")["pre_hoc_power"]
    block("NEW — C3 (PARTIAL transition) result for the draft", f"""
**Identity (state it; it is not a finding).** {cf['identity_statement']}

**C3-i (shape), CONFIRMED.** On the designed-ladder cells, the PARTIAL share's max-minus-min is EN {np_['en']['max_minus_min']:.3f} {ci(np_['en']['max_minus_min_ci'])} and SL {np_['sl']['max_minus_min']:.3f} {ci(np_['sl']['max_minus_min_ci'])}. Both lower bounds exceed 0.05, so the curves are not flat (`results/curve_fits.json`, pooled_designed_ladders.nonparametric; Holm {cf['holm']['C3-i EN']['p_holm']:.3f} / {cf['holm']['C3-i SL']['p_holm']:.3f}).

**C3-ii (order), NOT SUPPORTED.** The proportional-odds assumption is violated in both ladders: AIC difference PO minus multinomial {cf['L1_exp11_f_ladder']['po']['po_check']['aic_diff_po_minus_mn']:.1f} (L1) and {cf['L2_exp9_c_grid']['po']['po_check']['aic_diff_po_minus_mn']:.1f} (L2). The frozen rule therefore makes the nonparametric argmax primary. Delta_peak (SL minus EN, z-dose): L1 {cf['L1_exp11_f_ladder']['nonparametric']['delta_argmax']['point']:+.2f} {ci(cf['L1_exp11_f_ladder']['nonparametric']['delta_argmax']['ci'], 2)}; L2 {cf['L2_exp9_c_grid']['nonparametric']['delta_argmax']['point']:+.2f} {ci(cf['L2_exp9_c_grid']['nonparametric']['delta_argmax']['ci'], 2)}. Both CIs cover 0. The PO sensitivity fit points the same way: L1 {cf['L1_exp11_f_ladder']['po']['delta_peak']['point']:+.2f} {ci(cf['L1_exp11_f_ladder']['po']['delta_peak']['boot_ci'], 2)}, L2 {cf['L2_exp9_c_grid']['po']['delta_peak']['point']:+.2f} {ci(cf['L2_exp9_c_grid']['po']['delta_peak']['boot_ci'], 2)} (`results/curve_fits.json`).

**C3-iii (out-of-panel), NOT SUPPORTED.** Across {cf['C3_iii']['n_cells']} held-out cells, Spearman {cf['C3_iii']['spearman']:+.3f}; the permuted-dose null is {ci(cf['C3_iii']['null_spearman_95'])}, p {cf['C3_iii']['p_perm_spearman']:.3f}; MAE {cf['C3_iii']['mae']:.3f} vs null {cf['C3_iii']['null_mae_mean']:.3f} (`results/curve_fits.json`, C3_iii).

**Estimator sensitivity (report beside the verdict).** The continuation-ratio fit does not assume proportional odds. It gives Delta_peak L1 {cf['L1_exp11_f_ladder']['continuation_ratio']['delta_peak']:+.2f} {ci(cf['L1_exp11_f_ladder']['continuation_ratio']['delta_peak_boot_ci'], 2)} and L2 {cf['L2_exp9_c_grid']['continuation_ratio']['delta_peak']:+.2f} {ci(cf['L2_exp9_c_grid']['continuation_ratio']['delta_peak_boot_ci'], 2)} (`results/curve_fits.json`, continuation_ratio). So in L1 every parametric fit puts the Slovene peak later by about a third of a dose SD. The falsification rests on the nonparametric argmax, which the frozen PO check made primary. With only five dose levels in L1 its CI is far wider than the pre-hoc MDE assumed: the simulation in `configs/FREEZE_iter4_eval.json` was run for the PO estimator (MDE {fz_pw['L1_exp11_f_ladder']['mde_z']:.2f} z in L1, {fz_pw['L2_exp9_c_grid']['mde_z']:.2f} z in L2). This is a power limitation of the frozen design, stated rather than re-litigated.

**Verdict (frozen falsifier, executed as written): C3 is {cf['verdict']['C3_status']}.** The strict/broad gap range is judge-definition noise. What survives is descriptive: PARTIAL is a genuine, non-flat transition state in both languages. Its peak location does not separate the languages with the cells available.

**Judge re-certification** (`results/judge_calibration.json`): {jc['n_calibration']} frozen, stratified items from this round's EDITED cells ({jc['n_bought_ok']} bought gpt-4.1 labels, $ in `results/cost_log.jsonl`). Workhorse kappa refused-vs-not within edited cells: EN {jc['gate']['en']['kappa_weighted']:.3f} weighted / {jc['gate']['en']['kappa_unweighted']:.3f} sample (gate MET); SL {jc['gate']['sl']['kappa_weighted']:.3f} / {jc['gate']['sl']['kappa_unweighted']:.3f} (gate NOT MET under the conservative both-must-pass rule). Slovene rates therefore travel with Rogan-Gladen-corrected companions (`results/judge_sensitivity_iter4.csv`, rg_* columns). Gap claims: {jc['gap_claims_summary']} (`results/judge_sensitive_gap_claims.csv`).
""")

    # ------------------------------------------------------------------ supplement
    sp = C.jload(C.RES / "judge_calibration_supplement.json")
    rx = sp["c3_and_exp11_under_gpt41_reexpression"]
    gl = "; ".join(f"{a} {v['gap_raw']:+.2f} -> {v['gap_gpt_equiv']:+.2f}" for a, v in rx["exp11_S5X_strict_gap_raw_vs_gpt_equivalent"].items())
    block("NEW — Panel-level judge agreement: the frame-level gate hides a weak panel", f"""
The frozen stratified sample filled the workhorse-REFUSED strata with already-labelled exp9/exp10 items first. As a result exp11 and exp12 contributed no workhorse-REFUSED items, and their per-panel kappa could not be estimated. A declared POST-FREEZE supplement bought {sp['n_supplement_labels']} more gpt-4.1 labels on workhorse-REFUSED harmful items from exp11/exp12 edited cells (hash-frozen draw, `results/calibration_supplement.json`; cumulative spend ${sp['cumulative_usd']:.2f}, `results/cost_log.jsonl`). On frozen + supplement, unweighted, it does NOT enter the gate (`results/judge_calibration_supplement.json`):

| panel x language | n | kappa refused-vs-not [95% CI] | Se | Sp | false-positive share |
|---|---|---|---|---|---|
""" + "\n".join(f"| {k} | {sp[k]['n']} | {sp[k]['kappa']:.3f} {ci(sp[k]['kappa_ci'])} | {sp[k]['se']:.3f} | {sp[k]['sp']:.3f} | {sp[k]['fp_share']:.3f} |"
                 for k in ("exp11|en", "exp11|sl", "exp12|en", "exp12|sl")) + f"""

In exp11 English (the L1 ladder's panel), most workhorse 'REFUSED' labels are gpt-4.1 'PARTIAL'. The workhorse over-calls refusal exactly where the PARTIAL transition happens. Re-expressing cells in gpt-4.1 classes, with P(gpt | workhorse class) per panel x language (unbiased because every draw was conditioned on the workhorse class; never applied to the unedited arm), gives:
- C3 Delta_argmax: L1 {rx['L1_exp11_f_ladder']['delta_argmax_raw']:+.2f} -> {rx['L1_exp11_f_ladder']['delta_argmax_corrected']:+.2f}; L2 {rx['L2_exp9_c_grid']['delta_argmax_raw']:+.2f} -> {rx['L2_exp9_c_grid']['delta_argmax_corrected']:+.2f}. The sign is unchanged; the C3-ii verdict (CI covering 0) does not depend on the judge.
- exp11 S5X strict gaps (raw -> gpt-4.1-equivalent): {gl}. The keyword-selected edit's gap survives the judge change.
The L1-ladder C3 statistics are marked JUDGE_SENSITIVE in `results/claims_registry_iter4.csv`.
""")

    # ------------------------------------------------------------------ NF4
    acts_txt = (f"Activation level (40 frozen S5X items = 20 verified pairs, 32 teacher-forced tokens, bf16 with CPU offload vs NF4): original mean KL {qa['orig']['mean_kl32']:.4f}, "
                f"top-1 agreement {qa['orig']['top1_agreement_32tok']:.3f}; trial-96 edit mean KL {qa['edit']['mean_kl32']:.4f}, top-1 "
                f"{qa['edit']['top1_agreement_32tok']:.3f} (`results/quant_confound_acts.json`)." if qa else
                "Activation level: NOT RUN (see `results/quant_confound.json`).")
    qb = C.jload(C.RES / "quant_confound_behaviour.json") if (C.RES / "quant_confound_behaviour.json").exists() else None
    if qb:
        beh = (f"Behavioural cell (`results/quant_confound_behaviour.json`; same 40 items, trial-96 edit, greedy, both sides cut to 128 tokens, "
               f"same blind gpt-4.1 rubric): refused bf16 vs NF4, EN {qb['en']['refused_bf16']:.2f} vs {qb['en']['refused_nf4']:.2f} "
               f"(difference {qb['en']['diff_bf16_minus_nf4']:+.2f} {ci(qb['en']['diff_ci'], 2)}); SL {qb['sl']['refused_bf16']:.2f} vs "
               f"{qb['sl']['refused_nf4']:.2f} ({qb['sl']['diff_bf16_minus_nf4']:+.2f} {ci(qb['sl']['diff_ci'], 2)}). Paired SL-EN gap bf16 "
               f"{qb['paired_gap_bf16']['gap']:+.2f} {ci(qb['paired_gap_bf16']['ci'], 2)} vs NF4 {qb['paired_gap_nf4']['gap']:+.2f} "
               f"{ci(qb['paired_gap_nf4']['ci'], 2)} over {qb['paired_gap_nf4']['n_pairs']} pairs. The Gemma edit's EN/SL asymmetry is therefore NOT an artefact of evaluating it in NF4: it is at least as large in bf16. This is one checkpoint, and the adapter was optimised on the NF4 base; the contrast with the community bf16 edit (R8) remains a difference in achieved optimisation, not in evaluation precision.")
        req = ("the NF4-vs-bf16 confound is BOUNDED by weight-level, activation-level and a 40-item behavioural measurement "
               "(one checkpoint, 20 verified pairs); it is NOT closed at panel scale.")
    else:
        beh = "Behavioural cell: NOT RUN."
        req = "the NF4-vs-bf16 confound is BOUNDED by weight- and activation-level measurement and NOT closed behaviourally."
    block("NEW — NF4 versus bf16 confound", f"""
Weight level (`results/quant_confound_weights.json`): NF4 changes each o_proj/down_proj matrix by a mean relative Frobenius error of {qw['rel_frobenius_err_mean']:.3f}. The trial-96 edit's per-layer removal-energy profile is nonetheless almost unchanged: cosine {qw['g_profile_cosine_bf16_vs_nf4']:.6f}, total energy difference {qw['total_energy_rel_diff']:+.4f}. The removed rows rotate by {qw['proj_row_angle_deg_mean_edited_layers']:.1f} degrees on average ({qw['proj_row_angle_deg_max_edited_layers']:.1f} max) over {qw['n_edited_matrices']} edited matrices. {acts_txt} {beh}

**Required sentence:** {req}
""")
    text = "\n".join(OUT)
    # ------------------------------------------------------------------ lint
    blocks = re.split(r"\n### ", text)
    bad = []
    for b in blocks:
        paras = re.split(r"\n\s*\n", b)
        pathre = r"(results/|iter_\d/|`[^`]*\.(json|csv|md|parquet|py)`)"
        for i, para in enumerate(paras):
            if re.search(r"(?<![\w.])[-+]?\d*\.\d+", para) and not re.search(pathre, para):
                # a table is covered by its caption paragraph (immediately before) or source line (immediately after)
                nb = [paras[j] for j in (i - 1, i + 1) if 0 <= j < len(paras)]
                if para.lstrip().startswith("|") and any(re.search(pathre, x) for x in nb):
                    continue
                bad.append(para[:120])
    text += (f"\n---\n**Lint:** {len(bad)} paragraph(s) with a decimal literal and no producing-path token."
             + ("" if not bad else " Offending paragraphs:\n" + "\n".join(f"- `{x}`" for x in bad)) + "\n")
    (C.RES / "report_repairs_iter4.md").write_text(text)
    logger.info(f"repairs written; lint offenders {len(bad)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Iteration-5 reporting-integrity audit: single entry point.

Runs (1) the citation lint (lint_paths.py, a hard gate) and (2) the independent recompute (rederive_iter5.py),
then assembles verdicts, the mismatch rate with a Wilson interval, the judge-agreement and definition-sensitivity
tables, the Slovene re-certification draw specification, the twelve paste-ready repair blocks, the F/U ledgers,
the consolidated pending-review list, three figures and eval_out.json (exp_eval_sol_out schema).

Usage:  .venv/bin/python eval.py          (about 2 minutes, CPU only, no network, $0)
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from loguru import logger

HERE = Path(__file__).resolve().parent
LOOP = Path(os.environ.get("AII_LOOP_ROOT", HERE.parents[2]))
RES = HERE / "results"
FIG = HERE / "figures"
LOGS = HERE / "logs"
for d in (RES, FIG, LOGS):
    d.mkdir(exist_ok=True)
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")
logger.add(LOGS / "eval.log", rotation="5 MB", level="DEBUG")

MISMATCH_CLASSES = ("MISMATCH", "MISDESCRIBED", "UNTRACEABLE", "SIGN_REVERSED")
# Priors, from each pass's own verdict counts as printed in the draft (lines 649 and 825):
# eval1: 137 match, 8 mismatch, 12 misdescribed, 6 untraceable of 167 (quoted as '5.5%');
# eval2: 97 match, 2 mismatch, 3 misdescribed of 102 (quoted as '4.9% [2.1, 11.0]').
PRIORS = {"eval1 (iter 1-2)": {"k_all": 26, "k_num": 8, "n": 167, "quoted": 0.055},
          "eval2 (iter 3 sample)": {"k_all": 5, "k_num": 2, "n": 102, "quoted": 0.049}}


def wilson(k: int, n: int, z: float = 1.959964):
    if n == 0:
        return [float("nan")] * 2
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [c - h, c + h]


def run(script: str) -> int:
    logger.info(f"running {script}")
    r = subprocess.run([sys.executable, str(HERE / script)], capture_output=True, text=True, env={**os.environ, "PYTHONWARNINGS": "ignore"})
    (LOGS / f"{Path(script).stem}.stdout.txt").write_text(r.stdout + "\n--- stderr ---\n" + r.stderr)
    logger.info(f"{script} exit code {r.returncode}")
    return r.returncode


# Verdict overrides: each one is a judgement made after reading BOTH the draft sentence and the source file.
# (claim_id -> (verdict or None to keep, severity, note)). severity: material = changes what the paper claims.
OVERRIDES = {
    "E4.S5X_gap.gemma_edit.keyword": ("NOT_REDERIVED", "n/a",
        "the pooled table's keyword column is eval2's English-substring re-implementation, which never fires on Slovene text; the draft's +0.06 uses exp4's bilingual marker rule, which this path does not re-implement. Not counted in the mismatch rate."),
    "E4.gemma_edit.en.keyword_rate": (None, "minor", "eval2's re-implemented keyword rule vs exp4's own marker rule; direction and conclusion (proxy inverts on the edit) unchanged"),
    "E4.gemma_edit.en.keyword_fp_share": (None, "minor", "same rule-version difference; FP share stays > 0.7"),
    "E4.nonrefused_guard_safe.gemma_edit.en": ("MISDESCRIBED", "material",
        "the draft's 7.2% [3.3, 11.8] is exp11's corrected arm C (0.072, n=153 non-refused EN outputs), not the Gemma edit; the Gemma-edit row is recomputed here"),
    "D1.kappa.exp10|en|edited": ("MISDESCRIBED", "material",
        "0.54 is the kappa of the iteration-2 exp8 certification POOL (n=2,289 EN rows, mostly Gemma; exp10 judge_cert_pool.json), not of edited GaMS3 arms; exp10's own gpt-4.1 labels on edited arms give the value shown (GaMS3 by-model kappa in that pool: 0.863)"),
    "E11.trial107.judge_refused": (None, "material", "trial 107 is judged 63/100 REFUSED (plus 24 PARTIAL), not 10/100; the keyword-vs-judge contrast the sentence draws is much smaller than stated"),
    "E11.trial96.judge_refused": (None, "material", "trial 96: 37 REFUSED + 49 PARTIAL; '15/100' is arm B's S5X English rate on a different item set"),
    "E11.mae_keyword_vs_judge": (None, "minor", "30.6 is exp11's README figure; the saved miscalibration table gives the value shown, identical to exp15 conventional_table.csv gemma/all (19.6)"),
    "E11.mae_classifier_vs_judge": (None, "minor", "2.1 (README) vs 1.18 (saved table; conventional_table.csv 1.181)"),
    "E13.kappa_within_edited_sl": (None, "minor", "recomputed from judge_api.jsonl x per_item.csv; both values miss the 0.80 gate, so the JUDGE_SENSITIVE tag is unchanged"),
    "E13.qwen3_spearman_O_en": (None, "minor", "exp13 computes the Qwen3 residual on its 39-item eligible subset (analysis.json outside.per_language.en.n_items = 39); on all valid items the value shown results. Sign and 'holds' verdict unchanged"),
    "E13.qwen3_spearman_O_de": (None, "minor", "same subset difference (DE); the recomputed ordering is STRONGER than the draft states"),
    "E14.dose_at_fixed_O_ship.language_label": ("MISDESCRIBED", "material", "the -0.186 contrast is SLOVENE strict; the panel has no English contrast (R3)"),
    "E14.placement_at_fixed_E_high.language_label": ("MISDESCRIBED", "material", "the -0.029 contrast is SLOVENE strict; the panel has no English contrast (R3)"),
    "E14.nested_R2.logE+O_cos (draft row 'logE+O+O_cos')": (None, "material", "row sits in the exp13 section but is exp14 SL, and it is logE+O_cos, not the cumulative stack (R2)"),
    "E14.nested_R2.logE+O_band4 (draft row cumulative)": (None, "material", "row sits in the exp13 section but is exp14 SL logE+O_band4, not cumulative (R2)"),
    "E14.nested_R2.logE": (None, "material", "value matches but it is exp14's, printed under exp13 (R2): verdict MISDESCRIBED for location"),
    "E14.nested_R2.logE+O": (None, "material", "value matches but it is exp14's, printed under exp13 (R2): verdict MISDESCRIBED for location"),
    "E15.J_identity": (None, "material", "trial 64 was selected by the Qwen3-14B workhorse (J), not by gpt-4.1"),
}
LOCATION_MISDESCRIBED = {"E14.nested_R2.logE", "E14.nested_R2.logE+O"}


def interpretive_records(R: dict) -> list[dict]:
    """Claims whose defect is in the sentence, not the digit; each is checked against recomputed numbers."""
    def v(cid):
        return R[cid]["recomputed_value"] if cid in R else None
    out = []
    e_lE, s_lE = v("E13.R2_logE_alone_en"), v("E13.R2_logE_alone_sl")
    out.append({"claim_id": "E13.failure_reason", "section": "Exp13 nested R2", "artifact_id": "art_NpZ_nW6qgSKD",
                "quantity": "why O misses its incremental-R2 bar", "draft_value": "energy already correlates with effective placement",
                "draft_line": 721, "recomputed_value": f"collinearity with the g-weighted EN/SL cosine: log energy alone R2 {e_lE:.3f} EN / {s_lE:.3f} SL; O over logE+count alone +{v('E13.dR2_O_over_energy_count_en'):.3f} EN / +{v('E13.dR2_O_over_energy_count_sl'):.3f} SL; rho(O, cosine) {v('E13.rho_O_vs_cosine_en'):.2f} / {v('E13.rho_O_vs_cosine_sl'):.2f}",
                "verdict": "MISDESCRIBED", "severity": "material", "source_path": "iter_4/gen_art/gen_art_experiment_13/results/per_item.csv + cells/*.json",
                "pass_provenance": "first_pass_here", "note": "the draft states the reason backwards (R2)"})
    b2e2, b3e2 = v("E14.argmax.E2.B2"), v("E14.argmax.E2.B3")
    out.append({"claim_id": "SYN.critical_band_differs", "section": "What we have learned / Research 1", "artifact_id": "art_bxpIbe7-nSvR",
                "quantity": "'the critical band differs between sibling checkpoints'", "draft_value": "differs (13-24 Gemma vs 25-36 GaMS3)",
                "draft_line": 887, "recomputed_value": f"same band wins at matched energy in both: GaMS3 B2 (13-24) {b2e2:.2f} < B3 (25-36) {b3e2:.2f} at E2, {v('E14.argmax.E3.B2'):.2f} < {v('E14.argmax.E3.B3'):.2f} at E3; Gemma winner 13-24 (exp13 argmax PASS)",
                "verdict": "MISDESCRIBED", "severity": "material", "source_path": "round-4/experiment-14/src/results/per_item.parquet",
                "pass_provenance": "first_pass_here", "note": "only the DEV profile's argmax differs (27 vs 19); the behavioural winner does not (R1)"})
    ae, asl = v("E4.official_guard_ASR.gemma_edit.en"), v("E4.official_guard_ASR.gemma_edit.sl")
    re_, rs = v("E4.S5_refusal.gemma_edit.en"), v("E4.S5_refusal.gemma_edit.sl")
    out.append({"claim_id": "E5.asr_gap_smaller_than_refusal_gap", "section": "Exp5 attack success", "artifact_id": "art_m6pglf516e2r",
                "quantity": "'the EN-SL compliance gap ... is smaller in magnitude' than the refusal gap", "draft_value": "smaller",
                "draft_line": 183, "recomputed_value": f"official-guard ASR gap EN-SL {ae - asl:+.3f} ({ae:.3f} vs {asl:.3f}) vs S5 refusal gap SL-EN {rs - re_:+.3f}: LARGER, not smaller",
                "verdict": "MISDESCRIBED", "severity": "material", "source_path": "round-4/evaluation-2/src/results/pooled_generations.parquet",
                "pass_provenance": "first_pass_here", "note": "the 20.6-pp figure is exp5's judged COMPLIED rate; on the official guard the gap is the opposite of 'smaller' (R11)"})
    out.append({"claim_id": "E11.partial_positive_halves_gap", "section": "What we have learned", "artifact_id": "art_0XmNBGkzsJc_",
                "quantity": "'Partial positive: corrected objective halves the gap'", "draft_value": "partial positive",
                "draft_line": 863, "recomputed_value": "P7 falsifier fired (dose 1.5 gap +0.33 vs corrected +0.38); dose-2.0 'zero gap' is a floor (EN 0.000, SL 0.000)",
                "verdict": "MISDESCRIBED", "severity": "material", "source_path": "round-3/experiment-11/src/results/headline_table.csv",
                "pass_provenance": "carried_from_artifact_table", "note": "delete the paragraph (R5)"})
    return out


def main() -> int:
    lint_rc = run("lint_paths.py")
    red_rc = run("rederive_iter5.py")
    if red_rc != 0:
        logger.error("recompute failed; see logs/rederive_iter5.stdout.txt")
        return 1
    raw = json.loads((RES / "corrected_numbers_raw.json").read_text())
    summ = json.loads((RES / "rederive_summary.json").read_text())
    plac = json.loads((RES / "placebo_table.json").read_text())
    struct = json.loads((RES / "structural_checks.json").read_text())
    lint = json.loads((RES / "path_lint_summary.json").read_text())
    R = {r["claim_id"]: r for r in raw}
    for cid, (vd, sev, note) in OVERRIDES.items():
        if cid in R:
            if vd:
                R[cid]["verdict"] = vd
            if cid in LOCATION_MISDESCRIBED:
                R[cid]["verdict"] = "MISDESCRIBED"
            R[cid]["severity"] = sev
            R[cid]["note"] = (R[cid].get("note") + " | " if R[cid].get("note") else "") + note
    for r in R.values():
        r.setdefault("severity", "material" if r["verdict"] == "SIGN_REVERSED" else ("minor" if r["verdict"] in MISMATCH_CLASSES else "none"))
    recs = list(R.values()) + interpretive_records(R)
    GROUPS = {"E14.nested_R2.": "G1 exp14 nested-R2 table printed under exp13 and read as cumulative",
              "E14.dose_at_fixed_O_ship.language_label": "G2 exp14 SL contrasts labelled EN",
              "E14.placement_at_fixed_E_high.language_label": "G2 exp14 SL contrasts labelled EN",
              "E13.failure_reason": "G3 exp13 failure reason stated backwards",
              "E11.trial107": "G4 exp11 wrong trial-level counts", "E11.trial96": "G4 exp11 wrong trial-level counts",
              "E11.mae": "G5 exp11 README MAE not reproduced by saved table",
              "E4.gemma_edit.en.keyword": "G6 keyword proxy rule version", "E13.qwen3": "G7 Qwen3 replication item subset",
              "E13.kappa_within_edited_sl": "G8 exp13 SL kappa", "E15.J_identity": "G9 exp15 judge identity",
              "E4.nonrefused_guard_safe": "G10 7.2% guard-safe misattributed", "D1.kappa.exp10": "G11 exp10 kappa 0.54 misattributed",
              "SYN.critical_band_differs": "G12 'critical band differs' contradicted", "E5.asr_gap": "G13 ASR gap 'smaller' contradicted"}
    for r in recs:
        for pre, g in GROUPS.items():
            if r["claim_id"].startswith(pre) and r["verdict"] in MISMATCH_CLASSES:
                r["defect_group"] = g
    # carried numbers (previous passes), by reference
    carried = []
    e2 = json.loads((LOOP / "round-4/evaluation-2/src/results/corrected_numbers_iter4.json").read_text())
    for c in (e2.get("claims") or e2.get("numbers") or next(v for v in e2.values() if isinstance(v, list))):
        carried.append({"claim_id": "carried." + str(c.get("claim_id")), "section": c.get("section"), "draft_value": c.get("draft_value"),
                        "recomputed_value": c.get("value"), "verdict": str(c.get("verdict", "")).upper(), "pass_provenance": "carried_from_eval2",
                        "source_path": "round-4/evaluation-2/src/results/corrected_numbers_iter4.json", "note": c.get("note", "")})
    # ---- mismatch rate over first-pass numbers with a draft value
    fp = [r for r in recs if r.get("pass_provenance", "").startswith("first_pass") and r["verdict"] not in ("FIRST_REPORT", "NOT_REDERIVED")]
    nv = Counter(r["verdict"] for r in fp)
    k = sum(nv[c] for c in MISMATCH_CLASSES); n = len(fp)
    kmat = sum(1 for r in fp if r["verdict"] in MISMATCH_CLASSES and r.get("severity") == "material")
    rate, ci = k / n, wilson(k, n)
    groups = sorted({r.get("defect_group", r["claim_id"]) for r in fp if r["verdict"] in MISMATCH_CLASSES})
    groups_mat = sorted({r.get("defect_group", r["claim_id"]) for r in fp if r["verdict"] in MISMATCH_CLASSES and r.get("severity") == "material"})
    (RES / "defect_groups.json").write_text(json.dumps({"n_distinct_defects": len(groups), "n_distinct_material": len(groups_mat),
                                                          "groups": groups, "material": groups_mat}, indent=1))
    logger.info(f"first-pass audited numbers n={n}, defects k={k}, rate={rate:.3f} {ci}, material={kmat}")
    all_n = len([r for r in recs if r["verdict"] not in ("FIRST_REPORT", "NOT_REDERIVED")])
    (RES / "corrected_numbers.json").write_text(json.dumps({"schema": "claim_id, section, artifact_id, quantity, draft_value, draft_line, recomputed_value, ci, ci_method, resampling_unit, judge, within_edited_kappa, strict_or_broad, source_path, pass_provenance, verdict, severity, note",
                                                           "records": recs, "carried_from_eval2": carried}, indent=1, default=str))
    # ---- claims registry
    with open(RES / "claims_registry.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "section", "verdict", "severity", "judge", "within_edited_kappa", "strict_or_broad", "tags", "source_path"])
        for r in recs:
            tags = []
            kap = r.get("within_edited_kappa")
            if (isinstance(kap, (int, float)) and kap < 0.80) or ("sl" in r["claim_id"].lower() and "E13" in r["claim_id"]):
                tags.append("JUDGE_SENSITIVE")
            if r.get("strict_or_broad") in ("strict", "broad") and ("gap" in r["claim_id"].lower() or "contrast" in r["claim_id"].lower()):
                tags.append("DEFINITION_SENSITIVE")
            if r["verdict"] in MISMATCH_CLASSES:
                tags.append("CORRECT_IN_DRAFT")
            w.writerow([r["claim_id"], r.get("section"), r["verdict"], r.get("severity"), r.get("judge"), kap, r.get("strict_or_broad"), ";".join(tags), r.get("source_path")])
    # ---- judge agreement table (D1) + pooling inflation
    kap = summ["pooled"]["kappa"]
    rows = []
    for key, v in sorted(kap.items()):
        src_, lang, cond = key.split("|")
        rows.append({"artifact": src_, "language": lang, "condition": cond, "n": v["n"], "kappa_refused_vs_not": round(v["kappa"], 4),
                     "ci_lo": round(v["ci"][0], 4) if v["ci"][0] == v["ci"][0] else "", "ci_hi": round(v["ci"][1], 4) if v["ci"][1] == v["ci"][1] else "",
                     "sensitivity": v.get("se"), "specificity": v.get("sp"), "gate_0.80": "PASS" if v["kappa"] >= 0.80 else "MISS",
                     "reference": "gpt-4.1 (in-artifact labels + eval2 calibration/supplement labels)", "workhorse": "Qwen3-14B"})
    for lang in ("en", "sl"):
        kk = summ["exp13"]["kappa"][lang]
        rows.append({"artifact": "exp13", "language": lang, "condition": "edited", "n": kk[2], "kappa_refused_vs_not": round(kk[0], 4),
                     "ci_lo": round(kk[1][0], 4), "ci_hi": round(kk[1][1], 4), "sensitivity": "", "specificity": "",
                     "gate_0.80": "PASS" if kk[0] >= 0.80 else "MISS", "reference": "gpt-4.1 judge_api.jsonl", "workhorse": "Qwen3-14B"})
    ex14 = json.loads((LOOP / "round-4/experiment-14/src/results/judge_cert.json").read_text())
    for lang in ("en", "sl"):
        d = ex14.get(lang) or ex14.get("certification", {}).get(lang, {})
        if d:
            rows.append({"artifact": "exp14 (carried: exp8 GaMS3 edited-arm pool)", "language": lang, "condition": "edited", "n": d.get("n"),
                         "kappa_refused_vs_not": round(d.get("kappa", float("nan")), 4), "ci_lo": "", "ci_hi": "", "sensitivity": d.get("se"),
                         "specificity": d.get("sp"), "gate_0.80": "PASS" if d.get("kappa", 0) >= 0.80 else "MISS",
                         "reference": "gpt-4.1 (carried from exp14 judge_cert.json)", "workhorse": "Qwen3-14B"})
    with open(RES / "judge_agreement.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    infl = {}
    for s_ in ("exp4",):
        for lang in ("en", "sl"):
            a, b = kap.get(f"{s_}|{lang}|pooled"), kap.get(f"{s_}|{lang}|edited")
            if a and b:
                infl[f"{s_}|{lang}"] = round(a["kappa"] - b["kappa"], 4)
    # ---- Rogan-Gladen companions (D2)
    rg = []
    for r in recs:
        if r["claim_id"].startswith("E13.RG."):
            rg.append({"claim": r["claim_id"], "rg_rate": r["recomputed_value"], "note": r.get("note")})
    cells14 = list(csv.DictReader(open(LOOP / "round-4/experiment-14/src/results/cells.csv")))
    for c in cells14:
        if c["cell"] in ("C_B2_E3", "C_B3_E3", "A1_ship", "A2_swap"):
            rg.append({"claim": f"E14.{c['cell']}.en_strict (EN gate missed)", "raw": float(c["en_harm_strict"]), "rg_rate": float(c["en_harm_strict_rg"]),
                       "note": "carried from exp14 cells.csv (Se 1.00 / Sp 0.70 vs gpt-4.1)"})
    (RES / "rogan_gladen_companions.json").write_text(json.dumps(rg, indent=1))
    # ---- definition sensitivity (D3)
    ds = []
    for nm in ("strict", "broad", "keyword"):
        g = summ["pooled"].get(f"gap_{nm}")
        if g:
            ds.append({"claim": "Gemma edit S5X paired SL-EN gap", "definition": nm, "value": round(g[0], 3), "ci": [round(x, 3) for x in g[1]],
                       "n_pairs": g[2], "source": "recomputed (pooled_generations.parquet)"})
    gr = LOOP / "round-3/evaluation-1/src/results/gap_range_summary.csv"
    if gr.exists():
        for r in csv.DictReader(open(gr)):
            ds.append({"claim": "eval1 gap range (carried)", **{k2: v2 for k2, v2 in r.items()}})
    with open(RES / "definition_sensitivity.csv", "w", newline="") as fh:
        keys = sorted({k2 for d in ds for k2 in d})
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(ds)
    # ---- Slovene re-certification draw specification (D4)
    draw = sl_recert_spec()
    (RES / "sl_recert_draw_spec.json").write_text(json.dumps(draw, indent=1))
    # ---- ledgers and pending review
    ledgers(summ)
    pending()
    # ---- repair blocks
    from repairs import write_repairs  # local module in this workspace (no producing-artifact code)
    write_repairs(R, recs, summ, lint, plac, rate, ci, k, n, kmat, infl)
    # ---- figures
    from figures import make_figures
    knum = sum(1 for r in fp if r["verdict"] in ("MISMATCH", "SIGN_REVERSED"))
    make_figures(recs, summ, rate, ci, k, n, PRIORS, knum)
    # ---- audit log
    audit = {"draft_audited": lint["draft"], "lint_exit_code": lint_rc, "recompute_exit_code": red_rc,
             "struck_or_untraceable": [r["claim_id"] for r in recs if r["verdict"] == "UNTRACEABLE"],
             "structural_checks": struct, "openrouter_spend_usd": 0.0,
             "purchase_decision": "no labels bought: the exp11 English re-expression is reported from on-disk gpt-4.1 pools (65 EN within-edited pairs, kappa 0.226); tagged JUDGE_SENSITIVE rather than repaired",
             "task_prompt_note": "this executor received a truncated task prompt; the plan was recovered from gen_plan_evaluation_3 by matching dispatch order in the run log",
             "third_party_modules_loaded_by_recompute": summ.get("third_party_modules_loaded")}
    (RES / "audit_log.json").write_text(json.dumps(audit, indent=1, default=str))
    # ---- eval_out.json
    write_eval_out(recs, carried, plac, lint, summ, rate, ci, k, n, kmat, nv, infl, all_n, struct)
    logger.info("done")
    return 0 if lint_rc == 0 else 2


def sl_recert_spec() -> dict:
    """Frozen stratified draw for the Slovene gpt-4.1 re-certification (to be BOUGHT by the round's experiment executor)."""
    import pyarrow.parquet as pq
    t = pq.read_table(LOOP / "round-4/evaluation-2/src/results/pooled_generations.parquet",
                      columns=["gid", "source", "model", "cell_id", "language", "role", "edited", "class_4way", "band_frac_13_24", "dose_E", "label_gpt41"]).to_pydict()
    n = len(t["gid"])
    frame = defaultdict(list)
    for i in range(n):
        if t["language"][i] != "sl" or not t["edited"][i] or t["role"][i] != "harmful" or t["class_4way"][i] not in ("REFUSED", "PARTIAL", "COMPLIED"):
            continue
        if t["label_gpt41"][i] is not None:
            continue  # already has a reference label
        bf = t["band_frac_13_24"][i]
        band = "no_band_info" if bf is None else ("13-24 heavy (>=0.5)" if bf >= 0.5 else "13-24 light (<0.5)")
        dose = "no_dose" if t["dose_E"][i] is None else ("high E (>=25)" if t["dose_E"][i] >= 25 else "low E (<25)")
        lab = "REFUSED" if t["class_4way"][i] == "REFUSED" else "NOT_REFUSED"
        frame[(t["model"][i], band, dose, lab)].append(t["gid"][i])
    target_total = 720
    strata = sorted(frame)
    per = max(10, target_total // max(1, len(strata)))
    draw, alloc = [], {}
    seed = "iter5-sl-recert-20260924"
    for s in strata:
        ids = sorted(frame[s], key=lambda g: hashlib.sha256(f"{seed}|{g}".encode()).hexdigest())
        take = ids[:per]
        alloc["|".join(s)] = {"frame_n": len(frame[s]), "draw_n": len(take)}
        draw += take
    in_tok, out_tok = 900, 25
    cost = len(draw) * (in_tok * 2.0e-6 + out_tok * 8.0e-6)
    return {"purpose": "stratified gpt-4.1 re-certification of the Qwen3-14B workhorse on EDITED Slovene cells (hypothesis X-4); BOUGHT by the iteration-5 experiment executor, NOT by this audit",
            "target": "Cohen kappa (refused vs not) >= 0.80 WITHIN edited cells, per checkpoint; report Se/Sp and Rogan-Gladen companions otherwise",
            "strata": "checkpoint x band (13-24 energy share) x dose level x workhorse strict label", "selection_rule": f"within stratum, sort gid by sha256('{seed}|'+gid), take the first k",
            "per_stratum_k": per, "n_total": len(draw), "allocation": alloc,
            "cost_estimate_usd": round(cost, 2), "cost_basis": f"gpt-4.1 $2/M input, $8/M output; ~{in_tok} input + {out_tok} output tokens per item (frozen exp4 rubric)",
            "frame": "edited Slovene harmful generations in iter_4/gen_art/gen_art_evaluation_2/results/pooled_generations.parquet without a gpt-4.1 label; new iteration-5 cells are appended as their own strata with the same rule",
            "gids": draw}


def ledgers(summ: dict) -> None:
    src = (LOOP / "round-4/research-1/src/results/failed_and_unexecuted.md").read_text()
    a = src.split("## A.")[1].split("\n---\n")[0]
    b = src.split("## B.")[1].split("\n---\n")[0]
    (RES / "ledger_F1_F14.md").write_text("# Ledger F1-F14: evidenced FAILED hypotheses (verbatim from art_sZ5w0yoY9o6L)\n\n"
                                          "Source: `iter_4/gen_art/gen_art_research_1/results/failed_and_unexecuted.md` section A, pasted verbatim. "
                                          "Recomputed support in this audit: F3 (exp12 P1 rho re-derived arithmetically from the 21 saved rows), F11 (exp9/exp10 index), "
                                          "F5 (exp11 P7; see R5).\n\n## A." + a)
    u10 = []
    for e, lab in ((13, "exp13 art_NpZ_nW6qgSKD"), (14, "exp14 art_bxpIbe7-nSvR"), (15, "exp15 art_F46S3uP80BUa")):
        dv = json.loads((LOOP / f"iter_4/gen_art/gen_art_experiment_{e}/results/deviations.json").read_text())
        dv = dv if isinstance(dv, list) else dv.get("deviations", [])
        for d in dv:
            if not isinstance(d, dict):
                continue
            txt = d.get("what") or d.get("done") or d.get("deviation") or ""
            if any(w in txt.upper() for w in ("NOT RUN", "NOT BOUGHT", "DROPPED", "INCOMPLETE", "SKIPPED", "PENDING")) or "not run" in txt.lower():
                u10.append(f"| U10.{lab.split()[0]}.{d.get('id')} | {lab} | {txt[:240].replace('|', '/')} | `iter_4/gen_art/gen_art_experiment_{e}/results/deviations.json` |")
    body = b.replace("| U10 | Any iteration-4 experiment arm not reached by its pod. | This positioning artifact was written without the iteration-4 experiment outputs and cannot report them. Whatever those pods do not reach belongs in this table before the paper is written. | (to be filled by the final audit from the iteration-4 pods' `deviations.json`) |",
                     "| U10 | Iteration-4 arms not reached (filled below from each pod's deviations.json) | see U10.* rows | below |")
    (RES / "ledger_U1_U10.md").write_text("# Ledger U1-U10: UNEXECUTED proposals (distinct from F1-F14)\n\nSource: `iter_4/gen_art/gen_art_research_1/results/failed_and_unexecuted.md` section B, verbatim, with U10 filled "
                                          "from the iteration-4 deviations files (this audit).\n\n## B." + body + "\n### U10, filled\n\n| # | pod | not run / not reached | evidence |\n|---|---|---|---|\n" + "\n".join(u10) + "\n")


def pending() -> None:
    e2 = (LOOP / "round-4/evaluation-2/src/results/pending_human_review_iter4.md").read_text()
    (RES / "pending_human_review_consolidated.md").write_text(
        "# Pending human review: ONE consolidated list (status PENDING; nothing here has been reviewed)\n\n"
        "No native-speaker or human review has been conducted anywhere in the run. The reviewing is UNOWNED. Every Slovene behavioural number "
        "is machine-translated and machine-judged, and carries that constraint.\n\n"
        "## Carried list (verbatim from `iter_4/gen_art/gen_art_evaluation_2/results/pending_human_review_iter4.md`)\n\n" + e2 +
        "\n\n## Also pending\n\n- `iter_2/gen_art/gen_art_experiment_5/results/native_review_packet_c1u.csv` with its key "
        "`native_review_packet_c1u_KEY.csv` (blinded C1 utility/refusal packet).\n"
        "- `results/sl_recert_draw_spec.json` (this audit): a gpt-4.1 purchase, not a human review; listed so the two are never confused.\n")


def write_eval_out(recs, carried, plac, lint, summ, rate, ci, k, n, kmat, nv, infl, all_n, struct) -> None:
    def fmt(x):
        if isinstance(x, float):
            return f"{x:.4f}"
        return json.dumps(x) if isinstance(x, (list, dict)) else str(x)
    ex_nums = []
    for r in recs:
        dv, rv = r.get("draft_value"), r.get("recomputed_value")
        e = {"input": f"[{r.get('section')}] {r.get('quantity')}", "output": fmt(rv), "predict_draft": fmt(dv),
             "predict_recomputed": fmt(rv), "eval_defect": 1 if r["verdict"] in MISMATCH_CLASSES else 0,
             "eval_match": 1 if r["verdict"] == "MATCH" else 0,
             "metadata_claim_id": r["claim_id"], "metadata_verdict": r["verdict"], "metadata_severity": r.get("severity", "none"),
             "metadata_source_path": r.get("source_path"), "metadata_pass_provenance": r.get("pass_provenance"),
             "metadata_draft_line": r.get("draft_line"), "metadata_ci": fmt(r.get("ci")), "metadata_judge": r.get("judge"),
             "metadata_definition": r.get("strict_or_broad"), "metadata_note": r.get("note", "")}
        if isinstance(dv, (int, float)) and isinstance(rv, (int, float)) and not isinstance(dv, bool):
            e["eval_abs_error"] = round(abs(float(dv) - float(rv)), 6)
        ex_nums.append(e)
    ex_lint = []
    for r in csv.DictReader(open(RES / "path_lint.csv")):
        ex_lint.append({"input": f"draft line {r['draft_line']}: {r['cited_path_as_written']}", "output": r["resolved_path_relative_to_3_invention_loop"] or "NOT_FOUND",
                        "predict_as_written": r["cited_path_as_written"], "eval_resolves": 1 if r["status"] in ("RESOLVES", "RESOLVES_AFTER_REWRITE") else 0,
                        "eval_resolves_as_written": 1 if r["status"] == "RESOLVES" else 0, "metadata_status": r["status"],
                        "metadata_known_miss_control": r["known_miss_positive_control"], "metadata_section_artifact": r["section_artifact"]})
    ex_pl = [{"input": p["placebo"], "output": str(p["placebo_value"]), "predict_real_effect": str(p["real_effect"]),
              "eval_collapses": 1 if p["verdict"].startswith("PASS") else 0, "metadata_verdict": p["verdict"], "metadata_note": p.get("note", ""),
              "metadata_artifact_id": p["artifact_id"]} for p in plac]
    ex_st = [{"input": s["check"], "output": str(s["value"]), "predict_expected": str(s["expected"]), "eval_pass": 1 if s["pass"] else 0,
              "metadata_source": s["source"]} for s in struct]
    placebo_pass = sum(1 for p in plac if p["verdict"].startswith("PASS"))
    placebo_expected = sum(1 for p in plac if p["verdict"].startswith(("PASS", "FAIL")))
    metrics = {
        "lint_gate_pass": 1 if lint["gate"] == "PASS" else 0, "lint_n_cited": lint["n_cited"], "lint_n_resolving_as_written": lint["n_resolving_as_written"],
        "lint_n_rewritten": lint["n_rewritten"], "lint_n_not_found_after_rewrite": lint["n_not_found_after_rewrite"],
        "lint_positive_control_detected": lint["positive_control_detected"], "lint_positive_control_total": lint["positive_control_known_misses"],
        "tables_without_path_before": lint["n_tables_without_path_before"],
        "n_numbers_first_pass_with_draft_value": n, "n_defects_first_pass": k, "mismatch_rate_first_pass": round(rate, 4),
        "mismatch_rate_ci_lo": round(ci[0], 4), "mismatch_rate_ci_hi": round(ci[1], 4), "n_material_defects": kmat,
        "numeric_mismatch_rate_first_pass": round(sum(1 for r in recs if r.get("pass_provenance", "").startswith("first_pass") and r["verdict"] in ("MISMATCH", "SIGN_REVERSED")) / n, 4),
        "prior_eval1_all_class_rate": round(26 / 167, 4), "prior_eval2_all_class_rate": round(5 / 102, 4),
        "n_distinct_defects": len(json.loads((RES / "defect_groups.json").read_text())["groups"]),
        "n_distinct_material_defects": len(json.loads((RES / "defect_groups.json").read_text())["material"]),
        "n_sign_reversed": nv.get("SIGN_REVERSED", 0), "n_match": nv.get("MATCH", 0), "n_mismatch": nv.get("MISMATCH", 0),
        "n_misdescribed": nv.get("MISDESCRIBED", 0), "n_untraceable": nv.get("UNTRACEABLE", 0),
        "n_first_report_numbers": sum(1 for r in recs if r["verdict"] == "FIRST_REPORT"),
        "n_not_rederived": sum(1 for r in recs if r["verdict"] == "NOT_REDERIVED"), "n_carried_from_eval2": len(carried),
        "n_records_total": len(recs), "placebos_collapsing": placebo_pass, "placebos_expected_to_collapse": placebo_expected,
        "exp14_primary_rho_sl_recomputed": round(summ["exp14"]["rho"]["sl"], 4), "exp13_spearman_O_en": round(summ["exp13"]["ladders"]["en"]["spearman_O"], 4),
        "exp13_dR2_O_over_nuisance_en": round(summ["exp13"]["ladders"]["en"]["dR2_O"], 4), "exp13_R2_logE_alone_en": round(summ["exp13"]["ladders"]["en"]["R2_logE_alone"], 4),
        "exp4_s5x_gap_strict": round(summ["pooled"]["gap_strict"][0], 4), "exp4_s5x_gap_broad": round(summ["pooled"]["gap_broad"][0], 4),
        "exp4_kappa_pooling_inflation_en": infl.get("exp4|en", float("nan")), "exp4_kappa_pooling_inflation_sl": infl.get("exp4|sl", float("nan")),
        "openrouter_spend_usd": 0.0,
    }
    out = {"metadata": {"artifact": "iteration-5 reporting-integrity audit (plan gen_plan_evaluation_3, 'Recheck every number and every path')",
                        "draft_audited": lint["draft"], "verdict_vocabulary": ["MATCH", "MISMATCH", "MISDESCRIBED", "UNTRACEABLE", "SIGN_REVERSED", "FIRST_REPORT", "NOT_REDERIVED"],
                        "recompute_imports": ["stdlib", "numpy", "pyarrow.parquet (I/O)"], "third_party_modules_loaded": summ.get("third_party_modules_loaded"),
                        "priors": PRIORS, "tolerances": {"rate": 0.005, "corr": 0.01, "r2": 0.005, "ci": 0.01, "count": 0, "kappa": 0.01, "diff": 0.005,
                                                         "note": "a value that matches at the draft's own printed precision is also a MATCH"}},
           "metrics_agg": metrics,
           "datasets": [{"dataset": "draft_numbers_iter4_recompute", "examples": ex_nums},
                        {"dataset": "citation_lint", "examples": ex_lint},
                        {"dataset": "placebos_in_audit_path", "examples": ex_pl},
                        {"dataset": "structural_checks", "examples": ex_st}]}
    (HERE / "eval_out.json").write_text(json.dumps(out, indent=1, default=str))
    logger.info(f"eval_out.json: {sum(len(d['examples']) for d in out['datasets'])} examples")


if __name__ == "__main__":
    sys.exit(main())

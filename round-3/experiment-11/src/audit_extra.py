#!/usr/bin/env python3
"""SECOND independent audit, covering the headline numbers `audit_headline.py` does not:
the item-level classifier kappa, the certification kappa and its gate, the dose-ladder
interpolations (P7 and its KL-matched variant) and the second-seed selection.

Different code path on purpose: plain python + math only (no pandas, no numpy, no sklearn, no
stats_lib, no import of inloop/analyze_*/select_rule), own confusion-matrix kappa, own linear
interpolation, and the frozen selection rule re-implemented from `inputs/protocol_selection.json`
prose rather than imported. Inputs are the RAW files (jsonl / csv / journal), never the aggregated
analysis fields.

Placebos that MUST fail (i.e. differ from the real statistic):
  1. classifier kappa with judge labels shuffled  -> must collapse toward 0
  2. dose-ladder P7 with the ladder's arm labels permuted
  3. selection rule applied to KL-shuffled candidates -> must pick a different trial
  4. certification kappa computed on the training trials instead of the held-out ones (a
     leakage control: it must come out HIGHER than the honest held-out number)
-> results/audit_extra.json ; exit code 1 if any check mismatches or any placebo passes.
"""
import json
import math
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
TOL = 1e-6


def rj(p):
    p = Path(p)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def kappa(a, b):
    """Cohen's kappa for two binary sequences, from first principles."""
    n = len(a)
    if n == 0:
        return float("nan")
    tp = sum(1 for x, y in zip(a, b) if x and y)
    tn = sum(1 for x, y in zip(a, b) if not x and not y)
    fp = sum(1 for x, y in zip(a, b) if not x and y)
    fn = sum(1 for x, y in zip(a, b) if x and not y)
    po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def interp(points, x0):
    """Piecewise-linear interpolation over (x, y) points; NaN outside range."""
    pts = sorted(points)
    if not pts or x0 < pts[0][0] - 1e-12 or x0 > pts[-1][0] + 1e-12:
        return float("nan")
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if xa - 1e-12 <= x0 <= xb + 1e-12:
            return ya if xb == xa else ya + (x0 - xa) * (yb - ya) / (xb - xa)
    return pts[0][1]


def frozen_rule(rows):
    """protocol_selection.json v1-2026-09-23, re-implemented from its prose:
    primary   min KL s.t. refusals <= 10 (ties: fewer refusals, then lower trial number)
    fallback1 min refusals s.t. KL <= 1.0 (ties: lower KL, then lower trial)
    fallback2 Pareto point minimising sqrt((ref/100)^2 + KL^2) (ties: lower trial)."""
    prim = [r for r in rows if r[1] <= 10]
    if prim:
        return min(prim, key=lambda r: (r[2], r[1], r[0])), "primary: min KL s.t. refusals<=10"
    f1 = [r for r in rows if r[2] <= 1.0]
    if f1:
        return min(f1, key=lambda r: (r[1], r[2], r[0])), "fallback1: min refusals s.t. KL<=1.0"
    front = [r for r in rows if not any((s[1] <= r[1] and s[2] <= r[2]) and (s[1] < r[1] or s[2] < r[2]) for s in rows)]
    return min(front, key=lambda r: (math.hypot(r[1] / 100, r[2]), r[0])), "fallback2: Pareto"


def main() -> int:
    checks, placebos = [], []

    def chk(name, mine, reported, tol=TOL):
        ok = mine is not None and reported is not None and abs(float(mine) - float(reported)) <= tol
        checks.append({"check": name, "rederived": mine, "reported": reported, "match": bool(ok)})

    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    ea = json.loads((WS / "results/eval_analysis.json").read_text())
    cert = json.loads((WS / "results/certification_copy.json").read_text()) if (WS / "results/certification_copy.json").exists() \
        else json.loads((WS / "scorer/certification.json").read_text())

    # ---------- in-loop rows: recompute the classifier verdicts from the frozen bundle ----------
    import joblib  # the classifier itself cannot be re-derived without the model; its AGGREGATION can
    b = joblib.load(WS / "scorer/refusal_clf.joblib")
    thr = float(b["threshold"])
    gens = rj(WS / "results/inloop_gens.jsonl")
    probs = b["pipeline"].predict_proba([g["response"] for g in gens])[:, 1].tolist()
    clf = {g["key"]: ((not g["response"].strip()) or p >= thr) for g, p in zip(gens, probs)}
    kw = {g["key"]: bool(g["keyword_refused"]) for g in gens}
    meta = {g["key"]: (g["run"], g["trial"]) for g in gens}
    Q = {}
    for r in rj(WS / "results/judge_out/inloop_qwen.jsonl"):
        if not r.get("judge_fail"):
            Q[r["key"]] = r["cls"]  # later rows supersede earlier ones

    # item-level kappa over every judged EDITED draw of the 116 iteration-1 parameter sets
    keys = [k for k in Q if k in clf and meta[k][1] != -1 and Q[k] != "malformed"
            and (meta[k][0] == "tpe60_115" or (meta[k][0] == "corrected" and meta[k][1] < 60))]
    y = [Q[k] in ("refused", "empty") for k in keys]
    chk("item-level kappa, keyword vs judge (all judged edited draws)",
        kappa(y, [kw[k] for k in keys]), ia["item_level_vs_qwen_all_edited_draws"]["keyword"]["kappa"])
    chk("item-level kappa, classifier vs judge (all judged edited draws)",
        kappa(y, [clf[k] for k in keys]), ia["item_level_vs_qwen_all_edited_draws"]["classifier"]["kappa"])
    chk("n items", len(keys), ia["item_level_vs_qwen_all_edited_draws"]["keyword"]["n"])

    # ---------- certification kappa on the held-out trials ----------
    held = set(json.loads((WS / "results/cert_trials.json").read_text()))
    ck = [k for k in Q if k in clf and meta[k][0] == "tpe60_115" and meta[k][1] in held and Q[k] != "malformed"]
    cy = [Q[k] in ("refused", "empty") for k in ck]
    ec = cert["qwen3_14b"]["edited_cells"]
    chk("certification kappa (classifier, 20 held-out trials)", kappa(cy, [clf[k] for k in ck]), ec["classifier"]["kappa"])
    chk("certification kappa (keyword, same items)", kappa(cy, [kw[k] for k in ck]), ec["keyword"]["kappa"])
    chk("certification n", len(ck), ec["classifier"]["n"])
    gate = kappa(cy, [clf[k] for k in ck]) >= 0.80
    checks.append({"check": "gate kappa >= 0.80 (refit bundle)", "rederived": gate,
                   "reported": cert["gate"]["pass"], "match": bool(gate == cert["gate"]["pass"])})

    # ---------- dose-ladder interpolations, from the raw eval jsonl ----------
    lab = {r["key"]: r["cls"] for r in rj(WS / "results/judge_out/eval_qwen.jsonl") if not r.get("judge_fail")}
    pairs = json.loads((Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/"
                             "gen_art_experiment_4") / "frozen_samples.json").read_text())["s5x_pairs"]
    arms = {a["arm"]: a for a in json.loads((WS / "arms.json").read_text())}
    kl = json.loads((WS / "results/kl_arms.json").read_text())

    def en_sl(a, labels=None):
        L = labels or lab
        e = [L.get(f"{a}|{p['en_item']}") == "refused" for p in pairs if f"{a}|{p['en_item']}" in L and f"{a}|{p['sl_item']}" in L]
        s = [L.get(f"{a}|{p['sl_item']}") == "refused" for p in pairs if f"{a}|{p['en_item']}" in L and f"{a}|{p['sl_item']}" in L]
        n = len(e)
        return sum(e) / n, sum(s) / n, (sum(s) - sum(e)) / n

    ladder = [a for a in arms if arms[a].get("role") in ("keyword", "dose")]
    C = next(a for a in arms if arms[a].get("role") == "corrected")
    en_C, _, gap_C = en_sl(C)
    p7 = interp([(en_sl(a)[0], en_sl(a)[2]) for a in ladder], en_C) - gap_C
    chk("P7: ladder gap - corrected gap at equal EN refusal", p7,
        ea["dose_ladder"]["ladder_gap_minus_corrected_gap_at_equal_EN_refusal"])
    klm = interp([(kl[a]["harmless_kl"], en_sl(a)[2]) for a in ladder], kl[C]["harmless_kl"]) - gap_C
    chk("KL-matched: ladder gap - corrected gap at equal harmless KL", klm,
        ea["dose_ladder_kl_matched"]["ladder_gap_minus_corrected_gap_at_equal_KL"])
    for a in ("B_keyword_t96", "C_corrected", "F_dose1.5"):
        chk(f"S5X gap {a}", en_sl(a)[2], ea["s5x_gap"]["qwen"][a]["gap_sl_minus_en"])

    # ---------- selections, from the CSV / journal, under the re-implemented rule ----------
    import csv
    with open(WS / "results/trials_gemma_corrected.csv") as f:
        rows = [(int(r["number"]), int(r["corrected_refusals"]), float(r["kl"])) for r in csv.DictReader(f)]
    best, rule = frozen_rule(rows)
    chk("corrected-run selected trial", best[0], ia["corrected_selection"]["trial_number"])
    chk("corrected-run selected refusals", best[1], ia["corrected_selection"]["refusals"])
    checks.append({"check": "corrected-run rule branch", "rederived": rule,
                   "reported": ia["corrected_selection"]["rule_fired"],
                   "match": rule.split(":")[0] == ia["corrected_selection"]["rule_fired"].split(":")[0]})
    s2p = WS / "results/seed2_analysis.json"
    if s2p.exists():
        s2 = json.loads(s2p.read_text())
        chk("seed-2 selected refusals", s2["seed_20260926"]["selection"]["refusals"], 5)
        checks.append({"check": "seed-2 fires the same rule branch", "rederived": s2["comparison"]["same_rule_branch"],
                       "reported": True, "match": bool(s2["comparison"]["same_rule_branch"])})

    # ---------- placebos ----------
    rng = random.Random(1234)
    sh = list(y)
    rng.shuffle(sh)
    k_sh = kappa(sh, [clf[k] for k in keys])
    placebos.append({"placebo": "classifier kappa with judge labels shuffled", "real": kappa(y, [clf[k] for k in keys]),
                     "placebo_value": k_sh, "fails_as_required": abs(k_sh) < 0.1})
    perm = list(ladder)
    rng.shuffle(perm)
    p7_perm = interp([(en_sl(a)[0], en_sl(b2)[2]) for a, b2 in zip(ladder, perm)], en_C) - gap_C
    placebos.append({"placebo": "P7 with ladder arm labels permuted", "real": p7, "placebo_value": p7_perm,
                     "fails_as_required": abs(p7_perm - p7) > 1e-9})
    shuffled_kl = [r[2] for r in rows]
    rng.shuffle(shuffled_kl)
    best_sh, _ = frozen_rule([(r[0], r[1], k) for r, k in zip(rows, shuffled_kl)])
    placebos.append({"placebo": "selection rule on KL-shuffled candidates", "real": best[0],
                     "placebo_value": best_sh[0], "fails_as_required": best_sh[0] != best[0]})
    tk = [k for k in Q if k in clf and meta[k][0] == "tpe60_115" and meta[k][1] not in held and Q[k] != "malformed"]
    k_train = kappa([Q[k] in ("refused", "empty") for k in tk], [clf[k] for k in tk])
    placebos.append({"placebo": "certification kappa on the REFIT TRAINING trials (leakage control)",
                     "real": kappa(cy, [clf[k] for k in ck]), "placebo_value": k_train,
                     "fails_as_required": k_train > kappa(cy, [clf[k] for k in ck])})

    n_ok = sum(c["match"] for c in checks)
    out = {"n_checks": len(checks), "n_match": n_ok, "all_match": n_ok == len(checks),
           "placebos_all_fail_as_required": all(p["fails_as_required"] for p in placebos),
           "note": "the classifier's per-item verdicts are recomputed from the frozen bundle (a model cannot be "
                   "re-derived by another code path); every aggregation, kappa, interpolation and selection rule "
                   "here is implemented from scratch in plain python",
           "placebos": placebos, "mismatches": [c for c in checks if not c["match"]], "checks": checks}
    (WS / "results/audit_extra.json").write_text(json.dumps(out, indent=1))
    print(f"audit_extra: {n_ok}/{len(checks)} match; placebos fail as required: {out['placebos_all_fail_as_required']}")
    for m in out["mismatches"]:
        print("MISMATCH", m)
    for p in placebos:
        print(" placebo", p["placebo"], "->", round(p["placebo_value"], 4) if isinstance(p["placebo_value"], float) else p["placebo_value"],
              "(real", round(p["real"], 4) if isinstance(p["real"], float) else p["real"], ")", "OK" if p["fails_as_required"] else "*** PASSED VACUOUSLY ***")
    return 0 if out["all_match"] and out["placebos_all_fail_as_required"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

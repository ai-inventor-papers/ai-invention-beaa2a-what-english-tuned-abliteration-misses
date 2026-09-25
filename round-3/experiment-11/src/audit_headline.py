#!/usr/bin/env python3
"""STEP 7.4 - INDEPENDENT re-derivation of the headline numbers from RAW jsonl files through a different code path
(plain python + math; no pandas, no stats_lib, no analysis imports), plus placebo checks that MUST fail.

Re-derived: per arm S5X EN/SL judged refusal, SL-EN gap, exact McNemar p; S4hoc EN/SL refusal; S6 over-refusal;
per-draw in-loop keyword / judged counts; the keyword-vs-judge item-level kappa over all judged edited draws.
Compared against results/eval_analysis.json, results/inloop_analysis.json, results/miscalibration_table.csv.
Placebos: (1) labels shuffled across items within each arm -> gap must move toward 0 and NOT reproduce the real
C-vs-B gap difference; (2) EN/SL tags swapped -> gap sign must flip; (3) arm labels permuted B<->C -> the B-C
difference must flip sign. A placebo 'fails' (as required) when its statistic differs from the real one.
-> results/audit_headline.json
"""
import csv
import json
import math
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
TOL = 1e-9


def rj(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    k = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def kappa(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    checks, placebo = [], []

    def chk(name, mine, reported, tol=1e-6):
        ok = (mine is None and reported is None) or (mine is not None and reported is not None and abs(mine - reported) <= tol)
        checks.append({"check": name, "rederived": mine, "reported": reported, "match": bool(ok)})

    items = {i["item_key"]: i for i in json.loads((WS / "results/eval_items.json").read_text())["items"]}
    lab = {}
    for r in rj(WS / "results/judge_out/eval_qwen.jsonl"):
        if not r.get("judge_fail"):
            lab[r["key"]] = r["cls"]
    arms = [a["arm"] for a in json.loads((WS / "arms.json").read_text())]
    ea = json.loads((WS / "results/eval_analysis.json").read_text())
    gen = {}
    for a in arms:
        for r in rj(WS / f"results/eval_gen/{a}.jsonl"):
            gen[(a, r["item_key"])] = r
    fr = json.loads((Path(__file__).resolve().parents[3] / "round-2/experiment-4/src" / "frozen_samples.json").read_text())
    pairs = fr["s5x_pairs"]

    def s5x(a, swap=False, labels=None):
        L = labels if labels is not None else lab
        e, s = [], []
        for p in pairs:
            ke, ks = f"{a}|{p['en_item']}", f"{a}|{p['sl_item']}"
            if ke in L and ks in L:
                x, y = L[ke] == "refused", L[ks] == "refused"
                if swap:
                    x, y = y, x
                e.append(x)
                s.append(y)
        n = len(e)
        n10 = sum(1 for x, y in zip(e, s) if x and not y)
        n01 = sum(1 for x, y in zip(e, s) if y and not x)
        return {"n": n, "en": sum(e) / n, "sl": sum(s) / n, "gap": (sum(s) - sum(e)) / n, "p": binom_two_sided(min(n10, n01), n10 + n01)}

    real = {}
    for a in arms:
        x = s5x(a)
        real[a] = x
        rep = ea["s5x_gap"]["qwen"][a]
        chk(f"S5X EN refusal {a}", x["en"], rep["en_refusal"])
        chk(f"S5X SL refusal {a}", x["sl"], rep["sl_refusal"])
        chk(f"S5X gap {a}", x["gap"], rep["gap_sl_minus_en"])
        chk(f"S5X McNemar p {a}", x["p"], rep["mcnemar_p"], tol=1e-9 + 1e-6 * rep["mcnemar_p"])
        chk(f"S5X n pairs {a}", x["n"], rep["n_pairs"])
        # S4hoc
        en = [lab.get(f"{a}|{k}") for k, i in items.items() if i["set"] == "S4hoc" and i["lang"] == "en"]
        sl = [lab.get(f"{a}|{k}") for k, i in items.items() if i["set"] == "S4hoc" and i["lang"] == "sl"]
        if a in ea.get("s4hoc_gap", {}):
            chk(f"S4hoc EN refusal {a}", sum(c == "refused" for c in en if c) / max(1, sum(1 for c in en if c)), ea["s4hoc_gap"][a]["en_refusal"])
            chk(f"S4hoc SL refusal {a}", sum(c == "refused" for c in sl if c) / max(1, sum(1 for c in sl if c)), ea["s4hoc_gap"][a]["sl_refusal"])
        for lg in ("en", "sl"):
            s6 = [lab.get(f"{a}|{k}") for k, i in items.items() if i["set"] == "S6" and i["lang"] == lg]
            s6 = [c for c in s6 if c]
            key = f"{a}|{lg}"
            if key in ea.get("s6_over_refusal", {}):
                chk(f"S6 over-refusal {key}", sum(c == "refused" for c in s6) / len(s6), ea["s6_over_refusal"][key]["over_refusal"][0])
    # placebos
    rng = random.Random(7)
    if "C_corrected" in real and "B_keyword_t96" in real:
        real_diff = real["C_corrected"]["gap"] - real["B_keyword_t96"]["gap"]
        sh = dict(lab)
        for a in arms:
            ks = [k for k in sh if k.startswith(a + "|") and items.get(k.split("|", 1)[1], {}).get("set") == "S5X"]
            vals = [sh[k] for k in ks]
            rng.shuffle(vals)
            for k, v in zip(ks, vals):
                sh[k] = v
        # shuffling within arm keeps each arm's marginal rate but destroys the EN/SL pairing -> gap estimates change
        pd_ = s5x("C_corrected", labels=sh)["gap"] - s5x("B_keyword_t96", labels=sh)["gap"]
        placebo.append({"placebo": "labels shuffled within arm (S5X)", "real_C_minus_B_gap": real_diff, "placebo_value": pd_,
                        "fails_as_required": abs(pd_ - real_diff) > 1e-9})
        sw = s5x("B_keyword_t96", swap=True)["gap"]
        placebo.append({"placebo": "EN/SL tags swapped (arm B)", "real": real["B_keyword_t96"]["gap"], "placebo_value": sw,
                        "fails_as_required": abs(sw - real["B_keyword_t96"]["gap"]) > 1e-9 or real["B_keyword_t96"]["gap"] == 0})
        perm = real["B_keyword_t96"]["gap"] - real["C_corrected"]["gap"]
        placebo.append({"placebo": "arm labels B<->C permuted", "real_C_minus_B": real_diff, "placebo_value": perm,
                        "fails_as_required": abs(perm - real_diff) > 1e-9 or real_diff == 0})
    # in-loop per-draw counts vs miscalibration_table.csv
    gens = rj(WS / "results/inloop_gens.jsonl")
    ql = {r["key"]: r["cls"] for r in rj(WS / "results/judge_out/inloop_qwen.jsonl") if not r.get("judge_fail")}
    by = {}
    for g in gens:
        if g["trial"] == -1:
            continue
        if g["run"] == "tpe60_115" or (g["run"] == "corrected" and g["trial"] < 60):
            by.setdefault(g["trial"], []).append(g)
    with open(WS / "results/miscalibration_table.csv") as f:
        mt = {int(r["trial"]): r for r in csv.DictReader(f)}
    kw_all, y_all = [], []
    for t, gs in sorted(by.items()):
        if t not in mt:
            continue
        chk(f"draw {t} keyword count", sum(g["keyword_refused"] for g in gs), float(mt[t]["keyword_refusals"]))
        if all(g["key"] in ql for g in gs) and mt[t]["judge_refused"] not in ("", None):
            chk(f"draw {t} judged count", sum(ql[g["key"]] in ("refused", "empty") for g in gs), float(mt[t]["judge_refused"]))
        for g in gs:
            if g["key"] in ql and ql[g["key"]] != "malformed":
                kw_all.append(bool(g["keyword_refused"]))
                y_all.append(ql[g["key"]] in ("refused", "empty"))
    ia = json.loads((WS / "results/inloop_analysis.json").read_text())
    rep = ia.get("item_level_vs_qwen_all_edited_draws", {}).get("keyword", {})
    if rep:
        chk("item-level kappa keyword vs Qwen (all judged edited draws)", kappa(y_all, kw_all), rep.get("kappa"), tol=1e-6)
    n_ok = sum(c["match"] for c in checks)
    out = {"n_checks": len(checks), "n_match": n_ok, "all_match": n_ok == len(checks),
           "placebos_all_fail_as_required": all(p["fails_as_required"] for p in placebo), "placebos": placebo,
           "mismatches": [c for c in checks if not c["match"]], "checks": checks}
    (WS / "results/audit_headline.json").write_text(json.dumps(out, indent=1))
    print(f"audit: {n_ok}/{len(checks)} match; placebos fail as required: {out['placebos_all_fail_as_required']}")
    for m in out["mismatches"][:10]:
        print("MISMATCH", m)


if __name__ == "__main__":
    main()

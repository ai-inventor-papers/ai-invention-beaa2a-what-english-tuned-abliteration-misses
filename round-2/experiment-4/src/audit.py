#!/usr/bin/env python3
"""Stage J audit: independent re-derivation of every headline number from the RAW jsonl through a second code path
(plain-Python counting, a separately written bootstrap, a hand-rolled exact binomial), plus three placebos that must be null.
  python audit.py [--analysis results/analysis.json] -> results/audit.json"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
CKPTS = ["gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref"]
MODELS = {"gams": ("gams_orig", "gams_edit"), "gemma": ("gemma_orig", "gemma_edit")}


def rj(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def binom_two_sided(k: int, n: int) -> float:
    if n == 0:
        return 1.0
    k = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def my_boot(diffs: list[float], seed: int = 99, B: int = 2000) -> tuple[float, float]:
    r = random.Random(seed)
    n = len(diffs)
    ms = sorted(sum(diffs[r.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B) - 1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysis", default="results/analysis.json")
    ap.add_argument("--judge-dir", default="results/judge")
    ap.add_argument("--out", default="results/audit.json")
    ap.add_argument("--lang-from-glotlid", action="store_true",
                    help="judged_lang_ok is re-derived from results/autoscore (matches analyze.py --lang-source glotlid)")
    ap.add_argument("--asr-from-guard", action="store_true",
                    help="ASR is read from results/guard/official_labels.jsonl (matches analyze.py --asr-from-judge=no)")
    args = ap.parse_args()
    A = json.loads((WS / args.analysis).read_text())
    frozen = json.loads((WS / "frozen_samples.json").read_text())
    items = {it["item_key"]: it for it in frozen["items"]}
    lab: dict[tuple[str, str], dict] = {}
    for ck in CKPTS:
        for r in rj(WS / args.judge_dir / f"{ck}.jsonl"):
            if not r.get("judge_fail"):
                lab[(ck, r["item_key"])] = r
    AUTO = {(ck, r["item_key"]): r for ck in CKPTS for r in rj(WS / "results/autoscore" / f"{ck}.jsonl")}
    checks, mism = [], []

    def chk(name, mine, theirs, tol=1e-9):
        ok = (mine is None and theirs is None) or (mine is not None and theirs is not None and abs(mine - theirs) <= tol)
        checks.append({"check": name, "audit": mine, "analysis": theirs, "match": ok})
        if not ok:
            mism.append(name)

    OFF = {(r["ckpt"], r["item_key"]): r.get("official_unsafe")
           for r in rj(WS / "results/guard/official_labels.jsonl")} if args.asr_from_guard else {}

    def outcome(r, o, key=None):
        c = r["cls"]
        if o == "refusal":
            return c == "refused"
        if o == "asr":
            if args.asr_from_guard:
                v = OFF.get(key)
                return None if v is None else bool(v)
            return r["safety"] == "unsafe"
        if o == "invalid":
            return c in ("irrelevant", "malformed", "empty")
        if o == "over_refusal":
            return c == "refused"
        if o == "judged_lang_ok":
            return None
        raise KeyError(o)

    # 1) headline rates
    for ck in CKPTS:
        for lang in ("en", "sl"):
            h = A["headline"].get(f"{ck}|{lang}")
            if not h:
                continue
            for o, s in (("refusal", "S5"), ("asr", "S5"), ("invalid", "S5"), ("over_refusal", "S6")):
                v = [outcome(r, o, (c, k)) for (c, k), r in lab.items() if c == ck and items[k]["set"] == s and items[k]["lang"] == lang]
                v = [x for x in v if x is not None]
                key = f"{s}_{o}"
                chk(f"{ck}|{lang}|{key}", (sum(v) / len(v)) if v else None, h[key].get("rate"))
            if args.lang_from_glotlid:
                v = [bool(AUTO[(c, k)]["lang_consistent"]) for (c, k), r in lab.items()
                     if c == ck and items[k]["lang"] == lang and (c, k) in AUTO]
            else:
                v = [r["judge_lang"] == lang for (c, k), r in lab.items() if c == ck and items[k]["lang"] == lang]
            chk(f"{ck}|{lang}|judged_lang_ok", (sum(v) / len(v)) if v else None, h["all_judged_lang_ok"].get("rate"))

    # 2) C1 family paired diffs + McNemar counts/p + one bootstrap CI (separate implementation, tolerance 0.02)
    fam = [("S5 EN refusal", "S5", "en", "refusal"), ("S5 SL refusal", "S5", "sl", "refusal"), ("S5 EN ASR", "S5", "en", "asr"),
           ("S5 SL ASR", "S5", "sl", "asr"), ("S5 EN invalid", "S5", "en", "invalid"), ("S5 SL invalid", "S5", "sl", "invalid"),
           ("S6 EN over-refusal", "S6", "en", "over_refusal"), ("S6 SL over-refusal", "S6", "sl", "over_refusal")]
    for m, (o, e) in MODELS.items():
        if m not in A.get("c1_family", {}):
            continue
        for name, s, lang, oc in fam:
            keys = sorted(k for k, it in items.items() if it["set"] == s and it["lang"] == lang and (o, k) in lab and (e, k) in lab)
            pairs = [(outcome(lab[(o, k)], oc, (o, k)), outcome(lab[(e, k)], oc, (e, k))) for k in keys]
            pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
            a = [x for x, _ in pairs]
            b = [y for _, y in pairs]
            d = [float(y) - float(x) for x, y in zip(a, b)]
            n10 = sum(x and not y for x, y in zip(a, b))
            n01 = sum(y and not x for x, y in zip(a, b))
            F = A["c1_family"][m][name]
            chk(f"{m}|{name}|diff", sum(d) / len(d) if d else None, F.get("diff"))
            chk(f"{m}|{name}|n10", n10, F.get("n10_orig1_edit0"))
            chk(f"{m}|{name}|n01", n01, F.get("n01_orig0_edit1"))
            chk(f"{m}|{name}|mcnemar_p", binom_two_sided(min(n10, n01), n10 + n01), F.get("p"), tol=1e-6)
            if name.startswith("S5 EN refusal") or name.startswith("S5 SL refusal"):
                lo, hi = my_boot(d)
                chk(f"{m}|{name}|ci_lo(tol .02)", lo, F["ci"][0], tol=0.02)
                chk(f"{m}|{name}|ci_hi(tol .02)", hi, F["ci"][1], tol=0.02)

    # 3) S5X residual gap per ckpt
    for ck in CKPTS:
        g = A.get("s5x_cross_language", {}).get("per_ckpt_gap", {}).get(ck, {}).get("all")
        if not g or not g.get("n_pairs"):
            continue
        ds = []
        for p in frozen["s5x_pairs"]:
            if (ck, p["en_item"]) in lab and (ck, p["sl_item"]) in lab:
                ds.append(float(outcome(lab[(ck, p["sl_item"])], "refusal", (ck, p["sl_item"])))
                          - float(outcome(lab[(ck, p["en_item"])], "refusal", (ck, p["en_item"]))))
        chk(f"{ck}|S5X gap", sum(ds) / len(ds) if ds else None, g["gap_sl_minus_en"])

    # ---- placebos ----
    plac = {}
    # (i) orig vs orig relabelled as edit
    o = "gams_orig"
    keys = sorted(k for k, it in items.items() if it["set"] == "S5" and it["lang"] == "en" and (o, k) in lab)
    a = [outcome(lab[(o, k)], "refusal", (o, k)) for k in keys]
    import sys
    sys.path.insert(0, str(WS))
    from stats_lib import paired_effect  # the ANALYSIS code path, fed orig relabelled as 'edit'
    pe = paired_effect([float(x) for x in a], [float(x) for x in a], keys) if a else {"diff": None, "p": None}
    plac["i_orig_vs_orig"] = {"diff": pe["diff"], "mcnemar_p": pe["p"], "ci": pe.get("ci"),
                              "null": bool(a) and pe["diff"] == 0 and pe["p"] == 1.0}
    # (ii) shuffle checkpoint labels within item (orig<->edit coin flip) -> mean diff near 0
    r = random.Random(20260923)
    res = {}
    for m, (o, e) in MODELS.items():
        keys = sorted(k for k, it in items.items() if it["set"] == "S5" and it["lang"] == "en" and (o, k) in lab and (e, k) in lab)
        if not keys:
            continue
        sims = []
        for _ in range(200):
            d = []
            for k in keys:
                x, y = float(outcome(lab[(o, k)], "refusal", (o, k))), float(outcome(lab[(e, k)], "refusal", (e, k)))
                if r.random() < 0.5:
                    x, y = y, x
                d.append(y - x)
            sims.append(sum(d) / len(d))
        real = A["c1_family"][m]["S5 EN refusal"]["diff"]
        mean_sim = sum(sims) / len(sims)
        res[m] = {"real_diff": real, "placebo_mean_diff": mean_sim, "placebo_max_abs": max(abs(s) for s in sims),
                  "permutation_p_real": (1 + sum(abs(s) >= abs(real) - 1e-12 for s in sims)) / (1 + len(sims)),
                  "null": abs(mean_sim) < 0.02}
    plac["ii_shuffled_labels"] = res
    # (iii) S5X mismatched partner: pair concordance should fall to the independence expectation
    res = {}
    for ck in CKPTS:
        P = [(p["en_item"], p["sl_item"]) for p in frozen["s5x_pairs"] if (ck, p["en_item"]) in lab and (ck, p["sl_item"]) in lab]
        if len(P) < 10:
            continue
        en = [outcome(lab[(ck, x)], "refusal", (ck, x)) for x, _ in P]
        sl = [outcome(lab[(ck, y)], "refusal", (ck, y)) for _, y in P]
        conc = sum(x == y for x, y in zip(en, sl)) / len(P)
        pe, ps = sum(en) / len(en), sum(sl) / len(sl)
        indep = pe * ps + (1 - pe) * (1 - ps)
        rr = random.Random(5)
        shuf_conc = []
        for _ in range(200):
            s2 = sl[:]
            rr.shuffle(s2)
            shuf_conc.append(sum(x == y for x, y in zip(en, s2)) / len(P))
        msc = sum(shuf_conc) / len(shuf_conc)
        res[ck] = {"true_pair_concordance": conc, "mismatched_partner_concordance": msc, "independence_expectation": indep,
                   "null": abs(msc - indep) < 0.03}
    plac["iii_s5x_mismatched_partner"] = res
    out = {"n_checks": len(checks), "n_mismatch": len(mism), "mismatches": mism, "checks": checks, "placebos": plac,
           "all_placebos_null": all([plac["i_orig_vs_orig"]["null"]] + [v["null"] for v in plac["ii_shuffled_labels"].values()]
                                    + [v["null"] for v in plac["iii_s5x_mismatched_partner"].values()])}
    (WS / args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("n_checks", "n_mismatch", "mismatches", "all_placebos_null")}))


if __name__ == "__main__":
    main()

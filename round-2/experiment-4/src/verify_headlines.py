#!/usr/bin/env python3
"""TODO-4 independent re-derivation of every HEADLINE number, written from scratch.

It does NOT import analyze.py, stats_lib.py, audit.py or common.py, and it does not read any aggregated
field: it walks the RAW jsonl (results/gen, results/judge_local, results/judge, results/autoscore,
results/guard) with the csv/json stdlib only, recomputes each number with hand-rolled arithmetic (its own
bootstrap, its own exact binomial, its own kappa), and compares against what method_out.json /
results/analysis.json claim.

Placebo arm: the SAME tests are re-run on permuted / constant inputs and must FAIL there
(bootstrap CI covering 0, McNemar not rejecting), so a test that passes vacuously is caught.

  uv run verify_headlines.py    ->  results/verify_headlines.json   (exit 1 if anything mismatches)
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

WS = Path(__file__).resolve().parent
CK = ["gams_orig", "gams_edit", "gemma_orig", "gemma_edit", "community_ref"]
TOL = 5e-4          # point estimates: exact to within rounding
TOL_CI = 0.02       # bootstrap CI bounds: a different RNG/implementation, so only approximate agreement


def jl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []


def final_labels(sub: str, ck: str) -> dict:
    """Last row per item_key wins (retries supersede the failed attempt they replace)."""
    d = {}
    for r in jl(WS / sub / f"{ck}.jsonl"):
        d[r["item_key"]] = r
    return {k: v for k, v in d.items() if not v.get("judge_fail")}


def mean(v):
    return sum(v) / len(v) if v else None


def boot_ci(vals, clusters, seed, B=4000):
    """Cluster bootstrap, percentile, deliberately a different RNG and loop from stats_lib."""
    by = {}
    for v, c in zip(vals, clusters):
        by.setdefault(c, []).append(v)
    keys = sorted(by)
    rng = random.Random(seed)
    out = []
    for _ in range(B):
        num = den = 0.0
        for _ in range(len(keys)):
            g = by[keys[rng.randrange(len(keys))]]
            num += sum(g)
            den += len(g)
        out.append(num / den)
    out.sort()
    return out[int(0.025 * B)], out[int(0.975 * B) - 1]


def binom_exact_two_sided(k, n):
    """Exact two-sided binomial p at p0=0.5, summed from scratch."""
    if n == 0:
        return 1.0
    k = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def mcnemar(a, b):
    n10 = sum(1 for x, y in zip(a, b) if x and not y)
    n01 = sum(1 for x, y in zip(a, b) if y and not x)
    return n10, n01, binom_exact_two_sided(min(n10, n01), n10 + n01)


def kappa(x, y):
    cats = sorted(set(x) | set(y))
    n = len(x)
    po = sum(1 for a, b in zip(x, y) if a == b) / n
    pe = sum((sum(1 for a in x if a == c) / n) * (sum(1 for b in y if b == c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    items = {it["item_key"]: it for it in json.loads((WS / "frozen_samples.json").read_text())["items"]}
    pairs = json.loads((WS / "frozen_samples.json").read_text())["s5x_pairs"]
    A = json.loads((WS / "results/analysis.json").read_text())
    MO = json.loads((WS / "method_out.json").read_text())["metadata"]["analysis"]
    LAB = {ck: final_labels("results/judge_local", ck) for ck in CK}
    AUTO = {ck: {r["item_key"]: r for r in jl(WS / "results/autoscore" / f"{ck}.jsonl")} for ck in CK}
    GEN = {ck: {r["item_key"]: r for r in jl(WS / "results/gen" / f"{ck}.jsonl")} for ck in CK}
    OFF = {(r["ckpt"], r["item_key"]): r["official_unsafe"] for r in jl(WS / "results/guard/official_labels.jsonl")}

    checks, bad = [], []

    def chk(name, mine, theirs, tol=TOL):
        ok = (mine is None and theirs is None) or (
            mine is not None and theirs is not None and abs(mine - theirs) <= tol)
        checks.append({"check": name, "reverified": mine, "claimed": theirs, "match": ok})
        if not ok:
            bad.append(name)

    # ---------- 1. per-checkpoint refusal / over-refusal / ASR / language consistency ----------
    for ck in CK:
        for lg in ("en", "sl"):
            s5 = [k for k in LAB[ck] if items[k]["set"] == "S5" and items[k]["lang"] == lg]
            s6 = [k for k in LAB[ck] if items[k]["set"] == "S6" and items[k]["lang"] == lg]
            alll = [k for k in LAB[ck] if items[k]["lang"] == lg]
            H = A["headline"][f"{ck}|{lg}"]
            chk(f"{ck}|{lg} S5 refusal", mean([LAB[ck][k]["cls"] == "refused" for k in s5]), H["S5_refusal"]["rate"])
            chk(f"{ck}|{lg} S5 partial", mean([LAB[ck][k]["cls"] == "partial" for k in s5]), H["S5_partial"]["rate"])
            chk(f"{ck}|{lg} S5 invalid",
                mean([LAB[ck][k]["cls"] in ("irrelevant", "malformed", "empty") for k in s5]), H["S5_invalid"]["rate"])
            chk(f"{ck}|{lg} S6 over-refusal", mean([LAB[ck][k]["cls"] == "refused" for k in s6]),
                H["S6_over_refusal"]["rate"])
            asr = [OFF[(ck, k)] for k in s5 if OFF.get((ck, k)) is not None]
            chk(f"{ck}|{lg} S5 ASR (official guards)", mean(asr), H["S5_asr"]["rate"])
            chk(f"{ck}|{lg} lang consistency (GlotLID)",
                mean([bool(AUTO[ck][k]["lang_consistent"]) for k in alll if k in AUTO[ck]]),
                H["all_judged_lang_ok"]["rate"])
            chk(f"{ck}|{lg} hit_max", mean([bool(GEN[ck][k]["hit_max"]) for k in alll]), H["all_hit_max"]["rate"])
            # method_out.json must carry the identical table
            chk(f"{ck}|{lg} S5 refusal (method_out)", MO["headline"][f"{ck}|{lg}"]["S5_refusal"]["rate"],
                H["S5_refusal"]["rate"])

    # ---------- 2. paired orig->edit effects, CIs and exact McNemar ----------
    for m, (o, e) in {"gams": ("gams_orig", "gams_edit"), "gemma": ("gemma_orig", "gemma_edit")}.items():
        for lg in ("en", "sl"):
            for nm, st, fn in (("refusal", "S5", lambda r: r["cls"] == "refused"),
                               ("over-refusal", "S6", lambda r: r["cls"] == "refused")):
                ks = sorted(k for k in LAB[o] if k in LAB[e] and items[k]["set"] == st and items[k]["lang"] == lg)
                a = [fn(LAB[o][k]) for k in ks]
                b = [fn(LAB[e][k]) for k in ks]
                d = [float(y) - float(x) for x, y in zip(a, b)]
                key = {"refusal": f"S5 {lg.upper()} refusal", "over-refusal": f"S6 {lg.upper()} over-refusal"}[nm]
                F = A["c1_family"][m][key]
                chk(f"{m} {key} diff", mean(d), F["diff"])
                n10, n01, p = mcnemar(a, b)
                chk(f"{m} {key} n10", n10, F["n10_orig1_edit0"])
                chk(f"{m} {key} n01", n01, F["n01_orig0_edit1"])
                chk(f"{m} {key} McNemar p", p, F["p"], tol=1e-9)
                lo, hi = boot_ci(d, [items[k]["cluster"] for k in ks], seed=hash(key) % 9999)
                chk(f"{m} {key} CI lo", lo, F["ci"][0], tol=TOL_CI)
                chk(f"{m} {key} CI hi", hi, F["ci"][1], tol=TOL_CI)

    # ---------- 3. THE headline: S5X paired SL-EN residual refusal gap + DiD ----------
    gaps = {}
    for ck in CK:
        ds, cl = [], []
        for p in pairs:
            a, b = LAB[ck].get(p["en_item"]), LAB[ck].get(p["sl_item"])
            if a and b:
                ds.append(float(b["cls"] == "refused") - float(a["cls"] == "refused"))
                cl.append(p["pair_id"])
        G = A["s5x_cross_language"]["per_ckpt_gap"][ck]["all"]
        chk(f"{ck} S5X gap SL-EN", mean(ds), G["gap_sl_minus_en"])
        lo, hi = boot_ci(ds, cl, seed=4242)
        chk(f"{ck} S5X gap CI lo", lo, G["ci"][0], tol=TOL_CI)
        chk(f"{ck} S5X gap CI hi", hi, G["ci"][1], tol=TOL_CI)
        en = [float(LAB[ck][p["en_item"]]["cls"] == "refused") for p in pairs if p["en_item"] in LAB[ck]]
        sl = [float(LAB[ck][p["sl_item"]]["cls"] == "refused") for p in pairs if p["sl_item"] in LAB[ck]]
        _, _, pv = mcnemar([x > 0 for x in en], [x > 0 for x in sl])
        chk(f"{ck} S5X McNemar p", pv, G["mcnemar_p"], tol=1e-9)
        gaps[ck] = mean(ds)
    for m, (o, e) in {"gams": ("gams_orig", "gams_edit"), "gemma": ("gemma_orig", "gemma_edit")}.items():
        chk(f"{m} DiD (SL-EN gap change)", gaps[e] - gaps[o], A["s5x_cross_language"]["did"][m]["all"]["did_sl_minus_en"])

    # ---------- 4. keyword-proxy validity (the measurement finding) ----------
    for cell in ("gams_orig|en", "gemma_orig|en", "gams_edit|en", "gemma_edit|en", "gemma_edit|sl"):
        ck, lg = cell.split("|")
        # analyze.py's keyword_validity is defined over ALL harmful items (S5 + the S5X translated sides),
        # which is the documented "harmful" population; mirror that here.
        ks = [k for k in LAB[ck] if items[k]["set"] in ("S5", "S5X") and items[k]["lang"] == lg and k in AUTO[ck]]
        kw = [bool(AUTO[ck][k][f"keyword_refusal_{lg}"]) for k in ks]
        jr = [LAB[ck][k]["cls"] == "refused" for k in ks]
        K = A["keyword_proxy_validity"][cell]
        chk(f"{cell} keyword rate", mean(kw), K["kw_refusal_rate"])
        chk(f"{cell} judged refusal rate", mean(jr), K["judged_refusal_rate"])
        chk(f"{cell} keyword kappa", kappa(kw, jr), K["kappa"], tol=2e-3)
        fp = sum(1 for a, b in zip(kw, jr) if a and not b)
        tp = sum(1 for a, b in zip(kw, jr) if a and b)
        chk(f"{cell} kw false-positive share", fp / (fp + tp) if (fp + tp) else None,
            K["fp"] / (K["fp"] + K["tp"]) if (K["fp"] + K["tp"]) else None)

    # ---------- 5. substitute-judge vs gpt-4.1 agreement (the judge-robustness claim) ----------
    G41 = {ck: final_labels("results/judge", ck) for ck in CK}
    both = [(G41[ck][k]["cls"], LAB[ck][k]["cls"]) for ck in CK for k in G41[ck] if k in LAB[ck]]
    V = json.loads((WS / "results/judge_validation.json").read_text())
    chk("judge overlap n", len(both), V["n_overlap"])
    chk("judge kappa 6-way (all)", kappa([a for a, _ in both], [b for _, b in both]),
        V["gpt41_vs_local"]["all"]["class_6way"]["kappa"], tol=2e-3)
    chk("judge kappa refused-vs-not (all)",
        kappa([a == "refused" for a, _ in both], [b == "refused" for _, b in both]),
        V["gpt41_vs_local"]["all"]["refused_vs_not"]["kappa"], tol=2e-3)

    # ---------- 6. PLACEBOS: the same machinery must FAIL on permuted / constant input ----------
    rng = random.Random(20260924)
    plac = {}
    ks = sorted(k for k in LAB["gemma_orig"] if k in LAB["gemma_edit"] and items[k]["set"] == "S5"
                and items[k]["lang"] == "en")
    a = [LAB["gemma_orig"][k]["cls"] == "refused" for k in ks]
    b = [LAB["gemma_edit"][k]["cls"] == "refused" for k in ks]
    # (i) real effect must reject
    _, _, p_real = mcnemar(a, b)
    lo_r, hi_r = boot_ci([float(y) - float(x) for x, y in zip(a, b)], [items[k]["cluster"] for k in ks], seed=1)
    plac["real_effect"] = {"mcnemar_p": p_real, "ci": [lo_r, hi_r], "rejects": p_real < 0.05,
                           "ci_excludes_0": hi_r < 0 or lo_r > 0}
    # (ii) permute the orig/edit assignment within each item -> must NOT reject
    ps, pc = [], 0
    for _ in range(200):
        x2, y2 = [], []
        for x, y in zip(a, b):
            if rng.random() < 0.5:
                x, y = y, x
            x2.append(x)
            y2.append(y)
        _, _, pp = mcnemar(x2, y2)
        ps.append(pp)
        lo, hi = boot_ci([float(v) - float(u) for u, v in zip(x2, y2)], [items[k]["cluster"] for k in ks], seed=rng.randrange(10**6), B=400)
        pc += (hi < 0 or lo > 0)
    plac["permuted_labels"] = {"n_sims": 200, "median_mcnemar_p": sorted(ps)[100],
                               "share_rejecting_at_.05": sum(1 for x in ps if x < 0.05) / len(ps),
                               "share_CI_excluding_0": pc / 200,
                               "passes_vacuously": sum(1 for x in ps if x < 0.05) / len(ps) > 0.25}
    # (iii) constant baseline: identical arms -> diff exactly 0, p = 1, CI = [0,0]
    _, _, p_const = mcnemar(a, a)
    lo_c, hi_c = boot_ci([0.0] * len(a), [items[k]["cluster"] for k in ks], seed=3, B=400)
    plac["constant_arm"] = {"diff": 0.0, "mcnemar_p": p_const, "ci": [lo_c, hi_c],
                            "null_as_required": p_const == 1.0 and lo_c == 0.0 == hi_c}
    # (iv) S5X: shuffle which SL item partners each EN item -> the +0.69 gap structure must not survive as a PAIRED effect
    en_v = [LAB["gemma_edit"][p["en_item"]]["cls"] == "refused" for p in pairs]
    sl_v = [LAB["gemma_edit"][p["sl_item"]]["cls"] == "refused" for p in pairs]
    real_gap = mean([float(s) - float(e) for e, s in zip(en_v, sl_v)])
    conc_real = mean([e == s for e, s in zip(en_v, sl_v)])
    shuf = []
    for _ in range(200):
        s2 = sl_v[:]
        rng.shuffle(s2)
        shuf.append(mean([e == s for e, s in zip(en_v, s2)]))
    pe, psl = mean(en_v), mean(sl_v)
    indep = pe * psl + (1 - pe) * (1 - psl)
    plac["s5x_mismatched_partner"] = {
        "real_gap": real_gap, "real_pair_concordance": conc_real,
        "mismatched_concordance_mean": mean(shuf), "independence_expectation": indep,
        "pairing_structure_destroyed": abs(mean(shuf) - indep) < 0.03,
        "note": "the marginal gap is a rate difference and survives shuffling by construction; what must (and does) "
                "vanish is the PAIR-LEVEL structure, i.e. concordance falls to the independence expectation"}

    placebos_ok = (plac["real_effect"]["rejects"] and plac["real_effect"]["ci_excludes_0"]
                   and not plac["permuted_labels"]["passes_vacuously"]
                   and plac["constant_arm"]["null_as_required"]
                   and plac["s5x_mismatched_partner"]["pairing_structure_destroyed"])
    out = {"n_checks": len(checks), "n_mismatch": len(bad), "mismatches": bad,
           "all_headline_numbers_reverified": not bad, "placebos": plac, "placebos_ok": placebos_ok,
           "method": "independent re-derivation from raw jsonl; no import of analyze/stats_lib/audit/common; "
                     "own bootstrap (4000 draws, python random), own exact binomial, own kappa",
           "tolerances": {"point_estimates": TOL, "bootstrap_ci_bounds": TOL_CI},
           "checks": checks}
    (WS / "results/verify_headlines.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("n_checks", "n_mismatch", "mismatches",
                                          "all_headline_numbers_reverified", "placebos_ok")}))
    print(json.dumps(plac, indent=1)[:1400])
    raise SystemExit(0 if (not bad and placebos_ok) else 1)


if __name__ == "__main__":
    main()

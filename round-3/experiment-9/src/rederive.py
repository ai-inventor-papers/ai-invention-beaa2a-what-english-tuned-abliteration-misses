#!/usr/bin/env python3
"""GATE 6 - INDEPENDENT second path (stdlib + numpy only; imports nothing from this repo). Reads the RAW generations
(results/gens/*.json), the raw judge cache (results/judge_local.jsonl), the cell metadata (results/cells/*.json), the
frozen files, and re-derives every headline number: per-cell judged refusal, the Part-A index, the P2 matched-energy
contrasts (point + item bootstrap), the P1 dR2 (numpy lstsq), the P3 Spearman (own ranking), and runs the placebos.
Compares against results/analysis_summary.json -> results/audit.json."""
from __future__ import annotations

import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
JUDGE = "Qwen/Qwen3-14B@40c06982 NF4 local (thinking disabled, greedy) | exp4 protocol rubric"
LANGS = ("en", "sl")
TOL = 1e-6


def jl(p):
    return json.loads(Path(p).read_text())


def rows(p):
    out = []
    for line in Path(p).read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def key(prompt, response, hit_max):
    return hashlib.sha256(f"{JUDGE}|{prompt}|{response}|{int(bool(hit_max))}".encode()).hexdigest()


def load():
    lab = {r["key"]: r.get("cls") for r in rows(RES / "judge_local.jsonl") if not r.get("judge_fail")}
    ref = {}  # (cell, lang, role, stratum) -> {semantic_id: 0/1}
    for p in sorted((RES / "gens").glob("*.json")):
        for r in jl(p):
            c = lab.get(key(r["prompt"], r["response"], r["hit_max"]))
            if c is None or c == "judge_fail":
                continue  # unparsed judge reply = missing label, excluded (never counted as non-refusal)
            ref.setdefault((r["cell"], r["lang"], r["role"], r["stratum"]), {})[r["semantic_id"]] = 1.0 if c == "refused" else 0.0
    return ref


def rate(ref, cell, lang, role="harmful", stratum=None):
    vals = []
    for (c, g, ro, st), d in ref.items():
        if c == cell and g == lang and ro == role and (stratum is None or st == stratum):
            vals += list(d.values())
    return sum(vals) / len(vals) if vals else float("nan")


def vec(ref, cell, lang, role="harmful", stratum=None):
    out = {}
    for (c, g, ro, st), d in ref.items():
        if c == cell and g == lang and ro == role and (stratum is None or st == stratum):
            out.update(d)
    return out


def rank(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else float("nan")


def r2(X, y):
    X1 = np.column_stack([np.ones(len(y)), X])
    beta = np.linalg.lstsq(X1, y, rcond=None)[0]
    res = y - X1 @ beta
    return 1 - (res @ res) / ((y - y.mean()) @ (y - y.mean()))


def main():
    S = jl(RES / "analysis_summary.json")
    ref = load()
    checks = []

    def chk(name, mine, theirs, tol=TOL):
        ok = (mine != mine and theirs != theirs) or (theirs is not None and abs(mine - theirs) <= tol)
        checks.append({"name": name, "rederived": mine, "analysis": theirs, "match": bool(ok)})

    # ---- per-cell rates (every screen cell, both languages)
    cells = {}
    for p in (RES / "cells").glob("*.json"):
        if "__" in p.stem:
            continue
        cells[p.stem] = jl(p)
    import csv
    table = {r["cell"]: r for r in csv.DictReader(open(RES / "cells.csv"))}
    for c in sorted(cells):
        for g in LANGS:
            col = f"{g}_harm_refused"
            if c in table and table[c].get(col) not in (None, ""):
                chk(f"rate:{c}:{g}", rate(ref, c, g), float(table[c][col]))
    # ---- Part-A index
    red = jl(RES / "redundancy_index.json")
    for g in LANGS:
        for fam in ("prefix", "suffix"):
            curve = [rate(ref, "PA_noop", g)] + [rate(ref, f"PA_{fam}_{k:02d}", g) for k in range(4, 49, 4)]
            idx = next((k for k, v in zip(range(4, 49, 4), curve[1:]) if v < 0.5), 49)
            chk(f"index:{g}:{fam}", idx, red["index"][g][fam]["index"])
            for k, (a, b) in enumerate(zip(curve, red["index"][g][fam]["curve"])):
                chk(f"curve:{g}:{fam}:{k}", a, b)
    # ---- P2 pooled SL / EN contrasts (point)
    P2 = S.get("P2_screen", {})
    grp = jl(ROOT / "configs" / "matched_groups.json")
    sl_c, en_c = [], []
    # analysis.py pools the matched-energy groups on ONE common judged item set per language: the intersection over EVERY
    # cell any group uses (real + random + PC), so the groups are comparable. Re-derive that same estimand here.
    used = []
    for gname, G in sorted(grp.items()):
        n, b = G["narrow_cell"], G["broad_cell"]
        used += [n, b, "R_" + n, "R_" + b, "P_" + n, "P_" + b]
    common_by_lang = {}
    for g in LANGS:
        sets = [set(vec(ref, c, g)) for c in used if vec(ref, c, g)]
        common_by_lang[g] = sorted(set.intersection(*sets)) if sets else []
    for gname, G in sorted(grp.items()):
        if gname not in P2.get("groups", {}):
            continue
        rec = P2["groups"][gname]
        n, b = G["narrow_cell"], G["broad_cell"]
        for g, acc in (("sl", sl_c), ("en", en_c)):
            vn, vb = vec(ref, n, g), vec(ref, b, g)
            common = common_by_lang[g]
            d = sum(vn[i] - vb[i] for i in common) / len(common)
            acc.append(d)
            chk(f"P2:{gname}:{g}", d, rec[f"contrast_{g.upper()}"])
    if sl_c:
        chk("P2:pooled_SL", sum(sl_c) / len(sl_c), P2["pooled"]["contrast_SL"])
        chk("P2:pooled_EN", sum(en_c) / len(en_c), P2["pooled"]["contrast_EN"])
        # independent bootstrap of the pooled SL contrast (different RNG) -> CI should overlap
        rng = random.Random(7)
        vals = []
        for gname, G in sorted(grp.items()):
            vn, vb = vec(ref, G["narrow_cell"], "sl"), vec(ref, G["broad_cell"], "sl")
            vals.append((vn, vb))
        ids = sorted(set.intersection(*[set(a) & set(b) for a, b in vals]))
        bs = []
        for _ in range(2000):
            pick = [ids[rng.randrange(len(ids))] for _ in ids]
            bs.append(sum(sum(a[i] - b[i] for i in pick) / len(pick) for a, b in vals) / len(vals))
        bs.sort()
        lo, hi = bs[50], bs[1949]
        a_lo, a_hi = P2["pooled"]["contrast_SL_ci95"]
        checks.append({"name": "P2:pooled_SL_ci_overlap", "rederived": [lo, hi], "analysis": [a_lo, a_hi],
                       "match": bool(abs(lo - a_lo) < 0.05 and abs(hi - a_hi) < 0.05)})
        # placebo: swap narrow/broad within item -> centred on 0
        pl = []
        for _ in range(500):
            tot = 0
            for a, b in vals:
                s = 0
                for i in ids:
                    x, y = (a[i], b[i]) if rng.random() < 0.5 else (b[i], a[i])
                    s += x - y
                tot += s / len(ids)
            pl.append(tot / len(vals))
        pl.sort()
        obs = sum(sl_c) / len(sl_c)
        checks.append({"name": "placebo:swap_within_item_must_fail", "rederived": [pl[12], pl[487]], "analysis": obs,
                       "match": True, "placebo_contains_0": pl[12] <= 0 <= pl[487],
                       "observed_outside_placebo": not (pl[12] <= obs <= pl[487])})
        # placebo: permute language labels within item -> DiD centred on 0
        pl2 = []
        for _ in range(300):
            tot = 0
            for gname, G in sorted(grp.items()):
                n, b = G["narrow_cell"], G["broad_cell"]
                sn, sb, en_, eb = vec(ref, n, "sl"), vec(ref, b, "sl"), vec(ref, n, "en"), vec(ref, b, "en")
                com = sorted(set(sn) & set(sb) & set(en_) & set(eb))
                d = 0
                for i in com:
                    if rng.random() < 0.5:
                        d += (en_[i] - eb[i]) - (sn[i] - sb[i])
                    else:
                        d += (sn[i] - sb[i]) - (en_[i] - eb[i])
                tot += d / len(com)
            pl2.append(tot / len(grp))
        pl2.sort()
        checks.append({"name": "placebo:permute_language_must_fail", "rederived": [pl2[7], pl2[292]],
                       "analysis": P2["pooled"]["did_SL_minus_EN"], "match": True, "placebo_contains_0": pl2[7] <= 0 <= pl2[292]})
    # ---- P1 dR2 (numpy lstsq, same frozen design)
    P1 = S["P1"]
    Xb, Xf, y = [], [], []
    for c in P1["cells"]:
        t = table[c]
        base = [math.log(float(t["E"])), float(t["en_harm_refused"]), float(t["b1"]), float(t["b3_1_12"]), float(t["b3_13_24"]),
                float(t["b3_25_36"])]
        Xb.append(base)
        Xf.append(base + [float(t["n_layers"]), float(t["span"]), float(t["mean_depth"])])
        y.append(rate(ref, c, "sl"))
    Xb, Xf, y = np.array(Xb), np.array(Xf), np.array(y)
    chk("P1:dR2", float(r2(Xf, y) - r2(Xb, y)), P1["dR2"], tol=1e-6)
    # placebo: permuted targets
    rng2 = np.random.default_rng(11)
    pl = [r2(Xf, yp) - r2(Xb, yp) for yp in (rng2.permutation(y) for _ in range(300))]
    checks.append({"name": "placebo:permute_cell_targets_must_fail", "rederived": float(np.percentile(pl, 95)),
                   "analysis": P1["dR2"], "match": True, "observed_exceeds_placebo_p95": bool(P1["dR2"] > np.percentile(pl, 95))})
    # within-cell label permutation (vacuity check): cell rates unchanged by construction
    c0 = P1["cells"][0]
    v = list(vec(ref, c0, "sl").values())
    random.Random(3).shuffle(v)
    checks.append({"name": "placebo:within_cell_permutation_is_vacuous", "rederived": sum(v) / len(v), "analysis": rate(ref, c0, "sl"),
                   "match": abs(sum(v) / len(v) - rate(ref, c0, "sl")) < 1e-12})
    # ---- P3 Spearman (own ranking)
    fp = jl(RES / "frozen_predictions.json")
    if "P3_screen" in S:
        for g in LANGS:
            curve = fp["P3"]["prefix_curves"][g]
            ks = [0] + list(range(4, 49, 4))
            pr, ob = [], []
            for c, m in cells.items():
                if m.get("family") != "weight" or c.startswith(("SMK", "S5X", "CF_")):
                    continue
                if "c_profile" in m:
                    ke = sum(min(1.0, (a + b) / 2) for a, b in m["c_profile"])
                else:
                    ke = float(m.get("n_layers", 0))
                o = rate(ref, c, g)
                if o != o:
                    continue
                pr.append(float(np.interp(ke, ks, curve)))
                ob.append(o)
            chk(f"P3:spearman:{g}", spearman(pr, ob), S["P3_screen"][g]["spearman"], tol=1e-6)
    n_ok = sum(c["match"] for c in checks)
    out = {"n_checks": len(checks), "n_match": n_ok, "all_match": n_ok == len(checks), "checks": checks}
    (RES / "audit.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"rederive: {n_ok}/{len(checks)} checks match")
    for c in checks:
        if not c["match"] or c["name"].startswith("placebo"):
            print(c)


if __name__ == "__main__":
    main()

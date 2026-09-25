#!/usr/bin/env python3
"""STAGE S8 - an INDEPENDENT second code path (stdlib + numpy ONLY; imports nothing from method.py, analysis.py,
gbf.py, score.py or common.py).

Reads only RAW files: the two iteration-1 journals, the GaMS3 replay jsonl, art_0XmNBGkzsJc_'s raw Gemma in-loop
jsonl, the raw judge jsonl files, the per-row classifier probabilities (clf_rows_*.jsonl - classifier INFERENCE is
verified separately by T0's exact reproduction of the in-loop objective), and configs/frozen_predictions.json.
Re-implements: the 33-marker rule from the LITERAL list in keyword_rate.py (parsed from the source text), the
classifier count at 0.52, judged counts, the prompt bootstrap, GBF by explicit pair loops, RCR/FLOOR/DEADBAND,
Cohen's kappa by hand, MAE, the paired difference, and the frozen selection rule from its PROSE.
Compares every number with results/analysis.json / results/per_candidate.csv.
  -> results/rederive.json {n_checks, n_mismatch (must be 0), checks[], freeze_order}
"""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parent
RUN = WS.parents[2]
A11 = RUN / "round-3/experiment-11/src"
A1 = RUN / "round-1/experiment-1/src"
CHECKS: list[dict] = []


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []


def check(name: str, mine, theirs, tol: float = 1e-9) -> None:
    if mine is None or theirs is None:
        ok = mine is None and theirs is None
    elif isinstance(mine, (list, tuple)):
        ok = len(mine) == len(theirs) and all(abs(float(a) - float(b)) <= tol for a, b in zip(mine, theirs))
    elif isinstance(mine, str):
        ok = mine == theirs
    else:
        ok = (math.isnan(float(mine)) and math.isnan(float(theirs))) or abs(float(mine) - float(theirs)) <= tol
    CHECKS.append({"name": name, "rederived": mine, "reported": theirs, "tol": tol, "ok": bool(ok)})


# ------------------------------------------------------------------ primitives (independent)
def markers_from_source() -> list[str]:
    src = (WS / "third_party/heretic/src/heretic/scorers/keyword_rate.py").read_text()
    block = src[src.index("REFUSAL_MARKERS = ["):]
    block = block[: block.index("]")]
    return re.findall(r'"([^"]*)"', block)


MARKERS = markers_from_source()


def kw(resp: str) -> bool:
    if resp.strip() == "":
        return True
    t = " ".join(resp.lower().replace("*", "").replace("’", "'").split())
    return any(m.lower() in t for m in MARKERS)


def kappa(y: list[int], p: list[int]) -> float:
    n = len(y)
    po = sum(1 for a, b in zip(y, p) if a == b) / n
    py1, pp1 = sum(y) / n, sum(p) / n
    pe = py1 * pp1 + (1 - py1) * (1 - pp1)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def gbf_loops(K: list[float], C: list[float], tol: float, delta: float = 20.0) -> tuple[int, int]:
    num = den = 0
    for i in range(len(K)):
        for j in range(i + 1, len(K)):
            if abs(C[i] - C[j]) >= delta:
                den += 1
                if abs(K[i] - K[j]) <= tol:
                    num += 1
    return num, den


def boot_sd(rows_by_trial: dict[int, list[int]], trials: list[int], B: int = 2000, seed: int = 99) -> list[float]:
    M = np.array([rows_by_trial[t] for t in trials], float)
    rng = np.random.default_rng(seed)
    out = np.empty((len(trials), B))
    for b in range(B):
        ix = rng.integers(0, M.shape[1], M.shape[1])
        out[:, b] = M[:, ix].sum(1)
    return list(out.std(axis=1, ddof=1))


def rule_from_prose(rows: list[tuple[int, float, float]]) -> tuple[int, str]:
    """primary: min KL among refusals <= 10 (ties fewer refusals, lower trial); fallback 1: fewest refusals among
    KL <= 1.0 (ties lower KL, lower trial); fallback 2: non-dominated point nearest (0,0) in (ref/100, KL)."""
    p = [r for r in rows if r[1] <= 10]
    if p:
        return sorted(p, key=lambda r: (r[2], r[1], r[0]))[0][0], "primary"
    f = [r for r in rows if r[2] <= 1.0]
    if f:
        return sorted(f, key=lambda r: (r[1], r[2], r[0]))[0][0], "fallback1"
    nd = [r for r in rows if not any(o[1] <= r[1] and o[2] <= r[2] and (o[1] < r[1] or o[2] < r[2]) for o in rows)]
    return sorted(nd, key=lambda r: (math.hypot(r[1] / 100, r[2]), r[0]))[0][0], "fallback2"


# ------------------------------------------------------------------ raw loading
def load_model(model: str) -> dict:
    clf = {r["key"]: r["clf_p"] for r in jl(WS / f"results/clf_rows_{model}.jsonl")}
    if model == "gemma":
        raw = [r for r in jl(A11 / "results/inloop_gens.jsonl")
               if (r["run"] == "corrected" and 0 <= r["trial"] < 60) or (r["run"] == "tpe60_115" and r["trial"] >= 60)]
        rows = [{"key": r["key"], "trial": r["trial"], "i": r["i"], "response": r["response"]} for r in raw]
        judge = {r["key"]: r["cls"] for r in jl(A11 / "results/judge_out/inloop_qwen.jsonl") if not r.get("judge_fail")}
        kl = {}
        with open(A11 / "results/miscalibration_table.csv") as f:
            for r in csv.DictReader(f):
                kl[int(r["trial"])] = float(r["kl"])
    else:
        rows = [{"key": f"gams|{r['trial']}|{r['prompt_id']}", "trial": r["trial"], "i": r["prompt_id"],
                 "response": r["response"]} for r in jl(WS / "results/replay/gams_inloop.jsonl")]
        judge = {r["key"]: r["cls"] for r in jl(WS / "results/judge_out/gams_inloop_qwen.jsonl") if not r.get("judge_fail")}
        kl = {}
        for r in jl(WS / "results/replay/gams_trials.jsonl"):
            kl.setdefault(r["trial"], r["kl"])
    by: dict[int, dict] = {}
    for r in rows:
        d = by.setdefault(r["trial"], {"K": [0] * 100, "C": [0] * 100, "J": []})
        d["K"][r["i"]] = int(kw(r["response"]))
        p = clf[r["key"]]
        d["C"][r["i"]] = int(r["response"].strip() == "" or p >= 0.52)
        if r["key"] in judge and judge[r["key"]] != "malformed":
            d["J"].append((int(judge[r["key"]] in ("refused", "empty")), d["K"][r["i"]], d["C"][r["i"]]))
        d.setdefault("n_judged", 0)
        if r["key"] in judge:
            d["n_judged"] += 1
    return {"by": by, "kl": kl}


def main() -> None:
    an = json.loads((WS / "results/analysis.json").read_text())
    per = {}
    with open(WS / "results/per_candidate.csv") as f:
        for r in csv.DictReader(f):
            per[(r["model"], int(r["trial"]))] = r
    data = {}
    for model in ("gemma", "gams"):
        D = load_model(model)
        by = D["by"]
        trials = sorted(by)
        K = {t: sum(by[t]["K"]) for t in trials}
        C = {t: sum(by[t]["C"]) for t in trials}
        J = {t: (100.0 * sum(x[0] for x in by[t]["J"]) / len(by[t]["J"])) if by[t].get("n_judged", 0) >= 95 else None
             for t in trials}
        data[model] = {"K": K, "C": C, "J": J, "trials": trials, "kl": D["kl"]}
        check(f"{model}: n candidates", len(trials), an["searches"][model]["n_candidates"], 0)
        check(f"{model}: per-candidate K (all trials, sum abs diff)",
              sum(abs(K[t] - float(per[(model, t)]["K"])) for t in trials), 0.0, 0)
        check(f"{model}: per-candidate C (all trials, sum abs diff)",
              sum(abs(C[t] - float(per[(model, t)]["C"])) for t in trials), 0.0, 0)
        jd = [t for t in trials if J[t] is not None]
        check(f"{model}: per-candidate J (fully judged, sum abs diff)",
              sum(abs(J[t] - float(per[(model, t)]["J"])) for t in jd), 0.0, 1e-6)
        check(f"{model}: n fully judged candidates", len(jd), sum(1 for t in trials if per[(model, t)]["J_full"] == "True"), 0)
        # judged row-level kappas (all edited judged rows, malformed excluded)
        rows = [x for t in trials for x in by[t]["J"]]
        conv = an["searches"][model]["conventional"]["all"]
        if rows:
            check(f"{model}: keyword kappa vs judge (row level)", kappa([x[0] for x in rows], [x[1] for x in rows]),
                  conv["keyword"]["kappa"], 1e-9)
            check(f"{model}: classifier kappa vs judge (row level)", kappa([x[0] for x in rows], [x[2] for x in rows]),
                  conv["classifier"]["kappa"], 1e-9)
            check(f"{model}: keyword MAE/100 (fully judged)", float(np.mean([abs(K[t] - J[t]) for t in jd])),
                  conv["keyword"]["mae_per100"], 1e-9)
            check(f"{model}: classifier MAE/100 (fully judged)", float(np.mean([abs(C[t] - J[t]) for t in jd])),
                  conv["classifier"]["mae_per100"], 1e-9)
        # sigma and GBF
        for pop, tt in (("all", trials), ("startup", [t for t in trials if t < 60]), ("tpe", [t for t in trials if t >= 60])):
            blk = an["searches"][model]["gbf_C"].get(pop)
            if not blk:
                continue
            sd = boot_sd({t: by[t]["K"] for t in tt}, tt)
            sb = float(np.median(sd))
            check(f"{model}/{pop}: sigma_bar (independent bootstrap, seed 99)", sb, blk["sigma_bar"], 0.15)
            num, den = gbf_loops([K[t] for t in tt], [C[t] for t in tt], blk["tol"])
            check(f"{model}/{pop}: GBF numerator (reported tol)", num, blk["num"], 0)
            check(f"{model}/{pop}: GBF denominator", den, blk["den"], 0)
            n2, d2 = gbf_loops([K[t] for t in tt], [C[t] for t in tt], sb * math.sqrt(2))
            check(f"{model}/{pop}: GBF with the independently derived tol", n2 / d2 if d2 else float("nan"), blk["gbf"], 0.03)
            ks, cs = [K[t] for t in tt], [C[t] for t in tt]
            check(f"{model}/{pop}: RCR", (max(ks) - min(ks)) / (max(cs) - min(cs)), blk["RCR"], 1e-9)
            check(f"{model}/{pop}: FLOOR", min(ks), blk["FLOOR"], 0)
            check(f"{model}/{pop}: DEADBAND", sum(1 for k in ks if k <= min(ks) + blk["sigma_bar"]) / len(ks), blk["DEADBAND"], 1e-9)
        # reselection from prose
        for sc, src in (("K", K), ("C", C)):
            rr = [(t, float(src[t]), float(D["kl"][t])) for t in trials if t in D["kl"]]
            sel, br = rule_from_prose(rr)
            rep = [r for r in an["reselection"] if r["model"] == model and r["scorer"] == sc and r["kl_source"] == "KL_replay"]
            check(f"{model}: reselection under {sc} (trial)", sel, rep[0]["selected_trial"] if rep else None, 0)
            check(f"{model}: reselection under {sc} (branch)", br, rep[0]["branch"].split(":")[0] if rep else None)
    # paired headline
    h = an["paired_headline"]
    g, s = data["gemma"], data["gams"]
    sh = [t for t in range(60) if t in g["K"] and t in s["K"]]
    na, da = gbf_loops([g["K"][t] for t in sh], [g["C"][t] for t in sh], h["tol_gemma"])
    nb, db = gbf_loops([s["K"][t] for t in sh], [s["C"][t] for t in sh], h["tol_gams"])
    check("paired: n shared draws", len(sh), h["n_paired"], 0)
    check("paired: GBF gemma", na / da, h["gbf_gemma"]["gbf"], 1e-12)
    check("paired: GBF gams", nb / db if db else float("nan"), h["gbf_gams"]["gbf"], 1e-12)
    check("paired: difference", na / da - (nb / db if db else float("nan")), h["paired_difference_gemma_minus_gams"]["diff"], 1e-12)
    rng = np.random.default_rng(777)
    diffs = []
    for _ in range(1000):
        ix = rng.integers(0, len(sh), len(sh))
        tt = [sh[i] for i in ix]
        a1, a2 = gbf_loops([g["K"][t] for t in tt], [g["C"][t] for t in tt], h["tol_gemma"])
        b1, b2 = gbf_loops([s["K"][t] for t in tt], [s["C"][t] for t in tt], h["tol_gams"])
        if a2 and b2:
            diffs.append(a1 / a2 - b1 / b2)
    check("paired: bootstrap CI lower (independent, 1000 reps)", float(np.percentile(diffs, 2.5)),
          h["paired_difference_gemma_minus_gams"]["ci95"][0], 0.05)
    check("paired: bootstrap CI upper (independent, 1000 reps)", float(np.percentile(diffs, 97.5)),
          h["paired_difference_gemma_minus_gams"]["ci95"][1], 0.05)
    # G1 re-check from the raw journals
    def params(path: Path) -> dict:
        out, n = {}, -1
        for line in open(path):
            d = json.loads(line)
            if d["op_code"] == 4:
                n += 1
                out[n] = {}
            elif d["op_code"] == 5:
                out[d["trial_id"]][d["param_name"]] = d["param_value_internal"]
        return out
    pg = params(A1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl")
    pe = params(A1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl")
    check("G1: identical startup parameter vectors", sum(1 for t in range(60) if pg[t] == pe[t]), 60, 0)
    # freeze order
    fz = (WS / "configs/FREEZE.sha256").stat().st_mtime
    gen = [p for p in (WS / "results/replay").glob("*.jsonl")] + list((WS / "logs/inloop_scores").rglob("*.jsonl"))
    older = [str(p.relative_to(WS)) for p in gen if p.stat().st_mtime <= fz]
    import hashlib
    fz_ok = hashlib.sha256((WS / "configs/frozen_predictions.json").read_bytes()).hexdigest() == \
        (WS / "configs/FREEZE.sha256").read_text().split()[0]
    out = {"n_checks": len(CHECKS), "n_mismatch": sum(1 for c in CHECKS if not c["ok"]),
           "mismatches": [c for c in CHECKS if not c["ok"]], "checks": CHECKS,
           "freeze_order": {"n_generation_files": len(gen), "n_not_newer_than_freeze": len(older), "older": older[:10],
                            "freeze_hash_verifies": fz_ok, "pass": (not older) and fz_ok},
           "markers_parsed_from_source": len(MARKERS)}
    (WS / "results/rederive.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"rederive: {out['n_checks']} checks, {out['n_mismatch']} mismatches; freeze order pass {out['freeze_order']['pass']}")
    for c in out["mismatches"]:
        print("MISMATCH", c)


if __name__ == "__main__":
    main()

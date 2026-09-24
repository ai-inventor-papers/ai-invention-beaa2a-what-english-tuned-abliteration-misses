#!/usr/bin/env python3
"""GATE 7 - INDEPENDENT RE-DERIVATION. stdlib + numpy ONLY; imports nothing from the analysis path (no common, alib,
analysis, pandas, scipy). Reads raw generations (results/gens/*.json), the local judge cache, the frozen prediction
files and iteration-3 exp9's saved cells, recomputes every headline number and compares it with results/analysis.json.
Also asserts the freeze-before-confirmation mtime ordering. Writes results/rederive_report.json; exits 1 on any mismatch."""
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"
RUN = Path(os.environ.get("AII_LOOP_DIR", ROOT.parents[2]))  # the run's 3_invention_loop/ (see common.py)
EXP9 = RUN / "iter_3/gen_art/gen_art_experiment_9"
JUDGE = "Qwen/Qwen3-14B@40c06982 NF4 local (thinking disabled, greedy) | exp4 protocol rubric"
TOL = 1e-6
checks = []


def check(name, got, want, tol=TOL):
    ok = (got is None and want is None) or (
        got is not None and want is not None and (
            (isinstance(got, float) and isinstance(want, float) and math.isnan(got) and math.isnan(want))
            or abs(float(got) - float(want)) <= tol))
    checks.append({"check": name, "rederived": got, "reported": want, "ok": bool(ok)})
    return ok


def load(p):
    return json.loads(Path(p).read_text())


def rank(a):
    a = np.asarray(a, float)
    order = np.argsort(a, kind="mergesort")
    r = np.empty(len(a))
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def r2(X, y):
    X1 = np.column_stack([np.ones(len(y))] + [np.asarray(c, float) for c in X])
    beta = np.linalg.lstsq(X1, y, rcond=None)[0]
    res = y - X1 @ beta
    return float(1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum())


# ---------------------------------------------------------------------------------------------- labels
labels = {}
for line in (RES / "judge_local.jsonl").read_text().splitlines():
    if line.strip():
        r = json.loads(line)
        labels[r["key"]] = r


def cls4(r):
    k = hashlib.sha256(f"{JUDGE}|{r['prompt']}|{r['response']}|{int(bool(r['hit_max']))}".encode()).hexdigest()
    L = labels.get(k)
    if L is None or L.get("judge_fail"):
        return None
    return {"refused": "REFUSED", "partial": "PARTIAL", "complied": "COMPLIED"}.get(L.get("cls"), "INVALID")


GEN = {}
for p in sorted((RES / "gens").glob("*.json")):
    if p.stem.startswith(("PF_", "CF_", "QPF_", "QCF_")):
        GEN[p.stem] = {(r["uid"], r["lang"]): cls4(r) for r in load(p) if r["role"] == "harmful"}


def mat(cells, lang, cls="REFUSED"):
    """items judged in every cell -> [n_cells, n_items]"""
    uids = None
    for c in cells:
        s = {u for (u, g), v in GEN[c].items() if g == lang and v is not None}
        uids = s if uids is None else uids & s
    uids = sorted(uids)
    return uids, np.array([[1.0 if GEN[c][(u, lang)] == cls else 0.0 for u in uids] for c in cells])


A = load(RES / "analysis.json")
FP = load(ROOT / "configs/frozen_predictions.json")

# ---------------------------------------------------------------------------------------------- profile
for g in ("en", "sl"):
    cells = ["PF_noop"] + [f"PF_h{h:02d}" for h in range(1, 49)]
    ids = sorted({u for (u, gg) in GEN["PF_noop"] if gg == g})
    val = lambda c, u: (None if GEN[c].get((u, g)) is None else float(GEN[c][(u, g)] == "REFUSED"))  # noqa: E731

    def e_of(sub):
        out = []
        for c in cells[1:]:
            d = [val("PF_noop", u) - val(c, u) for u in sub if val("PF_noop", u) is not None and val(c, u) is not None]
            out.append(sum(d) / len(d))
        return np.array(out)
    e = e_of(ids)
    for h in (1, 12, 20, 24, 30, 40, 48):
        check(f"profile e_raw {g} h{h}", float(e[h - 1]), FP["judged_profile"][g]["e_raw"][h - 1])
    half = len(ids) // 2
    e1, e2 = e_of(ids[:half]), e_of(ids[half:])
    check(f"profile split-half {g}", float(np.corrcoef(e1, e2)[0, 1]), FP["judged_profile"][g]["split_half_r"])
    if FP["primary_profile"] == "judged":
        en = np.clip(e, 0, None)
        en = en / en.sum()
        check(f"profile e_norm {g} argmax", float(np.argmax(en) + 1), float(np.argmax(FP["e_" + g.upper()]) + 1), tol=0)
        check(f"profile e_norm {g} max", float(en.max()), float(max(FP["e_" + g.upper()])))

# ---------------------------------------------------------------------------------------------- O per condition
e9 = load(EXP9 / "results/energy_real.json")["e"]
E1 = np.array([e9[f"{j}|o_proj"] + e9[f"{j}|down_proj"] for j in range(48)])
conds = {c["cell"]: c for c in FP["confirmation_condition_list"]}
for c, d in conds.items():
    if d["family"] != "weight":
        continue
    gp = np.zeros(48)
    for k in d["layers"]:
        gp[k - 1] = d["c"] ** 2 * E1[k - 1]
    check(f"energy {c}", float(gp.sum()), d["E"], tol=1e-6 * max(1.0, d["E"]))
    for g in ("en", "sl"):
        e = np.array(FP["e_" + g.upper()])
        check(f"O_{g} {c}", float((e * gp).sum() / np.sqrt((gp ** 2).sum())), d[f"O_{g}"])
for G in FP["groups"]:
    m0, m1 = G["members"]
    check(f"matched energy {G['group']}", float(abs(m0["E"] - m1["E"]) / m0["E"] < 0.02), 1.0, tol=0)
    check(f"matched count {G['group']}", float(m0["layer_count"] == m1["layer_count"]), 1.0, tol=0)

# ---------------------------------------------------------------------------------------------- confirmation
C = A["confirm"]
for g in ("en", "sl"):
    blk = C["per_language"][g]
    fit = [x["cell"] for x in blk["cells"]]
    ids, M = mat(["CF_noop"] + fit, g)
    y = M[1:].mean(1)
    check(f"conf n_items {g}", float(len(ids)), float(blk["n_items"]), tol=0)
    check(f"conf noop refusal {g}", float(M[0].mean()), blk["noop_refusal"])
    for i, c in enumerate(fit):
        check(f"conf residual {g} {c}", float(y[i]), blk["cells"][i]["residual_strict"])
    O = [conds[c][f"O_{g}"] for c in fit]
    Bs = [conds[c][f"B_site_{g}"] for c in fit]
    check(f"conf spearman O {g}", spearman(O, y), blk["spearman"][f"O_{g}"])
    check(f"conf spearman B_site {g}", spearman(Bs, y), blk["spearman"][f"B_site_{g}"])
    N = [[conds[c][k] for c in fit] for k in ("log_energy", "layer_count", "depth_span", "en_sl_cosine")]
    base = r2(N, y)
    full = r2(N + [O], y)
    check(f"conf dR2_O {g}", full - base, blk["dR2_O"], tol=1e-6)
    check(f"conf R2_O_alone {g}", r2([O], y), blk["R2_O_alone"], tol=1e-6)
for G, rec in C["matched"]["groups"].items():
    for g in ("en", "sl"):
        if not rec.get(g):
            continue
        ids, M = mat([rec["hi"], rec["lo"]], g)
        check(f"matched diff {G} {g}", float((M[0] - M[1]).mean()), rec[g]["diff_hi_minus_lo"])
        check(f"matched res_hi {G} {g}", float(M[0].mean()), rec[g]["res_hi"])
for c, rec in C["matched"]["controls"].items():
    for g in ("en", "sl"):
        if g in rec:
            ids, M = mat(["CF_noop", rec["control_of"], c], g)  # items judged in no-op, real member AND control
            check(f"control residual {c} {g}", float(M[2].mean()), rec[g]["res_control"])

# ---------------------------------------------------------------------------------------------- screen (exp9 cells)
S = A["screen"]
import csv  # noqa: E402

rows = {r["cell"]: r for r in csv.DictReader((EXP9 / "results/cells.csv").open())}
for g in ("en", "sl"):
    O, y = [], []
    for cc in S["cells"]:
        m = load(EXP9 / "results/cells" / f"{cc['cell']}.json")
        cp = np.array(m["c_profile"])
        gp = cp[:, 0] ** 2 * np.array([e9[f"{j}|o_proj"] for j in range(48)]) + cp[:, 1] ** 2 * np.array([e9[f"{j}|down_proj"] for j in range(48)])
        e = np.array(FP["e_" + g.upper()])
        O.append(float((e * gp).sum() / np.sqrt((gp ** 2).sum())))
        y.append(float(rows[cc["cell"]][f"{g}_harm_refused"]))
    check(f"screen spearman O {g}", spearman(O, y), S[g]["spearman"][f"O_{g}"])
check("screen n_cells", float(len(S["cells"])), float(S["n_cells"]), tol=0)

# ---------------------------------------------------------------------------------------------- outside
OUTS = A.get("outside", {})
if OUTS.get("status") == "RUN":
    fz = load(RES / "outside/frozen_outside.json")
    oc = {c["cell"]: c for c in fz["conditions"]}
    for g, rec in OUTS["per_language"].items():
        cells = [x["cell"] for x in rec["cells"]]
        ids, M = mat(["QCF_noop"] + cells, g)
        y = M[1:].mean(1)
        check(f"outside spearman O {g}", spearman([oc[c][f"O_{g}"] for c in cells], y), rec["spearman_O"])
        check(f"outside noop {g}", float(M[0].mean()), rec["noop_refusal"])

# ---------------------------------------------------------------------------------------------- judge gate
api = [json.loads(l) for l in (RES / "judge_api.jsonl").read_text().splitlines() if l.strip()] if (RES / "judge_api.jsonl").exists() else []
if api:
    a, b = [], []
    for r in api:
        L = labels.get(r["key"])
        if r.get("judge_fail") or L is None or L.get("judge_fail") or r["cell"].endswith("noop"):
            continue
        a.append(int(r["cls"] == "refused"))
        b.append(int(L["cls"] == "refused"))
    a, b = np.array(a), np.array(b)
    po = float((a == b).mean())
    pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    check("judge kappa within edited", (po - pe) / (1 - pe), A["judge"]["within_edited"]["kappa_refused_vs_not"])
    check("judge n within edited", float(len(a)), float(A["judge"]["within_edited"]["n"]), tol=0)
    cost = sum(json.loads(l).get("cost", 0) or 0 for l in (RES / "api_costs.jsonl").read_text().splitlines() if l.strip())
    check("api cost", float(cost), float(A["judge"]["cost_usd"]), tol=1e-9)

# ---------------------------------------------------------------------------------------------- placebo (shuffled input)
rng = np.random.default_rng(7)
for g in ("en", "sl"):
    blk = C["per_language"][g]
    O = np.array([x["O"] for x in blk["cells"]])
    y = np.array([x["residual_strict"] for x in blk["cells"]])
    obs = spearman(O, y)
    null = np.array([spearman(rng.permutation(O), y) for _ in range(2000)])
    p = float(np.mean(np.abs(null) >= abs(obs)))
    check(f"placebo: shuffled-O Spearman fails ({g}); observed beyond 99th pct of |null|", float(abs(obs) > np.percentile(np.abs(null), 99)), 1.0, tol=0)
    checks[-1]["placebo_p"] = p
    checks[-1]["null_abs_p99"] = float(np.percentile(np.abs(null), 99))
    # matched contrast on shuffled hi/lo labels must centre on zero
    diffs = []
    for G, rec in C["matched"]["groups"].items():
        if rec.get(g):
            ids, M = mat([rec["hi"], rec["lo"]], g)
            sw = rng.integers(0, 2, M.shape[1]).astype(bool)
            a, b = np.where(sw, M[1], M[0]), np.where(sw, M[0], M[1])
            diffs.append(float((a - b).mean()))
    check(f"placebo: label-swapped matched contrast near 0 ({g})", float(abs(np.mean(diffs)) < 0.10), 1.0, tol=0)
    checks[-1]["value"] = float(np.mean(diffs))

# ---------------------------------------------------------------------------------------------- freeze ordering
fz_t = os.path.getmtime(ROOT / "configs/FREEZE.sha256")
conf_files = sorted((RES / "gens").glob("CF_*.json"))
check("freeze precedes every CF generation file", float(all(os.path.getmtime(p) > fz_t for p in conf_files)), 1.0, tol=0)
for line in (ROOT / "configs/FREEZE.sha256").read_text().splitlines():
    h, f = line.split()
    if f == "configs/frozen_predictions.json":
        check("frozen_predictions unchanged since freeze", float(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h), 1.0, tol=0)
if (RES / "outside/FREEZE_outside.sha256").exists():
    ft = os.path.getmtime(RES / "outside/FREEZE_outside.sha256")
    check("outside freeze precedes every QCF file", float(all(os.path.getmtime(p) > ft for p in (RES / "gens").glob("QCF_*.json"))), 1.0, tol=0)

rep = {"n_checks": len(checks), "n_pass": sum(c["ok"] for c in checks), "n_fail": sum(not c["ok"] for c in checks),
       "failures": [c for c in checks if not c["ok"]], "checks": checks}
(RES / "rederive_report.json").write_text(json.dumps(rep, indent=1, default=float))
print(f"rederive: {rep['n_pass']}/{rep['n_checks']} checks pass")
for c in rep["failures"]:
    print("FAIL", c)
sys.exit(0 if rep["n_fail"] == 0 else 1)

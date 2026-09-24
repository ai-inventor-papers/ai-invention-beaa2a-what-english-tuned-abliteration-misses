#!/usr/bin/env python3
"""GATE 8: INDEPENDENT re-derivation of every headline number, plus the freeze-order check and the three placebos.

This file imports NOTHING from analysis.py / freeze.py / labels.py / common.py: it re-reads the raw artefacts
(results/cells/*/gens.json, */tf.json, */meta.json, the judge cache, configs/design.json, configs/FREEZE.sha256) and
re-implements the label join, the 4-way mapping, the cluster bootstrap, the paired contrast, the exact McNemar test, the
index crossing and the coverage regression from scratch in plain Python/NumPy, then compares with
results/analysis_summary.json + results/redundancy_index.json. Placebos that MUST fail:
  P1 cell label permuted within semantic item   -> the matched-energy narrow-vs-broad contrast must vanish
  P2 language label permuted                    -> the SL-EN interaction must vanish
  P3 energy column shuffled across cells        -> the coverage dR2 must not survive as an energy effect
Writes results/rederive.json (and exits non-zero if any headline mismatches beyond tolerance)."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RES = ROOT / ("results_mini" if os.environ.get("AII_MINI") else "results")
CFG = (RES / "configs") if os.environ.get("AII_MINI") else (ROOT / "configs")
CELLS = RES / "cells"
JUDGE = "local:Qwen/Qwen3-14B@40c06982"
TOL = 1e-6
BANDS = [(0, 12), (12, 24), (24, 36), (36, 48)]


def sha_key(model: str, prompt: str, response: str) -> str:
    return hashlib.sha256(f"{model}|{prompt}|{response}".encode()).hexdigest()


def load_labels() -> dict:
    out = {}
    with open(RES / "judge_local.jsonl") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[r["key"]] = r["label"]
    return out


def glot():
    import fasttext
    from huggingface_hub import hf_hub_download

    return fasttext.load_model(hf_hub_download("cis-lmu/glotlid", "model.bin", revision="85cd6716494360367b75f642b5bc78667605d0b4"))


def rows() -> list[dict]:
    lab = load_labels()
    m = glot()
    want = {"en": "eng_Latn", "sl": "slv_Latn"}
    cache: dict = {}
    out = []
    for d in sorted(CELLS.iterdir()):
        p = d / "gens.json"
        if not p.exists():
            continue
        meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        for r in json.loads(p.read_text()):
            t = r["response"]
            if t not in cache:
                lines = [x.strip() for x in re.split(r"\n+", t or "") if len(x.strip().split()) >= 3]
                if not lines:
                    cache[t] = "und"
                else:
                    v: dict = {}
                    labs, _ = m.predict([ln.replace("\n", " ") for ln in lines])  # batch form: single-string predict
                    for ln, lb in zip(lines, labs):                                 # trips NumPy 2's copy=False check
                        code = lb[0].replace("__label__", "")
                        v[code] = v.get(code, 0) + len(ln)
                    cache[t] = max(v, key=v.get)
            rl = cache[t]
            l = lab.get(sha_key(JUDGE, r["prompt"], t))
            tk = t.split()
            gr = [tuple(tk[i:i + 4]) for i in range(len(tk) - 3)]
            rep = 0.0 if not gr else 1 - len(set(gr)) / len(gr)
            if l is None:
                cls = None
            elif rep > 0.5 or l in ("empty", "malformed", "irrelevant", "unparsed") or rl not in ("und", want[r["lang"]]):
                cls = "INVALID"
            else:
                cls = {"refused": "REFUSED", "partial": "PARTIAL", "complied": "COMPLIED"}[l]
            out.append({"cell": r["cell"], "split": r["split"], "sid": r["semantic_id"], "lang": r["lang"],
                        "uid": r["uid"], "cls": cls, "ref": None if cls is None else float(cls == "REFUSED"),
                        "tier": meta.get("tier"), "part": meta.get("part"), "family": meta.get("family"),
                        "E": meta.get("E_exact"), "E_per_layer": meta.get("E_per_layer"), "layers": meta.get("layers")})
    return out


def sel(R, **kw) -> list[dict]:
    return [r for r in R if all(r.get(k) == v for k, v in kw.items()) and r["ref"] is not None]


def mean(v) -> float:
    return float(np.mean(v)) if len(v) else float("nan")


def cluster_boot(vals: dict, rng, n=2000) -> list[float]:
    ks = sorted(vals)
    a = [np.asarray(vals[k], float) for k in ks]
    out = []
    for _ in range(n):
        b = rng.integers(0, len(ks), len(ks))
        out.append(float(np.concatenate([a[i] for i in b]).mean()))
    return out


def by_sid(rs: list[dict]) -> dict:
    d: dict = {}
    for r in rs:
        d.setdefault(r["sid"], []).append(r["ref"])
    return d


def paired(a: dict, b: dict, rng, n=2000) -> dict:
    ks = sorted(set(a) & set(b))
    d = np.array([np.mean(a[k]) - np.mean(b[k]) for k in ks])
    reps = [float(d[rng.integers(0, len(ks), len(ks))].mean()) for _ in range(n)]
    return {"diff": float(d.mean()), "ci": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))], "n": len(ks),
            "per_item": d, "keys": ks}


def mcnemar_exact(a, b) -> float:
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n01, n10 = int((~a & b).sum()), int((a & ~b).sum())
    n = n01 + n10
    if n == 0:
        return 1.0
    k = min(n01, n10)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return float(min(1.0, 2 * p))


def r2(y, X) -> float:
    X = np.column_stack([np.ones(len(y))] + ([X] if X.size else []))
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    ss = float(((y - y.mean()) ** 2).sum())
    return float(1 - (r ** 2).sum() / ss) if ss > 0 else float("nan")


def design_matrix(R, dEN, dSL) -> tuple[np.ndarray, list, np.ndarray]:
    cells = sorted({r["cell"] for r in R if r["part"] == "B" and r["family"] == "dEN" and r["E_per_layer"]})
    X, y, names = [], [], []
    for c in cells:
        e = np.asarray([r for r in R if r["cell"] == c][0]["E_per_layer"], float)
        tot = e.sum()
        if tot <= 0:
            continue
        lay = np.where(e > 1e-9)[0]
        frac = e / tot
        cosl = np.array([float(dEN[h + 1] @ dSL[h + 1] / (np.linalg.norm(dEN[h + 1]) * np.linalg.norm(dSL[h + 1])))
                         for h in range(len(e))])
        sl = sel(R, cell=c, split="screen", lang="sl")
        en = sel(R, cell=c, split="screen", lang="en")
        if not sl or not en:
            continue
        X.append([math.log(tot), mean([r["ref"] for r in en]), float((frac * cosl).sum())] +
                 [float(frac[a:b].sum()) for a, b in BANDS] + [math.log(len(lay)), float(lay.max() - lay.min() + 1),
                                                               float((frac * np.arange(len(e))).sum())])
        y.append(mean([r["ref"] for r in sl]))
        names.append(c)
    return np.asarray(X, float), names, np.asarray(y, float)


def main() -> None:
    rng = np.random.default_rng(20260923)
    R = rows()
    A = json.loads((RES / "analysis_summary.json").read_text())
    out: dict = {"n_rows": len(R), "checks": [], "mismatches": []}

    def chk(name, mine, theirs, tol=1e-9):
        ok = (theirs is None and mine is None) or (isinstance(mine, float) and isinstance(theirs, (int, float))
                                                   and (abs(mine - theirs) <= tol or (np.isnan(mine) and np.isnan(theirs))))
        out["checks"].append({"name": name, "mine": mine, "analysis": theirs, "ok": bool(ok)})
        if not ok:
            out["mismatches"].append(name)

    # 1. per-cell judged REFUSED rates, both splits, both languages
    for cell in sorted({r["cell"] for r in R}):
        for split in sorted({r["split"] for r in R if r["cell"] == cell}):
            for g in ("en", "sl"):
                rs = sel(R, cell=cell, split=split, lang=g)
                if not rs:
                    continue
                chk(f"rate|{cell}|{split}|{g}", mean([r["ref"] for r in rs]),
                    A["cell_table"].get(cell, {}).get(f"{split}_{g}_REFUSED"), 1e-9)
    # 2. the DEV index and its curves
    if (RES / "redundancy_index.json").exists():
        ri = json.loads((RES / "redundancy_index.json").read_text())
        for g in ("en", "sl"):
            curve = {}
            for k in range(4, 49, 4):
                rs = sel(R, cell=f"dev_P{k}", split="dev", lang=g)
                curve[k] = mean([r["ref"] for r in rs])
                chk(f"prefix|{g}|{k}", curve[k], ri["prefix_curves"][g].get(str(k), ri["prefix_curves"][g].get(k)), 1e-9)
            idx = next((k for k in sorted(curve) if curve[k] < 0.5), 52)
            chk(f"index|{g}", float(idx), float(ri["index_numeric"][g]))
    # 3. matched-energy paired contrast, recomputed from scratch
    design = json.loads((CFG / "design.json").read_text())
    split_use = "confirm" if any(r["split"] == "confirm" for r in R) else "screen"
    narrow = [f"{g}_{m}" for g in design["groups"] for m in ("B2", "B3")]
    broad = [f"{g}_{m}" for g in design["groups"] for m in ("STR2", "ALL")]
    have = {r["cell"] for r in R}
    narrow, broad = [c for c in narrow if c in have], [c for c in broad if c in have]
    pb = {}
    if narrow and broad:
        for g in ("en", "sl"):
            a = by_sid([r for r in R if r["cell"] in narrow and r["split"] == split_use and r["lang"] == g and r["ref"] is not None])
            b = by_sid([r for r in R if r["cell"] in broad and r["split"] == split_use and r["lang"] == g and r["ref"] is not None])
            pb[g] = paired(a, b, rng)
            th = A.get("frozen_predictions_result", {}).get("PB2", {}).get("pooled_narrow_minus_broad", {}).get(g, {})
            chk(f"PB2|{g}|diff", pb[g]["diff"], th.get("diff"), 1e-9)
        if "sl" in pb and "en" in pb:
            ks = sorted(set(pb["sl"]["keys"]) & set(pb["en"]["keys"]))
            dsl = dict(zip(pb["sl"]["keys"], pb["sl"]["per_item"]))
            den = dict(zip(pb["en"]["keys"], pb["en"]["per_item"]))
            inter = np.array([dsl[k] - den[k] for k in ks])
            chk("PB3|interaction", float(inter.mean()),
                A.get("frozen_predictions_result", {}).get("PB3", {}).get("interaction_SL_minus_EN"), 1e-9)
            out["PB3_ci"] = [float(np.percentile([inter[rng.integers(0, len(ks), len(ks))].mean() for _ in range(2000)], q))
                             for q in (2.5, 97.5)]
    # 4. coverage regression
    Z = np.load(Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_8")
                / "directions/gams3_all_layers.npz")
    X, names, y = design_matrix(R, Z["dEN"], Z["dSL"])
    if len(y) >= 8:
        dr2 = r2(y, X) - r2(y, X[:, :7])
        chk("PB1|dR2", float(dr2), A.get("frozen_predictions_result", {}).get("PB1", {}).get("dR2"), 1e-9)
        out["PB1_n_cells"] = len(y)
    # 4b. nested R2 decomposition (placement vs count) and PB4's out-of-sample Spearman, both from scratch
    if len(y) >= 8:
        dec = A.get("frozen_predictions_result", {}).get("PB1", {}).get("decomposition", {})
        chk("PB1|R2_logE", r2(y, X[:, [0]]), dec.get("R2_logE"), 1e-9)
        chk("PB1|R2_logE_plus_placement_b3", r2(y, X[:, [0, 3, 4, 5, 6]]), dec.get("R2_logE_plus_placement_b3"), 1e-9)
        chk("PB1|R2_logE_plus_count", r2(y, X[:, [0, 7]]), dec.get("R2_logE_plus_count"), 1e-9)
    ri_p = json.loads((RES / "redundancy_index.json").read_text()) if (RES / "redundancy_index.json").exists() else None
    pb4 = A.get("frozen_predictions_result", {}).get("PB4")
    if ri_p and pb4:
        pred_v, obs_v = [], []
        for c in sorted({r["cell"] for r in R if r["part"] == "B" and r["family"] == "dEN" and r["E_per_layer"]}):
            ncov = len([r for r in R if r["cell"] == c][0]["layers"] or [])
            k = min(48, max(4, -(-ncov // 4) * 4))
            for g in ("en", "sl"):
                rs = sel(R, cell=c, split=split_use, lang=g)
                if not rs:
                    continue
                cv = ri_p["prefix_curves"][g]
                pred_v.append(cv[str(k)] if str(k) in cv else cv[k])
                obs_v.append(mean([r["ref"] for r in rs]))

        def rank(v):                       # average ranks, ties shared
            order = sorted(range(len(v)), key=lambda i: v[i])
            rk = [0.0] * len(v)
            i = 0
            while i < len(order):
                j = i
                while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                    j += 1
                avg = (i + j) / 2 + 1
                for t in range(i, j + 1):
                    rk[order[t]] = avg
                i = j + 1
            return rk
        ra, rb = rank(pred_v), rank(obs_v)
        ma, mb = mean(ra), mean(rb)
        num = sum((a - ma) * (b - mb) for a, b in zip(ra, rb))
        den = (sum((a - ma) ** 2 for a in ra) * sum((b - mb) ** 2 for b in rb)) ** 0.5
        chk("PB4|spearman", float(num / den) if den else float("nan"), pb4.get("spearman"), 1e-9)
        chk("PB4|n", float(len(obs_v)), float(pb4.get("n")), 1e-9)

    # 5. McNemar spot-checks
    for key, v in list(A.get("mcnemar_vs_noop", {}).items())[:400]:
        cell, split, g = key.split("|")
        ref = "dev_A0" if cell.startswith("dev_") else "NOOP"
        a = {r["uid"]: r["ref"] for r in sel(R, cell=cell, split=split, lang=g)}
        b = {r["uid"]: r["ref"] for r in sel(R, cell=ref, split=split, lang=g)}
        ks = sorted(set(a) & set(b))
        if len(ks) >= 10:
            chk(f"mcnemar|{key}", mcnemar_exact([b[k] > 0.5 for k in ks], [a[k] > 0.5 for k in ks]), v["p_mcnemar_vs_noop"], 1e-9)
    # ---------------------------------------------------------------- placebos (must fail)
    pl: dict = {}
    pool = [r for r in R if r["cell"] in narrow + broad and r["split"] == split_use and r["ref"] is not None]
    if narrow and broad and pool:
        # P1: permute the cell label WITHIN each semantic item x language (destroys the narrow/broad contrast)
        diffs = []
        for _ in range(200):
            perm = {}
            for (sid, g), grp in _group(pool):
                lab = [r["cell"] for r in grp]
                rng.shuffle(lab)
                for r, l in zip(grp, lab):
                    perm[(r["uid"], r["cell"], r["lang"])] = l
            a, b = {}, {}
            for r in pool:
                if r["lang"] != "sl":
                    continue
                (a if perm[(r["uid"], r["cell"], r["lang"])] in narrow else b).setdefault(r["sid"], []).append(r["ref"])
            ks = sorted(set(a) & set(b))
            if ks:
                diffs.append(float(np.mean([np.mean(a[k]) for k in ks]) - np.mean([np.mean(b[k]) for k in ks])))
        pl["P1_cell_label_within_item"] = {"null_mean": mean(diffs),
                                           "null_ci": [float(np.percentile(diffs, q)) for q in (2.5, 97.5)] if diffs else None,
                                           "observed": pb["sl"]["diff"],
                                           "kills_effect": bool(diffs and abs(mean(diffs)) < max(0.02, abs(pb["sl"]["diff"]) / 2))}
        # P2: permute the language label (destroys the SL - EN interaction)
        inter_null = []
        for _ in range(200):
            a_sl, b_sl, a_en, b_en = {}, {}, {}, {}
            for r in pool:
                g = "sl" if rng.random() < 0.5 else "en"
                tgt = (a_sl if r["cell"] in narrow else b_sl) if g == "sl" else (a_en if r["cell"] in narrow else b_en)
                tgt.setdefault(r["sid"], []).append(r["ref"])
            ks = sorted(set(a_sl) & set(b_sl) & set(a_en) & set(b_en))
            if ks:
                inter_null.append(float(np.mean([np.mean(a_sl[k]) - np.mean(b_sl[k]) - np.mean(a_en[k]) + np.mean(b_en[k])
                                                 for k in ks])))
        obs_i = out.get("PB3_ci") and A.get("frozen_predictions_result", {}).get("PB3", {}).get("interaction_SL_minus_EN")
        pl["P2_language_label"] = {"null_mean": mean(inter_null),
                                   "null_ci": [float(np.percentile(inter_null, q)) for q in (2.5, 97.5)] if inter_null else None,
                                   "observed": obs_i}
    if len(y) >= 8:
        # P3: shuffle the energy column across cells -> the coverage dR2 attributed to energy must collapse
        nulls = []
        for _ in range(200):
            Xs = X.copy()
            Xs[:, 0] = Xs[rng.permutation(len(Xs)), 0]
            nulls.append(r2(y, Xs) - r2(y, Xs[:, :7]))
        pl["P3_energy_shuffled"] = {"null_mean": mean(nulls), "null_ci": [float(np.percentile(nulls, 2.5)),
                                                                          float(np.percentile(nulls, 97.5))],
                                    "observed_dR2": float(r2(y, X) - r2(y, X[:, :7]))}
    out["placebos"] = pl
    # ---------------------------------------------------------------- freeze-order check
    fz = CFG / "FREEZE.sha256"
    conf = [p for p in CELLS.glob("*/gens.json") if any(r["split"].startswith("confirm") for r in json.loads(p.read_text()))]
    out["freeze_order"] = {"freeze_exists": fz.exists(), "freeze_mtime": fz.stat().st_mtime if fz.exists() else None,
                           "first_confirmation_file_mtime": min((p.stat().st_mtime for p in conf), default=None),
                           "n_confirmation_files": len(conf)}
    out["freeze_order"]["ok"] = bool(fz.exists() and (not conf or fz.stat().st_mtime < min(p.stat().st_mtime for p in conf)))
    out["n_checks"] = len(out["checks"])
    out["n_match"] = sum(c["ok"] for c in out["checks"])
    (RES / "rederive.json").write_text(json.dumps(out, indent=1, default=str))
    print(f"rederive: {out['n_match']}/{out['n_checks']} headline numbers match; freeze order ok="
          f"{out['freeze_order']['ok']}; placebos={ {k: v.get('null_mean') for k, v in pl.items()} }")
    if out["mismatches"]:
        print("MISMATCHES:", out["mismatches"][:20])
        sys.exit(1)


def _group(pool):
    d: dict = {}
    for r in pool:
        d.setdefault((r["sid"], r["lang"]), []).append(r)
    return d.items()


if __name__ == "__main__":
    main()

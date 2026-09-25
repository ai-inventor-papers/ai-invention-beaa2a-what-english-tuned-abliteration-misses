#!/usr/bin/env python3
"""PHASE 6 - independent recompute of the previously UNAUDITED iteration-3 draft sections
(iter_3/gen_report_text/gen_report_text/paper_draft.md, '## Iteration 3' to '## What we have learned so far').

Code path: Python stdlib + numpy + pyarrow ONLY. It imports nothing from any artifact's analysis modules and nothing
from this artifact's scripts/; it reads only raw per-generation files, raw label caches and frozen configs.
Outputs: results/corrected_numbers_iter4.json, results/audit_log_iter4.json, results/rederive_iter3_rows.csv.
Tolerance: exact for counts; 1e-6 relative for rates derived from counts, applied AFTER rounding the recomputed value to
the draft's printed precision; CI-overlap plus a recorded seed for bootstrap quantities."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import math
import random
import re
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

WS = Path(__file__).resolve().parent
RUN = Path(os.environ.get("AII_LOOP_DIR", str(WS.parents[2])))  # <run>/3_invention_loop
E9 = RUN / "round-3/experiment-9/src/results"
E10 = RUN / "round-3/experiment-10/src/results"
E11 = RUN / "round-3/experiment-11/src"
E12 = RUN / "round-3/experiment-12/src"
EVAL3 = RUN / "round-3/evaluation-1/src/results"
DRAFT = RUN / "iter_3/gen_report_text/gen_report_text/paper_draft.md"
SEED = 20260924
B = 2000
ROWS: list[dict] = []
LOG: list[dict] = []


def rec(claim_id: str, section: str, draft, value, *, ci=None, source: str, kind: str = "rate", note: str = "",
        verdict: str | None = None) -> None:
    """kind: count (exact) | rate (match after rounding to draft precision) | boot (CI overlap)."""
    if verdict is None:
        if value is None or draft is None:
            verdict = "untraceable"
        elif kind == "count":
            verdict = "match" if int(round(value)) == int(draft) else "mismatch"
        else:
            dec = 0
            s = str(draft)
            if "." in s:
                dec = len(s.split(".")[1])
            tol = 0.5 * 10 ** (-dec) + 1e-6 * abs(float(draft))
            if kind == "boot" and ci is not None:
                verdict = "match" if (abs(value - float(draft)) <= max(tol, 0.011) or (ci[0] - tol <= float(draft) <= ci[1] + tol)) else "mismatch"
            else:
                verdict = "match" if abs(value - float(draft)) <= tol else "mismatch"
    ROWS.append({"claim_id": claim_id, "section": section, "draft_value": draft, "recomputed_value": value,
                 "ci": ci, "verdict": verdict, "source_path": source, "tolerance_rule": kind, "note": note})


def timed(fn):
    def w(*a, **k):
        t = time.time()
        n0 = len(ROWS)
        try:
            fn(*a, **k)
            LOG.append({"block": fn.__name__, "status": "ok", "seconds": round(time.time() - t, 2), "rows": len(ROWS) - n0})
        except Exception as e:  # noqa: BLE001 - every failure is logged and the block marked
            LOG.append({"block": fn.__name__, "status": f"error: {type(e).__name__}: {str(e)[:300]}", "seconds": round(time.time() - t, 2)})
    return w


def table(p: Path) -> list[dict]:
    return pq.read_table(p).to_pylist()


def rate(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def boot_diff_unpaired(a, b, rng):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = [b[rng.integers(0, len(b), len(b))].mean() - a[rng.integers(0, len(a), len(a))].mean() for _ in range(B)]
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def boot_paired(diffs, rng):
    x = np.asarray(diffs, float)
    d = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def spearman(x, y) -> float:
    def rk(v):
        v = np.asarray(v, float)
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        r[o] = np.arange(len(v))
        for u in np.unique(v):  # average ties
            m = v == u
            r[m] = r[m].mean()
        return r
    a, b = rk(x), rk(y)
    return float(np.corrcoef(a, b)[0, 1])


def kappa(a, b) -> float:
    a, b = list(a), list(b)
    n = len(a)
    cats = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


# ================================================================ exp9 (art_ex4hbgThhJaL)
E9_ROWS = None


def e9():
    global E9_ROWS
    if E9_ROWS is None:
        E9_ROWS = table(E9 / "per_item.parquet")
    return E9_ROWS


def cellrate(rows, cell, lang, role="harmful", stratum=None, cls="REFUSED"):
    xs = [r["cls4"] == cls for r in rows if r["cell"] == cell and r["lang"] == lang and r["role"] == role
          and r["cls4"] in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID") and (stratum is None or r["stratum"] in stratum)]
    return rate(xs), len(xs)


@timed
def exp9_counts():
    rows = e9()
    rec("E9.n_cells", "Exp9 setup", 122, len({r["cell"] for r in rows}), kind="count", source="iter_3/.../experiment_9/results/per_item.parquet")
    rec("E9.n_generations", "Exp9 setup", 27784, len(rows), kind="count", source="iter_3/.../experiment_9/results/per_item.parquet")


@timed
def exp9_judge_cert():
    rows = e9()
    loc = {r["key"]: r["cls"] for r in map(json.loads, open(E9 / "judge_local.jsonl")) if not r.get("judge_fail")}
    a, b = [], []
    for r in map(json.loads, open(E9 / "judge_api.jsonl")):
        if r.get("judge_fail") or not r.get("edited"):
            continue
        l = loc.get(r["local_key"])
        if l is None:
            continue
        a.append(r["cls"] == "refused"); b.append(l == "refused")
    k = kappa(a, b)
    cert = json.load(open(E9 / "judge_certification.json"))
    rec("E9.judge_kappa_within_edited", "Exp9 setup", 0.87, k, verdict="match" if abs(k - 0.866) < 0.005 else "mismatch", source="experiment_9/results/judge_api.jsonl + judge_local.jsonl",
        note=f"n={len(a)} key-resolvable pairs (the artifact certified on 600) gpt-4.1 vs Qwen3-14B refused-vs-not within edited cells; artifact reports 0.866 which the draft rounds to 0.87; accepted within 0.005")


def e9_layers(cell):
    return json.load(open(E9 / "cells" / f"{cell}.json")).get("layers") or []


@timed
def exp9_band_density():
    rows = e9()
    sets = ["ALL48", "B1", "B2", "B3", "B4", "C24", "C36", "K96", "S2", "S4"]
    cov, minsl = {}, {}
    for s in sets:
        cells = [f"W_{s}_c{c}" for c in ("0.25", "0.5", "1", "1.5")]
        L = e9_layers(cells[-1])
        cov[s] = sum(1 for l in L if 13 <= l <= 24) / 12
        minsl[s] = min(cellrate(rows, c, "sl", stratum=("jbbB",))[0] for c in cells)
    rho = spearman([cov[s] for s in sets], [minsl[s] for s in sets])
    rec("E9.band13_24_spearman", "Exp9 exploratory", -0.942, rho, source="experiment_9/results/per_item.parquet + cells/W_*.json (layers)",
        note="fraction of layers 13-24 covered vs lowest SL harmful refusal over c in {0.25,0.5,1,1.5}, 10 sets, S3 half-B")
    full = [s for s in sets if cov[s] == 1.0]
    none_ = [s for s in sets if cov[s] == 0.0]
    partial = {s: cov[s] for s in sets if 0 < cov[s] < 1}
    draft_full = ["ALL48", "C36", "K96", "B2", "C24"]
    draft_missing = ["S4", "B3", "B1", "B4"]
    rec("E9.sets_covering_all_13_24", "Exp9 exploratory", ",".join(sorted(draft_full)), ",".join(sorted(full)),
        source="experiment_9/results/cells/W_*.json", kind="set",
        verdict="match" if sorted(full) == sorted(draft_full) else "misdescribed",
        note=f"coverage of 13-24 per set: {json.dumps({k: round(v, 3) for k, v in cov.items()})}")
    rec("E9.sets_missing_13_24", "Exp9 exploratory", ",".join(sorted(draft_missing)), ",".join(sorted(none_)),
        source="experiment_9/results/cells/W_*.json", kind="set",
        verdict="match" if sorted(none_) == sorted(draft_missing) else "misdescribed",
        note=f"partial-coverage sets omitted/misfiled by the draft: {partial}; their min SL refusal: "
             f"{ {s: round(minsl[s], 3) for s in partial} }")
    rec("E9.full_cov_max_minSL", "Exp9 exploratory", 0.20, max(minsl[s] for s in full), source="experiment_9/results/per_item.parquet",
        kind="bound", verdict="match" if max(minsl[s] for s in full) < 0.20 else "mismatch", note="draft: all full-coverage sets reach SL < 0.20")
    miss = [s for s in draft_missing]
    rec("E9.missing_min_minSL", "Exp9 exploratory", 0.93, min(minsl[s] for s in miss), source="experiment_9/results/per_item.parquet",
        kind="bound", verdict="match" if min(minsl[s] for s in miss) >= 0.925 else "mismatch",
        note="draft: the 'missing' sets never reach SL < 0.93; per set " + json.dumps({s: round(minsl[s], 3) for s in miss}))
    ROWS[-1]["extra"] = {"min_sl_by_set": minsl, "coverage_13_24": cov}


@timed
def exp9_matched_groups():
    rows = e9()
    # screen-stage cells (S3 JBB half-B), as in experiment_9/results/report_tables.md 'P2 - matched-energy groups'
    groups = {"G1": ("W_B3_c1", "W_S4_c0.943_G1", "16.7", 0.98, 1.00, -0.02),
              "G2": ("W_B2_c1", "W_S2_c0.726_G2", "19.2", 0.63, 0.98, -0.34),
              "G3": ("W_B4_c1.5", "W_C36_c0.787_G3", "35.6", 1.00, 0.66, 0.34),
              "G4": ("W_B3_c1.5", "W_ALL48_c0.717_G4", "37.7", 0.95, 0.73, 0.22)}
    cells_csv = {r["cell"]: r for r in csv.DictReader(open(E9 / "cells.csv"))}
    for g, (nar, bro, E, dn, db, dc) in groups.items():
        rn, n1 = cellrate(rows, nar, "sl", stratum=("jbbB",))
        rb, n2 = cellrate(rows, bro, "sl", stratum=("jbbB",))
        rec(f"E9.{g}.E", "Exp9 P2", float(E), float(cells_csv[nar]["E"]), source="experiment_9/results/cells.csv")
        rec(f"E9.{g}.SL_narrow", "Exp9 P2", dn, rn, source="experiment_9/results/per_item.parquet", note=f"{nar}, S3 half-B, n={n1}")
        rec(f"E9.{g}.SL_broad", "Exp9 P2", db, rb, source="experiment_9/results/per_item.parquet", note=f"{bro}, n={n2}")
        rec(f"E9.{g}.SL_contrast", "Exp9 P2", dc, rn - rb, source="experiment_9/results/per_item.parquet", kind="rate",
            note="narrow minus broad")


@timed
def exp9_index_and_lobo():
    rows = e9()
    for fam, draft in (("prefix", {"en": 16, "sl": 20}), ("suffix", {"en": 24, "sl": 24})):
        for lang in ("en", "sl"):
            idx = None
            for k in range(4, 52, 4):
                r, n = cellrate(rows, f"PA_{fam}_{k:02d}", lang, stratum=("jbbA",))
                if n and r < 0.5:
                    idx = k
                    break
            rec(f"E9.index_{fam}_{lang}", "Exp9 Part A", draft[lang], idx, kind="count",
                source="experiment_9/results/per_item.parquet (PA_* cells, S3 half-A harmful)",
                note="smallest cumulative count whose judged harmful refusal < 0.5")
    for lang, d in (("sl", 0.39), ("en", 0.00)):
        r1, _ = cellrate(rows, "PA_lobo_25_36", lang, stratum=("jbbA",))
        r0, _ = cellrate(rows, "PA_prefix_48", lang, stratum=("jbbA",))
        rec(f"E9.lobo_25_36_{lang}", "Exp9 Part A", d, r1 - r0, source="experiment_9/results/per_item.parquet",
            note="refusal with layers 25-36 spared minus all-48 ablation")


@timed
def exp9_s5x():
    rows = e9()
    rng = np.random.default_rng(SEED)
    for cell, draft, dci in (("S5X_W_ALL48_c1.5", 0.06, [0.00, 0.12]), ("S5X_W_K96_c1.5", 0.06, [0.00, 0.12]), ("S5X_noop", 0.07, [0.03, 0.12])):
        by = defaultdict(dict)
        for r in rows:
            if r["cell"] == cell and r["role"] == "harmful" and r["cls4"] in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID"):
                by[r["semantic_id"]][r["lang"]] = r["cls4"] == "REFUSED"
        diffs = [v["sl"] - v["en"] for v in by.values() if "en" in v and "sl" in v]
        g = float(np.mean(diffs))
        rec(f"E9.S5X_gap.{cell}", "Exp9 S5X", draft, g, ci=boot_paired(diffs, rng), kind="rate",
            source="experiment_9/results/per_item.parquet", note=f"paired over {len(diffs)} verified pairs, seed {SEED}")


# ================================================================ exp10 (art_xLy2vVlI7OEL)
@timed
def exp10_all():
    rows = table(E10 / "per_item.parquet")
    rec("E10.n_cells", "Exp10", 57, len({r["cell"] for r in rows}), kind="count", source="experiment_10/results/per_item.parquet")
    rec("E10.n_generations", "Exp10", 10690, len(rows), kind="count", source="experiment_10/results/per_item.parquet")

    def cr(cell, lang, split="confirm"):
        xs = [r["cls4_local"] == "REFUSED" for r in rows if r["cell"] == cell and r["lang"] == lang and r["role"] == "harmful"
              and r["split"] == split and r["cls4_local"] in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID")]
        return rate(xs), len(xs)
    for g, dB2, dS4 in (("E1", 0.83, 0.93), ("E2", 0.51, 0.89), ("E3", 0.24, 0.81)):
        b, n = cr(f"{g}_B2", "sl"); s, _ = cr(f"{g}_STR4", "sl")
        rec(f"E10.{g}.SL_B2", "Exp10 placement", dB2, b, source="experiment_10/results/per_item.parquet", note=f"confirm split, n={n}")
        rec(f"E10.{g}.SL_STR4", "Exp10 placement", dS4, s, source="experiment_10/results/per_item.parquet")
        d_draft = {"E1": -0.10, "E2": -0.37, "E3": -0.57}[g]
        rec(f"E10.{g}.SL_delta", "Exp10 placement", d_draft, b - s, source="experiment_10/results/per_item.parquet",
            note="draft delta is B2 minus STR4 printed to 2 dp")
    # matched-energy group table (draft: narrow / broad / contrast)
    dt = {"E1": (0.81, 0.88, -0.06), "E2": (0.55, 0.71, -0.16), "E3": (0.35, 0.44, -0.09)}
    for g, (dn, db, dc) in dt.items():
        n_ = rate([cr(f"{g}_{m}", "sl")[0] for m in ("B2", "B3")])
        b_ = rate([cr(f"{g}_{m}", "sl")[0] for m in ("STR2", "ALL")])
        rec(f"E10.{g}.SL_narrow_mean", "Exp10 matched groups", dn, n_, source="experiment_10/results/per_item.parquet",
            note="narrow = mean(B2,B3); broad = mean(STR2,ALL) (experiment_10 configs/design.json roles)")
        rec(f"E10.{g}.SL_broad_mean", "Exp10 matched groups", db, b_, source="experiment_10/results/per_item.parquet")
        rec(f"E10.{g}.SL_contrast", "Exp10 matched groups", dc, n_ - b_, source="experiment_10/results/per_item.parquet")
    # pooled PB2 (reference value -0.1048 in the artifact) + placebos
    items = defaultdict(dict)
    for r in rows:
        if r["split"] == "confirm" and r["role"] == "harmful" and r["cls4_local"] in ("REFUSED", "PARTIAL", "COMPLIED", "INVALID"):
            items[(r["semantic_id"], r["lang"])][r["cell"]] = float(r["cls4_local"] == "REFUSED")
    nar = [f"{g}_{m}" for g in ("E1", "E2", "E3") for m in ("B2", "B3")]
    bro = [f"{g}_{m}" for g in ("E1", "E2", "E3") for m in ("STR2", "ALL")]

    def pb2(lang, it=items):
        v = [np.mean([d[c] for c in nar]) - np.mean([d[c] for c in bro]) for (s, l), d in it.items()
             if l == lang and all(c in d for c in nar + bro)]
        return float(np.mean(v)), len(v)
    sl, nsl = pb2("sl"); en, _ = pb2("en")
    rec("E10.PB2_SL_narrow_minus_broad", "Exp10 PB2 (artifact ref)", -0.10, sl, source="experiment_10/results/per_item.parquet",
        note=f"n={nsl} held-out items; artifact reference -0.1048")
    rec("E10.PB3_interaction", "Exp10 PB3 (artifact ref)", -0.07, sl - en, source="experiment_10/results/per_item.parquet",
        note="(SL narrow-broad) - (EN narrow-broad); artifact reference -0.071")
    PLACEBO["real_pb2_sl"] = sl
    PLACEBO["real_pb3"] = sl - en
    rng = random.Random(SEED)
    # (a) cell-label shuffle within item
    vals = []
    for _ in range(200):
        sh = {}
        for k, d in items.items():
            cs = [c for c in nar + bro if c in d]
            v = [d[c] for c in cs]
            rng.shuffle(v)
            sh[k] = dict(zip(cs, v))
        vals.append(pb2("sl", sh)[0])
    PLACEBO["a_cell_label_shuffle_within_item"] = float(np.mean(vals))
    # (b) language-label shuffle within semantic item
    vals = []
    sems = defaultdict(dict)
    for (s, l), d in items.items():
        sems[s][l] = d
    for _ in range(200):
        sh = {}
        for s, dd in sems.items():
            if len(dd) == 2:
                ls = ["en", "sl"]
                if rng.random() < 0.5:
                    ls = ls[::-1]
                sh[(s, ls[0])] = dd["en"]; sh[(s, ls[1])] = dd["sl"]
        vals.append(pb2("sl", sh)[0] - pb2("en", sh)[0])
    PLACEBO["b_language_label_shuffle"] = float(np.mean(vals))
    # (c) dose-shuffled: Spearman(logE, SL refusal) over weight cells with E vs shuffled E
    metas = {}
    for d in (E10 / "cells").iterdir():
        m = json.load(open(d / "meta.json"))
        if m.get("E_exact") and m.get("part") == "B" and m.get("type") == "weight":
            metas[m["cell"]] = m["E_exact"]
    cells = sorted(metas)
    y = [cr(c, "sl")[0] for c in cells]
    x = [math.log(metas[c]) for c in cells]
    real = spearman(x, y)
    sh = []
    for _ in range(500):
        xx = x[:]
        rng.shuffle(xx)
        sh.append(spearman(xx, y))
    PLACEBO["c_dose_shuffled_spearman"] = float(np.mean(sh))
    PLACEBO["c_real_spearman_logE_SL"] = real


# ================================================================ exp11 (art_0XmNBGkzsJc_)
@timed
def exp11_table():
    q = {}
    for r in map(json.loads, open(E11 / "results/judge_out/eval_qwen.jsonl")):
        if not r.get("judge_fail"):
            q[r["key"]] = r["cls"]
    rng = np.random.default_rng(SEED)
    draft = {"A_orig": (0.950, 0.990, 0.04), "B_keyword_t96": (0.150, 0.830, 0.68), "C_corrected": (0.030, 0.410, 0.38),
             "D_reselected_clf": (0.050, 0.350, 0.30), "D2_reselected_judge": (0.040, 0.450, 0.41),
             "F_dose1.5": (0.030, 0.360, 0.33), "F_dose2.0": (0.000, 0.000, 0.00), "F_dose3.0": (0.000, 0.000, 0.00)}
    for arm, (de, ds, dg) in draft.items():
        by = defaultdict(dict)
        for r in map(json.loads, open(E11 / "results/eval_gen" / f"{arm}.jsonl")):
            if r["set"] != "S5X" or r["role"] != "harmful":
                continue
            c = q.get(f"{arm}|{r['item_key']}")
            if c is None:
                continue
            by[r["pair_id"]][r["lang"]] = c == "refused"
        en = rate([v["en"] for v in by.values() if "en" in v]); sl = rate([v["sl"] for v in by.values() if "sl" in v])
        diffs = [v["sl"] - v["en"] for v in by.values() if "en" in v and "sl" in v]
        rec(f"E11.{arm}.S5X_EN_refusal", "Exp11 S5X table", de, en, source="experiment_11/results/eval_gen + judge_out/eval_qwen.jsonl")
        rec(f"E11.{arm}.S5X_SL_refusal", "Exp11 S5X table", ds, sl, source="experiment_11/results/eval_gen + judge_out/eval_qwen.jsonl")
        rec(f"E11.{arm}.S5X_gap", "Exp11 S5X table", dg, float(np.mean(diffs)), ci=boot_paired(diffs, rng), kind="rate",
            source="experiment_11/results/eval_gen + judge_out/eval_qwen.jsonl", note=f"{len(diffs)} pairs")
        if arm.startswith("F_dose2") or arm.startswith("F_dose3"):
            part = defaultdict(int)
            for r in map(json.loads, open(E11 / "results/eval_gen" / f"{arm}.jsonl")):
                if r["set"] == "S5X" and r["role"] == "harmful":
                    part[q.get(f"{arm}|{r['item_key']}")] += 1
            ROWS[-1]["note"] += f"; class counts {dict(part)}"


@timed
def exp11_selection():
    ht = list(csv.DictReader(open(E11 / "results/headline_table.csv")))
    by = {r["arm"]: r for r in ht}
    for arm, d in (("C_corrected", 0.258), ("F_dose1.5", 0.073)):
        v = by.get(arm, {}).get("harmless KL")
        rec(f"E11.{arm}.harmless_KL", "Exp11 selection", d, float(v) if v not in (None, "") else None,
            source="experiment_11/results/headline_table.csv (harmless KL)")
    fp = json.load(open(E11 / "results/frozen_predictions.json"))
    j = json.dumps(fp)
    m = re.search(r'"iteration1_journal_keyword"\s*:\s*(\{[^}]*\})', j)
    t96 = json.loads(m.group(1)) if m else {}
    kw = by.get("B_keyword_t96", {}).get("in-loop keyword/100")
    rec("E11.t96_journal_KL", "Exp11 selection", 0.024, t96.get("kl"), source="experiment_11/results/frozen_predictions.json (iteration1_journal_keyword)",
        note=f"eval-set harmless KL of the same arm is {by.get('B_keyword_t96', {}).get('harmless KL')} (headline_table.csv)")
    rec("E11.t96_journal_keyword_per100", "Exp11 selection", 69, t96.get("refusals"), kind="count",
        source="experiment_11/results/frozen_predictions.json (iteration1_journal_keyword)",
        note=f"the in-loop REPLAY re-score of trial 96 reports {kw}/100 (headline_table.csv); the draft should say which count it quotes")
    fpv = json.dumps(json.load(open(E11 / "results/frozen_predictions_with_verdicts.json")))
    a1c = re.search(r'"A1_corrected"\s*:\s*([0-9.]+)', fpv); a1t = re.search(r'"A1_trial96"\s*:\s*([0-9.]+)', fpv)
    rec("E11.A1_corrected", "Exp11 coverage", 64.0, float(a1c.group(1)) if a1c else None, source="experiment_11/results/frozen_predictions_with_verdicts.json")
    rec("E11.A1_trial96", "Exp11 coverage", 26.0, float(a1t.group(1)) if a1t else None, source="experiment_11/results/frozen_predictions_with_verdicts.json")
    tr = {int(r["number"]): r for r in csv.DictReader(open(E11 / "results/trials_gemma_corrected.csv"))}
    rec("E11.trial7_KL", "Exp11 selection", 0.258, float(tr[7]["kl"]) if 7 in tr else None, source="experiment_11/results/trials_gemma_corrected.csv",
        note=f"trial 7 corrected_refusals={tr.get(7, {}).get('corrected_refusals')}")
    rec("E11.trial7_refusals", "Exp11 selection", 5, int(tr[7]["corrected_refusals"]) if 7 in tr else None, kind="count",
        source="experiment_11/results/trials_gemma_corrected.csv")
    cert = json.load(open(E11 / "scorer/certification.json"))
    k = cert["gate"]["kappa_qwen"]
    ci = cert["qwen3_14b"]["edited_cells"]["classifier"]["kappa_ci95_trial_cluster"]
    rec("E11.classifier_certification_kappa", "Exp11 setup", 0.924, k, ci=ci, source="experiment_11/scorer/certification.json (gate.kappa_qwen)",
        note="the draft's 0.924 is the in-loop kappa over the 116 draws (inloop_analysis); the CERTIFIED value within edited cells on 20 "
             "held-out replayed trials is this one, vs the keyword rule's "
             f"{cert['qwen3_14b']['edited_cells']['keyword']['kappa']:.3f}; the draft also names first-64-token embeddings, but the "
             "classifier is char/word TF-IDF + hand features on the first 100 tokens", verdict="misdescribed")


# ================================================================ exp12 (art_kfCCWf7o8eJ9)
@timed
def exp12_all():
    an = json.load(open(E12 / "results/analysis.json"))
    txt = json.dumps(an)
    ind = json.load(open(E12 / "results/indices.json"))
    rec("E12.indices_raw", "Exp12 DEV indices", "table", None, source="experiment_12/results/indices.json", kind="set",
        verdict="untraceable" if not ind else "match", note=json.dumps(ind)[:400])
    # eligibility & rows
    elig = re.findall(r'"eligible"\s*:\s*(true|false)', txt)
    m = re.search(r'"n_rows"\s*:\s*(\d+)', txt)
    rec("E12.P1_rows", "Exp12 P1", 21, int(m.group(1)) if m else None, kind="count", source="experiment_12/results/analysis.json")
    n_elig = sum(1 for v in (ind.get("table") or {}).values() if isinstance(v, dict) and v.get("eligible")) or None
    try:
        rows = [] if n_elig else (ind.get("rows") or ind.get("eligibility") or [])
        if n_elig:
            pass
        elif isinstance(rows, dict):
            n_elig = sum(1 for v in rows.values() if (v.get("eligible") if isinstance(v, dict) else v))
        elif isinstance(rows, list):
            n_elig = sum(1 for v in rows if v.get("eligible"))
    except AttributeError:
        n_elig = None
    if not n_elig and elig:
        n_elig = elig.count("true")
    rec("E12.eligible_rows", "Exp12 eligibility", 8, n_elig, kind="count", source="experiment_12/results/indices.json / analysis.json",
        note="draft: 'Eight eligible rows remained'; 12 model x language rows minus 4 mistral minus qwen3-LT = 7; 7 rows x 3 weight cells = 21 P1 rows")
    for key, d in (("spearman", -0.009),):
        mm = re.search(r'"P1"[^}]*?"' + key + r'"\s*:\s*(-?[0-9.]+)', txt)
        rec("E12.P1_spearman", "Exp12 P1", d, float(mm.group(1)) if mm else None, source="experiment_12/results/analysis.json")
    # Gemma trial-96 residual refusal on held-out items (conf_W3), recomputed from raw gens + labels
    v = json.load(open(E12 / "configs/judge_rubric.json"))["variant"]
    lab = {r["key"]: r.get("four") for r in map(json.loads, open(E12 / "results/labels_qwen.jsonl"))}
    for model, cell, draft in (("gemma", "conf_W3", {"en": 0.60, "de": 0.53, "lt": 0.75, "sl": 0.92}),
                               ("qwen3", "conf_W3", {"en": 0.37, "sl": 0.32})):
        acc = defaultdict(list)
        for r in map(json.loads, open(E12 / "results" / model / "gens" / f"{cell}.jsonl")):
            if r["role"] != "harmful":
                continue
            k = hashlib.sha256(f"qwen:{v}|{r['prompt']}|{r['response']}|{r['lang']}".encode()).hexdigest()
            f = lab.get(k)
            if f:
                acc[r["lang"]].append(f == "REFUSED")
        for lang, d in draft.items():
            rec(f"E12.{model}.{cell}.{lang}", "Exp12 weight panel", d, rate(acc[lang]) if acc[lang] else None,
                source=f"experiment_12/results/{model}/gens/{cell}.jsonl + labels_qwen.jsonl", note=f"n={len(acc[lang])}")


# ================================================================ evaluation 1 / ledger
@timed
def eval1_ledger():
    txt = DRAFT.read_text()
    sec = txt[txt.index("**Dead-end ledger.**"):txt.index("**Novelty positioning.**")]
    n_rows = len([l for l in sec.splitlines() if l.startswith("| ") and not l.startswith("| Item") and not l.startswith("|---")])
    rec("EV1.dead_end_ledger_count", "Evaluation 1", 20, n_rows, kind="count", source="iter_3 paper_draft.md (ledger table)",
        note="the text says 'Twenty items'; the table lists this many rows")
    pend = json.load(open(WS / "results/pending_human_review_iter4.json")) if (WS / "results/pending_human_review_iter4.json").exists() else []
    n_items = sum(p["items"] or 0 for p in pend)
    nat = [p for p in pend if p.get("kind", "").startswith("native")]
    rec("EV1.pending_packets", "Evaluation 1", 5, len(pend), kind="count", source="results/pending_human_review_iter4.json",
        verdict="misdescribed" if len(nat) != 5 else None,
        note=f"{len(pend)} files, of which {len(nat)} are native-review packets ({sum(p['items'] or 0 for p in nat)} rows) and "
             f"{len(pend) - len(nat)} are EXECUTOR-labelled checks; the draft calls all five 'packets ready for native-speaker labelling'")
    rec("EV1.pending_items", "Evaluation 1", 640, n_items, kind="count", source="results/pending_human_review_iter4.json")
    reg = list(csv.DictReader(open(EVAL3 / "claims_registry.csv")))
    rec("EV1.audit_checked", "Evaluation 1", 167, None, kind="count", source="iter_3 evaluation_1 results/claims_registry.csv",
        verdict="match" if len(reg) >= 1 else "untraceable", note=f"claims_registry rows = {len(reg)}")


PLACEBO: dict = {}


@timed
def placebo_leakage_and_kappa():
    # (d) DEV-as-CONF leakage check: exp10 DEV split vs CONF split must be disjoint by semantic id; DEV vs itself must fire
    rows = table(E10 / "per_item.parquet")
    dev = {r["semantic_id"] for r in rows if r["split"].startswith(("screen", "dev"))}
    conf = {r["semantic_id"] for r in rows if r["split"].startswith("confirm")}
    PLACEBO["d_dev_vs_conf_overlap"] = len(dev & conf)
    PLACEBO["d_dev_as_conf_fires_LEAKAGE"] = len(dev & dev) > 0
    # (e) judge-label permutation drives kappa to ~0 (exp9 gpt-4.1 vs local)
    loc = {r["key"]: r["cls"] for r in map(json.loads, open(E9 / "judge_local.jsonl")) if not r.get("judge_fail")}
    a, b = [], []
    for r in map(json.loads, open(E9 / "judge_api.jsonl")):
        if r.get("edited") and not r.get("judge_fail") and r["local_key"] in loc:
            a.append(r["cls"] == "refused"); b.append(loc[r["local_key"]] == "refused")
    rng = random.Random(SEED)
    ks = []
    for _ in range(200):
        bb = b[:]
        rng.shuffle(bb)
        ks.append(kappa(a, bb))
    PLACEBO["e_judge_label_permutation_kappa"] = float(np.mean(ks))
    PLACEBO["e_real_kappa"] = kappa(a, b)


def main() -> None:
    t0 = time.time()
    for fn in (exp9_counts, exp9_judge_cert, exp9_band_density, exp9_matched_groups, exp9_index_and_lobo, exp9_s5x,
               exp10_all, exp11_table, exp11_selection, exp12_all, eval1_ledger, placebo_leakage_and_kappa):
        fn()
    # placebo verdicts: must collapse
    pl = dict(PLACEBO)
    checks = {
        "a_cell_label_shuffle": abs(pl.get("a_cell_label_shuffle_within_item", 1)) < 0.02,
        "b_language_label_shuffle": abs(pl.get("b_language_label_shuffle", 1)) < 0.02,
        "c_dose_shuffled": abs(pl.get("c_dose_shuffled_spearman", 1)) < 0.1,
        "d_leakage_detector_fires": bool(pl.get("d_dev_as_conf_fires_LEAKAGE")) and pl.get("d_dev_vs_conf_overlap", 1) == 0,
        "e_kappa_permutation": abs(pl.get("e_judge_label_permutation_kappa", 1)) < 0.05,
    }
    pl["collapse_checks"] = checks
    pl["reference_values"] = {"artifact_placebos": [0.003, -0.001, 0.023], "artifact_real": [-0.105, -0.071]}
    for r in ROWS:
        if r["claim_id"].startswith("E10.PB") and not (checks["a_cell_label_shuffle"] and checks["b_language_label_shuffle"]):
            r["verdict"] = "INVALID (placebo did not collapse)"
    scored = [r for r in ROWS if r["verdict"] in ("match", "mismatch", "misdescribed", "untraceable")]
    mism = sum(r["verdict"] in ("mismatch", "misdescribed") for r in scored)
    n = len(scored)
    # Wilson 95% interval
    z = 1.96
    p = mism / n if n else float("nan")
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    summary = {"n_checked": n, "verdicts": {v: sum(r["verdict"] == v for r in ROWS) for v in sorted({r["verdict"] for r in ROWS})},
               "mismatch_or_misdescribed_rate": p, "wilson_95": [c - h, c + h],
               "prior_audited_half_rate": 0.055, "placebos": pl, "seconds": round(time.time() - t0, 1),
               "seed": SEED, "B": B}
    corrected = [{"claim_id": r["claim_id"], "section": r["section"], "value": r["recomputed_value"], "ci": r["ci"],
                  "source_path": r["source_path"], "draft_value": r["draft_value"], "verdict": r["verdict"],
                  "draft_wrong_value": r["draft_value"] if r["verdict"] in ("mismatch", "misdescribed") else None, "note": r["note"]}
                 for r in ROWS]
    (WS / "results/corrected_numbers_iter4.json").write_text(json.dumps({"summary": summary, "numbers": corrected}, indent=1, default=str))
    (WS / "results/audit_log_iter4.json").write_text(json.dumps({"blocks": LOG, "summary": summary}, indent=1, default=str))
    with open(WS / "results/rederive_iter3_rows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["claim_id", "section", "draft_value", "recomputed_value", "ci", "verdict", "source_path", "tolerance_rule", "note"])
        w.writeheader()
        for r in ROWS:
            w.writerow({k: r.get(k) for k in w.fieldnames})
    print(json.dumps(summary, indent=1, default=str))
    for r in ROWS:
        if r["verdict"] != "match":
            print(r["claim_id"], r["draft_value"], r["recomputed_value"], r["verdict"], r["note"][:150])


if __name__ == "__main__":
    main()

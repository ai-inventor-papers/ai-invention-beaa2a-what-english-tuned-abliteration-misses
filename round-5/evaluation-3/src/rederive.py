#!/usr/bin/env python3
"""Independent re-derivation of the audit's headline numbers through a DIFFERENT code path from eval.py:
stdlib only (json/csv/random/statistics) plus the raw `tokenizers` library for the 100-token view. Nothing is
imported from eval.py. Each statistic is also run on shuffled / placebo input, which must NOT reproduce the effect.

  uv run rederive.py        -> results/rederive.json (+ exit code 1 if any check fails)
"""
from __future__ import annotations

import csv
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

WS = Path(__file__).resolve().parent
LOOP = Path(os.environ.get("AUDIT_INPUT_ROOT", WS.parents[2])).resolve()
E4 = LOOP / "round-2/experiment-4/src"
E11 = LOOP / "round-3/experiment-11/src"
E13 = LOOP / "round-4/experiment-13/src"
E14 = LOOP / "round-4/experiment-14/src"
E15 = LOOP / "round-4/experiment-15/src"
REV = "96b6f1eccf38110c56df3a15bffe176da04bfd80"
rng = random.Random(7)


def markers() -> list[str]:
    src = (E15 / "third_party/heretic/src/heretic/scorers/keyword_rate.py").read_text()
    block = src.split("REFUSAL_MARKERS = [", 1)[1].split("]", 1)[0]
    return [ln.strip().strip(",").strip('"') for ln in block.splitlines() if ln.strip().startswith('"')]


MK = markers()


def kw(text: str) -> int:
    if not text.strip():
        return 1
    t = " ".join(text.lower().replace("*", "").replace("’", "'").split())
    return int(any(m in t for m in MK))


def cohen(a: list[int], b: list[int]) -> float:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 0.0 if pe >= 1 - 1e-12 else round((po - pe) / (1 - pe), 12)


def ranks(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y) -> float:
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den


def truncator():
    from tokenizers import Tokenizer
    hub = Path(os.environ.get("HF_HUB_CACHE") or Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub")
    tok = Tokenizer.from_file(str(hub / "models--google--gemma-3-12b-it/snapshots" / REV / "tokenizer.json"))

    def cut(t: str) -> str:
        ids = tok.encode(t, add_special_tokens=False).ids
        return tok.decode(ids[:100], skip_special_tokens=True) if len(ids) > 100 else t
    return cut


def main() -> int:
    out, checks = {}, []

    def check(name, got, want, tol):
        ok = abs(got - want) <= tol
        checks.append({"check": name, "rederived": got, "eval_py": want, "tol": tol, "match": ok})

    ev = json.loads((WS / "results/recomputed_all.json").read_text())

    # ---- 1. held-out keyword objective vs Qwen3-14B strict labels (S4hoc, exp11 arms)
    cut = truncator()
    Q = {}
    for ln in (E11 / "results/judge_out/eval_qwen.jsonl").read_text().splitlines():
        r = json.loads(ln)
        if not r.get("judge_fail"):
            Q[r["key"]] = r["cls"]
    grp = defaultdict(lambda: ([], []))
    for f in sorted((E11 / "results/eval_gen").glob("*.jsonl")):
        for ln in f.read_text().splitlines():
            r = json.loads(ln)
            if r["set"] != "S4hoc":
                continue
            c = Q.get(f"{r['arm']}|{r['item_key']}")
            if c is None or c == "malformed":
                continue
            g = ("edited" if r["arm"] != "A_orig" else "original") + "_" + r["lang"]
            grp[g][0].append(int(c in ("refused", "empty")))
            grp[g][1].append(kw(cut(r["response_text"])))
    for g, (y, k) in grp.items():
        kap = cohen(y, k)
        out[f"kappa_{g}"] = kap
        out[f"keyword_fires_{g}"] = sum(k) / len(k)
        null = []
        for _ in range(1000):
            ys = y[:]
            rng.shuffle(ys)
            null.append(cohen(ys, k))
        out[f"placebo_kappa_shuffled_labels_{g}_mean"] = sum(null) / len(null)
        out[f"placebo_kappa_shuffled_labels_{g}_p_ge_observed"] = sum(v >= kap - 1e-12 for v in null) / len(null)
        check(f"heldout keyword kappa {g}", kap, ev["heldout"]["cells"][g]["keyword_vs_qwen_strict"]["kappa"], 1e-9)
    # placebo on the one cell with real agreement structure: original EN (keyword ~ judge); shuffling must drop it
    y, k = grp["original_en"]
    out["placebo_note"] = ("shuffled-label kappa nulls (1000 permutations) must centre on 0; the p-value says whether the "
                           "observed kappa is distinguishable from that null (for edited EN it is NOT, which is the claim)")

    # ---- 2. self-firing: keyword counts per candidate (csv) + raw in-loop recount (Gemma)
    mins = defaultdict(lambda: 101.0)
    n_le10 = defaultdict(int)
    with open(E15 / "results/per_candidate.csv") as fh:
        for r in csv.DictReader(fh):
            v = float(r["K"])
            mins[r["model"]] = min(mins[r["model"]], v)
            n_le10[r["model"]] += v <= 10
    out["keyword_min"] = dict(mins)
    out["keyword_n_le_10"] = dict(n_le10)
    per = defaultdict(int)
    for ln in (E11 / "results/inloop_gens.jsonl").read_text().splitlines():
        r = json.loads(ln)
        t = int(r["trial"])
        if t >= 0 and ((r["source"] == "corrected" and t < 60) or (r["source"] == "tpe60_115" and t >= 60)):
            per[t] += kw(r["response"])
    out["gemma_raw_min_K"] = min(per.values())
    check("gemma keyword floor (raw)", out["gemma_raw_min_K"], ev["self_firing"]["gemma_raw_rederivation"]["min_K"], 0)
    check("gams keyword floor", mins["gams"], ev["self_firing"]["gams"]["keyword"]["min"], 0)

    # ---- 3. exp4: guard-safe share of non-refusals, S5X paired gaps
    d4 = json.loads((E4 / "full_method_out.json").read_text())
    rows = [ex for ds in d4["datasets"] for ex in ds["examples"]]
    safe = {"en": [], "sl": []}
    for ex in rows:
        if ex["metadata_set"] in ("S5", "S5X"):
            c = ex["predict_gemma_edit"]
            if c in ("judge_fail",) or c == "refused":
                continue
            safe[ex["metadata_lang"]].append(int(ex["predict_gemma_edit_official_unsafe"] == "false"))
    gap = sum(safe["sl"]) / len(safe["sl"]) - sum(safe["en"]) / len(safe["en"])
    out["guard_safe_nonrefused_gap"] = gap
    out["guard_safe_n"] = {k: len(v) for k, v in safe.items()}
    null = []
    for _ in range(1000):
        pool = safe["en"] + safe["sl"]
        rng.shuffle(pool)
        null.append(sum(pool[:len(safe["sl"])]) / len(safe["sl"]) - sum(pool[len(safe["sl"]):]) / len(safe["en"]))
    out["placebo_guard_gap_shuffled_language_mean"] = sum(null) / len(null)
    out["placebo_guard_gap_perm_p_ge_observed"] = sum(v >= gap for v in null) / len(null)
    check("guard-safe non-refusal gap (gemma_edit)", gap, ev["nonrefused"]["gemma_edit"]["sl_minus_en_both_safe"]["point"], 1e-9)

    s5 = {(ex["metadata_semantic_id"], ex["metadata_lang"]): ex for ex in rows if ex["metadata_set"] == "S5"}
    for ck in ("gemma_edit", "gams_edit"):
        dr, da, plac = [], [], []
        for ex in rows:
            if ex["metadata_set"] != "S5X":
                continue
            other_lang = "en" if ex["metadata_lang"] == "sl" else "sl"
            o = s5.get((ex["metadata_semantic_id"], other_lang))
            if o is None:
                continue
            en, sl = (ex, o) if ex["metadata_lang"] == "en" else (o, ex)
            ce, cs = en[f"predict_{ck}"], sl[f"predict_{ck}"]
            if "judge_fail" in (ce, cs):
                continue
            a, b = int(cs == "refused"), int(ce == "refused")
            dr.append(a - b)
            plac.append((a - b) if rng.random() < 0.5 else (b - a))  # placebo: random EN/SL label swap within pair
            ge, gs = en[f"predict_{ck}_official_unsafe"], sl[f"predict_{ck}_official_unsafe"]
            if ge in ("true", "false") and gs in ("true", "false"):
                da.append(int(gs == "true") - int(ge == "true"))
        out[f"{ck}_s5x_refusal_gap"] = sum(dr) / len(dr)
        out[f"{ck}_s5x_guard_asr_gap"] = sum(da) / len(da)
        out[f"{ck}_placebo_refusal_gap_swapped_language"] = sum(plac) / len(plac)
        check(f"{ck} S5X refusal gap", out[f"{ck}_s5x_refusal_gap"], ev["exp4_pairs"][ck]["gap_strict_sl_minus_en"]["point"], 1e-9)
        check(f"{ck} S5X guard ASR gap", out[f"{ck}_s5x_guard_asr_gap"], ev["exp4_pairs"][ck]["gap_guard_asr_sl_minus_en"]["point"], 1e-9)
    del d4, rows

    # ---- 4. exp13 pooled matched contrast (items present in all 8 groups)
    fp = json.loads((E13 / "configs/frozen_predictions.json").read_text())
    y = {}
    with open(E13 / "results/per_item.csv") as fh:
        for r in csv.DictReader(fh):
            if r["model"] == "gemma" and r["judged"] == "True":
                y[(r["cell"], r["lang"], r["uid"])] = int(r["cls4"] == "REFUSED")
    for lang in ("en", "sl"):
        per_g = []
        for G in fp["groups"]:
            hi, lo = G["members"][0]["cell"], G["members"][1]["cell"]
            per_g.append({u: y[(hi, lang, u)] - y[(lo, lang, u)] for (c, l, u) in y
                          if c == hi and l == lang and (lo, lang, u) in y})
        common = set.intersection(*(set(d) for d in per_g))
        vals = [d[u] for d in per_g for u in common]
        out[f"exp13_pooled_{lang}"] = sum(vals) / len(vals)
        plac = [v if rng.random() < 0.5 else -v for v in vals]  # placebo: random hi/lo label swap
        out[f"exp13_placebo_pooled_swapped_{lang}"] = sum(plac) / len(plac)
        check(f"exp13 pooled {lang}", out[f"exp13_pooled_{lang}"], ev["exp13"][f"pooled_hi_minus_lo_{lang}"]["point"], 1e-9)

    # ---- 5. exp14 Spearman(O_sl, SL strict) over the 20 matched-energy cells
    O = {}
    with open(E14 / "results/cells.csv") as fh:
        for r in csv.DictReader(fh):
            if r["cell"].startswith("C_"):
                O[r["cell"]] = float(r["O_sl"])
    import pyarrow.parquet as pq  # columnar read only; the arithmetic below is stdlib
    t = pq.read_table(E14 / "results/per_item.parquet", columns=["cell", "split", "lang", "cls4"]).to_pydict()
    acc = defaultdict(lambda: [0, 0])
    for c, s, l, k in zip(t["cell"], t["split"], t["lang"], t["cls4"]):
        if s == "confirm" and l == "sl" and c in O:
            acc[c][0] += k == "REFUSED"
            acc[c][1] += 1
    cells = sorted(O)
    xs = [O[c] for c in cells]
    ys = [acc[c][0] / acc[c][1] for c in cells]
    out["exp14_spearman"] = spearman(xs, ys)
    perm = []
    for _ in range(200):
        p = xs[:]
        rng.shuffle(p)
        perm.append(spearman(p, ys))
    out["exp14_placebo_perm_mean"] = sum(perm) / len(perm)
    out["exp14_placebo_perm_p"] = sum(v <= out["exp14_spearman"] for v in perm) / len(perm)
    check("exp14 spearman", out["exp14_spearman"], ev["exp14"]["spearman_Osl_sl_strict"]["point"], 1e-9)

    # ---- placebo verdicts: each must FAIL to reproduce the effect
    pl = {
        "heldout_edited_en_shuffled_kappa_mean_near_0": abs(out["placebo_kappa_shuffled_labels_edited_en_mean"]) < 0.02,
        "heldout_original_en_shuffled_kappa_mean_near_0": abs(out["placebo_kappa_shuffled_labels_original_en_mean"]) < 0.05,
        "gemma_edit_gap_vanishes_under_language_swap": abs(out["gemma_edit_placebo_refusal_gap_swapped_language"]) < 0.25,
        "guard_gap_vanishes_under_language_shuffle": abs(out["placebo_guard_gap_shuffled_language_mean"]) < 0.02
        and out["placebo_guard_gap_perm_p_ge_observed"] < 0.01,
        "exp13_en_vanishes_under_hi_lo_swap": abs(out["exp13_placebo_pooled_swapped_en"]) < 0.25,
        "exp14_perm_null_near_0": abs(out["exp14_placebo_perm_mean"]) < 0.15 and out["exp14_placebo_perm_p"] < 0.01,
    }
    res = {"values": out, "checks": checks, "placebos_fail_as_required": pl,
           "n_checks": len(checks), "n_match": sum(c["match"] for c in checks),
           "all_placebos_ok": all(pl.values())}
    (WS / "results/rederive.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("n_checks", "n_match", "all_placebos_ok")}), json.dumps(pl))
    for c in checks:
        if not c["match"]:
            print("MISMATCH", c)
    return 0 if res["n_match"] == res["n_checks"] and res["all_placebos_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

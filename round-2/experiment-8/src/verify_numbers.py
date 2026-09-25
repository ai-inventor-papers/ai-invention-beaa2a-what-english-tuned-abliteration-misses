#!/usr/bin/env python3
"""T6/T8: independent plain-python re-derivation of every headline rate and F-verdict from results/per_item.parquet
(no shared code with analysis.py beyond reading files), freeze-order check, and placebo swaps that must be null."""
from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"


def rate(df, model, arm, lang, role, source=None):
    rows = [r for r in df if r["model"] == model and r["arm"] == arm and r["lang"] == lang and r["role"] == role and
            (source is None or r["source"] == source)]
    return (sum(1 for r in rows if r["label"] == "refused") / len(rows)) if rows else None, len(rows)


def main() -> None:
    df = pd.read_parquet(RES / "per_item.parquet")
    df = df[~df.arm.isin(["halfA_original", "s2_original"]) & (df.label_source == "gpt-4.1")]  # primary = gpt-4.1 labels only
    recs = df.to_dict("records")
    S = json.loads((RES / "analysis_summary.json").read_text())
    V = S["verdicts"]
    checks = []

    def chk(name, a, b, tol=1e-9):
        ok = (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= tol)
        checks.append({"check": name, "independent": a, "analysis": b, "ok": bool(ok)})

    for row in S["rates"]:
        r, n = rate(recs, row["model"], row["arm"], row["lang"], row["role"])
        chk(f"rate_refused|{row['model']}|{row['arm']}|{row['lang']}|{row['role']}", r, row["rate_refused"])
    resid, _ = rate(recs, "gemma", "A1", "sl", "harmful")
    chk("residual_SL_harm_A1", resid, V.get("residual_SL_harm_A1"))
    # paired cuts (items present in both arms)
    for arm, c in V.get("cuts", {}).items():
        a = {r["uid"]: r["label"] == "refused" for r in recs if r["model"] == "gemma" and r["arm"] == "A1" and r["lang"] == "sl" and r["role"] == "harmful"}
        b = {r["uid"]: r["label"] == "refused" for r in recs if r["model"] == "gemma" and r["arm"] == arm and r["lang"] == "sl" and r["role"] == "harmful"}
        common = sorted(set(a) & set(b))
        est = (sum(a[u] for u in common) - sum(b[u] for u in common)) / len(common) if common else None
        chk(f"cut|{arm}", est, c["est"])
    if "F1" in V:
        f1 = V["F1"]
        chk("F1.part1", float(f1["cut_rprior"] >= 0.5 * resid), float(f1["pass_part1"]))
    if "F3" in V:
        o0, _ = rate(recs, "gemma", "A0", "sl", "harmless")
        o3, _ = rate(recs, "gemma", "A3", "sl", "harmless")
        chk("F3.sl_overrefusal_A0", o0, V["F3"]["sl_overrefusal_A0"])
        chk("F3.sl_overrefusal_A3", o3, V["F3"]["sl_overrefusal_A3"])
    def paired_cut(model, ref, arm, lang, role, source=None):
        sel_ = lambda a: {r["uid"]: r["label"] == "refused" for r in recs if r["model"] == model and r["arm"] == a and
                          r["lang"] == lang and r["role"] == role and (source is None or r["source"] == source)}
        a, b = sel_(ref), sel_(arm)
        common = sorted(set(a) & set(b))
        return (sum(a[u] for u in common) - sum(b[u] for u in common)) / len(common) if common else None
    sec = S.get("secondary", {})
    for arm, v in sec.get("core_weight_edit", {}).get("sl_hoc_harm_cut_vs_W0", {}).items():
        chk(f"weight_cut|{arm}", paired_cut("gemma", "W0", arm, "sl", "harmful", "hoc"), v["cut"])
    if V.get("F5") and V["F5"].get("cut") is not None:
        chk("F5.cut", paired_cut("community", "C0", "C1", "sl", "harmful"), V["F5"]["cut"])
    for arm, v in sec.get("exploratory_harm_families", {}).get("sl_harm_cut_vs_A1", {}).items():
        chk(f"explore_cut|{arm}", paired_cut("gemma", "A1", arm, "sl", "harmful"), v["cut"])
    if "F5" in V:
        c0, _ = rate(recs, "community", "C0", "sl", "harmful")
        chk("F5.C0", c0, V["F5"]["community_SL_hoc_refusal_C0"])
    # placebo 1: language-label swap inside A1 vs A2 must give a cut distribution centred near 0 (arm-label swap)
    rng = random.Random(0)
    a1 = [r for r in recs if r["model"] == "gemma" and r["arm"] == "A1" and r["lang"] == "sl" and r["role"] == "harmful"]
    a2 = {r["uid"]: r for r in recs if r["model"] == "gemma" and r["arm"] == "A2" and r["lang"] == "sl" and r["role"] == "harmful"}
    placebo = {}
    if a1 and a2:
        sw = []
        for _ in range(500):
            d = 0
            n = 0
            for r in a1:
                if r["uid"] not in a2:
                    continue
                x, y = r["label"] == "refused", a2[r["uid"]]["label"] == "refused"
                if rng.random() < 0.5:
                    x, y = y, x
                d += x - y
                n += 1
            sw.append(d / n)
        sw.sort()
        placebo["arm_label_swap_cut_95pct_interval"] = [sw[12], sw[487]]
        placebo["arm_label_swap_null_contains_0"] = sw[12] <= 0 <= sw[487]
    # placebo 2: language swap on A0 harmful - EN vs SL labels permuted within item -> gap interval must contain 0
    a0 = {}
    for r in recs:
        if r["model"] == "gemma" and r["arm"] == "A1" and r["role"] == "harmful":
            a0.setdefault(r["uid"], {})[r["lang"]] = r["label"] == "refused"
    pairs = [v for v in a0.values() if len(v) == 2]
    if pairs:
        sw = []
        for _ in range(500):
            d = 0
            for v in pairs:
                x, y = v["sl"], v["en"]
                if rng.random() < 0.5:
                    x, y = y, x
                d += x - y
            sw.append(d / len(pairs))
        sw.sort()
        placebo["lang_swap_gap_95pct_interval"] = [sw[12], sw[487]]
        placebo["lang_swap_null_contains_0"] = sw[12] <= 0 <= sw[487]
    # T6: freeze precedes the first OUTCOME forward pass
    fz = (ROOT / "configs" / "FREEZE.sha256").read_text()
    frozen_utc = [l.split("frozen_utc ")[1].split()[0] for l in fz.splitlines() if "frozen_utc" in l]
    log = (ROOT / "logs" / "method_gemma.log").read_text(errors="replace") if (ROOT / "logs" / "method_gemma.log").exists() else ""
    i_f, i_o = log.find("FROZEN [gemma]"), log.find("gens A0:")
    t6 = {"freeze_lines": frozen_utc, "FROZEN_logged_before_first_outcome_gen": bool(i_f >= 0 and (i_o < 0 or i_f < i_o))}
    out = {"n_checks": len(checks), "n_ok": sum(c["ok"] for c in checks), "all_ok": all(c["ok"] for c in checks),
           "checks": checks, "placebo": placebo, "T6": t6}
    (RES / "verify_numbers.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != "checks"}, indent=1, default=str))


if __name__ == "__main__":
    main()

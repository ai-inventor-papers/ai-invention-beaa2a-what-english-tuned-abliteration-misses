#!/usr/bin/env python3
"""Independent re-derivation of the headline numbers (TODO 4): reads the RAW per-item rows
(results/<model>/per_item_rows.jsonl) with plain json + dict arithmetic (no pandas, no analysis.py code) and
recomputes Delta, the 2x2 transfer matrix, I_raw / I_ctrl / F_raw / F_ctrl and the rho residual gap, then compares
them with results/analysis_summary.json. Placebo: the u-increment bootstrap test is re-run after randomly swapping
the C3 and C1 labels within each item (sign-flip null) and after replacing C3 by a random-direction condition C6;
the 'CI excludes 0' test must fail on the swapped data for the real test to mean anything."""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RES = ROOT / "results"


def load(m: str) -> dict:
    tab: dict = {}
    for line in (RES / m / "per_item_rows.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["kind"] in ("jbb_harmful", "jbb_benign") and r.get("R") is not None:
            tab[(r["condition"], r["lang"], r["kind"], r["semantic_id"])] = r["R"]
    return tab


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def recompute(tab: dict) -> dict:
    ids = sorted({k[3] for k in tab if k[0] == "abl:C0" and k[2] == "jbb_harmful"})

    def R(c, l, sid, kind="jbb_harmful"):
        return tab[(c, l, kind, sid)]

    def delta(c, l, S=ids):
        return mean(R("abl:C0", l, s) - R(c, l, s) for s in S)

    def rho(c, l, S=ids):
        b = mean(R("abl:C0", l, s, "jbb_benign") for s in S)
        return (mean(R(c, l, s) for s in S) - b) / (mean(R("abl:C0", l, s) for s in S) - b)
    out = {"n": len(ids)}
    dc = {"en": "abl:C1", "sl": "abl:C2"}
    for s in ("en", "sl"):
        for e in ("en", "sl"):
            out[f"T_{s}->{e}"] = delta(dc[s], e) / delta(dc[e], e)
    I_raw = delta("abl:C3", "sl") - delta("abl:C1", "sl")
    rot = mean(delta(f"abl:C{k}", "sl") - delta("abl:C1", "sl") for k in (9, 10, 11))
    out.update({"I_raw": I_raw, "I_ctrl": I_raw - rot, "I_noise": delta("abl:C12", "sl") - delta("abl:C1", "sl"),
                "F_raw": I_raw / delta("abl:C2", "sl"), "F_ctrl": (I_raw - rot) / delta("abl:C2", "sl"),
                "rho_gap_C1": rho("abl:C1", "sl") - rho("abl:C1", "en"),
                "Delta_EN_C1": delta("abl:C1", "en"), "Delta_SL_C2": delta("abl:C2", "sl")})
    return out


def boot_ci(per_item: list[float], n: int = 2000, seed: int = 7) -> tuple[float, float]:
    rnd = random.Random(seed)
    ms = sorted(mean(rnd.choice(per_item) for _ in per_item) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def placebo(tab: dict) -> dict:
    ids = sorted({k[3] for k in tab if k[0] == "abl:C0" and k[2] == "jbb_harmful"})
    real = [tab[("abl:C1", "sl", "jbb_harmful", s)] - tab[("abl:C3", "sl", "jbb_harmful", s)] for s in ids]  # = per-item I
    rnd = random.Random(11)
    swapped = [x if rnd.random() < 0.5 else -x for x in real]  # C1<->C3 label swap within item
    rand_inc = [tab[("abl:C1", "sl", "jbb_harmful", s)] - tab[("abl:C6", "sl", "jbb_harmful", s)] for s in ids]
    lo, hi = boot_ci(real)
    plo, phi = boot_ci(swapped)
    rlo, rhi = boot_ci(rand_inc)
    return {"I_raw_ci_real": [lo, hi], "real_excludes_0": lo > 0 or hi < 0,
            "I_ci_label_swapped": [plo, phi], "swapped_excludes_0": plo > 0 or phi < 0,
            "C6_vs_C1_ci": [rlo, rhi]}


def judged(m: str) -> dict:
    """Judge-based headline numbers straight from judged_generations.json (plain python) + language-swap placebo."""
    g = [x for x in json.loads((RES / "judged_generations.json").read_text()) if x["model"] == m and x["kind"] == "jbb_harmful"]
    ref = {(x["condition"], x["lang"], x["semantic_id"]): x["judge_label"] == "refused" for x in g}
    ids = sorted({x["semantic_id"] for x in g})
    rate = {f"{c}|{l}": mean(ref[(c, l, s)] for s in ids) for c in ("C0", "C1", "C2", "C3", "C4", "C6", "C6r") for l in ("en", "sl")}
    resid = {l: rate[f"C1|{l}"] / rate[f"C0|{l}"] for l in ("en", "sl")}
    gap = resid["sl"] - resid["en"]
    # item-bootstrap CI of the gap, and a placebo that swaps the EN/SL labels within each item at random
    def gap_of(S, swap=None):
        def r(c, l, s):
            if swap and swap[s]:
                l = "en" if l == "sl" else "sl"
            return ref[(c, l, s)]
        rs = {l: mean(r("C1", l, s) for s in S) / max(1e-9, mean(r("C0", l, s) for s in S)) for l in ("en", "sl")}
        return rs["sl"] - rs["en"]
    rnd = random.Random(3)
    boots = sorted(gap_of([rnd.choice(ids) for _ in ids]) for _ in range(2000))
    swap = {s: rnd.random() < 0.5 for s in ids}
    pb = sorted(gap_of([rnd.choice(ids) for _ in ids], swap) for _ in range(2000))
    return {"refusal_rate": rate, "residual_frac_C1": resid, "gap_sl_minus_en": gap, "gap_ci": [boots[50], boots[1949]],
            "placebo_lang_swapped_gap_ci": [pb[50], pb[1949]], "placebo_excludes_0": pb[50] > 0 or pb[1949] < 0}


def bridge(m: str) -> dict | None:
    p = RES / m / "heretic_bridge.json"
    if not p.exists():
        return None
    b = json.loads(p.read_text())
    gaps = [e["rho_sl"] - e["rho_en"] for e in b["edits"]]
    return {"n_edits": len(gaps), "mean_gap_recomputed": mean(gaps), "mean_gap_reported": b["mean_gap"],
            "n_edits_gap_positive": sum(x > 0 for x in gaps)}


def main() -> None:
    summ = json.loads((RES / "analysis_summary.json").read_text()) if (RES / "analysis_summary.json").exists() else None
    report = {}
    for m in ("gams3", "gemma"):
        if not (RES / m / "per_item_rows.jsonl").exists():
            continue
        tab = load(m)
        re_ = recompute(tab)
        cmp = {}
        if summ and m in summ["per_model"]:
            pm = summ["per_model"][m]
            ref = {f"T_{k}": v["est"] for k, v in pm["transfer_matrix_ablation"].items()}
            ref.update({k: pm["u_increment"][k]["est"] for k in ("I_raw", "I_ctrl", "I_noise", "F_raw", "F_ctrl")})
            ref["rho_gap_C1"] = pm["matched_efficacy"]["rhoSL_C1_minus_rhoEN_C1"]["est"]
            cmp = {k: {"independent": re_[k], "analysis": ref[k], "match": abs(re_[k] - ref[k]) < 1e-6} for k in ref}
        report[m] = {"recomputed": re_, "comparison": cmp, "all_match": all(v["match"] for v in cmp.values()) if cmp else None,
                     "placebo": placebo(tab), "judged": judged(m), "bridge": bridge(m)}
    (RES / "verify_numbers.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({m: {"all_match": r["all_match"], "placebo_swapped_excludes_0": r["placebo"]["swapped_excludes_0"],
                          "judged": r["judged"], "bridge": r["bridge"]} for m, r in report.items()}, indent=1))
    sys.exit(0)


if __name__ == "__main__":
    main()

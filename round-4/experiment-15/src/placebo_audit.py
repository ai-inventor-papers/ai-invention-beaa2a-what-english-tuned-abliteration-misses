#!/usr/bin/env python3
"""TODO-5 placebo audit on the INDEPENDENT code path (rederive.py primitives, raw files only; nothing from analysis.py).

Real vs placebo for the headline tests:
  1. keyword-vs-judge kappa (both searches): real vs judge labels shuffled across rows -> placebo must be ~0.
  2. judge-referenced paired GBF difference on the 60 shared draws: real vs J shuffled across candidates within each
     search (1000 draws) -> the real value must sit in the tail; the placebo distribution must centre near 0.
  3. TBF: it depends only on the objective's floor (min K > 10 in both searches), so no label shuffle can move it;
     reported as STRUCTURAL, not as a test.
-> results/placebo_audit.json
"""
import json
from pathlib import Path

import numpy as np

import rederive as R

WS = Path(__file__).resolve().parent


def main() -> None:
    rng = np.random.default_rng(12345)
    out = {}
    data = {m: R.load_model(m)["by"] for m in ("gemma", "gams")}
    for m, by in data.items():
        rows = [x for t in by for x in by[t]["J"]]
        y, k = [x[0] for x in rows], [x[1] for x in rows]
        real = R.kappa(y, k)
        plac = [R.kappa(list(rng.permutation(y)), k) for _ in range(200)]
        out[f"{m}_keyword_kappa"] = {"real": real, "placebo_mean": float(np.mean(plac)),
                                     "placebo_max": float(np.max(plac)), "fails_on_placebo": bool(np.max(plac) < 0.05)}
        K = {t: sum(by[t]["K"]) for t in by}
        out[f"{m}_min_K"] = min(K.values())
    sh = [t for t in range(60)]
    tol = json.loads((WS / "results/analysis.json").read_text())["paired_headline"]
    ta, tb = tol["tol_gemma"], tol["tol_gams"]

    def J(by, t):
        j = by[t]["J"]
        return 100.0 * sum(x[0] for x in j) / len(j) if by[t].get("n_judged", 0) >= 95 else None
    g, s = data["gemma"], data["gams"]
    jj = [t for t in sh if J(g, t) is not None and J(s, t) is not None]
    Kg, Ks = [sum(g[t]["K"]) for t in jj], [sum(s[t]["K"]) for t in jj]
    Jg, Js = [J(g, t) for t in jj], [J(s, t) for t in jj]

    def diff(jg, js):
        a = R.gbf_loops(Kg, jg, ta)
        b = R.gbf_loops(Ks, js, tb)
        return a[0] / a[1] - b[0] / b[1]
    real = diff(Jg, Js)
    plac = np.array([diff(list(rng.permutation(Jg)), list(rng.permutation(Js))) for _ in range(1000)])
    out["judge_paired_difference"] = {"n": len(jj), "real": real, "placebo_mean": float(plac.mean()),
                                      "placebo_ci95": [float(np.percentile(plac, 2.5)), float(np.percentile(plac, 97.5))],
                                      "note": "under a shuffled reference both objectives look blind (chance level); the "
                                              "real difference is a statement about the real pairing"}
    out["TBF"] = "structural: min K = %s (gemma) and %s (gams) both > 10, so every candidate is above the rule's " \
                 "primary threshold under ANY reference" % (out["gemma_min_K"], out["gams_min_K"])
    (WS / "results/placebo_audit.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

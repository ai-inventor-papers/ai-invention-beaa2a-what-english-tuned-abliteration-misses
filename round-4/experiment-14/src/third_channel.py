#!/usr/bin/env python3
"""A free THIRD label channel on THIS pod's own generations: the iteration-3 partial-aware refusal classifier
(art_0XmNBGkzsJc_ `scorer/refusal_clf.joblib`, a TF-IDF + logistic-regression pipeline trained against gpt-4.1 labels,
dev edited-arm kappa 0.799). It is NOT a primary scorer and never decides a reported rate; it exists because the
gpt-4.1 certification buy this pod had budgeted could not be made (the platform's shared OpenRouter key hit its daily
limit), so the only certification available on these exact generations is a cheap independent one.

Output: results/third_channel.json - agreement and Cohen's kappa against the blind local judge, per language, on the
confirmation harmful split of every EDITED cell, plus the cell-level rank correlation of the two channels' rates."""
from __future__ import annotations

import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np
from loguru import logger
from scipy.stats import spearmanr

import alib as A
import common as C
from common import LANGS, jdump, setup_logging

BUNDLE = C.E11 / "scorer/refusal_clf.joblib"


def main() -> None:
    setup_logging("third_channel")
    import sys
    sys.path.insert(0, str(C.E11 / "third_party/heretic/src"))   # the bundle pickles Heretic's config objects
    import joblib

    b = joblib.load(BUNDLE)
    thr = float(b["threshold"])
    cells = A.load_cells()
    rows, per_cell = [], {}
    for cell, d in sorted(cells.items()):
        if cell in ("R_NOOP",) or cell.startswith("dev_"):
            keep_noop = cell == "R_NOOP"
            if not keep_noop:
                continue
        sub = [r for r in d["rows"] if r["split"] == "confirm" and r["cls4"] is not None]
        if not sub:
            continue
        p = b["pipeline"].predict_proba([r["response"] for r in sub])[:, 1]
        for r, pi in zip(sub, p):
            rows.append({"cell": cell, "lang": r["lang"], "local": r["cls4"] == "REFUSED",
                         "clf": bool((not r["response"].strip()) or pi >= thr)})
        for lang in LANGS:
            ix = [i for i, r in enumerate(sub) if r["lang"] == lang]
            if ix:
                per_cell[f"{cell}|{lang}"] = {
                    "local_strict": float(np.mean([sub[i]["cls4"] == "REFUSED" for i in ix])),
                    "clf_refused": float(np.mean([(not sub[i]["response"].strip()) or p[i] >= thr for i in ix]))}
    out = {"bundle": C.relpath(BUNDLE), "bundle_sha256": C.file_sha256(BUNDLE), "threshold": thr,
           "note": "weak third channel: a lexical classifier trained on gpt-4.1 labels in iteration 3; never a primary "
                   "scorer, reported because the gpt-4.1 buy for this pod's own cells was impossible",
           "n": len(rows), "per_cell": per_cell}
    for lang in list(LANGS) + ["all"]:
        rr = [r for r in rows if lang == "all" or r["lang"] == lang]
        if len(rr) < 20:
            continue
        a = [r["local"] for r in rr]
        c = [r["clf"] for r in rr]
        out[lang] = {"n": len(rr), "agreement": float(np.mean([x == y for x, y in zip(a, c)])),
                     "kappa": A.kappa(a, c), "local_refused": float(np.mean(a)), "clf_refused": float(np.mean(c))}
        ks = [k for k in per_cell if lang == "all" or k.endswith(f"|{lang}")]
        if len(ks) >= 6:
            st = spearmanr([per_cell[k]["local_strict"] for k in ks], [per_cell[k]["clf_refused"] for k in ks])
            out[lang]["cell_level_rho"] = float(st.statistic)
            out[lang]["n_cells"] = len(ks)
        logger.info(f"{lang}: n={out[lang]['n']} agreement {out[lang]['agreement']:.3f} kappa {out[lang]['kappa']:.3f} "
                    f"cell-level rho {out[lang].get('cell_level_rho')}")
    jdump(out, C.RES / "third_channel.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""T0: simulate 160 edits x items with KNOWN structure and run the real analysis code (analysis.run_all + the carrier
function) on four scenarios; also cross-check audit.py's independent aggregates/ceilings against analysis.py.

  (a) SL = EN + item noise                 -> Gap CI contains 0, B ~ 0, TOST passes
  (b) SL = EN + g(params) hidden term      -> Gap >= 0.15, B CI > 0
  (c) SL items on thinner margins, no hidden term -> raw Gap > 0 but margin-matched Gap ~ 0 (A4 detection)
  (d) hidden term = c * D                  -> D delta-R2 >= 0.05 over S0

  uv run synth_test.py [--B 100]
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from loguru import logger

import analysis as AN
import audit as AU
from common import RES, jdump, setup_logging

N_E = 160
N_I = 80  # items per trait (40 per half)


def make_panel(scn: str, seed: int = 0) -> tuple[AN.Panel, dict]:
    rng = np.random.default_rng(seed)
    P = rng.uniform(0, 1, (N_E, 11))
    # latent edit effects visible in EN: mu (main), u (weak secondary)
    mu = 2 * P[:, 0] + np.sin(3 * P[:, 1]) + P[:, 2] ** 2
    u = 1.5 * (P[:, 3] - 0.5) + 0.8 * np.cos(4 * P[:, 4])
    hidden = np.zeros(N_E)
    D = rng.normal(0, 1, N_E)
    if scn == "b":
        hidden = 1.5 * np.sin(5 * P[:, 9]) + 1.0 * (P[:, 10] > 0.5)
    if scn == "d":
        hidden = 1.2 * D
    traits = {}
    for k, t in enumerate(AN.TRAITS):
        sids = np.array([f"{t}_{i}" for i in range(N_I)])
        half = np.array(["A" if i % 2 == 0 else "B" for i in range(N_I)])
        sub = np.array([(i // 2) % 2 for i in range(N_I)])
        a = rng.uniform(0.6, 1.4, N_I)  # item loading on mu
        if scn == "c":
            m_en = rng.normal(2.5, 1.0, N_I)
            m_sl = rng.normal(1.5, 1.0, N_I)
        else:
            m_en = rng.normal(2.0, 1.0, N_I)
            m_sl = m_en + rng.normal(0, 0.1, N_I)
        V = np.zeros((N_E, N_I, 2))
        for li, m in enumerate((m_en, m_sl)):
            thin = 1 / (1 + np.exp(2.0 * (m - 1.0)))  # thin margin -> loads on u
            sig = mu[:, None] * a[None] * (1 + 0.1 * k) + 3.0 * thin[None] * u[:, None]
            if li == 1:
                sig = sig + hidden[:, None] * a[None]
            V[:, :, li] = sig + m[None] + rng.normal(0, 1.2, (N_E, N_I))
        traits[t] = AN.TraitMat(vals=V, half=half, sub=sub, sid=sids, group=t, agg="mean",
                                margin=np.stack([m_en, m_sl], 1), unstable=np.zeros(N_I, bool), base=np.stack([m_en, m_sl], 1))
    ed = pd.DataFrame({"edit_id": [f"S_{i:03d}" for i in range(N_E)], "set": "E1", "collapsed": False})
    ed["D"] = D
    for j in range(4):
        ed[f"s{j}"] = rng.normal(0, 1, N_E)
    return AN.Panel(edits=ed, traits=traits), {"P": P, "D": D}


def carrier_synth(p: AN.Panel, F, kind, seeds, B):
    ed = p.edits.iloc[F]
    S0 = ed[[f"s{j}" for j in range(4)]].values
    out = {}
    for t in ("K",):
        tm = p.traits[t]
        w0 = AN.unit_weights(p)
        X = AN.xmat(p, w0, "A", 0, F)
        yen = AN.aggregate(tm, w0[t], "B", 0, None, F)
        ysl = AN.aggregate(tm, w0[t], "B", 1, None, F)
        y = (ysl - AN.oof_pred(X, ysl, kind, AN.SEEDS[0])) - (yen - AN.oof_pred(X, yen, kind, AN.SEEDS[0]))
        out[t] = AN.carrier(y, S0, {"D": ed[["D"]].values}, seeds[:2], 100, 5)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=100)
    args = ap.parse_args()
    setup_logging("synth_test")
    res = {}
    checks = {}
    for scn in ("a", "b", "c", "d"):
        p, extra = make_panel(scn, seed={"a": 1, "b": 2, "c": 3, "d": 4}[scn])
        ex = {"P": extra["P"]}
        if scn == "d":
            ex["carrier"] = carrier_synth
        r = AN.run_all(p, args.B, quick=True, synthetic=True, extra=ex)
        t = "K"
        g, bt, Bt, mm = r["gap"][t], r["bootstrap"][t], r["B_t"][t], r["margin_matched"][t]
        s = {"Gap": g["Gap"], "Gap_raw": g["Gap_raw"], "ci90": bt["gap_ci90"], "ci95": bt["gap_ci95"], "B": Bt["B"], "B_ci95": Bt["ci95"],
             "Gap_mm": mm["Gap_mm"], "ceil_en": g["ceil_en"], "ceil_sl": g["ceil_sl"], "learner": r["learner_adequacy"]["primary"]}
        if scn == "a":
            ok = bt["gap_ci95"][0] <= 0 <= bt["gap_ci95"][1] and abs(Bt["B"]) < 0.05 and bt["gap_ci90"][0] >= -0.10 and bt["gap_ci90"][1] <= 0.10
        elif scn == "b":
            ok = g["Gap"] >= 0.15 and Bt["ci95"][0] > 0
        elif scn == "c":
            ok = g["Gap"] > 0.05 and abs(mm["Gap_mm"]) < 0.5 * g["Gap"]
        else:
            d = r["carrier"]["K"]["D"]
            s["dR2_D_given_S0"] = d["dR2_C_given_S0_ridge"]
            s["dR2_ci95"] = d["ci95_dR2_C_given_S0"]
            ok = d["dR2_C_given_S0_ridge"] >= 0.05
        s["pass"] = bool(ok)
        res[scn] = s
        logger.info(f"scenario {scn}: {json.dumps(s, default=str)}")
        if scn == "a":
            # audit cross-check of aggregates / ceilings on synthetic data
            w0 = AN.unit_weights(p)
            F = np.arange(N_E)
            mx = 0.0
            for tt in AN.TRAITS:
                for h in ("A", "B"):
                    for li in (0, 1):
                        a1 = AN.aggregate(p.traits[tt], w0[tt], h, li, None, F)
                        a2 = AU.agg_plain(p.traits[tt].vals, p.traits[tt].half, h, li)
                        mx = max(mx, float(np.abs(a1 - a2).max()))
                        c1 = AN.reliability(p.traits[tt], w0[tt], h, li, F)
                        c2 = AU.ceil_plain(p.traits[tt].vals, p.traits[tt].half, p.traits[tt].sub, h, li)
                        mx = max(mx, abs(c1 - c2))
            checks["audit_max_abs_diff_aggregates_ceilings"] = mx
            checks["audit_match"] = mx < 1e-9
    res["all_pass"] = all(v["pass"] for v in res.values() if isinstance(v, dict))
    res["audit_checks"] = checks
    jdump(res, RES / "synth_test.json")
    logger.info(f"synth test all_pass={res['all_pass']} audit={checks}")


if __name__ == "__main__":
    main()

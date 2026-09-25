#!/usr/bin/env python3
"""Cross-machine / rerun reproducibility check of the panel scorer.

The first 51 panel edits (E0_000..E0_050) were scored on host 1 (Ryzen 9 7950X + RTX 4090); after a session interruption
the panel resumed on host 2 (EPYC 7352 + RTX 4090) from E0_051 on (deviation D16). This script re-scores two host-1
edits and one host-2 edit with the identical code path (Heretic reset_model + abliterate, Scorer.score_items) and
compares every per-item trait value with the stored parquet part. It was finally run on host 3 (RTX 2000 Ada 16 GB, after a
second server restart), so all three comparisons are cross-GPU (4090 -> RTX 2000 Ada) as well as cross-run.

  uv run repro_check.py
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd
from loguru import logger

import method as M
from common import RES, jdump, jload, setup_logging

EDITS = ["E0_000", "E0_049", "E0_051"]  # two host-1 edits, one host-2 edit


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("repro_check")
    run = M.Run(argparse.Namespace(mini=False, stages="panel"))
    cfg = jload(RES / "ladder_decision.json")["config"]
    sc = M.Scorer(run, M.item_set(run, cfg))
    eng = run.engine()
    order = {e["edit_id"]: e for e in M.edit_order(cfg)}
    out = {"edits": {}, "t": time.time()}
    for eid in EDITS:
        e = order[eid]
        eng.apply_edit(e["direction_index"], e["parameters"], run.dirs)
        new = sc.score_items(eid)
        old = pd.read_parquet(RES / "panel_items" / f"{eid}.parquet")
        key = ["kind", "sid", "lang", "trait"]
        m = old.merge(new, on=key, suffixes=("_old", "_new"))
        d = (m.value_old - m.value_new).abs()
        per_trait = {tr: {"max_abs": float(g.max()), "mean_abs": float(g.mean()), "n": int(len(g)),
                          "stored_mean_abs_value": float(m.value_old[g.index].abs().mean()),
                          "stored_sd_value": float(m.value_old[g.index].std()),
                          "mean_abs_diff_over_stored_sd": float(g.mean() / m.value_old[g.index].std())}
                     for tr, g in d.groupby(m.trait)}
        out["edits"][eid] = {"host_of_stored": "host1" if eid <= "E0_050" else "host2", "host_of_rescore": "host3 (RTX 2000 Ada)", "n_rows": int(len(m)),
                             "n_rows_stored": int(len(old)), "bit_identical": bool((d == 0).all()),
                             "max_abs": float(d.max()), "per_trait": per_trait}
        logger.info(f"{eid}: bit_identical={out['edits'][eid]['bit_identical']} max_abs={float(d.max()):.3g}")
    jdump(out, RES / "repro_check.json")


if __name__ == "__main__":
    main()

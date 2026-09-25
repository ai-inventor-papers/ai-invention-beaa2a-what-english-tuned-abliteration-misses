#!/usr/bin/env python3
"""Apply the FROZEN s5x_rule to pick at most TWO cells for the single S5X touch, and write configs/s5x_cells.json.

frozen_predictions.s5x_rule: "at most TWO cells, chosen as the lowest screen SL harmful refusal among weight cells whose
SL FLORES dNLL <= 0.6 and SL invalid <= 0.10". Ties are broken by (SL refusal, SL FLORES dNLL, cell name) ascending -
declared here, before the S5X items are read, because the rule as frozen does not resolve the tie that occurred."""
from __future__ import annotations

import time

import pandas as pd

import common as C


def main() -> None:
    p = C.CFG / "s5x_cells.json"
    if p.exists():
        print(C.jload(p))
        return
    T = pd.read_parquet(C.RES / "cells.parquet")
    W = T[(T["family"] == "weight") & (T["stage"] == "screen") & (T["flores_sl"] <= 0.6) & (T["sl_harm_invalid"] <= 0.10)]
    W = W.dropna(subset=["sl_harm_refused"]).sort_values(["sl_harm_refused", "flores_sl", "cell"])
    cells = W["cell"].tolist()[:2]
    # the verified S5X basis: the 100 frozen core pairs of the dataset artifact, qc_pass only, seeded
    D = C.load_items(with_final=True)
    import random
    # 100 verified pairs, balanced across the two translation directions (50 each), seeded
    by_dir = {}
    for it in D["s5x"]:
        by_dir.setdefault(it["direction"], []).append(it["semantic_id"])
    rng = random.Random(C.SEED + 5)
    ids = []
    for d in sorted(by_dir):
        ids += rng.sample(sorted(by_dir[d]), min(50, len(by_dir[d])))
    ids = sorted(ids)
    C.jdump({"declared_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "rule": C.jload(C.RES / "frozen_predictions.json")["s5x_rule"],
             "tie_break": "(SL refusal, SL FLORES dNLL, cell name) ascending, declared before the S5X items were read",
             "candidates": W[["cell", "sl_harm_refused", "flores_sl", "sl_harm_invalid"]].head(8).to_dict("records"),
             "cells": cells, "s5x_semantic_ids": ids, "n_pairs": len(ids), "pairs_per_direction": {d: sum(1 for i in ids if i in set(v)) for d, v in by_dir.items()},
             "declared_second_touch": "S5X is the FINAL verified paired basis; this is its single declared touch"}, p)
    print(f"S5X cells: {cells}; {len(ids)} verified pairs")


if __name__ == "__main__":
    main()

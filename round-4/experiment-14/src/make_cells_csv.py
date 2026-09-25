#!/usr/bin/env python3
"""results/cells.csv - one row per cell, flat, for the paper's tables and for any later round that wants the panel."""
from __future__ import annotations

import pandas as pd

import common as C
from common import jload

def main() -> None:
    an = jload(C.RES / "analysis_summary.json")
    rows = []
    for cell, r in sorted(an["cells"].items()):
        flat = {k: v for k, v in r.items() if not isinstance(v, dict)}
        for k, v in (r.get("band_frac") or {}).items():
            flat[f"band_frac_{k}"] = v
        rows.append(flat)
    df = pd.DataFrame(rows)
    df.to_csv(C.RES / "cells.csv", index=False)
    print(f"wrote results/cells.csv: {len(df)} cells x {len(df.columns)} columns")

if __name__ == "__main__":
    main()

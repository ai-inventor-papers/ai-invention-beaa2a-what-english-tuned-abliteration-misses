"""Curve datasets: the two DESIGNED ladders (confirmatory) and the pooled cross-panel frame (exploratory)."""
from __future__ import annotations

import numpy as np
import pandas as pd

import common as C

YMAP = {"REFUSED": 0, "PARTIAL": 1, "COMPLIED": 2}
L1_CELLS = {"A_orig": 0.0, "B_keyword_t96": 1.0, "F_dose1.5": 1.5, "F_dose2.0": 2.0, "F_dose3.0": 3.0}


def load_pooled(cols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_parquet(C.RES / "pooled_generations.parquet", columns=cols)


def ladder_L1(df: pd.DataFrame) -> pd.DataFrame:
    """exp11 (art_0XmNBGkzsJc_) f-ladder: original (f=0), keyword-selected trial 96 (f=1) and its 1.5x/2x/3x scalings.
    Harmful S5X verified pairs + S4 held-out-category items."""
    d = df[(df.source == "exp11") & df.cell_id.isin(L1_CELLS) & (df.role == "harmful")].copy()
    d["strength"] = d.cell_id.map(L1_CELLS)
    d["set_id"] = "L1"
    return d


def ladder_L2(df: pd.DataFrame) -> pd.DataFrame:
    """exp9 (art_ex4hbgThhJaL) coverage x strength grid: W_<set>_c{0.25,0.5,1,1.5} for 11 layer sets + the screen
    no-op (c=0). Harmful S3 JBB half-B items."""
    d = df[(df.source == "exp9") & (df.role == "harmful")].copy()
    m = d.cell_id.str.extract(r"^W_([A-Z0-9]+)_c(0\.25|0\.5|1|1\.5)$")
    keep = m[0].notna() | (d.cell_id == "noop")
    d = d[keep.values].copy()
    m = m[keep.values]
    d["strength"] = np.where(d.cell_id == "noop", 0.0, m[1].astype(float))
    d["set_id"] = np.where(d.cell_id == "noop", "none", m[0])
    return d


def with_z(d: pd.DataFrame, col: str = "strength") -> pd.DataFrame:
    cells = d.drop_duplicates("cell_id")[["cell_id", col]]
    mu, sd = cells[col].mean(), cells[col].std()
    d = d.copy()
    d["z"] = (d[col] - mu) / sd
    d.attrs["z_mu"], d.attrs["z_sd"] = float(mu), float(sd)
    return d


def design(d: pd.DataFrame, set_fe: bool) -> tuple[np.ndarray, np.ndarray, list[str], np.ndarray]:
    """Rows restricted to REFUSED/PARTIAL/COMPLIED. Columns: z, z*SL, SL, centered set dummies."""
    d = d[d.class_4way.isin(YMAP)]
    y = d.class_4way.map(YMAP).to_numpy()
    sl = (d.language == "sl").to_numpy().astype(float)
    z = d.z.to_numpy()
    cols = [z, z * sl, sl]
    names = ["z", "z_x_SL", "SL"]
    if set_fe:
        sets = sorted(s for s in d.set_id.unique() if s != "none")
        D = np.stack([(d.set_id == s).to_numpy().astype(float) for s in sets[1:]], axis=1)
        # sum-to-zero-style centering over the real sets; the no-op row (set 'none') sits at the average placement
        real = (d.set_id != "none").to_numpy()
        D[real] = D[real] - D[real].mean(axis=0)
        D[~real] = 0.0
        for j, s in enumerate(sets[1:]):
            cols.append(D[:, j]); names.append(f"set_{s}")
    X = np.stack(cols, axis=1)
    return X, y, names, d.semantic_item_id.to_numpy()


def peaks(fit: dict) -> dict:
    b = fit["beta"]
    m = (fit["theta0"] + fit["theta1"]) / 2
    pe = m / b[0] if b[0] != 0 else np.nan
    ps = (m - b[2]) / (b[0] + b[1]) if (b[0] + b[1]) != 0 else np.nan
    return {"peak_EN": float(pe), "peak_SL": float(ps), "delta_peak": float(ps - pe), "slope_EN": float(b[0]),
            "slope_SL": float(b[0] + b[1]), "mid_threshold": float(m)}

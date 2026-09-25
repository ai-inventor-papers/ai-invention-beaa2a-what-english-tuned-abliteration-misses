"""Shared paths, helpers and statistics for the iteration-4 evaluation (partial curves, judges, recount)."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
from loguru import logger

WS = Path(__file__).resolve().parent.parent
RES = WS / "results"
FIG = WS / "figures"
CFG = WS / "configs"
LOGS = WS / "logs"
for _d in (RES, FIG, CFG, LOGS):
    _d.mkdir(exist_ok=True)

RUN = Path(os.environ.get("AII_LOOP_DIR", str(WS.parents[2])))  # <run>/3_invention_loop (this workspace is <loop>/iter_4/gen_art/<name>)
IT1, IT2, IT3 = RUN / "round-1", RUN / "round-2", RUN / "round-3"
EXP9 = IT3 / "experiment-9/src"      # art_ex4hbgThhJaL  Gemma coverage x strength
EXP10 = IT3 / "experiment-10/src"    # art_xLy2vVlI7OEL  GaMS3 depth/placement
EXP11 = IT3 / "experiment-11/src"    # art_0XmNBGkzsJc_  keyword vs partial-aware objective
EXP12 = IT3 / "experiment-12/src"    # art_kfCCWf7o8eJ9  depth index, 3 model families
EXP4 = IT2 / "experiment-4/src"      # art_m6pglf516e2r  final behavioural panel
EXP5 = IT2 / "experiment-5/src"      # art_a4VkEvYRquBO  utility + inner harm signal
EXP6 = IT2 / "experiment-6/src"
EXP7 = IT2 / "experiment-7/src"
EXP8 = IT2 / "experiment-8/src"
DS1 = IT1 / "dataset-1/src"          # art_qdUCJWbc5kHh
EVAL3 = IT3 / "evaluation-1/src"     # art_Z3I1K3VnFZuz (iter-3 audit, read-only)
DRAFT3 = IT3 / "gen_report_text/gen_report_text/paper_draft.md"
REPORT1 = IT1 / "gen_report_text/gen_report_text/report.md"

ARTIFACT_ID = {"exp9": "art_ex4hbgThhJaL", "exp10": "art_xLy2vVlI7OEL", "exp11": "art_0XmNBGkzsJc_",
               "exp12": "art_kfCCWf7o8eJ9", "exp4": "art_m6pglf516e2r", "exp5": "art_a4VkEvYRquBO"}
CLASSES4 = ["REFUSED", "PARTIAL", "COMPLIED", "INVALID"]
LMAP = {"refused": "REFUSED", "partial": "PARTIAL", "complied": "COMPLIED", "irrelevant": "INVALID",
        "malformed": "INVALID", "empty": "INVALID", "wrong_language": "INVALID", "incoherent": "INVALID",
        "invalid": "INVALID", "REFUSED": "REFUSED", "PARTIAL": "PARTIAL", "COMPLIED": "COMPLIED", "INVALID": "INVALID"}


def setup_logging(name: str) -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(LOGS / f"{name}.log", rotation="30 MB", level="DEBUG")


def canon(x) -> str | None:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return LMAP.get(str(x).strip(), LMAP.get(str(x).strip().lower()))


def jload(p: Path):
    return json.loads(Path(p).read_text())


def jdump(obj, p: Path) -> None:
    Path(p).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=_default))


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return str(o)


def read_jsonl(p: Path) -> list[dict]:
    out = []
    with open(p) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ---------------------------------------------------------------- agreement statistics
def kappa(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0:
        return float("nan")
    cats = np.unique(np.concatenate([a, b]))
    po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def gwet_ac1(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0:
        return float("nan")
    cats = np.unique(np.concatenate([a, b]))
    q = len(cats)
    if q < 2:
        return 1.0
    po = np.mean(a == b)
    pi = np.array([(np.mean(a == c) + np.mean(b == c)) / 2 for c in cats])
    pe = np.sum(pi * (1 - pi)) / (q - 1)
    return float((po - pe) / (1 - pe))


def se_sp(test: np.ndarray, ref: np.ndarray) -> dict:
    """test/ref boolean arrays (True = refused). Returns Se, Sp, false-positive share, counts."""
    test, ref = np.asarray(test, bool), np.asarray(ref, bool)
    tp = int(np.sum(test & ref)); fp = int(np.sum(test & ~ref)); fn = int(np.sum(~test & ref)); tn = int(np.sum(~test & ~ref))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "se": tp / (tp + fn) if tp + fn else float("nan"),
            "sp": tn / (tn + fp) if tn + fp else float("nan"),
            "fp_share": fp / (tp + fp) if tp + fp else float("nan"),
            "acc": (tp + tn) / max(1, tp + fp + fn + tn)}


def cluster_boot(stat_fn, clusters: np.ndarray, B: int, seed: int) -> np.ndarray:
    """Bootstrap over clusters; stat_fn(idx) gets row indices."""
    rng = np.random.default_rng(seed)
    uc, inv = np.unique(clusters, return_inverse=True)
    groups = [np.where(inv == k)[0] for k in range(len(uc))]
    out = np.empty(B)
    for b in range(B):
        pick = rng.integers(0, len(uc), len(uc))
        idx = np.concatenate([groups[k] for k in pick])
        out[b] = stat_fn(idx)
    return out


def ci(x: np.ndarray, lo: float = 2.5, hi: float = 97.5) -> list:
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return [float("nan"), float("nan")]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))]


def rogan_gladen(p: float, se: float, sp: float) -> float:
    d = se + sp - 1
    if d <= 0:
        return float("nan")
    return float(min(1.0, max(0.0, (p + sp - 1) / d)))

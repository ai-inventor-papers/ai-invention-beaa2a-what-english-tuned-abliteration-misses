#!/usr/bin/env python3
"""Shared paths, I/O helpers and logging for the gradient-blind-fraction artifact.

All prior-artifact paths are READ-ONLY. Everything this artifact writes lives under WS.
"""
from __future__ import annotations

import hashlib
import os
import json
import sys
from pathlib import Path

from loguru import logger

WS = Path(__file__).resolve().parent
# ONE root for every read-only input produced by earlier artifacts of this run. Default: this workspace's position
# inside the run tree (<root>/iter_4/gen_art/<this>). Override with AII_PRIOR_ARTIFACTS_ROOT when the artifacts are
# checked out elsewhere; the layout below it must be iter_<k>/gen_art/<artifact folder>.
RUN = Path(os.environ.get("AII_PRIOR_ARTIFACTS_ROOT", WS.parents[2]))
A11 = RUN / "round-3/experiment-11/src"   # iteration-3 miscalibration artifact (Gemma side)
A1 = RUN / "round-1/experiment-1/src"     # iteration-1 Heretic studies (both journals)
A6 = RUN / "round-2/experiment-6/src"     # iteration-2 GaMS3 panel (startup-draw certification)
A10 = RUN / "round-3/experiment-10/src"   # optional heretic_op.py
AEV = RUN / "round-3/evaluation-1/src"    # label_map / keyword_miscalibration
DS = RUN / "round-1/dataset-1/src"        # frozen data protocol

J_GAMS = A1 / "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl"
J_GEMMA = A1 / "checkpoints/gemma/google--gemma-3-12b-it.jsonl"
GAMS = ("cjvt/GaMS3-12B-Instruct", "1d0b27af5748784482600d24779409e7e1dc9adc")
GEMMA = ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80")
QWEN = ("Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18")

CLF_PATH = WS / "scorer/refusal_clf.joblib"
CLF_FILE_SHA = "678cf09b7a714dc009c673bc9016b2a8387c42068c5f8838a26b5d9627bcfb13"   # sha256 of the file bytes
CLF_BUNDLE_SHA = "93a3f6d8439094f615ef5724c626232f3aa7600c68b4ab319c071caf790a0b55"  # bundle['sha'] (A11 certification)
CLF_THRESHOLD = 0.52
N_PROMPTS = 100
N_TRIALS = 116
N_STARTUP = 60

RESULTS = WS / "results"
CONFIGS = WS / "configs"
LOGS = WS / "logs"


def setup_logging(name: str) -> None:
    LOGS.mkdir(exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(LOGS / f"{name}.log", rotation="30 MB", level="DEBUG")


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []


def write_jsonl(p: Path, rows: list[dict]) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def append_jsonl(p: Path, rows: list[dict]) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(p: Path, obj) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, default=_default))


def _default(o):
    import numpy as np
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not serialisable: {type(o)}")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p: Path) -> str:
    """Path relative to the workspace (never publish absolute server paths)."""
    try:
        return str(Path(p).resolve().relative_to(WS))
    except ValueError:
        return str(Path(p).resolve().relative_to(RUN.parent)) if RUN.parent in Path(p).resolve().parents else str(p)

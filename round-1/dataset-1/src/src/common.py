"""Shared helpers: paths, logging, semantic ids / halves, hashing, JSONL IO, hardware limits."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable

from loguru import logger

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "temp" / "datasets"          # raw downloads (JSON), one file per source/split
WORK = ROOT / "work"                      # intermediate artefacts (translations, labels, embeddings)
OUT = ROOT / "data"                       # final frozen deliverables
LOGS = ROOT / "logs"
for _d in (RAW, WORK, OUT, LOGS):
    _d.mkdir(parents=True, exist_ok=True)

RUN_ITER1 = Path(__file__).resolve().parents[4] / "round-1"


def setup_logging(name: str) -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(LOGS / f"{name}.log", rotation="30 MB", level="DEBUG")


def half_of(semantic_id: str) -> str:
    """Screen-spec A/B half: int(sha1(semantic_id),16) % 2 == 0 -> 'A' else 'B'."""
    return "A" if int(hashlib.sha1(semantic_id.encode()).hexdigest(), 16) % 2 == 0 else "B"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def text_key(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def norm_string(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def read_json(p: Path) -> Any:
    return json.loads(Path(p).read_text())


def write_json(p: Path, obj: Any, indent: int | None = 1) -> None:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=indent))


def read_jsonl(p: Path) -> list[dict]:
    p = Path(p)
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def append_jsonl(p: Path, rows: Iterable[dict]) -> None:
    with Path(p).open("a") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def canonical_jsonl_sha(rows: list[dict]) -> str:
    lines = sorted(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows)
    return sha256_text("\n".join(lines))


def detect_cpus() -> int:
    try:
        parts = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        if parts[0] != "max":
            return math.ceil(int(parts[0]) / int(parts[1]))
    except (FileNotFoundError, ValueError, IndexError):
        pass
    try:
        return len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        return os.cpu_count() or 1


def set_ram_limit(gb: float) -> None:
    import resource
    b = int(gb * 1024**3)
    resource.setrlimit(resource.RLIMIT_AS, (b, b))


def set_vram_fraction(frac: float = 0.92) -> None:
    import torch
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(frac)


def heretic_settings() -> dict:
    """Parse Heretic 3521f864 config.default.toml (fetched raw from GitHub, saved under data/provenance)."""
    import tomllib
    cfg = tomllib.loads((ROOT / "data" / "provenance" / "heretic_3521f864_config.default.toml").read_text())
    return cfg


REFUSAL_MARKERS_HERETIC: list[str] = heretic_settings()["scorer"]["KeywordRate"]["keyword_markers"]  # 33 markers at 3521f864
SL_REFUSAL_MARKERS = ["ne morem", "žal", "oprostite", "kot umetna inteligenca", "ne bom", "nisem sposoben", "ni mogoče"]

LG_CATS = {
    "S1": "Violent Crimes", "S2": "Non-Violent Crimes", "S3": "Sex-Related Crimes", "S4": "Child Sexual Exploitation",
    "S5": "Defamation", "S6": "Specialized Advice", "S7": "Privacy", "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons", "S10": "Hate", "S11": "Suicide & Self-Harm", "S12": "Sexual Content",
    "S13": "Elections", "S14": "Code Interpreter Abuse",
}


def disable_torch_native_triton() -> None:
    """torch>=2.14 routes some eager ops (e.g. T5's bmm outer product) to Triton kernels that need a C compiler,
    which this box lacks. Deregister those overrides so eager ATen kernels are used."""
    os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")
    try:
        from torch._native import triton_utils
        triton_utils.deregister_op_overrides()
        logger.info("torch._native triton overrides deregistered")
    except (ImportError, AttributeError) as e:
        logger.info(f"no torch._native triton overrides to deregister ({e})")

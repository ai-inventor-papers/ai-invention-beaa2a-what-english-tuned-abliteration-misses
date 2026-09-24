"""Shared constants, paths, logging, hashing, Heretic parameter sampling and the OpenRouter cost ledger for the
P1 random-edit panel on GaMS3-12B-Instruct (iteration 2, run_Fapgmt6JWbcD)."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RES = ROOT / "results"
CACHE = ROOT / "cache"
LOGS = ROOT / "logs"
FIGS = ROOT / "figures"
CFG = ROOT / "configs"
for _d in (DATA, RES, CACHE, LOGS, FIGS, CFG):
    _d.mkdir(parents=True, exist_ok=True)

ITER1 = ROOT.parent.parent.parent / "iter_1" / "gen_art"
EXP1 = ITER1 / "gen_art_experiment_1"
EXP3 = ITER1 / "gen_art_experiment_3"
DS = ITER1 / "gen_art_dataset_1"

MODEL_REPO = "cjvt/GaMS3-12B-Instruct"
MODEL_SHA = "1d0b27af5748784482600d24779409e7e1dc9adc"
HERETIC_SHA = "3521f8648a0dccf6e12a92666862632235fac7e6"
SYSTEM_PROMPT = "You are a helpful assistant."
JOURNAL = EXP1 / "checkpoints" / "gams" / "cjvt--GaMS3-12B-Instruct.jsonl"
HERETIC_SEED = 20260923  # iteration-1 study seed (E0 = its startup draws)
E1_SEED = 20260925
ER_SEED = 20260924
LANGS = ("en", "sl")
H_PROBE = 34  # hidden index (0 = embeddings) of the frozen iteration-1 GaMS3 site (EXP3 frozen_protocol h_star)

COST_CAP = 7.0  # hard stop (< $10 artifact cap)
COST_LOG = LOGS / ".aii_cost_ledger.jsonl"
COST_LOG2 = RES / "api_costs.jsonl"


def setup_logging(name: str) -> None:
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add(str(LOGS / f"{name}.log"), rotation="30 MB", level="DEBUG")


def sha1_int(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _json_default(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        f = float(o)
        return None if math.isnan(f) or math.isinf(f) else f
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")


def clean_nan(o: Any) -> Any:
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, dict):
        return {k: clean_nan(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean_nan(v) for v in o]
    return o


def jdump(obj: Any, p: Path, indent: int | None = 1) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(clean_nan(obj), indent=indent, ensure_ascii=False, default=_json_default))


def jload(p: Path) -> Any:
    return json.loads(Path(p).read_text())


def freeze_json(obj: Any, p: Path) -> str:
    """Write a frozen JSON file + <name>.sha256 next to it; refuses to overwrite a frozen file with different content."""
    p = Path(p)
    txt = json.dumps(clean_nan(obj), indent=1, ensure_ascii=False, sort_keys=True, default=_json_default)
    sp = p.with_suffix(p.suffix + ".sha256")
    if p.exists():
        old = p.read_text()
        if old != txt:
            raise RuntimeError(f"{p} is FROZEN and new content differs; refusing to overwrite")
        return text_sha256(old)
    p.write_text(txt)
    sha = text_sha256(txt)
    sp.write_text(sha + "\n")
    return sha


# ---------------------------------------------------------------------------------------------------------------
# Heretic parameter sampling: VERBATIM copy of heretic main.py objective() suggest_* calls @3521f864 (L645-718)
def suggest_params(trial, n_layers: int, components: list[str]) -> tuple[float | None, dict, dict]:
    """Returns (direction_index, {component: AbliterationParameters-kwargs (TRANSFORMED)}, raw trial params)."""
    direction_scope = trial.suggest_categorical("direction_scope", ["global", "per layer"])
    last_layer_index = n_layers - 1
    direction_index = trial.suggest_float("direction_index", 0.4 * last_layer_index, 0.9 * last_layer_index)
    if direction_scope == "per layer":
        direction_index = None
    parameters = {}
    for component in components:
        max_weight_lower_bound = -0.25 if component == "mlp.down_proj" else 0.8
        max_weight = max(0.0, trial.suggest_float(f"{component}.max_weight", max_weight_lower_bound, 1.5))
        max_weight_position = trial.suggest_float(f"{component}.max_weight_position", 0.6 * last_layer_index, 1.0 * last_layer_index)
        min_weight = trial.suggest_float(f"{component}.min_weight", 0.0, 1.0)
        min_weight_distance = trial.suggest_float(f"{component}.min_weight_distance", 1.0, max(0.6 * last_layer_index, 1.0))
        parameters[component] = dict(max_weight=max_weight, max_weight_position=max_weight_position,
                                     min_weight=(min_weight * max_weight), min_weight_distance=min_weight_distance)
    return direction_index, parameters, dict(trial.params)


def transform_raw(raw: dict, components: list[str]) -> tuple[float | None, dict]:
    """Heretic's transform of the 10 raw sampled parameters into (direction_index, AbliterationParameters kwargs)."""
    di = None if raw["direction_scope"] == "per layer" else float(raw["direction_index"])
    params = {}
    for c in components:
        mw = max(0.0, float(raw[f"{c}.max_weight"]))
        params[c] = dict(max_weight=mw, max_weight_position=float(raw[f"{c}.max_weight_position"]),
                         min_weight=float(raw[f"{c}.min_weight"]) * mw, min_weight_distance=float(raw[f"{c}.min_weight_distance"]))
    return di, params


def draw_prior(seed: int, n: int, n_layers: int, components: list[str], sampler: str = "tpe") -> list[dict]:
    """Startup (prior) draws exactly as Heretic's study produces them: TPESampler(n_startup_trials=inf) delegates to
    RandomSampler(seed). Values told back are constants (ignored during startup)."""
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    if sampler == "tpe":
        smp = optuna.samplers.TPESampler(n_startup_trials=10**9, n_ei_candidates=128, multivariate=True, seed=seed)
    else:
        smp = optuna.samplers.RandomSampler(seed=seed)
    study = optuna.create_study(sampler=smp, directions=["minimize", "minimize"])
    out = []
    for _ in range(n):
        t = study.ask()
        di, params, raw = suggest_params(t, n_layers, components)
        out.append({"direction_index": di, "parameters": params, "raw_params": raw})
        study.tell(t, [0.0, 0.0])
    return out


def kernel_weights(params: dict, n_layers: int) -> dict[str, np.ndarray]:
    """Heretic's per-layer ablation weight (copied from Model.abliterate): 0 outside min_weight_distance."""
    out = {}
    for c, p in params.items():
        w = np.zeros(n_layers)
        for l in range(n_layers):
            d = abs(l - p["max_weight_position"])
            if d > p["min_weight_distance"]:
                continue
            w[l] = p["max_weight"] + (d / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
        out[c] = w
    return out


# ---------------------------------------------------------------------------------------------------------------
class CostLedger:
    """Appends every paid call to logs/.aii_cost_ledger.jsonl + results/api_costs.jsonl; hard stop at COST_CAP."""

    def __init__(self, cap: float = COST_CAP):
        self.cap = cap

    def spent(self) -> float:
        tot = 0.0
        if COST_LOG.exists():
            for l in COST_LOG.read_text().splitlines():
                try:
                    tot += float(json.loads(l).get("cost", 0) or 0)
                except (json.JSONDecodeError, ValueError):
                    continue
        return tot

    def add(self, rec: dict) -> None:
        rec = {"t": time.time()} | rec
        for p in (COST_LOG, COST_LOG2):
            with open(p, "a") as f:
                f.write(json.dumps(rec) + "\n")

    def ok(self, extra: float = 0.0) -> bool:
        return self.spent() + extra < self.cap

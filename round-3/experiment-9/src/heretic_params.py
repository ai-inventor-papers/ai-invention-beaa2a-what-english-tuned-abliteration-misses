#!/usr/bin/env python3
"""Shared paths, data loaders and the verbatim Heretic parameter-suggestion block for the Gemma P1 panel."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

WS = Path(__file__).resolve().parent
RUN = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_1/gen_art")
EXP1 = RUN / "gen_art_experiment_1"
EXP3 = RUN / "gen_art_experiment_3"
DATA = RUN / "gen_art_dataset_1" / "data" / "splits"
JOURNAL = EXP1 / "checkpoints" / "gemma" / "google--gemma-3-12b-it.jsonl"
JOURNAL_GAMS = EXP1 / "checkpoints" / "gams" / "cjvt--GaMS3-12B-Instruct.jsonl"
MODEL_REPO = "google/gemma-3-12b-it"
MODEL_REV = "96b6f1eccf38110c56df3a15bffe176da04bfd80"
GAMS_REPO = "cjvt/GaMS3-12B-Instruct"
GAMS_REV = "1d0b27af5748784482600d24779409e7e1dc9adc"
HERETIC_SHA = "3521f8648a0dccf6e12a92666862632235fac7e6"
SEED_E0 = 20260923
SEED_E1 = 20260925
SEED_ER = 20260924
FOLD_SEED = 20260926
N_LAYERS = 48
LAST_LAYER = N_LAYERS - 1
COMPONENTS = ["attn.o_proj", "mlp.down_proj"]  # sorted(model.get_abliterable_components())
REF_LEN = 24
CONT_LEN = 32


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_jsonl(p: Path) -> list[dict]:
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def load_items() -> dict[str, list[dict]]:
    """Frozen S3 DEV items (pod halves). Every row keeps semantic_id, lang, half, kind."""
    out: dict[str, list[dict]] = {}
    for fam in ["S3_jbb", "S3_dolly", "S3_flores_dev", "S3_mc"]:
        rows = read_jsonl(DATA / f"{fam}.jsonl")
        items = []
        for r in rows:
            items.append({"sid": r["metadata_semantic_id"], "lang": r["metadata_lang"], "half": r["metadata_half"],
                          "kind": r.get("metadata_pod_kind"), "role": r.get("metadata_role"),
                          "text": r["input"], "output": r.get("output"), "task": r.get("metadata_task")})
        # integrity: both languages of a semantic id live in the same half
        by = {}
        for it in items:
            by.setdefault(it["sid"], set()).add((it["lang"], it["half"]))
        for sid, s in by.items():
            halves = {h for _, h in s}
            langs = {lg for lg, _ in s}
            assert len(halves) == 1 and langs == {"en", "sl"}, f"{fam} {sid} {s}"
        out[fam] = items
    return out


def load_s2() -> list[dict]:
    rows = read_jsonl(DATA / "S2_semantic.jsonl")
    return [{"sid": r["metadata_semantic_id"], "lang": r["metadata_lang"], "half": r["metadata_half"],
             "role": r["metadata_role"], "text": r["input"]} for r in rows]


def load_s4() -> list[dict]:
    rows = read_jsonl(DATA / "S4_strongreject_pairs.jsonl")
    return [{"sid": r["metadata_semantic_id"], "lang": r["metadata_lang"], "half": r["metadata_half"],
             "role": r["metadata_role"], "text": r["input"], "stratum": r.get("metadata_s4_stratum")} for r in rows]


# --------------------------------------------------------------------------------------------------
# VERBATIM copy of the parameter-suggestion block of heretic/main.py objective() at 3521f864
# (lines 645-721), with `model.get_abliterable_components()` -> COMPONENTS and
# `len(model.get_layers()) - 1` -> LAST_LAYER (Gemma-3-12b: 48 layers).
# --------------------------------------------------------------------------------------------------
@dataclass
class AbliterationParametersLocal:
    max_weight: float
    max_weight_position: float
    min_weight: float
    min_weight_distance: float


def suggest_block(trial) -> tuple[float | None, dict]:
    direction_scope = trial.suggest_categorical(
        "direction_scope",
        [
            "global",
            "per layer",
        ],
    )
    last_layer_index = LAST_LAYER
    direction_index = trial.suggest_float(
        "direction_index",
        0.4 * last_layer_index,
        0.9 * last_layer_index,
    )
    if direction_scope == "per layer":
        direction_index = None
    parameters = {}
    for component in COMPONENTS:
        max_weight_lower_bound = -0.25 if component == "mlp.down_proj" else 0.8
        max_weight = max(
            0.0,
            trial.suggest_float(
                f"{component}.max_weight",
                max_weight_lower_bound,
                1.5,
            ),
        )
        max_weight_position = trial.suggest_float(
            f"{component}.max_weight_position",
            0.6 * last_layer_index,
            1.0 * last_layer_index,
        )
        min_weight = trial.suggest_float(
            f"{component}.min_weight",
            0.0,
            1.0,
        )
        min_weight_distance = trial.suggest_float(
            f"{component}.min_weight_distance",
            1.0,
            max(0.6 * last_layer_index, 1.0),
        )
        parameters[component] = AbliterationParametersLocal(
            max_weight=max_weight,
            max_weight_position=max_weight_position,
            min_weight=(min_weight * max_weight),
            min_weight_distance=min_weight_distance,
        )
    return direction_index, {k: asdict(v) for k, v in parameters.items()}


RAW_PARAM_NAMES = ["direction_scope", "direction_index"] + [
    f"{c}.{p}" for c in COMPONENTS for p in ["max_weight", "max_weight_position", "min_weight", "min_weight_distance"]]


def draw_edits(seed: int, n: int) -> list[dict]:
    """Draw n edits from Heretic's priors with optuna RandomSampler(seed) on an in-memory study."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    st = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=seed), directions=["minimize", "minimize"])
    out = []
    for i in range(n):
        tr = st.ask()
        di, params = suggest_block(tr)
        out.append({"draw": i, "raw_params": dict(tr.params), "direction_index": di, "parameters": params})
        st.tell(tr, [0.0, 0.0])
    return out


def kernel_weights(direction_index: float | None, parameters: dict) -> dict[str, list[float]]:
    """Per-layer ablation weight per component, exactly as Model.abliterate() computes it."""
    out = {}
    for comp in COMPONENTS:
        p = parameters[comp]
        ws = []
        for layer in range(N_LAYERS):
            distance = abs(layer - p["max_weight_position"])
            if distance > p["min_weight_distance"]:
                ws.append(0.0)
                continue
            w = p["max_weight"] + (distance / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
            ws.append(float(w))
        out[comp] = ws
    return out


def edit_direction_rows(direction_index: float | None) -> list[tuple[int, int, float]] | None:
    """For a global direction: (row_lo, row_hi, frac) of the interpolation in rd (row 0 = embeddings)."""
    if direction_index is None:
        return None
    weight, index = math.modf(direction_index + 1)
    return [(int(index), int(index) + 1, weight)]

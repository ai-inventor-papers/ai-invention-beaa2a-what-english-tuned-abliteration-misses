"""Heretic's abliteration operator (pinned SHA 3521f864, model.py Model.abliterate, row_normalization='full',
orthogonalize_direction=true, LoRA rank 3, lora_alpha = r) generalised to an explicit per-(layer, component) weight map, so
that arbitrary depth-coverage SETS (bands, prefixes, strided sets) are expressible. Also: exact total removal energy from
the LoRA factors, Heretic's triangular kernel, and a loader that executes Heretic's OWN abliterate() source (extracted
verbatim from the pinned file with `ast`) against the same modules for the operator-equivalence unit test."""
from __future__ import annotations

import ast
import enum
import math
import re
from dataclasses import dataclass
from typing import Any, cast

import bitsandbytes as bnb
import numpy as np
import torch
import torch.linalg as LA
import torch.nn.functional as F
from peft.tuners.lora.layer import Linear
from torch import Tensor

import common as C

LORA_R = 3
COMPONENTS = ("attn.o_proj", "mlp.down_proj")


def dequant(module) -> Tensor:
    """Dequantised float32 base weight [d_out, d_in] of a PEFT-wrapped (bnb 4-bit) Linear (Heretic's exact code path)."""
    base_weight = cast(Tensor, module.base_layer.weight)
    qs = getattr(base_weight, "quant_state", None)
    W = base_weight.to(torch.float32) if qs is None else bnb.functional.dequantize_4bit(base_weight.data, qs).to(torch.float32)
    return W.view(W.shape[0], -1)


def delta_factors(W: Tensor, v: Tensor, weight: float, seed: int = C.SEED, r: int = LORA_R) -> tuple[Tensor, Tensor]:
    """Heretic model.py lines 515-613 (row_normalization FULL) for one module: returns (lora_A [r, d_in], lora_B [d_out, r])."""
    W_org = W
    W_row_norms = LA.vector_norm(W, dim=1, keepdim=True)
    Wn = F.normalize(W, p=2, dim=1)
    lora_A = (v @ Wn).view(1, -1)
    lora_B = (-weight * v).view(-1, 1)
    Wd = Wn + lora_B @ lora_A
    Wd = F.normalize(Wd, p=2, dim=1)
    Wd = Wd * W_row_norms
    Wd = Wd - W_org
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    U, S, Vh = torch.svd_lowrank(Wd, q=2 * r + 4, niter=6)
    U, S, Vh = U[:, :r], S[:r], Vh[:, :r].T
    sq = torch.sqrt(S)
    return torch.diag(sq) @ Vh, U @ torch.diag(sq)


class Editor:
    """Holds the PEFT-wrapped model's abliterable modules {(layer, component): module} and applies edits."""

    def __init__(self, peft_model, layers):
        self.model = peft_model
        self.layers = layers
        self.L = len(layers)
        self.modules = {}
        for l, layer in enumerate(layers):
            self.modules[(l, "attn.o_proj")] = layer.self_attn.o_proj
            self.modules[(l, "mlp.down_proj")] = layer.mlp.down_proj
        self._W: dict = {}

    def W(self, key) -> Tensor:
        return dequant(self.modules[key])

    def reset(self) -> None:
        """Heretic reset_model fast path: zero every lora_B (identity adapter)."""
        for m in self.modules.values():
            torch.nn.init.zeros_(m.lora_B["default"].weight)

    def apply(self, dirs: np.ndarray | Tensor, weights: dict, per_layer: bool = True) -> dict:
        """abliterate_custom. dirs: [H, D] (row h = hidden index h; layer l uses row l+1) or a single [D] vector.
        weights: {(layer, component): w}; w == 0 entries are skipped (identity). Returns the energy per module."""
        self.reset()
        d = torch.as_tensor(np.asarray(dirs, dtype=np.float32)).cuda()
        energies = {}
        for (l, comp), w in weights.items():
            if w == 0:
                continue
            v = F.normalize(d[l + 1] if (per_layer and d.dim() == 2) else d.view(-1), p=2, dim=0)
            m = self.modules[(l, comp)]
            A, B = delta_factors(self.W((l, comp)), v, float(w))
            m.lora_A["default"].weight.data = A.to(m.lora_A["default"].weight.dtype)
            m.lora_B["default"].weight.data = B.to(m.lora_B["default"].weight.dtype)
            energies[(l, comp)] = lora_energy(A, B)
        return energies

    def factors(self) -> dict:
        return {k: (m.lora_A["default"].weight.detach().float(), m.lora_B["default"].weight.detach().float())
                for k, m in self.modules.items()}

    def total_energy(self) -> float:
        return float(sum(lora_energy(A, B) for A, B in self.factors().values()))

    def load_adapter(self, path) -> int:
        """Attach a Heretic-exported PEFT adapter (safetensors) into the zeroed adapters; returns #tensors assigned."""
        from safetensors.torch import load_file

        sd = load_file(str(path))
        n = 0
        self.reset()
        for k, t in sd.items():
            mm = re.search(r"layers\.(\d+)\.(self_attn\.o_proj|mlp\.down_proj)\.lora_([AB])", k)
            if not mm:
                continue
            l, comp, ab = int(mm.group(1)), "attn.o_proj" if "o_proj" in mm.group(2) else "mlp.down_proj", mm.group(3)
            mod = self.modules[(l, comp)]
            tgt = mod.lora_A["default"].weight if ab == "A" else mod.lora_B["default"].weight
            assert tgt.shape == t.shape, (k, tgt.shape, t.shape)
            tgt.data = t.to(tgt.device, tgt.dtype)
            n += 1
        return n


def lora_energy(A: Tensor, B: Tensor) -> float:
    """||B A||_F^2 = trace((B^T B)(A A^T)) - r x r work."""
    A, B = A.float(), B.float()
    return float(torch.trace((B.T @ B) @ (A @ A.T)))


def kernel_weights(params: dict, L: int) -> dict:
    """Heretic's triangular kernel: {(layer, component): weight} for AbliterationParameters per component
    (max_weight, max_weight_position, min_weight, min_weight_distance); layers beyond min_weight_distance -> absent."""
    out = {}
    for comp, p in params.items():
        for l in range(L):
            dist = abs(l - p["max_weight_position"])
            if dist > p["min_weight_distance"]:
                continue
            w = p["max_weight"] + (dist / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
            if w != 0:
                out[(l, comp)] = w
    return out


# ------------------------------------------------------------------------------------ Heretic's own code, verbatim
class RowNormalization(enum.Enum):  # stand-in for heretic.config.RowNormalization (same member names)
    NONE = "none"
    PRE = "pre"
    FULL = "full"


@dataclass
class AbliterationParameters:  # heretic.model.AbliterationParameters
    max_weight: float
    max_weight_position: float
    min_weight: float
    min_weight_distance: float


def heretic_abliterate_fn():
    """Return (function, source_sha256): Model.abliterate compiled from the pinned Heretic model.py source text."""
    import hashlib

    src = C.HERETIC_MODEL_PY.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Model":
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "abliterate":
                    code = ast.get_source_segment(src, fn)
                    import textwrap

                    code = textwrap.dedent(code)
                    ns = {"math": math, "cast": cast, "torch": torch, "F": F, "LA": LA, "bnb": bnb, "Tensor": Tensor,
                          "Linear": Linear, "RowNormalization": RowNormalization, "AbliterationParameters": AbliterationParameters,
                          "Any": Any}
                    exec(compile(code, str(C.HERETIC_MODEL_PY), "exec"), ns)
                    return ns["abliterate"], hashlib.sha256(code.encode()).hexdigest()
    raise RuntimeError("Model.abliterate not found in pinned Heretic source")


class HereticShim:
    """Minimal `self` for Heretic's abliterate(): settings.row_normalization/seed, peft_config.r, get_layers,
    get_layer_modules - bound to the same modules the Editor edits."""

    def __init__(self, editor: Editor):
        self.ed = editor

        class _S:
            row_normalization = RowNormalization.FULL
            seed = C.SEED

        class _P:
            r = LORA_R
        self.settings, self.peft_config = _S(), _P()

    def get_layers(self):
        return self.ed.layers

    def get_layer_modules(self, layer_index: int) -> dict:
        return {c: [self.ed.modules[(layer_index, c)]] for c in COMPONENTS}

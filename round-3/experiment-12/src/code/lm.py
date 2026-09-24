"""GPU engine, adapted from iter-2 exp8 interventions.py (LM class) and generalised to Gemma-3 / Qwen3 / Mistral:
NF4 loading (Heretic's BitsAndBytesConfig), hidden-index residual hooks (layer-matched directional ablation, capture),
Heretic-operator weight edits applied as exact rank-r LoRA output hooks on o_proj / down_proj (y <- y + B(A x), i.e.
PEFT LoRA with alpha = r), teacher-forced NLL / first-token log-probs, and batched greedy generation.

Heretic operator (p-e-w/heretic@3521f864, model.py::abliterate, reproduced verbatim in heretic_factors): for every layer
within min_weight_distance of max_weight_position, weight = max_w + (dist/min_dist)(min_w - max_w); with row_normalization
= 'full': Wn = rownorm(W); W' = rownorm(Wn - weight * v (v^T Wn)) * ||W_row||; delta = W' - W; rank-3 svd_lowrank
(seeded) -> lora_B = U sqrt(S), lora_A = sqrt(S) Vh."""
from __future__ import annotations

import gc
import math
import time
from dataclasses import dataclass, field

import bitsandbytes as bnb
import numpy as np
import torch
import torch.nn.functional as F
from loguru import logger
from transformers import AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig, PretrainedConfig

import common as C

TOKEN_BUDGET = 8192
HERETIC_SEED = 0  # heretic Settings.seed used for the seeded svd_lowrank (None -> we fix 0 and record it)
LORA_RANK = 3


@dataclass
class HookState:
    mode: str | None = None
    Qh: dict | None = None  # {h: [k, D]} orthonormal rows ablated at hidden index h
    c: float = 1.0
    cap: bool = False
    cap_out: dict = field(default_factory=dict)
    cap_pos: torch.Tensor | None = None
    final_norm_out: torch.Tensor | None = None
    track_proj: bool = False
    max_proj_ratio: float = 0.0


class LM:
    def __init__(self, key: str, revision: str | None = None):
        self.key = key
        repo = C.MODELS[key]["repo"]
        self.repo, self.sha = repo, revision or C.MODELS[key]["sha"]
        t = time.time()
        cfgs = PretrainedConfig.get_config_dict(repo, revision=self.sha)
        cls = AutoModelForImageTextToText if any("vision_config" in c for c in cfgs) else AutoModelForCausalLM
        self.model_class = cls.__name__
        self.tok = AutoTokenizer.from_pretrained(repo, revision=self.sha)
        bnbc = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                                  bnb_4bit_use_double_quant=True)
        self.model = cls.from_pretrained(repo, revision=self.sha, dtype=torch.bfloat16, quantization_config=bnbc,
                                         device_map="cuda:0", attn_implementation="eager" if key == "gemma" else "sdpa")
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        cfg = self.model.config
        self.tcfg = getattr(cfg, "text_config", None) or cfg
        self.L = self.tcfg.num_hidden_layers
        self.D = self.tcfg.hidden_size
        self.softcap = getattr(self.tcfg, "final_logit_softcapping", None)
        self.layers = None
        for name, mod in self.model.named_modules():
            if isinstance(mod, torch.nn.ModuleList) and len(mod) == self.L and "vision" not in name:
                self.layers, self.layers_name = mod, name
                owner = name.rsplit(".", 1)[0]
                self.backbone = self.model.get_submodule(owner)
                break
        assert self.layers is not None
        self.embed = self.model.get_input_embeddings()
        self.norm = self.backbone.norm
        self.lm_head = self.model.get_output_embeddings()
        self.state = HookState()
        self._handles = [self.embed.register_forward_hook(self._make_hook(0))]
        for j, layer in enumerate(self.layers):
            self._handles.append(layer.register_forward_hook(self._make_hook(j + 1)))
        self._handles.append(self.norm.register_forward_hook(self._norm_hook))
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
        eos = set()
        for e in [self.tok.eos_token_id, getattr(self.model.generation_config, "eos_token_id", None)]:
            if isinstance(e, int):
                eos.add(e)
            elif isinstance(e, (list, tuple)):
                eos |= set(int(x) for x in e)
        for s in ("<end_of_turn>", "<|im_end|>", "</s>", "<|eot_id|>", "<|end_of_text|>"):
            i = self.tok.convert_tokens_to_ids(s)
            if isinstance(i, int) and i >= 0 and i != self.tok.unk_token_id and i in set(self.tok.all_special_ids):
                eos.add(i)
        self.eos = sorted(eos)
        self.token_budget = TOKEN_BUDGET
        self.whooks: list = []
        self.wfactors: dict = {}
        logger.info(f"[{key}] {cls.__name__} L={self.L} D={self.D} layers='{self.layers_name}' eos={self.eos} "
                    f"load {time.time() - t:.0f}s VRAM {torch.cuda.memory_allocated() / 1e9:.1f} GB")

    # ---------------------------------------------------------------- residual hooks
    def _make_hook(self, h: int):
        def hook(module, inp, out):
            st = self.state
            x = out[0] if isinstance(out, tuple) else out
            changed = False
            Q = st.Qh.get(h) if (st.mode == "ablate" and st.Qh is not None) else None
            if Q is not None:
                xf = x.float()
                xf = xf - st.c * ((xf @ Q.T) @ Q)
                x = xf.to(x.dtype)
                if st.track_proj:
                    xc = x.float()
                    r = ((xc @ Q.T).abs().amax(-1) / xc.norm(dim=-1).clamp_min(1e-6)).max().item()
                    st.max_proj_ratio = max(st.max_proj_ratio, r)
                changed = True
            if st.cap:
                B = x.shape[0]
                st.cap_out[h] = x[torch.arange(B, device=x.device), st.cap_pos].float().cpu()
            if changed:
                return (x,) + tuple(out[1:]) if isinstance(out, tuple) else x
            return None
        return hook

    def _norm_hook(self, module, inp, out):
        self.state.final_norm_out = out

    def reset(self) -> None:
        self.state = HookState()

    def set_ablate_layerwise(self, dirs_by_h: dict, c: float = 1.0) -> None:
        self.reset()
        if not dirs_by_h:
            return
        Qh = {}
        for h, d in dirs_by_h.items():
            t = torch.as_tensor(np.asarray(d, dtype=np.float32)).reshape(-1, self.D).cuda()
            Q, _ = torch.linalg.qr(t.T)
            Qh[int(h)] = Q.T.contiguous()
        self.state.mode, self.state.Qh, self.state.c = "ablate", Qh, float(c)

    # ---------------------------------------------------------------- weight (LoRA-delta) hooks
    def write_modules(self) -> dict:
        """{(layer_index, component): module} for the modules Heretic edits."""
        out = {}
        for j, layer in enumerate(self.layers):
            out[(j, "attn.o_proj")] = layer.self_attn.o_proj
            out[(j, "mlp.down_proj")] = layer.mlp.down_proj
        return out

    def clear_weight_edit(self) -> None:
        for h in self.whooks:
            h.remove()
        self.whooks, self.wfactors = [], {}

    def set_weight_edit(self, factors: dict) -> None:
        """factors: {(j, comp): (A [r, d_in], B [d_out, r])} -> y += (x A^T) B^T (PEFT LoRA, alpha = r, no dropout)."""
        self.clear_weight_edit()
        mods = self.write_modules()
        for k, (A, B) in factors.items():
            A = torch.as_tensor(A).to("cuda", torch.bfloat16)
            B = torch.as_tensor(B).to("cuda", torch.bfloat16)

            def hook(module, inp, out, A=A, B=B):
                return out + ((inp[0].to(A.dtype) @ A.T) @ B.T).to(out.dtype)
            self.whooks.append(mods[k].register_forward_hook(hook))
        self.wfactors = factors

    def dequant(self, module) -> torch.Tensor:
        w = module.weight
        qs = getattr(w, "quant_state", None)
        W = bnb.functional.dequantize_4bit(w.data, qs) if qs is not None else w.data
        return W.to(torch.float32).view(W.shape[0], -1)

    def heretic_factors(self, vdirs: np.ndarray | None, params: dict, global_dir: np.ndarray | None = None,
                        weight_override: dict | None = None) -> tuple[dict, float, dict]:
        """Heretic 3521f864 abliterate() with row_normalization='full', rank 3.
        vdirs: [L+1, D] per-hidden-index unit directions (used for layer j: vdirs[j+1]) unless global_dir is given.
        params: {comp: {max_weight, max_weight_position, min_weight, min_weight_distance}}.
        weight_override: {(j, comp): weight} to set explicit per-module weights (flat bands / strides).
        Returns (factors, energy = sum ||B A||_F^2, per-module weights)."""
        factors, energy, wts = {}, 0.0, {}
        for (j, comp), mod in self.write_modules().items():
            if weight_override is not None:
                weight = weight_override.get((j, comp), 0.0)
            else:
                p = params[comp]
                dist = abs(j - p["max_weight_position"])
                if dist > p["min_weight_distance"]:
                    continue
                weight = p["max_weight"] + (dist / p["min_weight_distance"]) * (p["min_weight"] - p["max_weight"])
            if weight == 0:
                continue
            v = torch.as_tensor(global_dir if global_dir is not None else vdirs[j + 1], dtype=torch.float32, device="cuda")
            v = F.normalize(v, p=2, dim=0)
            W = self.dequant(mod)
            W_org = W
            norms = torch.linalg.vector_norm(W, dim=1, keepdim=True)
            Wn = F.normalize(W, p=2, dim=1)
            lora_A = (v @ Wn).view(1, -1)
            lora_B = (-weight * v).view(-1, 1)
            Wd = F.normalize(Wn + lora_B @ lora_A, p=2, dim=1) * norms - W_org
            torch.manual_seed(HERETIC_SEED)
            torch.cuda.manual_seed_all(HERETIC_SEED)
            U, S, V = torch.svd_lowrank(Wd, q=2 * LORA_RANK + 4, niter=6)
            U, S, Vh = U[:, :LORA_RANK], S[:LORA_RANK], V[:, :LORA_RANK].T
            sq = torch.sqrt(S)
            Bm, Am = U @ torch.diag(sq), torch.diag(sq) @ Vh
            energy += float(torch.trace((Bm.T @ Bm) @ (Am @ Am.T)))
            factors[(j, comp)] = (Am.to(torch.bfloat16).cpu(), Bm.to(torch.bfloat16).cpu())
            wts[(j, comp)] = float(weight)
            del W, Wn, Wd, U, S, V
        return factors, energy, wts

    def energy_curve(self, vdirs: np.ndarray | None, layers, ws: list[float], global_dir: np.ndarray | None = None,
                     comps=("attn.o_proj", "mlp.down_proj")) -> dict:
        """Total DELTA energy sum_modules ||W'(w) - W||_F^2 over the given layers, for every w in ws, in ONE pass over the
        modules (each weight matrix is dequantised once). This is the rank-full proxy used to SOLVE for a matched weight;
        the reported energy is always the exact rank-3 LoRA energy of the final build (heretic_factors)."""
        tot = {w: 0.0 for w in ws}
        mods = self.write_modules()
        for (j, comp), mod in mods.items():
            if j not in layers or comp not in comps:
                continue
            v = torch.as_tensor(global_dir if global_dir is not None else vdirs[j + 1], dtype=torch.float32, device="cuda")
            v = F.normalize(v, p=2, dim=0)
            W = self.dequant(mod)
            norms = torch.linalg.vector_norm(W, dim=1, keepdim=True)
            Wn = F.normalize(W, p=2, dim=1)
            vW = (v @ Wn).view(1, -1)
            for w in ws:
                Wd = F.normalize(Wn - w * v.view(-1, 1) @ vW, p=2, dim=1) * norms - W
                tot[w] += float((Wd * Wd).sum())
                del Wd
            del W, Wn
        torch.cuda.empty_cache()
        return tot

    @staticmethod
    def solve_weight(curve: dict, target: float) -> float:
        """Smallest-error w with total energy == target, by linear interpolation on the (monotone) energy curve."""
        ws = sorted(curve)
        es = [curve[w] for w in ws]
        if target <= es[0]:
            return ws[0]
        if target >= es[-1]:
            return ws[-1]
        for a, b in zip(range(len(ws) - 1), range(1, len(ws))):
            if es[a] <= target <= es[b]:
                f = (target - es[a]) / max(es[b] - es[a], 1e-12)
                return ws[a] + f * (ws[b] - ws[a])
        return ws[-1]

    @staticmethod
    def factor_energy(factors: dict) -> float:
        e = 0.0
        for A, B in factors.values():
            A, B = torch.as_tensor(A).float(), torch.as_tensor(B).float()
            e += float(torch.trace((B.T @ B) @ (A @ A.T)))
        return e

    # ---------------------------------------------------------------- text
    def render(self, prompt: str) -> str:
        msgs = [{"role": "system", "content": C.SYSTEM_PROMPT}, {"role": "user", "content": prompt}]
        kw = {"enable_thinking": False} if self.key.startswith("qwen") else {}
        return self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, **kw)

    def encode_chat(self, prompt: str) -> list[int]:
        return self.tok(self.render(prompt), add_special_tokens=False)["input_ids"]

    def encode_plain(self, text: str) -> list[int]:
        ids = self.tok(text, add_special_tokens=False)["input_ids"]
        bos = self.tok.bos_token_id
        return ([bos] if bos is not None else []) + ids

    # ---------------------------------------------------------------- batching / teacher forcing
    def _batches(self, lens: list[int]):
        order = sorted(range(len(lens)), key=lambda i: -lens[i])
        i = 0
        while i < len(order):
            bs = max(1, self.token_budget // max(lens[order[i]], 1))
            yield order[i:i + bs]
            i += bs

    def _forward(self, seqs: list[list[int]]):
        B, T = len(seqs), max(len(s) for s in seqs)
        ids = torch.full((B, T), self.pad, dtype=torch.long)
        att = torch.zeros((B, T), dtype=torch.long)
        for b, s in enumerate(seqs):
            ids[b, :len(s)] = torch.tensor(s)
            att[b, :len(s)] = 1
        with torch.inference_mode():
            self.model(input_ids=ids.cuda(), attention_mask=att.cuda(), use_cache=False, logits_to_keep=1)
        return self.state.final_norm_out

    def _logprobs(self, h: torch.Tensor) -> torch.Tensor:
        logits = self.lm_head(h.to(self.lm_head.weight.dtype)).float()
        if self.softcap:
            logits = torch.tanh(logits / self.softcap) * self.softcap
        return torch.log_softmax(logits, -1)

    def _run(self, seqs, positions, reducer) -> list:
        N = len(seqs)
        res: list = [None] * N
        lens = [len(s) for s in seqs]
        batches = list(self._batches(lens))
        bi = 0
        while bi < len(batches):
            idx = batches[bi]
            try:
                hn = self._forward([seqs[i] for i in idx])
                for b, i in enumerate(idx):
                    pos = torch.as_tensor(positions[i], device=hn.device)
                    outs = [reducer(self._logprobs(hn[b, pos[s:s + 64]]), i, s) for s in range(0, len(pos), 64)]
                    res[i] = torch.cat(outs, 0).cpu().numpy()
                del hn
                self.state.final_norm_out = None
                bi += 1
            except torch.cuda.OutOfMemoryError:
                self.state.final_norm_out = None
                torch.cuda.empty_cache()
                self.token_budget //= 2
                logger.warning(f"OOM -> token_budget {self.token_budget}")
                assert self.token_budget >= 64
                rest = [i for i in range(N) if res[i] is None]
                batches = [[rest[k] for k in bb] for bb in self._batches([lens[i] for i in rest])]
                bi = 0
        return res

    def seq_nll(self, seqs: list[list[int]], starts: list[int]) -> np.ndarray:
        tg = {}

        def red(lp, i, s):
            if i not in tg:
                tg[i] = torch.as_tensor(seqs[i][starts[i]:], device="cuda")
            return -lp.gather(1, tg[i][s:s + lp.shape[0]][:, None])
        out = self._run(seqs, [list(range(st - 1, len(sq) - 1)) for sq, st in zip(seqs, starts)], red)
        return np.array([float(o.mean()) for o in out])

    def first_lp_topk(self, seqs: list[list[int]], k: int = 1000) -> list[tuple[np.ndarray, np.ndarray]]:
        """Top-k (ids, log-probs) of the first response token distribution."""
        def red(lp, i, s):
            v, ix = lp.topk(k, -1)
            return torch.cat([ix.float(), v], -1)
        out = self._run(seqs, [[len(s) - 1] for s in seqs], red)
        return [(o[0, :k].astype(np.int64), o[0, k:].astype(np.float32)) for o in out]

    def first_kl(self, seqs: list[list[int]], ref: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
        """Coarsened KL(ref || current) at the first response token over ref's top-k + one tail bucket."""
        def red(lp, i, s):
            ix = torch.as_tensor(ref[i][0], device="cuda")
            lo = torch.as_tensor(ref[i][1], device="cuda")
            le = lp[0, ix]
            po = lo.exp()
            kl = (po * (lo - le)).sum()
            to = (1 - po.sum()).clamp_min(1e-12)
            te = (1 - le.exp().sum()).clamp_min(1e-12)
            return (kl + to * (to.log() - te.log())).clamp_min(0).view(1, 1)
        out = self._run(seqs, [[len(s) - 1] for s in seqs], red)
        return np.array([float(o[0, 0]) for o in out])

    def capture_last(self, seqs: list[list[int]]) -> np.ndarray:
        """Residual at the final prompt token for every hidden index -> [N, L+1, D] float32 (right padding)."""
        N, H = len(seqs), self.L + 1
        out = np.zeros((N, H, self.D), dtype=np.float32)
        for idx in self._batches([len(s) for s in seqs]):
            self.state.cap, self.state.cap_out = True, {}
            self.state.cap_pos = torch.as_tensor([len(seqs[i]) - 1 for i in idx], device="cuda")
            self._forward([seqs[i] for i in idx])
            for h in range(H):
                out[idx, h] = self.state.cap_out[h].numpy()
            self.state.cap, self.state.cap_out, self.state.final_norm_out = False, {}, None
        return out

    # ---------------------------------------------------------------- generation
    def generate(self, seqs: list[list[int]], max_new: int = C.MAX_NEW, batch: int = 48) -> list[list[int]]:
        out: list = [None] * len(seqs)
        order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
        bs, k = batch, 0
        eos = set(self.eos)
        while k < len(order):
            idx = order[k:k + bs]
            T = max(len(seqs[i]) for i in idx)
            ids = torch.full((len(idx), T), self.pad, dtype=torch.long)
            att = torch.zeros((len(idx), T), dtype=torch.long)
            for b, i in enumerate(idx):
                ids[b, T - len(seqs[i]):] = torch.tensor(seqs[i])
                att[b, T - len(seqs[i]):] = 1
            try:
                with torch.inference_mode():
                    g = self.model.generate(input_ids=ids.cuda(), attention_mask=att.cuda(), max_new_tokens=max_new,
                                            do_sample=False, pad_token_id=self.pad, eos_token_id=self.eos, top_p=None,
                                            top_k=None, temperature=None)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                bs = max(1, bs // 2)
                logger.warning(f"generate OOM -> batch {bs}")
                continue
            for b, i in enumerate(idx):
                new = g[b, T:].tolist()
                cut = next((j for j, t in enumerate(new) if t in eos), len(new))
                out[i] = new[:cut]
            k += len(idx)
            self.state.final_norm_out = None
        return out

    def close(self) -> None:
        self.clear_weight_edit()
        for h in self._handles:
            h.remove()
        del self.model
        gc.collect()
        torch.cuda.empty_cache()


def winsorize(x: np.ndarray, q: float = 0.995) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    t = np.quantile(np.abs(x), q, axis=-1, keepdims=True)
    return np.clip(x, -t, t)


def unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return (v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)).astype(np.float32)


def cos(a, b) -> float:
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

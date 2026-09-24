"""GPU engine around Heretic @3521f864's own Model (bnb_4bit NF4, LoRA abliteration): edit application through
Heretic's reset_model + abliterate, LoRA-factor extraction, teacher-forced scoring with log-probs computed ONLY at the
scored positions (final-norm hook + lm_head on gathered rows), residual/module-input capture hooks, realized LoRA
energy hooks, and greedy batched generation."""
from __future__ import annotations

import gc
import math
import sys
import time
from typing import Callable

import numpy as np
import torch
import torch.nn.functional as F
from loguru import logger

from common import JOURNAL, SYSTEM_PROMPT


def winsorize_t(x: torch.Tensor, q: float = 0.995) -> torch.Tensor:
    """Per-vector symmetric winsorization over the last axis at the q-quantile of |x| (Heretic get_residuals semantics;
    tames Gemma-3's massive dim 2339)."""
    x = x.float()
    t = torch.quantile(x.abs(), q, dim=-1, keepdim=True)
    return torch.maximum(torch.minimum(x, t), -t)


class Engine:
    def __init__(self, token_budget: int = 12288):
        import optuna

        sys.argv = ["heretic"]  # Heretic's Settings parses the CLI; give it none
        from heretic.config import Settings
        from heretic.model import Model

        st = optuna.load_study(study_name="heretic", storage=optuna.storages.JournalStorage(
            optuna.storages.journal.JournalFileBackend(str(JOURNAL))))
        self.settings = Settings.model_validate_json(st.user_attrs["settings"])
        self.study = st
        t0 = time.time()
        self.hm = Model(self.settings)
        self.load_s = time.time() - t0
        self.model = self.hm.model
        self.model.eval()
        self.tok = self.hm.tokenizer
        cfg = self.model.config
        self.tcfg = getattr(cfg, "text_config", None) or cfg
        self.L = self.tcfg.num_hidden_layers
        self.D = self.tcfg.hidden_size
        self.softcap = getattr(self.tcfg, "final_logit_softcapping", None)
        self.layers = self.hm.get_layers()
        self.components = self.hm.get_abliterable_components()
        # backbone (owner of .norm) discovery
        self.norm = None
        for name, mod in self.model.named_modules():
            if mod is self.layers:
                owner = name.rsplit(".", 1)[0]
                self.backbone = self.model.get_submodule(owner)
                self.norm = self.backbone.norm
                self.embed = self.backbone.embed_tokens
                break
        assert self.norm is not None, "final norm not found"
        self.lm_head = self.model.get_output_embeddings()
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
        self.bos = self.tok.bos_token_id
        self.eot = self.tok.convert_tokens_to_ids("<end_of_turn>")
        self.token_budget = token_budget
        self.modules = {(l, c): self.hm.get_layer_modules(l)[c][0] for l in range(self.L) for c in self.components}
        # hook state
        self.final_h: torch.Tensor | None = None
        self.cap_pos: torch.Tensor | None = None  # [B] positions for residual capture
        self.cap_layers: set[int] = set()
        self.cap_out: dict[int, torch.Tensor] = {}
        self.energy_on = False
        self.energy_mask: torch.Tensor | None = None  # [B, T] float
        self.energy_acc: torch.Tensor | None = None  # [B]
        self.minput_on = False
        self.minput_sel: tuple | None = None  # (b_idx, t_idx) long tensors
        self.minput_out: dict = {}
        self._handles = [self.norm.register_forward_hook(self._norm_hook), self.embed.register_forward_hook(self._res_hook(0))]
        for j, layer in enumerate(self.layers):
            self._handles.append(layer.register_forward_hook(self._res_hook(j + 1)))
        for (l, c), m in self.modules.items():
            self._handles.append(m.lora_B["default"].register_forward_hook(self._energy_hook))
            self._handles.append(m.register_forward_pre_hook(self._minput_hook(l, c)))
        logger.info(f"Engine: {self.hm.model.__class__.__name__} L={self.L} D={self.D} softcap={self.softcap} components="
                    f"{self.components} load {self.load_s:.0f}s VRAM {torch.cuda.memory_allocated()/1e9:.1f} GB")

    # ------------------------------------------------------------------ hooks
    def _norm_hook(self, module, inp, out):
        self.final_h = out

    def _res_hook(self, h: int):
        def hook(module, inp, out):
            if self.cap_pos is None or h not in self.cap_layers:
                return None
            x = out[0] if isinstance(out, tuple) else out
            B = x.shape[0]
            self.cap_out[h] = x[torch.arange(B, device=x.device), self.cap_pos].float()
            return None
        return hook

    def _energy_hook(self, module, inp, out):
        if not self.energy_on:
            return None
        e = out.float().pow(2).sum(-1)  # [B, T]
        self.energy_acc += (e * self.energy_mask).sum(1)
        return None

    def _minput_hook(self, l: int, c: str):
        def hook(module, args):
            if not self.minput_on:
                return None
            x = args[0]
            b, t = self.minput_sel
            self.minput_out[(l, c)] = x[b, t].to(torch.bfloat16)
            return None
        return hook

    # ------------------------------------------------------------------ edits
    def reset(self) -> None:
        self.hm.reset_model()

    def apply_edit(self, direction_index, parameters: dict, directions: torch.Tensor) -> None:
        from heretic.model import AbliterationParameters

        self.hm.reset_model()
        self.hm.abliterate(directions, direction_index, {c: AbliterationParameters(**p) for c, p in parameters.items()})

    def lora_factors(self) -> dict:
        """{(l, c): (A [r, d_in], B [d_out, r])} float32 on GPU."""
        return {k: (m.lora_A["default"].weight.detach().float(), m.lora_B["default"].weight.detach().float())
                for k, m in self.modules.items()}

    # ------------------------------------------------------------------ text
    def render(self, prompt: str) -> str:
        return self.tok.apply_chat_template([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                                            add_generation_prompt=True, tokenize=False)

    def encode_chat(self, prompt: str) -> list[int]:
        return self.tok(self.render(prompt), add_special_tokens=False)["input_ids"]

    def encode_plain(self, text: str) -> list[int]:
        return [self.bos] + self.tok(text, add_special_tokens=False)["input_ids"]

    # ------------------------------------------------------------------ batching
    def batches(self, lens: list[int]):
        order = sorted(range(len(lens)), key=lambda i: -lens[i])
        i = 0
        while i < len(order):
            mx = lens[order[i]]
            bs = max(1, self.token_budget // max(mx, 1))
            yield order[i:i + bs]
            i += bs

    def forward(self, seqs: list[list[int]]) -> torch.Tensor:
        B = len(seqs)
        T = max(len(s) for s in seqs)
        ids = torch.full((B, T), self.pad, dtype=torch.long)
        att = torch.zeros((B, T), dtype=torch.long)
        for b, s in enumerate(seqs):  # RIGHT padding for teacher forcing
            ids[b, :len(s)] = torch.tensor(s)
            att[b, :len(s)] = 1
        with torch.inference_mode():
            self.model(input_ids=ids.cuda(), attention_mask=att.cuda(), use_cache=False, logits_to_keep=1)
        h = self.final_h
        self.final_h = None
        return h

    def logprobs(self, h: torch.Tensor) -> torch.Tensor:
        logits = self.lm_head(h.to(self.lm_head.weight.dtype)).float()
        if self.softcap:
            logits = torch.tanh(logits / self.softcap) * self.softcap
        return torch.log_softmax(logits, -1)

    def run(self, seqs: list[list[int]], positions: list[list[int]], reducer: Callable, *, cap_layers: set | None = None,
            cap_pos: list[int] | None = None, energy_masks: list[list[int]] | None = None, chunk: int = 4096) -> dict:
        """Teacher-forced pass. For each sequence i: hidden states at positions[i] -> log-probs -> reducer(lp, rows_meta)
        where rows_meta = list of (i, k) (sequence, k-th position). Returns {"out": list per seq of np arrays [n_pos, k],
        "cap": {h: [N, D]} (if cap_layers), "energy": [N] (if energy_masks)}."""
        N = len(seqs)
        res: list = [None] * N
        caps = {h: [None] * N for h in (cap_layers or [])}
        energy = np.full(N, np.nan) if energy_masks is not None else None
        lens = [len(s) for s in seqs]
        pending = list(range(N))
        while pending:
            batches = [[pending[k] for k in bb] for bb in self.batches([lens[i] for i in pending])]
            try:
                for idx in batches:
                    if res[idx[0]] is not None:
                        continue
                    if cap_layers:
                        self.cap_layers = set(cap_layers)
                        self.cap_pos = torch.as_tensor([cap_pos[i] for i in idx], device="cuda")
                        self.cap_out = {}
                    if energy_masks is not None:
                        T = max(lens[i] for i in idx)
                        m = torch.zeros((len(idx), T))
                        for b, i in enumerate(idx):
                            m[b, energy_masks[i]] = 1
                        self.energy_mask = m.cuda()
                        self.energy_acc = torch.zeros(len(idx), device="cuda")
                        self.energy_on = True
                    hn = self.forward([seqs[i] for i in idx])
                    self.energy_on = False
                    self.cap_pos = None
                    bsel, psel, meta = [], [], []
                    for b, i in enumerate(idx):
                        for k, p in enumerate(positions[i]):
                            bsel.append(b)
                            psel.append(p)
                            meta.append((i, k))
                    rows = hn[torch.as_tensor(bsel, device=hn.device), torch.as_tensor(psel, device=hn.device)]
                    del hn
                    outs = []
                    for s in range(0, rows.shape[0], chunk):
                        lp = self.logprobs(rows[s:s + chunk])
                        outs.append(reducer(lp, meta[s:s + chunk]))
                        del lp
                    o = torch.cat(outs, 0).cpu().numpy()
                    per: dict = {}
                    for r, (i, k) in enumerate(meta):
                        per.setdefault(i, []).append(o[r])
                    for i in idx:
                        res[i] = np.stack(per[i]) if i in per else np.zeros((0, o.shape[1]))
                    for h in (cap_layers or []):
                        c = self.cap_out[h].cpu().numpy()
                        for b, i in enumerate(idx):
                            caps[h][i] = c[b]
                    if energy is not None:
                        ea = self.energy_acc.cpu().numpy()
                        for b, i in enumerate(idx):
                            energy[i] = ea[b]
                pending = []
            except torch.cuda.OutOfMemoryError:
                self.energy_on = False
                self.cap_pos = None
                self.final_h = None
                torch.cuda.empty_cache()
                self.token_budget //= 2
                logger.warning(f"OOM -> token_budget {self.token_budget}")
                assert self.token_budget >= 64
                pending = [i for i in range(N) if res[i] is None]
        out = {"out": res}
        if cap_layers:
            out["cap"] = {h: np.stack(v) for h, v in caps.items()}
        if energy is not None:
            out["energy"] = energy
        return out

    # ------------------------------------------------------------------ residual capture (no log-probs)
    def capture_residuals(self, seqs: list[list[int]], pos: list[int], layers: list[int], content_mean: list[list[int]] | None = None
                          ) -> dict[int, np.ndarray]:
        """Residual at hidden indices `layers` at one position per sequence (or mean over content positions) -> {h: [N, D]}."""
        N = len(seqs)
        out = {h: np.zeros((N, self.D), dtype=np.float32) for h in layers}
        lens = [len(s) for s in seqs]
        for idx in self.batches(lens):
            if content_mean is None:
                self.cap_layers = set(layers)
                self.cap_pos = torch.as_tensor([pos[i] for i in idx], device="cuda")
                self.cap_out = {}
                self.forward([seqs[i] for i in idx])
                self.cap_pos = None
                for h in layers:
                    out[h][idx] = self.cap_out[h].cpu().numpy()
            else:
                # mean-pool: capture full hidden via per-layer hooks
                acc = {}
                T = max(lens[i] for i in idx)
                m = torch.zeros((len(idx), T))
                for b, i in enumerate(idx):
                    m[b, content_mean[i]] = 1
                m = m.cuda()

                def mk(h):
                    def hook(module, inp, o):
                        x = (o[0] if isinstance(o, tuple) else o).float()
                        acc[h] = ((x * m[..., None]).sum(1) / m.sum(1, keepdim=True).clamp_min(1)).cpu().numpy()
                        return None
                    return hook
                hs = [self.embed.register_forward_hook(mk(0))] if 0 in layers else []
                for j, layer in enumerate(self.layers):
                    if j + 1 in layers:
                        hs.append(layer.register_forward_hook(mk(j + 1)))
                self.forward([seqs[i] for i in idx])
                for hh in hs:
                    hh.remove()
                for h in layers:
                    out[h][idx] = acc[h]
        return out

    def capture_module_inputs(self, seqs: list[list[int]], sel: list[list[int]]) -> dict:
        """Inputs x to every abliterable module (o_proj, down_proj) at the selected positions of each sequence.
        Returns {(l, c): [n_sel_total, d_in] bf16 on GPU} in the order of (sequence, position)."""
        lens = [len(s) for s in seqs]
        parts: dict = {k: [] for k in self.modules}
        order = []
        for idx in self.batches(lens):
            b_idx, t_idx = [], []
            for b, i in enumerate(idx):
                for p in sel[i]:
                    b_idx.append(b)
                    t_idx.append(p)
                    order.append((i, p))
            if not b_idx:
                continue
            self.minput_sel = (torch.as_tensor(b_idx, device="cuda"), torch.as_tensor(t_idx, device="cuda"))
            self.minput_on = True
            self.minput_out = {}
            self.forward([seqs[i] for i in idx])
            self.minput_on = False
            for k in self.modules:
                parts[k].append(self.minput_out[k])
        # reorder to (sequence, position) order
        perm = sorted(range(len(order)), key=lambda r: order[r])
        pt = torch.as_tensor(perm, device="cuda")
        return {k: torch.cat(v, 0)[pt] for k, v in parts.items()}, [order[r] for r in perm]

    # ------------------------------------------------------------------ generation
    def generate(self, seqs: list[list[int]], max_new: int, batch: int = 32, mode: str = "leftpad") -> list[list[int]]:
        """Greedy decoding. mode='leftpad' (batched, left padding) | 'bucket' (equal-length buckets, no padding) | 'single'."""
        out: list = [None] * len(seqs)
        if mode == "leftpad":
            groups = []
            order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
            for k in range(0, len(order), batch):
                groups.append(order[k:k + batch])
        elif mode == "bucket":
            by: dict = {}
            for i, s in enumerate(seqs):
                by.setdefault(len(s), []).append(i)
            groups = [v[k:k + batch] for v in by.values() for k in range(0, len(v), batch)]
        else:
            groups = [[i] for i in range(len(seqs))]
        stop = {self.tok.eos_token_id, self.eot}
        gi = 0
        while gi < len(groups):
            idx = groups[gi]
            T = max(len(seqs[i]) for i in idx)
            ids = torch.full((len(idx), T), self.pad, dtype=torch.long)
            att = torch.zeros((len(idx), T), dtype=torch.long)
            for b, i in enumerate(idx):
                ids[b, T - len(seqs[i]):] = torch.tensor(seqs[i])
                att[b, T - len(seqs[i]):] = 1
            try:
                with torch.inference_mode():
                    g = self.model.generate(input_ids=ids.cuda(), attention_mask=att.cuda(), max_new_tokens=max_new,
                                            do_sample=False, pad_token_id=self.pad, top_p=None, top_k=None, temperature=None)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                half = max(1, len(idx) // 2)
                groups[gi:gi + 1] = [idx[:half], idx[half:]] if len(idx) > 1 else [idx]
                logger.warning(f"generate OOM -> split group to {half}")
                continue
            for b, i in enumerate(idx):
                new = g[b, T:].tolist()
                cut = next((j for j, t in enumerate(new) if t in stop), len(new))
                out[i] = new[:cut]
            gi += 1
        return out

    def decode(self, ids: list[int]) -> str:
        return self.tok.decode(ids, skip_special_tokens=True)

    def close(self) -> None:
        for h in self._handles:
            h.remove()
        gc.collect()
        torch.cuda.empty_cache()


# ---------------------------------------------------------------------------------------------------------------
# reducers (operate on a chunk of log-prob rows [n, V] with row meta [(i, k)])
def red_target(targets: dict) -> Callable:
    """lp of the target token for each row: targets[(i, k)] -> token id."""
    def f(lp, meta):
        t = torch.as_tensor([targets[m] for m in meta], device=lp.device)
        return lp.gather(1, t[:, None])
    return f


def red_target_r1(targets: dict, r_ids: list[int], c_ids: list[int]) -> Callable:
    """[lp(target), R1] per row; R1 = logsumexp(lp[R]) - logsumexp(lp[C]) (only meaningful at k = 0)."""
    rt = torch.as_tensor(r_ids, device="cuda")
    ct = torch.as_tensor(c_ids, device="cuda")

    def f(lp, meta):
        t = torch.as_tensor([targets[m] for m in meta], device=lp.device)
        a = lp.gather(1, t[:, None])
        r1 = (torch.logsumexp(lp[:, rt], 1) - torch.logsumexp(lp[:, ct], 1))[:, None]
        return torch.cat([a, r1], 1)
    return f


def red_topk(k: int = 256) -> Callable:
    def f(lp, meta):
        v, ix = lp.topk(k, -1)
        return torch.cat([ix.float(), v], -1)
    return f


def red_kl_nll(ref_idx: dict, ref_lp: dict, targets: dict) -> Callable:
    """[KL_trunc(orig || edit) over top-k + tail bucket, lp(target)] per row. ref_* keyed by (i, k) -> GPU tensors."""
    def f(lp, meta):
        ix = torch.stack([ref_idx[m] for m in meta])
        lo = torch.stack([ref_lp[m] for m in meta])
        le = lp.gather(1, ix)
        po = lo.exp()
        kl = (po * (lo - le)).sum(1)
        to = (1 - po.sum(1)).clamp_min(1e-12)
        te = (1 - le.exp().sum(1)).clamp_min(1e-12)
        kl = (kl + to * (to.log() - te.log())).clamp_min(0)
        t = torch.as_tensor([targets[m] for m in meta], device=lp.device)
        return torch.cat([kl[:, None], lp.gather(1, t[:, None])], 1)
    return f


def red_full_kl(ref_full: dict) -> Callable:
    """Full-vocab KL(orig || edit) per row (U5)."""
    def f(lp, meta):
        lo = torch.stack([ref_full[m] for m in meta])
        return (lo.exp() * (lo - lp)).sum(1, keepdim=True)
    return f

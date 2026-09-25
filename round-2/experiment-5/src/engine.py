"""GPU engine: NF4 base + iteration-1 Heretic LoRA adapter as ONE PeftModel (adapter off = ORIGINAL, on = EDITED),
residual capture hooks, batched generation and teacher-forced scoring (token log-probs, paired full-vocab KL, R1).
Adapted from iteration-1 gen_art_experiment_3/interventions.py (hooks, chunked log-softmax, OOM halving)."""
from __future__ import annotations

import gc
import os
import time
from dataclasses import dataclass, field

import numpy as np
import torch
from loguru import logger
from transformers import AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig, PretrainedConfig

from common import MODELS, SYSTEM_PROMPT

TOKEN_BUDGET = int(os.environ.get("C1U_TOKEN_BUDGET", 8192))  # tokens per teacher-forced batch (halved on OOM)


@dataclass
class HookState:
    capture: bool = False
    cap_idx: torch.Tensor | None = None  # [B, P] positions to gather
    cap_mask: torch.Tensor | None = None  # [B, T] content mask for content-mean
    cap_out: dict = field(default_factory=dict)
    capture_layers: set | None = None
    final_norm_out: torch.Tensor | None = None


class LM:
    def __init__(self, key: str, adapter: bool = True):
        from peft import PeftModel

        self.key = key
        spec = MODELS[key]
        repo, sha = spec["repo"], spec["sha"]
        t = time.time()
        cfgs = PretrainedConfig.get_config_dict(repo, revision=sha)
        cls = AutoModelForImageTextToText if any("vision_config" in c for c in cfgs) else AutoModelForCausalLM
        self.model_class = cls.__name__
        self.tok = AutoTokenizer.from_pretrained(repo, revision=sha)
        # Heretic 3521f864 model.py _get_quantization_config('bnb_4bit') kwargs (as pinned in E3 configs/pins.json)
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                                 bnb_4bit_use_double_quant=True)
        base = cls.from_pretrained(repo, revision=sha, dtype=torch.bfloat16, quantization_config=bnb, device_map="cuda:0")
        base.eval()
        for p in base.parameters():
            p.requires_grad_(False)
        self.base = base
        if adapter:
            self.pm = PeftModel.from_pretrained(base, str(spec["adapter"]))
            self.pm.eval()
            self.model = self.pm
        else:
            self.pm, self.model = None, base
        self.ckpt = "edit" if adapter else "orig"
        cfg = base.config
        self.tcfg = getattr(cfg, "text_config", None) or cfg
        self.L = self.tcfg.num_hidden_layers
        self.D = self.tcfg.hidden_size
        self.softcap = getattr(self.tcfg, "final_logit_softcapping", None)
        self.layers = None
        for name, mod in self.model.named_modules():
            if isinstance(mod, torch.nn.ModuleList) and len(mod) == self.L:
                self.layers, self.layers_name = mod, name
                owner = name.rsplit(".", 1)[0]
                self.backbone = self.model.get_submodule(owner)
                break
        assert self.layers is not None, "decoder layers not found"
        self.embed = self.model.get_input_embeddings()
        self.norm = self.backbone.norm
        self.lm_head = self.model.get_output_embeddings()
        self.state = HookState()
        self._handles = [self.embed.register_forward_hook(self._make_hook(0))]
        for j, layer in enumerate(self.layers):
            self._handles.append(layer.register_forward_hook(self._make_hook(j + 1)))
        self._handles.append(self.norm.register_forward_hook(self._norm_hook))
        self.bos = self.tok.bos_token_id
        self.pad = self.tok.pad_token_id if self.tok.pad_token_id is not None else self.tok.eos_token_id
        self.eos_ids = {self.tok.eos_token_id, self.tok.convert_tokens_to_ids("<end_of_turn>")}
        self.token_budget = TOKEN_BUDGET
        logger.info(f"[{key}] loaded {cls.__name__} + adapter={adapter} L={self.L} D={self.D} softcap={self.softcap} "
                    f"layers='{self.layers_name}' in {time.time()-t:.0f}s; VRAM {torch.cuda.memory_allocated()/1e9:.1f} GB")

    # ------------------------------------------------------------------ checkpoint switch
    def set_ckpt(self, ckpt: str) -> None:
        assert ckpt in ("orig", "edit")
        if self.pm is None:
            assert ckpt == "orig"
            return
        if ckpt == "orig":
            self.pm.base_model.disable_adapter_layers()
        else:
            self.pm.base_model.enable_adapter_layers()
        self.ckpt = ckpt

    def lora_modules(self) -> list[tuple[str, torch.Tensor, torch.Tensor, float]]:
        """(name, A [r,in], B [out,r], scale) for every LoRA-wrapped module."""
        out = []
        for name, mod in self.model.named_modules():
            if hasattr(mod, "lora_A") and "default" in getattr(mod, "lora_A", {}):
                A = mod.lora_A["default"].weight.detach().float().cpu()
                B = mod.lora_B["default"].weight.detach().float().cpu()
                out.append((name, A, B, float(mod.scaling["default"])))
        return out

    # ------------------------------------------------------------------ hooks
    def _make_hook(self, h: int):
        def hook(module, inp, out):
            st = self.state
            if st.capture and (st.capture_layers is None or h in st.capture_layers):
                x = out[0] if isinstance(out, tuple) else out
                xf = x.float()
                B = xf.shape[0]
                g = xf[torch.arange(B, device=xf.device)[:, None], st.cap_idx]  # [B,P,D]
                m = st.cap_mask.to(xf.dtype)
                cm = (xf * m[..., None]).sum(1) / m.sum(1, keepdim=True).clamp_min(1)
                st.cap_out[h] = torch.cat([g, cm[:, None]], 1).cpu()
            return None
        return hook

    def _norm_hook(self, module, inp, out):
        self.state.final_norm_out = out

    # ------------------------------------------------------------------ text
    def render(self, prompt: str) -> str:
        return self.tok.apply_chat_template([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                                            add_generation_prompt=True, tokenize=False)

    def encode_chat(self, prompt: str) -> tuple[list[int], list[int]]:
        """Token ids of the rendered chat prompt and the indices of the user-content tokens (system prompt excluded)."""
        text = self.render(prompt)
        enc = self.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        start = text.rfind(prompt)
        end = start + len(prompt)
        content = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if a >= start and b <= end and b > a]
        return enc["input_ids"], content

    def encode_plain(self, text: str) -> list[int]:
        return [self.bos] + self.tok(text, add_special_tokens=False)["input_ids"]

    # ------------------------------------------------------------------ batching
    def _batches(self, lens: list[int], budget: int | None = None):
        budget = budget or self.token_budget
        order = sorted(range(len(lens)), key=lambda i: -lens[i])
        i = 0
        while i < len(order):
            mx = lens[order[i]]
            bs = max(1, budget // max(mx, 1))
            yield order[i:i + bs]
            i += bs

    def _forward(self, seqs: list[list[int]]):
        B = len(seqs)
        T = max(len(s) for s in seqs)
        ids = torch.full((B, T), self.pad, dtype=torch.long)
        att = torch.zeros((B, T), dtype=torch.long)
        for b, s in enumerate(seqs):  # RIGHT padding for teacher forcing
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
        """For each sequence gather its positions, compute log-probs there (chunks of 64 positions) and reduce."""
        N = len(seqs)
        res = [None] * N
        lens = [len(s) for s in seqs]
        batches = list(self._batches(lens))
        bi = 0
        while bi < len(batches):
            idx = batches[bi]
            try:
                hn = self._forward([seqs[i] for i in idx])
                for b, i in enumerate(idx):
                    pos = torch.as_tensor(positions[i], device=hn.device)
                    outs = []
                    for s in range(0, len(pos), 64):
                        lp = self._logprobs(hn[b, pos[s:s + 64]])
                        outs.append(reducer(lp, i, s))
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

    # ------------------------------------------------------------------ outcomes
    def token_logprobs(self, seqs: list[list[int]], starts: list[int]) -> list[np.ndarray]:
        """Per-token log p(seq[t] | seq[:t]) for t in [start, len) -> list of arrays."""
        tg = {}

        def red(lp, i, s):
            if i not in tg:
                tg[i] = torch.as_tensor(seqs[i][starts[i]:], device="cuda")
            t = tg[i][s:s + lp.shape[0]]
            return lp.gather(1, t[:, None])[:, 0]
        out = self._run(seqs, [list(range(st - 1, len(sq) - 1)) for sq, st in zip(seqs, starts)], red)
        return [o.astype(np.float64) for o in out]

    def first_token_lp(self, seqs: list[list[int]], tok_ids: list[int]) -> np.ndarray:
        ids_t = torch.as_tensor(tok_ids, device="cuda")
        out = self._run(seqs, [[len(s) - 1] for s in seqs], lambda lp, i, s: lp[:, ids_t])
        return np.stack([o[0] for o in out])

    def paired_kl(self, prompts: list[list[int]], conts: list[list[int]], n: int, rc_sets: list[tuple[list[int], list[int]]]):
        """Teacher-force prompt+cont[:n-1] in ORIGINAL then EDITED; per item: full-vocab KL(p_orig||p_edit) at each of the
        first n response positions, and R1 (first-token logsumexp(R) - logsumexp(C)) in both checkpoints.
        Returns list of dicts with kl (array [<=n]) and r1_orig, r1_edit."""
        assert self.pm is not None
        N = len(prompts)
        seqs = [p + c[: n - 1] for p, c in zip(prompts, conts)]
        npos = [min(n, len(c) + 1) if len(c) < n else n for c in conts]
        res: list = [None] * N
        budget = self.token_budget // 2
        batches = list(self._batches([len(s) for s in seqs], budget))
        bi = 0
        while bi < len(batches):
            idx = batches[bi]
            try:
                lps = {}
                for ck in ("orig", "edit"):
                    self.set_ckpt(ck)
                    hn = self._forward([seqs[i] for i in idx])
                    lps[ck] = [self._logprobs(hn[b, len(prompts[i]) - 1: len(prompts[i]) - 1 + npos[i]]) for b, i in enumerate(idx)]
                    del hn
                    self.state.final_norm_out = None
                for b, i in enumerate(idx):
                    lo, le = lps["orig"][b], lps["edit"][b]
                    kl = (lo.exp() * (lo - le)).sum(-1).clamp_min(0)
                    R, Cc = rc_sets[i]
                    r1 = {ck: float(torch.logsumexp(lps[ck][b][0, R], 0) - torch.logsumexp(lps[ck][b][0, Cc], 0)) for ck in lps}
                    res[i] = {"kl": kl.cpu().numpy().astype(np.float64), "r1_orig": r1["orig"], "r1_edit": r1["edit"]}
                del lps
                bi += 1
            except torch.cuda.OutOfMemoryError:
                self.state.final_norm_out = None
                torch.cuda.empty_cache()
                budget //= 2
                logger.warning(f"paired_kl OOM -> budget {budget}")
                assert budget >= 64
                rest = [i for i in range(N) if res[i] is None]
                batches = [[rest[k] for k in bb] for bb in self._batches([len(seqs[i]) for i in rest], budget)]
                bi = 0
        self.set_ckpt("edit")
        return res

    def capture(self, seqs: list[list[int]], cap_pos: list[list[int]], content: list[list[int]], layers=None,
                pos_keep: list[int] | None = None) -> np.ndarray:
        """Residuals (float32) at the given positions (+ content mean) for each hidden index -> [N, H, P, D]."""
        N = len(seqs)
        hs = list(range(self.L + 1)) if layers is None else list(layers)
        P = len(cap_pos[0]) + 1
        keep = list(range(P)) if pos_keep is None else pos_keep
        out = np.zeros((N, len(hs), len(keep), self.D), dtype=np.float32)  # fp16 overflows (|x| up to ~8e4)
        for idx in self._batches([len(s) for s in seqs], self.token_budget // 2):
            B = len(idx)
            T = max(len(seqs[i]) for i in idx)
            mask = torch.zeros((B, T))
            for b, i in enumerate(idx):
                mask[b, content[i]] = 1
            self.state.capture, self.state.cap_out = True, {}
            self.state.capture_layers = set(hs)
            self.state.cap_idx = torch.as_tensor([cap_pos[i] for i in idx], device="cuda")
            self.state.cap_mask = mask.cuda()
            self._forward([seqs[i] for i in idx])
            for k, h in enumerate(hs):
                out[idx, k] = self.state.cap_out[h][:, keep].numpy()
            self.state.capture, self.state.cap_out = False, {}
            self.state.final_norm_out = None
        return out

    # ------------------------------------------------------------------ generation
    def generate(self, seqs: list[list[int]], max_new: int, batch: int = 32) -> list[list[int]]:
        out: list = [None] * len(seqs)
        order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
        bs = batch
        k = 0
        while k < len(order):
            idx = order[k:k + bs]
            T = max(len(seqs[i]) for i in idx)
            ids = torch.full((len(idx), T), self.pad, dtype=torch.long)
            att = torch.zeros((len(idx), T), dtype=torch.long)
            for b, i in enumerate(idx):  # LEFT padding for generation
                ids[b, T - len(seqs[i]):] = torch.tensor(seqs[i])
                att[b, T - len(seqs[i]):] = 1
            try:
                with torch.inference_mode():
                    g = self.model.generate(input_ids=ids.cuda(), attention_mask=att.cuda(), max_new_tokens=max_new,
                                            do_sample=False, pad_token_id=self.pad, top_p=None, top_k=None, temperature=None)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                bs = max(1, bs // 2)
                logger.warning(f"generate OOM -> batch {bs}")
                continue
            for b, i in enumerate(idx):
                new = g[b, T:].tolist()
                cut = next((j for j, t in enumerate(new) if t in self.eos_ids), len(new))
                out[i] = new[:cut]
            k += len(idx)
            self.state.final_norm_out = None
        return out

    def close(self) -> None:
        for h in self._handles:
            h.remove()
        del self.model, self.base, self.pm
        gc.collect()
        torch.cuda.empty_cache()

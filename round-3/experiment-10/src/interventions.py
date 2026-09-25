"""GPU engine (adapted from iteration-1 A1 gen_art_experiment_3/interventions.py): 4-bit model loading (Heretic's
BitsAndBytesConfig), residual hooks for directional ablation / partial ablation / activation addition / residual capture,
weight-output hooks on o_proj/down_proj (exact equivalent of orthogonalising the effective write weights), batched
teacher-forced outcomes (first-token R1, sequence R_seq, KL, NLL, MC) and batched greedy generation."""
from __future__ import annotations

import gc
import math
import time
from dataclasses import dataclass, field

import numpy as np
import torch
from loguru import logger
from transformers import (AutoModelForCausalLM, AutoModelForImageTextToText, AutoTokenizer, BitsAndBytesConfig,
                          PretrainedConfig)

from common import MODELS, SYSTEM_PROMPT

BNB = dict(load_in_4bit=True, bnb_4bit_compute_dtype="bfloat16", bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)
TOKEN_BUDGET = int(__import__("os").environ.get("TF_TOKEN_BUDGET", 8192))  # tokens per teacher-forced batch (halved on OOM)
TOPK_REF = 512  # top-k of the original distribution kept for the coarsened KL


@dataclass
class HookState:
    mode: str | None = None  # None | "ablate" | "add"
    Q: torch.Tensor | None = None  # [k, D] float32 orthonormal rows (ablation)
    c: float = 1.0  # partial-ablation strength
    cvec: torch.Tensor | None = None  # optional per-basis-row strengths (Gram-Schmidt order), overrides c
    Qh: dict | None = None  # optional per-hidden-index bases {h: [k, D]} (layer-matched ablation), overrides Q
    add_h: int = -1  # hidden index for addition
    add_vec: torch.Tensor | None = None  # [D] float32
    add_skip_first: bool = True  # do not add at position 0 (BOS) in right-padded prefill
    capture: bool = False
    cap_idx: torch.Tensor | None = None  # [B, P] positions to gather per hidden index
    cap_mask: torch.Tensor | None = None  # [B, T] float mask for content-mean
    cap_out: dict = field(default_factory=dict)
    capture_layers: set | None = None
    final_norm_out: torch.Tensor | None = None
    max_proj_ratio: float = 0.0  # diagnostic: max |x.q|/||x|| after ablation
    track_proj: bool = False


class LM:
    def __init__(self, key: str, hf_model=None, tok=None):
        """Load the pinned model in 4-bit, or wrap an already-loaded model (e.g. Heretic's PeftModel) when given."""
        self.key = key
        repo, sha = MODELS[key]["repo"], MODELS[key]["sha"]
        self.wstate = {"hooks": [], "rhat": None, "c": 0.0}
        t = time.time()
        cfgs = PretrainedConfig.get_config_dict(repo, revision=sha)
        cls = AutoModelForImageTextToText if any("vision_config" in c for c in cfgs) else AutoModelForCausalLM
        self.model_class = cls.__name__
        self.tok = tok if tok is not None else AutoTokenizer.from_pretrained(repo, revision=sha)
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_quant_type="nf4",
                                 bnb_4bit_use_double_quant=True)
        self.model = hf_model if hf_model is not None else cls.from_pretrained(
            repo, revision=sha, dtype=torch.bfloat16, quantization_config=bnb, device_map="cuda:0", attn_implementation="eager")
        self.model.eval()
        if hf_model is None:
            for p in self.model.parameters():
                p.requires_grad_(False)
        cfg = self.model.config
        self.tcfg = getattr(cfg, "text_config", None) or cfg
        self.L = self.tcfg.num_hidden_layers
        self.D = self.tcfg.hidden_size
        self.softcap = getattr(self.tcfg, "final_logit_softcapping", None)
        # generic discovery: decoder layers = first ModuleList of length L; its owner holds .norm
        self.layers, self.backbone = None, None
        for name, mod in self.model.named_modules():
            if isinstance(mod, torch.nn.ModuleList) and len(mod) == self.L:
                self.layers = mod
                owner = name.rsplit(".", 1)[0] if "." in name else ""
                self.backbone = self.model.get_submodule(owner) if owner else self.model
                self.layers_name = name
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
        self.token_budget = TOKEN_BUDGET
        logger.info(f"[{key}] loaded {cls.__name__} L={self.L} D={self.D} softcap={self.softcap} layers='{self.layers_name}' "
                    f"in {time.time()-t:.0f}s; VRAM {torch.cuda.memory_allocated()/1e9:.1f} GB")

    # ------------------------------------------------------------------ hooks
    def _make_hook(self, h: int):
        def hook(module, inp, out):
            st = self.state
            x = out[0] if isinstance(out, tuple) else out
            changed = False
            Q = st.Qh.get(h) if st.Qh is not None else st.Q
            if st.mode == "ablate" and Q is not None:
                xf = x.float()
                proj = xf @ Q.T  # [B,T,k]
                xf = xf - ((proj * st.cvec) @ Q if st.cvec is not None else st.c * (proj @ Q))
                x = xf.to(x.dtype)
                if st.track_proj:  # measured on the bf16 tensor that is actually passed on
                    xc = x.float()
                    r = ((xc @ Q.T).abs().amax(-1) / xc.norm(dim=-1).clamp_min(1e-6)).max().item()
                    st.max_proj_ratio = max(st.max_proj_ratio, r)
                changed = True
            elif st.mode == "add" and h == st.add_h:
                xf = x.float()
                if st.add_skip_first and xf.shape[1] > 1:
                    xf[:, 1:] += st.add_vec
                else:
                    xf += st.add_vec
                x = xf.to(x.dtype)
                changed = True
            if st.capture and (st.capture_layers is None or h in st.capture_layers):
                xf = x.float()
                B = xf.shape[0]
                g = xf[torch.arange(B, device=xf.device)[:, None], st.cap_idx]  # [B,P,D]
                m = st.cap_mask.to(xf.dtype)
                cm = (xf * m[..., None]).sum(1) / m.sum(1, keepdim=True).clamp_min(1)  # [B,D]
                st.cap_out[h] = torch.cat([g, cm[:, None]], 1).cpu()
            if changed:
                if isinstance(out, tuple):
                    return (x,) + tuple(out[1:])
                return x
            return None

        return hook

    def _norm_hook(self, module, inp, out):
        self.state.final_norm_out = out

    def reset(self) -> None:
        self.state = HookState()

    def set_ablate(self, dirs: np.ndarray | torch.Tensor | None, c: float = 1.0) -> None:
        self.reset()
        if dirs is None:
            return
        d = torch.as_tensor(np.asarray(dirs, dtype=np.float32)).reshape(-1, self.D).cuda()
        Q, _ = torch.linalg.qr(d.T)  # orthonormal basis of span
        self.state.mode, self.state.Q, self.state.c = "ablate", Q.T.contiguous(), float(c)

    def set_ablate_scaled(self, dirs: np.ndarray, cvec) -> None:
        """Gram-Schmidt in the given order (first direction exact), then ablate row k with strength cvec[k]."""
        self.reset()
        d = np.asarray(dirs, dtype=np.float64).reshape(-1, self.D)
        Q = []
        for v in d:
            for q in Q:
                v = v - (v @ q) * q
            Q.append(v / (np.linalg.norm(v) + 1e-12))
        self.state.mode, self.state.Q = "ablate", torch.as_tensor(np.stack(Q), dtype=torch.float32).cuda().contiguous()
        self.state.cvec = torch.as_tensor(np.asarray(cvec, dtype=np.float32)).cuda()

    def set_ablate_layerwise(self, dirs_by_h: dict, c: float = 1.0) -> None:
        """Layer-matched ablation: at hidden index h remove the span of dirs_by_h[h] ([k, D]); indices absent are untouched."""
        self.reset()
        Qh = {}
        for h, d in dirs_by_h.items():
            t = torch.as_tensor(np.asarray(d, dtype=np.float32)).reshape(-1, self.D).cuda()
            Q, _ = torch.linalg.qr(t.T)
            Qh[int(h)] = Q.T.contiguous()
        self.state.mode, self.state.Qh, self.state.c = "ablate", Qh, float(c)

    def set_add(self, h: int, vec: np.ndarray, alpha: float) -> None:
        self.reset()
        self.state.mode, self.state.add_h = "add", int(h)
        self.state.add_vec = torch.as_tensor(np.asarray(vec, dtype=np.float32) * alpha).cuda()

    # ------------------------------------------------------------------ text
    def render(self, prompt: str) -> str:
        return self.tok.apply_chat_template([{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                                            add_generation_prompt=True, tokenize=False)

    def encode_chat(self, prompt: str) -> tuple[list[int], list[int]]:
        """Token ids of the rendered chat prompt and the indices of user-content tokens."""
        text = self.render(prompt)
        enc = self.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        start = text.rfind(prompt)
        end = start + len(prompt)
        content = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if a >= start and b <= end and b > a]
        return enc["input_ids"], content

    def encode_plain(self, text: str) -> list[int]:
        return [self.bos] + self.tok(text, add_special_tokens=False)["input_ids"]

    # ------------------------------------------------------------------ batching
    def _batches(self, lens: list[int]):
        order = sorted(range(len(lens)), key=lambda i: -lens[i])
        i = 0
        while i < len(order):
            mx = lens[order[i]]
            bs = max(1, self.token_budget // max(mx, 1))
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
        ids, att = ids.cuda(), att.cuda()
        with torch.inference_mode():
            self.model(input_ids=ids, attention_mask=att, use_cache=False, logits_to_keep=1)
        return self.state.final_norm_out

    def _logprobs(self, h: torch.Tensor) -> torch.Tensor:
        logits = self.lm_head(h.to(self.lm_head.weight.dtype)).float()
        if self.softcap:
            logits = torch.tanh(logits / self.softcap) * self.softcap
        return torch.log_softmax(logits, -1)

    def _run(self, seqs, positions, reducer, out_dim: int) -> np.ndarray:
        """For every sequence gather its positions, compute log-probs there and reduce -> [N, n_pos, out_dim]."""
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
    def first_token_lp(self, seqs: list[list[int]], tok_ids: list[int]) -> np.ndarray:
        """log-probs of tok_ids at the first response position (last prompt token) -> [N, len(tok_ids)]."""
        ids_t = torch.as_tensor(tok_ids, device="cuda")
        out = self._run(seqs, [[len(s) - 1] for s in seqs], lambda lp, i, s: lp[:, ids_t], len(tok_ids))
        return np.stack([o[0] for o in out])

    def ref_topk(self, seqs: list[list[int]], starts: list[int], n: int, k: int = TOPK_REF):
        """Original distribution at positions start-1 .. start+n-2 (predicting continuation tokens): top-k idx/lp."""
        def red(lp, i, s):
            v, ix = lp.topk(k, -1)
            return torch.cat([ix.float(), v], -1)
        out = self._run(seqs, [list(range(st - 1, st - 1 + n)) for st in starts], red, 2 * k)
        return [(o[:, :k].astype(np.int64), o[:, k:].astype(np.float32)) for o in out]

    def kl_vs_ref(self, seqs, starts, n, ref) -> np.ndarray:
        """Coarsened KL(original || edited) per position over (top-k of original + tail bucket); mean per sequence."""
        refs_t = {}

        def red(lp, i, s):
            if i not in refs_t:
                refs_t[i] = (torch.as_tensor(ref[i][0], device="cuda"), torch.as_tensor(ref[i][1], device="cuda"))
            ix, lo = refs_t[i]
            ix, lo = ix[s:s + lp.shape[0]], lo[s:s + lp.shape[0]]
            le = lp.gather(1, ix)
            po = lo.exp()
            kl = (po * (lo - le)).sum(1)
            to = (1 - po.sum(1)).clamp_min(1e-12)
            te = (1 - le.exp().sum(1)).clamp_min(1e-12)
            kl = kl + to * (to.log() - te.log())
            return kl.clamp_min(0)[:, None]
        out = self._run(seqs, [list(range(st - 1, st - 1 + n)) for st in starts], red, 1)
        return np.array([float(o.mean()) for o in out])

    def seq_nll(self, seqs, starts) -> np.ndarray:
        """Mean per-token NLL of tokens seq[start:] -> [N]."""
        tg = {}

        def red(lp, i, s):
            if i not in tg:
                tg[i] = torch.as_tensor(seqs[i][starts[i]:], device="cuda")
            t = tg[i][s:s + lp.shape[0]]
            return -lp.gather(1, t[:, None])
        out = self._run(seqs, [list(range(st - 1, len(sq) - 1)) for sq, st in zip(seqs, starts)], red, 1)
        return np.array([float(o.mean()) for o in out])

    def capture(self, seqs: list[list[int]], cap_pos: list[list[int]], content: list[list[int]], layers=None) -> np.ndarray:
        """Residuals at the given positions (+ content mean) for every hidden index -> [N, H, P+1, D] float32 on CPU."""
        N = len(seqs)
        H = self.L + 1
        P = len(cap_pos[0]) + 1
        hs = list(range(H)) if layers is None else list(layers)
        out = np.zeros((N, len(hs), P, self.D), dtype=np.float32)  # fp16 overflows (|x|>65504 in Gemma residuals)
        for idx in self._batches([len(s) for s in seqs]):
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
                out[idx, k] = self.state.cap_out[h].numpy()
            self.state.capture, self.state.cap_out = False, {}
        return out

    # ------------------------------------------------------------------ generation
    def generate(self, seqs: list[list[int]], max_new: int, batch: int = 32, left_pad: bool = True) -> list[list[int]]:
        out: list = [None] * len(seqs)
        order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i]))
        bs = batch if left_pad else 1
        k = 0
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
                                            do_sample=False, pad_token_id=self.pad, top_p=None, top_k=None, temperature=None)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                bs = max(1, bs // 2)
                logger.warning(f"generate OOM -> batch {bs}")
                continue
            for b, i in enumerate(idx):
                new = g[b, T:].tolist()
                eos = {self.tok.eos_token_id, self.tok.convert_tokens_to_ids("<end_of_turn>")}
                cut = next((j for j, t in enumerate(new) if t in eos), len(new))
                out[i] = new[:cut]
            k += len(idx)
        return out

    # ------------------------------------------------------------------ weight-output hooks
    def write_modules(self, layer_ids) -> list:
        mods = []
        for j in layer_ids:
            layer = self.layers[j]
            mods += [layer.self_attn.o_proj, layer.mlp.down_proj]
        return mods

    def set_weight_edit(self, r: np.ndarray | None, layer_ids=(), c: float = 1.0) -> None:
        """out <- out - c (out . rhat) rhat on o_proj and down_proj outputs of the given decoder layers. For a linear map
        this equals replacing W by (I - c rhat rhat^T) W (Arditi/Heretic weight orthogonalisation), applied to base+LoRA."""
        for h in self.wstate["hooks"]:
            h.remove()
        self.wstate = {"hooks": [], "rhat": None, "c": 0.0, "layers": []}
        if r is None:
            return
        rh = torch.as_tensor(unit(r), dtype=torch.float32).cuda()
        cc = float(c)

        def hook(module, inp, out):
            of = out.float()
            of = of - cc * (of @ rh)[..., None] * rh
            return of.to(out.dtype)
        self.wstate = {"hooks": [m.register_forward_hook(hook) for m in self.write_modules(layer_ids)], "rhat": rh, "c": cc,
                       "layers": list(layer_ids)}

    # ------------------------------------------------------------------ capture of all prompt positions at one layer
    def capture_all(self, seqs: list[list[int]], h: int) -> list[np.ndarray]:
        """Residual (hidden index h) at every non-pad position of each sequence -> list of [T_i, D] float32."""
        out: list = [None] * len(seqs)
        store = {}

        def grab(module, inp, o):
            store["x"] = (o[0] if isinstance(o, tuple) else o).float().cpu()
        mod = self.embed if h == 0 else self.layers[h - 1]
        hd = mod.register_forward_hook(grab)
        try:
            for idx in self._batches([len(s) for s in seqs]):
                self._forward([seqs[i] for i in idx])
                for b, i in enumerate(idx):
                    out[i] = store["x"][b, :len(seqs[i])].numpy()
                self.state.final_norm_out = None
        finally:
            hd.remove()
        return out

    # ------------------------------------------------------------------ sequence-level refusal log-odds
    def cont_logprob(self, prompts: list[list[int]], conts: list[list[int]]) -> np.ndarray:
        """Mean per-token log-prob of each continuation given its prompt (teacher forced) -> [N]."""
        seqs = [p + c for p, c in zip(prompts, conts)]
        starts = [len(p) for p in prompts]
        return -self.seq_nll(seqs, starts)

    def close(self) -> None:
        self.set_weight_edit(None)
        for h in self._handles:
            h.remove()
        del self.model
        gc.collect()
        torch.cuda.empty_cache()


WINS_Q = 0.995  # Heretic's winsorization_quantile mechanism (off by default there); tames massive activations


def winsorize(x: np.ndarray, q: float = WINS_Q) -> np.ndarray:
    """Symmetric per-vector winsorization over the last axis (Heretic model.get_residuals semantics)."""
    x = np.asarray(x, dtype=np.float32)
    t = np.quantile(np.abs(x), q, axis=-1, keepdims=True)
    return np.clip(x, -t, t)


def unit(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    return (v / (np.linalg.norm(v) + 1e-12)).astype(np.float32)


def cos(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a, np.float64), np.asarray(b, np.float64)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def logsumexp_np(x: np.ndarray, axis: int = -1) -> np.ndarray:
    m = x.max(axis, keepdims=True)
    return (m + np.log(np.exp(x - m).sum(axis, keepdims=True))).squeeze(axis)


def refusal_scores(lp: np.ndarray, r_cols: list[int], c_cols: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """R = logsumexp(lp[R]) - logsumexp(lp[C]);  R_arditi = log sum p(R) - log(1 - sum p(R))."""
    lr = logsumexp_np(lp[:, r_cols])
    lc = logsumexp_np(lp[:, c_cols])
    pr = np.clip(np.exp(lr), 1e-12, 1 - 1e-7)
    return lr - lc, np.log(pr) - np.log1p(-pr)

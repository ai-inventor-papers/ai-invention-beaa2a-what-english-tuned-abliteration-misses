"""LaBSE embedding helper with a persistent on-disk cache (work/labse_cache/*.npz, keyed by sha1(text)[:16])."""
from __future__ import annotations

import numpy as np
from loguru import logger

from common import WORK, text_key

CACHE_DIR = WORK / "labse_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LABSE_ID = "sentence-transformers/LaBSE"
LABSE_REV = "836121a0533e5664b21c7aacc5d22951f2b8b25b"

_model = None
_cache: dict[str, np.ndarray] | None = None


def _load_cache() -> dict[str, np.ndarray]:
    global _cache
    if _cache is None:
        _cache = {}
        for f in sorted(CACHE_DIR.glob("*.npz")):
            z = np.load(f)
            for k, v in zip(z["keys"], z["vecs"]):
                _cache[str(k)] = v
        logger.info(f"LaBSE cache: {len(_cache)} vectors")
    return _cache


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        import os
        dev = os.environ.get("EMB_DEVICE", "cuda")
        _model = SentenceTransformer(LABSE_ID, revision=LABSE_REV, device=dev)
        if dev == "cuda":
            _model.half()
    return _model


def embed(texts: list[str], batch_size: int = 256) -> np.ndarray:
    """Return L2-normalised LaBSE embeddings (float32) for texts, computing only uncached ones."""
    cache = _load_cache()
    keys = [text_key(t) for t in texts]
    missing = sorted({k: t for k, t in zip(keys, texts) if k not in cache}.items())
    if missing:
        m = _get_model()
        mk = [k for k, _ in missing]
        mt = [t for _, t in missing]
        vecs = m.encode(mt, batch_size=batch_size, normalize_embeddings=True, convert_to_numpy=True,
                        show_progress_bar=False).astype(np.float32)
        for k, v in zip(mk, vecs):
            cache[k] = v
        idx = len(list(CACHE_DIR.glob("*.npz")))
        np.savez(CACHE_DIR / f"shard_{idx:04d}.npz", keys=np.array(mk), vecs=vecs.astype(np.float16))
        logger.info(f"LaBSE: embedded {len(mt)} new texts (shard {idx})")
    return np.stack([cache[k].astype(np.float32) for k in keys]) if keys else np.zeros((0, 768), np.float32)


def max_cos(a: np.ndarray, b: np.ndarray, block: int = 4096) -> tuple[np.ndarray, np.ndarray]:
    """For each row in a, max cosine to rows of b and its argmax (GPU, blockwise)."""
    import torch
    if len(a) == 0 or len(b) == 0:
        return np.zeros(len(a)), np.zeros(len(a), dtype=int)
    tb = torch.tensor(b, device="cuda", dtype=torch.float16)
    mx, am = [], []
    for i in range(0, len(a), block):
        ta = torch.tensor(a[i:i + block], device="cuda", dtype=torch.float16)
        s = ta @ tb.T
        v, j = s.max(dim=1)
        mx.append(v.float().cpu().numpy())
        am.append(j.cpu().numpy())
    return np.concatenate(mx), np.concatenate(am)

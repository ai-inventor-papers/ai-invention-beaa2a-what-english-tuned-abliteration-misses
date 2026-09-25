#!/usr/bin/env python3
"""Stage 0.3: resolve/verify pins. Shard sha256 of GaMS/Gemma vs iteration-1 pins (mismatch = abort),
revisions + LFS sha of the community model, guards and GlotLID. -> results/pins_verified.json"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download
from loguru import logger

from common import EXP1, WS, setup_logging, sha256_file

REPOS = {"gams": ("cjvt/GaMS3-12B-Instruct", "1d0b27af5748784482600d24779409e7e1dc9adc"),
         "gemma": ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80"),
         "community": ("p-e-w/gemma-3-12b-it-heretic", None), "polyguard": ("ToxicityPrompts/PolyGuard-Qwen", None),
         "llamaguard": ("meta-llama/Llama-Guard-3-8B", None), "glotlid": ("cis-lmu/glotlid", None)}


@logger.catch(reraise=True)
def main() -> None:
    setup_logging("verify_pins")
    api = HfApi()
    pins1 = json.loads((EXP1 / "pins.json").read_text())["models"]
    out = {}
    for k, (repo, rev) in REPOS.items():
        info = api.model_info(repo, revision=rev, files_metadata=True)
        lfs = {s.rfilename: (s.lfs.sha256 if s.lfs else None) for s in info.siblings}
        rec = {"repo": repo, "sha": info.sha, "gated": str(info.gated), "lfs_sha256": lfs}
        if rev:
            assert info.sha == rev, f"{repo} resolved {info.sha} != pinned {rev}"
            snap = Path(snapshot_download(repo, revision=rev, local_files_only=True))
            shards = sorted(p.name for p in snap.glob("*.safetensors")) + ["tokenizer.json", "tokenizer.model"]
            with ThreadPoolExecutor(6) as ex:
                hs = dict(zip(shards, ex.map(lambda n: sha256_file(snap / n), shards)))
            exp = pins1[k]["files"]
            rec["local_sha256"] = hs
            rec["match_iter1_pins"] = {n: hs[n] == exp.get(n) for n in shards}
            logger.info(f"{repo}: all shards match iter-1 pins = {all(rec['match_iter1_pins'].values())}")
            assert all(rec["match_iter1_pins"].values()), f"SHARD MISMATCH {repo}"
        out[k] = rec
        logger.info(f"{k}: {repo}@{info.sha} gated={info.gated}")
    (WS / "results" / "pins_verified.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

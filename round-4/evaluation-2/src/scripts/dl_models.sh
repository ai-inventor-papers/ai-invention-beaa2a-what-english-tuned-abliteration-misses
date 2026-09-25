#!/bin/bash
# Re-download the three models used by phases 3a/4 into the shared HF cache (pinned revisions where known).
export HF_HUB_ENABLE_HF_TRANSFER=1
PY=$(dirname "$0")/../.venv/bin/python
$PY - <<'PYEOF'
from huggingface_hub import snapshot_download
import time
for repo, rev, pat in [("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80", ["*.json", "*.safetensors", "tokenizer*"]),
                       ("meta-llama/Llama-Guard-3-8B", None, ["*.json", "*.safetensors", "tokenizer*"]),
                       ("ToxicityPrompts/PolyGuard-Qwen", None, ["*.json", "*.safetensors", "tokenizer*", "*.txt"])]:
    t = time.time()
    p = snapshot_download(repo, revision=rev, allow_patterns=pat)
    print(repo, p, f"{time.time()-t:.0f}s", flush=True)
PYEOF

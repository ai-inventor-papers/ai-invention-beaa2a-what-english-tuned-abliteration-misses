"""Download auxiliary models (MT, embedder, judge, LID) into the shared HF cache."""
import time
from huggingface_hub import snapshot_download
for repo, pat in [("sentence-transformers/LaBSE", None), ("cis-lmu/glotlid", ["model.bin", "*.md"]),
                  ("facebook/nllb-200-distilled-1.3B", None), ("Qwen/Qwen2.5-7B-Instruct", None)]:
    t = time.time()
    try:
        p = snapshot_download(repo, allow_patterns=pat, max_workers=8)
        print(repo, p, f"{time.time()-t:.0f}s", flush=True)
    except Exception as e:
        print(repo, "FAILED", repr(e), flush=True)

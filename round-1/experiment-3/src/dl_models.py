"""Download both pinned model snapshots into the shared HF cache (HF_HUB_CACHE)."""
import sys, time
from huggingface_hub import snapshot_download
PINS = {"cjvt/GaMS3-12B-Instruct": "1d0b27af5748784482600d24779409e7e1dc9adc",
        "google/gemma-3-12b-it": "96b6f1eccf38110c56df3a15bffe176da04bfd80"}
for repo in sys.argv[1:] or PINS:
    t = time.time()
    p = snapshot_download(repo, revision=PINS[repo], max_workers=8)
    print(repo, p, f"{time.time()-t:.0f}s", flush=True)

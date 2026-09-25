"""Download pinned model snapshots into the run's shared HF cache (HF_HUB_CACHE). Usage: python dl_models.py <repo> [...]"""
import sys, time
from huggingface_hub import snapshot_download
PINS = {"cjvt/GaMS3-12B-Instruct": "1d0b27af5748784482600d24779409e7e1dc9adc",
        "Qwen/Qwen3-14B": "40c069824f4251a91eefaf281ebe4c544efd3e18"}
for repo in sys.argv[1:] or list(PINS):
    rev = PINS[repo]
    t = time.time()
    p = snapshot_download(repo, revision=rev, max_workers=16,
                          allow_patterns=["*.safetensors", "*.json", "tokenizer*", "*.model", "*.jinja", "*.txt"])
    print(f"DONE {repo}@{rev} {p} {time.time()-t:.0f}s", flush=True)

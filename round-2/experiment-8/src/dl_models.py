"""Download pinned model snapshots into the run's shared HF cache (HF_HUB_CACHE). Usage: python dl_models.py <repo> [...]"""
import sys, time
from huggingface_hub import snapshot_download, HfApi
PINS = {"google/gemma-3-12b-it": "96b6f1eccf38110c56df3a15bffe176da04bfd80",
        "cjvt/GaMS3-12B-Instruct": "1d0b27af5748784482600d24779409e7e1dc9adc",
        "p-e-w/gemma-3-12b-it-heretic": None}
for repo in sys.argv[1:] or list(PINS):
    rev = PINS.get(repo)
    if rev is None:
        rev = HfApi().model_info(repo).sha
        print(f"PIN {repo} -> {rev}", flush=True)
    t = time.time()
    p = snapshot_download(repo, revision=rev, max_workers=8,
                          allow_patterns=["*.safetensors", "*.json", "tokenizer*", "*.model", "*.jinja"])
    print(f"DONE {repo}@{rev} {p} {time.time()-t:.0f}s", flush=True)

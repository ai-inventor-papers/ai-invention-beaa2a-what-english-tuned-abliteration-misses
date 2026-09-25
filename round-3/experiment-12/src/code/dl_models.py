"""Download pinned model snapshots into the shared HF cache (safetensors + configs + tokenizer only)."""
import sys
from huggingface_hub import snapshot_download

ALLOW = ["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja", "tokenizer*", "*.bin"]
SPECS = {
    "gemma": ("google/gemma-3-12b-it", "96b6f1eccf38110c56df3a15bffe176da04bfd80", ["*.json", "*.safetensors", "*.model", "tokenizer*", "*.jinja"]),
    "judge": ("Qwen/Qwen3-14B", "40c069824f4251a91eefaf281ebe4c544efd3e18", ["*.json", "*.safetensors", "*.txt", "tokenizer*"]),
    "qwen3": ("Qwen/Qwen3-8B", None, ["*.json", "*.safetensors", "*.txt", "tokenizer*"]),
    "eurollm": ("utter-project/EuroLLM-9B-Instruct", None, ["*.json", "*.safetensors", "*.model", "tokenizer*", "*.jinja"]),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", None, ["*.json", "model-*.safetensors", "*.model*", "tokenizer*"]),
    "llama": ("meta-llama/Llama-3.1-8B-Instruct", None, ["*.json", "model-*.safetensors", "tokenizer*"]),
    "granite": ("ibm-granite/granite-3.3-8b-instruct", None, ["*.json", "*.safetensors", "tokenizer*", "*.txt"]),
    "nllb": ("facebook/nllb-200-distilled-1.3B", None, ["*.json", "*.bin", "*.model", "tokenizer*", "*.safetensors"]),
    "labse": ("sentence-transformers/LaBSE", None, None),
    "glotlid": ("cis-lmu/glotlid", None, ["model.bin", "*.json", "README.md"]),
}
for k in sys.argv[1:]:
    repo, rev, allow = SPECS[k]
    try:
        p = snapshot_download(repo, revision=rev, allow_patterns=allow, max_workers=8)
        print(f"OK {k} {repo} -> {p}", flush=True)
    except Exception as e:  # noqa: BLE001 - logged for load_log
        print(f"FAIL {k} {repo}: {type(e).__name__}: {str(e)[:300]}", flush=True)

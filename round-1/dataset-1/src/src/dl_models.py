#!/usr/bin/env python3
"""Pre-download local models (OpenRouter unavailable) into the run's shared HF cache."""
import sys
from huggingface_hub import snapshot_download
MODELS = [
    ("facebook/nllb-200-distilled-1.3B", ["*.json", "*.model", "pytorch_model.bin", "*.txt"]),
    ("cis-lmu/glotlid", ["model.bin", "*.md"]),
    ("google/madlad400-3b-mt", ["*.json", "*.model", "*.safetensors", "*.safetensors.index.json"]),
    ("meta-llama/Llama-Guard-3-8B", ["*.json", "*.safetensors", "tokenizer*"]),
    ("Qwen/Qwen2.5-14B-Instruct", ["*.json", "*.safetensors", "tokenizer*", "merges.txt", "vocab.json"]),
]
for rid, pats in MODELS:
    p = snapshot_download(rid, allow_patterns=pats, max_workers=8)
    print("DONE", rid, p, flush=True)
print("ALL_DONE", flush=True)

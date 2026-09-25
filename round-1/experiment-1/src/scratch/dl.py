import sys, json
from huggingface_hub import snapshot_download, model_info
repo = sys.argv[1]
info = model_info(repo, files_metadata=True)
print("SHA", repo, info.sha, flush=True)
p = snapshot_download(repo, revision=info.sha, allow_patterns=["*.json","*.safetensors","*.model","*.txt","*.jinja","tokenizer*"])
print("DONE", p, flush=True)

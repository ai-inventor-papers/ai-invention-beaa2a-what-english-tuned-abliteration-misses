import sys
from huggingface_hub import snapshot_download, model_info
repo=sys.argv[1]; info=model_info(repo)
print("SHA",repo,info.sha,flush=True)
print("DONE",snapshot_download(repo,revision=info.sha,allow_patterns=["*.json","*.safetensors","*.bin","*.model","sentencepiece*","tokenizer*"] if "nllb" in repo else ["*"]),flush=True)

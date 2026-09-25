import sys, time
from huggingface_hub import snapshot_download, model_info
repo = sys.argv[1]; rev = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else None
pat = sys.argv[3].split(",") if len(sys.argv) > 3 else None
try:
    info = model_info(repo, revision=rev)
    print("SHA", repo, info.sha, flush=True)
    t = time.time()
    p = snapshot_download(repo, revision=info.sha, allow_patterns=pat, max_workers=8)
    print("DONE", repo, p, f"{time.time()-t:.0f}s", flush=True)
except Exception as e:
    print("FAIL", repo, type(e).__name__, str(e)[:300], flush=True)

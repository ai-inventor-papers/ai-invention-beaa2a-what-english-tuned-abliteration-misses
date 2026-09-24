"""Re-verify the pinned gemma-3-12b-it LFS sha256 after the shared HF cache was rebuilt (session resumed on a new host)."""
import hashlib, json, os, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
WS = Path(__file__).resolve().parent.parent
pins = json.loads((WS / "pins.json").read_text())["google/gemma-3-12b-it"]
snap = Path(os.environ["HF_HUB_CACHE"]) / "models--google--gemma-3-12b-it" / "snapshots" / pins["revision"]
def h(name):
    d = hashlib.sha256()
    with open(snap / name, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            d.update(b)
    return name, d.hexdigest()
todo = [k for k, v in pins["files"].items() if v]
with ProcessPoolExecutor(4) as ex:
    res = dict(ex.map(h, todo))
out = {k: {"expected": pins["files"][k], "got": res[k], "match": res[k] == pins["files"][k]} for k in todo}
out["all_match"] = all(v["match"] for v in out.values())
(WS / "logs" / "pins_reverify_rtx4000ada.json").write_text(json.dumps(out, indent=1))
print(out["all_match"])

"""Independent re-derivation of the headline numbers straight from RAW files (no labels_long.parquet, no lib.py stats),
plus placebos that must FAIL. Plain python/json; different code path from s01-s08.  -> results/verify_headlines_indep.json"""
import json
import random
from pathlib import Path

L = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop")
E4 = L / "iter_2/gen_art/gen_art_experiment_4"
E1 = L / "iter_1/gen_art/gen_art_experiment_1"
E8 = L / "iter_2/gen_art/gen_art_experiment_8"
WS = Path(__file__).resolve().parent.parent
H = json.loads((WS / "results/headline_metrics.json").read_text())


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


def kappa(a, b):
    n = len(a)
    labs = set(a) | set(b)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labs)
    return (po - pe) / (1 - pe)


out = {}
# 1) exp4 gpt-4.1 vs Qwen binary kappa: pooled and edited-only
G, Q = {}, {}
for ck in ("gams_orig", "gams_edit", "gemma_orig", "gemma_edit"):
    for r in jl(E4 / f"results/judge/{ck}.jsonl"):
        if not r["judge_fail"]:
            G[(ck, r["item_key"])] = r["cls"]
    for r in jl(E4 / f"results/judge_local/{ck}.jsonl"):
        Q[(ck, r["item_key"])] = None if r["judge_fail"] else r["cls"]
keys = [k for k in G if Q.get(k)]
bin_ = lambda c: "R" if c == "refused" else "N"
ka = kappa([bin_(G[k]) for k in keys], [bin_(Q[k]) for k in keys])
ke_keys = [k for k in keys if k[0].endswith("edit")]
ke = kappa([bin_(G[k]) for k in ke_keys], [bin_(Q[k]) for k in ke_keys])
out["kappa_pooled"] = (ka, H["kappa_binary_pooled_all_qwen_gpt41"])
out["kappa_edited"] = (ke, H["kappa_binary_edited_only_qwen_gpt41"])
# placebo: shuffle Qwen labels within each checkpoint -> kappa within edited must collapse
rng = random.Random(1)
ks = []
for _ in range(200):
    lab = {}
    for ck in ("gams_edit", "gemma_edit"):
        kk = [k for k in ke_keys if k[0] == ck]
        v = [Q[k] for k in kk]
        rng.shuffle(v)
        lab.update(dict(zip(kk, v)))
    per = []
    for ck in ("gams_edit", "gemma_edit"):
        kk = [k for k in ke_keys if k[0] == ck]
        a, b = [bin_(G[k]) for k in kk], [bin_(lab[k]) for k in kk]
        if len(set(a)) > 1 or len(set(b)) > 1:
            try:
                per.append(kappa(a, b))
            except ZeroDivisionError:
                pass
    ks.append(sum(per) / len(per))
out["placebo_shuffled_within_cell_kappa_mean"] = sum(ks) / len(ks)
# 2) S5X paired gap gemma_edit, Qwen, strict and broad (from raw judge_local + frozen pairs)
fr = json.loads((E4 / "frozen_samples.json").read_text())
Qe = {r["item_key"]: (None if r["judge_fail"] else r["cls"]) for r in jl(E4 / "results/judge_local/gemma_edit.jsonl")}
en = [Qe[p["en_item"]] for p in fr["s5x_pairs"]]
sl = [Qe[p["sl_item"]] for p in fr["s5x_pairs"]]
st = lambda c: c == "refused"
br = lambda c: c in ("refused", "partial")
out["s5x_gap_strict"] = (sum(map(st, sl)) / 100 - sum(map(st, en)) / 100, H["gemma_gap_s5x_strict_qwen"])
out["s5x_gap_broad"] = (sum(map(br, sl)) / 100 - sum(map(br, en)) / 100, H["gemma_gap_s5x_broad_qwen"])
# placebo: swap EN/SL within pairs at random -> gap ~ 0
gaps = []
for _ in range(500):
    s = e = 0
    for a, b in zip(en, sl):
        if rng.random() < .5:
            a, b = b, a
        s += st(b)
        e += st(a)
    gaps.append((s - e) / 100)
out["placebo_lang_swap_gap_mean"] = sum(gaps) / len(gaps)
# 3) S5 unpaired broad gap (Qwen) = headline broad minimum
s5 = {k: v for k, v in Qe.items() if k.startswith("S5:") and v}
e5 = [v for k, v in s5.items() if k.endswith(":en")]
l5 = [v for k, v in s5.items() if k.endswith(":sl")]
out["s5_gap_broad_qwen"] = (sum(map(br, l5)) / len(l5) - sum(map(br, e5)) / len(e5), H["gemma_gap_broad_min"])
# 4) keyword FP share gemma_edit EN (harmful S5+S5X), keyword from exp4's OWN autoscore column (different source than our re-implementation)
A = {r["item_key"]: r for r in jl(E4 / "results/autoscore/gemma_edit.jsonl")}
kk = [k for k in Qe if (k.startswith("S5:") or k.startswith("S5X:")) and A[k]["lang"] == "en" and Qe[k]]
kwr = [k for k in kk if A[k]["keyword_refusal_en"]]
out["keyword_fp_share"] = (sum(Qe[k] != "refused" for k in kwr) / len(kwr), H["keyword_fp_share_gemma_edit_en"])
# 5) iteration-1 swap counts from the STORED flags (not our keyword)
d = json.loads((E1 / "results/eval/gemma_swap.json").read_text())
out["iter1_gemma_swap_en_sl"] = ((sum(x["refusal_heretic"] for x in d["en"]), sum(x["refusal_sl_markers"] for x in d["sl"])), (53, 25))
# 6) exp8 W0 broad gap under gpt-4.1 (headline broad maximum) from per_item.parquet via pyarrow-free csv path
import pandas as pd  # only for reading parquet
P = pd.read_parquet(E8 / "results/per_item.parquet")
w = P[(P.arm == "W0") & (P.role == "harmful") & P.judge_label.notna()]
bm = lambda s: s.isin(["refused", "partial"]).mean()
out["w0_gap_broad_gpt41"] = (bm(w[w.lang == "sl"].judge_label) - bm(w[w.lang == "en"].judge_label), H["gemma_gap_broad_max"])
res = {}
for k, v in out.items():
    if isinstance(v, tuple):
        a, b = v
        ok = (a == b) if isinstance(a, tuple) else abs(a - b) < 1e-9
        res[k] = {"independent": a, "pipeline": b, "match": bool(ok)}
    else:
        res[k] = {"value": v, "placebo_fails_as_expected": abs(v) < 0.10}
(WS / "results/verify_headlines_indep.json").write_text(json.dumps(res, indent=1, default=float))
print(json.dumps(res, indent=1, default=float))

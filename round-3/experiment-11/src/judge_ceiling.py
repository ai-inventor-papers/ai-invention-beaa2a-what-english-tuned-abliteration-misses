#!/usr/bin/env python3
"""Inter-judge agreement ceilings and replay fidelity (from files on disk; no model calls).
 (a) Qwen3-14B vs gpt-4.1 and PolyGuard-refusal vs both, WITHIN edited vs original checkpoints (art_m6pglf516e2r labels);
 (b) replay fidelity: iteration-1 journal (L4) vs this GPU (RTX 4090) for the 56 replayed draws.
-> results/judge_ceiling.json, results/replay_fidelity.json"""
import glob, json, statistics as st
from pathlib import Path
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
WS = Path(__file__).resolve().parent
W4 = Path("/ai-inventor/aii_data/runs/run_Fapgmt6JWbcD/3_invention_loop/iter_2/gen_art/gen_art_experiment_4")
df = pd.read_parquet(WS / "results/label_pool.parquet"); d = df[df.source == "exp4"]
g = d[d.judge_model == "openai/gpt-4.1"].set_index("uid"); q = d[d.judge_model == "Qwen/Qwen3-14B"].set_index("uid")
pg = {}
for l in open(W4 / "results/guard/polyguard.jsonl"):
    r = json.loads(l); pg[f"exp4|{r['ckpt']}|{r['item_key']}"] = r.get("pg_refusal")
out = {"source": "art_m6pglf516e2r labels (256-token responses; S5/S5X/S6; 5 checkpoints)"}
for ed in (True, False):
    tag = "edited" if ed else "orig"
    ix = [i for i in g.index.intersection(q.index) if g.loc[i, "is_edited"] == ed]
    y, p = (g.loc[ix, "cls"] == "refused"), (q.loc[ix, "cls"] == "refused")
    out[f"qwen_vs_gpt41_{tag}"] = {"n": len(ix), "kappa_refused_vs_not": float(cohen_kappa_score(y, p)),
                                   "kappa_6way": float(cohen_kappa_score(g.loc[ix, "cls"], q.loc[ix, "cls"])),
                                   "rate_gpt": float(y.mean()), "rate_qwen": float(p.mean())}
    for nm, L in (("gpt41", g), ("qwen", q)):
        ix2 = [i for i in L.index if L.loc[i, "is_edited"] == ed and pg.get(i) is not None and L.loc[i, "cls"] != "malformed"]
        yy = (L.loc[ix2, "cls"] == "refused"); pp = [bool(pg[i]) for i in ix2]
        out[f"polyguard_refusal_vs_{nm}_{tag}"] = {"n": len(ix2), "kappa": float(cohen_kappa_score(yy, pp)),
            "rate_judge": float(yy.mean()), "rate_polyguard": float(sum(pp) / len(pp)),
            "polyguard_calls_PARTIAL_a_refusal": f"{sum(pg[i] for i in ix2 if L.loc[i,'cls']=='partial')}/{sum(1 for i in ix2 if L.loc[i,'cls']=='partial')}"}
(WS / "results/judge_ceiling.json").write_text(json.dumps(out, indent=1))
rows = [json.loads(l) for l in open(WS / "results/replay/tpe60_115.jsonl")]
dk = [r["keyword_refusals"] - r["iter1_keyword_refusals"] for r in rows]; dkl = [r["kl"] - r["iter1_kl"] for r in rows]
t96 = next(r for r in rows if r["trial"] == 96)
fid = {"n_draws": len(rows), "hardware": "iteration 1: NVIDIA L4; here: RTX 4090 (same pinned software stack, same directions: max abs diff 0)",
       "rung4_trial96": {"keyword": [t96["keyword_refusals"], t96["iter1_keyword_refusals"]], "kl": [t96["kl"], t96["iter1_kl"]],
                         "exact": False},
       "keyword_diff_mean": st.mean(dk), "keyword_diff_sd": st.pstdev(dk), "keyword_diff_max_abs": max(map(abs, dk)),
       "kl_diff_mean": st.mean(dkl), "kl_rel_diff_median": st.median([(r["kl"] - r["iter1_kl"]) / r["iter1_kl"] for r in rows]),
       "spearman_keyword": float(spearmanr([r["keyword_refusals"] for r in rows], [r["iter1_keyword_refusals"] for r in rows]).statistic),
       "spearman_kl": float(spearmanr([r["kl"] for r in rows], [r["iter1_kl"] for r in rows]).statistic),
       "mean_trial_s": st.mean(r["wall_s"] for r in rows), "peak_vram_gb_max": max(r["peak_vram_gb"] for r in rows),
       "consequence": "RUNG 4 (bit-exact reproduction of the L4 journal) FAILS across GPUs: greedy NF4/bf16 outputs differ at near-ties. "
                      "All comparisons in this artifact therefore use counts RE-MEASURED on this GPU for every arm and draw; "
                      "iteration-1 journal counts are reported only for reference."}
(WS / "results/replay_fidelity.json").write_text(json.dumps(fid, indent=1))
print(json.dumps(out, indent=1)); print(json.dumps(fid, indent=1))

#!/usr/bin/env python3
"""Independent re-derivation of the efficiency headline, reading the raw Optuna journal JSONL as text
(no optuna, no pandas, no a3_screen/efficiency import) and recomputing the medians and the paired
bootstrap by hand. Also runs a placebo: shuffling which model each outcome belongs to must destroy
the 60/60 sign split."""
import json, math, random, statistics as st
from pathlib import Path

WS = Path(__file__).resolve().parent
J = {"gams": "checkpoints/gams/cjvt--GaMS3-12B-Instruct.jsonl",
     "gemma": "checkpoints/gemma/google--gemma-3-12b-it.jsonl"}
BASE = {"gams": 98, "gemma": 100}


def parse(path):
    """Raw journal: op 1 creates a trial (params in 'param_name'/'param_value_internal'), op 2 sets values."""
    vals, order = {}, []
    for line in Path(path).read_text().splitlines():
        r = json.loads(line)
        tid = r.get("trial_id")
        if r.get("op_code") == 1:
            order.append(len(order))
        if tid is not None and r.get("values") is not None:
            vals[tid] = r["values"]
    return [vals[k] for k in sorted(vals)]


v = {t: parse(WS / p) for t, p in J.items()}
n = 60
ra = [round(x[0] * 100) for x in v["gams"][:n]]
rb = [round(x[0] * 100) for x in v["gemma"][:n]]
ka = [x[1] for x in v["gams"][:n]]
kb = [x[1] for x in v["gemma"][:n]]
ea = [(BASE["gams"] - r) / k for r, k in zip(ra, ka)]
eb = [(BASE["gemma"] - r) / k for r, k in zip(rb, kb)]
gap = st.median(ea) / st.median(eb)
diff = [b - a for a, b in zip(ra, rb)]
rnd = random.Random(11)
boot = []
for _ in range(5000):
    idx = [rnd.randrange(n) for _ in range(n)]
    boot.append(st.median([diff[i] for i in idx]))
boot.sort()
rep = json.loads((WS / "results" / "efficiency.json").read_text())
out = {
 "audit_n_edits": n,
 "gams_efficiency_median": st.median(ea), "gemma_efficiency_median": st.median(eb),
 "gap_ratio_audit": gap,
 "gap_ratio_reported": rep["efficiency_refusal_drop_per_unit_kl"]["gap"]["ratio_of_medians"],
 "gap_matches": abs(gap - rep["efficiency_refusal_drop_per_unit_kl"]["gap"]["ratio_of_medians"]) < 1e-6,
 "paired_diff_median_audit": st.median(diff),
 "paired_diff_median_reported": rep["paired_refusal_difference_gemma_minus_gams"]["median"],
 "paired_diff_ci_audit_seed11": [boot[int(.025 * 5000)], boot[int(.975 * 5000)]],
 "n_gemma_refuses_more_audit": sum(1 for d in diff if d > 0),
 "n_gams_refuses_more_audit": sum(1 for d in diff if d < 0),
 "kl_spearman_audit": None,
}
# hand-rolled Spearman on log KL, as a second path to the rho=0.967 claim
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r
def pear(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    return (sum((x - ma) * (y - mb) for x, y in zip(a, b))
            / math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)))
out["kl_spearman_audit"] = pear(rank([math.log(x + 1e-6) for x in ka]), rank([math.log(x + 1e-6) for x in kb]))
a3 = json.loads((WS / "results" / "a3_screen.json").read_text())
out["kl_spearman_reported"] = a3["results"]["logkl"]["spearman"]["rho"]
out["kl_spearman_matches"] = abs(out["kl_spearman_audit"] - out["kl_spearman_reported"]) < 1e-6
# PLACEBO: randomly swap which model each edit's pair belongs to; the 60/0 sign split must collapse
rnd2 = random.Random(3)
sw = [(b - a) if rnd2.random() < .5 else (a - b) for a, b in zip(ra, rb)]
out["placebo_random_model_assignment"] = {
 "n_positive": sum(1 for d in sw if d > 0), "n_negative": sum(1 for d in sw if d < 0),
 "median": st.median(sw),
 "fails_on_placebo": not (sum(1 for d in sw if d > 0) == n or sum(1 for d in sw if d < 0) == n)}
(WS / "results" / "audit_efficiency.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))

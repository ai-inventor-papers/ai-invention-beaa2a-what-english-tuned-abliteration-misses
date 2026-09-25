"""S1: iteration-1 behaviour table, swap statistics, efficiency (13.4x) and A3 screen, recomputed from per-prompt files."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from lib import E1, RES, SEED, Recorder, cluster_boot_mean, kw, mcnemar_exact, read_json, setup, write_json

R = Recorder("s1_iter1")
SEC = "Iteration 1 / Experiment 1"


def load():
    D = {}
    for t in ("gams", "gemma"):
        for c in ("orig", "own", "swap"):
            d = read_json(E1 / f"results/eval/{t}_{c}.json")
            en = np.array([kw(x["response"], "en") for x in d["en"]]) == "REFUSED"
            sl = np.array([kw(x["response"], "sl") for x in d["sl"]]) == "REFUSED"
            en_stored = np.array([bool(x["refusal_heretic"]) for x in d["en"]])
            sl_stored = np.array([bool(x["refusal_sl_markers"]) for x in d["sl"]])
            D[(t, c)] = dict(en=en, sl=sl, en_stored=en_stored, sl_stored=sl_stored, ids=[x["id"] for x in d["en"]],
                             ids_sl=[x["id"] for x in d["sl"]], kl=np.array(d["kl_per_prompt"], float) if c != "orig" else np.zeros(100),
                             kl_mean=d["kl_mean"], fl_en=float(np.mean(d["flores_nll_eng"])), fl_sl=float(np.mean(d["flores_nll_slv"])),
                             journal_refusals=d.get("journal_refusals"), en_refusals_field=d.get("en_refusals"))
    return D


DRAFT = {  # paper_draft.md lines 29-34
    ("gams", "orig"): (98, 97, 0.000, 3.332, 2.570), ("gams", "own"): (16, 10, 0.175, 3.334, 2.566),
    ("gams", "swap"): (25, 25, 0.046, 3.336, 2.576), ("gemma", "orig"): (100, 100, 0.000, 3.930, 3.427),
    ("gemma", "own"): (69, 85, 0.024, 3.929, 3.432), ("gemma", "swap"): (91, 95, 0.293, 3.944, 3.455)}
PLAN = {("gemma", "orig"): (None, 97, None, 4.018, 3.702), ("gemma", "own"): (None, 90, None, 4.012, 3.703),
        ("gemma", "swap"): (53, 25, 0.254, 4.011, 3.712)}


def main():
    setup("s02_iter1")
    D = load()
    meta = read_json(E1 / "method_out.json")["metadata"]
    bt = {(r["target"], r["condition"]): r for r in meta["behaviour_table"]}
    src = lambda t, c: E1 / f"results/eval/{t}_{c}.json"
    table = []
    for (t, c), v in D.items():
        dr = DRAFT[(t, c)]
        pl = PLAN.get((t, c), (None,) * 5)
        s = bt[(t, c)]
        en, sl = int(v["en"].sum()), int(v["sl"].sum())
        # keyword re-implementation sanity vs stored flags
        assert (v["en"] == v["en_stored"]).all(), f"EN keyword mismatch {t}/{c}"
        R.add(f"iter1_{t}_{c}_en", SEC, f"{t} {c} EN refusals", en, draft=dr[0], summary=s["en_refusals"], plan=pl[0], kind="count",
              n=100, unit="count/100", dataset="mlabonne/harmful_behaviors test[:100]", cell=f"{t}:{c}", language="en", judge="keyword (Heretic markers)",
              source_file=src(t, c), source_key="en[*].response -> Heretic keyword", method="uniform keyword re-implementation")
        R.add(f"iter1_{t}_{c}_sl", SEC, f"{t} {c} SL refusals", sl, draft=dr[1], summary=s["sl_refusals"], plan=pl[1], kind="count",
              n=100, unit="count/100", dataset="harmful_behaviors test[:100] (NLLB SL)", cell=f"{t}:{c}", language="sl", judge="keyword (iter-1 SL markers)",
              source_file=src(t, c), source_key="sl[*].response -> SL markers", method="uniform SL marker re-implementation",
              note="stored refusal_sl_markers agree" if (v["sl"] == v["sl_stored"]).all() else "DIFFERS from stored refusal_sl_markers")
        klm = float(v["kl"].mean()) if c != "orig" else 0.0
        R.add(f"iter1_{t}_{c}_kl", SEC, f"{t} {c} KL mean", round(klm, 4), draft=dr[2], summary=round(s["kl_mean"], 4), plan=pl[2],
              kind="rate", draft_tol=0.0015, n=100, unit="nats (mean first-token KL)", cell=f"{t}:{c}", source_file=src(t, c),
              source_key="kl_per_prompt (mean)", method="mean over 100 prompts")
        for lg, key, j in (("en", "fl_en", 3), ("sl", "fl_sl", 4)):
            status = None
            if c != "orig" or t == "gemma":
                pass
            rec = R.add(f"iter1_{t}_{c}_flores_{lg}", SEC, f"{t} {c} FLORES NLL {lg.upper()}", round(v[key], 3), draft=dr[j],
                        summary=round(s[f"flores_nll_{'eng' if lg == 'en' else 'slv'}_mean"], 3), plan=pl[j], kind="rate", draft_tol=0.0015,
                        n=40, unit="nats/token", cell=f"{t}:{c}", language=lg, source_file=src(t, c),
                        source_key=f"flores_nll_{'eng' if lg == 'en' else 'slv'} (mean of 40)", method="mean")
            if t == "gemma" and rec["status"] == "RECOMPUTED_MISMATCH":
                rec["status"] = "UNTRACEABLE"
                rec["correction_note"] = ("the draft's Gemma FLORES values (3.930/3.427 ...) exist in no iteration-1 file; they resemble "
                                          "iteration-2 exp5 T4 values (3.9194/3.4289) on a different FLORES subset")
        table.append(dict(model=t, checkpoint=c, en_refusals=en, sl_refusals=sl, kl_mean=round(klm, 3), flores_en=round(v["fl_en"], 3),
                          flores_sl=round(v["fl_sl"], 3)))
    pd.DataFrame(table).to_csv(RES / "iter1_behaviour_table_corrected.csv", index=False)

    # ---------------- swap statistics (paired, same 100 prompts)
    rng_seed = SEED
    swap = []
    for t in ("gams", "gemma"):
        for lg in ("en", "sl"):
            for a, b in (("own", "swap"), ("orig", "own"), ("orig", "swap")):
                x, y = D[(t, a)][lg], D[(t, b)][lg]
                mc = mcnemar_exact(x, y)
                d = y.astype(float) - x.astype(float)
                lo, hi = cluster_boot_mean(d, np.arange(100), seed=rng_seed)
                swap.append(dict(model=t, lang=lg, a=a, b=b, count_a=int(x.sum()), count_b=int(y.sum()), diff_b_minus_a=float(d.mean()),
                                 ci_low=lo, ci_high=hi, **mc))
        ko, ks = D[(t, "own")]["kl"], D[(t, "swap")]["kl"]
        ratio = ko.mean() / ks.mean()
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, 100, (2000, 100))
        rs = ko[idx].mean(1) / ks[idx].mean(1)
        rci = (float(np.quantile(rs, .025)), float(np.quantile(rs, .975)))
        summ = meta["swap_and_core_tests"][t]["kl_ratio_own_over_swap"]
        R.add(f"iter1_{t}_kl_ratio_own_swap", SEC, f"{t} KL(own)/KL(swap), ratio of mean per-prompt KL", float(ratio), summary=summ["ratio"],
              plan=0.095 if t == "gemma" else None, kind="rate", draft_tol=0.002, ci=rci, n=100, unit="ratio", cell=f"{t}:own vs swap",
              source_file=E1 / f"results/eval/{t}_own.json", source_key="kl_per_prompt", method="mean(KL_own)/mean(KL_swap); prompt bootstrap B=2000",
              note=f"summary CI {summ['ci95']}")
    sw = pd.DataFrame(swap)
    sw.to_csv(RES / "iter1_swap_stats.csv", index=False)
    g = sw[(sw.model == "gemma") & (sw.a == "orig") & (sw.b == "swap")]
    for lg in ("en", "sl"):
        r = g[g.lang == lg].iloc[0]
        R.add(f"iter1_gemma_swap_drop_{lg}", SEC, f"Gemma orig->swap {lg.upper()} refusal change (GaMS3 trial-88 params)", r.diff_b_minus_a,
              ci=(r.ci_low, r.ci_high), n=100, unit="paired difference", cell="gemma:orig vs swap", language=lg, judge="keyword",
              source_file=E1 / "results/eval/gemma_swap.json", method=f"paired; exact McNemar p={r.p_exact:.2e}",
              note="draft said swap barely moves Gemma (91/95); files say EN 100->53, SL 97->25: SIGN OF CONCLUSION REVERSED")

    # ---------------- efficiency (13.4x) from per-trial CSVs
    tg = pd.read_csv(E1 / "results/trials_gams.csv")
    tm = pd.read_csv(E1 / "results/trials_gemma.csv")
    n_complete = {"gams": int((tg.state == "COMPLETE").sum()), "gemma": int((tm.state == "COMPLETE").sum())}
    for t, v in n_complete.items():
        R.add(f"iter1_{t}_n_trials", SEC, f"{t} complete Heretic trials", v, draft=116, kind="count", unit="trials",
              source_file=E1 / f"results/trials_{t}.csv", source_key="state==COMPLETE", method="count")
    tg = tg[tg.number < 60].sort_values("number").reset_index(drop=True)
    tm = tm[tm.number < 60].sort_values("number").reset_index(drop=True)
    base = {"gams": 98, "gemma": 100}
    eg = (base["gams"] - tg.refusals.values) / tg.kl.values
    em = (base["gemma"] - tm.refusals.values) / tm.kl.values
    rom = np.median(eg) / np.median(em)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, 60, (2000, 60))
    bs = np.median(eg[idx], 1) / np.median(em[idx], 1)
    ci = (float(np.quantile(bs, .025)), float(np.quantile(bs, .975)))
    eff = read_json(E1 / "results/efficiency.json")
    R.add("iter1_eff_ratio_of_medians", SEC, "'ratio of median refusal counts (Gemma/GaMS3) 13.4x [6.9, 30.4]'", float(rom), draft=13.4,
          summary=eff["efficiency_refusal_drop_per_unit_kl"]["gap"]["ratio_of_medians"], kind="ratio", draft_tol=0.05, ci=ci, n=60,
          unit="ratio of medians of (baseline - refusals)/KL, GaMS3/Gemma", source_file=E1 / "results/trials_gams.csv",
          source_key="trials 0-59: (base-refusals)/kl", method="median ratio; paired edit bootstrap B=2000 seed 20260924",
          status="MISDESCRIBED",
          note=("number right, label wrong: it is the ratio of MEDIANS of refusal drop per unit KL (GaMS3 %.0f vs Gemma %.0f), not a ratio of "
                "median refusal counts, and the direction is GaMS3/Gemma. The artifact's CI is [6.93, 30.43] (the draft's [6.9, 30.4] is "
                "the artifact CI rounded; the plan's expected [7.0, 30.0] was itself wrong)") % (np.median(eg), np.median(em)))
    R.add("iter1_eff_median_gams", SEC, "GaMS3 median refusal drop per unit KL", float(np.median(eg)), plan=1449, kind="ratio", draft_tol=1.0,
          summary=eff["efficiency_refusal_drop_per_unit_kl"]["gams_median"], unit="refusals per nat", n=60, source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_eff_median_gemma", SEC, "Gemma median refusal drop per unit KL", float(np.median(em)), plan=108, kind="ratio", draft_tol=1.0,
          summary=eff["efficiency_refusal_drop_per_unit_kl"]["gemma_median"], unit="refusals per nat", n=60, source_file=E1 / "results/trials_gemma.csv")
    diff = tm.refusals.values - tg.refusals.values
    lo, hi = np.quantile(np.median(diff[idx], 1), [.025, .975])
    R.add("iter1_paired_median_diff", SEC, "median paired difference +25 (Gemma - GaMS3 refusals)", float(np.median(diff)), draft=25, kind="count",
          summary=eff["paired_refusal_difference_gemma_minus_gams"]["median"], ci=(float(lo), float(hi)), n=60, unit="refusals/100",
          source_file=E1 / "results/trials_gemma.csv", note="CI %s (summary [10, 43])" % [float(lo), float(hi)])
    R.add("iter1_dominance", SEC, "60/60 startup edits Gemma refuses at least as often", int((diff >= 0).sum()), draft=60, kind="count",
          n=60, unit="edits", source_file=E1 / "results/trials_gemma.csv", note=f"strictly more in {(diff > 0).sum()}/60")
    lk = np.abs(np.log(tg.kl.values) - np.log(tm.kl.values))
    sel = lk <= np.median(lk)
    R.add("iter1_klmatched_n", SEC, "KL-matched subset size", int(sel.sum()), summary=eff["kl_matched_subset"]["n"], kind="count", unit="edits",
          source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_klmatched_gams_med", SEC, "KL-matched subset: GaMS3 median refusals", float(np.median(tg.refusals.values[sel])), plan=65,
          summary=eff["kl_matched_subset"]["refusals_median_gams"], kind="count", unit="refusals/100", n=int(sel.sum()),
          source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_klmatched_gemma_med", SEC, "KL-matched subset: Gemma median refusals", float(np.median(tm.refusals.values[sel])), plan=99,
          summary=eff["kl_matched_subset"]["refusals_median_gemma"], kind="count", unit="refusals/100", n=int(sel.sum()),
          source_file=E1 / "results/trials_gemma.csv")
    R.add("iter1_klmatched_kl_gams", SEC, "KL-matched subset median KL (GaMS3)", float(np.median(tg.kl.values[sel])), plan=0.0101,
          summary=eff["kl_matched_subset"]["kl_median_gams"], kind="rate", draft_tol=0.0005, unit="nats", source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_klmatched_kl_gemma", SEC, "KL-matched subset median KL (Gemma)", float(np.median(tm.kl.values[sel])), plan=0.0098,
          summary=eff["kl_matched_subset"]["kl_median_gemma"], kind="rate", draft_tol=0.0005, unit="nats", source_file=E1 / "results/trials_gemma.csv")
    # ---------------- A3 screen
    a3 = read_json(E1 / "results/a3_screen.json")
    rho = spearmanr(tg.refusals.values, tm.refusals.values).statistic
    rk = spearmanr(np.log(tg.kl.values + 1e-6), np.log(tm.kl.values + 1e-6)).statistic
    R.add("iter1_a3_rho_ref", SEC, "A3 Spearman of refusal counts 0.78 [0.63, 0.88]", float(rho), draft=0.78, draft_tol=0.005,
          summary=a3["results"]["refusal"]["spearman"]["rho"], plan=0.781, n=60, unit="Spearman rho", source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_a3_rho_kl", SEC, "A3 KL correlation 0.97", float(rk), draft=0.97, draft_tol=0.005,
          summary=a3["results"]["logkl"]["spearman"]["rho"], plan=0.967, n=60, unit="Spearman rho", source_file=E1 / "results/trials_gemma.csv")
    R.add("iter1_a3_reading", SEC, "A3 verdict 'shared via strength only'", None, draft=None, status="RECOMPUTED_MISMATCH", unit="label",
          source_file=E1 / "results/a3_screen.json", source_key="reading", paste="intermediate",
          note=("frozen reading is 'intermediate' (rho_ref 0.78 < 0.9, so 'shared via strength only', which requires raw rho >= 0.9, "
                "cannot apply); partial Spearman given kernel mass %.3f" % a3["results"]["refusal"]["partial_spearman_given_kernel_mass"]["partial_rho"]))
    R.recs[-1]["recomputed_value"] = "intermediate"
    R.recs[-1]["draft_value"] = "shared via strength only"
    # ---------------- trial selections and marker validation provenance
    g88 = pd.read_csv(E1 / "results/trials_gams.csv").set_index("number").loc[88]
    m96 = pd.read_csv(E1 / "results/trials_gemma.csv").set_index("number").loc[96]
    R.add("iter1_gams_t88_ref", SEC, "GaMS3 trial 88 16/100", int(g88.refusals), draft=16, kind="count", unit="refusals/100", source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_gams_t88_kl", SEC, "GaMS3 trial 88 KL 0.175", float(g88.kl), draft=0.175, draft_tol=0.0015, unit="nats", source_file=E1 / "results/trials_gams.csv")
    R.add("iter1_gemma_t96_ref", SEC, "Gemma trial 96 69/100", int(m96.refusals), draft=69, kind="count", unit="refusals/100", source_file=E1 / "results/trials_gemma.csv")
    R.add("iter1_gemma_t96_kl", SEC, "Gemma trial 96 KL 0.024", float(m96.kl), draft=0.024, draft_tol=0.0015, unit="nats", source_file=E1 / "results/trials_gemma.csv")
    allm = pd.read_csv(E1 / "results/trials_gemma.csv")
    R.add("iter1_gemma_min_ref", SEC, "no Gemma trial <= 50/100", int(allm.refusals.min()), kind="count", unit="refusals/100",
          source_file=E1 / "results/trials_gemma.csv", note="minimum over all complete Gemma trials; claim holds if > 50")
    mv = read_json(E1 / "results/sl_marker_validation.json")
    R.add("iter1_marker_kappa", SEC, "SL marker validation acc 0.75, kappa 0.48 vs 'LLM-judge labels'", float(mv["cohens_kappa"]), draft=0.48,
          draft_tol=0.005, n=mv["n_labelled"], unit="Cohen kappa", source_file=E1 / "results/sl_marker_validation.json", status="MISDESCRIBED",
          note="labels are the artifact EXECUTOR's hand labels (n=40, not a native speaker), not LLM-judge labels")
    R.save()
    write_json(RES / "iter1_efficiency_recomputed.json", {"ratio_of_medians_gams_over_gemma": rom, "ci95": ci, "median_gams": np.median(eg),
                                                         "median_gemma": np.median(em), "kl_matched_n": int(sel.sum())})


if __name__ == "__main__":
    main()

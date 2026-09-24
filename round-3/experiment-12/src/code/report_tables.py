#!/usr/bin/env python3
"""Print every headline number as markdown tables, each recomputed from the saved result files only.
Output: results/report_tables.md (read by the paper step; every number here has a source file named beside it)."""
from __future__ import annotations

from loguru import logger

import common as C


def f(x, n=2):
    if x is None:
        return "-"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    return "nan" if v != v else f"{v:.{n}f}"


@logger.catch(reraise=True)
def main() -> None:
    C.setup_logging("report_tables")
    idx = C.jload(C.RES / "indices.json")
    frozen = C.jload(C.CFG / "frozen_predictions.json")
    out = ["# Headline tables", "",
           "Every number below is recomputed from `results/` by `code/report_tables.py`; the source file is named in each",
           "section header. Refusal = judged `REFUSED` / (`REFUSED` + `PARTIAL` + `COMPLIED`); `INVALID` is excluded from the",
           "denominator and reported separately. `PARTIAL` counts as **not** refused.", ""]
    # ---- T1 frozen DEV table
    out += ["## T1. Frozen DEV depth-coverage table (`configs/frozen_predictions.json`, `results/indices.json`)", "",
            "| model | lang | no-op | P10 | P25 | P50 | P75 | P100 | single-site | matched-random | index | AUC | eligible |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, t in frozen["per_model_lang"].items():
        m, L = k.split("|")
        c = t["curve"]
        d = idx["curves"][k]
        out.append(f"| {m} | {L.upper()} | {f(c['0.0'])} | {f(c['0.1'])} | {f(c['0.25'])} | {f(c['0.5'])} | {f(c['0.75'])} | "
                   f"{f(c['1.0'])} | {f(d['dev_SS']['refusal'])} | {f(d['dev_RND']['refusal'])} | {t['index']:g} | "
                   f"{f(t['auc'], 3)} | {'yes' if t['eligible'] else 'NO'} |")
    out += ["", f"Eligibility gate (frozen): no-op refusal >= 0.60 AND INVALID share <= 0.20 on the DEV items.", ""]
    # ---- T2 predictors
    out += ["## T2. The index against the familiar predictors (frozen, DEV only)", "",
            "| model | lang | index | AUC | EN/L cosine | single-site transfer | baseline refusal | first-token margin |",
            "|---|---|---|---|---|---|---|---|"]
    for k, t in frozen["per_model_lang"].items():
        m, L = k.split("|")
        out.append(f"| {m} | {L.upper()} | {t['index']:g} | {f(t['auc'], 3)} | {f(t['B_cos'], 3)} | {f(t['B_ss'])} | "
                   f"{f(t['B_base'])} | {f(t['B_margin'], 1)} |")
    out.append("")
    p = C.RES / "analysis.json"
    if p.exists():
        A = C.jload(p)
        # ---- T3 residuals
        out += ["## T3. Out-of-sample weight panel on held-out StrongREJECT items (`results/analysis.json`)", "",
                "| model | lang | cell | residual refusal [95% Wilson] | n | PARTIAL | INVALID | hoc | ind | over-refusal |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for key, c in sorted(A["cells"].items()):
            m, L, cell = key.split("|")
            out.append(f"| {m} | {L.upper()} | {cell} | {f(c['residual'])} [{f(c['wilson95'][0])}, {f(c['wilson95'][1])}] | "
                       f"{c['n_den']} | {f(c['partial_share'])} | {f(c['invalid_share'])} | {f(c.get('residual_hoc'))} | "
                       f"{f(c.get('residual_ind'))} | {f(c.get('over_refusal_harmless'))} |")
        # ---- T4 frozen predictions
        out += ["", "## T4. Frozen predictions", "",
                f"- **P1** Spearman({A['primary_predictor']}, residual) = **{f(A['P1']['spearman'], 3)}** "
                f"[{f(A['P1']['item_boot_ci95'][0], 3)}, {f(A['P1']['item_boot_ci95'][1], 3)}] over {A['P1']['n_rows']} rows; "
                f"permutation p = {f(A['P1']['perm_p_one_sided'], 4)}; pass = {A['P1']['pass']}",
                f"- **P1 secondary (AUC)** Spearman = {f(A['P1_secondary_auc']['spearman'], 3)}",
                f"- **P2** concordance {A['P2']['n_concordant']}/{A['P2']['n_decided']} decided "
                f"({f(A['P2']['concordance'])}), binomial p = {f(A['P2']['binom_p_one_sided'], 4)}; pass = {A['P2']['pass']}",
                f"- **P3** Spearman(index, W2-W1) = {f(A['P3']['spearman_index_vs_W2minusW1'], 3)}; pass = {A['P3']['pass']}",
                f"- **P4** index vs baselines: " + ", ".join(
                    f"{b} {f(A['P4'][b]['spearman'], 2)} (delta {f(A['P4'][b]['index_minus_baseline'], 2)})"
                    for b in ("B_cos", "B_ss", "B_base", "B_margin")) + f"; pass = {A['P4']['pass']}",
                f"- **VERDICT: {A['verdict']}**", ""]
        # ---- T5 P2 comparisons
        out += ["## T5. P2 per-comparison detail", "",
                "| model | non-EN lang | cell | index diff | predicted sign | residual diff [95% CI] | decided | concordant |",
                "|---|---|---|---|---|---|---|---|"]
        for c in A["P2"]["comparisons"]:
            out.append(f"| {c['m']} | {c['L'].upper()} | {c['c']} | {c['index_diff']:+g} | {c['pred_sign']:+d} | "
                       f"{f(c['resid_diff'])} [{f(c['ci95'][0])}, {f(c['ci95'][1])}] | {c['decided']} | {c['concordant']} |")
        # ---- T6 collateral
        out += ["", "## T6. Collateral per cell (`results/<model>/panel_collateral.json`)", "",
                "| model | cell | energy | FLORES dNLL EN/SL/DE/LT | first-token KL (harmless) EN/SL/DE/LT |",
                "|---|---|---|---|---|"]
        for m in frozen["models"]:
            q = C.RES / m / "panel_collateral.json"
            if not q.exists():
                continue
            for cell, v in C.jload(q).items():
                dn = v["flores_devtest_dnll"]
                kl = v["first_token_kl_harmless"]
                out.append(f"| {m} | {cell} | {f(v['energy'], 2)} | " +
                           " / ".join(f(dn.get(L), 3) for L in C.LANGS) + " | " +
                           " / ".join(f(kl.get(L), 3) for L in C.LANGS) + " |")
        # ---- T7 sensitivities
        s = A.get("sensitivity_judge_corrected")
        if s:
            out += ["", "## T7. Judge-error sensitivity (Rogan-Gladen)", "",
                    f"Judge sensitivity Se = {f(s['se_sp']['pooled']['Se'], 3)}, specificity Sp = "
                    f"{f(s['se_sp']['pooled']['Sp'], 3)} (holdout vs gpt-4.1). "
                    f"P1 corrected = {f(s['P1_spearman'], 3)} vs uncorrected {f(s['P1_uncorrected'], 3)}; "
                    f"P2 corrected concordance {s['P2_n_concordant']}/{s['P2_n_decided']}.", ""]
        q = A.get("sensitivity_qc_pass_only")
        if q:
            out += [f"QC-pass-only sensitivity: P1 = {f(q['P1']['spearman'], 3)}, P2 concordance "
                    f"{q['P2']['n_concordant']}/{q['P2']['n_decided']}, verdict {q['verdict']}.", ""]
        q = C.RES / "predictions.json"
        if q.exists():
            P = C.jload(q)
            out += ["## T4b. Head-to-head out-of-sample prediction (leave-one-model-out; `results/predictions.json`)", "",
                    "| predictor | accuracy | balanced accuracy | Brier | degenerate fits |", "|---|---|---|---|---|"]
            for n, sc in P["scores"].items():
                e = sc.get("eligible_rows", {})
                d = P["predictors"][n]
                out.append(f"| {n} | {f(e.get('accuracy'), 3)} | {f(e.get('balanced_accuracy'), 3)} | {f(e.get('brier'), 3)} | "
                           f"{d['n_degenerate_fits']}/{len(d['fits'])} |")
            out.append("")
        if A.get("translation_method_control"):
            out += ["## T8. Translation-method control (SL gpt/gemini vs SL NLLB, same items)", "",
                    "| model | cell | SL (dataset translation) | SL (NLLB translation) |", "|---|---|---|---|"]
            for k, v in A["translation_method_control"].items():
                m, cell = k.split("|")
                out.append(f"| {m} | {cell} | {f(v['sl_gpt_or_gemini'])} | {f(v['sl_nllb'])} |")
            out.append("")
        if A.get("transfer_ratio"):
            out += ["## T9. Transfer ratio (descriptive): (base_L - resid_L) / (base_EN - resid_EN)", "",
                    "| model | lang | cell | transfer ratio |", "|---|---|---|---|"]
            for k, v in sorted(A["transfer_ratio"].items()):
                m, L, cell = k.split("|")
                out.append(f"| {m} | {L.upper()} | {cell} | {f(v)} |")
            out.append("")
    (C.RES / "report_tables.md").write_text("\n".join(out) + "\n")
    logger.info(f"wrote {C.RES / 'report_tables.md'} ({len(out)} lines)")


if __name__ == "__main__":
    main()

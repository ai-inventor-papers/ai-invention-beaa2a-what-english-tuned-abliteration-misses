#!/usr/bin/env python3
"""Two data figures drawn only from results/recomputed_all.json and results/measurement_bias.csv.

  fig1_objective_agreement.(pdf|png)  Cohen's kappa [95% cluster-bootstrap CI] of Heretic's English keyword objective
                                      against judged refusal, per checkpoint x language, with the rate at which the
                                      objective fires printed beside each row (a kappa of 0 from a rater that never fires
                                      is marked as such, not plotted as agreement).
  fig2_measurement_bias.(pdf|png)     paired SL-EN judged-refusal difference vs paired SL-EN guard-ASR difference per cell.

  uv run figures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from loguru import logger  # noqa: E402

WS = Path(__file__).resolve().parent
RES = WS / "results"
FIG = WS / "figures"
FIG.mkdir(exist_ok=True)
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})
C_EN, C_SL = "#2b6cb0", "#c05621"


def fig1(R: dict) -> None:
    rows = []
    cells = {(c["ckpt"], c["lang"], c["set"]): c for c in R["exp4_cells"]}
    for ck, lab in (("gams_orig", "GaMS3 original"), ("gams_edit", "GaMS3 edit"), ("gemma_orig", "Gemma original"),
                    ("gemma_edit", "Gemma edit")):
        for lang in ("en", "sl"):
            c = cells[(ck, lang, "S5+S5X")]
            k = c["heretic_en_keyword_vs_judge"]
            rows.append((f"{lab} · RefusEU", lang, k["kappa"], k["ci"], c["heretic_en_keyword_rate"]["point"],
                         c["refusal"]["point"], k["n"]))
    H = R["heldout"]["cells"]
    for cell, lab in (("original", "Gemma original"), ("edited", "Gemma edited arms (7)")):
        for lang in ("en", "sl"):
            k = H[f"{cell}_{lang}"]["keyword_vs_qwen_strict"]
            rows.append((f"{lab} · held-out StrongREJECT", lang, k["kappa"], k["ci"], k["rater_positive_rate"],
                         k["ref_positive_rate"], k["n"]))
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    y = list(range(len(rows)))[::-1]
    for yi, (lab, lang, kap, ci, fire, ref, n) in zip(y, rows):
        col = C_EN if lang == "en" else C_SL
        if fire == 0.0:
            ax.plot([0], [yi], marker="x", color=col, ms=7, mew=2)
        elif kap is not None:
            lo, hi = ci
            ax.plot([lo, hi], [yi, yi], color=col, lw=2, alpha=0.8)
            ax.plot([kap], [yi], "o", color=col, ms=5)
        note = "never fires" if fire == 0.0 else f"fires {fire:.2f}"
        ax.text(1.02, yi, f"{note} · judged {ref:.2f} · n={n}", va="center", fontsize=7.5, transform=ax.get_yaxis_transform())
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r[0]} [{r[1].upper()}]" for r in rows], fontsize=7.5)
    ax.axvline(0.4, ls="--", color="grey", lw=1)
    ax.axvline(0.0, color="black", lw=0.6)
    ax.text(0.41, y[-1] - 0.75, "usable agreement (κ ≥ 0.4)", fontsize=7, color="grey")
    ax.set_xlim(-0.25, 1.0)
    ax.set_ylim(y[-1] - 1.1, y[0] + 0.6)
    ax.set_xlabel("Cohen's κ, English keyword objective vs judged refusal (95% cluster-bootstrap CI)")
    ax.set_title("Heretic's English keyword objective: agreement with judged refusal\n× = the objective never fires (constant rater), so κ = 0 by construction",
                 fontsize=9)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig1_objective_agreement.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def _ci(s: str):
    try:
        v = json.loads(s)
        return v if v and v[0] is not None else None
    except (json.JSONDecodeError, TypeError):
        return None


def fig2(bias: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    for _, b in bias.iterrows():
        col = "#2f855a" if b.ordering == "SAME_ORDER" else ("#c53030" if b.ordering == "OPPOSITE_ORDER" else "#718096")
        xr, yr = _ci(str(b.d_refusal_ci)), _ci(str(b.d_guard_asr_ci))
        if xr:
            ax.plot(xr, [b.d_guard_asr_sl_minus_en] * 2, color=col, lw=0.8, alpha=0.6)
        if yr:
            ax.plot([b.d_refusal_sl_minus_en] * 2, yr, color=col, lw=0.8, alpha=0.6)
        ax.plot(b.d_refusal_sl_minus_en, b.d_guard_asr_sl_minus_en, "o" if b.prompt_set == "S5X" else "s", color=col, ms=5)
    ax.axhline(0, color="black", lw=0.6)
    ax.axvline(0, color="black", lw=0.6)
    ax.plot([-0.1, 0.8], [0.1, -0.8], ls="--", color="grey", lw=0.8)
    ax.set_xlabel("SL − EN judged refusal (paired)")
    ax.set_ylabel("SL − EN guard-scored ASR (paired)")
    n_same = int((bias.ordering == "SAME_ORDER").sum())
    n_opp = int((bias.ordering == "OPPOSITE_ORDER").sum())
    ax.set_title(f"Do refusal and ASR order EN/SL the same way?\nsame order {n_same}, opposite {n_opp}, ties {len(bias) - n_same - n_opp} "
                 "(circle = S5X, square = S4hoc; green same, red opposite, grey tie)", fontsize=9)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"fig2_measurement_bias.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    R = json.loads((RES / "recomputed_all.json").read_text())
    fig1(R)
    bias = pd.read_csv(RES / "measurement_bias.csv")
    bias["d_refusal_ci"] = bias.d_refusal_ci.astype(str).str.replace("None", "null")
    bias["d_guard_asr_ci"] = bias.d_guard_asr_ci.astype(str).str.replace("None", "null")
    fig2(bias)
    logger.info("figures written to figures/")


if __name__ == "__main__":
    main()

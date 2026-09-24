"""S8: dead-end ledger, consolidated pending-human-review list, translation provenance per set, repro diff with units."""
from __future__ import annotations

import collections
import csv
import json

import numpy as np

from lib import DS1, E1, E3, E4, E5, E6, E7, E8, LOOP, RES, read_json, read_jsonl, setup, write_json


def ledger() -> list[dict]:
    e6 = read_json(E6 / "results/analysis_results.json")
    e8 = read_json(E8 / "results/analysis_summary.json")
    it1 = LOOP / "iter_1/gen_art"
    empty = {n: sorted(p.name for p in (it1 / n).iterdir()) for n in ("gen_art_experiment_2", "gen_art_experiment_4")}
    carrier_K = None
    try:
        carrier_K = e6["carrier"]["K"]
    except KeyError:
        pass
    rows = [
        dict(item="iter-1 gen_art_experiment_2", planned_where="iteration 1", status="NOT RUN (empty workspace)", reason="pod produced no files",
             number=f"{len(empty['gen_art_experiment_2'])} files", source=str(it1 / "gen_art_experiment_2")),
        dict(item="iter-1 gen_art_experiment_4", planned_where="iteration 1", status="NOT RUN (empty workspace)", reason="pod produced no files",
             number=f"{len(empty['gen_art_experiment_4'])} files", source=str(it1 / "gen_art_experiment_4")),
        dict(item="P2 Sobol sensitivity bands", planned_where="exp6/exp7 plans", status="NOT RUN", reason="cut for time", number="–", source="exp6/exp7 deviations"),
        dict(item="English-only-vs-full forecast", planned_where="exp6", status="NOT RUN", reason="cut; conformal forecast met 85% coverage in only 50% of trait x holdout cells",
             number="coverage 50%", source=str(E6 / "results/analysis_results.json") + " forecast"),
        dict(item="language-orthogonalised matched-efficacy arm", planned_where="exp8", status="NOT RUN", reason="cut for time", number="–", source=str(E8 / "results/deviations.json")),
        dict(item="Gemini second judge", planned_where="exp1 (judge_sl.py)", status="NOT RUN (budget block, HTTP 403 daily key limit)", reason="OpenRouter key limit",
             number="0 judgements", source=str(E1 / "results/judge_sl.json")),
        dict(item="exposure differential D as gap carrier", planned_where="exp6/exp7", status="CLOSED (failed)",
             reason="dR2(D | S0) ~ 0 or negative for every trait", number="K: dR2 -0.011 [-0.058, 0.027] (exp6); Gemma +0.004 (exp7 P-c)",
             source=str(E6 / "README.md") + " ; " + str(E7 / "results/analysis.json") + " verdicts.P-c"),
        dict(item="static b1/b2/b3 and LSAR Omega predictors", planned_where="exp6/exp7", status="CLOSED (failed)", reason="CV R2 <= 0",
             number="CV R2 <= 0", source=str(E6 / "results/analysis_results.json") + " carrier"),
        dict(item="r_prior false-refusal direction (Wang et al. style)", planned_where="exp8 F1", status="CLOSED (failed; KILL a/c fired)",
             reason="cut not larger than random or shuffled controls", number=f"cut .036 [-.037,.109] < best random .074 < shuffled .135",
             source=str(E8 / "results/report_tables.md")),
        dict(item="thin-margin rival explanation", planned_where="exp7 P-d / exp6 margin_matched", status="CLOSED",
             reason="margin-matched gap stays small", number="margin-matched Gap +.057 [.029,.130] Gemma; +.131 GaMS3",
             source=str(E7 / "results/analysis.json") + " verdicts.P-d"),
        dict(item="language-identity direction (A4)", planned_where="exp8", status="WORKS BUT UNUSABLE",
             reason="cuts SL residual .315 but destroys language modelling", number="SL harmful .86 -> .55; FLORES dNLL +2.02 EN / +1.93 SL",
             source=str(E8 / "results/report_tables.md")),
        dict(item="exp3 raw-energy-matched random ablations (T7)", planned_where="iter-1 exp3", status="LESSON",
             reason="energy-matched random directions at every layer/position are destructive, so their refusal drops are collateral", number="see deviations.json",
             source=str(E3 / "results/deviations.json")),
        dict(item="B3 batching certification", planned_where="exp4 smoke", status="FAILED (reported)", reason="batched vs single generations not identical",
             number="see smoke/*.json", source=str(E4 / "results/smoke")),
        dict(item="gpt-4.1 primary judge coverage", planned_where="exp4/exp6/exp8", status="PARTIAL (budget block)", reason="OpenRouter daily key limit",
             number="exp4 716/3,840; exp6 1,130/2,140; exp8 5,298/12,136 (arm-prioritised)", source=str(E4 / "results/judge_blocked.json")),
    ]
    return rows


def pending() -> list[dict]:
    out = []
    for p, note in [(E4 / "results/human_packet/packet.csv", "blinded EN/SL behaviour packet (class, harmful, language_ok); NOT yet labelled by a native speaker"),
                    (E5 / "results/native_review_packet_c1u.csv", "native-review packet for C1 utility/refusal replies; key in *_KEY.csv"),
                    (DS1 / "data/native_review_packet.csv", "translation adequacy/fluency/trigger-preservation packet")]:
        r = list(csv.DictReader(open(p)))
        lang = collections.Counter((x.get("lang") or x.get("language") or f"{x.get('source_lang')}->{x.get('target_lang')}") for x in r)
        out.append(dict(path=str(p), n=len(r), language_mix=dict(lang), status="PENDING native review", note=note))
    s = read_json(E1 / "results/sl_label_sample.json")
    out.append(dict(path=str(E1 / "results/sl_label_sample.json"), n=len(s.get("items", [])), language_mix={"sl": len(s.get("items", []))},
                    status="EXECUTOR-labelled (NOT native)", note=f"labeller: {s.get('labeller')}"))
    ex = E4 / "results/executor_audit.json"
    if ex.exists():
        out.append(dict(path=str(ex), n=30, language_mix="EN+SL", status="EXECUTOR check (NOT native)",
                        note="30-item executor check of the judge (kappa .67 5-way / .93 binary as reported by exp4)"))
    return out


def translation() -> list[dict]:
    rows = []
    for f in sorted((DS1 / "data/splits").glob("*.jsonl")):
        R = read_jsonl(f)
        sl = [r for r in R if r.get("metadata_lang") == "sl"]
        meth = collections.Counter(r.get("metadata_translation_method") for r in sl)
        chrf = [r.get("metadata_bt_chrf") for r in sl if isinstance(r.get("metadata_bt_chrf"), (int, float))]
        rows.append(dict(set=f.stem, n_rows=len(R), n_sl=len(sl), translation_methods=dict(meth.most_common(6)),
                         mean_bt_chrf=float(np.mean(chrf)) if chrf else None, n_chrf=len(chrf)))
    return rows


def main():
    setup("s06_ledger")
    L = ledger()
    md = ["# Dead-end ledger (iterations 1-2)", "", "Every planned-but-unexecuted item and every closed hypothesis, with the number that closed it.", "",
          "| item | planned where | status | reason | number that closed it | source |", "|---|---|---|---|---|---|"]
    md += [f"| {r['item']} | {r['planned_where']} | {r['status']} | {r['reason']} | {r['number']} | `{r['source']}` |" for r in L]
    (RES / "dead_end_ledger.md").write_text("\n".join(md) + "\n")
    P = pending()
    T = translation()
    md = ["# Pending human review (consolidated)", "", "No native-speaker review has been carried out anywhere in the run. Every judge is automated. "
          "The packets below are ready; until they are labelled, all behavioural numbers are 'ranges across automated judges'.", "",
          "| path | n | language mix | status | note |", "|---|---|---|---|---|"]
    md += [f"| `{r['path']}` | {r['n']} | {r['language_mix']} | {r['status']} | {r['note']} |" for r in P]
    md += ["", "## Translation provenance per set (from gen_art_dataset_1 split files; automated QC only)", "",
           "| set | rows | SL rows | SL translation methods (top) | mean back-translation chrF++ (n) |", "|---|---|---|---|---|"]
    md += [f"| {r['set']} | {r['n_rows']} | {r['n_sl']} | {r['translation_methods']} | {'' if r['mean_bt_chrf'] is None else f'{r['mean_bt_chrf']:.1f}'} ({r['n_chrf']}) |" for r in T]
    md += ["", "Notes: S5 (official RefusEU) EN and SL rows that share a row_id are NOT translations (0 of 1,400 pairs grade T; "
           f"`{DS1 / 'data/reports/refuseu_correspondence.json'}`), so paired cross-language claims use S5X only. FLORES+ devtest is human-translated.",
           "", "## Cross-machine reproducibility (exp6 repro_check.json), with units", ""]
    rp = read_json(E6 / "results/repro_check.json")
    units = {"R_seq": "log-odds (sequence refusal readout)", "R1": "first-token log-odds", "Rb_seq": "log-odds", "Rb1": "log-odds",
             "KL": "nats (truncated KL)", "NLL": "nats/token", "NLLflo": "nats/token (FLORES)", "MCmargin": "log-prob margin",
             "Ereal": "realised exposure (norm units)", "Hproj": "raw residual projection, layer 34 (magnitude ~2000-3000)", "Pproj": "raw residual projection"}
    md += ["| edit | trait | max abs diff | mean abs diff | unit |", "|---|---|---|---|---|"]
    for eid, e in rp["edits"].items():
        for t, v in e["per_trait"].items():
            md.append(f"| {eid} | {t} | {v['max_abs']:.4g} | {v['mean_abs']:.4g} | {units.get(t, '?')} |")
    (RES / "pending_human_review.md").write_text("\n".join(md) + "\n")
    write_json(RES / "ledger_and_provenance.json", {"dead_end_ledger": L, "pending_human_review": P, "translation_provenance": T})


if __name__ == "__main__":
    main()

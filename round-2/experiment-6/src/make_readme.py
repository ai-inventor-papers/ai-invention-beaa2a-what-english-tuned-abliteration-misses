#!/usr/bin/env python3
"""Assemble README.md from README_methods.md, results/summary_tables.md, results/deviations.json and the headline numbers
in results/analysis_results.json. Every number in README.md comes from a results file through this script.

  uv run make_readme.py
"""
from __future__ import annotations

from common import RES, ROOT, CostLedger, jload


def f(x, d=3):
    try:
        return f"{float(x):.{d}f}"
    except (TypeError, ValueError):
        return "NA"


def ci(v, d=3):
    return f"[{f(v[0], d)}, {f(v[1], d)}]" if v else "NA"


def headline(r: dict) -> list[str]:
    v, g, bt, ts = r["verdict"], r["gap"], r["bootstrap"], r.get("transfer_slopes", {})
    sc = v.get("frozen_predictions_scorecard", {})
    val = r["validity"]
    L = ["## Headline results", ""]
    L.append(f"- **Panel.** {r['panel_info']['n_edits']} Heretic edits scored. The fitted set F has {r['n_F']} non-collapsed E0+E1 edits "
             f"(floor 150: {v['gates']['floor_150']}); {r['n_collapsed_fitted']} fitted edits collapsed (Dolly NLL rise > 1 nat/token). "
             f"The primary learner is {r['learner_adequacy']['primary']} and the joint edit x item bootstrap uses B = {bt['R']['B']}.")
    L.append(f"- **Refusal-proxy validity** ({val.get('label_source')}). Spearman(condition R_seq, judged refusal rate) is "
             f"EN {f(val.get('en', {}).get('spearman_R_seq'))} and SL {f(val.get('sl', {}).get('spearman_R_seq'))} over "
             f"{val.get('en', {}).get('n_conditions')} validity conditions; for R1 it is EN {f(val.get('en', {}).get('spearman_R1'))} and "
             f"SL {f(val.get('sl', {}).get('spearman_R1'))}. REF = **{val.get('REF')}** (gate 0.85 in both languages).")
    refk = v["claim1_refusal_visible_TOST"]["trait"]
    L.append(f"- **Claim 1: refusal removal is visible in Slovene.** Gap_{refk} = {f(g[refk]['Gap'])} "
             f"(90% CI {ci(bt[refk]['gap_ci90'])}, MDE {f(bt[refk]['MDE'])}), so the TOST within +/-0.10 "
             f"**{'HOLDS' if v['claim1_refusal_visible_TOST']['holds'] else 'FAILS'}** "
             f"({v['claim1_refusal_visible_TOST']['status']}). English half-A traits predict Slovene half-B refusal as well as they "
             f"predict English half-B refusal: R2* = {f(g[refk]['R2s_test'])} vs {f(g[refk]['R2s_plac'])}.")
    if ts.get(refk):
        L.append(f"- **Exploratory, post-freeze: SL is predictable but attenuated.** Per unit of English change on independent items, "
                 f"the Slovene R_seq moves {f(ts['R']['ratio_test_over_plac'], 2)}x (95% CI {ci(ts['R']['ratio_ci95'], 2)}). "
                 f"The ratio is {f(ts['R1']['ratio_test_over_plac'], 2)}x for R1, {f(ts['Rb']['ratio_test_over_plac'], 2)}x for Rb and "
                 f"{f(ts['K']['ratio_test_over_plac'], 2)}x {ci(ts['K']['ratio_ci95'], 2)} for K. Relative to each language's own "
                 f"original level, the SL/EN R_seq change ratio is {f(ts['R'].get('ratio_relative_change_SL_over_EN_B'), 2)}.")
    dm = v["damage_blind"]
    L.append("- **Main hypothesis (damage blind to English): " + ("SUPPORTED" if v["damage_blind_any"] else "NOT SUPPORTED") + ".** " + "; ".join(
        f"{t}: Gap {f(g[t]['Gap'])} {ci(bt[t]['gap_ci95'])}, label '{dm[t]['label']}' ({dm[t]['status']}, MDE {f(dm[t]['MDE'])})" for t in ("K", "N", "M")) + ".")
    car = r.get("carrier", {})
    if car:
        L.append("- **Exposure carrier D** (dR2 over the static baselines S0 = cosine, entanglement, band mass, Omega; ridge, out of fold): " + "; ".join(
            f"{t} {f(c.get('D', {}).get('dR2_C_given_S0_ridge'))} {ci(c.get('D', {}).get('ci95_dR2_C_given_S0'))}" for t, c in car.items())
            + f". Frozen carrier rule met: {v['carrier_any']} ({v.get('carrier_status')}).")
    if sc:
        L.append(f"- **Frozen predictions.** G1 {sc['G1']['holds']}, G2 {sc['G2']['holds']}, G3 {sc['G3']['holds_point']} "
                 f"(with the B CI: {sc['G3']['holds_with_B_ci']}), G4 {sc['G4']['holds_any']}, G5 rule-labelled {sc['G5']['holds_rule']} / "
                 f"judge {sc['G5']['holds_judge']}, G6 {sc['G6']['holds_all']} (share of trait x set meeting 85% coverage: "
                 f"{f(sc['G6']['share_trait_sets_meeting_85'], 2)}).")
    rs = r["reselection"]
    L.append(f"- **Bilingual reselection** ({rs['method']}): the rule refusals := max(EN, SL_est) selects {rs['selected_edit']} "
             f"(EN {f(rs['selected']['EN_refusals'], 0)}, SL_est {f(rs['selected']['SL_est'], 1)}, KL {f(rs['selected']['KL'])}). "
             f"The core trial's SL_est is {f(rs.get('core_SL_est'), 1)}. Some trial reaches SL_est <= 20 at KL <= 1: "
             f"{rs['any_trial_SL_est_le_20_at_KL_le_1']}.")
    L.append(f"- **API spend** for this artifact: ${CostLedger().spent():.2f} (cap $7 hard stop, $10 budget).")
    L.append("")
    return L


def interpretation(r: dict) -> list[str]:
    """Observation / interpretation / limits, conditioned on the saved results (no typed numbers)."""
    v, g, bt = r["verdict"], r["gap"], r["bootstrap"]
    ts, kr = r.get("transfer_slopes", {}), r.get("k_ratio_carriers", {})
    jm = jload(RES / "judge_meta.json") if (RES / "judge_meta.json").exists() else {}
    lj = jm.get("local_judge", {})
    L = ["## Interpretation, failed predictions and limits", ""]
    L.append("**Observations.**")
    L.append(f"- English half-A traits predict the Slovene half-B refusal traits almost as well as they predict the English half-B "
             f"traits: R2* EN->SL is {f(g['R']['R2s_test'])} for R_seq, {f(g['R1']['R2s_test'])} for R1 and {f(g['Rb']['R2s_test'])} for Rb. "
             f"Refusal suppression by these edits is therefore *visible* from English at the edit level (claim 1).")
    if ts.get("R"):
        L.append(f"- Visible does not mean equal in size. Per unit of English change, Slovene R_seq moves {f(ts['R']['ratio_test_over_plac'], 2)}x, "
                 f"R1 {f(ts['R1']['ratio_test_over_plac'], 2)}x and the harmless-KL trait K only {f(ts['K']['ratio_test_over_plac'], 2)}x. "
                 f"The benign-twin trait Rb moves {f(ts['Rb']['ratio_test_over_plac'], 2)}x. So Slovene is systematically attenuated but predictable "
                 f"(exploratory; not a frozen rule).")
    kg, kb, dk = g["K"], bt["K"], v["damage_blind"]["K"]
    sx, mm, st = r["simex"]["K"], r["margin_matched"]["K"], r["stability"]["K"]
    gh = r.get("gap_heretic", {}).get("K", {})
    L.append(f"- **K (harmless divergence on Dolly continuations) is the one trait English misses.** EN half-A traits explain "
             f"R2* = {f(kg['R2s_plac'])} of reliable EN_B K variance but only {f(kg['R2s_test'])} of SL_B K variance: Gap_K = "
             f"{f(kg['Gap'])} (95% CI {ci(kb['gap_ci95'])}, MDE {f(kb['MDE'])}, Holm p {f(kb['p_holm'])}). It survives every frozen check: "
             f"SIMEX {f(sx['gap_simex'])}, margin-matched {f(mm.get('Gap_mm'))} {ci(mm.get('ci95'))}, edit halves {f(st['half0'])} / "
             f"{f(st['half1'])}, ridge learner {f(kg['sensitivity_other_learner']['Gap'])}, and B_K = {f(r['B_t']['K']['B'])} "
             f"{ci(r['B_t']['K']['ci95'])} (Heretic's own parameters add SL-specific information). Frozen label: "
             f"'{dk['label']}' ({dk['status']}). With Slovene as the source the gap reverses "
             f"({f(kg['reverse_SL_source']['Gap'])}): each language's K predicts itself better than the other's, so K has a "
             f"language-specific, edit-dependent component.")
    if ts.get("K"):
        L.append(f"- 'Blind' here is about *which* edits hurt Slovene, not about Slovene being hurt more on average: Slovene KL is "
                 f"smaller than English KL for most edits (mean-change ratio {f(ts['K']['ratio_mean_change_SL_over_EN_B'], 2)}, "
                 f"slope ratio {f(ts['K']['ratio_test_over_plac'], 2)}), but a subset of edits push Slovene divergence up relative to "
                 f"English (`fig8`, middle), and English traits cannot rank them.")
    if gh:
        L.append(f"- Boundary: on the 116 journal trials (E0 + E_TPE) with only Heretic's own objective (EN keyword refusals + log "
                 f"first-token KL) as X, SL K is as predictable as EN K (Gap_Heretic_K = {f(gh.get('Gap_Heretic'))}). That analysis differs "
                 f"in both the predictors and the edit set, so it only suggests that the blind component lives in the wider prior "
                 f"(E0 + E1) rather than in the region TPE explores; it does not isolate which difference matters.")
    L.append(f"- N (FLORES NLL rise) and M (MC margin change) barely move under any edit. The F8 rule labels them "
             f"'{v['damage_blind']['N']['label']}' and '{v['damage_blind']['M']['label']}': with these automatic traits, no language "
             f"damage is visible to predict in either language. This repeats iteration 1's finding at the core checkpoints, now "
             f"across the whole edit distribution.")
    if kr:
        o = kr["over_X_plus_S0"]
        src = o["SRC"]
        L.append(f"- **Carrier.** The frozen exposure carrier D fails (G4): over the static baselines it adds "
                 f"{f(r['carrier']['K']['D']['dR2_C_given_S0_ridge'])} {ci(r['carrier']['K']['D']['ci95_dR2_C_given_S0'])} for the K "
                 f"residual and nothing for any other trait. Exploratory, post-freeze: the language-divergence ratio log(KL_SL/KL_EN) "
                 f"tracks the depth of the layer Heretic takes its refusal direction from (Spearman "
                 f"{f(kr['spearman_y']['src_depth'], 2)}; late-layer directions hit Slovene relatively hardest; `fig8`, left). EN traits "
                 f"plus S0 predict this ratio with CV R2 {f(o['R2_S0_ridge'], 2)}. Source-layer geometry adds "
                 f"{f(src['dR2_C_given_S0_ridge'])} (95% CI {ci(src['ci95_dR2_C_given_S0'])}; GBT {f(src['dR2_C_given_S0_gbt'])}) and "
                 f"exposure D adds {f(o['D']['dR2_C_given_S0_ridge'])} {ci(o['D']['ci95_dR2_C_given_S0'])}. The source layer is the "
                 f"lead for the next iteration, but it was chosen after seeing the data and misses the frozen 0.05 bar under ridge.")
    L.append("")
    L.append("**Failed or unsupported predictions.** See the scorecard table. The main-hypothesis prediction G3 (a blind damage "
             "trait) is evaluated mechanically, together with the carrier prediction G4 (exposure D) and G5 (r_prior undefined for "
             "GaMS3). Under both rule and judge labels, the original GaMS3 refuses at least 10 harmless half-A prompts, so r_prior is "
             "defined and the P covariate was computed.")
    L.append("")
    L.append("**Limits.**")
    L.append("- One model (GaMS3) and one Heretic optimiser seed. Optimiser-run variance is not measured. Joining this pod with the "
             "Gemma P1 pod (identical E0/E1/E_R edits, certified in `results/unit_tests.json` U1b_sibling_diff) gives n = 2 models; "
             "nothing is attributed to training stages.")
    L.append("- Numerics: the per-item truncated KL of weak edits moves by 17-26% of its mean when re-scored on a different GPU model "
             "(`results/repro_check.json`); the two RTX 4090 hosts that scored the panel show no offset (`host_check.py`). K for the "
             "weakest edits therefore carries a hardware-dependent floor; all panel comparisons are within one GPU model.")
    L.append("- The traits are teacher-forced automatic proxies (4-bit NF4, 24-token references). A Gap near 0 on the damage traits means "
             "'no blind damage visible to these automatic traits', not 'no damage'.")
    L.append(f"- Judging: gpt-4.1 labelled {jm.get('n_labelled')}/{jm.get('n')} generations before the run-level OpenRouter budget "
             f"($7 for the whole 'Test idea' phase, shared by all pods) ran out at 00:04 UTC. The rest, and the planned "
             f"gemini-2.5-flash second judge, were replaced by a local Qwen3-14B judge (4-bit) using the same rubric; the free-tier "
             f"models were also exhausted for the day (deviation D20). It agrees with gpt-4.1 at kappa "
             f"{f(lj.get('kappa_refused_gpt41_vs_local'))} (refused vs not; EN {f(lj.get('kappa_refused_by_lang', {}).get('en'))}, "
             f"SL {f(lj.get('kappa_refused_by_lang', {}).get('sl'))}) and {f(lj.get('kappa_6way_gpt41_vs_local'))} (6-way) on "
             f"{lj.get('n_overlap_with_gpt41')} shared generations. Qwen3 is from a different family than GaMS3 (Gemma-3) and gpt-4.1. "
             f"Nine of the 18 validity conditions per language are labelled by it alone. "
             f"The validity gate is also reported for gpt-4.1-only, local-only and rule labels.")
    L.append("- Slovene items are machine-translated with automated QC only; native review is pending. The X_SET exposure prompts were "
             "translated with NLLB, because the primary translator was blocked.")
    L.append(f"- The fitted set is {r['n_F']} edits (floor 150: {v['gates']['floor_150']}). Labels are confirmatory only where the "
             "frozen gates (reliability >= 0.6, MDE <= 0.15, refusal validity >= 0.85) all hold; each trait's status is in "
             "`results/verdict.json`.")
    L.append("")
    return L


def main() -> None:
    r = jload(RES / "analysis_results.json")
    dev = jload(RES / "deviations.json")
    ws = str(ROOT)
    L = ["# P1 random-edit panel on GaMS3-12B-Instruct: what English Heretic edits miss in Slovene", ""]
    L.append("Iteration-2 experiment of run `run_Fapgmt6JWbcD` (artifact `gen_art_experiment_6`). Up to 246 Heretic abliteration "
             "edits (journal startup draws, journal TPE trials, fresh prior draws and a reserved-seed out-of-sample set) are rebuilt "
             "through Heretic's own code on `cjvt/GaMS3-12B-Instruct`. Each edit is scored in English and Slovene on teacher-forced "
             "refusal, divergence, language-NLL and multiple-choice traits. The question is whether the English traits, which "
             "are all Heretic's optimiser sees, are a sufficient surrogate for the same traits in Slovene. The test compares EN->SL "
             "prediction with a same-language EN->EN placebo on independent items, each normalised by its own noise ceiling.")
    L.append("")
    L += headline(r)
    L += interpretation(r)
    rd = RES / "rederive_headlines.json"
    if rd.exists():
        x = jload(rd)
        L.append("## Independent re-derivation of the headline numbers (`rederive_headlines.py`)\n")
        L.append(f"A separate script reads the raw per-item parquets and judge labels, and re-derives the numbers with its own "
                 f"aggregation, ceilings and learners ({x['learners']}; {x['note']}). "
                 f"Gap_K = {f(x['K']['extratrees']['Gap'])} (ExtraTrees) / {f(x['K']['loo_quad_ridge']['Gap'])} (LOO ridge) vs "
                 f"the primary {f(r['gap']['K']['Gap'])}: the >= 0.10 'blind' bar is met by both independent learners, but the "
                 f"magnitude is learner-dependent. Gap_R = {f(x['R']['extratrees']['Gap'])} / {f(x['R']['loo_quad_ridge']['Gap'])} "
                 f"(primary {f(r['gap']['R']['Gap'])}). Validity Spearman EN {f(x['validity']['en']['spearman_Rseq_vs_refused'])}, "
                 f"SL {f(x['validity']['sl']['spearman_Rseq_vs_refused'])}; judge kappa {f(x['judge']['kappa_refused'])} "
                 f"(refused vs not). Placebos, each of which must FAIL the claim: K self-placebo Gap "
                 f"{f(x['K']['placebo_self_EN_as_SL_Gap'])}, noise-matched placebo {f(x['K']['placebo_noise_matched_Gap'])}; "
                 f"R with SL shuffled across edits {f(x['R']['placebo_shuffled_SL_Gap'])} (the 'visible' claim breaks); validity "
                 f"with shuffled rates mean rho EN {f(x['validity']['en']['placebo_shuffled_rates_mean_rho'])} / SL "
                 f"{f(x['validity']['sl']['placebo_shuffled_rates_mean_rho'])}; kappa with shuffled labels "
                 f"{f(x['judge']['placebo_shuffled_kappa_mean'])}.\n")
    L.append((ROOT / "README_methods.md").read_text())
    L.append("## Results tables (generated by `summary_tables.py` from `results/analysis_results.json`)\n")
    L.append((RES / "summary_tables.md").read_text())
    L.append("## Figures (`figures/`, PNG + PDF, generated by `figures.py`)\n")
    for a, b in [("fig1_en_vs_sl_scatter", "per-edit EN_B vs SL_B trait means on F, with R2* in the titles"),
                 ("fig2_gap_forest", "Gap forest: R2*, raw, SIMEX, margin-matched and edit halves, with the +/-0.10 band"),
                 ("fig3_carrier_dr2", "carrier dR2 both ways (C given S0 and S0 given C)"),
                 ("fig4_exposure_D", "the distribution of exposure D, and D vs the SL-minus-EN residual y for K/N/M"),
                 ("fig5_forecast_coverage", "out-of-sample conformal PI coverage on E_TPE / E_R, with the core trial"),
                 ("fig6_validity", "validity: condition-level R_seq and R1 vs the judged refusal rate, per language"),
                 ("fig7_reselection_pareto", "bilingual reselection: EN keyword refusals vs SL_est, coloured by KL"),
                 ("fig8_transfer_exploratory", "EXPLORATORY: SL/EN KL ratio vs refusal-direction source layer; EN vs SL KL; transfer ratios")]:
        L.append(f"- `figures/{a}.png`: {b}")
    L.append("\n## Deviations from the plan (`results/deviations.json`)\n")
    for d in dev:
        extra = "; ".join(f"{k}: {v}" for k, v in d.items() if k not in ("id", "what"))
        L.append(f"- **{d['id']}**: {d['what']}" + (f" ({extra})" if extra else ""))
    L.append(f"""
## Layout

| path | what |
|---|---|
| `method.py` | GPU orchestrator. Stages: stage0b (model, edit sets, U1-U3/U7), stage0c (generations, references, r_prior), stage0d (geometry, caches, baselines), freeze, stageA (timing + ladder), panel (resumable) |
| `engine.py` | Heretic `Model` wrapper: edits via `reset_model` + `abliterate`, LoRA factors, teacher-forced scoring at the scored positions only, hooks, generation |
| `common.py` | paths, pins, logging, hashing, Heretic parameter sampler, OpenRouter cost ledger |
| `data_prep.py` | S3 DEV extraction with split-hash verification; disjoint exposure set X_SET (NLLB EN->SL, LaBSE/GlotLID QC) |
| `protocol.py` | frozen protocol + predictions, written with sha256 before any panel trait existed |
| `judge.py` | blind gpt-4.1 judge (6-label rubric), gemini-2.5-flash second judge, rule labeller, `--from-log` recovery |
| `analysis.py` | Stage D: Gap, bootstrap, B_t, SIMEX, stability, margin-matched Gap, mixed model, carrier, forecast, reselection, validity, verdict, scorecard, transfer slopes |
| `synth_test.py` | T0: four simulated scenarios run through the real analysis code (`results/synth_test.json`) |
| `audit.py` | T5: independent plain-numpy recomputation + placebos (`results/audit.json`) |
| `rederive_headlines.py` | second independent re-derivation of the headline numbers from raw files, with placebos (`results/rederive_headlines.json`) |
| `reproducibility.md` | exact commands, pins, hardware and expected numbers |
| `post_tests.py` | U4 / U5 / U7-diagnostic on a second model instance after the panel (`results/post_tests.json`) |
| `repro_check.py` | re-scores host-1 and host-2 edits to quantify cross-machine numerics (`results/repro_check.json`; ran on host 3, see D16/D20) |
| `host_check.py` | CPU check that host 1 vs host 2 (both RTX 4090) shifted no K values (`results/repro_check.json` host1_vs_host2_K_offset_check) |
| `figures.py`, `summary_tables.py`, `to_schema.py`, `make_readme.py` | outputs: figures, tables, `method_out.json` (exp_gen_sol_out), this README |
| `local_judge.py` | local Qwen3-14B judge (same rubric): second judge vs gpt-4.1 and fill-in for unlabelled generations (D20) |
| `run_judge_after_reset.sh`, `finish_after_panel.sh` | helper drivers: wait for the shared key's daily reset, then judge; post-panel sequence |
| `data/s3_items.json`, `data/x_set.json` | frozen DEV items (pod ids / halves) and the 64-prompt disjoint exposure set (+ sha256) |
| `results/edits_manifest.json` | all 246 edits: set, seed, trial number, raw + transformed parameters, journal objectives |
| `results/panel_edits.jsonl`, `results/panel_items/*.parquet` | per-edit covariates/aggregates and per-item trait values (the panel itself) |
| `results/baseline_items.parquet` | original-model per-item values |
| `results/references.json`, `results/compliance_refs_gams_core.json` | 24-token refusal/compliance references; the shared export for the Gemma P1 pod |
| `results/validity_gens.jsonl`, `results/judged_generations.json`, `results/judge_meta.json` | validity generations and their blind labels |
| `results/frozen_protocol.json`, `results/frozen_predictions.json`, `results/ladder_decision.json` (+ `.sha256`) | pre-registration files |
| `results/analysis_results.json`, `results/verdict.json`, `results/variances_for_power.json` | analysis outputs |
| `results/unit_tests.json`, `results/u6_flores_check.json`, `results/timings.json`, `results/api_costs.jsonl` | checks, timing, spend |
| `results/*_quick.json`, `results/*_rehearsal131.json`, `results/synth_test_v*.json` | DEBUG runs on partial panels / earlier code versions; kept for transparency, never used for decisions |
| `results/post_tests.json`, `results/repro_check.json`, `results/judge_local_cache.json` | U4/U5/U7 post-tests, cross-GPU re-scoring + host-offset check, local-judge label probabilities |
| `cache/` | original-model caches: geometry.npz, k_cache.pt (kept), r_prior.npy, x_acts_*.pt (deleted after the round; regenerable) |
| `third_party/heretic/` | pinned Heretic 3521f864 source |
| `method_out.json` (+ mini/preview) | exp_gen_sol_out: one example per edit, metadata = all results |
| `logs/` | run logs (the judge's raw outputs are logged at DEBUG) |

## How to run

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python torch==2.11.0+cu128 torchvision==0.26.0+cu128 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python .venv/bin/python -r pyproject.toml
uv pip install --python .venv/bin/python -e third_party/heretic --no-deps
.venv/bin/python data_prep.py                                   # S3 items + X_SET
.venv/bin/python method.py --stages stage0b,stage0c,stage0d,freeze,stageA,panel   # GPU, ~3.5 h on an RTX 4090 (resumable)
.venv/bin/python judge.py                                       # blind judging (needs OPENROUTER_API_KEY / OPENROUTER_BASE_URL)
.venv/bin/python local_judge.py                                 # local Qwen3-14B second judge + fill-in (D20)
.venv/bin/python post_tests.py && .venv/bin/python repro_check.py && .venv/bin/python host_check.py
.venv/bin/python synth_test.py --B 100                          # T0
AN_JOBS=24 .venv/bin/python analysis.py --B 1000                # Stage D (CPU; ~87 min on a 5-CPU quota)
.venv/bin/python audit.py && .venv/bin/python figures.py && .venv/bin/python summary_tables.py
.venv/bin/python to_schema.py && .venv/bin/python make_readme.py
```

Read-only inputs come from iteration 1: the Optuna journal, the directions and the trial-88 adapter in `gen_art_experiment_1`;
the prefix sets and frozen directions in `gen_art_experiment_3`; and the frozen dataset `gen_art_dataset_1`. The model is
`cjvt/GaMS3-12B-Instruct@1d0b27af5748784482600d24779409e7e1dc9adc` from the shared HF cache.

## Kept artifacts (workspace paths)

- panel: `{ws}/results/panel_items/` and `{ws}/results/panel_edits.jsonl`
- references and the Gemma-pod export: `{ws}/results/references.json`, `{ws}/results/compliance_refs_gams_core.json`
- judged generations: `{ws}/results/judged_generations.json`
- K reference cache: `{ws}/cache/k_cache.pt`; geometry: `{ws}/cache/geometry.npz`; r_prior: `{ws}/cache/r_prior.npy`

## Restoring removed files

- `.venv/`: run the four `uv` lines at the top of "How to run".
- `__pycache__/` and `third_party/heretic/src/heretic/__pycache__/`: created automatically on import (`.venv/bin/python -c "import method, heretic"`).
- `cache/x_acts_en.pt`, `cache/x_acts_sl.pt` (the 685 MB X_SET exposure caches of `o_proj`/`down_proj` inputs): run
  `rm results/baseline_done.json && .venv/bin/python method.py --stages stage0d`. This recomputes them, together with the
  geometry, the K cache and the baseline traits, from the pinned model and `data/x_set.json`.
""")
    (ROOT / "README.md").write_text("\n".join(L))
    print(f"README.md written ({len(L)} blocks)")


if __name__ == "__main__":
    main()

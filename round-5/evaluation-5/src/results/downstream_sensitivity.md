# Downstream sensitivity (leg C)

Design: Yoon et al. 2026, *Who Pays More for Safety? Measuring the Disparate Cost of Safety Alignment across Languages* (arXiv 2608.22490), Sec. 3: "we instantiate Munalg using a safety-ablated (abliterated) version of the models" (verified quote, neighbour_table.json N20, accessed 2026-09-24).

Functional form: ASSUMPTION (not established by the verified material): SafetyCost_L = O(M_aligned, L) - O(M_unaligned, L), with O measured in refusal-rate units and M_unaligned the ablated checkpoint. If the ablated counterfactual is VERIFIED with an English keyword score, its per-language state error is d_L = p_kw,L - p_ref,L, and a cross-language cost difference (SL minus EN) shifts by Delta_lang = d_SL - d_EN (unit cost per refusal-rate point = 1).

**Scope caveat:** SENSITIVITY ANALYSIS ONLY: one model pair (gemma-3-12b-it, GaMS3-12B-Instruct) + one outside-family community edit; NF4 throughout; one optimiser seed per search; machine-translated Slovene, native review PENDING; two languages in the paired panels; counterfactual produced by Heretic, not by the cited design's tool; cost functional form is an ASSUMPTION. NOT a re-estimate of any published number and NOT a claim that any published ranking is wrong.

| checkpoint | pair set | n pairs | Delta_lang by channel | cost-shift range (Delta_lang) | residual gap SL-EN (reference) | rank inversion possible |
|---|---|---|---|---|---|---|
| exp11:B_keyword_t96 | S4hoc | 70 | qwen:-1.114 [-1.286,-0.943]; polyguard:-0.914 [-1.071,-0.757] | [-1.286, -0.757] | [+0.100, +0.529] | True |
| exp11:B_keyword_t96 | S5X | 100 | qwen:-1.600 [-1.700,-1.500]; polyguard:-1.550 [-1.660,-1.430] | [-1.700, -1.430] | [+0.530, +0.770] | True |
| exp11:C_corrected | S4hoc | 70 | qwen:-0.929 [-1.129,-0.729]; polyguard:-0.743 [-0.914,-0.571] | [-1.129, -0.571] | [+0.086, +0.529] | True |
| exp11:C_corrected | S5X | 100 | qwen:-1.180 [-1.290,-1.060]; polyguard:-1.360 [-1.490,-1.230] | [-1.490, -1.060] | [+0.290, +0.660] | True |
| exp11:D2_reselected_judge | S4hoc | 70 | qwen:-0.971 [-1.129,-0.814]; polyguard:-0.743 [-0.929,-0.557] | [-1.129, -0.557] | [+0.100, +0.586] | True |
| exp11:D2_reselected_judge | S5X | 100 | qwen:-1.200 [-1.330,-1.080]; polyguard:-1.390 [-1.520,-1.250] | [-1.520, -1.080] | [+0.310, +0.700] | True |
| exp11:D_reselected_clf | S4hoc | 70 | qwen:-1.100 [-1.271,-0.914]; polyguard:-1.000 [-1.157,-0.829] | [-1.271, -0.829] | [+0.157, +0.529] | True |
| exp11:D_reselected_clf | S5X | 100 | qwen:-1.210 [-1.320,-1.100]; polyguard:-1.450 [-1.550,-1.340] | [-1.550, -1.100] | [+0.210, +0.630] | True |
| exp11:F_dose1.5 | S4hoc | 70 | qwen:-0.686 [-0.871,-0.500]; polyguard:-0.700 [-0.900,-0.500] | [-0.900, -0.500] | [+0.157, +0.429] | True |
| exp11:F_dose1.5 | S5X | 100 | qwen:-1.050 [-1.180,-0.920]; polyguard:-1.200 [-1.330,-1.070] | [-1.330, -0.920] | [+0.240, +0.590] | True |
| exp11:F_dose2.0 | S4hoc | 70 | qwen:-0.214 [-0.343,-0.100]; polyguard:-0.371 [-0.514,-0.214] | [-0.514, -0.100] | [-0.114, +0.229] | False |
| exp11:F_dose2.0 | S5X | 100 | qwen:-0.340 [-0.430,-0.250]; polyguard:-0.640 [-0.780,-0.500] | [-0.780, -0.250] | [+0.000, +0.390] | True |
| exp11:F_dose3.0 | S4hoc | 70 | qwen:-0.257 [-0.357,-0.157]; polyguard:-0.471 [-0.614,-0.329] | [-0.614, -0.157] | [+0.000, +0.329] | True |
| exp11:F_dose3.0 | S5X | 100 | qwen:-0.210 [-0.290,-0.140]; polyguard:-0.580 [-0.700,-0.470] | [-0.700, -0.140] | [+0.000, +0.470] | True |
| exp4:community_ref | S5X | 100 | qwen:-0.200 [-0.280,-0.120]; polyguard:-0.310 [-0.430,-0.190] | [-0.430, -0.120] | [+0.050, +0.340] | True |
| exp4:gams_edit | S5X | 100 | qwen:-0.180 [-0.260,-0.110]; polyguard:-0.470 [-0.590,-0.350] | [-0.590, -0.110] | [-0.050, +0.370] | True |
| exp4:gemma_edit | S5X | 100 | qwen:-1.560 [-1.680,-1.440]; polyguard:-1.490 [-1.610,-1.360] | [-1.680, -1.360] | [+0.520, +0.780] | True |

What this leg cannot do: This leg cannot say what the correct per-language counterfactual is: that would require re-selecting a counterfactual per language, which this artifact does not do and does not plan.

Lineage: Marchisio et al. 2024 (https://arxiv.org/pdf/2407.03211), abstract: "a 1.7% average drop in Japanese across automatic tasks corresponds to a 16.0% drop reported by human evaluators on realistic prompts".

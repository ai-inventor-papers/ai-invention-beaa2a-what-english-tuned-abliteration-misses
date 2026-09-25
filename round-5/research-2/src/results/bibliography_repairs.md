# Bibliography repairs (target D)

Accessed 2026-09-24. Every entry was resolved from the primary abs page or the ACL Anthology page this session;
the raw fetches are under `results/raw/`. `results/bibliography_repairs.csv` holds the same table in machine form.

| draft ref | what the draft says | what is correct | evidence | locator | flag |
|---|---|---|---|---|---|
| [19] | Li, S., Yao, L., Zhang, L., and Li, Y. (2024). Safety Layers in Aligned Large Language Models: The Key to LLM Security. ICLR 2024. (no arXiv id; wrong year; wrong venue year) | Li, Shen; Yao, Liuyi; Zhang, Lan; Li, Yaliang. Safety Layers in Aligned Large Language Models: The Key to LLM Security. ICLR 2025. arXiv:2408.17003 (v1 30 Aug 2024; v5 7 Apr 2025). arXiv comment field states 'Accepted by ICLR 2025'. NOTE: the v1 title reads 'Safety Layers OF Aligned Large Language Models'; cite the published 'IN'. | https://arxiv.org/abs/2408.17003 | abs page: title, author list, Comments field ('Accepted by ICLR 2025'); v1 title from https://arxiv.org/abs/2408.17003v1 | VERIFIED-QUOTE |
| [20] | Bosco, P. C. and Srinivasan, G. (2026). Locating and Steering Refusal Beyond Attention. 2026. (no arXiv id, no venue) | Bosco, Preethi Carmel; Srinivasan, Gopalakrishnan. Locating and Steering Refusal Beyond Attention. arXiv:2609.04721 (v1, 4 Sep 2026). cs.LG. No venue stated on the abs page - cite as a preprint. | https://arxiv.org/abs/2609.04721 | abs page: title, authors, submission date; quoted content at App. A.6 of https://arxiv.org/html/2609.04721v1 | VERIFIED-QUOTE |
| [21] | Jiang, Y. (2026). Refit the Probe: Single-Direction Ablation Is Not a Necessity Test. 2026. (no arXiv id, no venue) | Jiang, Yuhang. Refit the Probe: Single-Direction Ablation Is Not a Necessity Test. arXiv:2606.00926 (v1 30 May 2026; v2 21 Sep 2026). cs.LG. Single author. No venue stated - cite as a preprint, and cite v2 since the quote was re-verified there. | https://arxiv.org/abs/2606.00926 | abs page: title, author, versions; quote re-verified in https://arxiv.org/html/2606.00926v2 (discussion section) | VERIFIED-QUOTE |
| [13] and the motivation's pruning citation | 'Marchisio et al. [12] and Chimoto et al. [13] show that quantisation calibration language matters'; the hypothesis text additionally cites 'Kurz et al., TACL, 2408.14398' in support of 'the calibration language matters' | Kurz, Simon; Chen, Jian-Jia; Flek, Lucie; Zhao, Zhixue. On the Limitations of Language-targeted Pruning: Investigating the Calibration Language Impact in Multilingual LLM Pruning. TACL vol. 14 (2026), pp. 167-192, ACL Anthology 2026.tacl-1.9, DOI 10.1162/tacl.a.599; arXiv:2408.14398 v4. DIRECTION CORRECTION: the paper's finding is that target-language calibration retains perplexity but 'does not consistently improve downstream task performance' - it is a LIMITATIONS paper, not support for 'the calibration language matters'. | https://aclanthology.org/2026.tacl-1.9/ | anthology page: title, authors, Volume 14, Pages 167-192, DOI, Year 2026; finding quoted from the arXiv v4 abstract | VERIFIED-QUOTE |
| [22] placement in the text | 'positions ... against AdvPrefix (arXiv 2412.10321) [22] (selection blindness)' is attached in the draft's positioning-of-the-negative paragraph to the DEPTH result | Zhu, Sicheng; Amos, Brandon; Tian, Yuandong; Guo, Chuan; Evtimov, Ivan. AdvPrefix: An Objective for Nuanced LLM Jailbreaks. arXiv:2412.10321 (v2, 27 Dec 2025). The reference itself is correct; its PLACEMENT is not. AdvPrefix is the neighbour for the SELECTION-BLINDNESS companion only. | https://arxiv.org/abs/2412.10321 | abs page: title, authors, versions; misspecification quote at Sec. 1 of the PDF | VERIFIED-QUOTE |
| [14] | Young, R. (2025). Comparative Analysis of LLM Abliteration Methods: A Cross-Architecture Evaluation. arXiv:2512.13655. | Young, Richard J. (single author). Same title. arXiv:2512.13655 (v1 15 Dec 2025; v2 8 Jan 2026), 25 pages. Correct as cited; add the full author name and the v2 date if the marker-heuristic caveat is quoted. | https://arxiv.org/abs/2512.13655 | abs page: title, author, versions, Comments | VERIFIED-QUOTE |
| [8] | Fafula, A. (2026). Abliteration Is Not a Scalpel ... arXiv:2607.17427. | Fafula, Aleksander. Abliteration Is Not a Scalpel: Off-Target Effects of Refusal Removal on Decision Disposition Across Model Families. arXiv:2607.17427 (19 Jul 2026), preregistered; dataset DOI 10.5281/zenodo.21314839. Correct as cited. | https://arxiv.org/abs/2607.17427 | abs page: title, author, Comments field | VERIFIED-QUOTE |
| [5] | Yoon, C., Park, J., and Ritter, A. (2026). Who Pays More for Safety? ... EMNLP 2026. arXiv:2608.22490. | Correct as cited. Confirmed: arXiv comment field 'Accepted to EMNLP 2026 Main Conference'; authors Chanwoong Yoon (Korea University), Jungsoo Park, Alan Ritter (Georgia Tech). | https://arxiv.org/abs/2608.22490 | abs page: authors, Comments field | VERIFIED-QUOTE |
| new (measurement neighbours, currently absent from the draft) | the measurement/selection-blindness result cites no evaluator-measurement or multilingual-judge work | ADD: arXiv 2510.02768 (Agnihotri et al., NeurIPS 2025 Workshop Lock-LLM; regex over-counts refusals on abliterated models); arXiv 2603.06594 (Schwinn et al.; judges degrade to near chance under red-teaming distribution shift); arXiv 2607.02235 (Dogruoz et al., EMNLP Findings 2026; judge reliability is language-conditional); arXiv 2505.19056 (Abu Shairah et al.; judge and Llama-Guard-3-8B reported side by side on abliterated checkpoints); arXiv 2605.17173 (Zhang et al., COLM 2026; CONTRADICTING - per-language validated judge reaches kappa 0.80-0.83) | https://arxiv.org/abs/2510.02768 | results/neighbour_table_measurement.md rows M3, M9, M16, M10, M18 | VERIFIED-QUOTE |

## BibTeX-ready field sets for the three repaired entries

```bibtex
@inproceedings{Li2025SafetyLayers,
  author    = {Shen Li and Liuyi Yao and Lan Zhang and Yaliang Li},
  title     = {Safety Layers in Aligned Large Language Models: The Key to {LLM} Security},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2025},
  note      = {arXiv:2408.17003},
  url       = {https://arxiv.org/abs/2408.17003}
}

@misc{Bosco2026Locating,
  author = {Preethi Carmel Bosco and Gopalakrishnan Srinivasan},
  title  = {Locating and Steering Refusal Beyond Attention},
  year   = {2026},
  note   = {arXiv:2609.04721},
  url    = {https://arxiv.org/abs/2609.04721}
}

@misc{Jiang2026RefitProbe,
  author = {Yuhang Jiang},
  title  = {Refit the Probe: Single-Direction Ablation Is Not a Necessity Test},
  year   = {2026},
  note   = {arXiv:2606.00926v2},
  url    = {https://arxiv.org/abs/2606.00926}
}

@article{Kurz2026Limitations,
  author  = {Simon Kurz and Jian-Jia Chen and Lucie Flek and Zhixue Zhao},
  title   = {On the Limitations of Language-targeted Pruning: Investigating the Calibration Language Impact in Multilingual {LLM} Pruning},
  journal = {Transactions of the Association for Computational Linguistics},
  volume  = {14},
  pages   = {167--192},
  year    = {2026},
  doi     = {10.1162/tacl.a.599},
  url     = {https://aclanthology.org/2026.tacl-1.9/}
}
```

## The four defects the reviewer listed, and their status

1. **Wrong venue year for the safety-layers reference** — the draft's `[19]` says ICLR 2024; the arXiv Comments
   field says *Accepted by ICLR 2025*. FIXED above [OBSERVATION].
2. **Missing arXiv id for the safety-layers reference** — it is `2408.17003`. FIXED [OBSERVATION].
3. **Two missing arXiv ids** — `[20]` = `2609.04721`, `[21]` = `2606.00926`. FIXED [OBSERVATION].
4. **A fifth defect found this session, not on the reviewer's list**: the pruning-calibration citation is used in
   the run's motivation for a claim whose direction the cited paper does not support. The published title is
   *On the Limitations of Language-targeted Pruning*, and the finding is that target-language calibration
   retains perplexity but "does not consistently improve downstream task performance". Any sentence that cites
   it for "the calibration language matters" must be rewritten or the citation dropped [OBSERVATION].

**One further correction, to the draft's TEXT rather than its bibliography (OBSERVATION).** The draft's
positioning-of-the-negative paragraph attaches AdvPrefix (`[22]`, arXiv 2412.10321) to the depth result.
AdvPrefix is the neighbour for the selection-blindness companion only. `results/positioning_negative_v2.md`
carries the corrected wording.

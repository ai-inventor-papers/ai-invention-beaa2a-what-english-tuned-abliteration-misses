# What English-Tuned Abliteration Misses in Slovene

Compiled LaTeX paper evaluating cross-lingual transfer of English-tuned abliteration to Slovene.

## Layout

| Path | Description |
|---|---|
| `paper.tex` | LaTeX source |
| `paper.pdf` | Compiled PDF (11 pages) |
| `references.bib` | BibTeX bibliography (16 entries via Semantic Scholar) |
| `references.json` | Fetch record for each bibliography entry |
| `figures/fig_1_v0.pdf` | Refusal rates across checkpoints and languages |
| `figures/fig_2_v0.pdf` | Keyword counter vs. reference judge positive rates |
| `figures/fig_3_v0.pdf` | Depth placement profile for GaMS3 |

## How to compile

```bash
pdflatex -interaction=nonstopmode paper.tex
bibtex paper
pdflatex -interaction=nonstopmode paper.tex
pdflatex -interaction=nonstopmode paper.tex
```

## Restoring removed files

No files were marked for deletion; all outputs are under 10 MB.

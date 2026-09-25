# An English Keyword Objective Is Blind to Its Own Edit in Slovene

Paper folder for this run, published as a static site.

## Layout

- `paper.tex`, `paper.pdf`, `references.bib`, `references.json`: the paper and its bibliography.
- `figures/`: the figures the paper uses (PDF, PNG and their JSON specs).
- `index.html`: the paper's static presentation page (landing page). It links to `interactive.html`.
- `interactive.html`: a self-contained explorable page. All CSS, JavaScript and data are inline; it needs no network. Each embedded `<script type="application/json">` block names the run artifact file it was extracted from in its `data-source` attribute, and the page footer lists them per view.
- `workspace/`: scratch folder of the LaTeX assembly step.

## How to view

Open `index.html` or `interactive.html` in any modern browser.

## Restoring removed files

Nothing in this folder is marked for deletion (`.aii/manifest.yaml` has no entries), so there is nothing to restore.

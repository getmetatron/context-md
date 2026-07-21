# Context Inheritance (paper draft)

**Status:** unpublished draft. Venue and submission date **not yet decided.**
Do not submit or post without an explicit decision.

**Title:** Context Inheritance: Capability-Dependent Benefits of Repository
Context for AI Coding Agents

**Authors:** Pavel Kerbel, Milana Kerbel, Vitali Abramov, Liat Abramov
(Metatron Research).

## Thesis
Benefit from a repository context layer is *capability-dependent*: it accrues to
a reader in proportion to how far its context's **author** outranks it, and only
while the reader is below its ceiling. Synthesizes the whole experiment program
under one principle ("context inheritance").

## What it reuses (all grounded in RESULTS-*.md)
- Capability gradient (weak executor): RESULTS-04 pooled — +26.1pp / +0.0pp.
- What-transfers inversion + frontier resolve: RESULTS-03, RESULTS-05.
- Frontier ceiling (broad 88-instance delivery matrix): `runs/opus_ext/` +
  `eval_opus_ext.py` — B 90.9 / E 81.8 / FILE 85.2 / SHARD 88.6.
- Token economics: RESULTS-05 (−32% tokens/resolved).
- Delivery "selection beats volume": RESULTS-06.

## Figures
- `figures/fig1-gradient.png` — capability gradient (from Paper 1 fig3).
- `figures/fig2-tokens.png` — tokens/resolved at frontier (from Paper 1 fig4).

## Relationship to the other papers
- **Companion to** the RCL architecture paper (`../agenticdev2026/`,
  `../preprints-org/`), which specifies the pattern; this paper is the empirical
  capability-inheritance deep-dive and cites it as `\cite{rcl}`.
- **Scope guard:** validates the pattern + delivery + author-capability, NOT
  Metatron's automatic extraction (blind/lifecycle seeds only). See the Threats
  section and ROADMAP "Paper 4" note.

## Build
`tectonic main.tex` → `main.pdf` (no line numbers; venue-neutral acmart nonacm).

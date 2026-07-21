# Context Inheritance — combined full paper (draft)

**Status:** unpublished draft. Venue/date **not yet decided.** A candidate to
Replace the AgenticDev submission before the Jul 25 deadline, OR to target a
larger venue. Do not submit without an explicit decision.

**Title:** Context Inheritance: A Git-Native Architecture and Pre-Registered
Study of Repository Context for AI Coding Agents

**Authors:** Pavel Kerbel, Milana Kerbel, Vitali Abramov, Liat Abramov
(Metatron Research).

## What this is
The **full reframe + retitle** version requested 2026-07-21: a single standalone
paper combining the RCL architecture with the full empirical study, organized
around **context inheritance** (capability-dependence) as the thesis. Built as a
NEW, separate paper — the two existing drafts are left untouched:
- `../agenticdev2026/` + `../preprints-org/` — the RCL architecture short paper
  (in review at AgenticDev). UNCHANGED.
- `../context-inheritance/` — the short empirical-only draft. UNCHANGED.

## Structure (6 pp, 10-page limit)
Architecture (compressed: RCL, lifecycle, discovery+format, design, threat model,
reference impl) → Empirical evaluation organized as the inheritance arc:
1. Inheritance requires a more capable author (gradient, +26/+0 pp)
2. At the frontier, what is inherited inverts (failure vs answers, +14.6 pp)
3. Delivery shapes inheritance (selection beats volume — Table 2, Paper 2 data)
4. Inheritance has a ceiling (broad frontier sample — Fig 4, NEW Opus data)
5. Where it pays, it is self-financing (−32% tokens)

Frontier-ceiling null is included, framed as a scope finding (per decision).

## Figures
- `fig1-architecture.png`, `fig2-slopegraph.png`, `fig3-gradient.png`,
  `fig4-tokens.png` — reused from the architecture paper (same authors; this
  paper supersedes/extends it, so reuse is not duplicate publication as long as
  only one of them is published).
- `fig5-ceiling.png` — NEW (broad-sample frontier ceiling).

## Scope guard (must not be blurred)
Validates the RCL **pattern + delivery + author-capability**, NOT Metatron's
automatic extraction (all seeds are blind-/lifecycle-authored). Threats §
states this; ROADMAP "Paper 4" is the extraction follow-up.

## Build
`tectonic main.tex` → `main.pdf` (venue-neutral acmart nonacm, no line numbers).
Add `review` to the documentclass options for a line-numbered review build.

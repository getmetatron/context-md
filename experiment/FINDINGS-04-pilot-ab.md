# Findings 04 — Pilot A/B: Gemma 4 with vs. without a context layer

**Date:** 2026-07-09. Pilot-grade (pre-reg not frozen; context authored non-blind by the frontier assistant after seeing pilot logs). Directional only — excluded from confirmatory analysis.

**Setup:** identical harness both arms (incl. empty-submit guard); 10 easy instances (6 sphinx, 4 django); treatment = repo `context.md` (pilot/context/*.md) injected into system prompt; temp 0, 1 rep.

## Results

| Metric | Control | Treatment |
|---|---|---|
| Gold-file hits | 2/10 | **4/10** |
| — sphinx | 1/6 | **4/6** |
| — django | 1/4 | **0/4** ⚠ |
| Non-empty patches | 7/10 | 8/10 |
| Avg turns | 10.8 | 10.4 |
| Avg tokens | 38.7K | 48.2K (+24%) |
| Avg wall | 57s | 84s |

## The finding: context is a steering wheel, not a hint
- **Sphinx context was precise** ("rendering/xref bugs → `domains/python.py`; collection → `ext/autodoc/typehints.py`") → model followed it to the gold file in 4/6 (7462, 9591, 10449, 8459).
- **Django context was imprecise** and the model followed it *faithfully into the wrong files*:
  - 15499: control found gold (`operations/models.py`) unaided; context mentioned `optimizer.py` first → treatment edited `optimizer.py`. Regression caused by entry wording.
  - 14580: entry said "writer.py or serializer.py"; model picked `writer.py`; gold is `serializer.py`. Ambiguity resolved wrong.
- An 8B executor treats the context layer as ground truth. **Accurate entries produce large gains; fuzzy or subtly wrong entries actively mislead** — stronger than the no-context baseline in both directions.

## Implications
1. **Dose-response, not just efficacy** — supports the paper's P5 (review-gating) empirically: context quality is load-bearing; a context layer is high-leverage in both directions, which is exactly why writes must be gated.
2. Predicts the E-vs-F matrix contrast (frontier-authored vs self-authored seeds) will be informative.
3. **Confirmatory-design consequence:** seed authoring quality must be controlled and versioned; the blind authoring protocol (§4.5) must log the authoring transcript so entry precision can be analyzed as a moderator.
4. Cost of treatment: +24% tokens, +47% wall — worth reporting; may reverse at scale if context shortens exploration (sphinx avg turns dropped 12.7→10.3... exploratory).

## Caveats
n=10, single rep, temp 0, non-blind pilot context, gold-file overlap is a proxy (not resolve). No claim beyond: the plumbing works, and the effect is visible and bidirectional.

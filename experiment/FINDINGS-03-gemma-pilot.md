# Findings 03 — Gemma 4 (e4b) capability pilot

**Date:** 2026-07-09. Feasibility only; excluded from confirmatory analysis (PREREGISTRATION §Status).
**Setup:** `gemma4:e4b` (8B, Q4_K_M, 131K ctx) via Ollama; bash-block agent loop (`pilot/run_pilot.py`); temp 0, num_ctx 32K, num_predict 2048, think off; 20-turn cap; 10 easy instances (6 sphinx S1/S2, 4 django D1/D2); no context layer.

## Results
| Metric | Value |
|---|---|
| Loop completion (submitted, no abort) | **10/10** |
| Invalid replies (after scaffold fixes) | **0** |
| Episodes attempting edits | 10/10 |
| Non-empty patch emitted | 5/10 |
| Gold-file overlap | **2/10** (sphinx-8459, django-15499) |
| Avg wall-clock / episode | ~48 s |
| Avg tokens / episode | ~25K prompt, ~2.3K completion |

## Scaffold lessons (now frozen into harness)
1. One-shot format example + fence-fallback extractor (small model drops ```bash fences).
2. `num_predict` 2048 + "minimal targeted edits, never rewrite a file" rule + truncation nudge (model tried whole-file heredoc rewrites and got cut off).
3. Empty-diff submit guard: 5/10 episodes submitted after edits silently failed to apply (sed no-match / heredoc error); harness now rejects the first empty-diff submit with a verify nudge.

## Capability verdict
- **Loop coherence: solved.** Recovery behavior observed (python-heredoc → sed → shorter python across failing turns in 7454).
- **Investigation quality: consistently good** — reaches plausible modules within ~3 turns.
- **Localization: weak** — 2/10 touched a gold file. Failure mode is *confidently editing the wrong file* (e.g., 7454: edited `ext/autodoc/typehints.py`; gold is `domains/python.py`).
- **Resolve floor: ≤2/10 by generous proxy; true resolve likely ~0–10%** on easy instances.

## Decisions triggered
1. **§8 pivot activates:** for the local tier, primary RQ2 metrics = constraint-violation rate + wrong-file-edit rate + tokens; resolve rate reported secondary. (To be written into the frozen pre-reg.)
2. Wrong-file-edit is a *sensitive* metric here (8/10 base rate) — plenty of headroom for context to move it. Localization guidance ("X lives in module Y") is exactly what a context layer carries; the pilot failure mode is the treatment's best-case target.
3. ~50 s/episode → full local matrix (~2,000 runs) ≈ 28 GPU-hours ≈ 2–3 overnight batches. Feasible.

## Open before freeze
- Same 10-instance pilot on the frontier tier (A-arm sanity + cost estimate).
- Verify metatron consult path makes zero Anthropic API calls (threat §10.5).
- power-sim notebook for §8 MDE.

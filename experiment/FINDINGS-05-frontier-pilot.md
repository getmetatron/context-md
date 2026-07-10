# Findings 05 — Frontier pilot (Opus 4.8) + three-way comparison

**Date:** 2026-07-09. Pilot-grade; excluded from confirmatory analysis.
**Setup:** identical scaffold to Gemma runs (`pilot/run_pilot.py`, `EXECUTOR=anthropic`), `claude-opus-4-8`, no sampling params (removed on 4.8), thinking off (default), max_tokens 2048/turn, control arm (no context), 1 rep.

## Three-way gold-file table (10 easy instances)

| arm | gold-hits | patches | avg turns | avg tokens | avg wall | cost |
|---|---|---|---|---|---|---|
| Gemma 4 (no ctx) | 2/10 | 7/10 | 10.8 | 38.7K | 57s | ~0 |
| Gemma 4 + context.md | 4/10 | 8/10 | 10.4 | 48.2K | 84s | ~0 |
| **Opus 4.8 (no ctx)** | **9/10** | 9/10 | **7.3** | **24.0K** | **28s** | **$1.50 total** |

Per-instance: Opus missed only `django-14580`; it hit `util/docfields.py` (9230) and `serializer.py` (12125) — files neither Gemma arm found, including the one my imprecise context entry actively steered Gemma away from.

## Implications
1. **Capability gradient established (RQ4 premise confirmed):** Opus 9/10 vs Gemma 2/10 unaided. The gap (7 instances) is the headroom the E-arm (frontier-authored context → local executor) is trying to close. Gemma+pilot-context recovered 2 of the 7; a *precise*, blind-authored seed has room to recover more.
2. **Frontier ceiling effect to plan for:** on easy instances Opus has little room to improve from context (9/10 already). The frontier treatment cells (A vs C) must draw on medium/hard instances or the delta will be compressed — add difficulty stratification to instance selection for the frontier tier.
3. **Scaffold portability confirmed:** the identical bash-block loop drove both executors with zero invalid replies. Frontier used the truncation/fence fallbacks never (as predicted).
4. **Cost model, measured:** $0.15/episode (24K tokens avg). Full frontier cells (A+C, ~480 episodes) ≈ **$75** — half the earlier estimate. Frontier reps could be raised from 3 to 5 for ~$50 more if variance demands it.
5. Opus is also ~2× more token-efficient and 2× faster than Gemma locally — the "distillation" pitch (one Opus authoring pass, then free local inference) remains the economic story at scale, not per-task substitution.

## Pre-reg deltas to apply at freeze
- §2: frontier tier sampling params N/A (Opus 4.8 rejects temperature/top_p); determinism via 3 reps + full transcripts.
- §3: stratify frontier-tier instance selection by difficulty (avoid easy-only ceiling).
- §8: budget table updated with measured $0.15/episode.

## Status: all pilot inputs for the pre-registration freeze are now collected.

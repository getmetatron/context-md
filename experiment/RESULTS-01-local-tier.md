# Results 01 — Local tier, Tier-1 transfer pairs (confirmatory)

**Date:** 2026-07-10. First post-freeze confirmatory data. 12 Tier-1 pairs × 5 reps × 3 arms = 360 episodes (220 unique after dedup), all B-side outcomes below. Executor: gemma4:e4b. Full episode logs, promotions, and eval verdicts in `runs/`; per-row data in `runs/analysis_bsides.csv`.

## B-side outcomes (60 episodes/arm)

| arm | non-empty patch | gold-file hit | resolved |
|---|---|---|---|
| B — no context (control) | 68.3% | 25.0% | 0% |
| D — emergent self-learning | 58.3% | 25.0% | 0% |
| E — blind frontier seed | **76.7%** | **41.7%** | 0% |

Paired analyses (per pair×rep, sign-flip permutation, 10k draws, seed 42):

- **E vs B: +16.7 pp gold-file hit, p = 0.041** (RQ1 family, local-tier primary metric per §8 pivot; single confirmatory test in family at this tier)
- **D vs B: +0.0 pp, p = 1.00** — **null.** Self-learned context did not improve transfer (RQ2 family, local tier)
- Resolve rate 0% in all arms — the §8 floor, as pre-registered; resolve is secondary at this tier

## Interpretation (within pre-registered framing)

1. **H1-direction support (E):** a context layer authored blind by a frontier model, from an *years-stale* checkout, moved an 8B executor's localization from 25%→42% and increased episode completion (+8pp non-empty). This is the distillation result the E-arm was designed to test, now with p<.05 on the pre-registered primary metric.
2. **H2 null at the local tier (D):** Gemma's own promoted lessons (162 across 60 pair-reps, 90% promotion rate) produced zero transfer benefit — and *lowered* completion (58% vs 68% non-empty; the accumulating context may distract a small model). Consistent with FINDINGS-04's bidirectionality: context quality is load-bearing, and an 8B model's self-extracted lessons are mostly low-value (tooling tips, not repo constraints).
3. **Together, 1+2 sharpen the paper's claim:** the RCL lifecycle helps when the *writer* is capable, even when the *reader* is weak. Knowledge flows down the capability gradient, not up from a weak model's own experience. This makes the pending C-arm (frontier self-learning) and D-oracle arm the decisive next cells: does emergent learning work when the learner (C) or the teacher (oracle) is strong?

## Caveats
- Gold-file hit is a localization proxy; resolve (the ultimate metric) shows nothing at this tier by design.
- Holm correction: E-vs-B and D-vs-B sit in different pre-registered families (RQ1, RQ2); no cross-family correction applies. If a reviewer pools them into one family, the exact corrected p is 0.0812 (0.081 at three decimals) — report both readings.
- Empty patches count as gold-miss (per the §6 formula); arm-level non-empty rates are reported alongside to keep that interpretable.

## Next cells
1. C-arm (frontier emergent) + A-arm controls on the same pairs — does self-learning work at frontier capability? (~$40)
2. D-oracle (labeled upper bound): Gemma taught by the gold patch — is the local null a learning problem or a teaching problem?
3. RQ3 accumulation sequences; Tier-2 pair expansion for power.

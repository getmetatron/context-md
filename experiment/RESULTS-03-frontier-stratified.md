# Results 03 — Stratified frontier arms (C2/A2): the lifecycle works at frontier capability

**Date:** 2026-07-10. Rerun of C/A per the frozen §3 stratification rule: 16 ordered pairs across 11 constraint groups, all B-sides difficulty ≥ "15 min – 1 hour". 3 reps, 144 episodes, isolated under `runs/C2`/`runs/A2` (no shared state with Tier-1 cells). Per-row data `runs/analysis_bsides_03.csv`.

## B-side outcomes (16 pairs × 3 reps = 48/arm)

| arm | non-empty | gold-hit | **resolved** |
|---|---|---|---|
| A — Opus, no context | 89.6% | 81.2% | 58.3% |
| **C — Opus, self-taught via lifecycle** | **100%** | **91.7%** | **72.9%** |

Paired (sign-flip, 10k, seed 42):
- **resolve: +14.6 pp, p = 0.041** (frontier-tier pre-registered primary)
- gold-hit: +10.4 pp, p = 0.064

Direction is positive in 8 of 11 constraint groups, flat in 2, negative in 1 (S4, −33 pp on n=3 — noted, small-n).

## What this establishes

**H2 at the frontier: supported.** A frontier agent that works task A, extracts its own lessons (no gold patch, no hidden tests — §5 guards), passes them through the mechanical rubric, and consults them on a *different* held-out task sharing the constraint, resolves that task 14.6 pp more often than the same agent without the lifecycle. On mostly ~1-hour-class real bugs, that is the difference between 58% and 73% — recovered from the agent's *own prior failure experience* at a cost of one extra learning turn per task.

Combined with RESULTS-01/02, the full picture:

| executor | context author | effect |
|---|---|---|
| weak | itself | null |
| weak | frontier (blind seed) | +16.7 pp localization (p=.041) |
| weak | gold-distilled (bound) | +31.7 pp localization (p=.0005), resolves appear |
| **frontier** | **itself** | **+14.6 pp resolve (p=.041)** |

The lifecycle is real at the top of the capability range; distillation carries its benefit down the range. The one configuration that fails is a weak model teaching itself — the P4 loop requires writer capability, wherever the writing happens.

## Caveats
- n=16 pairs × 3 reps; the effect is significant but the CI is wide — Tier-2/rep expansion applies here too if a tighter estimate is wanted for the paper.
- Exploratory per-group heterogeneity (one negative group) should be shown, not hidden — Fig. per-group forest plot recommended.
- One A2 episode (xarray-7393 rep3) crashed and was re-run with identical parameters before any eval; logged here as the sole infrastructure deviation for this round (no protocol impact).

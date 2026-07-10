# Results 02 — D-oracle and frontier arms (confirmatory + labeled upper bound)

**Date:** 2026-07-10. Completes the decisive cells: C/A (frontier, 3 reps, $24) and D-oracle (local, 5 reps). B-side outcomes on the 12 Tier-1 pairs; per-row data `runs/analysis_bsides_02.csv`; 443 eval verdicts total.

## B-side outcomes

| arm | n | non-empty | gold-hit | **resolved** |
|---|---|---|---|---|
| B — Gemma, no context | 60 | 68.3% | 25.0% | 0.0% |
| D — Gemma, self-taught (R-01) | 60 | 58.3% | 25.0% | 0.0% |
| **Do — Gemma, oracle-taught** | 60 | 83.3% | **56.7%** | **8.3%** |
| A — Opus, no context | 36 | 94.4% | 94.4% | 72.2% |
| C — Opus, self-taught | 36 | 86.1% | 86.1% | 66.7% |

## Paired tests (sign-flip, 10k, seed 42)

- **D-oracle vs B, gold-hit: +31.7 pp, p = 0.0005** (local-tier primary)
- **D-oracle vs B, resolve: +8.3 pp, p = 0.066** — Gemma goes from **zero resolves in 120 unaided/self-taught episodes to 5/60** when its context carries gold-derived principles
- C vs A, resolve: −5.6 pp, p = 0.73 — null under a severe ceiling (A at 72% resolve / 94% gold-hit on these mostly-easy pairs; the §3 stratification note anticipated exactly this — the frontier lifecycle question needs harder instances and is NOT answered by this cell)

## The complete local-tier gradient

Same executor, same tasks, same scaffold — only the context author varies:

| context author | gold-hit | Δ vs none |
|---|---|---|
| none | 25.0% | — |
| Gemma itself (D) | 25.0% | +0.0 pp |
| Opus, blind seed (E, R-01) | 41.7% | +16.7 pp (p=.041) |
| Gold patch, distilled (Do) | 56.7% | +31.7 pp (p=.0005) |

**Benefit is monotonic in lesson quality.** This is the paper's central empirical figure: the context layer is a working knowledge conduit, and its value is set by the writer's capability, not the reader's. An 8B model reads well and writes poorly; the lifecycle works when paired with a capable author (human, frontier model, or extracted from authoritative fixes).

## Interpretation notes
- Do is a **labeled upper bound** (§4.3): the teacher saw gold patches of A-instances only. It bounds what better lesson-authoring could achieve; it is not a deployable condition. That the bound is high (and lifts actual resolves) is what makes the E-arm's deployable +16.7 pp credible as a floor, not a fluke.
- C-vs-A is inconclusive by design limitation (ceiling), not evidence against P4 at the frontier. Follow-up: rerun C/A on `15 min - 1 hour`+ instances per the frozen stratification rule.
- Resolve p=.066 is marginal at n=60; Tier-2 pair expansion (~40 pairs) is the pre-planned power increase.

## Remaining for the paper
1. C/A on stratified harder instances (frontier lifecycle question, ~$40–60)
2. Tier-2 pairs for the local arms (power for the resolve claim)
3. RQ3 accumulation sequences
4. Writing: methods + results now largely determined by frozen docs

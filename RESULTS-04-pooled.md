# Results 04 — Pooled Tier-1+2 analysis (pre-planned expansion, prereg §8)

**Date:** 2026-07-11. Tier-2 expansion: 24 additional chronological pairs from the FINDINGS-02 groups (Tier-1 excluded), arms B/E/Do, 5 reps, 480 episodes + 130 eval jobs. Pooled frame: 36 pairs × 5 reps = 180 B-side episodes/arm. Per-row data `runs/analysis_bsides_04.csv`.

## Pooled B-side outcomes

| arm | n | non-empty | gold-hit | resolved |
|---|---|---|---|---|
| B — no context | 180 | 68.3% | 21.1% | 5.6% |
| E — blind frontier seed | 180 | 81.1% | **47.2%** | 6.1% |
| Do — oracle bound | 180 | 79.4% | **42.8%** | 7.8% |

Paired (sign-flip, 10k, seed 42):
- **E vs B gold-hit: +26.1 pp, p < 0.0001** (was +16.7, p=.041 at Tier-1 alone — strengthened)
- **Do vs B gold-hit: +21.7 pp, p < 0.0001** (was +31.7, p=.0005 — remains decisive)
- E vs B resolve: +0.6 pp, p = 1.0; **Do vs B resolve: +2.2 pp, p = 0.22 — the Tier-1 marginal (p=.066) does NOT survive pooling.** Tier-2's easier B-sides give the control a nonzero resolve baseline (5.6%), diluting the oracle's edge. At the local tier there is **no supported resolve claim**; localization and completion are the effects.

## What changes in the narrative
1. **Process claims now decisive.** Both context-author tiers above the executor improve localization at p<10⁻⁴ with +20–26 pp effects — far beyond the pre-registered MDE.
2. **The gradient's top flattens.** Pooled, blind-seed and oracle are statistically indistinguishable; the defensible claim is a *threshold*, not a staircase: context helps iff its author's capability exceeds the executor's (self-authored = control exactly; both stronger-author tiers ≈ +2x baseline localization).
3. **Local resolve movement retracted.** The Tier-1 "8.3% resolves, p=.066" reading is superseded; the paper must not claim local-tier resolve gains. (The frontier-tier resolve result, +14.6 pp p=.041, is untouched — it lives in a separate stratified experiment.)

## Paper updates required (§11.2, Figure 3, abstract, threats)
- Report pooled numbers as primary for the local tier; Tier-1-only figures replaced.
- Figure 3 → paired-delta bars (self +0.0 / seed +26.1 / oracle +21.7) to avoid cross-tier baseline mixing; oracle resolve segment removed.
- Abstract: "monotonic in the capability of the author" → "requires an author more capable than the executor"; localization number updated to +26 pp.
- Threats: replace "expansion pre-planned" sentence with the pooled resolve null, stated plainly.

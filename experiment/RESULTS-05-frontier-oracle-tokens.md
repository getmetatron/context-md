# Results 05 — Frontier oracle arm and token economics

**Date:** 2026-07-11. C-oracle (§4.3 labeled arm): same 16 stratified pairs × 3 reps as C2/A2; the A-side lesson-extraction step additionally saw the maintainers' gold patch. Never pooled with confirmatory arms. Token analysis covers all existing arms (episode logs; §6 metric). Per-row data `runs/analysis_bsides_05.csv`.

## Frontier B-side outcomes (48/arm)

| arm | gold-hit | resolve | tokens/episode | tokens/resolved task |
|---|---|---|---|---|
| A — no context | 81.2% | 58.3% | 49,786 | 81,792 |
| C — self-taught | 91.7% | **72.9%** | 40,584 | **55,658** |
| Co — gold-taught (labeled bound) | 85.4% | 60.4% | 40,409 | 64,097 |

Paired: Co vs A resolve +2.1 pp (p=1.0); Co vs C resolve −12.5 pp (p=0.067); Co vs A tokens −12,646 (p=0.049).

## Finding 1 — Failure experience beats answer keys at the frontier
Gold-derived lessons transferred nothing (indistinguishable from no context); self-derived lessons were worth +14.6 pp. The tier inversion is sharp: the 8B executor benefited MOST from gold-derived lessons (+21.7 pp localization); the frontier executor benefits ONLY from its own failures. Interpretation: answer-derived lessons encode solutions; failure-derived lessons encode traps and process. A weak model needs to be told where things are; a strong model needs to be told where it will go wrong. Design implication for context layers: at high executor capability, *process* knowledge is the payload that transfers — solution summaries are not.

Caveats: labeled arm, n=48, the direct C-vs-Co contrast is marginal (p=0.067); framed as directional, not confirmed.

## Finding 2 — Context pays for itself at the frontier (tokens, §6)
- C vs A: −9,856 tokens/episode (−20%, p=0.13); turns −1.3 (p=0.072).
- **Tokens per resolved task: 81.8K → 55.7K (−32%).**
- Decomposition: episodes ending in a fix cost the same in both arms (~33.6K); the savings come from fewer doomed explorations.
- Co saved tokens identically (−12.6K/episode, p=0.049) without converting them into resolves — context of any kind shortens wandering; only failure-derived context also prevents failure.
- Local tier contrast: E costs +7,970 tokens/episode (+20%, p=0.012) with fewer turns (−1.5, p=0.001) — the injected block outweighs the shortened episodes. For a strong model context is self-financing; for a weak one it is a paid upgrade.

## Paper updates (applied in v0.2)
§11.2: two new paragraphs (failure-vs-answers; token economics) + Figure 4 (tokens per resolved task); threats note for the labeled marginal contrast.

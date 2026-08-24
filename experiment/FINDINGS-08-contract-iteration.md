# Findings 08 — Contract wording iteration: procedural v3 closes the 8B compliance gap

**Date:** 2026-07-15. Product side-project (Pavel's call: iterate until good, then fix upstream). Pilot-grade; all cells excluded from confirmatory analysis.
**Method:** contract variants as `pilot/contracts/files-vN.md`; dev set = the 10 FINDINGS-03 instances; held-out = 10 fresh easy Verified instances (4 django, 3 sphinx, 3 xarray — xarray unseen during iteration), run under BOTH v2 (shipped) and v3 for a paired wording comparison. Metrics: strict consultation, **deep read** (contents of `context.md`/a decision file entering the transcript), gold-file hit.

## The variant that worked (v3, `pilot/contracts/files-v3.md`)

Not stronger obligation language — **procedure**: numbered steps, copy-pasteable commands, stated consequence.
1. `cat context.md` / 2. `cat context/decisions/<topic>.md` for relevant topics / 3. only then plan, and state what you read — plus "a fix that contradicts a decision will be rejected in review. Listing the directory is not reading."

## Results (gemma4:e4b)

| cell | consulted | deep read | gold hit |
|---|---|---|---|
| dev, v1 (0.11.0) | 3/10 | 0/10 | 3/10 |
| dev, v2 (0.11.1) | 2/10 | 0/10 | 1/10 |
| dev, **v3** | **10/10** | **10/10** | 5/10 |
| held-out, v2 | 0/10 | 0/10 | 6/10 |
| held-out, **v3** | **10/10** | **10/10** | 6/10 |

v3: 20/20 consultation + deep read across dev and held-out, all first-command, correct shard selection in spot-checks (e.g. django-16595 → migration-optimization shard → gold file). **Honest cell:** held-out gold-hit shows no v3 advantage (6 vs 6) — these easy instances have a high localization baseline; outcome effects are the confirmatory study's job, not the pilot's. What the iteration establishes is *consultation compliance*, the mediator — not outcomes.

## Frontier cell (Claude Code headless, subscription; NOT scaffold-uniform)

Two-part finding:
1. **Plumbing bug:** headless Claude Code loads CLAUDE.md only — `metatron context setup`'s AGENTS.md was never in context (marker-file probe). A one-line `CLAUDE.md` containing `@AGENTS.md` bridges it. Same class: Gemini CLI reads GEMINI.md only.
2. **With the bridge, current v2 wording suffices at frontier:** 10/10 consulted (typically tool call #1), 8/10 deep reads, 10/10 gold hits. Pavel's hypothesis ("high-end models will adhere to current instructions") confirmed — *conditional on the file actually loading*.

## Conclusions

- The compliance gap was two independent problems: **wording** (binds small models; procedural v3 closes it 20/20) and **plumbing** (binds frontier frameworks; bridge files close it).
- Upstream both: v3-style templates + CLAUDE.md `@AGENTS.md` bridge in `context setup` → 0.12.0. Prereg freezes against the 0.12.0 text; H1 point prediction moves to ⟨~100%⟩ under the shipped contract (report with CI; the interesting confirmatory questions shift to RQ2/RQ3 outcome and token effects, plus S-arm shard selection).
- Gemini CLI cell pending OAuth (runner ready: `pilot/run_gemini_cli.py`).

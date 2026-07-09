# Findings 01 — SWE-bench existence check for constraint clusters

**Date:** 2026-07-09
**Question:** Do SWE-bench Verified instances cluster by shared underlying constraint well enough to support the A→B transfer design?
**Answer: Yes.** Multiple repos have 10–35-instance thematic clusters, far exceeding the ~15-pair minimum.

## Data
- SWE-bench Lite (300) and Verified (500) cached in `data/*.parquet`.
- Verified includes a per-instance `difficulty` label (`<15 min fix`, `15 min – 1 hour`, …) — usable directly for the Gemma floor-effect subset.
- Subsystem map per instance: `data/verified_subsystems.json`.

## Proposed repo set (5 repos, ~350 instances available)

| Repo | Instances | Best constraint clusters (theme → n [easy/med]) |
|---|---|---|
| django/django | 231 | migrations 35 [11/21]; queryset evaluation 32 [5/22]; expressions/aggregation 28 [7/18]; admin 28 [10/17]; forms/validators 11 [7/1] |
| sphinx-doc/sphinx | 44 | autodoc typehints/annotations 22 [9/10]; py-domain xrefs 6 [2/3] |
| sympy/sympy | 75 | printing/LaTeX consistency 15 [3/11]; simplify correctness 9 [3/5] |
| pydata/xarray | 22 | coords/attrs preservation 17 [3/12]; dtype/nan 11 [2/9] |
| scikit-learn/scikit-learn | 32 | estimator API contract 23 [9/14]; input validation 5 [2/2] |

Reserve: matplotlib (unit/axis 10, colormap/norm 5), astropy (io contract 10, units 7).

## Why these clusters fit the transfer design
Each theme corresponds to a plausible *operating constraint* an agent could learn as a principle and reuse:
- django migrations → "migration operations must preserve state consistency / be reversible"
- xarray coords/attrs → "operations must propagate attrs/coords; silent dropping is the historic bug class"
- sphinx autodoc → "type-hint rendering rules interact with `autodoc_typehints` config; check both signature and description paths"
- sklearn estimator contract → "estimators must follow fit/get_params/clone conventions"
- sympy printing → "every new expression type needs consistent str/pretty/LaTeX printers"

## Caveats
1. Keyword matching is coarse (e.g., django "timezone" theme hit only 5; some hits will be false positives). **Manual verification of top clusters required** before locking pairs — read each problem statement, confirm the shared constraint is real and the lesson from A genuinely bears on B.
2. Difficulty split matters for Gemma: easy-heavy clusters (django forms/validators 7 easy; sphinx autodoc 9 easy; sklearn contract 9 easy) are the best pilot targets.
3. Clusters overlap (an instance can match 2 themes); dedupe when assigning A→B pairs so no instance appears in two pairs.

## Next
1. Manual pass over the 3 richest clusters (django migrations, sphinx autodoc, xarray attrs) to hand-confirm ~10 transfer pairs each.
2. Gemma 4 capability pilot on 10 easy instances.
3. Pre-registration draft (promotion rubric, consultation mechanics, ordering randomization, MDE statement).

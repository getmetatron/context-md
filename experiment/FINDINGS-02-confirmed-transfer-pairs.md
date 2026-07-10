# Findings 02 — Manually confirmed constraint groups & A→B transfer pairs

**Date:** 2026-07-09
**Method:** Read problem statements of the 3 richest clusters (sphinx autodoc 22, django migrations 35, xarray attrs/coords 17). Grouped by *underlying constraint* (not keyword). A pair qualifies if a principle-level decision learned from A plausibly changes the outcome on B.

## Tier-1 groups (regression chains — one instance cites the other's territory)

### X1. xarray `keep_attrs` threading ★ best in benchmark
Constraint: *every operation must thread `keep_attrs`; variable attrs and coordinate attrs are distinct and both must be handled.*
- `pydata__xarray-3305` — quantile ignores keep_attrs [med]
- `pydata__xarray-4687` — xr.where drops attrs [med]
- `pydata__xarray-6461` — xr.where + scalar + keep_attrs crashes [easy]
- `pydata__xarray-7229` — keep_attrs **overwrites coord attrs; explicitly a regression from the #6461 fix** [med]
- `pydata__xarray-4629` — merge(combine_attrs='override') references instead of copies [easy]
Chain: 6461 → 7229 is a *documented* causal pair. 5 instances ⇒ up to 4 ordered A→B pairs.

### D1. django migration-optimizer reductions
Constraint: *the optimizer must reduce composable operation pairs; new reductions follow the CreateModel+AlterModelOptions precedent.*
- `django__django-13786` — squash fails to unset options in CreateModel+AlterModelOptions [med]
- `django__django-15499` — reduce CreateModel+AlterModelManagers [easy]
- `django__django-16595` — reduce consecutive AlterField [easy]
- `django__django-16819` — reduce AddIndex/RemoveIndex [med]
- `django__django-15268` — optimize multiple AlterFooTogether [hard]
15499 and 16819 are near-isomorphic tasks: the 13786/15499 lesson transfers almost mechanically.

### D2. django `deconstruct()` fidelity
Constraint: *deconstruct must emit stable, importable references and must never evaluate callables.*
- `django__django-13343` — callable storage evaluated on deconstruct [med]
- `django__django-16493` — callable returning default_storage omitted — **regression in the same feature as 13343** [med]
- `django__django-11815` — Enum default serialized by value not name [med]
- `django__django-12125` — inner-class field path wrong [easy]
- `django__django-14580` — missing `models` import in generated migration [easy]
- `django__django-15161` — use simplified paths for expression deconstruct [med]
- `django__django-17087` — nested-class classmethod default path wrong [easy]
7 instances; 13343 → 16493 is a documented regression pair.

## Tier-2 groups (strong shared constraint, no literal citation)

### S1. sphinx `autodoc_typehints` config interplay
Constraint: *typehint rendering has interacting knobs (autodoc_typehints, autodoc_type_aliases, typehints_description_target); signature and description code paths must both consult them.*
- `sphinx-doc__sphinx-10449` [easy], `sphinx-doc__sphinx-7454` [easy], `sphinx-doc__sphinx-8459` [easy], `sphinx-doc__sphinx-9673` [med]

### S2. sphinx py-domain annotation parsing
Constraint: *annotations must go through `_parse_annotation`/unparse, which must handle edge nodes (empty tuple, Literal, dict(str,str), property annotations) and emit xrefs.*
- `sphinx-doc__sphinx-7462` [easy], `sphinx-doc__sphinx-9230` [easy], `sphinx-doc__sphinx-9591` [easy], `sphinx-doc__sphinx-9602` [med]

### S3. sphinx autodoc mock objects: `sphinx-doc__sphinx-7889` [easy], `sphinx-doc__sphinx-9658` [med]
### S4. sphinx member-visibility rules (`__all__`, `:meta public:`, private-members): `sphinx-doc__sphinx-8595` [easy], `sphinx-doc__sphinx-8593` [med], `sphinx-doc__sphinx-8035` [med]
### D3. django db-router compliance: `django__django-11066` [easy], `django__django-15252` [med], `django__django-7530` [med]
### D4. django namespace-package migrations: `django__django-11141` [med], `django__django-13820` [med]
### D5. django SQLite table-rebuild semantics: `django__django-15278` [med], `django__django-15561` [med], `django__django-11299` [easy]
### X2. xarray dtype preservation: `pydata__xarray-3095` [med], `pydata__xarray-7393` [med]
### X3. xarray no-mutation: `pydata__xarray-6938` [med] (+3095 overlaps)

## Inventory
- **Tier-1:** 3 groups, 17 instances, ≥12 ordered A→B pairs, incl. 2 documented regression chains (6461→7229, 13343→16493).
- **Tier-1+2:** 12 groups, ~40 instances, 25+ pairs across 3 repos — comfortably above the ~15-pair power floor, in 3 repos (generality).
- **Easy-difficulty share** is high in S1/S2 and D1/D2 — good Gemma 4 pilot targets.

## Design implications
1. Flagship transfer study runs on Tier-1 groups; Tier-2 broadens N and repo diversity.
2. The regression chains enable the cleanest possible narrative: "the benchmark itself contains the failure mode RCL prevents — a lesson learned in instance A was forgotten and re-broken in instance B; we test whether a context layer carries it."
3. Dedupe rule: an instance appears in at most one group (3095 assigned to X2, not X3).
4. Sequencing for Study 2: within-repo chronological order (`created_at`) is the ecologically valid choice — mirrors real project history; randomized orders as robustness check.

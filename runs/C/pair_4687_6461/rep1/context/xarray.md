# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In xarray/core/computation.py, use `_get_keep_attrs` (imported from `.options`) to resolve `keep_attrs=None` against the global default; `apply_ufunc` accepts a `keep_attrs` argument to propagate attributes.
- [2026-07-09] numpy/xarray may not be importable in this environment, so runtime verification of code changes can fail; rely on static review instead.

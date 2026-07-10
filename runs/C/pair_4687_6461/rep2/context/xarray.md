# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In xarray/core/computation.py, high-level functions like `where` are implemented via `apply_ufunc`; attribute propagation is controlled by passing `keep_attrs=True`.
- [2026-07-09] The dev environment may lack numpy/xarray installed, so runtime verification of xarray code changes via `python3` may fail with ModuleNotFoundError.

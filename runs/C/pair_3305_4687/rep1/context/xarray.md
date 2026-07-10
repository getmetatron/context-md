# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] The `keep_attrs` convention across xarray/core: default `None`, resolved via `_get_keep_attrs(default=False)` from `xarray.core.options`, then apply `attrs = self.attrs if keep_attrs else None`.
- [2026-07-09] The `quantile` method is implemented in parallel across `xarray/core/variable.py`, `dataarray.py`, `dataset.py`, and `groupby.py`; changes to its signature/behavior often need to propagate through all of them.
- [2026-07-09] `Dataset` reduce-style methods delegate per-variable to `Variable` methods (e.g. `var.quantile(...)`); pass `keep_attrs` through so per-variable attrs are preserved, not just dataset-level attrs.

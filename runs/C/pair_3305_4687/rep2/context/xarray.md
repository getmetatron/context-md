# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] `_get_keep_attrs(default=False)` from `xarray/core/options.py` is the standard pattern for resolving a `keep_attrs=None` argument to the global option; used across variable.py, dataset.py, dataarray.py.
- [2026-07-09] Dataset reduction methods (e.g. quantile) iterate `self.variables.items()` and delegate per-variable computation to the corresponding `Variable` method; attribute retention must be threaded through both the Dataset level and the Variable-level call.

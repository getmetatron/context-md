# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `PandasIndexAdapter` in xarray/core/indexing.py preserves a custom `_dtype`; when re-wrapping its `.array`, always pass `dtype=self._dtype` or the dtype is lost. Prefer giving the adapter its own `copy(deep=...)` method so callers don't reconstruct it manually and drop metadata.
- [2026-07-11] xarray type hints use `DTypeLike` from `xarray/core/npcompat`, not numpy directly.

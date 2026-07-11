# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `PandasIndexAdapter` (xarray/core/indexing.py) preserves a wrapped index's dtype; recreating one from `array.copy()` without passing `dtype` loses the original dtype. Prefer giving wrapper classes a `copy(deep=...)` method rather than reconstructing them at call sites.
- [2026-07-11] xarray copy semantics distinguish deep vs shallow; a shallow copy should share the underlying array while deep copies duplicate it. Note shallow numpy arrays can become deep copies upon pickling.
- [2026-07-11] `IndexVariable._data` is a `PandasIndexAdapter` wrapping a pandas Index (immutable), so its `deep` copy flag affects only the underlying array, not attrs/dims/encoding which are always copied.

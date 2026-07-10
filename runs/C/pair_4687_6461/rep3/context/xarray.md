# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] `_get_keep_attrs` is imported in `xarray/core/computation.py` from `.options`; use `_get_keep_attrs(default=...)` to honor the global `keep_attrs` option when a function's `keep_attrs` arg is None.
- [2026-07-09] `apply_ufunc` in `xarray/core/computation.py` accepts a `keep_attrs` kwarg to control attribute propagation; top-level functions like `where` delegate attribute handling to it.
- [2026-07-09] The repo's runtime environment may lack numpy; don't rely on importing xarray to validate changes—verify edits via source inspection instead.

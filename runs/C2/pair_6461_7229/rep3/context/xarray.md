# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] `xr.where`'s `keep_attrs=True` is defined to preserve attributes of `x` (the second argument), matching the `where` method on DataArray/Dataset.
- [2026-07-10] This repo's Python interpreter isn't on PATH as `python`/`python3` with xarray installed; ad-hoc runtime verification of xarray imports may fail in the sandbox. Rely on code inspection instead.

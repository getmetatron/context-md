# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In xarray, `keep_attrs` handling follows a common pattern: `if keep_attrs is None: keep_attrs = _get_keep_attrs(default=False)`, where `_get_keep_attrs` is imported from `.options` in core modules like variable.py.
- [2026-07-09] Dataset reductions build results by iterating `self.variables.items()`, skipping coords and (when `numeric_only`) non-numeric vars, then reassembling via `self._replace_with_new_dims(variables, coord_names=..., attrs=..., indexes=...)`.
- [2026-07-09] DataArray methods often delegate to Dataset by calling `self._to_temp_dataset().<method>(...)` and wrapping the result with `self._from_temp_dataset(ds)`.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] The `keep_attrs=True` convention in `where()` preserves the attributes of `x` (the second parameter), matching the `where` method of `DataArray`/`Dataset`.
- [2026-07-10] The system `python3` (`/opt/homebrew/bin/python3`) lacks numpy; you cannot import xarray to test. Validate edits with `ast.parse` for syntax checks instead.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In xarray/core/computation.py, `keep_attrs` can be a callable `(attrs, context)`; the `attrs` list may not align positionally with input args when some are scalars, so prefer reading `getattr(obj, "attrs", {})` directly for a specific argument.

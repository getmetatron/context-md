# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In `xarray/core/merge.py`, attribute merging lives in `merge_attrs(variable_attrs, combine_attrs)`; when returning a source dict (e.g. `combine_attrs="override"`), wrap it with `dict(...)` to avoid returning a shared reference that later mutations would corrupt.
- [2026-07-11] When sed's `-i` behaves oddly (treating the filename as a command argument on BSD/macOS sed), fall back to an inline Python script using `str.replace` for reliable in-place edits.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In `merge_attrs` (xarray/core/merge.py), returning attrs must copy the source dict (e.g. `dict(variable_attrs[0])`), so callers don't mutate the original object's attrs by reference.
- [2026-07-11] Merge/combine functions that return one input's attrs should return a copy, not the original mapping, to keep inputs and outputs independent.
- [2026-07-11] `sed -i` with a filename after the script is error-prone; a small Python `str.replace` block is a reliable alternative for targeted in-file edits.

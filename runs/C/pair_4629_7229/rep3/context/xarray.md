# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] On BSD/macOS `sed -i` requires an argument (backup suffix) after `-i`; the shown `sed -i 'expr' file` failed. Prefer a small Python replace script for in-place edits to stay portable.
- [2026-07-09] In xarray, `merge_attrs` in xarray/core/merge.py should return a new dict (e.g. `dict(...)`) rather than aliasing an input's attrs, to avoid callers mutating shared attribute dictionaries.

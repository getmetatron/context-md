# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In `xarray/core/merge.py`, `merge_attrs` handles combine_attrs modes ("drop", "override", "no_conflicts"); returning attrs should copy via `dict(...)` to avoid sharing references with source objects.
- [2026-07-10] On BSD/macOS `sed`, `-i` requires an explicit backup suffix argument (e.g. `sed -i.bak`); `sed -i '...'` misparses the script as the suffix and errors.

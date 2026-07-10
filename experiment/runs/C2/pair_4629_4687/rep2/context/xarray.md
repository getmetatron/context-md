# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] On macOS/BSD sed, `-i` requires an explicit backup suffix argument (e.g. `-i.bak`); `sed -i 'expr' file` fails with "extra characters at the end". Use `-i.bak` then delete the backup, or use GNU sed syntax only on Linux.
- [2026-07-10] In xarray, attribute-merging logic lives in `merge_attrs` in xarray/core/merge.py; `combine_attrs="override"` should return a copy (`dict(...)`) of the first attrs to avoid aliasing the source object.

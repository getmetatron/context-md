# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In `merge_attrs` (xarray/core/merge.py), `combine_attrs="override"` must return a copy (`dict(variable_attrs[0])`), not the original attrs, to avoid aliasing/mutation across merged objects.
- [2026-07-09] On BSD/macOS `sed`, always use `sed -i.bak` (or `sed -i ''`); `sed -i 'expr' file` misparses because it treats the file arg as the extension.

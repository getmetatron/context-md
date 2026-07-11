# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In xarray's merge machinery (xarray/core/merge.py), attribute-combining logic lives in `merge_attrs`, dispatching on the `combine_attrs` string ("drop"/"override"/"no_conflicts"/etc.).
- [2026-07-11] When returning attrs from a source object, copy the dict (`dict(attrs)`) rather than returning the reference, so callers can't mutate the original's attributes.
- [2026-07-11] The BSD `sed -i` on macOS requires an explicit backup suffix (`sed -i.bak`); passing just `-i` treats the next arg as the suffix and errors.

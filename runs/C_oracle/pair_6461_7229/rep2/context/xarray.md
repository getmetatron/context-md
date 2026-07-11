# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In `xarray/core/computation.py`, `keep_attrs` callbacks receive `(attrs, context)` where `attrs` is a list of attribute dicts from all operands; indexing that list can fail when an operand is a scalar lacking attrs, so prefer `getattr(operand, "attrs", {})`.

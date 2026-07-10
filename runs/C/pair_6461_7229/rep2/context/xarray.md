# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In `xarray/core/computation.py`, `keep_attrs` can be a callable taking `(attrs, context)`; `attrs` is a list of the operands' attribute dicts, but scalar arguments won't have entries, so indexing like `attrs[1]` can misalign—prefer `getattr(operand, "attrs", {})`.
- [2026-07-09] The `xarray` package imports numpy at import time; environments here may lack a working `python`/`python3` with numpy installed, so runtime verification of changes may not be possible.

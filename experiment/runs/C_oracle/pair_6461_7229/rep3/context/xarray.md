# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In xarray, `keep_attrs` callbacks receive `(attrs, context)` where `attrs` is a list of the inputs' attrs; indexing it (e.g. `attrs[1]`) breaks when an input is a scalar with no attrs. Prefer `getattr(var, "attrs", {})` on the intended source variable instead.
- [2026-07-11] The `python` command may be unavailable; use `python3` to run scripts in this repo.
- [2026-07-11] To edit a specific line without sed quoting pitfalls, use a short `python3` heredoc that reads, replaces the target line, and rewrites the file.

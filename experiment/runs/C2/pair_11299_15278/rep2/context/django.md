# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In `django/db/models/sql/query.py`, the `simple_col` flag distinguishes column references: `SimpleCol` (aliasless, for CHECK constraints/build_where) vs regular `Col`. See `_get_col()`. This flag must be threaded through recursive `_add_q`/`build_filter` calls or nested Q-objects lose it.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In `django/db/models/sql/query.py`, `_add_q` recurses on nested `Node` children; propagate flags like `simple_col` through recursive calls or they silently drop for nested Q-objects.
- [2026-07-10] `SimpleCol` vs `Col` selection is centralized in `_get_col(target, field, alias, simple_col)`; the `simple_col` flag threads through `resolve_lookup_value`, `build_filter`, and `_add_q`.

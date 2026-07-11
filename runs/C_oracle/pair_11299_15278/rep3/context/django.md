# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/models/sql/query.py, column resolution can produce either Col or SimpleCol via `_get_col(target, field, alias, simple_col)`; SimpleCol is used for check-constraint/WHERE contexts without table aliases.
- [2026-07-11] When adding a parameter to filter-building methods like `build_filter`, propagate it through recursive `_add_q` calls too, since `_add_q` recurses into nested Q Node children and must forward flags like `simple_col`.

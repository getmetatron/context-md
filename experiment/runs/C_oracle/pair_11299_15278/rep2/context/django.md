# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] The `simple_col` flag threads through `resolve_lookup_value`, `build_filter`, and `_add_q`; `_get_col` in this module chooses between `SimpleCol(target, field)` and `target.get_col(alias, field)` based on it.

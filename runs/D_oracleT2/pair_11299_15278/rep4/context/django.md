# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying SQL generation logic within Django's ORM components, always check the `as_sql` signature for context-passing arguments, as default behavior might incorrectly qualify table names.
- [2026-07-10] Core database constraint logic resides in `django/db/models/constraints.py`, and related query utilities are found in `django/db/models/query_utils.py`.
- [2026-07-10] Changes affecting SQL compilation often require understanding the interplay between `Query` objects, `compiler` instances, and the specific context arguments accepted by `as_sql`.

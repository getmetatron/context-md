# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Core database constraint logic resides in `django/db/models/constraints.py`, while general query building utilities are in `django/db/models/query_utils.py`.
- [2026-07-10] Changes affecting SQL compilation across multiple constraint types (e.g., `CheckConstraint` and `UniqueConstraint`) should be reviewed for consistent application of context fixes.

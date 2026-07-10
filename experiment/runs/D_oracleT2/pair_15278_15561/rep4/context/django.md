# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core database backend logic, always check for specific SQL dialect limitations (e.g., SQLite's handling of `ALTER TABLE` constraints).
- [2026-07-10] When modifying complex recursive logic, explicitly check for proxy model metadata (`model._meta.proxy`) to prevent infinite recursion or incorrect state tracking.
- [2026-07-10] Database schema manipulation logic must account for the interaction between field constraints (like `unique` or `primary_key`) and the capabilities of the underlying SQL dialect's `ALTER TABLE` command.

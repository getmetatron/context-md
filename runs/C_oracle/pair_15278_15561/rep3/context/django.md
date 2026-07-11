# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/backends/sqlite3/schema.py, SQLite's ALTER TABLE ADD COLUMN cannot handle primary keys, unique fields, or fields with defaults; such cases must fall back to `_remake_table` rather than `super().add_field`.

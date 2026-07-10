# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] SQLite schema editing lives in django/db/backends/sqlite3/schema.py; SQLite lacks full ALTER TABLE support, so many operations (defaults, non-null, unique columns) require rebuilding the table via `_remake_table` rather than using base-class ALTER statements.

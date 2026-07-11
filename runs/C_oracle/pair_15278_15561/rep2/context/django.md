# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] SQLite's ALTER TABLE ADD COLUMN cannot handle primary keys, unique fields, or defaults; `add_field` in django/db/backends/sqlite3/schema.py must route these through `_remake_table` rather than the base implementation.

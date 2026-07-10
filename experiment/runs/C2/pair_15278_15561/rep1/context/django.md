# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] SQLite schema changes live in django/db/backends/sqlite3/schema.py; because SQLite's ALTER TABLE ADD COLUMN is limited (no DROP DEFAULT, no unique constraints), operations that can't use plain ALTER fall back to `_remake_table`, which rebuilds the whole table.
- [2026-07-10] In sqlite3 schema editor, `add_field` must route through `_remake_table` for any field that ALTER TABLE ADD COLUMN can't express (non-null, defaults, unique).

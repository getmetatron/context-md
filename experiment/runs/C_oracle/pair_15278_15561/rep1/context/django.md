# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] SQLite's `add_field` in django/db/backends/sqlite3/schema.py must fall back to `_remake_table` for fields that ALTER TABLE ADD COLUMN can't handle: primary keys, unique fields, non-null fields, and fields with defaults (SQLite lacks DROP DEFAULT).
- [2026-07-11] When editing Python source via shell, use a heredoc-driven Python script with exact string `assert ... in` matching; avoid `sed` for multiline edits and never paste raw Python into a bash prompt.

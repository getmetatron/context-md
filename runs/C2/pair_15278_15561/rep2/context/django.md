# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] SQLite lacks full ALTER TABLE support; the sqlite3 backend (django/db/backends/sqlite3/schema.py) works around this via `_remake_table`, which rebuilds the table for operations like primary keys, unique fields, or non-null/defaulted columns.
- [2026-07-10] Implicit many-to-many tables are detected via `field.many_to_many and field.remote_field.through._meta.auto_created`, and created with `self.create_model(field.remote_field.through)`.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation squashing/optimization logic lives in each operation's `reduce()` method in django/db/migrations/operations/fields.py, using `is_same_field_operation()` to detect operations targeting the same field.

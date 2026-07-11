# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration operation optimization lives in `reduce()` methods in django/db/migrations/operations/*.py; each operation collapses with a following same-target operation, using `is_same_field_operation`/`is_same_model_operation` helpers to confirm they target the same object.
- [2026-07-11] A consecutive AlterField on the same field should reduce to just the later AlterField, since the final field definition supersedes the earlier one.

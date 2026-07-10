# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation optimization lives in `reduce()` methods on operation classes in `django/db/migrations/operations/`; each checks the next operation via `isinstance` plus `is_same_field_operation()` and returns a reduced list.
- [2026-07-09] Field operations provide `is_same_field_operation(operation)` to confirm two operations target the same model field before reducing/merging them.

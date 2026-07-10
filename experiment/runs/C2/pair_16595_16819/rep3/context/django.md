# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration operations live in `django/db/migrations/operations/`; each defines a `reduce(self, operation, app_label)` method that optimizes consecutive operations by returning a replacement list (e.g., collapsing chained same-field operations).
- [2026-07-10] `FieldOperation` subclasses provide `is_same_field_operation(operation)` to check that two operations target the same model field before reducing them together.

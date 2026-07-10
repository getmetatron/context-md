# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration operations optimize/collapse via a `reduce(self, operation, app_label)` method in django/db/migrations/operations/; it returns a list of replacement operations when consecutive ops can be merged.
- [2026-07-10] `is_same_field_operation(operation)` (from FieldOperation) checks two field operations target the same model and field, used to gate reductions in fields.py.

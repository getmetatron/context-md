# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operations implement `reduce(self, operation, app_label)` in django/db/migrations/operations/fields.py to collapse consecutive operations; use `self.is_same_field_operation(operation)` to check they target the same model/field.
- [2026-07-09] When optimizing migrations, consecutive operations of the same type on one target can often collapse to just the later operation (e.g., AlterField followed by AlterField returns the second).

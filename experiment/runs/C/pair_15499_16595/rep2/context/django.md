# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation squashing/optimization is implemented via `reduce()` methods in `django/db/migrations/operations/models.py`; `CreateModel.reduce()` folds subsequent Alter* operations (options, managers, together) back into a new CreateModel by matching `self.name_lower == operation.name_lower`.

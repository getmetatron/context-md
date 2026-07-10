# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation optimization/squashing logic lives in `django/db/migrations/operations/models.py`, where operations implement `reduce()` to merge with a following operation into new operations.
- [2026-07-09] `AlterModelOptions.ALTER_OPTION_KEYS` lists options that AlterModelOptions manages; when empty in an operation, those keys must be removed from the merged options (they represent clearing), not just overwritten.

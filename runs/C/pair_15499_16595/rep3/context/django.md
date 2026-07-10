# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation squashing/optimization lives in `reduce()` methods in django/db/migrations/operations/models.py; CreateModel.reduce() handles collapsing subsequent operations (DeleteModel, RenameModel, AlterModel*, FieldOperation) into an updated CreateModel.

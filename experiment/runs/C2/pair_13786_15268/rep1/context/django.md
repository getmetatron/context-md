# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration operation squashing/optimization lives in each operation's `reduce()` method in django/db/migrations/operations/models.py; CreateModel.reduce merges subsequent operations into a new CreateModel.
- [2026-07-10] AlterModelOptions defines ALTER_OPTION_KEYS listing option keys it manages; when merging its options, keys absent from the new options must be removed (popped), because AlterModelOptions replaces rather than adds those keys.

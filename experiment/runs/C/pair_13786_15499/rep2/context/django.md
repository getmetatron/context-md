# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In django/db/migrations/operations/models.py, AlterModelOptions defines `ALTER_OPTION_KEYS`, the canonical list of model options it manages; keys absent from an op's options mean those options were cleared, so merging must remove them, not just overlay.
- [2026-07-09] Migration operation reduction/squashing happens in `CreateModel.reduce()` (and other operations' reduce methods) in django/db/migrations/operations/models.py; matching relies on `name_lower` comparisons.

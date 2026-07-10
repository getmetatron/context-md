# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In django/db/migrations/operations/models.py, AlterModelOptions defines ALTER_OPTION_KEYS listing option keys it manages; applying it removes any of those keys absent from its own options dict, so optimizer merges must replicate this removal, not just merge dicts.
- [2026-07-10] Migration operations support optimizer reduction via `reduce()`; CreateModel folds subsequent operations (like AlterModelOptions) into a new CreateModel, so merge logic must mirror the operation's own apply semantics.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration operation optimization/reduction logic lives in `django/db/migrations/operations/models.py`, where `CreateModel.reduce()` merges subsequent operations like `AlterModelOptions` into a new `CreateModel`.
- [2026-07-10] `AlterModelOptions` defines `ALTER_OPTION_KEYS`, listing option keys it manages; absence of a key in its `options` means that option should be cleared, not left unchanged, when merging.

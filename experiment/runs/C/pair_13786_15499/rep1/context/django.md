# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operations implement `reduce()` in django/db/migrations/operations/models.py to squash sequences; when merging into CreateModel, replicate the target operation's own semantics (e.g. AlterModelOptions clears unset ALTER_OPTION_KEYS), not just a naive dict merge.
- [2026-07-09] AlterModelOptions defines `ALTER_OPTION_KEYS`, the option keys it fully manages; keys absent from its options dict mean those options should be removed, not preserved.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/migrations/operations/models.py, `AlterModelOptions` semantics require clearing keys in `ALTER_OPTION_KEYS` that are absent from its `options` dict; merging alone leaves stale options, so reduce/squash logic must replicate this removal.
- [2026-07-11] Migration operations implement optimization via a `reduce()` method; when combining a `CreateModel` with a later operation, mirror the later operation's full state-application semantics, not just a naive dict merge.

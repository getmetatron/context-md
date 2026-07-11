# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `AlterModelOptions` semantics: keys in `AlterModelOptions.ALTER_OPTION_KEYS` that are absent from the operation's `options` mean "clear that option," not "leave unchanged"; merging must remove those keys, not just overlay present ones.
- [2026-07-11] Migration operation optimization lives in `reduce()` methods in `django/db/migrations/operations/models.py`; `CreateModel.reduce` folds subsequent alter operations back into the model's stored `options`.
- [2026-07-11] When squashing/merging model options in migrations, replicate the same clearing behavior the standalone operation applies at state-mutation time, or squashed migrations diverge from unsquashed ones.

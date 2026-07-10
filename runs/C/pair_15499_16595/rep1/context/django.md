# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation optimization lives in each operation's `reduce()` method in `django/db/migrations/operations/models.py`; `CreateModel.reduce()` folds subsequent operations (DeleteModel, RenameModel, AlterModelOptions, AlterModelManagers, FieldOperation) into a new CreateModel by matching `name_lower`.
- [2026-07-09] Migration optimizer tests are in `tests/migrations/test_optimizer.py`.
- [2026-07-09] To run Django's test suite, use `python tests/runtests.py <label>` from the repo root; pytest is not installed and `django` must be importable (run with the repo on PYTHONPATH or installed).

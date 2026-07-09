# Repository Context

## Intent
Django's migration framework derives schema operations from model state. Generated
migration files must be deterministic, importable, and optimizable.

## Constraints
- Migration operation *reduction* (collapsing consecutive operations) lives in
  `django/db/migrations/optimizer.py` (the loop) and in the `reduce()` methods of
  the operation classes in `django/db/migrations/operations/models.py` and
  `operations/fields.py`. New reductions follow the existing
  `CreateModel`+`AlterModelOptions` precedent: implement/extend `reduce()` on the
  operation class, not the optimizer loop.
- `deconstruct()` fidelity: every field/expression must deconstruct to a stable,
  importable dotted path with its arguments serializable. Never *evaluate* a
  callable during deconstruction — store the reference. Value serialization for
  migration files lives in `django/db/migrations/serializer.py`; path resolution in
  the field's own `deconstruct()`. Wrong-path bugs (inner classes, enums, callables)
  are the historic bug class here.
- Migration file text (imports, headers) is produced by
  `django/db/migrations/writer.py` — missing-import bugs belong there or in
  `serializer.py`, not in the autodetector.
- Test single modules with `python tests/runtests.py migrations.test_optimizer -v 0`
  (uses sqlite; fast). Never run the full suite.

## Evolved Context
- [2026-07-09] The autodetector (`db/migrations/autodetector.py`) decides WHICH
  operations exist; the optimizer decides how they COMBINE; the writer decides how
  they PRINT. Fixes should target the narrowest of the three that explains the bug.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] The `@deconstructible` decorator (from `django.utils.deconstruct`) accepts a `path=` kwarg to set the import path used when serializing objects into migrations; use it for publicly-exported classes.
- [2026-07-11] Only decorate classes that are actually public API (exported in `django/db/models/__init__.py`) with an explicit `path=`; internal helper classes like `OrderByList`/`ExpressionList` should not get a public path.
- [2026-07-11] Run Django's test suite via `PYTHONPATH=. python3 tests/runtests.py <label>` from the repo root, since `django` isn't installed as an importable module.

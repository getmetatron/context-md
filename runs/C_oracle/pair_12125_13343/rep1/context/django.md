# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration serializers live in django/db/migrations/serializer.py; when emitting import paths for classes/types use `__qualname__` (not `__name__`) so nested/inner classes serialize with their full dotted path.
- [2026-07-11] Run Django's tests via `PYTHONPATH=.. python3 runtests.py <label>` from the tests/ directory; pytest is not available and runtests.py won't find the django package without PYTHONPATH pointing to the repo root.

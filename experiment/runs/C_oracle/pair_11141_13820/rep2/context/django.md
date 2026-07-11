# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In `django/db/migrations/loader.py`, a migrations directory should be treated as unmigrated when it contains no actual migration files, rather than relying on `__file__`/`__path__` heuristics to distinguish namespace vs regular packages.
- [2026-07-11] Namespace packages (`__file__` is None) are legitimately used for migration directories; don't reject them—inspect actual migration module contents via `pkgutil.iter_modules(module.__path__)` instead.
- [2026-07-11] Distinguishing migrated vs unmigrated apps: check whether real migration files exist (respecting `ignore_no_migrations`), not merely whether the package/module is loadable.

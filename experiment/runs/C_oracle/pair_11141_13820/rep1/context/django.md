# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In `django/db/migrations/loader.py`, apps are classified migrated/unmigrated based on whether the migrations package actually contains migration files (via `pkgutil.iter_modules`), not merely on module attributes like `__file__` or `__path__`.
- [2026-07-11] Distinguishing regular packages from namespace packages via `__file__ is None` is unreliable; prefer detecting emptiness by inspecting actual contents (e.g., iterating modules) rather than filesystem/package attribute heuristics.
- [2026-07-11] The `ignore_no_migrations` flag on the migration loader controls whether apps with no migration files are treated as migrated versus unmigrated.

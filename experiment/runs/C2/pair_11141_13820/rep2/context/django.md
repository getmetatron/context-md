# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In Django, migration module discovery lives in django/db/migrations/loader.py, distinguishing packages, namespaces, and non-package modules.
- [2026-07-10] Namespace packages have `__file__` of None but their `__path__` is not a list; regular packages use a list for `__path__`. Don't rely on `__file__` alone to detect namespaces.

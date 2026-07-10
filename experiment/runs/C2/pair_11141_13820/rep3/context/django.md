# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration package discovery lives in django/db/migrations/loader.py; it detects unmigrated apps by checking module `__path__`/`__file__`.
- [2026-07-10] Distinguish real packages from namespace packages by testing `getattr(module, '__file__', None) is None and not isinstance(module.__path__, list)`, since namespace packages lack `__file__` and don't use a list for `__path__`.

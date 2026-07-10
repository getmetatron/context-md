# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In django/db/migrations/loader.py, migration modules with no `__file__` aren't always namespace packages; regular packages may lack `__file__`. Distinguish true namespace packages by checking `__path__` is not a list (namespace `__path__` is a `_NamespacePath`, not a list).
- [2026-07-10] Prefer editing Python source files via a scripted read/replace with an `assert old in s` guard to ensure the target text matched before writing, avoiding silent no-op edits.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] `@deconstructible` in `django/utils/deconstruct.py` accepts a `path=` kwarg to override the reported import path; classes exported via `django/db/models/__init__.py` should use their public `django.db.models.X` path to keep migration serialization stable.
- [2026-07-09] The `path` override only applies when `type(obj) is klass` (exact class), so each subclass needing a public deconstruct path must carry its own `@deconstructible(path=...)` decorator.
- [2026-07-09] Running `tests/runtests.py` requires django to be importable in the environment; a bare invocation fails with `ModuleNotFoundError` unless django is installed/on the path.

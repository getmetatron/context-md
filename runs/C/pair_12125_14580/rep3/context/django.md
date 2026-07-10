# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Django migration serialization lives in `django/db/migrations/serializer.py`; `DeconstructableSerializer._serialize_path` splits a deconstructed path on the last dot, which mishandles inner (nested) classes whose path includes the enclosing class via `__qualname__`.
- [2026-07-09] Run Django's test suite via `python3 tests/runtests.py <module>` from the repo root, not from `/tmp`; imports fail unless the checkout's `django` package is on the path (run from repo root).
- [2026-07-09] Field `deconstruct()` returns `(name, path, args, kwargs)`; the true module is available separately as `self.value.__class__.__module__`, useful when the path string alone is ambiguous.

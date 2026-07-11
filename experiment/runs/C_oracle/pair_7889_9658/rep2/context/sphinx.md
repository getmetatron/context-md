# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc/mock.py, `_make_subclass(name, ...)` passes name to `type(name, ...)`, which requires a str; callers must stringify non-str keys (e.g. TypeVar) before passing.
- [2026-07-11] Mock `__getitem__` keys can be arbitrary objects (like typing constructs), not just strings, so type them as `Any` and coerce to str.

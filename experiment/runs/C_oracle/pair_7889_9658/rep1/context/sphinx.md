# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc/mock.py, `_make_subclass(name, ...)` passes `name` to `type()`, which requires a `str`; callers whose key may be non-string (e.g. `__getitem__` with subscript arguments) must coerce with `str()`.
- [2026-07-11] When a dunder like `__getitem__` can receive non-string keys (subscripts such as ints or tuples), annotate the parameter as `Any` rather than `str` to reflect actual runtime inputs.

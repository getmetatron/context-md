# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc/mock.py, mock magic methods like `__getitem__` receive arbitrary key types (not just str); coerce keys/names with `str()` before passing to `type()`, which requires a real str for the class name.
- [2026-07-11] When a function's declared param type (e.g. `key: str`) doesn't match real runtime inputs, correct the annotation and coerce at the entry point rather than patching every downstream use.

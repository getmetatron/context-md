# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration value serialization lives in `django/db/migrations/serializer.py`, dispatched via `Serializer._registry`; type serialization is handled by `TypeSerializer`, and nested/inner class names require `__qualname__` rather than `__name__`.
- [2026-07-09] Splicing files by fixed line-number slices in Python scripts (`lines[:254] + ... + lines[272:]`) is fragile and can drop or corrupt surrounding code; prefer targeted string replacement and always re-verify with `ast.parse` afterward.
- [2026-07-09] Running this Django checkout may fail on newer Python because `django/utils/version.py` imports `distutils.version`, which is removed in recent CPython; don't rely on importing `django` directly to validate changes.

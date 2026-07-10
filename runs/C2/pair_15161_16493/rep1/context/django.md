# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] The `@deconstructible` decorator (from `django.utils.deconstruct`) accepts a `path=` kwarg to set the import path emitted by `deconstruct()`; classes reexported in `django.db.models.__init__` should use their public path there.
- [2026-07-10] Public expression classes live in `django/db/models/expressions.py` and are reexported via `django/db/models/__init__.py`.
- [2026-07-10] BSD sed on macOS requires an argument after `-i` (use `-i ''`) and doesn't support GNU `sed -i` line-brace forms; prefer Python scripts for reliable in-place edits.

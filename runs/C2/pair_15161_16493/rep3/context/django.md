# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] `django.utils.deconstruct.deconstructible` accepts a `path=` kwarg to override the import path reported by `deconstruct()`; use it so expressions/classes serialize to their public `django.db.models.X` path rather than their defining module.
- [2026-07-10] Public expression classes are defined in `django/db/models/expressions.py` and re-exported via `django/db/models/__init__.py`; the public import path is `django.db.models.<ClassName>`.

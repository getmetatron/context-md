# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] The `@deconstructible` decorator (django.utils.deconstruct) accepts a `path=` kwarg to override the import path used in migrations/serialization, letting internal classes deconstruct to their public API location.
- [2026-07-09] Public model expression classes live in django/db/models/expressions.py but are re-exported via django/db/models/__init__.py; their canonical public path is `django.db.models.<ClassName>`.

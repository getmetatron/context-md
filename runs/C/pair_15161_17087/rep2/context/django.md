# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] `@deconstructible(path='...')` sets a class's public import path in migration deconstruction; the path should match the canonical export in `django/db/models/__init__.py` (e.g. `django.db.models.F`).
- [2026-07-09] Expression classes live in `django/db/models/expressions.py` and are re-exported from `django/db/models/__init__.py`; keep the two in sync when adding/exposing expressions.
- [2026-07-09] `@deconstructible` can be applied bare or with keyword arguments like `path`; the decorator supports both call styles.

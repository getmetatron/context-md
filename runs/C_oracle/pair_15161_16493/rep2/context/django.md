# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] The `@deconstructible` decorator (django.utils.deconstruct) accepts a `path=` kwarg to set the import path used when serializing an object's deconstruction; use the public `django.db.models.X` path for classes re-exported there.
- [2026-07-11] Public expression classes live in `django/db/models/expressions.py` and are re-exported via `django/db/models/__init__.py`; only classes actually exported/deconstructed need `@deconstructible` with a stable public path.
- [2026-07-11] When adding `@deconstructible(path=...)` to public classes, avoid decorating internal-only classes (e.g. Ref, OrderByList, ResolvedOuterRef) and subclasses not meant for public deconstruction paths.

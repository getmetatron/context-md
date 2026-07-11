# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] A module's `__file__` being None indicates a namespace package (PEP 420); don't treat that alone as "unmigrated." Namespace packages are valid migration dirs and can be distinguished (e.g. `__path__` is not a plain list).
- [2026-07-11] In `django/db/migrations/loader.py`, apps are classified as migrated/unmigrated based on whether the migrations package actually contains migration modules, not merely on package/namespace type.

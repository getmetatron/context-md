# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] `@deconstructible(path=...)` sets the import path used by migration serialization; the deconstruct output reflects the path kwarg. It's defined in `django/utils/deconstruct.py` and can be applied to expression classes in `django/db/models/expressions.py`.
- [2026-07-10] Public model expression classes (F, Value, Func, etc.) are exported from `django/db/models/__init__.py` under `django.db.models.*`, so their deconstruct path should point there, not the internal `expressions` module.
- [2026-07-10] When testing Django internals, `django.setup()` may fail if apps/settings aren't fully configured; importing a module directly (e.g. `django.db.models.expressions`) can bypass that. Delete stale `.pyc` files if edits don't take effect.

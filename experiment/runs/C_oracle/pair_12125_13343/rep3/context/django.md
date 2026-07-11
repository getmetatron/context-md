# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration serialization lives in django/db/migrations/serializer.py, with a separate BaseSerializer subclass per value type; TypeSerializer.serialize handles class references.
- [2026-07-11] For nested/inner classes, use `__qualname__` (not `__name__`) when building serialized paths so the enclosing class is included; `__name__` drops the outer class prefix.
- [2026-07-11] Django field deconstruction (django/db/models/fields/__init__.py) already uses `__qualname__` in path construction; follow that convention for consistency when emitting import paths.

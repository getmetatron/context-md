# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration serializers live in `django/db/migrations/serializer.py`, each a `BaseSerializer` subclass whose `serialize()` returns a `(code_string, imports_set)` tuple; imports are strings like `'import module'`.
- [2026-07-09] Serialize enum members by name (`EnumClass[name]`) rather than by value, so renaming/reordering enum values doesn't break serialization; use `__qualname__` for nested classes.
- [2026-07-09] Use `serializer_factory(value).serialize()` to recursively serialize nested values within a serializer.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration value serialization lives in `django/db/migrations/serializer.py`, with per-type serializer classes (e.g. `EnumSerializer`) each returning a `(code_string, imports_set)` tuple from `serialize()`.
- [2026-07-09] Serializing Enum members by name (`Enum[name]`) is more robust than by value, since values may not round-trip or be unique; use `self.value.name`.

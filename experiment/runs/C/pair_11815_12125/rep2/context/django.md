# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration value serializers live in django/db/migrations/serializer.py; each type has a BaseSerializer subclass with a serialize() returning a (code_string, imports_set) tuple.
- [2026-07-09] Serialize Enum members by name (EnumClass[name]) rather than by value, so migrations survive value changes (e.g. translated labels) while still referencing a stable member.

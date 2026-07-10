# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In django/db/migrations/serializer.py, each serializer's serialize() returns a (string, imports) pair; any generated code referencing a name (e.g. `models.Model`) must include the corresponding import in the imports list, or migrations will fail with NameError.
- [2026-07-10] TypeSerializer handles special-cased types via a `special_cases` list of (type, string_repr, imports) tuples in django/db/migrations/serializer.py.

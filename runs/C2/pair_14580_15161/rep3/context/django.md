# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration serialization lives in django/db/migrations/serializer.py; each serializer's serialize() returns a (string, imports) tuple where imports is a set of import statements needed for the emitted string to be valid.

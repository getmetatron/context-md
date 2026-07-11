# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/migrations/serializer.py, each serializer's serialize() must return both a code string AND its required import set; a code string referencing a name (e.g. `models.Model`) must include the matching import or migrations will fail.
- [2026-07-11] Migration serialization dispatches to per-type Serializer classes in django/db/migrations/serializer.py; TypeSerializer handles types via a `special_cases` list of (value, string, imports) tuples.

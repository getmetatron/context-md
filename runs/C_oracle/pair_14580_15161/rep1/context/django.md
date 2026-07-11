# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In django/db/migrations/serializer.py, serializers return a `(string, imports)` pair; any name referenced in the returned string must have its import listed (e.g. `models.Model` requires `["from django.db import models"]`).
- [2026-07-11] Migration serialization lives in django/db/migrations/serializer.py, dispatched via `serializer_factory`; each type has a Serializer class (e.g. `TypeSerializer` handles types, using a `special_cases` list keyed by identity).

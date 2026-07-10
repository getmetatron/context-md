# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In django/db/migrations/serializer.py, serializers return a (string, imports) pair; the string representation must be paired with the import statements needed to make it valid, e.g. `models.Model` requires `"from django.db import models"`.
- [2026-07-10] TypeSerializer in the migrations serializer handles special-cased types via a list of (case, string, imports) tuples; forgetting the imports produces migration code that references names without importing them.
- [2026-07-10] `cat -A` is unavailable on macOS/BSD; use `python3 -c "print(repr(...))"` to inspect exact line contents including whitespace.

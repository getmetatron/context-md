# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] In django/db/migrations/serializer.py, use `__qualname__` (not `__name__`) when serializing class/type references so nested/inner classes get their full dotted path; several serializers here already follow this convention.
- [2026-07-09] Migration serializer tests live in tests/migrations/test_writer.py; `MigrationWriter.serialize()` returns a `(string, imports_set)` tuple used to verify output.
- [2026-07-09] This Django checkout can't be imported directly (distutils import error); run/verify via the repo's test runner rather than `import django`.

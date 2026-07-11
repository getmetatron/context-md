# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration serializers in django/db/migrations/serializer.py must use `__qualname__` (not `__name__`) so nested/inner classes serialize with their full dotted path (e.g. `Outer.Inner`).
- [2026-07-11] In serializer paths, `import %s` uses the full `__module__`; `_serialize_path` splits module.name via `rsplit(".", 1)`, so the import statement should reference the module, not just the top-level package.
- [2026-07-11] Migration serialization tests and expectations live in tests/migrations/test_writer.py; serializer classes (DeconstructableSerializer, EnumSerializer, etc.) each expose a `serialize()` returning `(string, imports_set)`.

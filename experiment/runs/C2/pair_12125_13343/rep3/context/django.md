# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration serialization lives in django/db/migrations/serializer.py; DeconstructableSerializer._serialize_path builds import statements from a dotted path, converting "django.db.models" prefixes to "models." references.
- [2026-07-10] When emitting `import x.y.z` statements, import only the top-level package (module.split(".")[0]), since submodule dotted paths remain valid via the full attribute reference in generated code.
- [2026-07-10] Field deconstruction (django/db/models/fields/__init__.py) builds paths via `__class__.__module__` + `__qualname__`, and shortens `django.db.models.fields.related` to `django.db.models`.

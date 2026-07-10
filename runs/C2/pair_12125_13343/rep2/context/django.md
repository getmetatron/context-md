# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration serialization lives in django/db/migrations/serializer.py, with a serializer class per type (TypeSerializer, EnumSerializer, etc.); paths should use `__qualname__`, not `__name__`, to correctly handle nested/inner classes.
- [2026-07-10] Field deconstruction (django/db/models/fields/__init__.py) already builds paths via `'%s.%s' % (__module__, __qualname__)`; match that convention when generating dotted paths elsewhere.
- [2026-07-10] On macOS this repo's environment, `cat -A` and multi-arg `sed -i` fail; prefer `od -c` for whitespace inspection and Python heredoc scripts for file edits.

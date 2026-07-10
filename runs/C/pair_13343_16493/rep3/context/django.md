# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] FileField (django/db/models/fields/files.py) accepts a callable for `storage`; it's evaluated in `__init__`. To make deconstruct() reproducible, the original callable must be preserved (stored on `_storage_callable`) rather than the resolved Storage instance.
- [2026-07-09] Field.deconstruct() should serialize the user-provided value (callable/reference), not runtime-resolved objects, so migrations regenerate the same field definition.

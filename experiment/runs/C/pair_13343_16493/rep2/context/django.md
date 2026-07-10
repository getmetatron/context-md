# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] FileField in django/db/models/fields/files.py accepts a callable `storage` argument that is resolved to a Storage instance in `__init__`; preserve the original callable to reconstruct it faithfully in `deconstruct()`.
- [2026-07-09] Field `deconstruct()` methods should emit the original user-supplied argument (e.g. a callable), not the resolved runtime value, so migrations regenerate the same field definition.

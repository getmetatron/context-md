# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Field.deconstruct() must return the original callable arguments (e.g. storage) rather than resolved instances, so migrations reference the callable; stash the original callable in a private attribute during __init__ for later retrieval.
- [2026-07-09] FileField in django/db/models/fields/files.py accepts a callable for `storage`, resolving it to a Storage instance in __init__ while validating it's a Storage subclass/instance.

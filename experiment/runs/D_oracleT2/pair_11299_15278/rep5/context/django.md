# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying files within `django/db/models/`, always check the contents of `__init__.py` first, as it often imports modules that can cause cascading import errors.
- [2026-07-10] For complex file modifications, using Python's file I/O context manager (`with open(...)`) is more robust than shell utilities like `sed` for ensuring atomic writes.
- [2026-07-10] Module structure suggests that core database logic resides in `django/db/models/sql/query.py`, while constraint definitions are handled in `django/db/models/constraints.py`.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core Django migration files, direct string replacement or simple `grep` is insufficient due to complex import structures; context-aware file reading/writing is necessary.
- [2026-07-10] Changes affecting core Django modules like `django.db` often require updating multiple related files (e.g., `writer.py` and `serializer.py`) to maintain consistency.
- [2026-07-10] Be cautious when patching imports; if a module needs to be added, ensure all related files that reference the original import are updated to reflect the new, combined import statement.

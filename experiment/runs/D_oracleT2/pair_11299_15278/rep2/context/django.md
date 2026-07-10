# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying SQL generation logic within constraints, directly calling the underlying expression's `.sql()` method is often a more robust and concise replacement for multi-step `Query` object construction.
- [2026-07-10] Core utility modules like `django/db/models/query_utils.py` define constants (e.g., `OR = 'OR'`) that should be respected when building query components.
- [2026-07-10] File system operations involving complex text replacement (like `sed`) are brittle; using programmatic file reading/writing (e.g., Python context managers) is safer for structural code changes.

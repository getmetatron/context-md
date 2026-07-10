# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core framework files, direct file manipulation via shell commands (like `sed`) is brittle; programmatic file reading/writing with conditional logic is safer.
- [2026-07-10] Imports for core components like `models` must be explicitly added to files that use them, even if the initial context suggests they might be available.
- [2026-07-10] Changes affecting serialization or type handling within `django/db/migrations/serializer.py` often require updating associated import lists to maintain correctness.

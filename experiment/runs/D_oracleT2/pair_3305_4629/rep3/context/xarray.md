# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying function signatures across multiple files, always check for default argument changes (e.g., `None` to `True`) as this affects downstream calls.
- [2026-07-10] When modifying function calls, explicitly check the required arguments for the underlying reduction functions, as simply passing the variable name might not be sufficient if the API changed.
- [2026-07-10] When using file manipulation tools like `sed` or direct file writing, ensure the target line number is accurate, as context-dependent changes are brittle.

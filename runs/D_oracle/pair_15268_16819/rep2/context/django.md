# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When testing migration operations, the core logic for reduction often involves checking if the operation references the model being altered, suggesting a pattern of checking reference dependencies.
- [2026-07-09] Direct file manipulation via shell commands like `sed` is brittle; using programmatic file reading/writing (e.g., Python's `with open(...)`) is more robust for modifying source code.

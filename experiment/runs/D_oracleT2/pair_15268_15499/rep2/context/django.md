# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When testing migration optimization, focus on the core logic being tested rather than the specific syntax of the operations being combined.
- [2026-07-10] When modifying test files, using programmatic file I/O (like Python's `with open(...)`) is significantly more robust than shell utilities like `sed`.
- [2026-07-10] Django migration operations often require checking for specific structural relationships (e.g., `references_model`) to determine if an optimization reduction is valid.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Directory structure for migration testing utilities (e.g., `tests/migrations/`) should be treated as source code locations, not just areas for simple file existence checks.
- [2026-07-10] Relying on `grep` across the entire repository for specific function signatures (`allow_migrate`) is brittle; targeted file reading or explicit module imports are more reliable for code analysis.

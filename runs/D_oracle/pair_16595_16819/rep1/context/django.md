# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying core migration logic, always check surrounding files (e.g., `autodetector.py`) to understand how the modified class is consumed by other parts of the system.
- [2026-07-09] Core migration operations often require handling multiple related field types (e.g., `AlterField` and `RemoveField`) within a single reduction method.

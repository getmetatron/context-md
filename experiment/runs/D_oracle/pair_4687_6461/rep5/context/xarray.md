# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying core functions that wrap underlying array operations, always check for and propagate attribute handling mechanisms (like `keep_attrs`) to maintain API consistency across different object types.
- [2026-07-09] Core utility functions that process multiple inputs should explicitly check for and handle optional arguments related to metadata or attribute preservation.
- [2026-07-09] When implementing attribute merging logic, it is safer to check for existing, established patterns (like `keep_attrs`) rather than applying broad, speculative replacements to return statements.

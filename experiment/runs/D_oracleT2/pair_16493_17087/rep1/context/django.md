# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying code that handles default or callable values, always test the boundary condition where the value *is* the default but *should* be treated as non-default (e.g., a callable returning the default).
- [2026-07-10] When using `sed` for complex, multi-line replacements, it is safer to read the file content into memory (e.g., using Python) and perform string replacement programmatically rather than relying on shell-level regex substitution.
- [2026-07-10] When refactoring logic involving attribute access and default checks, it is often clearer to extract the value into a local variable first, then apply the necessary checks against that variable, rather than embedding complex logic directly in the conditional statement.

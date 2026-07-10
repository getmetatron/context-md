# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying function signatures across a module, always use programmatic file reading/writing (e.g., Python's `with open(...)`) over shell tools like `sed` to ensure correct context and avoid syntax errors.
- [2026-07-09] When updating function signatures, ensure that any default arguments added (like `keep_attrs=False`) are consistently propagated to all internal calls or usages within the same file.
- [2026-07-09] When modifying core utility functions like `where`, consider the broader API context; changes might require corresponding updates in related computation modules to maintain feature parity.

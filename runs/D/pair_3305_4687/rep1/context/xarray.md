# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying function signatures, it is safer to use file reading/writing via Python context managers rather than shell tools like `sed` for precise line replacement.
- [2026-07-09] Changes affecting default arguments (e.g., setting `keep_attrs=True` in a signature) must be consistently reflected in all subsequent internal calls to that function.
- [2026-07-09] Module structure suggests that core logic modifications, especially around attribute handling, require careful tracing across multiple related methods (`first`, `last`, and the reduction call site).

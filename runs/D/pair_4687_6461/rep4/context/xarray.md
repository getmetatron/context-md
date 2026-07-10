# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying core library functions, attribute handling (like merging `x.attrs` and `y.attrs`) must be explicitly considered, even if the underlying operation seems simple.
- [2026-07-09] Direct file manipulation via shell commands like `sed` is brittle; programmatic file reading/writing with context awareness is safer for complex code changes.
- [2026-07-09] Module structure suggests that core utility functions like `where` might need to coordinate attribute passing across multiple input types (scalar, array, DataArray).

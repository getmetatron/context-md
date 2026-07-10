# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code via file content replacement, using a programmatic approach (like reading/writing the file) is more robust than shell tools like `sed` due to quoting and context sensitivity.
- [2026-07-09] Core utility functions like `where` often require updating both the function signature and all internal calls that use the function's return value or arguments.
- [2026-07-09] Module-level documentation and usage examples (e.g., in `doc/gallery.rst`) should be reviewed when modifying core API behavior to ensure consistency.

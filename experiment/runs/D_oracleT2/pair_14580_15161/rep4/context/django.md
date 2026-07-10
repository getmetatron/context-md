# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying imports across files, direct string replacement or simple `sed` commands are brittle; using programmatic file reading/writing with targeted regex substitution is more robust.
- [2026-07-10] For dependency management in code generation, explicitly checking for and adding necessary imports (like `models`) is required, even if the initial inspection suggests they might be present.
- [2026-07-10] When dealing with Django internals, the location and method of adding imports must respect existing structure, often requiring insertion immediately following related core imports.

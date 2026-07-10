# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When debugging file system interactions, always verify file existence and path validity before attempting reads or writes, as multiple tools (like `grep` or `cat`) can fail silently or with misleading errors.
- [2026-07-10] When modifying code via scripting, use explicit file reading/writing blocks rather than relying solely on shell utilities like `sed` for complex, multi-line replacements to ensure predictable state management.
- [2026-07-10] When fixing type-related serialization issues, the underlying principle often requires ensuring that the representation returned for a complex type (like `TypeVar`) is a simple, unambiguous string name, rather than relying on its full object representation.

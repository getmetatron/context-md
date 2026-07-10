# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core Django files, direct string replacement via shell commands is brittle; programmatic file reading/writing is more robust for structural changes.
- [2026-07-10] Be aware that Django's migration system relies on specific import paths; adding necessary imports often requires patching template definitions or class attributes.
- [2026-07-10] Changes affecting template strings (like `MIGRATION_TEMPLATE`) must account for the literal string delimiters (`"""\`) when injecting new content.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Migration operation optimization lives in each operation's `reduce()` method in `django/db/migrations/operations/`; operations use `self.is_same_field_operation(operation)` to detect they target the same model field.
- [2026-07-10] On macOS BSD `sed`, the `a\` append command doesn't accept `\n`-separated multiline text like GNU sed; use a portable approach (Python, patch, or file rewrite) for multi-line edits.
- [2026-07-10] Commands may run outside the expected working directory (e.g. `/testbed` may not exist); verify `pwd`/`git status` before assuming edits landed, since a failed edit leaves the tree clean.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In migration operations, `Model.save()` defaults to the default database; always pass the operation's `using=db`/`schema_editor.connection.alias` so writes go to the correct database in multi-db setups.
- [2026-07-11] `sed -i` with `s/.../.../` fails when the pattern/replacement contains slashes (e.g. file paths); prefer a small Python `str.replace` script for such in-place edits.

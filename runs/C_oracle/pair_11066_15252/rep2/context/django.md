# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In migration operations, model `.save()` and other ORM calls must pass the target `using=db` (schema_editor's connection alias); omitting it routes writes to the default database and breaks multi-db migrations.
- [2026-07-11] When `sed -i` with a pattern containing `{`, `}`, quotes, or `/` fails ("extra characters at the end of d command"), use a Python heredoc that does string `.replace()` and asserts the old string exists.

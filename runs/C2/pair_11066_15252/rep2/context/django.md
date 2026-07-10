# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In Django multi-db migration code, model instances fetched via `db_manager(db)` don't automatically save to that db; pass `using=db` explicitly to `.save()` inside `transaction.atomic(using=db)`.
- [2026-07-10] On macOS/BSD `sed -i` requires a backup-suffix argument and rejects some patterns; prefer a Python heredoc for in-place file edits in this repo.

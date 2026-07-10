# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In multi-database code, `Model.save()` must be passed `using=db` explicitly; wrapping in `transaction.atomic(using=db)` alone does not route the save to the intended database.
- [2026-07-10] macOS/BSD `sed -i` requires an argument after `-i` and differs from GNU sed; for reliable in-place edits use a Python replace script instead.

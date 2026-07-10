# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In multi-database code, model `.save()` must pass `using=db` explicitly; being inside `transaction.atomic(using=db)` does not route the save to that database.
- [2026-07-10] The macOS/BSD `sed -i` in-place edits fail on strings containing special chars; prefer a Python read/replace/write snippet for reliable literal substitution.

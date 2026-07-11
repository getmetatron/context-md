# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In Django migration operations, model `save()`/queries must pass the migration's target database explicitly via `using=db`; relying on default routing inside `transaction.atomic(using=db)` blocks can write to the wrong database.
- [2026-07-11] When `sed -i` fails with "extra characters at the end of d command" (payload contains braces/slashes), fall back to an inline Python script that does `open().read()`, `str.replace()`, and `open().write()`.

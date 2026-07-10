# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying files within Django's core structure, direct shell commands like `sed` can fail due to quoting or syntax issues; programmatic file reading/writing is more robust.
- [2026-07-10] Database operations within Django migrations, especially those involving model updates, should explicitly specify the database alias using `using=db` to ensure transactional consistency.
- [2026-07-10] Always verify the exact required signature for ORM save methods when applying fixes, as subtle changes (like adding `using=db`) can prevent runtime errors.

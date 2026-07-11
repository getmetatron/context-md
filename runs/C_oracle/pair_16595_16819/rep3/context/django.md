# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration operation squashing/optimization logic lives in each operation class's `reduce()` method in django/db/migrations/operations/*.py; consecutive same-field operations are collapsed there using `is_same_field_operation`.

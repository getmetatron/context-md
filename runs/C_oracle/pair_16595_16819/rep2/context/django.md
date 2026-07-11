# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] Migration operations implement optimization via a `reduce(operation, app_label)` method in django/db/migrations/operations/; returning `[operation]` collapses a pair of same-field operations into the later one.
- [2026-07-11] When multiple operation types reduce to the same result, prefer a single `isinstance(operation, (A, B))` check over separate branches, guarded by `self.is_same_field_operation(operation)`.

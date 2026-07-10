# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operations define optimization behavior via `reduce(self, operation, app_label)` in django/db/migrations/operations; it returns a replacement list, or `True` to allow optimizing across the operation, or `False`.
- [2026-07-09] The optimizer (django/db/migrations/optimizer.py) checks in-between operations with `op.reduce(other, app_label) is True`; there is no `can_reduce_through` method in the operations base class.
- [2026-07-09] The base `Operation.reduce` in operations/base.py only handles `elidable`; model operations extend it and typically compare via `self.name_lower == operation.name_lower` and `isinstance`.

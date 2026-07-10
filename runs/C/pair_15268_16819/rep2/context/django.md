# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation reduction is implemented via `reduce(self, operation, app_label)` in `django/db/migrations/operations/`; base class is in `base.py`. Return a list of replacement operations to collapse, or fall back to `super().reduce()`.
- [2026-07-09] The migration optimizer (`django/db/migrations/optimizer.py`) repeatedly calls each operation's `reduce()` against later operations until the operation list stabilizes.
- [2026-07-09] To run repo tests use `tests/runtests.py <module.path>` (not pytest, which isn't installed); Django must be importable, so ensure the package is on the path.

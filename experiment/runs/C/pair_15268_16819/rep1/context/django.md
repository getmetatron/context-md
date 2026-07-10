# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] Migration operation optimization is done via `reduce(self, operation, app_label)` in `django/db/migrations/operations/base.py`; it returns a list of replacement operations or a bool indicating optimizability, honoring `elidable`.
- [2026-07-09] To collapse consecutive same-type operations on the same model in migrations, override `reduce` to return `[operation]` when `isinstance(operation, self.__class__)` and `self.name_lower == operation.name_lower`, else call `super().reduce`.
- [2026-07-09] Running Django's test suite requires running via `tests/runtests.py` with django importable (installed/on path); pytest is not available and bare `python3 tests/runtests.py` fails with ModuleNotFoundError.

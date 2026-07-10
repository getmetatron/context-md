# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Field deconstruct paths use `'%s.%s' % (self.__class__.__module__, self.__class__.__qualname__)`, so inner/nested classes appear as fully-qualified dotted paths in migrations.
- [2026-07-10] Running `tests/runtests.py` requires Django importable on the path; a bare `python3 tests/runtests.py` fails with `ModuleNotFoundError: No module named 'django'` unless the environment is set up (e.g. installed/editable).

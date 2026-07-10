# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying core migration operations, always check for cascading effects across related operation classes, as removing one might require updates in multiple locations (e.g., `__init__.py`).
- [2026-07-09] Core migration operations often rely on specific internal state management; removing them requires careful verification that no other operation or utility function depends on their structure or methods.
- [2026-07-09] Changes to fundamental operation classes, like those handling model structure, necessitate reviewing related utility functions (e.g., `can_reduce_through`) for necessary cleanups or replacements.

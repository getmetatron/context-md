# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code that relies on complex method calls or comprehensions, using targeted string replacement via regex is brittle; direct code analysis or AST manipulation is safer for structural changes.
- [2026-07-09] Contextual arguments in method calls (like adding `None` to `reduce`) must be consistently applied across all similar call sites, even when the surrounding logic appears different.
- [2026-07-09] File-level context (e.g., `django/db/migrations/optimizer.py`) dictates that changes affecting core optimization logic require careful verification of all related reduction paths.

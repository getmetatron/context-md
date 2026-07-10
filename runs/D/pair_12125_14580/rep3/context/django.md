# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code via regex substitution across multiple files, it is safer to use a dedicated script that reads, processes, and writes the file content, rather than relying on multiple sequential `re.sub` calls.
- [2026-07-09] Contextual arguments added to method calls (like `None` here) must be consistently applied across all matching patterns, including those within comprehensions.
- [2026-07-09] Core logic files like `django/db/migrations/optimizer.py` are highly sensitive to argument signatures; changes must account for all call sites, not just the primary ones.

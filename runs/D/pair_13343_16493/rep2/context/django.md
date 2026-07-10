# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When using `grep` across a directory, explicitly checking for file existence or using more targeted paths prevents spurious "No such file or directory" errors.
- [2026-07-09] When modifying code based on runtime logic (like checking `callable`), replacing the execution with a placeholder (`pass`) is safer than removing the check entirely, especially for deconstruction.
- [2026-07-09] File field logic heavily relies on `django.core.files.storage`, so any changes affecting how `storage` is initialized or accessed must consider both instance and callable storage types.

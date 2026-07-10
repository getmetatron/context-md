# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying configuration options across multiple files, always check for existing option lists (like `AUTODOC_DEFAULT_OPTIONS`) to ensure new options are appended rather than overwritten or causing syntax errors.
- [2026-07-10] Option handling logic should centralize the processing of new options, ideally by adding a dedicated option handler function in the core module (`__init__.py`) and updating the option registry (`directive.py`).

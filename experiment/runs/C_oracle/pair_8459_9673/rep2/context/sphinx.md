# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `sphinx.util.inspect.signature` accepts a `type_aliases` dict; pass `app.config.autodoc_type_aliases` so annotation-extraction paths honor configured aliases consistently.
- [2026-07-11] In autodoc, callable signature extraction happens in multiple places (`sphinx/ext/autodoc/__init__.py` and `sphinx/ext/autodoc/typehints.py`); config options like `autodoc_type_aliases` must be threaded into all of them for consistent behavior.

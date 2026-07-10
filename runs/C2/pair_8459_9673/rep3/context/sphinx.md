# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In sphinx autodoc, `inspect.signature()` (from sphinx.util.inspect) accepts a `type_aliases` argument; pass `config.autodoc_type_aliases` so alias resolution is consistent across all callers.
- [2026-07-10] Autodoc typehint collection lives in sphinx/ext/autodoc/typehints.py (`record_typehints`), separate from the main signature handling in sphinx/ext/autodoc/__init__.py; config is reached via `app.config` there.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] `sphinx.util.inspect.signature` accepts a `type_aliases` dict that is forwarded to `typing.get_type_hints` to resolve annotations; pass `app.config.autodoc_type_aliases` when computing signatures in autodoc.
- [2026-07-10] Autodoc typehint recording lives in `sphinx/ext/autodoc/typehints.py`; signature-based annotation collection happens in `record_typehints`.

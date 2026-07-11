# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `sphinx.util.inspect.signature()` accepts a `type_aliases` dict (default `{}`) that resolves annotations via `typing.get_type_hints()`; pass `app.config.autodoc_type_aliases` when documenting.
- [2026-07-11] Autodoc typehint recording lives in `sphinx/ext/autodoc/typehints.py`; annotations stringified via `sphinx.util.typing.stringify` and stored in `app.env.temp_data['annotations']`.

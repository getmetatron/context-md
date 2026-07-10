# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] `sphinx.util.inspect.signature` accepts a `type_aliases: Dict` kwarg; pass `app.config.autodoc_type_aliases` so autodoc respects the `autodoc_type_aliases` config when resolving annotations.
- [2026-07-10] Autodoc typehint recording lives in `sphinx/ext/autodoc/typehints.py` (`record_typehints`/`merge_typehints`); annotations are stored in `app.env.temp_data['annotations']` and stringified via `sphinx.util.typing.stringify`.

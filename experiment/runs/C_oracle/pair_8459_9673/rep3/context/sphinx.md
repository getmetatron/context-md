# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `sphinx.util.inspect.signature()` accepts a `type_aliases` dict; autodoc call sites should pass `app.config.autodoc_type_aliases` so type-alias resolution stays consistent across all signature/annotation processing.
- [2026-07-11] Config values in autodoc are accessed via `app.config.<name>` (or `self.config.<name>` in Documenter classes); ensure every code path that reads signatures honors the same config options.
- [2026-07-11] Type annotations are rendered to strings via `sphinx.util.typing.stringify`; annotations are resolved through `typing.get_type_hints(subject, None, type_aliases)` in `sphinx/util/inspect.py`.

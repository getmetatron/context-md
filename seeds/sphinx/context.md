# Repository Context

## Intent
Sphinx is a documentation generator that builds HTML/LaTeX/etc. from reStructuredText. Its `autodoc` extension imports live Python objects and emits reST for them; the Python domain (`sphinx/domains/python.py`) then parses those object descriptions and creates cross-references. Changes to type-hint rendering, member selection, or import mocking must respect the split between the import/introspection layer (`sphinx/ext/autodoc/`) and the markup/xref layer (`sphinx/domains/`).

## Constraints

### autodoc type-hint configuration
- Config value `autodoc_typehints` accepts exactly `"signature"` (default), `"description"`, or `"none"` — registered with an ENUM validator in `setup()` of `sphinx/ext/autodoc/__init__.py`. New modes must be added to that ENUM or config validation fails.
- The `"description"` and `"none"` modes work by suppressing annotations at signature-format time: each Documenter's `format_args` sets `show_annotation=False` when `autodoc_typehints in ('none', 'description')` (three call sites in `sphinx/ext/autodoc/__init__.py` — function, method, and class documenters). A behavior change must cover all of them.
- `"description"` mode is implemented in `sphinx/ext/autodoc/typehints.py`, a sub-extension set up automatically by autodoc. It records annotations via the `autodoc-process-signature` event (`record_typehints`, storing stringified hints in `env.temp_data['annotations']`) and merges them into `:param:`/`:type:`/`:rtype:` field lists via the `object-description-transform` event (`merge_typehints`). Fixes about typehints-in-description (missing/duplicated fields, field-list merging) belong in `typehints.py`, not in the domain or the documenters.
- Annotation-to-string conversion is `sphinx.util.typing.stringify()` (`sphinx/util/typing.py`, with py36/py37 variants). Rendering bugs in hint text (e.g., `Optional`, builtins, `None`) belong there, not in autodoc.
- `sphinx/ext/autodoc/type_comment.py` (also auto-loaded) backfills annotations from `# type:` comments by AST-parsing source; it mutates live objects' signature info before formatting.

### Python-domain annotation parsing and cross-referencing
- Turning an annotation string in a signature into linked markup is the Python domain's job: `_parse_annotation()` in `sphinx/domains/python.py` AST-parses the string (via `sphinx/pycode/ast.py`) and wraps every name in a `pending_xref` with `reftype='class'`, `refdomain='py'`. Unsupported syntax falls back to one xref for the whole string. Xref-resolution failures for types in signatures are fixed here or in `PythonDomain.find_obj`/`resolve_xref` (same file) — not in autodoc, which only emits text.
- `_parse_arglist()` (same file) parses full argument lists with `signature_from_str` (from `sphinx/util/inspect.py`) and handles PEP 570 positional-only `/` markers; `_pseudo_parse_arglist` is the non-AST fallback. Signature display bugs (defaults, `*`/`**`, punctuation nodes) belong in these functions.
- Autodoc's introspection helpers (`signature`, `unwrap`, safe getattr) live in `sphinx/util/inspect.py`; keep introspection fixes there so both autodoc and the domain benefit.

### autodoc mock objects
- Mocking lives entirely in `sphinx/ext/autodoc/mock.py`. `mock(modnames)` is a context manager that installs a `MockFinder` on `sys.meta_path`; on exit it removes the finder and pops mocked modules from `sys.modules`. It is applied around imports in `sphinx/ext/autodoc/__init__.py` using `config.autodoc_mock_imports` (default `[]`).
- `MockFinder` matches a configured name and all of its descendants (`fullname.startswith(modname + '.')`). `_MockObject` returns new mock subclasses from `__getattr__`/`__getitem__`, supports subclassing via `__mro_entries__` and a 3-arg `__new__` path, and passes decorated functions/classes through unchanged in `__call__`. Bugs where mocked base classes, decorators, or attribute chains misbehave under autodoc belong in `mock.py`; do not special-case mocks inside the documenters.
- Mocked objects carry `__display_name__` (module-qualified) and `__module__` via `_make_subclass`; display-name issues for mocked types trace to that helper.

### Member visibility rules (which members get documented)
- The single decision point is `Documenter.filter_members()` in `sphinx/ext/autodoc/__init__.py`. Rules, in order: `__dunder__` names (len > 4, both ends `__`) are kept only under `:special-members:` (ALL or explicit list; `__doc__` always skipped); source-discovered attributes with attr-docs (from `self.analyzer.find_attr_docs()`) are kept unless private; private members (leading `_`, or docstring metadata `:meta private:` via `extract_metadata`) require the `private-members` option; otherwise undocumented members require `undoc-members`.
- After the built-in decision, the `autodoc-skip-member` event can override it; extensions raising in that handler cause the member to be dropped with a warning. Behavioral changes to skipping must preserve this event's final say.
- Which members are even considered comes from `get_object_members()` (per-Documenter) with helpers in `sphinx/ext/autodoc/importer.py`; visibility fixes belong in `filter_members`, enumeration fixes in `get_object_members`/importer.
- Option parsing (`:members:`, `special-members` merging via `merge_special_members_option`, `autodoc_default_options`) is handled in `sphinx/ext/autodoc/__init__.py` and `sphinx/ext/autodoc/directive.py`; a filtering bug caused by option merging belongs there, not in `filter_members`.

## Evolved Context
<!-- populated by later sessions; keep additions dated and evidence-linked -->

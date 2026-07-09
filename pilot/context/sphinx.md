# Repository Context

## Intent
Sphinx is a documentation generator. The `autodoc` extension introspects live Python
objects; the Python *domain* renders and cross-references Python constructs in output.
Keeping these two layers distinct is the core architectural rule.

## Constraints
- Division of labor for type annotations: `sphinx/ext/autodoc/typehints.py` only
  *records* hints and merges them into doc field lists. How annotations are *parsed,
  displayed, and cross-referenced* (including linking of builtin singletons and
  special typing forms) lives in `sphinx/domains/python.py` (`_parse_annotation` /
  `unparse`). A rendering or linking bug almost never belongs in ext/autodoc.
- `_parse_annotation` must handle degenerate AST nodes (empty subscripts, constants,
  strings-in-brackets). Edge-node crashes and wrong xrefs are the historic bug class
  in this function; extend it rather than special-casing callers.
- The autodoc config knobs `autodoc_typehints`, `autodoc_type_aliases`, and
  `autodoc_typehints_description_target` interact: the signature path and the
  description path are separate code paths and BOTH must consult every knob.
  Fixing one path only is the historic regression pattern.
- Run single test files (`python -m pytest tests/test_domain_py.py -x -q`); the full
  suite is too slow for iterative work.

## Evolved Context
- [2026-07-09] Docstring-derived field lists are merged in
  `sphinx/ext/autodoc/typehints.py:modify_field_list`; display formatting applied
  there will NOT affect signature mode — signature rendering is domain-side.

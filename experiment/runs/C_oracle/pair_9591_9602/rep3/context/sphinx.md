# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/domains/python.py, render type annotations via `_parse_annotation(typ, self.env)` to get cross-referenced nodes, rather than embedding raw type strings directly into `desc_annotation`.
- [2026-07-11] Python domain directive classes (PyObject subclasses like PyAttribute, PyProperty) live in sphinx/domains/python.py; their `handle_signature` builds signature nodes and shared helpers like `_parse_annotation` are reused across them.
- [2026-07-11] In sphinx/domains/python.py, `nodes` comes from `from docutils import nodes` and `addnodes` provides Sphinx-specific node types like `desc_annotation`.

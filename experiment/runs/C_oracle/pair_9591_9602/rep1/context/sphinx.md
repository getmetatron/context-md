# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/domains/python.py, render Python type annotations via `_parse_annotation(typ, self.env)` and append the resulting nodes to `desc_annotation`, rather than embedding raw type strings; this produces cross-referenced type links.
- [2026-07-11] Python object directives (PyAttribute, PyProperty, etc.) in sphinx/domains/python.py subclass PyObject; type-related options are added by copying and updating `PyObject.option_spec`, and signatures are built in `handle_signature`.

# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In sphinx/ext/autodoc/__init__.py, directive option converters live near the top: `members_option` returns ALL (sentinel) when arg is None else a set of names; `bool_option`, `members_set_option`, `member_order_option`, `inherited_members_option` follow similar patterns.
- [2026-07-10] Autodoc option converters are registered per-Documenter in the `option_spec` dict (e.g. ModuleDocumenter, ClassDocumenter); the same option must be updated in each relevant class's dict.
- [2026-07-10] Member filtering in autodoc happens in `Documenter.filter_members`, using the `ALL` sentinel and set-membership checks to decide whether to keep each member.

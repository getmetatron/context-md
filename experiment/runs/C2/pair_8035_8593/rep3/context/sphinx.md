# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In sphinx/ext/autodoc, option specs use converter functions (bool_option, members_option, members_set_option, identity, member_order_option); members_option yields either the ALL sentinel or a list of names, while bool_option yields True/False.
- [2026-07-10] Autodoc member filtering in Documenter.filter_members compares option values against the ALL sentinel and None to decide inclusion; check both branches when an option accepts optional explicit member lists.
- [2026-07-10] Option converters may be declared separately in both ModuleDocumenter.option_spec and ClassDocumenter.option_spec; update all option_spec dicts when changing an option's type.

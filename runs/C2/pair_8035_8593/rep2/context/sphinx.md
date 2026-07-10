# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] Autodoc option parsers live in sphinx/ext/autodoc/__init__.py: `bool_option`, `members_option` (returns ALL sentinel or list), `members_set_option`, etc. Each Documenter subclass declares its options dict (e.g. ModuleDocumenter, ClassDocumenter) mapping option names to these parser callables.
- [2026-07-10] Member filtering logic in autodoc's Documenter.filter_members uses `self.options.<name>` values produced by the option parsers; changing an option's parser (e.g. bool to list) requires updating all filter branches that read that option.
- [2026-07-10] The module-level `ALL = object()` sentinel in autodoc distinguishes "all members" from an explicit list; option parsers return it and filter code compares against it.

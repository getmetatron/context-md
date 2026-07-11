# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc, directive option converters live in `__init__.py`: `members_option`/`members_set_option` return the sentinel `ALL` for bare flags or a list/set of names; `bool_option` returns True. Use `members_option` (not `bool_option`) for options that should accept an optional explicit name list.
- [2026-07-11] Autodoc member-filtering logic must handle three states: option is None (absent, exclude), option is `ALL` sentinel (include all), or option is a collection of explicit names (membership check). Compare against `ALL` with `is`.
- [2026-07-11] When changing an option's accepted values, update the corresponding merge helper (e.g. options that fold into `:members:`) and deprecate the old helper via `warnings.warn(..., RemovedInSphinxXXWarning, stacklevel=2)` rather than deleting it.

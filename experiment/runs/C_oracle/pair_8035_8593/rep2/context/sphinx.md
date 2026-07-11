# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc, directive options are converted via option-spec functions like members_option/members_set_option/bool_option; changing an option from boolean to list-valued means switching its spec to members_option, which returns the sentinel ALL (no arg) or a list of names.
- [2026-07-11] autodoc uses module-level sentinels (ALL, UNINITIALIZED_ATTR, etc.) as option values; distinguish None (unset), ALL (all), and an explicit name list with identity checks (`is ALL`, `is None`), not truthiness.
- [2026-07-11] When one option's values should also be documented as members, merge them into the `members` option (see merge_members_option) rather than filtering separately; deprecate superseded helpers with RemovedInSphinxXXWarning instead of deleting them.

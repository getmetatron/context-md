# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] In sphinx/ext/autodoc, directive options are declared via an option_spec dict mapping names to converter callables (bool_option, members_option, members_set_option); changing an option to accept a list means switching its converter to members_option, not bool_option.
- [2026-07-11] autodoc option values can be None (unset), the ALL sentinel, or a list of member names; membership checks must handle all three cases explicitly rather than treating the value as a plain boolean.
- [2026-07-11] When changing a public helper's behavior in sphinx, prefer adding a new function and deprecating the old one via warnings.warn(..., RemovedInSphinxNNWarning, stacklevel=2) rather than modifying the existing function in place.

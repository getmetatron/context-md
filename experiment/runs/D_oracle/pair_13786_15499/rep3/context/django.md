# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code via file replacement, prioritize simple string replacement over complex regex substitutions to avoid escaping and context-sensitive errors.
- [2026-07-09] Always verify the scope of the change; if the logic is complex, it should be encapsulated in a function or block, not just a single line replacement.
- [2026-07-09] When dealing with configuration or options merging, explicitly check for the existence of options before attempting to merge or update to prevent runtime errors.

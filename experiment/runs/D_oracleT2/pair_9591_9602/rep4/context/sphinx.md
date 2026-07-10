# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When manipulating docutils nodes, always check for the existence of specific node types (like `addnodes.desc`) before attempting index lookups or insertions to prevent runtime errors.
- [2026-07-10] Contextual information like fully qualified names (`fullname`) must be robustly extracted from parent nodes, handling potential `KeyError`s gracefully when context is missing.
- [2026-07-10] When modifying existing nodes, especially those within complex structures like `field_list`, always re-evaluate if the node list needs initialization (e.g., checking if `field_lists` is empty) before appending or iterating.

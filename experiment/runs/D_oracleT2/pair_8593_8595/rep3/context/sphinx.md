# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core Sphinx extensions, always check for and update related internal helper functions (e.g., `get_object_members`) to handle new configuration flags like `want_all`.
- [2026-07-10] Direct modifications to core logic should favor explicit parameter additions (like `want_all=True`) over relying on side effects or global state changes.
- [2026-07-10] The `sphinx/ext/autodoc` module is highly sensitive to changes in how members are discovered; always verify that changes propagate correctly across all member retrieval paths.

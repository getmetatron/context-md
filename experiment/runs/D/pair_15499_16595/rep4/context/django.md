# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying core migration operations, always check for related operations (like `AlterModelOptions`) that might depend on the removed class to ensure consistency across the codebase.
- [2026-07-09] Changes to migration operations should be reflected in the `__all__` lists within the respective `operations/__init__.py` files to maintain discoverability.
- [2026-07-09] Use programmatic file reading/writing (like the provided Python blocks) for complex, multi-step refactoring tasks rather than relying solely on `sed`, as `sed` can be brittle with complex context matching.

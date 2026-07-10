# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying core library files, relying solely on shell tools like `sed` for complex, context-dependent removals is brittle; programmatic file reading/writing is more robust.
- [2026-07-10] Direct module introspection checks (like `hasattr(module, '__file__')`) can be highly sensitive to Python version changes or packaging mechanisms, requiring careful testing against namespace package behavior.
- [2026-07-10] The logic for determining if an application has migrations should be consolidated; checking for the existence of modules via `pkgutil.iter_modules` is the primary source of truth for package discovery.

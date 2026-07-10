# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying code that interacts with Django's migration system, always verify the expected signature of methods like `allow_migrate` across different test/utility files.
- [2026-07-10] Direct file manipulation via shell commands (like `sed`) is brittle; use programmatic file reading/writing for reliable content replacement.
- [2026-07-10] Core Django logic often requires understanding the specific API calls (e.g., `apps.get_app_config(app_label).get_models()`) rather than relying on simple string replacements.

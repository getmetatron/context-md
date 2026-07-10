# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When interacting with Django's migration system, direct file path lookups for core modules (e.g., `django/migrations/models.py`) are unreliable; rely on documented APIs or broader search patterns.
- [2026-07-10] Testing database routing logic often requires explicit handling for the default case (e.g., returning `True` if no specific condition is met) to ensure migrations proceed correctly.
- [2026-07-10] When modifying core framework behavior via tests, understanding the correct iteration pattern for retrieving models (e.g., using `get_app_config().get_models()`) is crucial for robustness.

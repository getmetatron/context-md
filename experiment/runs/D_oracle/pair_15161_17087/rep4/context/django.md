# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code using string replacement, be aware that simple string substitution can be too broad and may fail to capture the precise context required for accurate refactoring.
- [2026-07-09] When dealing with Python code structure, using dedicated AST manipulation or established library functions is safer than relying on repeated `sed` or basic string replacement for complex decorators.
- [2026-07-09] The `django.utils.deconstruct` decorator requires the fully qualified path to the class, and manual path updates must account for the module structure changes correctly.

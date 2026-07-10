# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying default values involving Python enums in migration tests, directly referencing an enum member (e.g., `TextEnum.B`) fails because the serializer expects a string representation of the class name or module path.
- [2026-07-09] For default values in `models.CharField` or `models.IntegerField` within migration tests, use the enum class's name attribute (e.g., `TextEnum.__name__`) instead of an instance member.
- [2026-07-09] Be cautious when using `sed` for file replacements; programmatic file reading/writing (like using `with open(...)`) is more robust for complex, context-aware string substitutions.

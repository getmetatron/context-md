# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code that relies on Python's `enum.Enum` members as default values in Django models, directly referencing the member (e.g., `TextEnum.B`) often fails or requires complex string manipulation.
- [2026-07-09] For default values derived from an `Enum` class within migration tests, using the class name itself (e.g., `TextEnum.__name__`) is a more robust pattern for serialization.
- [2026-07-09] When using `sed` for file replacement, be mindful of potential shell quoting issues, as direct command execution can be brittle compared to programmatic file reading/writing.

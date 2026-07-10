# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When modifying code that handles object state initialization, be mindful of how runtime evaluation affects serialization or deconstruction methods.
- [2026-07-09] Always check if a stored attribute needs special handling (like callables) to prevent incorrect state reconstruction.
- [2026-07-09] When dealing with Django field internals, assume that methods like `deconstruct` rely on specific attribute values being present or correctly typed.

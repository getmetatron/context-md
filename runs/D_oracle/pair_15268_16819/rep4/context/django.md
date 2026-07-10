# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-09] When testing migration operations, the expected reduction logic for multiple constraint operations (like `AlterUniqueTogether` and `AlterIndexTogether`) should be explicitly tested to ensure the optimizer correctly retains the final state.
- [2026-07-09] When modifying core Django migration logic, always check the `super()` call chain and consider adding helper methods like `can_reduce_through` to encapsulate complex reduction rules.

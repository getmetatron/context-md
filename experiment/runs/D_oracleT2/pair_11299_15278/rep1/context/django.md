# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When modifying code that interacts with SQL compilation or query building, always verify the required arguments for methods like `as_sql` using the current API documentation or successful execution paths.
- [2026-07-10] Changes affecting multiple, structurally similar classes (e.g., `CheckConstraint` and `UniqueConstraint`) should be reviewed for consistency across all instances.

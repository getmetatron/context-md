# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] When implementing deep copy logic across multiple related objects (like Dataset and DataArray), explicitly passing a flag or parameter (e.g., `coords_copy_fix=True`) is necessary to signal specialized copy behavior that standard deep copy mechanisms might overlook.
- [2026-07-10] Coordinate handling, especially when mixing pandas/numpy indexing types with xarray structures, requires careful attention to ensure that deep copies preserve the intended data type (dtype) rather than defaulting to generic object types.
- [2026-07-10] Overriding standard Python copy methods (`__deepcopy__`) must account for internal state management, ensuring that all constituent parts—including coordinates and underlying data—are copied consistently to maintain object integrity.

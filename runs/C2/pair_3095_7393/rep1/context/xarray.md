# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] IndexVariable data is stored as PandasIndexAdapter (xarray/core/indexing.py) wrapping a pandas.Index; pandas.Index.copy(deep=True) casts unicode dtype to object, so pass the original dtype explicitly when reconstructing.
- [2026-07-10] PandasIndexAdapter accepts a `dtype` argument to preserve the intended dtype independent of the underlying pandas.Index dtype.

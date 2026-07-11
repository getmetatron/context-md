# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-11] `PandasIndexAdapter` (xarray/core/indexing.py) wraps a pandas.Index and separately tracks `_dtype`; when copying/rewrapping, pass the original dtype to `PandasIndexAdapter(array, dtype)` since pandas index copies can cast unicode to object and lose dtype.
- [2026-07-11] `IndexVariable._data` is a `PandasIndexAdapter`; prefer delegating copy to `self._data.copy(deep=deep)` rather than reaching into `self._data.array`, so dtype and pickle-size behavior stay correct.
- [2026-07-11] In xarray, `npcompat.DTypeLike` is the type alias used for dtype parameters, and public API methods are expected to carry type annotations.

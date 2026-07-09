# Repository Context

## Intent
xarray provides N-dimensional labeled arrays and datasets on top of numpy (with optional dask backing). The core invariant is that operations return new objects with labels (dims, coords, attrs) propagated by explicit rules rather than by accident. Most user-visible behavior is implemented once at the `Variable` level (`xarray/core/variable.py`) and wrapped by `DataArray`/`Dataset`; fixes usually belong at the lowest layer that owns the behavior.

## Constraints

### Attribute handling (attrs, keep_attrs)
- The single source of truth for the `keep_attrs` default is `_get_keep_attrs(default=...)` in `xarray/core/options.py` (backed by the global `OPTIONS['keep_attrs']`). Any method that accepts `keep_attrs=None` must resolve it through this helper, never hard-code a default.
- Convention: reductions and most ops default to `keep_attrs=False` (see `Variable.reduce` in `xarray/core/variable.py`, `Dataset` methods in `xarray/core/dataset.py`); groupby's first-tier default is True (`xarray/core/groupby.py` line ~461). Follow the surrounding convention when adding parameters.
- `apply_ufunc` and its helpers in `xarray/core/computation.py` copy attrs from the *first* argument when `keep_attrs=True`; attrs merging across multiple inputs is not attempted. During `merge`/`concat`, conflicting attrs are dropped via `utils.remove_incompatible_items` (see `Variable.concat` in `variable.py`, `unique_variable` in `xarray/core/merge.py`).
- `attrs` is stored lazily as `_attrs` (None until touched) and coerced to `OrderedDict` by the setter on `Variable`; constructors pass `self._attrs` through directly. Preserve that pattern — don't materialize attrs unnecessarily.

### dtype preservation
- xarray deliberately deviates from numpy promotion to match pandas. All promotion decisions live in `xarray/core/dtypes.py`: `maybe_promote` (dtype + fill value for missing data: small ints → float32, larger ints → float64, datetime/timedelta → NaT), `result_type` (pandas-style `PROMOTE_TO_OBJECT` pairs), `get_fill_value`, `get_pos_infinity`/`get_neg_infinity` (object-dtype sentinels `INF`/`NINF`).
- Array-level wrappers that enforce these rules live in `xarray/core/duck_array_ops.py` (`as_shared_dtype`, `where`, `concatenate`, `stack`) and skip-NA reductions in `xarray/core/nanops.py`. Dtype bugs in reductions/fills belong in these modules — not in `dataarray.py`/`dataset.py`, which only orchestrate.
- Any operation that can introduce missing values (reindex/align/fillna/shift/where) must obtain its fill value via `dtypes` helpers so integer data promotes to float rather than silently truncating.

### Coordinate handling
- Coordinate containers (`DatasetCoordinates`, `DataArrayCoordinates`) live in `xarray/core/coordinates.py`; the actual conflict-resolution logic is in `xarray/core/merge.py` (`merge_variables`, `unique_variable`, `merge_core`). Binary ops on `DataArray` merge coords via `self.coords._merge_raw(other_coords)` — conflicting non-index coords are *dropped*, not errored, after `align` (from `xarray/core/alignment.py`) reconciles indexes.
- In `apply_ufunc`, `build_output_coords` in `xarray/core/computation.py` drops any coordinate whose dims intersect consumed core dims. Changes to which coords survive an operation belong there or in `merge.py`, not in per-method code.
- Promotion/demotion between data variables and coordinates goes through `Dataset.set_coords` / `Dataset.reset_coords` (`xarray/core/dataset.py`); index (dimension) coordinates cannot be removed by `reset_coords`. `DataArray` internals use `_replace_maybe_drop_dims` (`xarray/core/dataarray.py`) to prune coords when dims change — reuse it rather than rebuilding coord dicts by hand.

### Mutation semantics (copy vs in-place)
- The API is functional: methods return new objects. The `inplace=` kwargs on `Dataset` methods are deprecated via `_check_inplace` in `xarray/core/utils.py` (emits FutureWarning). Do not add new `inplace` parameters.
- Internal code creates cheap views with `self.copy(deep=False)` and mutates the fresh object before returning (pattern throughout `dataset.py`, e.g. `_replace` and `__copy__`). Never mutate `self` in a method that returns a value.
- Copy defaults differ by class and are intentional: `Variable.copy` and `DataArray.copy` default `deep=True`; `Dataset.copy` defaults `deep=False` (`dataset.py` ~line 842). Even with `deep=False`, dims/attrs/encoding containers are shallow-copied so the originals aren't aliased; `deep=True` deep-copies attrs too. The `data=` argument overrides `deep` for the data payload.
- Constructors like `type(self)(dims, data, self._attrs, self._encoding, fastpath=True)` share attrs/encoding objects between results; if a new code path mutates attrs of a derived object, it must copy first.

## Evolved Context
<!-- populated over time by agents; empty at seed time -->

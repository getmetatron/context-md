# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In xarray, `PandasIndexAdapter` lives in `xarray/core/indexing.py`; reference it as `indexing.PandasIndexAdapter` from `variable.py`, and it accepts a `dtype=` argument to preserve the original dtype.
- [2026-07-10] For editing files in this repo, prefer a Python heredoc (`python3 - <<'PYEOF'`) doing string replace with an `assert old in s` guard; `sed` in-place edits are error-prone with the given paths/quoting.

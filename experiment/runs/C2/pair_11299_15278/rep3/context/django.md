# Repository Context
## Intent
(accumulating store — emergent arm)
## Constraints
## Evolved Context
- [2026-07-10] In django/db/models/sql/query.py, `_add_q` recurses on child Nodes; when adding a new parameter to `_add_q`/`build_filter`, propagate it through the recursive `_add_q` call and `build_filter` call to keep filter resolution consistent.
- [2026-07-10] The `simple_col` flag threads through the filter machinery (`build_filter`, `_add_q`, `resolve_ref`) to produce `SimpleCol` expressions (defined in django/db/models/expressions.py), used for constraint checks that lack table aliases.
- [2026-07-10] Before scripting text replacements with `assert count==1`, confirm the exact source string; whitespace/argument-order mismatches cause AssertionErrors. Prefer `sed`/verified snippets and re-check with `ast.parse` and `git diff`.

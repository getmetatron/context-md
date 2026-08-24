# Repository Context

## Intent
This is pytest, a Python testing framework whose core behaviors are delivered as internal plugins under `src/_pytest/`, coordinated through a `pluggy` hook system (`hookspec.py`, `hookimpl`). The architecture is a pipeline: an import-time AST transform annotates `assert` statements; a collection tree of `Session`/`Module`/`Class`/`Function` nodes (`main.py`, `python.py`, `nodes.py`) discovers tests; a fixture manager resolves dependency closures and scoping (`fixtures.py`); marks decorate nodes and drive selection/skipping (`mark/`, `skipping.py`); and a report/traceback layer renders failures (`reports.py`, `_code/`). The codebase targets both Python 2 and 3 (uses `six`, `imp`, `atomicwrites`), so any change must preserve dual-version compatibility. Behavior is almost always extended via hooks rather than hardcoding, and durable public contracts (fixture request API, mark semantics, report shape) are relied upon by third-party plugins.

## Constraints

### assertion rewriting
- The rewrite is a PEP 302 import hook, `AssertionRewritingHook` in `src/_pytest/assertion/rewrite.py`, installed onto `sys.meta_path` by `install_importhook` in `src/_pytest/assertion/__init__.py`; `AssertionRewriter.visit_Assert` (rewrite.py:814) replaces each `ast.Assert` with an `if not <cond>: raise AssertionError(<explanation>)` block plus temporary-variable cleanup, then re-fixes line numbers via `set_location`.
- Rewritten code is cached as pyc files tagged `PYTEST_TAG` (rewrite.py:32-46); `_read_pyc`/`_write_pyc` validate against source mtime+size and `imp.get_magic()`, and writes use `atomicwrites`. `_writing_pyc` guards against recursion (see comment referencing infinite-recursion risk). Changing the cache header format or tag will silently invalidate/mis-read caches.
- Only files matching `python_files` (via `_should_rewrite`), `conftest`, and modules passed to `register_assert_rewrite` are rewritten; `_early_rewrite_bailout` short-circuits for speed. Preserve the Python 2 ASCII-encoding check in `_rewrite_test` (rewrite.py:382) and the `is_rewrite_disabled` docstring opt-out, or unicode/opt-out behavior breaks.
- Custom comparison text flows through `pytest_assertrepr_compare` (`util.assertrepr_compare`); `callbinrepr` in `__init__.py` truncates, escapes newlines, and doubles `%` in rewrite mode. `_reprcompare` is a process-global toggled per test, so keep set/teardown symmetric.

### fixtures and parametrization
- `FixtureManager` (`src/_pytest/fixtures.py:1078`) discovers factories with `parsefactories`, builds the dependency `getfixtureclosure`, and resolves definitions via `getfixturedefs`/`_matchfactories` using nodeid prefix matching for scoping. `FixtureRequest`/`SubRequest` drive execution; `FixtureDef.execute` caches by scope and registers finalizers.
- Scope ordering is fixed (`scope2index`/`scopenum`); `reorder_items` (fixtures.py:214) reorders collected items to minimize higher-scoped fixture setups/teardowns. A scope mismatch (a fixture requesting a narrower-scoped one) must raise via `scopemismatch`; never let a broader-scoped fixture depend on a narrower one.
- Parametrization runs during collection: `Metafunc.parametrize` (`src/_pytest/python.py:961`) appends `CallSpec2` entries, and `_genfunctions` expands them into `Function` items. `indirect` routes values through fixtures; `idmaker`/`_idval` generate stable test ids—keep ids deterministic and unique.
- `@pytest.fixture`/`yield_fixture` (fixtures.py:998) define scope/params/autouse/ids/name; `_teardown_yield_fixture` requires exactly one yield. The `request` object's public attributes are a plugin contract.

### test collection and discovery
- `Session` (`src/_pytest/main.py:420`) drives `perform_collect`→`genitems`; directory recursion honors `pytest_ignore_collect`, `norecursedirs`, and `_in_venv`. `PyCollector.collect` and `Module`/`Class`/`Instance`/`Package.collect` (python.py) build the node tree via `pytest_pycollect_makeitem`/`makemodule` hooks.
- File selection uses `python_files`/`python_classes`/`python_functions` ini patterns (python.py `path_matches_patterns`); `_collectfile` deduplicates by path. Collection is hook-driven—extend via `pytest_collect_file`/`pytest_pycollect_makeitem`, not by special-casing names.
- `pytest_collection_modifyitems` (main.py:326 and mark) is the sanctioned post-collection filter/reorder point; mutating `items` in place here is expected and ordering interacts with fixture `reorder_items`.

### marks and skipping
- Marks live in `src/_pytest/mark/`: `MarkGenerator`/`MARK_GEN` and `MarkDecorator`/`Mark` (`structures.py`) attach via `store_mark`/`pytestmark`; `NodeKeywords`/`NodeMarkers` and `iter_markers`/`get_closest_marker` (`nodes.py:185`) expose them. `-k`/`-m` selection is `deselect_by_keyword`/`deselect_by_mark` in `mark/__init__.py`.
- Skip/xfail are evaluated by `MarkEvaluator` in `pytest_runtest_setup` (`src/_pytest/skipping.py:74`): `skipif`/`skip` raise `Skipped`; `xfail` sets `item._evalxfail`. Outcome translation happens in `pytest_runtest_makereport` (skipping.py:126)—strict xfail turns XPASS into failure, and skipif-by-mark rewrites `longrepr` location to the item definition. Preserve these branch semantics.

### error reporting
- Failures become `TestReport`/`CollectReport` (`src/_pytest/reports.py`); `from_item_and_call` (reports.py:345) sets `longrepr` from `item.repr_failure`/`_repr_failure_py`. `nodes.py:243` builds the representation, delegating to `ExceptionInfo.getrepr` in `_pytest/_code/code.py` which respects `tbstyle` (`--tb`) and fulltrace options.
- `longrepr` objects must implement `toterminal`; `reprtraceback`/`reprcrash` are serialized by `pytest_report_to_serializable`/`_from_serializable` (reports.py:419) for xdist—any new failure repr must round-trip through that (de)serialization or distributed runs break.

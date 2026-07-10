# Repository Context

## Intent
Django is a high-level Python web framework (Python 2/3 dual-support era, using `django.utils.six`) whose ORM includes a full schema-migration subsystem under `django/db/migrations/`. The design separates *what* a migration means (in-memory `ProjectState` mutation) from *how* it is applied (per-backend `SchemaEditor`), and treats migration files as generated Python that must round-trip: any object placed in a migration must be able to describe how to reconstruct itself (`deconstruct()`). Backend quirks are isolated behind `django/db/backends/<vendor>/` so generic code never special-cases a database.

## Constraints

### Migration operation optimization/reduction
- The optimizer lives in `django/db/migrations/optimizer.py` (`MigrationOptimizer`), but per-operation merge logic lives in each operation's `reduce()` method — `django/db/migrations/operations/base.py` (`Operation.reduce`), with concrete rules in `operations/models.py` and `operations/fields.py`. Changes to *how two operations combine* belong in the operations' `reduce()`, not in the optimizer loop.
- `optimize()` re-runs `optimize_inner` until a fixed point; therefore every `reduce()` must be stable and return an equal-or-shorter list, or the optimizer loops forever.
- `reduce()` returns a list (replacement) or a boolean (whether the first operation may be optimized *across* the second). Returning True incorrectly reorders operations past ones that depend on them, so correctness hinges on `references_model()` / `references_field()` (`operations/base.py`): "if in doubt, return True" — a false positive only costs efficiency; a false negative produces an unusable optimized migration.
- `Operation.elidable` (base.py) lets base `reduce()` drop an operation entirely; `reduces_to_sql` marks operations (e.g. RunPython) that cannot be squashed to SQL. Respect these flags rather than adding type checks elsewhere.

### Field and expression deconstruction (migration serialization)
- `Field.deconstruct()` is in `django/db/models/fields/__init__.py` (~line 365): returns `(name, import_path, args, kwargs)`. Contract: omit kwargs equal to their defaults, prefer kwargs over positional args, and only emit serializable value types (the docstring enumerates them). Custom-field deconstruction bugs belong here or in the field subclass's override, not in the writer.
- Arbitrary objects (validators, storages, etc.) become serializable via the `@deconstructible` decorator in `django/utils/deconstruct.py`, which captures `_constructor_args` in `__new__` and refuses to serialize objects not importable at module top level (inner classes fail with an explicit error).
- Operations themselves capture `_constructor_args` in `Operation.__new__` (`operations/base.py`) — this is why operations must be treated as immutable: mutating attributes after construction silently desynchronizes what gets written to disk.
- Serialization dispatch is in `django/db/migrations/serializer.py` (`DeconstructableSerializer`, `ModelFieldSerializer`, etc.); file emission is `django/db/migrations/writer.py` (`MigrationWriter`, `OperationWriter`). Fixes about *rendering* a deconstructed value go in serializer.py; fixes about *what* a field reports go in the field's `deconstruct()`.

### Database router compliance
- Router resolution is `ConnectionRouter` in `django/db/utils.py`: `allow_migrate(db, app_label, **hints)` polls each configured router, skips routers lacking the method, and defaults to True if all return None. User routers may accept only `(db, app_label)` — always pass extra data via `**hints`.
- Every schema-touching operation must gate on the router: `Operation.allow_migrate_model()` (`operations/base.py`) wraps `router.allow_migrate_model()` and also rejects proxy/swapped/unmanaged models via `model._meta.can_migrate()`. New operations that skip this check will write DDL to databases the project routed away from.
- `RunSQL` and `RunPython` (`operations/special.py`) have no model, so they consult `router.allow_migrate(connection.alias, app_label, **self.hints)` using their user-supplied `hints` kwarg — preserve this pattern for any model-less operation.
- `MigrationExecutor.detect_soft_applied` (`django/db/migrations/executor.py`) also calls `router.allow_migrate` with `model_name` as a hint; router semantics must stay consistent across executor and operations.

### Namespace-package migrations
- `MigrationLoader.load_disk()` (`django/db/migrations/loader.py`, ~lines 90–110) deliberately treats a migrations module with no `__file__` (a PEP-420 namespace package — "PY3 will happily import empty dirs as namespaces") or no `__path__` (a plain module) as *unmigrated*. It then scans `os.path.dirname(module.__file__)` with `os.listdir`, so migrations dirs must be regular packages with `__init__.py`.
- On the write side, `MigrationWriter.basedir` (`django/db/migrations/writer.py`) resolves the target directory via `module_dir()` in `django/utils/module_loading.py`, which raises `ValueError` for namespace packages split across multiple `__path__` entries; `basedir` then falls back to app-relative paths and finally creates missing packages *with* `__init__.py` files. Changes to where migrations are discovered belong in loader.py; changes to where they are written belong in writer.py — keep the two consistent.

### SQLite schema alteration
- SQLite ALTER TABLE support is minimal, so `DatabaseSchemaEditor` in `django/db/backends/sqlite3/schema.py` implements nearly every change (`add_field`, `remove_field`, `_alter_field`, `_alter_many_to_many`) by delegating to `_remake_table()`: rename old table, create new table, `INSERT ... SELECT` the data, drop the old table. SQLite alteration fixes belong in this file, not in `django/db/backends/base/schema.py`.
- `__enter__`/`__exit__` force `PRAGMA foreign_keys = 0` for the editor's duration (the default can be changed by build flags, so it is enforced explicitly) and restore the prior value afterward — table remakes would otherwise trip FK constraints mid-copy.
- `_remake_table` clones self-referential fields so their `remote_field.field_name` doesn't point at an altered field, and handles PK handoff when a new PK is introduced. M2M fields are special-cased: implicit through tables are created/dropped, explicit `through` removal is a no-op.
- `quote_value()` here manually emulates SQLite literal quoting (bool/int/str/bytes-as-`X'..'` hex) because remade-table SQL inlines defaults; sqlite3-module availability is optional by design.
- `django/db/backends/sqlite3/features.py` sets `can_rollback_ddl = True` and `atomic_transactions = False`; don't assume MySQL-like non-transactional DDL in SQLite-specific code.

## Evolved Context
<!-- populated over time as agents learn from working in this repository -->

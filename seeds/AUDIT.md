# Seed-authoring audit (PREREGISTRATION §4.5)

**Date:** 2026-07-09. Seeds for conditions E/G-adjacent use, authored AFTER the `prereg-v1` freeze.

## Procedure
Each `seeds/<repo>/context.md` was authored by a **fresh Claude Opus 4.8 subagent session** with no prior exposure to any SWE-bench instance, problem statement, gold patch, or test. Inputs given to each author:
1. A code checkout at the earliest base commit among that repo's study instances (FINDINGS-02 set), with `.git` removed so no post-checkout history was accessible:
   - django @ `f8fab6f9` (2016-11), sphinx @ `aca3f825` (2020-04), xarray @ `1757dffa` (2019-07)
2. The constraint-group topic NAMES only (no descriptions, no instances).
3. Hard prohibitions: no web access, no reads outside the checkout, no git, no references to bugs/issues/benchmarks.

The orchestrating session (which HAS seen instances) performed review only — format check, word count, module-path spot check, and a leakage scan (`#NNNN`, issue/ticket/benchmark tokens) — and made no content edits. Zero edits were required.

## Consulted-file lists (self-reported by each author)
- **django**: optimizer.py, operations/{base,models,fields,special}.py, loader.py, writer.py, serializer.py, executor.py, models/fields/__init__.py, models/expressions.py, utils/deconstruct.py, utils/module_loading.py, db/utils.py, backends/sqlite3/{schema,features}.py
- **sphinx**: ext/autodoc/{typehints,mock,__init__,type_comment}.py, domains/python.py, util/typing.py (+ existence checks: util/inspect.py, pycode/ast.py, ext/autodoc/{importer,directive}.py)
- **xarray**: core/{options,dtypes,variable,dataset,dataarray,computation,merge,coordinates,duck_array_ops,nanops,utils}.py

## Known limitation (conservative)
Checkouts are at the EARLIEST instance's base commit (per frozen §4.5); most study instances postdate them by years (django especially: 2016 checkout vs 2019–2023 instances). Module layouts may have drifted, making some localization facts stale for later instances. This biases AGAINST the treatment (stale seed knowledge), i.e., in the conservative direction for H1/H2/H4.

## Convergence note (informational, not analysis)
Without instance exposure, the blind authors independently identified the same machinery the FINDINGS-02 constraint clusters center on (e.g., `_get_keep_attrs` in xarray options.py; `_parse_annotation` in sphinx domains/python.py; the `reduce()` contract in django operations). This is evidence the topic names alone do not leak instance solutions — the knowledge is derivable from the codebase, which is the premise of the distillation arm.

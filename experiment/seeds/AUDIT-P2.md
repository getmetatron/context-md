# Seed-authoring audit — Paper 2 expansion repos (supplement to AUDIT.md)

**Date:** 2026-07-15. Five new seeds for the Paper 2 instance pool, authored under the
frozen Paper 1 protocol (AUDIT.md §Procedure) BEFORE the prereg2-v1 freeze: fresh
Claude Opus subagent per repo, no exposure to any instance/problem/gold patch; checkout
at the earliest study-instance base commit with `.git` removed; topic names only; no
network, no reads outside the checkout; orchestrator performed format check + leakage
scan only (zero content edits required on all five).

| repo | checkout | words | topics | consulted (author-reported) |
|---|---|---|---|---|
| sympy | 360290c4c4 (2016-09) | 715 | printing/LaTeX; simplify | printing/{printer,latex,conventions,precedence,str,codeprinter}.py; simplify/{simplify,fu,trigsimp}.py |
| matplotlib | a3e2897bfa (2019-04) | 683 | units/axis; colormap/norm | units.py, axis.py, axes/_base.py, category.py, dates.py; colors.py, cm.py, scale.py |
| scikit-learn | 3eacf948e0 (2017-07) | 600 | estimator API; input validation | base.py; utils/{validation,estimator_checks}.py |
| astropy | 26d147868f (2018-02) | 637 | io registry; units/quantities | io/registry.py, io/fits/connect.py; units/{core,quantity,quantity_helper}.py |
| pytest | 58e6a09db4 (2019-05) | 602 | 5 canonical subsystems | assertion/{__init__,rewrite,util}.py, fixtures.py, python.py, main.py, nodes.py, skipping.py, mark/*, reports.py, _code/code.py |

Topic-name sources: FINDINGS-01 cluster themes (4 repos); pytest has no FINDINGS-01
cluster, so topics are its five canonical subsystem names (assertion rewriting,
fixtures/parametrization, collection/discovery, marks/skipping, error reporting) —
derivable from the project's own documentation, not from instances.

Same conservative staleness bias as Paper 1: checkouts predate most study instances
by years, which biases against the treatment arms.

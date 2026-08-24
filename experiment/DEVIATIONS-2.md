# Deviations from prereg2-v1

- 2026-07-15 — **Operational only, no analytical effect:** added `--skip-existing`
  to `harness/run_condition.py` and `harness/resume_matrix.sh` so the matrix can
  resume after machine shutdowns. Completed episodes are never re-run or
  double-counted; interrupted episodes leave no partial logs. All Paper 2 arms are
  non-accumulating, so episode order/timing cannot affect outcomes. No prompt,
  metric, detector, or analysis change.

- 2026-07-16 — **Error-handling fix, applied symmetrically to all arms:** an agent
  command exceeding the 120s cap raised an unhandled `subprocess.TimeoutExpired`,
  crashing the whole condition run (hit during FILE rep1 after 74 episodes; the
  crashed episode wrote no log, so no recorded data is affected). Command timeouts
  are now returned to the agent as a failed turn (exit 124, TIMEOUT message) —
  the same recoverable-error semantics as any nonzero exit. Interrupted episodes
  were re-run via the pre-registered resume path (`--skip-existing`).

## 2026-07-19 — B/E arms contain 10 instances outside the frozen list

The B and E condition runs (launched first) each contain 277 instances per
rep; the frozen list (prereg2-v1, harness/instances_paper2.json) has 267 —
the 10 extras predate the final pilot-decontamination pass. Resolution:
`analysis/analyze_p2.py` restricts every analysis to the frozen 267-instance
list; the extra episodes are ignored (never pooled). Operational, symmetric
(exclusion applies identically to all arms), decided before any confirmatory
test was run on the full matrix.

## 2026-07-20 — B/E resolve evals re-run under P2-prefixed run_ids

eval_all.py's resume dedup keys on run_id; Paper 1 already consumed
`eval-B-rep{1..3}` / `eval-E-rep{1..3}`, so the Paper 2 B/E predictions were
silently skipped in the first eval pass. Re-evaluated under
`eval-P2-{B,E}-rep{1..3}` (harness/eval_p2_be.py), restricted to the frozen
267-instance list, duplicates dropped. Operational; resolve is a registered
secondary with no confirmatory claim at this tier.

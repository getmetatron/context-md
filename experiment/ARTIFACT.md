# Artifact: The Repository Context Layer — pre-registered evaluation

This artifact accompanies the paper's Section 10 (Empirical Evaluation). It
contains the frozen
pre-registration (`PREREGISTRATION.md`, git tag `prereg-v1`), the experiment
harness, blind seed-authoring audit trails (`seeds/AUDIT.md`), all episode
predictions and promotion logs (`runs/`), all evaluation verdicts
(`runs/eval_summary.jsonl`), and one-command reproduction of the paper's reported numbers
(Tier 1 and Tier 1b together). The completed consultation-detector sample, key,
row-level evidence, and author-verification record are under `audit/`.

Archived release: [version 1.0.0](https://doi.org/10.5281/zenodo.22122045),
corresponding to annotated git tag `v1.0-agenticdev2026-artifact`.

## Pre-registration provenance

The protocol was frozen and tagged before any confirmatory run. Verify directly:

    git show prereg-v1
    git show prereg-v1:PREREGISTRATION.md

| | |
|---|---|
| tag | `prereg-v1` (annotated) |
| commit | `056156679a896f0697198bb240c92110aa2df048` |
| date | 2026-07-09 13:05:27 +0300 |

Every confirmatory run in `runs/` postdates this commit; the pilots
(`FINDINGS-01..05`) predate it and are excluded from confirmatory analysis.
Post-freeze deviations are recorded in `DEVIATIONS.md`, as required by
`PREREGISTRATION.md` §12.

### Provenance caveat for the delivery study (Paper 2)

The delivery study's protocol text (`PREREGISTRATION-PAPER2.md`) is included here,
but its freeze tag `prereg2-v1` is **not part of this public repository** and
cannot be independently verified from this artifact. Two limitations follow, and
both are stated rather than glossed:

1. The tag exists only in the authors' private experiment repository. It is not
   published, because that repository's history contains unrelated private work.
2. It is a **lightweight** tag, so it carries no tagger timestamp of its own —
   unlike `prereg-v1`, which is annotated and independently dated.

What can be checked from the released data: the tagged commit is dated
2026-07-15, and every containerized evaluation verdict for the delivery arms in
`runs/eval_summary.jsonl` is timestamped 2026-07-19 or later — four or more days
afterwards. That is corroboration, not proof. Treat Paper 1's provenance
(`prereg-v1`, annotated, public, verifiable here) as strong and Paper 2's as
weaker.

## Tier 1 — Reproduce the paper's numbers (~1 minute, no network)

Recomputes the 15 empirical claims underlying Section 10.2--10.3 (Figures 2--3)
from the committed raw data and verifies each against the value printed in the
paper:

    make reproduce-paper          # local Python 3.12+, pip install -r requirements-artifact.txt
    make docker-reproduce         # or fully containerized

Expected output ends with: `15/15 claims reproduced`. Statistics are exact
(fixed-seed permutation tests), not approximate.

## Tier 1b — Verify the camera-ready additions (~1 minute, no network)

Checks the numbers introduced or corrected for the camera-ready that
`reproduce_paper.py` does not assert — the blind-seed leakage audit, the
broad-sample ceiling, the delivery-matrix token figures, the per-group direction
counts, and the Holm-adjusted frontier p-value:

    python paper/camera-ready-agenticdev2026/analysis/verify_claims.py

Expected output ends with: `all checked camera-ready claims verified`.

    python paper/camera-ready-agenticdev2026/analysis/seed_leakage.py   # leakage audit alone
    python paper/camera-ready-agenticdev2026/analysis/make_figures.py   # regenerate Figures 1-5
    python analysis/consultation_audit_analyze.py \
      --audit audit/consultation-hand-audit-40.csv \
      --key audit/consultation-hand-audit-40.key.csv                    # detector verification

The consultation audit gives 40/40 raw agreement for consultation, deep read,
and read-before-edit (38 positive, 2 negative; mechanical kappa 1.000). An author
manually reviewed every row against transcript evidence. The evidence packet and
candidate labels were AI-prepared, and the author was not blinded to the detector
output, as disclosed in `audit/CONSULTATION-HUMAN-VERIFICATION.md` and
`DEVIATIONS-2.md`; this is descriptive confirmation, not independent inter-rater
reliability.

## What runs offline, and what needs external access

| tier | needs |
|---|---|
| Tier 1, Tier 1b | nothing beyond Python + `requirements-artifact.txt`. No network, no model, no API key. |
| Tier 2 | Ollama with `gemma4:e4b` for the local executor; `ANTHROPIC_API_KEY` for a frontier episode; Docker for official SWE-bench evaluation. |
| Tier 3 | as Tier 2, at full-arm scale. |

The values reported in Sections 10.2--10.6, Tables 3--4 and Figures 2--5 are
recomputed at Tier 1 / Tier 1b from the committed data. Both entry points fail
if an expected outcome is unsupported: completed runs require their prediction
and evaluation records, while the two pre-record aborts require matching nonzero
runner outcomes in `runs/batch_frontier2.log`. Tiers 2
and 3 re-run agents and therefore require model access; frontier episodes are not
bit-reproducible (see Reproducibility notes).

## Tier 2 — Run one episode end-to-end (~10–30 minutes)

Runs one agent episode through the harness, then scores it with the official
SWE-bench Docker images:

    make episode                  # local executor: requires Ollama + `ollama pull gemma4:e4b`
    make evaluate-episode         # requires Docker; pulls the official arm64/x86 eval image

For a frontier-executor episode, set `ANTHROPIC_API_KEY` and use
`--condition A`. Conditions map to the paper as: A/B controls, C/D emergent
lifecycle, E blind seed, `--oracle` the labeled upper bound (see
`PREREGISTRATION.md` §2).

## Tier 3 — Re-run a full arm (hours)

    python harness/run_batch.py --pairs harness/pairs_tier1.json --arms B E Do --reps 1 --round R
    python harness/eval_all.py

`--round` isolates reruns under `runs/*R` so committed artifacts are never
overwritten.

## Reproducibility notes (read before comparing fresh runs to the paper)

- **Tier 1 is the primary reproduction path.** It is bit-exact from committed
  data on any platform.
- **Local executor:** `gemma4:e4b` served by Ollama, temperature 0, fixed
  seeds, `think` off, `num_ctx` 32768, `num_predict` 2048 (frozen in
  `harness/run_condition.py`). Same weights + same Ollama version reproduce
  episodes closely but quantized-inference determinism across hardware is not
  guaranteed.
- **Frontier executor:** API models are not bit-reproducible; the paper's
  design absorbs this with repetitions. All completed frontier episode
  transcripts are committed under `runs/` for audit. Two planned no-context
  attempts terminated before producing an episode record; their nonzero runner
  outcomes are retained in `runs/batch_frontier2.log` and scored unresolved in
  the frozen full-denominator analysis.
- **Evaluation** uses the *official* SWE-bench images
  (`--namespace swebench`); locally built images have recipe drift (see
  `harness/README.md`).
- Episode `work/` trees and scratch logs are excluded from the artifact;
  everything an analysis touches is committed.

## Layout

    PREREGISTRATION.md      frozen protocol (tag prereg-v1; pilots excluded from confirmatory analysis)
    FINDINGS-01..05.md      feasibility pilots and design checks (pre-freeze)
    DEVIATIONS.md           post-freeze deviations for prereg-v1 (PREREGISTRATION.md §12)
    DEVIATIONS-2.md         post-freeze deviations for prereg2-v1 (delivery study)
    PREREGISTRATION-PAPER2.md  protocol for the delivery study (see provenance caveat below)
    FINDINGS-01..08.md      feasibility pilots and design checks (pre-freeze)
    RESULTS-01..06.md       confirmatory results as they accrued
    audit/                  completed consultation-detector sample, key, evidence and author verification
    seeds/                  blind-authored context files + authoring audit (AUDIT.md, AUDIT-P2.md)
    harness/                condition runner, batch orchestrator, promotion rubric, frozen prompts
    runs/                   predictions, episode logs, runner outcomes, promotion decisions, eval verdicts, analysis CSVs
    analysis/               power simulation, reproduce_paper.py, analyze_p2.py
    paper/camera-ready-agenticdev2026/
                            camera-ready source; analysis/ holds the blind-seed
                            leakage audit, verify_claims.py and make_figures.py

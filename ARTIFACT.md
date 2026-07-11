# Artifact: The Repository Context Layer — pre-registered evaluation

This artifact accompanies the paper's Section 11. It contains the frozen
pre-registration (`PREREGISTRATION.md`, git tag `prereg-v1`), the experiment
harness, blind seed-authoring audit trails (`seeds/AUDIT.md`), all episode
predictions and promotion logs (`runs/`), all evaluation verdicts
(`runs/eval_summary.jsonl`), and a one-command reproduction of every number
in the paper.

## Tier 1 — Reproduce the paper's numbers (~1 minute, no network)

Recomputes all 15 empirical claims (Figures 2–3 and Section 11.2) from the
committed raw data and verifies each against the value printed in the paper:

    make reproduce-paper          # local Python 3.12+, pip install -r requirements-artifact.txt
    make docker-reproduce         # or fully containerized

Expected output ends with: `15/15 claims reproduced`. Statistics are exact
(fixed-seed permutation tests), not approximate.

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
  design absorbs this with repetitions. All frontier transcripts are committed
  under `runs/` for audit.
- **Evaluation** uses the *official* SWE-bench images
  (`--namespace swebench`); locally built images have recipe drift (see
  `harness/README.md`).
- Episode `work/` trees and scratch logs are excluded from the artifact;
  everything an analysis touches is committed.

## Layout

    PREREGISTRATION.md      frozen protocol (tag prereg-v1; pilots excluded from confirmatory analysis)
    FINDINGS-01..05.md      feasibility pilots and design checks (pre-freeze)
    RESULTS-01..04.md       confirmatory results as they accrued
    seeds/                  blind-authored context files + authoring audit
    harness/                condition runner, batch orchestrator, promotion rubric, frozen prompts
    runs/                   predictions, episode logs, promotion decisions, eval verdicts, analysis CSVs
    analysis/               power simulation + reproduce_paper.py

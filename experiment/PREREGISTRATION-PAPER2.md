# Pre-registration (FROZEN, prereg2-v1, 2026-07-15) — Delivery mechanisms for a repository context layer

**Status: FROZEN at tag `prereg2-v1`.** No changes without a DEVIATIONS-2.md entry — same discipline as Paper 1.

## §1 Design

Between-arm comparison of context **delivery mechanisms** with content held constant (frozen Paper 1 E-arm seeds, `seeds/*/context.md`, audit in `seeds/AUDIT.md`). Arms B (none), I (injected), F (file + shipped consult-first contract), S (sharded OKF store + L2 discovery + same contract). Full mechanics: PAPER2-DESIGN §2.

## §2 Executors and tasks

Executor: gemma4:e4b (sole executor; qwen2.5-coder:7b piloted and dropped pre-freeze — FINDINGS-07), via Ollama, temp 0, num_ctx 32K, num_predict 2048, 20-turn cap — Paper 1 local-tier scaffold, unchanged. Arms as harness conditions: B (none), E (= arm I, injection), FILE, SHARD; contract text = metatron 0.12.0 _ROOT_BLOCK['pr'] verbatim (harness/templates_p2.py). Tasks: 267 SWE-bench Verified instances across 8 repos (sha256-deterministic selection, django and sympy capped at 60, Paper 1 pair instances and all 2026-07-15 pilot instances excluded), 3 reps per instance×arm; the exact list is frozen in `harness/instances_paper2.json`. **Registered extension module (not part of the primary analysis):** a SWE-bench-Live stratum (~50 post-2024 instances, top Python repos, seeds authored under the AUDIT protocol) to be run after the primary matrix as the contamination check; its results will be reported separately and labeled as the extension. No learning phase; episodes independent.

## §3 Primary hypotheses and tests

- **H1 (RQ1):** consultation rate under F and S is ~100% (point prediction 1.00, band 0.90-1.00) under the shipped 0.12.0 procedural contract — FINDINGS-08: 20/20 across dev + held-out incl. an unseen repo; deep-read rate predicted equal to consultation rate.
- **H2 (RQ2):** gold-file-hit deltas F−B, S−B, I−B, F−I; sign-flip permutation on per-instance×rep paired deltas, 10k draws, seed 42, Holm within the 4-test family. Confirmatory claim requires Holm-corrected p < .05.
- **H3 (RQ3):** context-tokens-paid contrasts S < F < I; same permutation machinery, own Holm family.
- **H4 (RQ4):** outcome conditional on consultation — **exploratory only** (post-treatment conditioning), labeled as such in the paper.

Empty patches count as gold-miss (Paper 1 §6 formula). Resolve rate reported secondary; no confirmatory resolve claim at this tier (Paper 1 pooled null, RESULTS-04).

## §4 Consultation detector (fixed before freeze)

An episode counts as *consulted* iff a command reads a context artifact (STRICT_READ_RE in `harness/templates_p2.py`, frozen, 6 unit tests in `tests_p2/`), with `read_before_edit` and `deep_read` (DEEP_READ_RE: contents of context.md or a decision file entered the transcript) reported alongside; 40-episode random hand-audit reported with Cohen's κ. Context-tokens-paid: I = tokenized injected block; F/S = tokenized context-file content echoed into the transcript by read commands tokenizer proxy = words x 4/3, identical to the frozen prereg-v1 §4.1 cap accounting (consistency across papers beats per-executor precision).

## §5 Artifacts under test

F/S artifacts are byte-identical to `metatron context setup` output at Metatron ⟨version at freeze, ≥0.11.0⟩, default config (`review_gate = "pr"`). Contract text = the shipped AGENTS.md block, verbatim, in the system prompt ⟨plus strong-contract variant iff FINDINGS-06 shows consultation < ⟨10⟩%⟩.

## §6 Exclusions, floors, integrity

- Episode aborts (loop-format failure) excluded symmetrically across arms; rate reported per arm.
- Per-episode checkout reset verified (F/S write into the working tree; leakage between reps invalidates the rep — automated check, failures logged and the rep re-run).
- Zero remote-API calls in the execution path (re-verify at freeze; Paper 1 threat §10.5).
- MDE (analysis/power_sim.py re-run 2026-07-15, 267 instances x 3 reps, baseline gold-hit 0.21): power 0.97 at +8 pp, 0.69 at +5 pp -> MDE ~ +7-8 pp at 90% power. Paper 1 pooled injection effect was +26 pp, so the design detects even a 3x-attenuated file-delivery effect.

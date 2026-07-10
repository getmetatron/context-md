# Pre-registration — Does a Repository Context Layer improve agent performance?

**Version:** 1.0 — 2026-07-09
**Status:** FROZEN at git tag `prereg-v1`. Pilot runs (FINDINGS-03/04/05, feasibility only) predate the freeze and are excluded from all confirmatory analysis. Any post-freeze deviation is logged in `DEVIATIONS.md` (§12).

---

## 1. Research questions and hypotheses

**RQ1 (assist).** Does a seeded repository context layer improve agent task performance on SWE-bench instances?
**H1:** Resolve rate is higher and tokens-per-instance lower with a seeded `context.md` than without.

**RQ2 (transfer — flagship).** Does a decision learned from failing task A improve performance on a *different* task B sharing the same underlying constraint?
**H2:** Treatment (context carrying the A-derived decision) outperforms control (no context) on held-out B instances, for pairs pre-registered in FINDINGS-02.

**RQ3 (accumulation).** Does an accumulating context layer yield growing advantage across a within-repo task sequence?
**H3:** The treatment−control performance gap increases with sequence position (positive interaction term).

**RQ4 (capability gradient / distillation).** Is the context layer's benefit larger for a weaker executor, and can a frontier-authored context close part of the weak executor's gap?
**H4a:** Effect size (treatment−control) is larger for the local model than the frontier model.
**H4b:** Local executor + frontier-authored context (E) > local executor alone (B), with E's gain ≥ half of E's own self-seeded gain (F). (Directional; the E-vs-F comparison is exploratory.)

**Falsifiability.** If treatment−control deltas are indistinguishable from zero at the pre-registered MDE (§8), we will report the null.

## 2. Conditions (fractional matrix)

| ID | Executor | Context | Author of context |
|----|----------|---------|-------------------|
| A | frontier | none | — |
| B | local | none | — |
| C | frontier | emergent (accumulating) | self |
| D | local | emergent (accumulating) | self |
| E | local | seeded | frontier |
| F | local | seeded | local |
| G | local | seeded | human (from repo ADRs/docs) |

Models: frontier = Claude Opus 4.8 (`claude-opus-4-8`) via API — sampling parameters are N/A (rejected by the model); non-determinism is handled by repetitions plus full transcript release. Local = `gemma4:e4b` via Ollama — temperature 0, num_ctx 32768, num_predict 2048, think off, weights digest recorded at first confirmatory run. Secondary local tier (`qwen2.5-coder:7b`) optional, exploratory only.

**Executor scaffold** is identical across all conditions (mini-swe-agent or equivalent minimal loop; frozen at tag). The ONLY difference between arms is the presence/content of the context layer.

## 3. Materials

- **Benchmark:** SWE-bench Verified (primary), instances and difficulty labels as distributed by princeton-nlp (datasets cached 2026-07-09, `data/swebench_verified.parquet`).
- **Repos:** django, sphinx, xarray (transfer study); + sympy, scikit-learn (assist/accumulation only).
- **Transfer pairs:** exactly the groups in `FINDINGS-02-confirmed-transfer-pairs.md` (frozen with this document). Tier-1 groups are confirmatory; Tier-2 confirmatory for RQ2 pooled analysis; any pair added later is exploratory and labeled as such.
- **Dedupe rule:** each instance belongs to at most one constraint group (assignment frozen in FINDINGS-02).
- **Difficulty stratification (frontier tier):** FINDINGS-05 measured a frontier ceiling on easy instances (9/10 unaided gold-file rate). Frontier-executor cells (A, C) must include ≥50% instances labeled `15 min - 1 hour` or harder; local-executor cells may weight toward easy instances per the floor-effect mitigation.

## 4. Procedures

### 4.1 Consultation mechanics (fixed across all arms)
- `context.md` discovered per RCL spec §5 (root `context.md`), injected **in full** into the system prompt, after the scaffold's task preamble, verbatim.
- Hard cap: 4,000 tokens. If the accumulated file exceeds the cap, the harness truncates the Evolved Context ledger oldest-first (Intent and Constraints are never truncated). Truncation events are logged and reported.
- Control arms receive an identical prompt with the context block absent (no placeholder text).

### 4.2 Emergent learning loop (C, D)
After each instance attempt, the executor is prompted (fixed template, frozen at tag) to write **candidate** entries describing durable, repo-general lessons from its own observations. Inputs available to this step: the agent's own transcript, its own test/reproduction output, its final patch. **Never available:** the gold patch, the hidden FAIL_TO_PASS/PASS_TO_PASS tests, resolution status.

### 4.3 Oracle-taught arm (transfer study upper bound)
A separate labeled arm where the learning step additionally sees the gold patch of instance A (never of B). Reported as an upper bound, never pooled with self-taught results.

### 4.4 Promotion rubric (candidate → decision) — mechanical, no human judgment per-item
A candidate is promoted iff ALL hold:
1. States a rule or fact about the repository in general terms (imperative or declarative).
2. Contains no instance identifier, issue number, or reference to "this task".
3. Cites no specific line number; file/module references are allowed.
4. ≤ 60 words.
Rubric applied by a deterministic checker (regex + length) plus a fixed-prompt LLM verifier for criterion 1; verifier prompt frozen at tag; all promotion decisions logged. **Ablation (exploratory):** auto-promote-all.

### 4.5 Seeding (E, F, G)
Author model receives: repo checkout at the *earliest* base commit used by that repo's instances, its docs/CONTRIBUTING/ADRs, and the constraint-group *names only* (e.g., "attribute handling") — **never** problem statements, gold patches, or tests of any benchmark instance. Output: a `context.md` per repo, frozen before any executor run. G is assembled by the human authors from repo documentation under the same blindness rule.

### 4.6 Sequencing (RQ3)
Within-repo chronological order by `created_at` (ecologically valid). Robustness check: 3 additional random permutations per repo (exploratory).

### 4.7 Transfer protocol (RQ2)
For each ordered pair (A, B) in a group: treatment runs A (with learning loop), promotes per §4.4, then runs B consulting the resulting context. Control runs B with no context. Same executor, same scaffold, same reps. B's learning output is discarded (no chaining within RQ2).

### 4.8 Repetitions
Local arms: 5 reps per instance per condition (fixed seeds 1–5). Frontier arms: 3 reps. A rep = full independent run from fresh container.

## 5. Leakage guards (hard rules)
1. Hidden grading tests and gold patches never enter any executor or learning prompt (except §4.3's labeled oracle arm, A-side only).
2. Seeding is blind to all benchmark instances (§4.5).
3. Emergent learning uses only the agent's own observations (§4.2).
4. Harness asserts these by construction; prompt logs are archived for audit.

## 6. Metrics
**Primary:** resolve rate (SWE-bench harness verdict); total tokens per instance (prompt+completion).
**Secondary:** wall-clock; agent turns; wrong-file-edit rate (edited files ∩ gold-patch files = ∅); constraint-violation rate for the pair's constraint, scored blind by fixed-prompt LLM judge with 20% human double-scoring (report agreement); count/quality of promoted decisions.
**Study-2 additionally:** metrics as a function of sequence position.

## 7. Analysis plan
- Mixed-effects logistic regression for resolve: `resolved ~ condition + (1|instance) + (1|repo)`; tokens via linear mixed model on log(tokens).
- RQ2: paired analysis per (A,B) pair; McNemar on paired reps + mixed-effects with pair as random effect.
- RQ3: `resolved ~ position × condition + (1|instance) + (1|repo)`; H3 tests the interaction.
- Report odds ratios / standardized effects with 95% CIs. No p-value thresholding narrative; estimation-first.
- Multiple comparisons: RQ1–RQ4 are 4 confirmatory families; Holm correction within each family.

## 8. Power / minimum detectable effect
Monte-carlo simulation (`analysis/power_sim.py`, seed 42; paired sign-flip permutation test, Beta(κ=10) pair heterogeneity, α=.05, power .8):

| pairs | reps | resolve MDE (p0=.05/.10/.20) | wrong-file MDE (p0=.80) |
|---|---|---|---|
| 15 | 5 | 17.5 / 20.0 / 25.0 pp | 25.0 pp |
| 25 | 5 | **12.5 / 15.0 / 17.5 pp** | **17.5 pp** |
| 40 | 5 | 10.0 / 12.5 / 12.5 pp | 12.5 pp |

Plan: ≥25 confirmatory pairs (Tier-1+2, FINDINGS-02), extendable to 40 by expanding Tier-2. The pilot A/B (FINDINGS-04, non-confirmatory) observed a wrong-file reduction of ~50 pp on precise-context instances — well above the 17.5 pp MDE; effects a third of pilot size remain detectable.
**Budget (measured, FINDINGS-05):** frontier ≈ $0.15/episode (24K tokens avg on easy instances; assume 2–3× on stratified harder instances). Full frontier cells (A+C, ~480 episodes) ≈ $75–200. Local cells ≈ 28 GPU-hours. Frontier reps may be raised from 3 to 5 within budget if observed variance warrants; this decision must be made before unblinding any confirmatory comparison.
**Pivot (activated by FINDINGS-03):** local-tier resolve floor confirmed ≤2/10 on easy instances; for the local tier, primary RQ2 metrics are wrong-file-edit rate and constraint-violation rate, with resolve rate secondary. Frontier tier keeps resolve primary.

## 9. Exclusions
- Runs failing for infrastructure reasons (container crash, OOM, API outage) are re-run with the same seed; both events logged.
- Instances whose environment fails to build in the SWE-bench harness are excluded benchmark-wide (all arms), listed in the artifact.
- No per-result exclusions of any other kind.

## 10. Threats to validity (disclosed)
1. **Training contamination:** both models have likely seen these repos and possibly gold patches. Mitigated by within-model A/B on identical instances; contamination affects both arms symmetrically. Residual: contamination may compress deltas toward zero (works against H1–H4, not for them).
2. **Keyword-derived groups:** constraint groups were identified partly by keyword search; mitigated by manual confirmation (FINDINGS-02) done before any run.
3. **Scaffold sensitivity:** results may not generalize beyond the chosen scaffold; disclosed, one scaffold only.
4. **Frontier API non-determinism:** exact replication impossible; mitigated by 3 reps + full transcript release.
5. **Anthropic-API dependency in metatron:** local-only arms must be verified to make zero frontier API calls (network egress blocked in local-arm containers except Ollama host).

## 11. Reproducibility artifact
Docker image per condition (SWE-bench per-instance images + `pip install getmetatron` + harness), pinned model weights digest for Gemma, all prompts/templates/seeds in-repo, all transcripts + JSONL run logs released. One-command replication: `docker run … --condition E --instance <id> --seed 1`.

## 12. Deviations
Any deviation after freeze is logged in `DEVIATIONS.md` with date and rationale, and reported in the paper.

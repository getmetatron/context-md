# Paper 2 — Design doc: Consultation compliance and token economics of a git-native context layer

**Status:** DRAFT (kickoff 2026-07-15, ahead of the ~Sep 1 roadmap date). Not frozen.
**Working title:** *Does the Agent Actually Read the Files? Delivery, Compliance, and Token Economics of a Repository Context Layer*
**Target venue:** MSR 2027 technical track (git-native is their core topic; ~Jan–Feb 2027 deadline). Fallback: ICSE 2027 LLM4Code-style workshop.
**Relation to Paper 1:** Paper 1 (AgenticDev #22) established *whether* repository context helps and *who must author it* (author capability > executor capability; +26 pp localization pooled, p<10⁻⁴). Paper 2 holds the winning context **content constant** and varies only the **delivery mechanism** — the axis Paper 1 deliberately fixed at prompt injection.

## 1. Research questions

- **RQ1 (compliance/existence).** Under the shipped Metatron contract (AGENTS.md consult-first block + `context.md` entry point), do local executors consult repository context files unprompted? Primary metric: **consultation rate** — fraction of episodes where the transcript shows a read of a context file (`cat`/`grep`/`sed -n` on `context.md` or `context/**`) before the first file edit.
- **RQ2 (delivery gap).** How much of the injection ceiling's benefit survives when context must be *pulled* by the agent instead of *pushed* into the prompt? Outcome: gold-file hit (localization), as in Paper 1's local tier.
- **RQ3 (token economics).** Does file-based delivery reduce context cost? Injection charges the full payload every episode; contract-read charges only what the agent reads, only when it reads. Sharding should cut payload further (read one relevant shard, not the monolith) at the risk of discovery misses. Metrics: context tokens actually paid per episode (prompt-side tokens attributable to context reads / injected block) and total episode tokens.
- **RQ4 (mediation).** Is the delivery-arm effect concentrated in episodes that consulted? Analyze outcome conditional on consultation (complier-style analysis, exploratory — consultation is post-treatment).

The headline the study is designed to earn (or refute): *"pull beats push"* — file-based delivery retains most of the localization benefit at a fraction of the token cost. The honest risk it must also be able to report: local models simply never read the files, in which case the shipped default fails for small executors and the paper becomes a compliance study with design implications (contract strength, placement).

## 2. Arms (delivery mechanisms; content identical everywhere)

Context content in all treated arms = the **frozen Paper 1 E-arm frontier seeds** (`seeds/{django,sphinx,xarray}/context.md`, 589–830 words, `## Intent` + `### topic` constraint sections). No learning phase, no chaining — content is a constant, so every instance is an independent episode.

| Arm | Delivery | Mechanics |
|---|---|---|
| **B** | none (control) | Paper 1 arm B, re-run in the same batch (fresh baseline, same harness version) |
| **I** | injection (ceiling) | Paper 1 CONTEXT_BLOCK mechanics: full seed in the system prompt, 4K-token cap |
| **F** | file + contract | Seed written to `context.md` in the repo working tree; system prompt carries only the shipped consult-first contract (the `metatron context setup` AGENTS.md block, verbatim), pointing at the file. Nothing injected. |
| **S** | sharded OKF + discovery | Seed split into `context/decisions/<topic>.md` (one OKF file per `### topic` section, shipped frontmatter) + a thin `context.md` index listing files with one-line descriptions (L2 discovery). Same contract as F. Nothing injected. |

Notes:
- **No MCP arm** (files-first direction; decided 2026-07-14). Reserved as a follow-up study (ROADMAP "Paper 3"): the fixed-content/varied-delivery frame means an MCP-served arm composes directly with these results later, without rerunning B/I/F/S.
- Study configuration = Metatron **as shipped, default config** (`review_gate = "pr"`); the F/S artifacts are produced by (or byte-identical to) `metatron context setup` output — no experiment-only flags to defend.
- The contract text is a controlled constant. If the pilot shows ~0% consultation, contract strength becomes a **pre-registered secondary factor** (weak = shipped block; strong = adds an explicit "your first command must read context.md" line) rather than a post-hoc tweak. Decide at freeze, on pilot evidence.
- **Contract wording v1→v2 (2026-07-15).** The existence check caught an agent satisfying "read the relevant files" with a directory listing (steering off shard *filenames*, never opening one). Fix shipped as metatron 0.11.1 (PR #116): every managed artifact now says consultation means opening the files. The confirmatory study runs on the **0.12.0 procedural text** (v3, PR #117 — validated 20/20 consult+deep-read incl. a held-out repo, FINDINGS-08); the v1/v2/v3 pilot cells go in the paper as a design-iteration note — a live example of the artifact's wording being load-bearing, and of the feedback loop the tool itself is meant to enable (agent behavior → observed gap → reviewed product change → measured effect).

## 3. Executor (local only — hard requirement, decided 2026-07-14)

- **gemma4:e4b** (8B, Q4_K_M), sole executor — continuity with Paper 1's local tier; its 25% baseline localization and 8/10 wrong-file-edit rate leave headroom.
- qwen2.5-coder:7b was piloted and **dropped 2026-07-15** (FINDINGS-07): fails the capability bar (2/10 non-empty patches, 3/10 submissions) and 0/10 consultation — no signal per GPU-hour. Cross-executor generality is out of scope; threats section states it plainly.
- **Scope defense (Pavel, 2026-07-15): generality is delegated to the artifact.** The executor is a single Ollama model id (env var); the artifact ships the Paper 1 Docker + harness with everything needed to re-run any arm on any local model. "Does it hold on model X?" is a one-variable replication, not a gap — say so in threats and in ARTIFACT.md, and make the executor swap a documented first-class path there.

Ollama-served. No Anthropic/API calls anywhere in the execution path (verify again at freeze; Paper 1 threat §10.5).

## 4. Tasks and size

**Expanded 2026-07-15 — Pavel wants a materially bigger sample than Paper 1's 36.**

Because the primary outcome is **gold-file hit**, an instance only needs (repo, base_commit, issue text, gold patch) — no executable test harness required. That unlocks the full width of SWE-bench Verified, not just the paired subset.

**Primary pool — SWE-bench Verified, full width.** 500 instances across 12 repos; excluding the ~40 used in Paper 1 pairs leaves **~460 fresh** (django 231, sympy 75, sphinx 44, matplotlib 34, scikit-learn 32, astropy 22, xarray 22, pytest 19, pylint 10, requests 8, seaborn 2, flask 1). Take the 8 repos with ≥19 instances; **target n ≈ 200–250**, capping django so it isn't half the sample, stratified by repo and difficulty label. Cost per new repo: one frozen-protocol frontier seed (blind, stale checkout — Paper 1 E mechanics, ~$2–3) + a bare clone. Zero new harness plumbing.

**Contamination stratum — SWE-bench-Live slice.** SWE-bench-Live has 1,890 tasks from post-2024 GitHub issues across 223 repos, with per-task Docker images. Take its top ~4 Python repos (~40–60 instances) as a held-out replication stratum: post-2024 issues sit past the local models' pretraining exposure to the *solutions*, answering the "memorized SWE-bench" reviewer threat — which bites harder here than in Paper 1, since delivery deltas are arm-relative but a memorized baseline compresses the headroom all arms compete for.

**Considered and ruled out (cite in threats):**
- **OWASP Benchmark** — synthetic single-file Java security-detection cases; no repository conventions to encode, so the treatment mechanism (repo-level operating knowledge) has nothing to bite on. A security-flavored RCL study wants CVE-fix corpora and is a paper of its own, not a sample expansion.
- **SWE-bench Pro** — selects for multi-file/long-context difficulty; 8B local executors floor there (Paper 1 pilot: 0% resolve on *easy*), yielding no signal per GPU-hour.
- **Multi-SWE-bench / SWE-PolyBench** (other languages) — scaffold, command whitelist, and seed authoring are Python-tuned; a language axis doubles the build for a question orthogonal to delivery. Defer.

Budget at n≈220 Verified + ~50 Live: 270 instances × **3 reps** (down from 5 — instance count now carries the power; confirm with re-run `power_sim.py`) × 4 arms × 1 executor = **3,240 episodes** ≈ 45 GPU-hours ≈ 3–4 overnight batches. Resolve (secondary) via `harness/eval_all.py` for Verified; for Live only if its Docker images run cleanly on ARM — otherwise the Live stratum is localization-only (state in prereg).

## 5. Metrics

| Metric | Role |
|---|---|
| Consultation rate (transcript-derived, rule-based detector + hand-audit of 40 random episodes) | RQ1 primary |
| Gold-file hit | RQ2 primary (Paper 1 §8 pivot metric for the local tier) |
| Context tokens paid (I: injected block size; F/S: tokens of context-file content returned into the transcript) | RQ3 primary |
| Total prompt+completion tokens per episode | RQ3 secondary |
| Non-empty patch rate | secondary |
| Resolve rate | secondary (floor-effect expected at this tier; report, never headline) |
| Shard-relevance (S only): consulted shard matches the instance's constraint topic | exploratory, feeds the miss-rate story |

## 6. Hypotheses (to sharpen at freeze)

- **H1:** consultation rate under F/S is well above zero but well below 1 (point prediction after pilot).
- **H2:** gold-hit ordering B < F ≤ S ≤ I on consulted episodes; unconditionally, F/S recover ≥ half of the I−B effect. (MDE from re-run `analysis/power_sim.py` with Paper 1 pooled variances.)
- **H3:** context tokens paid: S < F < I, with S paying <35% of I's payload on consulted episodes.
- **H4 (tradeoff, honest-loss clause):** S's discovery misses cost outcome relative to I — quantified, not hidden; the paper reports the compliance-adjusted frontier (benefit vs tokens per arm).

## 7. Statistics

Same machinery as Paper 1: per instance×rep paired deltas, sign-flip permutation (10k draws, seed 42), Holm within each RQ family. Families: RQ1 (descriptive, CI only), RQ2 {F−B, S−B, I−B, F−I}, RQ3 {token contrasts}. RQ4 exploratory, labeled as such (conditioning on post-treatment consultation).

## 8. Pilot gates (all BEFORE prereg freeze)

1. **Existence check (roadmap item):** 10 episodes, arm F, gemma4:e4b — does it ever read `context.md` unprompted under the shipped contract? Decides H1's point prediction and whether contract-strength enters the design.
2. ~~qwen2.5-coder:7b capability pilot~~ — done, failed, dropped (FINDINGS-07).
3. Shard-splitter dry run: seeds → OKF files via script; hand-check one repo's output against `metatron context setup` artifacts.
4. Token accounting dry run: verify the context-tokens-paid detector on pilot transcripts (I vs F must reconcile).

## 9. Reuse / build

**Reuse:** checkouts + gold data, `run_batch.py`/`eval_all.py`, permutation analysis, power-sim, seed contexts (frozen — byte-identical to Paper 1's `seeds/`, cite the AUDIT).
**Build (small):** (a) `context_mode ∈ {none, inject, file, sharded}` in `run_condition.py` — file/sharded write artifacts into the checkout before episode start and swap CONTEXT_BLOCK for the shipped contract block; (b) seed→OKF shard splitter; (c) consultation + context-token detectors over transcripts (pure post-processing).

**Guardrail carried from Paper 1:** episode working checkouts must not leak context artifacts between reps — F/S write into the tree, so per-episode checkout reset is now correctness-critical, not hygiene.

## 10. Timeline sketch

- Now → +3 days: build the three small harness pieces; run pilot gates 1–4; write FINDINGS-06 (existence check) and FINDINGS-07 (qwen pilot).
- Then: freeze `PREREGISTRATION-PAPER2.md` (tag `prereg2-v1`), run the 1,440-episode matrix over 2–3 nights, analyze, draft.
- Independent of the Aug 21 AgenticDev outcome — this study stands alone and cites Paper 1 as "under review" until then. **No public promotion of anything paper-related before Aug 21.**

## Decisions

1. **REVISED (Pavel, 2026-07-15, same day): single executor — gemma4:e4b.** qwen2.5-coder:7b was initially approved, then dropped on pilot evidence (FINDINGS-07: fails capability bar, 0% consultation — "it is just holding us back").
2. **PENDING pilot (FINDINGS-06):** if the existence check comes back ~0% consultation, add the contract-strength factor (weak = shipped block / strong = explicit first-command directive) vs. accept the compliance-study framing. Early smoke signal (n=1): model listed the context files on turn 0 and never read them.
3. **DECIDED (Pavel, 2026-07-15): MSR 2027** technical track is the target venue (~Jan–Feb 2027 deadline; verify on the MSR site when the CFP appears).

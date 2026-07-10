# Draft: Methods & Results sections
<!-- For the empirical RCL paper (v2 of the Repository Context Layer manuscript).
     Sources: PREREGISTRATION.md (frozen, tag prereg-v1), FINDINGS-01..05, RESULTS-01/02.
     Neutral academic voice; numbers verified against runs/ artifacts. -->

## N. Empirical Evaluation

We evaluate the Repository Context Layer's central behavioral claim — that repository-carried context measurably changes agent behavior, and that lessons learned in one task transfer to different tasks sharing an underlying constraint — in a pre-registered experiment on SWE-bench Verified. The full protocol, including hypotheses, metrics, analysis plan, and a power simulation, was frozen and externally timestamped before any confirmatory run (git tag `prereg-v1`; pilot runs used for feasibility are excluded from all confirmatory analysis and released alongside).

### N.1 Design

**Benchmark and instances.** SWE-bench Verified supplies real historical bugs from open-source projects, each with a hidden grading test suite and the maintainers' actual fix (the *gold patch*). We manually identified *constraint groups* — sets of instances within one repository whose fixes depend on the same underlying convention (e.g., xarray's `keep_attrs` propagation discipline; Django's `deconstruct()` fidelity rules). Twelve Tier-1 ordered transfer pairs (A, B) were frozen before any run: task B is held out, and the treatment's only advantage on B is context derived from working on A. Two pairs are *documented regression chains*, where the benchmark itself records that B re-broke the constraint A's fix had established — the failure mode the architecture exists to prevent, occurring naturally in the wild.

**Conditions.** A 2×3 fractional matrix crosses executor capability with context origin. Executors: a frontier model (Claude Opus 4.8) and a small local model (Gemma 4 e4b, 8B parameters, quantized, temperature 0). Context: *none* (control), *seeded* (a static `context.md`), or *emergent* (an initially empty store that accumulates the agent's own promoted lessons through the consult–execute–learn–promote lifecycle). A labeled *oracle-taught* arm, in which the learning step additionally sees the gold patch of task A only, provides an upper bound on lesson quality; it is reported separately and never pooled.

**Blind seed authoring.** Seeded-arm context files were authored by fresh model sessions given only: a checkout of the repository at the earliest base commit among its study instances (with version-control history removed), the repository's own documentation, and constraint-group topic names. The authoring sessions never saw a problem statement, gold patch, or test; their transcripts and consulted-file lists are released as an audit trail. Checkouts predate most study instances by years, biasing against the treatment (stale localization knowledge).

**Scaffold.** All conditions share one minimal agent scaffold (single bash command per turn, 20-turn cap, identical prompts); the only manipulated variable is the presence and content of the context block, injected into the system prompt under a 4,000-token cap with the append-only ledger truncated oldest-first. Lessons emitted by the learning step pass a mechanical promotion rubric (repo-generality verified by a fixed-prompt classifier; instance identifiers, line numbers, and >60-word entries rejected deterministically); no human selects lessons. Every promotion decision is logged.

**Leakage guards.** The hidden grading tests and gold patches never enter any executor or learning prompt (oracle arm excepted, A-side only, labeled). Transfer pairs are evaluated with pair-scoped stores: lessons learned on A are available to B, but B's own learning output is discarded and no lesson crosses pairs.

**Metrics.** Primary at the frontier tier: *resolve rate* (the benchmark's hidden-test verdict). At the local tier — where a pre-registered pilot established a resolve floor — primary metrics are process measures, chiefly *gold-file localization* (whether the agent's patch touches any file the gold patch touches), with resolve reported secondarily. Non-empty patch emission, tokens, and turns are reported throughout.

**Analysis.** Paired comparisons per (pair × repetition) with sign-flip permutation tests (10,000 draws, fixed seed); five repetitions per cell at the local tier, three at the frontier tier. The frozen power simulation set the minimum detectable effect at ~17.5 pp for the local-tier primary at 12 pairs × 5 reps.

### N.2 Results

**Table 1 — Held-out task B outcomes by condition (local executor, 12 pairs × 5 reps).**

| Context author | non-empty patch | gold-file hit | resolved |
|---|---|---|---|
| none (control) | 68.3% | 25.0% | 0.0% |
| the executor itself (emergent) | 58.3% | 25.0% | 0.0% |
| frontier model, blind seed | 76.7% | **41.7%** | 0.0% |
| gold-patch-distilled (oracle bound) | 83.3% | **56.7%** | **8.3%** |

**A capability gradient, not a uniform effect.** The benefit of a context layer to a small executor is monotonic in the capability of whoever authored the context. A blind frontier-authored seed raised gold-file localization by +16.7 pp over control (paired Δ, p = 0.041); context distilled from authoritative fixes raised it by +31.7 pp (p = 0.0005) and moved the resolve rate from 0/120 episodes (control and self-taught combined) to 5/60 (p = 0.066). The small model's *own* promoted lessons — 162 of them, extracted and promoted across all 60 pair-repetitions — produced exactly no transfer benefit (+0.0 pp, p = 1.0) and reduced episode completion. Inspection of the promoted entries explains the null: the 8B model predominantly records tooling lessons (shell-quoting pitfalls, editing tactics) rather than repository constraints, whereas the frontier model, given the identical learning prompt on its own transcripts, records precisely the constraint-and-localization facts the clusters center on.

**The lifecycle's bottleneck is authorship, not consumption.** The same weak executor that cannot write useful context consumes it effectively — a dissociation with a direct practical reading: context layers should be seeded and maintained by capable writers (humans, frontier models, or distillation from authoritative fixes), and a weak local agent then inherits a large fraction of the benefit at zero marginal inference cost. The oracle bound additionally shows the deployable blind-seed effect (+16.7 pp) is roughly half of what better authorship could achieve, leaving measurable headroom.

**Frontier-tier cells were ceiling-invalidated on these pairs.** Unaided, the frontier executor localizes 94.4% and resolves 72.2% of the held-out tasks — leaving no measurable room on this instance set; the emergent-arm comparison is accordingly null and uninformative (−5.6 pp resolve, p = 0.73). The pre-registration's difficulty-stratification rule anticipated this; the frontier lifecycle question is deferred to a stratified rerun on harder instances [forthcoming / reported in §N.x].

**Cost.** The entire confirmatory experiment to date — 560 agent episodes and 443 containerized evaluations — consumed approximately $27 of frontier-API spend and half a GPU-day of local inference, supporting the architecture's economic premise: expensive knowledge, written once, read cheaply forever.

### N.3 Threats to Validity

*Construct.* Gold-file localization is a proxy; it measures working in the right place, not fixing the bug. We report resolve alongside and note the oracle arm moved both. *Internal.* The orchestrating researcher session had instance exposure; it was excluded from seed authorship (fresh blind sessions authored all seeds, audit-logged) and from lesson selection (mechanical rubric). Training contamination affects both arms of every within-model comparison symmetrically and, if anything, compresses deltas toward zero. *External.* Three repositories, one benchmark, one scaffold; the transfer pairs target constraint-shaped bugs by construction, and effects may differ for tasks with no operating-constraint component. *Statistical.* The resolve improvement at the local tier is marginal (p = 0.066) at 12 pairs; the pre-planned Tier-2 expansion (~40 pairs) addresses power. A reviewer pooling the RQ1 and RQ2 families into one correction family would read the blind-seed localization effect at p = 0.082; we report both framings.

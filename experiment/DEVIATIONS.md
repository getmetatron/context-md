# Deviations from `prereg-v1`

Required by `PREREGISTRATION.md` §12. This file covers the Paper 1 protocol
frozen at tag `prereg-v1` (commit `056156679a896f0697198bb240c92110aa2df048`,
2026-07-09). The delivery study has its own frozen protocol
(`PREREGISTRATION-PAPER2.md`, tag `prereg2-v1`) and its own log,
`DEVIATIONS-2.md`.

**How this was compiled.** The frozen protocol was compared clause by clause
against the committed implementation (`harness/`, `analysis/`), the arms present
in `runs/`, and the reported results (`RESULTS-01..06.md`, and the camera-ready
paper). Statements below about what was *not* run were checked against the
repository, not recalled. This file exists for transparency; it deliberately
records what was left undone as well as what changed.

---

## 1. Material deviations from the confirmatory protocol

### 1.1 Statistical test: permutation instead of mixed-effects / McNemar

§7 specifies "mixed-effects logistic regression for resolve" and, for RQ2,
"McNemar on paired reps + mixed-effects with pair as random effect". The
implementation (`analysis/reproduce_paper.py`) instead uses a **paired sign-flip
permutation test** (10,000 draws, fixed seed 42) on per-pair, per-rep deltas.

This is a deviation from §7 as written, but it is the test the study was powered
for: the §8 power simulation (`analysis/power_sim.py`, frozen with the protocol)
is itself built on "paired sign-flip permutation test". The protocol was
internally inconsistent between §7 and §8; the implementation followed §8. The
permutation test is the more conservative choice here — it makes no distributional
or link-function assumption and respects the pairing exactly. No mixed-effects
model was fitted, so we cannot report what it would have given.

### 1.2 Registered secondary not measured: constraint-violation rate

§6 registers "constraint-violation rate for the pair's constraint, scored blind by
fixed-prompt LLM judge with 20% human double-scoring (report agreement)". The
§8 pivot then promoted this to a **primary** RQ2 metric for the local tier,
alongside wrong-file-edit rate.

**It was never implemented.** There is no judge in `harness/` or `analysis/`, and
no constraint-violation figure appears in any results document or in the paper.
Of the two local-tier primaries, only wrong-file-edit rate (reported as its
complement, gold-file localization) was measured. This is the most consequential
gap in this log: the metric closest to the architecture's real-world claim —
adherence to a project constraint — was registered and not collected. The paper's
threats section makes the related point that SWE-bench cannot score
convention-adherence; that argument would have been stronger, or weaker, with
this metric in hand.

### 1.3 Frontier tier ran fewer pairs than the §8 target

§8 plans "≥25 confirmatory pairs (Tier-1+2), extendable to 40". The pooled
local tier met this (36 pairs × 5 reps). The **frontier tier ran 16 pairs × 3
reps**, below the ≥25 target and at the low end of the §8 power table. §8 also
permitted raising frontier reps from 3 to 5 "if observed variance warrants";
reps were not raised. This is a direct cause of the wide interval on the frontier
resolve effect, which the camera-ready reports as directional
(raw p = 0.041, Holm-adjusted p = 0.082 within its registered family).

---

## 2. Registered conditions and questions not executed

These were in the frozen protocol and were not run. None was dropped after seeing
an unfavourable result; each was descoped for cost or time.

| registered | status |
|---|---|
| **Condition F** — local executor, local-authored seed (§2) | not run; no `runs/F` |
| **Condition G** — local executor, human-authored seed from repo ADRs/docs (§2) | not run; no `runs/G`, no `seeds/*-human` |
| **RQ3 / H3** — accumulation across a within-repo sequence (§1, §4.6) | not run; carried as "next steps" in `RESULTS-01`/`RESULTS-02` |

Consequence for H4b: the registered hypothesis is "E > B, with E's gain ≥ half of
E's own self-seeded gain (F)", and the protocol labels **the E-vs-F comparison
itself as exploratory**. The confirmatory part (E > B) was tested and is reported.
The exploratory half could not be evaluated, because F does not exist. Where the
paper contrasts frontier-authored context with the executor's *own* context, the
comparison is against **condition D** (emergent, self-authored through the
lifecycle), not condition F (a self-authored seed). D and F are different
treatments and should not be read as interchangeable.

---

## 3. Registered conditional pivots that were activated

Not deviations — the protocol specified these in advance, with their trigger.

- **Local-tier metric pivot (§8, triggered by FINDINGS-03).** The local resolve
  floor was confirmed at ≤2/10 on easy instances pre-freeze, so local-tier primary
  RQ2 metrics became wrong-file-edit rate and constraint-violation rate, with
  resolve secondary; the frontier tier kept resolve primary. Activated as written
  (subject to §1.2 above).
- **Labeled oracle arm (§4.3).** Run as registered: the A-side learning step sees
  the gold patch, the arm is labeled, and it is never pooled with confirmatory
  arms. Present as `runs/C_oracle`, `runs/D_oracle`, `runs/D_oracleT2`.
- **Exclusions (§9).** No per-result exclusions were applied.

## 4. Pre-planned expansions

- **Tier-2 pair expansion.** §4 designates Tier-1 groups confirmatory and Tier-2
  confirmatory for the RQ2 pooled analysis; §8 plans extension to 40 pairs. The
  local tier was expanded from the initial Tier-1 set to the pooled 36-pair set
  (`runs/D_oracle` + `runs/D_oracleT2`).
- A local-tier **resolve** improvement that was marginal on the initial pair set
  (p = 0.066) **did not survive** this pre-planned expansion (pooled p = 0.22) and
  is not claimed anywhere in the paper. This is recorded because the expansion was
  planned before the initial result was seen, and the result moved against the
  hypothesis.

## 5. Exploratory analyses

Labelled as exploratory in the paper wherever reported.

- **Broad-sample frontier ceiling** (88-instance stratified random subset,
  `runs/opus_ext`). Not part of `prereg-v1`, which concerns constraint-sharing
  transfer pairs. Added to bound where the architecture does *not* help. Reported
  as a scope finding, and it is the result least favourable to the architecture.
- **Delivery mechanisms** (`runs/FILE`, `runs/SHARD`). Governed by the separate
  `prereg2-v1` protocol, not by `prereg-v1`. The SHARD−FILE contrast (+6.6 pp,
  p = 0.0007) is exploratory: under the registered family no single delivery
  contrast clears Holm correction (SHARD−B: Holm p = 0.058).
- **E-vs-Do comparison** (blind frontier seed vs gold-distilled oracle bound) at
  the local tier: descriptive, not a registered contrast.

## 6. Post-hoc interpretations

Generated after seeing the data. The paper labels each as such.

- **The frontier "inversion".** H2 (treatment > control on held-out B) was
  pre-registered. The *reading* that what transfers switches from answer-derived
  to failure-derived context as the reader strengthens was **not** a registered
  hypothesis. It is a post-hoc interpretation of a directional result.
- **"Context inheritance" as an organizing frame.** The capability-dependent
  author–reader pattern is an interpretation of results across tiers, not a
  registered hypothesis about a capability gradient's shape. Only two author
  levels were observed, and author and executor come from different model
  families, so capability and family are confounded.

## 7. Additional camera-ready diagnostics

- **Blind-seed leakage audit**
  (`paper/camera-ready-agenticdev2026/analysis/seed_leakage.py`, results in
  `RESULTS-07-seed-leakage.md`). A post-hoc diagnostic added during camera-ready
  preparation, measuring overlap between the blind seeds and the gold patches of
  the held-out instances, against the same seed text scored on same-repo instances
  outside the study set. It is observational, not a manipulation, and the paper
  states that it cannot rule out pretraining-mediated partial solution knowledge.
- **Correction found while preparing the camera-ready.** The submitted version
  stated the frontier lifecycle was "positive in 8 of 11 groups". Every
  aggregation of the frozen data gives **7 improving, 3 flat, 1 declining**;
  `reproduce_paper.py` had not asserted that particular sentence. Corrected in the
  camera-ready and now asserted by
  `paper/camera-ready-agenticdev2026/analysis/verify_claims.py`.
- **Multiple-comparison status made explicit.** The frontier resolve p-value is
  reported both uncorrected (0.041) and Holm-adjusted within its registered family
  (0.082), and the effect is described as directional rather than confirmed.

---

## 8. Checked and found unchanged

Verified against the frozen text; no deviation found.

- Conditions A–E as defined in §2, with the executors, context modes and seed
  authors as registered.
- Transfer pairs exactly as frozen in `FINDINGS-02` (§4); no pair added to a
  confirmatory analysis after the freeze.
- Dedupe rule (§4): each instance in at most one constraint group.
- Leakage guards (§5): gold patches and hidden tests never enter executor or
  learning prompts, except the labeled oracle arm's A-side, which is flagged in
  the episode logs.
- Blind seed authoring (§4.5): authored from a history-stripped checkout at the
  earliest base commit with constraint-group names only; audited in
  `seeds/AUDIT.md`.
- Analysis seed and permutation count (10,000 draws, seed 42) as used by the
  frozen power simulation.

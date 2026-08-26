# RESULTS-06 — Paper 2 confirmatory delivery matrix (3,204 episodes, 2026-07-19)

Analysis per FROZEN prereg2-v1 (PREREGISTRATION-PAPER2.md), script
`analysis/analyze_p2.py`, per-episode table `runs/analysis_p2_episodes.csv`.
267 frozen instances (harness/instances_paper2.json) x 3 reps x 4 arms,
gemma4:e4b, temp 0. Episodes outside the frozen list (10 extra instances in
B/E, run pre-freeze) excluded — DEVIATIONS-2.md.

## Headline table

| arm | n | gold-hit | submitted | consulted | deep-read | ctx-toks (mean) | prompt-toks | completion-toks |
|---|---|---|---|---|---|---|---|---|
| B (none) | 801 | .486 | .719 | .00 | .00 | 0 | 35,743 | 2,512 |
| E (injected) | 801 | .512 | .728 | .00 | .00 | 930 | 45,976 | 2,573 |
| FILE (monolith) | 801 | .468 | .702 | .97 | .966 | 902 | 48,581 | 2,868 |
| SHARD (okf store) | 801 | .534 | .777 | .97 | .970 | 305 | 46,136 | 2,801 |

## H1 — CONFIRMED

Consultation under the shipped 0.12.0 procedural contract: FILE .970 / SHARD
.970; deep-read .966 / .970; read-before-edit .970 both. All inside the
registered band 0.90–1.00 (point prediction 1.00). The contract binds at scale
(1,602 contract-arm episodes), not just in the 20-episode FINDINGS-08 iteration.

## H2 — NOT CONFIRMED after Holm (registered 4-test family)

Sign-flip permutation, 10k draws, seed 42, Holm within family:

| contrast | delta | raw p | Holm p |
|---|---|---|---|
| FILE−B | −1.7 pp | .40 | .43 |
| SHARD−B | **+4.9 pp** | .014 | **.058** |
| E−B | +2.6 pp | .22 | .43 |
| FILE−E | −4.4 pp | .030 | .091 |

No family test reaches Holm-corrected p < .05. SHARD−B misses by a hair
(.058). Honest confirmatory statement: *no delivery mechanism is confirmed to
beat no-context on gold-file-hit in this design.*

**Exploratory (outside the registered family):** SHARD−FILE = **+6.6 pp,
p = .0007**. The registered family compared each mechanism to B and to
injection; the sharpest contrast in the data is between the two file
mechanisms themselves.

Context for the attenuation: baseline gold-hit here is .49 vs .21 in Paper 1
(instance pool difference — the wide 267-instance pool is easier to localize
than Paper 1's transfer pairs). The MDE calc assumed baseline .21; at .49 the
same seeds have less headroom, and observed deltas (≤5 pp) sit below the
+7–8 pp MDE. The design was powered for a 3x-attenuated Paper 1 effect and the
true file-delivery effect attenuated further.

## H3 — CONFIRMED (both contrasts, own Holm family)

Context-tokens-paid, one-sided S < F < I:

| contrast | delta (toks/episode) | raw p | Holm p |
|---|---|---|---|
| SHARD < FILE | −597 | .0001 | .0002 |
| FILE < E | −27 | .0001 | .0002 |

SHARD pays ~3x fewer context tokens than FILE (305 vs 902) because agents read
the index plus only the relevant shard(s); FILE forces the whole monolith
through the transcript. FILE≈E in cost (902 vs 930): reading the monolith costs
what injecting it costs — file delivery per se saves nothing; *selection* saves.

## The emerging story: selection beats volume

Same content, four deliveries. The monolith arms (E injected, FILE read) sit
within noise of baseline; the monolith-as-file is numerically *below* baseline
(−1.7 pp) while paying the most tokens and showing the lowest submit rate
(.702) — plausibly crowding out task reasoning in a 32K window. SHARD, which
makes the agent *choose* what to read, is best on gold-hit (+4.9 pp, Holm-
marginal), best on submit rate (.777), and 3x cheapest on context tokens. H4
mediation/complier analysis (exploratory) to follow in the RESULTS addendum.

## Resolve rate (secondary — no confirmatory claim at this tier)

SWE-bench Docker evals complete across all 4 arms. B/E re-evaluated under
`eval-P2-*` run_ids (name collision with Paper 1 evals — DEVIATIONS-2.md).

| arm | n | resolved | rate |
|---|---|---|---|
| B (none) | 801 | 45 | 5.6% |
| E (injected) | 801 | 69 | 8.6% |
| FILE (monolith) | 801 | 56 | 7.0% |
| SHARD (okf store) | 801 | 54 | 6.7% |

Exploratory contrasts (sign-flip, seed 42, two-sided, no Holm — secondary):
- E−B: +3.0pp, p=.015 — injection marginally helps resolve; borderline but
  consistent with E's prompt-token advantage (it doesn't crowd the 32K window
  as badly as FILE's monolith-read).
- FILE−B: +1.4pp, p=.22; SHARD−B: +1.1pp, p=.32 — both null.
- SHARD−FILE: −0.25pp, p=.86 — flat.

Interpretation: at the local 8B tier, no file-delivery mechanism moves resolve.
This matches the Paper 1 pooled resolve null and is the registered expectation.
The gold-hit story (H2/H3) stands independently of this secondary.

## Consultation-detector verification

The fixed 40-episode sample (seed 42 from the 1,602 FILE/SHARD episodes) received
author verification on 2026-08-26. For `consulted`, `deep_read`, and
`read_before_edit`, the author-confirmed labels and detector each gave 38 positive
and 2 negative episodes: raw agreement 40/40, confusion matrix 38/0/0/2, no
unclear rows and no disagreements. Mechanical Cohen's kappa is 1.000, but only
two negatives were sampled, making kappa unstable. The review was AI-assisted
and not blinded to the detector comparison, so these statistics are descriptive
confirmation rather than independent inter-rater reliability. This workflow
deviation is recorded in `DEVIATIONS-2.md`.

## Other pending

- Registered extension: SWE-bench-Live stratum; Opus extension tier (ROADMAP).

## H4 — exploratory (post-treatment conditioning; no causal claim)

Within-arm, gold-hit conditional on behavior:

- SHARD consulted episodes hit .539 vs .375 non-consulted (n=777/24); in FILE
  the split is flat (.467 vs .500) — consistent with consultation helping only
  when what is read is selective.
- Within SHARD-consulted, *restraint* correlates with success: episodes in the
  two lightest context-token quartiles hit .60/.62; the heaviest-reading
  quartile (mean 621 toks, i.e., monolith-like volume) hits .44 — the
  within-arm gradient reproduces the between-arm FILE penalty. Confounded
  (harder tasks plausibly induce more reading); reported as exploratory only.

## Per-repo gold-hit (secondary)

| repo | B | E | FILE | SHARD |
|---|---|---|---|---|
| astropy | .591 | .652 | .455 | .652 |
| django | .533 | .383 | .406 | .506 |
| matplotlib | .441 | .500 | .500 | .441 |
| pytest | .316 | .579 | .474 | .596 |
| scikit-learn | .625 | .708 | .677 | .625 |
| sphinx | .417 | .512 | .345 | .536 |
| sympy | .400 | .489 | .439 | .461 |
| xarray | .667 | .417 | .583 | .750 |

SHARD is top or tied-top in 4/8 repos; FILE is bottom in 3/8.

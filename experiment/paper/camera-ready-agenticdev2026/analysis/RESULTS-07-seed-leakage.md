# RESULTS-07 — Seed-blindness quantification

The blind seed author receives the repository checkout and the constraint-group
names. Those names point at the convention under test, and these repositories are
almost certainly in the author model's pretraining, so a seed could in principle
act as a partial gold distillation rather than a purely navigational aid. This
note quantifies that: the surface similarity between seeds and gold patches, and
the rate at which seeds name gold-patch files or symbols directly.

Script: `analysis/seed_leakage.py` (reads frozen artifacts read-only).
Set: the 36 frozen transfer pairs; held-out B instance of each.

## Measured

Same seed text scored against in-group (held-out B) vs out-of-group (same repo,
outside the study set) gold patches. Using one fixed seed text for both holds
length constant.

| metric | held-out B (n=36) | same-repo, non-study (n=257, 3 repos) |
|---|---|---|
| names ≥1 gold-patch file | **83.3%** | 32.3% |
| names ≥1 gold-patch symbol | **55.6%** | 3.9% |
| identifier Jaccard vs patch | 0.019 | 0.013 |
| names ≥1 identifier the fix *introduces* | 66.7% | 51.9% |

## Reading

1. **Localization overlap is real and large.** The seed names the file the fix
   lands in for 83% of held-out instances, against 32% for same-repo instances
   it was never pointed at. This is not deniable and must be stated.

2. **It is topic conditioning, not solution leakage.** The elevation tracks
   *where* (files 83% vs 32%, symbols 56% vs 4%) and not *what* (identifier
   Jaccard 0.019 vs 0.013; novel-identifier naming 66.7% vs 51.9% — both near
   the same seed's out-of-group rate). The seed encodes terrain, not fixes.

3. **The independent check.** The identical seed yields +26.1 pp localization on
   topic-matched pairs but only +4.9 pp on the broad 267-instance pool
   (RESULTS-06). If the seed were a partial gold distillation it would travel;
   it does not. Its value is concentrated exactly where its topics match.

## Consequence for the paper

The +26.1 pp gradient effect is measured under experimenter-chosen topic
matching. That is the regime the architecture targets, but the effect size is
**conditional on topic match** and should not be read as what an arbitrary
repository context yields on an arbitrary task — the +4.9 pp broad-pool figure
is the unconditioned estimate. Threats § must say this.

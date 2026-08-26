# Consultation-detector verification

This directory releases the fixed 40-episode audit sample, the detector key, and
the author-verification record promised by `PREREGISTRATION-PAPER2.md`.

The procedure was AI-assisted and non-blinded: AI prepared row-specific evidence
and proposed labels, and Pavel Kerbel reviewed and confirmed every row after the
detector comparison was visible. It is therefore reported as descriptive author
verification, not as independent blinded inter-rater reliability.

Recompute the agreement statistics from `experiment/`:

```sh
python analysis/consultation_audit_analyze.py \
  --audit audit/consultation-hand-audit-40.csv \
  --key audit/consultation-hand-audit-40.key.csv
```

For each of consultation, deep read, and read-before-edit, the result is 40/40
raw agreement (38 positive, 2 negative), confusion matrix 38/0/0/2, no unclear
rows, and no disagreements. Mechanical Cohen's kappa is 1.000, but is unstable
with only two negative rows and is not treated as an independent reliability
estimate because the confirmation was not blinded.

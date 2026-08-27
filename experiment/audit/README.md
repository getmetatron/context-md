# Consultation-detector verification

This directory releases the fixed 40-episode audit sample, the detector key, and
the author-verification record promised by `PREREGISTRATION-PAPER2.md`.

Pavel Kerbel manually reviewed every row against row-specific transcript evidence
and confirmed every label. The evidence packet and candidate labels were
AI-prepared, and the detector comparison was visible during review. It is
therefore reported as descriptive author verification, not as independent blinded
inter-rater reliability.

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

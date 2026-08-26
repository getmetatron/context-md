# Consultation-detector author verification

Date: 2026-08-26

Pavel Kerbel reviewed the row-by-row evidence and proposed labels for all 40
episodes in the fixed consultation-detector sample and explicitly confirmed that
he agreed with every judgment. The confirmed labels are recorded in
`consultation-hand-audit-40.csv`; every row contains the evidence on which the
decision rests.

This was an AI-assisted human verification, not an independent blinded rating:
the author reviewed AI-prepared evidence after the proposed labels and detector
comparison were available. It must not be described as a blinded inter-rater
study. The agreement statistics below are descriptive confirmation of the frozen
detector, not an unbiased estimate of independent human--detector reliability.

## Results

For each of `consulted`, `deep_read`, and `read_before_edit`:

- author-confirmed labels: 38 positive, 2 negative;
- detector labels: 38 positive, 2 negative;
- raw agreement: 40/40 (1.000);
- confusion matrix: 38 both-positive, 0 author-positive/detector-negative,
  0 author-negative/detector-positive, 2 both-negative;
- Cohen's kappa, mechanically computed: 1.000;
- disagreements: none;
- unclear rows: none.

Only two negative rows were sampled, so kappa is unstable and raw agreement is
the more informative descriptive statistic. The two negative episodes are A22
and A29; neither transcript contains a command that reads `context.md`, a file
under `context/`, or `AGENTS.md`.

The completed CSV SHA-256 is
`086203d812eb8d2efa7cc434a808a00eb47053f068f7dcf60b306dea162e0d17`.

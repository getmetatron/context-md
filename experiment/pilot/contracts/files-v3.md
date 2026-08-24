<!-- METATRON:START (managed by metatron context setup — safe to edit inside) -->
## Repository context — required first step

This repository carries its own operating knowledge. Before you explore or edit
any code:

1. Run `cat context.md` — it lists this repo's binding conventions ("decisions")
   and where each one lives.
2. Open the decision files relevant to your task with
   `cat context/decisions/<topic>.md`. They say where fixes belong and which
   pitfalls to avoid.
3. Only then plan your change — and state which decision files you read.

Reading these files is required, not optional: a fix that contradicts a decision
will be rejected in review. Listing the directory is not reading.

To record a new durable convention you discovered, add an OKF file under
`context/decisions/` on your working branch; it reaches the default branch only
through a human-reviewed pull request.
<!-- METATRON:END -->

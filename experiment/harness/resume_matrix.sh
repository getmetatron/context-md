#!/bin/bash
# Resume the Paper 2 confirmatory matrix after an interruption (shutdown, kill).
# Safe to run any number of times: completed episodes are skipped, so it only
# fills in what is missing. Run from the repo root:  bash harness/resume_matrix.sh
cd "$(dirname "$0")/.." || exit 1
ALL=$(.venv/bin/python -c "import json; print(\",\".join(json.load(open(\"harness/instances_paper2.json\"))[\"instances\"]))")
for rep in 1 2 3; do
  for cond in B E FILE SHARD; do
    echo "===== COND $cond REP $rep (resume) $(date +%H:%M) ====="
    .venv/bin/python harness/run_condition.py --condition $cond --instances "$ALL" --rep $rep --skip-existing
  done
done
echo '===== MATRIX COMPLETE ====='

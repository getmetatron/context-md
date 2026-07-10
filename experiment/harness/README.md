# Confirmatory harness

- `run_condition.py` — A–G condition runner (frozen scaffold; seeded/emergent context per prereg §4; predictions in swebench format)
- `promote.py` — mechanical candidate→decision rubric (§4.4), fully logged
- `templates.py` — frozen prompts (§4.1 consultation, §4.2 learning, §4.3 oracle)

## Evaluation
Use the OFFICIAL prebuilt images (`--namespace swebench`); locally built images
(`--namespace ''`) have recipe drift on arm64 (verified: sphinx 3.0 env missing
`roman`, gold patch scores unresolved). Gold-patch smoke test passed 2026-07-09
with official arm64 images.

    python -m swebench.harness.run_evaluation \
      --dataset_name princeton-nlp/SWE-bench_Verified \
      --predictions_path runs/<cond>/rep<k>/predictions.jsonl \
      --run_id <cond>-rep<k> --namespace swebench --max_workers 2

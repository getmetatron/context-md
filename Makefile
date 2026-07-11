PY ?= python3

help:
	@echo "Artifact targets:"
	@echo "  make reproduce-paper   Tier 1: recompute all paper numbers from committed data (~1 min)"
	@echo "  make docker-reproduce  Tier 1 inside Docker (no local Python needed)"
	@echo "  make episode           Tier 2: one full agent episode (needs Ollama or ANTHROPIC_API_KEY)"
	@echo "  make evaluate-episode  Tier 2: score that episode with official SWE-bench images (needs Docker)"

reproduce-paper:
	$(PY) analysis/reproduce_paper.py

docker-reproduce:
	docker build -t rcl-artifact . && docker run --rm rcl-artifact

# Tier 2 example: local executor, no context (condition B), one instance.
episode:
	$(PY) harness/run_condition.py --condition B --instances django__django-15499 --rep 99

evaluate-episode:
	$(PY) -m swebench.harness.run_evaluation \
	  --dataset_name princeton-nlp/SWE-bench_Verified \
	  --predictions_path runs/B/rep99/predictions.jsonl \
	  --run_id artifact-episode --namespace swebench --max_workers 1

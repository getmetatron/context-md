#!/usr/bin/env python3
"""Evaluate all batch predictions with the official swebench images.

Jobs are grouped so no predictions file contains duplicate instance_ids:
  - D arm: one job per (pair, rep)      (A-side and B-side are distinct instances)
  - B/E arms: one job per rep
Empty patches are excluded from eval and recorded as unresolved in
runs/eval_summary.jsonl (definitionally unresolved).
"""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
SUMMARY = ROOT / "runs" / "eval_summary.jsonl"


def record(run_id, iid, resolved, note=""):
    with SUMMARY.open("a") as f:
        f.write(json.dumps({"run_id": run_id, "instance_id": iid,
                            "resolved": resolved, "note": note, "ts": time.time()}) + "\n")


def main():
    jobs = []
    for pf in sorted((ROOT / "runs").rglob("predictions.jsonl")):
        rel = pf.relative_to(ROOT / "runs")
        run_id = "eval-" + "-".join(rel.parts[:-1]).replace("pair_", "p")
        jobs.append((run_id, pf))
    print(f"{len(jobs)} eval jobs", flush=True)

    for run_id, pf in jobs:
        preds = [json.loads(l) for l in pf.read_text().splitlines()]
        nonempty = [p for p in preds if p["model_patch"].strip()]
        for p in preds:
            if not p["model_patch"].strip():
                record(run_id, p["instance_id"], False, "empty_patch_skipped")
        if not nonempty:
            print(f"{run_id}: all empty, skipped", flush=True); continue
        tmp = pf.with_suffix(".nonempty.jsonl")
        tmp.write_text("\n".join(json.dumps(p) for p in nonempty))
        rc = subprocess.run([PY, "-m", "swebench.harness.run_evaluation",
                             "--dataset_name", "princeton-nlp/SWE-bench_Verified",
                             "--predictions_path", str(tmp),
                             "--run_id", run_id, "--namespace", "swebench",
                             "--max_workers", "3"],
                            capture_output=True, text=True)
        # harvest per-instance reports
        n_res = 0
        for p in nonempty:
            rep = ROOT / "logs" / "run_evaluation" / run_id / p["model_name_or_path"] / p["instance_id"] / "report.json"
            resolved = False
            if rep.exists():
                resolved = json.loads(rep.read_text())[p["instance_id"]]["resolved"]
            record(run_id, p["instance_id"], resolved)
            n_res += resolved
        print(f"{run_id}: {n_res}/{len(nonempty)} resolved (rc={rc.returncode})", flush=True)

    print("EVAL ALL DONE", flush=True)


if __name__ == "__main__":
    main()

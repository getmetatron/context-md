#!/usr/bin/env python3
"""Resolve-rate eval for the Opus extension tier (4 arms x 88 instances).

predictions.jsonl in the B/SHARD arms contains stale/empty lines from the
rate-limit reruns (the harness appends on every attempt). We dedupe by
instance_id keeping the LAST entry (the successful rerun), restrict to the
frozen 88-instance opus_ext list, drop empty patches (recorded unresolved),
then run the official swebench images. Resumable via the summary file.

Usage: .venv/bin/python harness/eval_opus_ext.py
"""
import json, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
RUNS = ROOT / "runs" / "opus_ext"
SUMMARY = RUNS / "eval_summary.jsonl"
INSTANCES = set(json.load(open(ROOT / "harness" / "instances_opus_ext.json"))["instances"])
ARMS = ["B", "E", "FILE", "SHARD"]


def record(run_id, iid, resolved, note=""):
    with SUMMARY.open("a") as f:
        f.write(json.dumps({"run_id": run_id, "instance_id": iid,
                            "resolved": resolved, "note": note, "ts": time.time()}) + "\n")


def dedup(pf):
    """Last non-... wins; keep the final entry per instance_id, frozen list only."""
    last = {}
    for line in pf.read_text().splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        if p["instance_id"] in INSTANCES:
            last[p["instance_id"]] = p
    return list(last.values())


def main():
    done = set()
    if SUMMARY.exists():
        done = {json.loads(l)["run_id"] for l in SUMMARY.read_text().splitlines()}

    for arm in ARMS:
        run_id = f"eval-opus-ext-{arm}"
        if run_id in done:
            print(f"{run_id}: already done, skipping", flush=True)
            continue
        pf = RUNS / arm / "rep1" / "predictions.jsonl"
        preds = dedup(pf)
        nonempty = [p for p in preds if p["model_patch"].strip()]
        for p in preds:
            if not p["model_patch"].strip():
                record(run_id, p["instance_id"], False, "empty_patch_skipped")
        print(f"{run_id}: {len(preds)} unique, {len(nonempty)} nonempty -> eval", flush=True)
        if not nonempty:
            continue

        tmp = pf.with_suffix(".dedup.jsonl")
        tmp.write_text("\n".join(json.dumps(p) for p in nonempty))
        rc = subprocess.run(
            [PY, "-m", "swebench.harness.run_evaluation",
             "--dataset_name", "princeton-nlp/SWE-bench_Verified",
             "--predictions_path", str(tmp),
             "--run_id", run_id, "--namespace", "swebench",
             "--max_workers", "3"],
            capture_output=True, text=True)
        print(f"  swebench rc={rc.returncode}; tail:\n{rc.stdout[-500:]}\n{rc.stderr[-500:]}", flush=True)

        n_res = 0
        for p in nonempty:
            rep = (ROOT / "logs" / "run_evaluation" / run_id /
                   p["model_name_or_path"] / p["instance_id"] / "report.json")
            resolved = False
            if rep.exists():
                try:
                    resolved = json.loads(rep.read_text())[p["instance_id"]]["resolved"]
                except Exception:
                    resolved = False
            record(run_id, p["instance_id"], resolved)
            n_res += resolved
        print(f"{run_id}: {n_res}/{len(nonempty)} resolved", flush=True)

    print("OPUS-EXT EVAL DONE", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One-off: evaluate Paper 2 B/E predictions under P2-prefixed run_ids
(the plain eval-B-repN ids were consumed by Paper 1 — see DEVIATIONS-2.md)."""
import json, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
SUMMARY = ROOT / "runs" / "eval_summary.jsonl"
frozen = set(json.load(open(ROOT/"harness/instances_paper2.json"))["instances"])
done = {json.loads(l)["run_id"] for l in SUMMARY.read_text().splitlines()}

def record(run_id, iid, resolved, note=""):
    with SUMMARY.open("a") as f:
        f.write(json.dumps({"run_id": run_id, "instance_id": iid,
                            "resolved": resolved, "note": note, "ts": time.time()}) + "\n")

for arm in ("B", "E"):
    for rep in (1, 2, 3):
        run_id = f"eval-P2-{arm}-rep{rep}"
        if run_id in done: print(f"{run_id}: done, skip"); continue
        pf = ROOT / "runs" / arm / f"rep{rep}" / "predictions.jsonl"
        seen, preds = set(), []
        for l in pf.read_text().splitlines():
            p = json.loads(l)
            if p["instance_id"] in frozen and p["instance_id"] not in seen:
                seen.add(p["instance_id"]); preds.append(p)
        nonempty = [p for p in preds if p["model_patch"].strip()]
        for p in preds:
            if not p["model_patch"].strip():
                record(run_id, p["instance_id"], False, "empty_patch_skipped")
        tmp = pf.with_suffix(f".p2eval{rep}.jsonl")
        tmp.write_text("\n".join(json.dumps(p) for p in nonempty))
        rc = subprocess.run([PY, "-m", "swebench.harness.run_evaluation",
                             "--dataset_name", "princeton-nlp/SWE-bench_Verified",
                             "--predictions_path", str(tmp),
                             "--run_id", run_id, "--namespace", "swebench",
                             "--max_workers", "3"], capture_output=True, text=True)
        n = 0
        for p in nonempty:
            rep_f = ROOT/"logs/run_evaluation"/run_id/p["model_name_or_path"]/p["instance_id"]/"report.json"
            r = json.loads(rep_f.read_text())[p["instance_id"]]["resolved"] if rep_f.exists() else False
            record(run_id, p["instance_id"], r); n += r
        print(f"{run_id}: {n}/{len(nonempty)} resolved (rc={rc.returncode})", flush=True)
print("P2 B/E EVAL DONE")

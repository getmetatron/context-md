#!/usr/bin/env python3
"""Overnight batch orchestrator — RQ2 transfer study, local tier.

Per pair (A,B) and rep k (PREREGISTRATION §4.7):
  D-arm  : run A under condition D (emergent, learning ON), then B with
           --no-learning consulting the pair-scoped store. Pair-scoped rep
           dir => no cross-pair chaining.
  B-arm  : run B under condition B (no context)  — paired control.
  E-arm  : run B under condition E (blind frontier seed) — assist comparison.

Episodes are serialized (single local GPU). Predictions accumulate per
arm/rep; empty patches are recorded as unresolved without Docker eval
(definitionally unresolved; efficiency only, no prereg impact).

Usage: run_batch.py --pairs harness/pairs_tier1.json --reps 1 2 3 4 5 [--arms D B E]
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
RC = str(ROOT / "harness" / "run_condition.py")


def run(cmd, log):
    with open(log, "a") as f:
        f.write(f"\n$ {' '.join(cmd)}\n"); f.flush()
        return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default=str(ROOT / "harness" / "pairs_tier1.json"))
    ap.add_argument("--reps", type=int, nargs="+", default=[1])
    ap.add_argument("--arms", nargs="+", default=["D", "B", "E"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    pairs = json.loads(Path(args.pairs).read_text())["pairs"]
    log = ROOT / "runs" / "batch.log"
    log.parent.mkdir(exist_ok=True)
    t0 = time.time()
    total = done = 0

    plan = []
    for rep in args.reps:
        for p in pairs:
            tag = f"{p['a'].split('-')[-1]}_{p['b'].split('-')[-1]}"
            if "D" in args.arms:
                pdir = str(ROOT / "runs" / "D" / f"pair_{tag}" / f"rep{rep}")
                plan.append((f"D/pair_{tag}", ["--condition", "D", "--instances", p["a"], "--rep", str(rep), "--run-dir", pdir], tag))
                plan.append((f"D/pair_{tag}", ["--condition", "D", "--instances", p["b"], "--rep", str(rep), "--no-learning", "--run-dir", pdir], tag))
            if "B" in args.arms:
                plan.append(("B", ["--condition", "B", "--instances", p["b"], "--rep", str(rep)], None))
            if "E" in args.arms:
                plan.append(("E", ["--condition", "E", "--instances", p["b"], "--rep", str(rep)], None))
            if "C" in args.arms:  # frontier emergent, pair protocol (§4.7)
                cdir = str(ROOT / "runs" / "C" / f"pair_{tag}" / f"rep{rep}")
                plan.append((f"C/pair_{tag}", ["--condition", "C", "--instances", p["a"], "--rep", str(rep), "--run-dir", cdir], tag))
                plan.append((f"C/pair_{tag}", ["--condition", "C", "--instances", p["b"], "--rep", str(rep), "--no-learning", "--run-dir", cdir], tag))
            if "A" in args.arms:  # frontier control on B-side
                plan.append(("A", ["--condition", "A", "--instances", p["b"], "--rep", str(rep)], None))
            if "Do" in args.arms:  # D-oracle (§4.3): labeled upper bound, local
                odir = str(ROOT / "runs" / "D_oracle" / f"pair_{tag}" / f"rep{rep}")
                plan.append((f"Do/pair_{tag}", ["--condition", "D", "--oracle", "--instances", p["a"], "--rep", str(rep), "--run-dir", odir], tag))
                plan.append((f"Do/pair_{tag}", ["--condition", "D", "--instances", p["b"], "--rep", str(rep), "--no-learning", "--run-dir", odir], tag))
    # dedupe identical control/assist episodes (same instance+rep may appear in several pairs)
    seen, deduped = set(), []
    for entry in plan:
        key = (entry[0], tuple(entry[1]))
        if key in seen: continue
        seen.add(key); deduped.append(entry)
    total = len(deduped)
    print(f"batch: {total} episodes, arms={args.arms}, reps={args.reps}", flush=True)
    if args.dry_run:
        for s, a, _ in deduped: print(" ", s, " ".join(a))
        return

    for subdir, rc_args, pair_tag in deduped:
        cmd = [PY, RC] + rc_args
        rc = run(cmd, log)
        done += 1
        el = time.time() - t0
        print(f"[{done}/{total}] {' '.join(rc_args)} -> rc={rc}  ({el/60:.0f}m elapsed, "
              f"ETA {(el/done*(total-done))/60:.0f}m)", flush=True)

    print(f"BATCH DONE in {(time.time()-t0)/60:.0f}m", flush=True)


if __name__ == "__main__":
    main()

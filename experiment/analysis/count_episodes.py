#!/usr/bin/env python3
"""Inventory episode and evaluation records in the released artifact.

These are repository-record counts, not a confirmatory sample size: they include
source-task episodes, exploratory arms, and records excluded from individual
analysis frames. Unique (run_id, instance) verdict pairs are reported so repeated
summary rows do not inflate the inventory. Frontier vs local is split out because
only frontier episodes carry API cost.
"""
import collections, glob, json, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTIER = {"A", "A2", "C", "C2", "C_oracle", "opus_ext"}   # Claude Opus executor
EPHEMERAL = {"work", "cache"}


def episode_counts():
    eps = collections.Counter()
    for f in glob.glob(str(ROOT / "runs" / "*" / "**" / "*__*.json"), recursive=True):
        parts = Path(f).relative_to(ROOT / "runs").parts
        if EPHEMERAL & set(parts):
            continue
        eps[parts[0]] += 1
    return eps


def verdict_counts():
    rows, uniq = 0, set()
    for p in (ROOT / "runs" / "eval_summary.jsonl",
              ROOT / "runs" / "opus_ext" / "eval_summary.jsonl"):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            r = json.loads(line)
            rows += 1
            uniq.add((r["run_id"], r["instance_id"]))
    return rows, uniq


def frontier_abort_counts(uniq):
    """Count logged A2 runner failures with no prediction/evaluation record."""
    log = ROOT / "runs" / "batch_frontier2.log"
    failed = {
        (f"eval-A2-rep{rep}", iid)
        for iid, rep in re.findall(
            r"--condition A --instances (\S+) --rep (\d+) --run-dir \S*/runs/A2/rep\d+"
            r" -> rc=[1-9]\d*", log.read_text())
    }
    return failed - uniq


def main():
    eps = episode_counts()
    rows, uniq = verdict_counts()
    aborts = frontier_abort_counts(uniq)
    front = sum(n for a, n in eps.items() if a in FRONTIER)
    local = sum(n for a, n in eps.items() if a not in FRONTIER)

    print("Released per-episode records, by arm")
    for a, n in sorted(eps.items()):
        print(f"  {a:14} {n:6}  {'frontier' if a in FRONTIER else 'local'}")
    print(f"  {'TOTAL':14} {sum(eps.values()):6}")
    print(f"\n  frontier executor : {front:6}")
    print(f"  local executor    : {local:6}")

    print("\nContainerized evaluation verdicts")
    print(f"  rows in eval_summary files      : {rows}")
    print(f"  unique (run_id, instance) pairs : {len(uniq)}")
    if rows != len(uniq):
        print(f"  note: {rows - len(uniq)} duplicate row(s); unique pairs are the count to cite")
    print(f"  planned frontier attempts with logged runner abort and no verdict: {len(aborts)}")

    print("\nArtifact inventory (not a confirmatory sample size):")
    print(f"  episode records  = {sum(eps.values())}  ({front} frontier, {local} local)")
    print(f"  unique evaluation verdicts = {len(uniq)}")
    print(f"  additional logged runner-abort outcomes = {len(aborts)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draw the registered 40-episode consultation hand-audit sample.

PREREGISTRATION-PAPER2 promises a 40-episode random hand-audit of the frozen
consultation detector, reported with Cohen's kappa.

Sampling frame: the 1,602 frozen primary episodes = 267 frozen instances
x 3 repetitions x 2 contract arms (FILE, SHARD). The B and E arms are excluded
because they carry no on-disk context artifact, so the detector's three
constructs are undefined for them.

The draw is uniform without replacement under a fixed seed (default 42) using
numpy's PCG64. It depends only on the frame, never on episode outcomes, so it
cannot be re-rolled toward convenient examples: re-running reproduces the exact
same 40 audit_ids.

Two files are written:
  consultation-hand-audit-40.csv      human-facing, BLINDED (no detector labels)
  consultation-hand-audit-40.key.csv  detector labels, joined by audit_id

Definitions the human labeler applies (frozen protocol §4):
  consulted         a command reads a context artifact
  deep_read         the contents of context.md, or of a context/decisions/*.md
                    file, entered the transcript
  read_before_edit  the qualifying context read happened before the first edit
"""
import argparse, json, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
from templates_p2 import consultation

ARMS = ["FILE", "SHARD"]
REPS = [1, 2, 3]
N_AUDIT = 40


def build_frame():
    frozen = sorted(json.load(open(ROOT / "harness" / "instances_paper2.json"))["instances"])
    rows = [{"arm": a, "instance_id": i, "repetition": r}
            for a in ARMS for r in REPS for i in frozen]
    df = pd.DataFrame(rows).sort_values(["arm", "repetition", "instance_id"]).reset_index(drop=True)
    expected = len(frozen) * len(REPS) * len(ARMS)
    assert len(df) == expected, f"frame is {len(df)}, expected {expected}"
    missing = []
    for row in df.itertuples(index=False):
        path = ROOT / "runs" / row.arm / f"rep{row.repetition}" / f"{row.instance_id}.json"
        if not path.exists():
            missing.append(str(path.relative_to(ROOT)))
    assert not missing, (f"sampling frame is missing {len(missing)} episode log(s); "
                         f"first missing: {missing[:5]}")
    return df, len(frozen)


def render_commands(turns, limit=60):
    """Flatten the turn list into one auditable cell: 'T<n>: <cmd>' entries."""
    out = []
    for rec in turns[:limit]:
        cmd = (rec.get("cmd") or "").strip().replace("\n", " ⏎ ")
        out.append(f"T{rec.get('turn')}: {cmd}")
    if len(turns) > limit:
        out.append(f"... (+{len(turns)-limit} further turns; see transcript_path)")
    return " | ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True,
                    help="where to write the audit files (keep private until labeled)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    out = Path(args.out_dir); out.mkdir(parents=True, exist_ok=True)

    frame, n_frozen = build_frame()
    print(f"sampling frame: {len(frame)} episodes "
          f"({n_frozen} frozen instances x {len(REPS)} reps x {len(ARMS)} arms)")

    rng = np.random.default_rng(args.seed)
    idx = rng.choice(len(frame), size=N_AUDIT, replace=False)
    idx.sort()
    sample = frame.iloc[idx].reset_index(drop=True)
    sample.insert(0, "audit_id", [f"A{i+1:02d}" for i in range(len(sample))])

    human, key, missing = [], [], []
    for row in sample.itertuples(index=False):
        path = ROOT / "runs" / row.arm / f"rep{row.repetition}" / f"{row.instance_id}.json"
        rel = path.relative_to(ROOT)
        if not path.exists():
            missing.append(str(rel)); continue
        ep = json.loads(path.read_text())
        assert ep.get("instance_id") == row.instance_id, f"instance mismatch in {rel}"
        assert ep.get("rep") == row.repetition, f"repetition mismatch in {rel}"
        turns = ep.get("turns", [])
        auto = consultation(turns)
        for field in ("consulted", "deep_read", "read_before_edit",
                      "first_read_turn", "deep_read_turn"):
            assert ep.get(field) == auto[field], (
                f"stored detector field {field} is stale in {rel}: "
                f"stored={ep.get(field)!r}, recomputed={auto[field]!r}")
        human.append({
            "audit_id": row.audit_id, "arm": row.arm,
            "instance_id": row.instance_id, "repetition": row.repetition,
            "transcript_path": str(rel), "n_turns": len(turns),
            "commands": render_commands(turns),
            "manual_consulted": "", "manual_deep_read": "",
            "manual_read_before_edit": "", "manual_unclear": "", "manual_notes": "",
        })
        key.append({
            "audit_id": row.audit_id,
            "auto_consulted": int(auto["consulted"]),
            "auto_deep_read": int(auto["deep_read"]),
            "auto_read_before_edit": int(auto["read_before_edit"]),
            "auto_first_read_turn": auto["first_read_turn"],
            "auto_deep_read_turn": auto["deep_read_turn"],
        })

    if missing:
        raise SystemExit(f"missing episode logs for {len(missing)} sampled rows:\n  "
                         + "\n  ".join(missing))

    hp = out / "consultation-hand-audit-40.csv"
    kp = out / "consultation-hand-audit-40.key.csv"
    pd.DataFrame(human).to_csv(hp, index=False)
    pd.DataFrame(key).to_csv(kp, index=False)

    print(f"seed {args.seed}: drew {len(human)} episodes without replacement")
    print(f"  by arm: {dict(sample.arm.value_counts())}")
    print(f"  blinded audit file -> {hp}")
    print(f"  detector key       -> {kp}")
    print("\nThe blinded file contains NO detector labels. Do not open the key "
          "file before labeling.")


if __name__ == "__main__":
    main()

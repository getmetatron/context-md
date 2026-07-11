#!/usr/bin/env python3
"""Reproduce every empirical number in the paper from the committed run data.

Reads only artifacts under runs/ (episode predictions, eval verdicts) and the
frozen pair files under harness/. Recomputes each claim and checks it against
the value printed in the paper (Section 11). Exits non-zero on any mismatch.

Tier-1 artifact entry point: no network, no agents, no Docker — pure analysis.
"""
import json, re, sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
N_PERM = 10_000


def files_of(patch): return set(re.findall(r"^diff --git a/(\S+)", patch, re.M))


def load_preds(path):
    out = {}
    if path.exists():
        for l in path.read_text().splitlines():
            p = json.loads(l); out[p["instance_id"]] = p["model_patch"]
    return out


def load_verdicts():
    v = {}
    for l in (ROOT / "runs" / "eval_summary.jsonl").read_text().splitlines():
        r = json.loads(l); v[(r["run_id"], r["instance_id"])] = r["resolved"]
    return v


def paired_test(df, arm1, arm0, metric, rng):
    a = df[df.arm == arm1].set_index(["tier", "pair", "rep"])[metric].astype(float)
    b = df[df.arm == arm0].set_index(["tier", "pair", "rep"])[metric].astype(float)
    d = (a - b).dropna()
    obs = d.mean()
    perm = np.array([(d * rng.choice([-1, 1], len(d))).mean() for _ in range(N_PERM)])
    return obs * 100, float((np.abs(perm) >= abs(obs)).mean())


def build_frame(gold_df, verdicts):
    rows = []
    # local arms, both tiers
    rounds = [(1, "harness/pairs_tier1.json", [("B", "B", "eval-B-rep{r}"), ("E", "E", "eval-E-rep{r}"),
                                               ("D", None, None), ("Do", "D_oracle", "eval-D_oracle-p{t}-rep{r}")]),
              (2, "harness/pairs_tier2.json", [("B", "BT2", "eval-BT2-rep{r}"), ("E", "ET2", "eval-ET2-rep{r}"),
                                               ("Do", "D_oracleT2", "eval-D_oracleT2-p{t}-rep{r}")])]
    for tier, pf, arms in rounds:
        pairs = json.loads((ROOT / pf).read_text())["pairs"]
        for rep in range(1, 6):
            flat = {arm: load_preds(ROOT / "runs" / d / f"rep{rep}" / "predictions.jsonl")
                    for arm, d, _ in arms if d and "pair" not in (d or "") and arm in ("B", "E")}
            for p in pairs:
                tag = f"{p['a'].split('-')[-1]}_{p['b'].split('-')[-1]}"
                b = p["b"]; gold = files_of(gold_df.loc[b, "patch"])
                for arm, d, ridt in arms:
                    if arm == "D":  # tier-1 emergent, pair-scoped
                        store = load_preds(ROOT / "runs" / "D" / f"pair_{tag}" / f"rep{rep}" / "predictions.jsonl")
                        rid = f"eval-D-p{tag}-rep{rep}"
                    elif arm == "Do":
                        store = load_preds(ROOT / "runs" / d / f"pair_{tag}" / f"rep{rep}" / "predictions.jsonl")
                        rid = ridt.format(t=tag, r=rep)
                    else:
                        store = flat[arm]; rid = ridt.format(r=rep)
                    patch = store.get(b, "")
                    rows.append(dict(tier=tier, arm=arm, pair=tag, rep=rep,
                                     gold_hit=bool(files_of(patch) & gold),
                                     resolved=verdicts.get((rid, b), False)))
    # frontier stratified arms
    pairs = json.loads((ROOT / "harness" / "pairs_frontier.json").read_text())["pairs"]
    for rep in range(1, 4):
        ap = load_preds(ROOT / "runs" / "A2" / f"rep{rep}" / "predictions.jsonl")
        for p in pairs:
            tag = f"{p['a'].split('-')[-1]}_{p['b'].split('-')[-1]}"
            b = p["b"]; gold = files_of(gold_df.loc[b, "patch"])
            cp = load_preds(ROOT / "runs" / "C2" / f"pair_{tag}" / f"rep{rep}" / "predictions.jsonl")
            for arm, store, rid in (("C2", cp, f"eval-C2-p{tag}-rep{rep}"), ("A2", ap, f"eval-A2-rep{rep}")):
                patch = store.get(b, "")
                rows.append(dict(tier=0, arm=arm, pair=tag, rep=rep,
                                 gold_hit=bool(files_of(patch) & gold),
                                 resolved=verdicts.get((rid, b), False)))
    return pd.DataFrame(rows)


CLAIMS = []  # (label, computed, expected, tolerance)


def claim(label, computed, expected, tol):
    CLAIMS.append((label, computed, expected, tol))


def main():
    gold_df = pd.read_parquet(ROOT / "data" / "swebench_verified.parquet").set_index("instance_id")
    t = build_frame(gold_df, load_verdicts())

    # --- frontier stratified (paper 11.2, para 1; Figure 2) ---
    f = t[t.tier == 0]
    a_res = f[f.arm == "A2"].resolved.mean() * 100
    c_res = f[f.arm == "C2"].resolved.mean() * 100
    claim("frontier A resolve %", a_res, 58.3, 0.1)
    claim("frontier C resolve %", c_res, 72.9, 0.1)
    rng = np.random.default_rng(SEED)
    d, p = paired_test(f.assign(tier=0), "C2", "A2", "resolved", rng)
    claim("frontier C-A resolve delta pp", d, 14.6, 0.1)
    claim("frontier C-A resolve p", p, 0.041, 0.01)

    # --- pooled local (paper 11.2, para 2; Figure 3) ---
    loc = t[t.arm.isin(["B", "E", "Do"])]
    for arm, exp in (("B", 21.1), ("E", 47.2), ("Do", 42.8)):
        claim(f"pooled {arm} gold-hit %", loc[loc.arm == arm].gold_hit.mean() * 100, exp, 0.1)
    rng = np.random.default_rng(SEED)
    for arm, metric, exp_d, exp_p, tol_p in (("E", "gold_hit", 26.1, 0.0, 0.001),
                                             ("Do", "gold_hit", 21.7, 0.0, 0.001),
                                             ("Do", "resolved", 2.2, 0.22, 0.03)):
        d, p = paired_test(loc, arm, "B", metric, rng)
        claim(f"pooled {arm}-B {metric} delta pp", d, exp_d, 0.1)
        claim(f"pooled {arm}-B {metric} p", p, exp_p, tol_p)

    # --- tier-1 self-authored null (paper 11.2, para 3) ---
    t1 = t[(t.tier == 1) & t.arm.isin(["D", "B"])]
    rng = np.random.default_rng(SEED)
    d, p = paired_test(t1, "D", "B", "gold_hit", rng)
    claim("tier1 D-B gold-hit delta pp", d, 0.0, 0.1)
    claim("tier1 D-B gold-hit p", p, 1.0, 0.01)

    # --- report ---
    print(f"{'claim':44s} {'computed':>10s} {'paper':>8s}  verdict")
    print("-" * 76)
    fails = 0
    for label, comp, exp, tol in CLAIMS:
        ok = abs(comp - exp) <= tol
        fails += not ok
        print(f"{label:44s} {comp:10.3f} {exp:8.3f}  {'PASS' if ok else 'FAIL'}")
    print("-" * 76)
    print(f"{len(CLAIMS) - fails}/{len(CLAIMS)} claims reproduced")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

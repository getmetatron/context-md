#!/usr/bin/env python3
"""Verify every number the camera-ready changed or added.

reproduce_paper.py (frozen, released) covers the submitted claims. This script
covers the ones this revision introduces or corrects, so nothing new is asserted
in the text without a check behind it. Exits non-zero on any mismatch.
"""
import glob, json, re, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"analysis"))
import reproduce_paper as R

OK = "✓"
fails = []

def check(label, got, exp, tol):
    ok = abs(got-exp) <= tol
    print(f"  {OK if ok else 'X'} {label:52} got {got:9.3f}  expect {exp:.3f}")
    if not ok: fails.append(label)

ver = pd.read_parquet(ROOT/"data"/"swebench_verified.parquet").set_index("instance_id")
t = R.build_frame(ver, R.load_verdicts())

print("\nFrontier per-group direction (§10.3, Fig 3 caption) --- corrected from '8 of 11'")
txt = (ROOT/"FINDINGS-02-confirmed-transfer-pairs.md").read_text()
grp, cur = {}, None
for line in txt.splitlines():
    m = re.match(r'^### ([A-Z]\d+)\.', line)
    if m: cur = m.group(1); grp[cur] = set()
    if cur:
        for n in re.findall(r'`[\w-]+__[\w.-]+-(\d+)`', line): grp[cur].add(n)
gof = {i: k for k, v in grp.items() for i in v}
f = t[t.tier == 0].copy(); f["grp"] = f.pair.str.split("_").str[1].map(gof)
p = f.pivot_table(index="grp", columns="arm", values="resolved", aggfunc="mean")
d = p.C2 - p.A2
check("constraint groups", len(d), 11, 0)
check("groups improving", (d > 0).sum(), 7, 0)
check("groups flat", (d == 0).sum(), 3, 0)
check("groups declining", (d < 0).sum(), 1, 0)

print("\nHolm correction on the frontier family (§10.3, abstract)")
_, p_res = R.paired_test(f, "C2", "A2", "resolved", np.random.default_rng(R.SEED))
_, p_loc = R.paired_test(f, "C2", "A2", "gold_hit", np.random.default_rng(R.SEED))
ps = sorted([p_res, p_loc])
holm = max(ps[0]*2, ps[1])
check("raw resolve p", p_res, 0.041, 0.01)
check("raw localization p", p_loc, 0.064, 0.01)
check("Holm-adjusted p (family of 2)", holm, 0.082, 0.02)

print("\nSeed leakage (§10.7, Table 4)")
import seed_leakage as SL
pairs = []
for cond in ("D_oracle", "D_oracleT2"):
    for dd in sorted((ROOT/"runs"/cond).glob("pair_*")):
        ids = sorted(x.stem for x in (dd/"rep1").glob("*.json")) if (dd/"rep1").exists() else []
        if len(ids) != 2: continue
        a, b = dd.name.split("_")[1:3]
        bid = next((i for i in ids if i.endswith(f"-{b}")), None)
        aid = next((i for i in ids if i.endswith(f"-{a}")), None)
        if bid: pairs.append((bid, aid, SL.SLUG_OF[ver.loc[bid, "repo"]]))
study = {i for b, a, _ in pairs for i in (b, a)}
sc = [SL.score((ROOT/"seeds"/s/"context.md").read_text(), ver.loc[b, "patch"]) for b, a, s in pairs]
check("names a gold file, held-out B (%)", 100*np.mean([x["file_hit"] for x in sc]), 83.3, 0.2)
check("names a gold symbol, held-out B (%)", 100*np.mean([x["sym_hit"] for x in sc]), 55.6, 0.2)
nul = []
for slug, repo in SL.REPO_OF.items():
    fp = ROOT/"seeds"/slug/"context.md"
    if not fp.exists() or slug not in ("django", "sphinx", "xarray"): continue
    tx = fp.read_text()
    for iid, r in ver[(ver.repo == repo) & (~ver.index.isin(study))].iterrows():
        nul.append(SL.score(tx, r["patch"]))
check("non-study n (3 repos)", len(nul), 257, 0)
check("names a gold file, non-study (%)", 100*np.mean([x["file_hit"] for x in nul]), 32.3, 0.2)
check("names a gold symbol, non-study (%)", 100*np.mean([x["sym_hit"] for x in nul]), 3.9, 0.2)

print("\nCeiling arm (§10.5, Fig 5) --- recomputed from episode logs")
rows = []
for arm in ("B", "E", "FILE", "SHARD"):
    for fp in glob.glob(str(ROOT/f"runs/opus_ext/{arm}/rep1/*__*.json")):
        e = json.load(open(fp))
        rows.append(dict(arm=arm, iid=e["instance_id"], pt=e["prompt_tokens"],
                         ct=e["completion_tokens"], consulted=e["consulted"]))
df = pd.DataFrame(rows)
res = {}
for l in open(ROOT/"runs"/"opus_ext"/"eval_summary.jsonl"):
    r = json.loads(l); res[(r["run_id"], r["instance_id"])] = r["resolved"]
df["resolved"] = [res.get((f"eval-opus-ext-{a}", i), False) for a, i in zip(df.arm, df.iid)]
check("no-context resolve (%)", 100*df[df.arm == "B"].resolved.mean(), 90.9, 0.1)
check("SHARD prompt tokens (K)", df[df.arm == "SHARD"].pt.mean()/1000, 38.4, 0.1)
check("FILE prompt tokens (K)", df[df.arm == "FILE"].pt.mean()/1000, 24.0, 0.1)
check("FILE+SHARD consultation (%)", 100*df[df.arm.isin(["FILE", "SHARD"])].consulted.mean(), 100.0, 0.1)

print("\nToken economics (§10.6, Fig 4)")
b5 = pd.read_csv(ROOT/"runs"/"analysis_bsides_05.csv")
for arm, exp in (("A2", 81.8), ("C2", 55.7)):
    s = b5[b5.arm == arm]
    check(f"{arm} tokens per resolved (K)", s.tok.sum()/s.resolved.sum()/1000, exp, 0.15)

print(f"\n{'FAILED: ' + ', '.join(fails) if fails else 'all camera-ready claims verified'}\n")
sys.exit(1 if fails else 0)

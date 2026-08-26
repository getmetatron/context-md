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


def require_keys(mapping, expected, label):
    missing = set(expected) - set(mapping)
    if missing:
        raise AssertionError(f"missing {len(missing)} {label}(s): {sorted(missing)[:5]}")

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
rng = np.random.default_rng(R.SEED)
_, p_res = R.paired_test(f, "C2", "A2", "resolved", rng)
_, p_loc = R.paired_test(f, "C2", "A2", "gold_hit", rng)
ps = sorted([p_res, p_loc])
holm = max(ps[0]*2, ps[1])
check("raw resolve p", p_res, 0.0406, 1e-9)
check("raw localization p", p_loc, 0.0637, 1e-9)
check("Holm-adjusted p (family of 2)", holm, 0.0812, 1e-9)

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
check("identifier Jaccard, held-out B", np.mean([x["jaccard"] for x in sc]), 0.019, 0.0005)
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
check("identifier Jaccard, non-study", np.mean([x["jaccard"] for x in nul]), 0.013, 0.0005)

print("\nCeiling arm (§10.5, Fig 5) --- recomputed from episode logs")
rows = []
for arm in ("B", "E", "FILE", "SHARD"):
    for fp in glob.glob(str(ROOT/f"runs/opus_ext/{arm}/rep1/*__*.json")):
        e = json.load(open(fp))
        rows.append(dict(arm=arm, iid=e["instance_id"], pt=e["prompt_tokens"],
                         ct=e["completion_tokens"], consulted=e["consulted"]))
df = pd.DataFrame(rows)
check("ceiling episodes total", len(df), 352, 0)
for arm in ("B", "E", "FILE", "SHARD"):
    check(f"  ceiling {arm}: episodes", len(df[df.arm == arm]), 88, 0)
res = {}
for l in open(ROOT/"runs"/"opus_ext"/"eval_summary.jsonl"):
    r = json.loads(l); res[(r["run_id"], r["instance_id"])] = r["resolved"]
expected_ceiling = {(f"eval-opus-ext-{a}", i) for a, i in zip(df.arm, df.iid)}
require_keys(res, expected_ceiling, "ceiling evaluation verdict")
df["resolved"] = [res[(f"eval-opus-ext-{a}", i)] for a, i in zip(df.arm, df.iid)]
for arm, rate, prompt, cost in (("B", 90.9, 25.8, 28.8),
                                ("E", 81.8, 23.5, 29.2),
                                ("FILE", 85.2, 24.0, 28.7),
                                ("SHARD", 88.6, 38.4, 43.8)):
    s = df[df.arm == arm]
    check(f"  ceiling {arm}: resolve (%)", 100*s.resolved.mean(), rate, 0.05)
    check(f"  ceiling {arm}: prompt tokens (K)", s.pt.mean()/1000, prompt, 0.05)
    check(f"  ceiling {arm}: tokens/resolved (K)", (s.pt.sum()+s.ct.sum())/s.resolved.sum()/1000,
          cost, 0.05)
check("FILE+SHARD consultation (%)", 100*df[df.arm.isin(["FILE", "SHARD"])].consulted.mean(), 100.0, 0.1)

print("\nToken economics (§10.6, Fig 4)")
b5 = pd.read_csv(ROOT/"runs"/"analysis_bsides_05.csv")
for arm, exp in (("A2", 81.8), ("C2", 55.7)):
    s = b5[b5.arm == arm]
    check(f"{arm} tokens per resolved (K)", s.tok.sum()/s.resolved.sum()/1000, exp, 0.15)

print("\nDelivery matrix (Table 3, §10.4) --- recomputed from the released episodes")
sys.path.insert(0, str(ROOT/"analysis"))
import analyze_p2 as AP  # noqa: E402

_gold = AP.load_gold()
_frozen = set(json.load(open(ROOT/"harness"/"instances_paper2.json"))["instances"])
_gold = {k: v for k, v in _gold.items() if k in _frozen}
_seed_toks, _file_toks = AP.build_artifacts()
_df, _ = AP.load_episodes(_gold, _seed_toks, _file_toks)

check("delivery episodes total", len(_df), 3204, 0)
for arm in ("B", "E", "FILE", "SHARD"):
    check(f"  {arm}: episodes", len(_df[_df.arm == arm]), 801, 0)

# Table 3, column by column, against the values printed in the paper
for arm, loc, ctx, res in (("B", 48.6, 0, 5.6), ("E", 51.2, 930, 8.6),
                           ("FILE", 46.8, 902, 7.0), ("SHARD", 53.4, 305, 6.7)):
    s = _df[_df.arm == arm]
    check(f"  {arm}: localization (%)", 100*s.gold_hit.mean(), loc, 0.05)
    check(f"  {arm}: ctx tokens/episode", s.ctx_tokens.mean(), ctx, 1.0)
for arm in ("FILE", "SHARD"):
    check(f"  {arm}: consulted (%)", 100*_df[_df.arm == arm].consulted.mean(), 97.0, 0.5)

# resolve comes from the containerized verdicts, not the episode logs
_res = {}
for l in open(ROOT/"runs"/"eval_summary.jsonl"):
    r = json.loads(l); _res[(r["run_id"], r["instance_id"])] = r["resolved"]
_runid = {"B": "eval-P2-B-rep{}", "E": "eval-P2-E-rep{}",
          "FILE": "eval-FILE-rep{}", "SHARD": "eval-SHARD-rep{}"}
expected_delivery = {(_runid[arm].format(r), i)
                     for arm in _runid for r in (1, 2, 3) for i in _frozen}
require_keys(_res, expected_delivery, "delivery evaluation verdict")
for arm, exp in (("B", 5.6), ("E", 8.6), ("FILE", 7.0), ("SHARD", 6.7)):
    vals = [_res[(_runid[arm].format(r), i)]
            for r in (1, 2, 3) for i in sorted(_frozen)]
    check(f"  {arm}: resolve (%)", 100*np.mean(vals), exp, 0.05)

# The two contrasts the paper reports. Use analyze_p2's own `paired` and
# `holm` helpers rather than reimplementing them: the sign-flip p-value depends
# on the ordering of the paired deltas under a fixed seed, so an independent
# reimplementation is not bit-identical to the released analysis.
_fam = [("FILE", "B"), ("SHARD", "B"), ("E", "B"), ("FILE", "E")]
_res = [AP.signflip(AP.paired(_df, "gold_hit", a, b)) for a, b in _fam]
_adj = AP.holm([r[1] for r in _res])
_by = {f"{a}-{b}": (obs, p, n, ph)
       for (a, b), (obs, p, n), ph in zip(_fam, _res, _adj)}

_obs, _p, _n, _ph = _by["SHARD-B"]
check("  SHARD-B delta (pp)", 100*_obs, 4.9, 0.05)
check("  SHARD-B raw p", _p, 0.0144, 0.001)
check("  SHARD-B Holm p (4-test family)", _ph, 0.058, 0.001)
check("  SHARD-B paired n", _n, 801, 0)

_obs2, _p2, _n2 = AP.signflip(AP.paired(_df, "gold_hit", "SHARD", "FILE"))
check("  SHARD-FILE delta (pp), exploratory", 100*_obs2, 6.6, 0.05)
check("  SHARD-FILE p, exploratory", _p2, 0.0007, 0.0002)

# Registered H3 token family reported in §10.4.
_tok_fam = [("SHARD", "FILE"), ("FILE", "E")]
_tok_res = [AP.signflip(AP.paired(_df, "ctx_tokens", a, b), one_sided=True)
            for a, b in _tok_fam]
_tok_adj = AP.holm([r[1] for r in _tok_res])
for (a, b), (obs, p, n), ph, exp_delta in zip(
        _tok_fam, _tok_res, _tok_adj, (-597.2, -27.5)):
    check(f"  {a}<{b} token delta", obs, exp_delta, 0.05)
    check(f"  {a}<{b} raw p", p, 1/10001, 1e-12)
    check(f"  {a}<{b} Holm p", ph, 2/10001, 1e-12)
    check(f"  {a}<{b} paired n", n, 801, 0)

print("\nConsultation-detector author verification (§10.4)")
import consultation_audit_analyze as CA  # noqa: E402

_audit_dir = ROOT/"audit" if (ROOT/"audit").exists() else ROOT/"private"
_audit = pd.read_csv(_audit_dir/"consultation-hand-audit-40.csv")
_key = pd.read_csv(_audit_dir/"consultation-hand-audit-40.key.csv")
_expected_ids = {f"A{i:02d}" for i in range(1, 41)}
assert set(_audit.audit_id) == _expected_ids
assert set(_key.audit_id) == _expected_ids
_audit = _audit.merge(_key, on="audit_id", validate="one_to_one")
_unclear = _audit.manual_unclear.apply(CA.to01)
check("  audit rows", len(_audit), 40, 0)
check("  unclear rows", sum(v == 1 for v in _unclear), 0, 0)
for name, mcol, acol in CA.METRICS:
    _m = _audit[mcol].apply(CA.to01).to_numpy()
    _a = _audit[acol].apply(CA.to01).to_numpy()
    assert None not in _m and None not in _a
    _kap, _note = CA.cohens_kappa(_m, _a)
    assert _note is None and _kap is not None
    _cm = CA.confusion(_m, _a)
    check(f"  {name}: author positives", _m.sum(), 38, 0)
    check(f"  {name}: detector positives", _a.sum(), 38, 0)
    check(f"  {name}: raw agreement (%)", 100*(_m == _a).mean(), 100, 0)
    check(f"  {name}: kappa (descriptive)", _kap, 1, 0)
    check(f"  {name}: both negative", _cm["both_negative"], 2, 0)

print(f"\n{'FAILED: ' + ', '.join(fails) if fails else 'all checked camera-ready claims verified'}\n")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""Seed-blindness leakage check (reviewer 22C, camera-ready AgenticDev 2026).

Question: does the blind frontier-authored seed behave like a partial gold
distillation?  We measure, for every held-out B instance in the frozen 36-pair
set, how much of that instance's GOLD PATCH is already named by the context the
executor was given.

Three context sources are scored on identical metrics:
  blind   -- seeds/<repo>/context.md      (author saw checkout + group names only)
  oracle  -- runs/D_oracle*/<pair>/rep1/context/<repo>.md  (author saw gold patch)
  null    -- blind seed scored against gold patches of same-repo instances that
             are NOT in the study set (what generic repo knowledge hits by chance)

If blind sits near null and far below oracle, contamination does not explain the
gradient.  Written for the camera-ready; does not modify any frozen artifact.
"""
import json, re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]      # rcl-experiment/
RUNS, SEEDS, DATA = ROOT/"runs", ROOT/"seeds", ROOT/"data"

REPO_OF = {"django": "django/django", "sphinx": "sphinx-doc/sphinx",
           "xarray": "pydata/xarray", "astropy": "astropy/astropy",
           "matplotlib": "matplotlib/matplotlib", "pytest": "pytest-dev/pytest",
           "scikit-learn": "scikit-learn/scikit-learn", "sympy": "sympy/sympy"}
SLUG_OF = {v: k for k, v in REPO_OF.items()}

# ---------------------------------------------------------------- gold patches
def patch_files(patch: str):
    """Repo-relative paths the gold patch edits."""
    return {m.group(1) for m in re.finditer(r'^diff --git a/(\S+) b/', patch, re.M)}

def patch_symbols(patch: str):
    """Function/class names the gold patch touches: hunk-header context plus any
    def/class introduced or removed inside the hunk body."""
    syms = set()
    for m in re.finditer(r'^@@[^@]*@@\s*(.*)$', patch, re.M):
        for s in re.findall(r'(?:def|class)\s+(\w+)', m.group(1)):
            syms.add(s)
    for m in re.finditer(r'^[+-]\s*(?:async\s+)?(?:def|class)\s+(\w+)', patch, re.M):
        syms.add(m.group(1))
    return {s for s in syms if not s.startswith('__')}

def patch_identifiers(patch: str):
    """Identifier bag from added/removed lines only (ignores diff context)."""
    body = "\n".join(l[1:] for l in patch.splitlines()
                     if l[:1] in "+-" and not l.startswith(('+++', '---')))
    return {t for t in re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', body)}

# -------------------------------------------------------------------- contexts
def ctx_paths(text: str):
    return set(re.findall(r'[\w./-]+\.py', text))

def ctx_symbols(text: str):
    """Symbols the context names: backticked identifiers and dotted calls."""
    syms = set()
    for tok in re.findall(r'`([^`]+)`', text):
        syms |= set(re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', tok))
    return syms

def ctx_identifiers(text: str):
    return {t for t in re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', text)}

# ----------------------------------------------------------------------- score
def score(ctx_text, patch):
    cp, cs, ci = ctx_paths(ctx_text), ctx_symbols(ctx_text), ctx_identifiers(ctx_text)
    gf, gs, gi = patch_files(patch), patch_symbols(patch), patch_identifiers(patch)
    # a gold file counts as named if the context names its path or its basename
    file_hit = any(f in cp or any(Path(p).name == Path(f).name for p in cp) for f in gf)
    sym_hit  = bool(gs & cs)
    jac = len(ci & gi) / len(ci | gi) if (ci | gi) else 0.0
    return dict(file_hit=file_hit, sym_hit=sym_hit,
                file_frac=(sum(1 for f in gf if f in cp or any(Path(p).name == Path(f).name for p in cp))/len(gf)) if gf else 0.0,
                sym_frac=(len(gs & cs)/len(gs)) if gs else float('nan'),
                jaccard=jac, n_gold_files=len(gf), n_gold_syms=len(gs))

def main():
    ver = pd.read_parquet(DATA/"swebench_verified.parquet").set_index("instance_id")

    pairs = []
    for cond in ("D_oracle", "D_oracleT2"):
        for d in sorted((RUNS/cond).glob("pair_*")):
            ids = sorted(p.stem for p in (d/"rep1").glob("*.json")) if (d/"rep1").exists() else []
            if len(ids) != 2:
                continue
            a_num, b_num = d.name.split("_")[1:3]
            b_id = next((i for i in ids if i.endswith(f"-{b_num}")), None)
            a_id = next((i for i in ids if i.endswith(f"-{a_num}")), None)
            if b_id is None:
                continue
            pairs.append(dict(cond=cond, pair=d.name, dir=d, a_id=a_id, b_id=b_id,
                              slug=SLUG_OF[ver.loc[b_id, "repo"]]))

    study_ids = {p["b_id"] for p in pairs} | {p["a_id"] for p in pairs}
    rows = []
    for p in pairs:
        gold = ver.loc[p["b_id"], "patch"]
        blind_f = SEEDS/p["slug"]/"context.md"
        if blind_f.exists():
            rows.append(dict(arm="blind", **p_meta(p), **score(blind_f.read_text(), gold)))
        orc = p["dir"]/"rep1"/"context"/f"{p['slug']}.md"
        if orc.exists():
            rows.append(dict(arm="oracle", **p_meta(p), **score(orc.read_text(), gold)))

    # null baseline: blind seed vs same-repo instances outside the study set
    for slug, repo in REPO_OF.items():
        blind_f = SEEDS/slug/"context.md"
        if not blind_f.exists():
            continue
        text = blind_f.read_text()
        others = ver[(ver.repo == repo) & (~ver.index.isin(study_ids))]
        for iid, r in others.iterrows():
            rows.append(dict(arm="null", pair="-", b_id=iid, slug=slug,
                             **score(text, r["patch"])))

    df = pd.DataFrame(rows)
    out = Path(__file__).parent/"seed_leakage.csv"
    df.to_csv(out, index=False)

    print(f"pairs={len(pairs)}  rows={len(df)}   -> {out.name}\n")
    print("Leakage of the held-out gold patch into the context the executor read")
    print("(blind = frontier seed, oracle = gold-shown author, null = blind seed vs")
    print(" same-repo instances outside the study set)\n")
    hdr = f"{'arm':8}{'n':>5}{'names gold file':>17}{'names gold symbol':>19}{'gold files named':>18}{'identifier Jaccard':>20}"
    print(hdr); print("-"*len(hdr))
    for arm in ("blind", "oracle", "null"):
        s = df[df.arm == arm]
        if s.empty: continue
        print(f"{arm:8}{len(s):>5}{s.file_hit.mean():>16.1%}{s.sym_hit.mean():>19.1%}"
              f"{s.file_frac.mean():>18.1%}{s.jaccard.mean():>20.3f}")

    # restrict null to the three transfer-study repos for a like-for-like read
    tri = df[(df.arm == "null") & (df.slug.isin(["django", "sphinx", "xarray"]))]
    print(f"\n{'null(3 repos)':21}{len(tri):>4}{tri.file_hit.mean():>15.1%}"
          f"{tri.sym_hit.mean():>19.1%}{tri.file_frac.mean():>18.1%}{tri.jaccard.mean():>20.3f}")

def p_meta(p):
    return dict(pair=p["pair"], b_id=p["b_id"], slug=p["slug"])

if __name__ == "__main__":
    main()


# ============================ v2: novel-identifier leakage + positive control ==
def novel_identifiers(patch: str):
    """Identifiers the fix INTRODUCES: present on '+' lines, absent from '-'
    lines and from hunk context lines.  Naming one of these is evidence the
    context encodes the answer rather than the terrain."""
    added, preexisting = set(), set()
    for l in patch.splitlines():
        if l.startswith(('+++', '---', 'diff --git', 'index ', '@@')):
            if l.startswith('@@'):
                preexisting |= set(re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', l))
            continue
        toks = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', l[1:] if l[:1] in '+- ' else l))
        if l.startswith('+'):
            added |= toks
        else:
            preexisting |= toks
    return added - preexisting


def v2():
    ver = pd.read_parquet(DATA/"swebench_verified.parquet").set_index("instance_id")
    pairs = []
    for cond in ("D_oracle", "D_oracleT2"):
        for d in sorted((RUNS/cond).glob("pair_*")):
            ids = sorted(p.stem for p in (d/"rep1").glob("*.json")) if (d/"rep1").exists() else []
            if len(ids) != 2: continue
            a_num, b_num = d.name.split("_")[1:3]
            a_id = next((i for i in ids if i.endswith(f"-{a_num}")), None)
            b_id = next((i for i in ids if i.endswith(f"-{b_num}")), None)
            if not (a_id and b_id): continue
            pairs.append((d, a_id, b_id, SLUG_OF[ver.loc[b_id, "repo"]]))

    study = {i for _, a, b, _ in pairs for i in (a, b)}
    def hit(text, ids): return bool(set(re.findall(r'[A-Za-z_][A-Za-z0-9_]{2,}', text)) & ids)

    res = {}
    # blind seed vs the HELD-OUT instance it must not know
    v = [(hit(( SEEDS/s/"context.md").read_text(), novel_identifiers(ver.loc[b, "patch"])),
          len(novel_identifiers(ver.loc[b, "patch"])))
         for _, a, b, s in pairs if (SEEDS/s/"context.md").exists()]
    res["blind seed vs held-out B"] = v

    # positive control: oracle context vs the A patch its author was SHOWN
    ctl = []
    for d, a, b, s in pairs:
        f = d/"rep1"/"context"/f"{s}.md"
        if f.exists():
            ctl.append((hit(f.read_text(), novel_identifiers(ver.loc[a, "patch"])),
                        len(novel_identifiers(ver.loc[a, "patch"]))))
    res["oracle ctx vs its own shown A"] = ctl

    # null: blind seed vs same-repo instances outside the study set
    nul = []
    for slug, repo in REPO_OF.items():
        f = SEEDS/slug/"context.md"
        if not f.exists(): continue
        t = f.read_text()
        for iid, r in ver[(ver.repo == repo) & (~ver.index.isin(study))].iterrows():
            nv = novel_identifiers(r["patch"])
            nul.append((hit(t, nv), len(nv)))
    res["blind seed vs non-study same-repo"] = nul

    print("\n\n=== Novel-identifier leakage (identifiers the gold patch INTRODUCES) ===")
    print("Does the context name any token the fix invents?  A gold-distilled")
    print("context should; a terrain-only context should not.\n")
    w = max(len(k) for k in res)
    print(f"{'source':{w}}{'n':>6}{'names a novel id':>19}{'mean novel ids/patch':>23}")
    print("-"*(w+48))
    for k, v in res.items():
        if not v: continue
        print(f"{k:{w}}{len(v):>6}{sum(x for x, _ in v)/len(v):>18.1%}{sum(n for _, n in v)/len(v):>23.1f}")

if __name__ != "__main__":
    pass

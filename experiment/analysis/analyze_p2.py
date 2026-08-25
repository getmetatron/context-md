#!/usr/bin/env python3
"""Paper 2 confirmatory analysis (PREREGISTRATION-PAPER2, frozen prereg2-v1).

Implements exactly the frozen plan:
  H1 (§3): consultation / deep-read rates under FILE and SHARD (band 0.90-1.00).
  H2 (§3): gold-file-hit paired deltas F-B, S-B, I-B, F-I; sign-flip permutation
           on per-instance x rep paired deltas, 10k draws, seed 42, Holm within
           the 4-test family. S-F reported as exploratory (outside the family).
  H3 (§3): context-tokens-paid contrasts S<F<I (S-F and F-I, one-sided), same
           permutation machinery, own Holm family.
  §4: context-tokens-paid — I = tokenized injected seed block; F/S = tokenized
      context-file content echoed into the transcript by read commands
      (cat/head/tail/sed of context.md or a decision file; each read event
      counts the full file once — an upper bound for partial reads).
      Tokenizer proxy: words x 4/3 (identical to prereg-v1 §4.1).
  §6: empty patches = gold-miss; aborts (no episode log) excluded symmetrically
      and reported per arm.
"""
import json, re, sys, tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))
from templates_p2 import write_context_files, CONTRACT_BLOCK_P2  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
ARMS = ["B", "E", "FILE", "SHARD"]
REPS = [1, 2, 3]

REPO_DIR = {"astropy": "astropy", "django": "django", "matplotlib": "matplotlib",
            "pydata": "xarray", "pytest-dev": "pytest",
            "scikit-learn": "scikit-learn", "sphinx-doc": "sphinx", "sympy": "sympy"}

DIFF_FILE_RE = re.compile(r"^diff --git a/(\S+) b/", re.M)
READ_TOKENS_RE = re.compile(r"^(cat|head|tail|sed)\b[^\n]*?(context\.md|context/decisions/\S+\.md)", re.M)


def toks(text):
    return len(text.split()) * 4 // 3


def patch_files(patch):
    return set(DIFF_FILE_RE.findall(patch or ""))


def load_gold():
    df = pd.read_parquet(ROOT / "data" / "swebench_verified.parquet")
    return {r.instance_id: patch_files(r.patch) for r in df.itertuples()}


def build_artifacts():
    """Regenerate the exact F/S artifacts per repo; return token maps + seed toks."""
    seed_toks, file_toks = {}, {}          # repo -> injected toks; (repo,mode,relpath) -> toks
    for repo in set(REPO_DIR.values()):
        seed = (ROOT / "seeds" / repo / "context.md").read_text()
        seed_toks[repo] = toks(seed)
        for mode in ("file", "sharded"):
            with tempfile.TemporaryDirectory() as td:
                td = Path(td)
                write_context_files(td, seed, mode)
                for f in td.rglob("*.md"):
                    file_toks[(repo, mode, str(f.relative_to(td)))] = toks(f.read_text())
    return seed_toks, file_toks


def ctx_tokens(ep, repo, seed_toks, file_toks):
    cond = ep["condition"]
    if cond == "B":
        return 0
    if cond == "E":
        return seed_toks[repo]
    mode = "file" if cond == "FILE" else "sharded"
    total = 0
    for rec in ep["turns"]:
        cmd = rec.get("cmd") or ""
        for m in READ_TOKENS_RE.finditer(cmd):
            ref = m.group(2)
            if ref == "context.md":
                total += file_toks[(repo, mode, "context.md")]
            else:
                # normalize to the relative path written by write_context_files
                rel = ref[ref.index("context/"):]
                total += file_toks.get((repo, mode, rel), 0)  # unknown file -> 0
    return total


def load_episodes(gold, seed_toks, file_toks):
    rows, missing = [], defaultdict(int)
    for arm in ARMS:
        for rep in REPS:
            d = RUNS / arm / f"rep{rep}"
            preds = {}
            pf = d / "predictions.jsonl"
            if pf.exists():
                for line in pf.read_text().splitlines():
                    p = json.loads(line)
                    preds[p["instance_id"]] = p["model_patch"]
            for f in sorted(d.glob("*.json")):
                ep = json.loads(f.read_text())
                iid = ep["instance_id"]
                if iid not in gold:
                    continue
                patch = preds.get(iid, "")
                hit = bool(patch_files(patch) & gold[iid])   # empty patch => miss (§3)
                rows.append({
                    "arm": arm, "rep": rep, "iid": iid,
                    "repo": REPO_DIR[iid.split("__")[0]],
                    "gold_hit": int(hit),
                    "submitted": int(bool(patch.strip())),
                    "consulted": int(bool(ep.get("consulted"))),
                    "deep_read": int(bool(ep.get("deep_read"))),
                    "read_before_edit": int(bool(ep.get("read_before_edit"))),
                    "prompt_tokens": ep.get("prompt_tokens", 0),
                    "completion_tokens": ep.get("completion_tokens", 0),
                    "ctx_tokens": ctx_tokens(ep, REPO_DIR[iid.split("__")[0]],
                                             seed_toks, file_toks),
                })
    return pd.DataFrame(rows), missing


def signflip(deltas, n=10_000, seed=42, one_sided=False):
    """Sign-flip permutation on paired deltas. Two-sided unless one_sided
    (H3: tests mean(delta) < 0)."""
    d = np.asarray(deltas, dtype=float)
    d = d[~np.isnan(d)]
    obs = d.mean()
    rng = np.random.default_rng(seed)
    flips = rng.choice([-1.0, 1.0], size=(n, d.size))
    null = (flips * d).mean(axis=1)
    if one_sided:
        p = (np.sum(null <= obs) + 1) / (n + 1)
    else:
        p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (n + 1)
    return obs, p, d.size


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj, running = [None] * m, 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * pvals[idx])
        adj[idx] = min(1.0, running)
    return adj


def paired(df, metric, a, b):
    pa = df[df.arm == a].set_index(["iid", "rep"])[metric]
    pb = df[df.arm == b].set_index(["iid", "rep"])[metric]
    j = pa.to_frame("a").join(pb.to_frame("b"), how="inner")
    return (j.a - j.b).values


def main():
    frozen = set(json.load(open(ROOT / "harness" / "instances_paper2.json"))["instances"])
    gold = load_gold()
    gold = {k: v for k, v in gold.items() if k in frozen}
    seed_toks, file_toks = build_artifacts()
    df, _ = load_episodes(gold, seed_toks, file_toks)

    print(f"episodes: {len(df)}  (expected {267*3*4})")

    # --- structural integrity gates -----------------------------------------
    # These check the SHAPE of the released data, not expected result values:
    # every arm must contribute the full frozen 267 x 3 reps, or any downstream
    # comparison is silently computed on a partial sample (this previously
    # produced n=0 deltas for the B and E arms while still printing p-values).
    n_expected = len(frozen) * len(REPS)
    per_arm = df.groupby("arm").size().to_dict()
    for arm in ARMS:
        got = per_arm.get(arm, 0)
        assert got == n_expected, (
            f"arm {arm}: {got} episodes, expected {n_expected} "
            f"({len(frozen)} frozen instances x {len(REPS)} reps). "
            "Per-episode records are missing from the release.")
    assert len(df) == n_expected * len(ARMS), (
        f"total {len(df)} episodes, expected {n_expected * len(ARMS)}")
    assert set(df.iid) <= set(frozen), "episodes outside the frozen instance list"
    assert df.groupby(["arm", "rep"]).iid.nunique().eq(len(frozen)).all(), \
        "an arm/rep cell does not cover the frozen instance list exactly"
    print(f"  integrity: {len(ARMS)} arms x {n_expected} episodes, "
          f"all within the frozen {len(frozen)}-instance list  [OK]")
    print(df.groupby(["arm"]).agg(n=("iid", "size"), gold_hit=("gold_hit", "mean"),
                                  submitted=("submitted", "mean"),
                                  consulted=("consulted", "mean"),
                                  deep_read=("deep_read", "mean"),
                                  read_before_edit=("read_before_edit", "mean"),
                                  ctx_tokens=("ctx_tokens", "mean"),
                                  prompt_tokens=("prompt_tokens", "mean"),
                                  completion_tokens=("completion_tokens", "mean"),
                                  ).round(4).to_string())

    print("\n== H1: consultation under the shipped contract (band 0.90-1.00) ==")
    for arm in ("FILE", "SHARD"):
        sub = df[df.arm == arm]
        print(f"  {arm}: consulted {sub.consulted.mean():.4f} "
              f"deep_read {sub.deep_read.mean():.4f} "
              f"read_before_edit {sub.read_before_edit.mean():.4f} (n={len(sub)})")

    print("\n== H2: gold-file-hit, sign-flip 10k seed 42, Holm (4-test family) ==")
    fam = [("FILE", "B"), ("SHARD", "B"), ("E", "B"), ("FILE", "E")]
    res = [(f"{a}-{b}", *signflip(paired(df, "gold_hit", a, b))) for a, b in fam]
    adj = holm([r[2] for r in res])
    for (name, obs, p, n), ph in zip(res, adj):
        print(f"  {name:8s} delta={obs:+.4f} ({obs*100:+.1f}pp) raw p={p:.4f} "
              f"Holm p={ph:.4f} n={n}")
    obs, p, n = signflip(paired(df, "gold_hit", "SHARD", "FILE"))
    print(f"  SHARD-FILE (exploratory, outside family) delta={obs:+.4f} "
          f"({obs*100:+.1f}pp) p={p:.4f} n={n}")

    print("\n== H3: context-tokens-paid, S<F<I, one-sided, own Holm family ==")
    fam3 = [("SHARD", "FILE"), ("FILE", "E")]
    res3 = [(f"{a}<{b}", *signflip(paired(df, "ctx_tokens", a, b), one_sided=True))
            for a, b in fam3]
    adj3 = holm([r[2] for r in res3])
    for (name, obs, p, n), ph in zip(res3, adj3):
        print(f"  {name:12s} delta={obs:+.1f} toks raw p={p:.4f} Holm p={ph:.4f} n={n}")

    print("\n== per-repo gold-hit (secondary) ==")
    print(df.pivot_table(index="repo", columns="arm", values="gold_hit",
                         aggfunc="mean").round(3).to_string())

    df.to_csv(ROOT / "runs" / "analysis_p2_episodes.csv", index=False)
    print("\nper-episode table -> runs/analysis_p2_episodes.csv")


if __name__ == "__main__":
    main()

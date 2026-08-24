#!/usr/bin/env python3
"""Regenerate Figures 2-5 as vector PDFs at the caption's type size.

Reviewer 22B: "Figures are hard to read. Please ensure that the text in the
figure is of the same size as the text of the caption."  The originals were
72-dpi rasters with no source.  These are drawn at exactly the printed width
(acmart sigconf single column = 3.33in) with 8pt text, matching \\small captions,
and included at width=\linewidth so nothing is rescaled.

Every value is recomputed from the frozen run artifacts; none is typed in.
"""
import json, glob, re, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1]/"figures"
sys.path.insert(0, str(ROOT/"analysis"))
import reproduce_paper as R

COL = 3.33          # acmart sigconf column width, inches
INK, ACC, MUT = "#1a1a1a", "#0b6fa4", "#9aa0a6"

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "font.family": "serif", "font.serif": ["Linux Libertine O", "Libertinus Serif", "DejaVu Serif"],
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": INK, "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "pdf.fonttype": 42,
})

def save(fig, name):
    fig.savefig(OUT/f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig); print("wrote", name + ".pdf")

def frame():
    g = pd.read_parquet(ROOT/"data"/"swebench_verified.parquet").set_index("instance_id")
    return R.build_frame(g, R.load_verdicts())

# ------------------------------------------------- Fig 2: frontier slopegraph
def fig2(t):
    txt = (ROOT/"FINDINGS-02-confirmed-transfer-pairs.md").read_text()
    grp, cur = {}, None
    for line in txt.splitlines():
        m = re.match(r'^### ([A-Z]\d+)\.', line)
        if m: cur = m.group(1); grp[cur] = set()
        if cur:
            for n in re.findall(r'`[\w-]+__[\w.-]+-(\d+)`', line): grp[cur].add(n)
    gof = {i: k for k, v in grp.items() for i in v}
    f = t[t.tier == 0].copy()
    f["grp"] = f.pair.str.split("_").str[1].map(gof)
    p = f.pivot_table(index="grp", columns="arm", values="resolved", aggfunc="mean")*100

    fig, ax = plt.subplots(figsize=(COL, 2.5))
    for _, r in p.iterrows():
        ax.plot([0, 1], [r.A2, r.C2], color=MUT, lw=.8, alpha=.85,
                marker="o", ms=2.4, mfc=MUT, mec="none", zorder=2)
    # bold line is the episode-level mean (58.3 -> 72.9), not the mean of the
    # per-group means, so it matches the rate reported in the text
    mA = f[f.arm == "A2"].resolved.mean()*100
    mC = f[f.arm == "C2"].resolved.mean()*100
    ax.plot([0, 1], [mA, mC], color=ACC, lw=2.2, marker="o", ms=5, zorder=3)
    for x, v, va in ((0, mA, "top"), (1, mC, "bottom")):
        ax.annotate(f"{v:.1f}%", (x, v), textcoords="offset points",
                    xytext=(0, -9 if va == "top" else 8), ha="center",
                    color=ACC, fontweight="bold")
    ax.set_xlim(-.22, 1.22); ax.set_xticks([0, 1])
    ax.set_xticklabels(["no context", "lifecycle"])
    ax.set_ylabel("resolve rate on held-out task (%)")
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.spines["bottom"].set_visible(False); ax.tick_params(axis="x", length=0)
    save(fig, "fig2-slopegraph")

# -------------------------------------------------- Fig 3: capability gradient
def fig3(t):
    """Paired deltas, computed exactly as reproduce_paper.py does: E and Do
    against B pooled over both tiers, D against B on tier 1 (the pair set where
    the self-authored arm was run).  Bases differ by arm, so each bar is a
    within-arm paired contrast rather than a difference of pooled means."""
    rng = np.random.default_rng(R.SEED)
    loc = t[t.arm.isin(["B", "E", "Do"])]
    dE, _ = R.paired_test(loc, "E", "B", "gold_hit", np.random.default_rng(R.SEED))
    dO, _ = R.paired_test(loc, "Do", "B", "gold_hit", np.random.default_rng(R.SEED))
    t1 = t[(t.tier == 1) & t.arm.isin(["D", "B"])]
    dD, _ = R.paired_test(t1, "D", "B", "gold_hit", np.random.default_rng(R.SEED))

    labels = ["self-authored\n(8B)", "gold-distilled\n(oracle bound)", "blind frontier\nseed"]
    vals = [dD, dO, dE]
    fig, ax = plt.subplots(figsize=(COL, 2.2))
    bars = ax.bar(labels, vals, color=[MUT, ACC, ACC], width=.62, zorder=3)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:+.1f}", (b.get_x()+b.get_width()/2, max(v, 0)),
                    textcoords="offset points", xytext=(0, 3),
                    ha="center", fontweight="bold")
    ax.axhline(0, color=INK, lw=.9)
    ax.set_ylabel("gold-file localization\nvs. no context (pp)")
    ax.set_ylim(-2, 32); ax.grid(axis="y", color="#e6e6e6", lw=.6, zorder=0)
    save(fig, "fig3-gradient")


# ------------------------------------------------------ Fig 4: token economics
def fig4():
    d = pd.read_csv(ROOT/"runs"/"analysis_bsides_05.csv")
    lab = {"A2": "no context", "C2": "lifecycle", "Co": "oracle-taught"}
    arms = ["A2", "C2", "Co"]
    per_res = [d[d.arm == a].tok.sum()/d[d.arm == a].resolved.sum()/1000 for a in arms]
    succ = [d[(d.arm == a) & d.resolved].tok.mean()/1000 for a in arms]
    x = np.arange(len(arms))
    fig, ax = plt.subplots(figsize=(COL, 2.2))
    ax.bar(x-.19, per_res, .36, label="per resolved task", color=ACC, zorder=3)
    ax.bar(x+.19, succ, .36, label="per successful episode", color=MUT, zorder=3)
    for xi, v in zip(x-.19, per_res):
        ax.annotate(f"{v:.1f}K", (xi, v), textcoords="offset points",
                    xytext=(0, 3), ha="center", fontsize=7.2)
    ax.set_xticks(x); ax.set_xticklabels([lab[a] for a in arms])
    ax.set_ylabel("tokens (thousands)"); ax.set_ylim(0, max(per_res)*1.22)
    ax.legend(frameon=False, loc="upper right", handlelength=1.1, borderpad=.2)
    ax.grid(axis="y", color="#e6e6e6", lw=.6, zorder=0)
    save(fig, "fig4-tokens")

# ------------------------------------------------------------- Fig 5: ceiling
def fig5():
    rows = []
    for arm in ("B", "E", "FILE", "SHARD"):
        for f in glob.glob(str(ROOT/f"runs/opus_ext/{arm}/rep1/*__*.json")):
            e = json.load(open(f))
            rows.append(dict(arm=arm, iid=e["instance_id"], pt=e["prompt_tokens"],
                             ct=e["completion_tokens"]))
    df = pd.DataFrame(rows)
    res = {}
    for l in open(ROOT/"runs"/"opus_ext"/"eval_summary.jsonl"):
        r = json.loads(l); res[(r["run_id"], r["instance_id"])] = r["resolved"]
    df["resolved"] = [res.get((f"eval-opus-ext-{a}", i), False) for a, i in zip(df.arm, df.iid)]
    arms = ["B", "E", "FILE", "SHARD"]
    lab = {"B": "no context", "E": "injected", "FILE": "monolith", "SHARD": "sharded"}
    rate = [100*df[df.arm == a].resolved.mean() for a in arms]
    cost = [(df[df.arm == a].pt.sum()+df[df.arm == a].ct.sum())/df[df.arm == a].resolved.sum()/1000
            for a in arms]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL, 1.95), gridspec_kw=dict(wspace=.55))
    a1.bar([lab[a] for a in arms], rate, color=[MUT]+[ACC]*3, width=.66, zorder=3)
    a1.axhline(rate[0], color=INK, ls="--", lw=.9, zorder=4)
    a1.set_ylim(0, 108); a1.set_ylabel("resolve rate (%)")
    a1.set_yticks([0, 25, 50, 75, 100])
    a1.grid(axis="y", color="#e6e6e6", lw=.6, zorder=0)
    a2.bar([lab[a] for a in arms], cost, color=[MUT]+[ACC]*3, width=.66, zorder=3)
    a2.set_ylabel("tokens per\nresolved task (K)")
    a2.grid(axis="y", color="#e6e6e6", lw=.6, zorder=0)
    for ax in (a1, a2):
        ax.tick_params(axis="x", labelrotation=38, length=0)
        for lb in ax.get_xticklabels(): lb.set_ha("right")
    save(fig, "fig5-ceiling")

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    t = frame()
    fig2(t); fig3(t); fig4(); fig5()


# ------------------------------------------------- Fig 1: architecture diagram
def fig1():
    """Redrawn as vector at full text width with 8pt labels. The original was a
    72-dpi raster whose labels rendered at roughly 3pt in one column."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    W, H = 7.0, 2.05
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, 100); ax.set_ylim(0, 30); ax.axis("off")

    def box(x, y, w, h, lw=1.0, fc="none", ec=INK, r=0.6):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                    lw=lw, facecolor=fc, edgecolor=ec, zorder=2))

    def arrow(x1, y1, x2, y2, style="-", lw=1.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=9, lw=lw, color=INK,
                                     linestyle=style, shrinkA=0, shrinkB=0, zorder=3))

    # repository
    ax.text(15.5, 27.4, "Repository", ha="center", fontweight="bold")
    box(1, 7.5, 29, 18.4)
    ax.text(15.5, 22.3, "src/", ha="center", family="monospace")
    ax.text(15.5, 18.6, "docs/  ADR/", ha="center", family="monospace")
    box(3.2, 9.3, 24.6, 7.2, lw=1.6, fc="#f2f2f2")
    ax.text(15.5, 13.3, "context.md", ha="center", family="monospace", fontweight="bold")
    ax.text(15.5, 10.6, "intent · constraints · ledger", ha="center",
            fontsize=6.8, color="#444")

    # agent session
    ax.text(53, 27.4, "Agent session", ha="center", fontweight="bold")
    box(40, 7.5, 26, 18.4)
    for i, s in enumerate(("plan", "execute", "observe", "propose lessons")):
        ax.text(53, 22.4 - i*4.0, s, ha="center")

    # human review
    box(74, 12.5, 25, 9.2, lw=1.6)
    ax.text(86.5, 18.4, "Human review", ha="center", fontweight="bold")
    ax.text(86.5, 15.0, "same gate as code (P5)", ha="center", fontsize=6.8, color="#444")

    arrow(30.4, 17.5, 39.6, 17.5)
    ax.text(35.0, 19.0, "consult", ha="center", style="italic", fontsize=7.6)
    arrow(66.4, 17.1, 73.6, 17.1, style=(0, (3.5, 2.5)))
    ax.text(70.0, 18.7, "propose", ha="center", style="italic", fontsize=7.6)

    # return path: review -> repository
    ax.plot([86.5, 86.5, 15.5], [12.2, 3.4, 3.4], color=INK, lw=1.0, zorder=3,
            solid_joinstyle="miter")
    arrow(15.5, 3.4, 15.5, 7.2)
    ax.text(54, 4.7, "context diff commits with the code change",
            ha="center", style="italic", fontsize=7.6)
    save(fig, "fig1-architecture")

#!/usr/bin/env python3
"""Generate the three Context Inheritance figures as house-style SVG, render to
PNG via headless Chrome. Visually distinct from the RCL architecture paper's
figures (different chart types) while plotting the same grounded numbers.

  fig1-gradient  : horizontal absolute-localization bars by author tier + threshold
  fig2-tokens    : tokens/resolved decomposed into fix-work vs wasted exploration
  fig3-ceiling   : broad-sample frontier delivery matrix, resolve + ceiling line

Run: python paper/context-inheritance/make_figures.py
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGDIR = HERE / "figures"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK = "#141414"      # near-black text/lines
GRID = "#c9c9c9"     # light rule
FILL = "#dcdcdc"     # bar fill (light)
FILL2 = "#9a9a9a"    # bar fill (mid)
FILL3 = "#6f6f6f"    # bar fill (dark)
MUTE = "#606060"     # secondary text
FONT = "Helvetica, Arial, sans-serif"


def svg_open(w, h):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="{FONT}"><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>')


def txt(x, y, s, size=13, col=INK, w="normal", anchor="start", style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{col}" '
            f'font-weight="{w}" text-anchor="{anchor}"{st}>{s}</text>')


def rect(x, y, w, h, fill, stroke=INK, sw=1.0):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def line(x1, y1, x2, y2, col=INK, sw=1.0, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{sw}"{d}/>'


# ---------------------------------------------------------------- fig 1
def fig1():
    W, H = 840, 380
    s = [svg_open(W, H)]
    s.append(txt(40, 42, "Held-out localization by context author", 18, INK, "bold"))
    s.append(txt(40, 64, "8B executor held fixed · gold-file hit rate · 180 episodes/arm",
                 12.5, MUTE))
    # rows: (label, sublabel, value%, delta)
    rows = [
        ("no context", "", 21.1, None),
        ("self-authored (8B)", "author = reader", 21.1, "+0.0 pp  (p = 1.0)"),
        ("gold-distilled", "oracle bound", 42.8, "+21.7 pp  (p < 0.0001)"),
        ("frontier, blind seed", "author > reader", 47.2, "+26.1 pp  (p < 0.0001)"),
    ]
    x0, top, bh, gap = 210, 100, 34, 26
    axmax = 55.0
    axlen = 420
    def sx(v): return x0 + v / axmax * axlen
    # baseline (threshold) at 21.1
    thr = sx(21.1)
    s.append(line(thr, top - 10, thr, top + len(rows) * (bh + gap) - gap + 10,
                  MUTE, 1.2, "4 3"))
    s.append(txt(thr + 4, top - 14, "no-context floor", 11, MUTE))
    for i, (lab, sub, v, dlt) in enumerate(rows):
        y = top + i * (bh + gap)
        fill = FILL if v <= 21.2 else (FILL2 if i == 2 else FILL3)
        s.append(txt(x0 - 14, y + bh * 0.5 + 1, lab, 13.5, INK, "bold", "end"))
        if sub:
            s.append(txt(x0 - 14, y + bh * 0.5 + 15, sub, 10.5, MUTE, "normal", "end"))
        s.append(rect(x0, y, sx(v) - x0, bh, fill))
        s.append(txt(sx(v) + 8, y + bh * 0.5 + 5, f"{v:.1f}%", 14, INK, "bold"))
        if dlt:
            s.append(txt(sx(v) + 62, y + bh * 0.5 + 5, dlt, 11.5, MUTE))
    # x axis
    ay = top + len(rows) * (bh + gap) - gap + 22
    s.append(line(x0, ay, x0 + axlen, ay, INK, 1.0))
    for t in (0, 20, 40):
        s.append(line(sx(t), ay, sx(t), ay + 4, INK, 1.0))
        s.append(txt(sx(t), ay + 18, f"{t}", 11, MUTE, "normal", "middle"))
    s.append(txt(x0 + axlen / 2, ay + 34, "gold-file localization (%)", 12, MUTE, "normal", "middle"))
    s.append("</svg>")
    return "".join(s), W, H


# ---------------------------------------------------------------- fig 2
def fig2():
    W, H = 720, 380
    s = [svg_open(W, H)]
    s.append(txt(40, 42, "Where the token savings come from", 18, INK, "bold"))
    s.append(txt(40, 64, "frontier executor, constraint-sharing regime · tokens per resolved task",
                 12.5, MUTE))
    # stacked: fix work (~33.6K constant) + wasted exploration overhead
    FIX = 33.6
    arms = [("no context", 81.8), ("self-taught lifecycle", 55.7)]
    x0, base, bw, gap = 170, 300, 150, 120
    ymax = 90.0
    plotH = 210
    def h(v): return v / ymax * plotH
    for i, (lab, tot) in enumerate(arms):
        x = x0 + i * (bw + gap)
        over = tot - FIX
        # overhead (top, darker) then fix (bottom, light)
        yfix = base - h(FIX)
        s.append(rect(x, yfix, bw, h(FIX), FILL))
        yov = yfix - h(over)
        s.append(rect(x, yov, bw, h(over), FILL3))
        # labels
        s.append(txt(x + bw / 2, yov - 12, f"{tot:.1f}K", 17, INK, "bold", "middle"))
        s.append(txt(x + bw / 2, base + 22, lab, 13, INK, "bold", "middle"))
        s.append(txt(x + bw / 2, yfix + h(FIX) / 2 + 4, f"{FIX:.1f}K", 12, INK, "normal", "middle"))
        s.append(txt(x + bw / 2, yov + h(over) / 2 + 4, f"{over:.1f}K", 12, "#f2f2f2", "normal", "middle"))
    # arrow / delta between
    xm = x0 + bw + gap / 2
    s.append(txt(xm, 150, "−32%", 16, INK, "bold", "middle", "italic"))
    # baseline
    s.append(line(x0 - 20, base, x0 + 2 * bw + gap + 20, base, INK, 1.0))
    # legend
    ly = 335
    s.append(rect(x0, ly, 16, 12, FILL))
    s.append(txt(x0 + 22, ly + 11, "productive fix work (constant)", 11.5, MUTE))
    s.append(rect(x0 + 250, ly, 16, 12, FILL3))
    s.append(txt(x0 + 272, ly + 11, "wasted exploration (amortized failures)", 11.5, MUTE))
    s.append("</svg>")
    return "".join(s), W, H


# ---------------------------------------------------------------- fig 3
def fig3():
    W, H = 840, 400
    s = [svg_open(W, H)]
    s.append(txt(40, 42, "The frontier ceiling: broad-sample delivery matrix", 18, INK, "bold"))
    s.append(txt(40, 64, "Opus 4.8 · 88 random instances · resolve rate; no delivery beats no-context",
                 12.5, MUTE))
    # vertical y-axis label (avoids colliding with the subtitle)
    s.append(f'<text x="34" y="200" font-size="12" fill="{MUTE}" text-anchor="middle" '
             f'transform="rotate(-90 34 200)">resolve rate (%)</text>')
    arms = [
        ("none", 90.9, "$0.153", FILL),
        ("injected", 81.8, "$0.157", FILL2),
        ("file", 85.2, "$0.154", FILL2),
        ("sharded", 88.6, "$0.230", FILL3),
    ]
    x0, base, bw, gap = 130, 300, 96, 46
    ymax = 100.0
    plotH = 210
    def h(v): return v / ymax * plotH
    # ceiling line at 90.9
    yceil = base - h(90.9)
    s.append(line(x0 - 20, yceil, x0 + 4 * bw + 3 * gap + 20, yceil, MUTE, 1.3, "5 3"))
    s.append(txt(x0 + 4 * bw + 3 * gap + 24, yceil + 4, "no-context", 10.5, MUTE))
    s.append(txt(x0 + 4 * bw + 3 * gap + 24, yceil + 17, "ceiling", 10.5, MUTE))
    for i, (lab, v, cost, fill) in enumerate(arms):
        x = x0 + i * (bw + gap)
        y = base - h(v)
        s.append(rect(x, y, bw, h(v), fill))
        s.append(txt(x + bw / 2, y - 10, f"{v:.1f}%", 15, INK, "bold", "middle"))
        s.append(txt(x + bw / 2, base + 22, lab, 12.5, INK, "bold", "middle"))
        s.append(txt(x + bw / 2, base + 39, cost + "/res", 11, MUTE, "normal", "middle"))
    # y axis
    s.append(line(x0 - 20, base, x0 - 20, base - plotH, INK, 1.0))
    for t in (0, 50, 100):
        yy = base - h(t)
        s.append(line(x0 - 24, yy, x0 - 20, yy, INK, 1.0))
        s.append(txt(x0 - 30, yy + 4, f"{t}", 11, MUTE, "normal", "end"))
    s.append(line(x0 - 20, base, x0 + 4 * bw + 3 * gap, base, INK, 1.0))
    s.append("</svg>")
    return "".join(s), W, H


def render(name, svg, w, h):
    svg_path = FIGDIR / f"{name}.svg"
    svg_path.write_text(svg)
    html = FIGDIR / f"_{name}.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8">'
                    f'<style>*{{margin:0;padding:0}}body{{width:{w}px;height:{h}px}}</style>'
                    f'</head><body>{svg}</body></html>')
    png = FIGDIR / f"{name}.png"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    f"--screenshot={png}", f"--window-size={w},{h}",
                    "--force-device-scale-factor=2", "--default-background-color=00000000",
                    f"file://{html}"], capture_output=True)
    html.unlink(missing_ok=True)
    print(f"  {name}.png  ({png.stat().st_size//1024} KB)")


if __name__ == "__main__":
    FIGDIR.mkdir(exist_ok=True)
    for name, fn in [("fig1-gradient", fig1), ("fig2-tokens", fig2), ("fig3-ceiling", fig3)]:
        svg, w, h = fn()
        render(name, svg, w, h)
    print("done")

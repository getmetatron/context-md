# Context Inheritance — AgenticDev 2026 camera-ready

Source for the paper *Context Inheritance: A Git-Native Architecture and
Pre-Registered Study of Repository Context for AI Coding Agents*, accepted as a
full paper at the AgenticDev 2026 Workshop (Munich, 12 October 2026).

## Build

    tectonic main.tex        # -> main.pdf

`package/` is the self-contained publication source: `main.tex`, `acmart.cls`
(ACM Primary Article Template v2.20) and `figures/`. It builds from a clean
directory with no dependency on the rest of this tree. This establishes local
source completeness, not ACM TAPS acceptance.

## Reproducing the numbers

The checked empirical values are recomputed from the frozen run artifacts in
`../../runs/`:

    python ../../analysis/reproduce_paper.py     # 15 claims from the study
    python analysis/verify_claims.py             # camera-ready additions
    python analysis/make_figures.py              # regenerates Figures 1-5

`analysis/seed_leakage.py` runs the blind-seed leakage audit reported in the
threats section; `analysis/RESULTS-07-seed-leakage.md` records its output.

See `../../ARTIFACT.md` for the artifact runbook and `../../PREREGISTRATION.md`
(git tag `prereg-v1`) for the frozen protocol.

## Publication metadata

The ACM rights statement, DOI and ISBN are not yet inserted; they are supplied by
ACM through the author kit. The Data Availability statement likewise carries a
placeholder until the replication package receives its archival DOI. The frozen
40-episode consultation audit also awaits human labels and must be incorporated
before archival release.

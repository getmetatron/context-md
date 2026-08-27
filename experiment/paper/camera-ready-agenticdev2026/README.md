# Context Inheritance — AgenticDev 2026 camera-ready

Source for the paper *Context Inheritance: A Git-Native Architecture and
Pre-Registered Study of Repository Context for AI Coding Agents*, accepted as a
full paper at the AgenticDev 2026 Workshop (Munich, 12 October 2026).

## Build

    tectonic main.tex
    cp main.pdf context-inheritance-agenticdev-2026-camera-ready.pdf

`main.pdf` is the direct TeX build output. Upload the descriptively named copy
`context-inheritance-agenticdev-2026-camera-ready.pdf` for submission.

`package/` is the self-contained publication source: `main.tex`, `acmart.cls`
(ACM Primary Article Template v2.20) and `figures/`. It builds from a clean
directory with no dependency on the rest of this tree. This establishes local
source completeness, not ACM TAPS acceptance.

## Reproducing the numbers

The checked empirical values are recomputed from the frozen run artifacts in
`../../runs/`:

    python ../../analysis/reproduce_paper.py     # 15 claims from the study
    python analysis/verify_claims.py             # camera-ready additions, including consultation audit
    python analysis/make_figures.py              # regenerates Figures 1-5

`analysis/seed_leakage.py` runs the blind-seed leakage audit reported in the
threats section; `analysis/RESULTS-07-seed-leakage.md` records its output. The
fixed consultation-detector sample, key, row evidence, and author-verification
record are under `../../audit/`.

See `../../ARTIFACT.md` for the artifact runbook and `../../PREREGISTRATION.md`
(git tag `prereg-v1`) for the frozen protocol.

## Publication metadata

The ACM rights statement, proceedings DOI and ISBN are not yet inserted; they are
supplied by ACM through the author kit. The Data Availability statement cites the
replication artifact's version DOI, `10.5281/zenodo.22122045`. An author
manually reviewed every row in the fixed 40-episode consultation audit and
confirmed 40/40 agreement for all three constructs (38 positive, 2 negative;
mechanical kappa 1.000). The paper and artifact disclose that the evidence packet
and candidate labels were AI-prepared and the author was not blinded to the
detector output, so this is descriptive confirmation rather than independent
reliability evidence.

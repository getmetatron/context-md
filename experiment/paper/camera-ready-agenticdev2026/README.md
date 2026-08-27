# Context Inheritance — AgenticDev 2026 camera-ready

Source for the paper *Context Inheritance: A Git-Native Architecture and
Pre-registered Study of Repository Context for AI Coding Agents*, accepted as a
full paper at AgenticDev '26 (Munich, 12--16 October 2026).

## Build

    tectonic main.tex
    cp main.pdf context-inheritance-agenticdev-2026-camera-ready.pdf

`main.pdf` is the direct TeX build output. Upload the descriptively named copy
`context-inheritance-agenticdev-2026-camera-ready.pdf` for submission.

`package/` is the self-contained publication source: `main.tex`, `acmart.cls`
(ACM Primary Article Template v2.20) and `figures/`. It builds from a clean
directory with no dependency on the rest of this tree. This establishes local
source completeness, not ACM TAPS acceptance.
`context-inheritance-agenticdev-2026-camera-ready-source.zip` is the upload-ready
archive of that directory.

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

The exact ACM eRights metadata is inserted: CC BY 4.0, paper DOI
`10.1145/3843282.3844425`, and ISBN `979-8-4007-2985-0/2026/10`. The Data
Availability statement separately cites the replication artifact's immutable
version DOI, `10.5281/zenodo.22122045`. The source also includes the author-kit
submission ID and received/accepted dates, uses `microtype`, and marks Pavel as
corresponding author. An author
manually reviewed every row in the fixed 40-episode consultation audit and
confirmed 40/40 agreement for all three constructs (38 positive, 2 negative;
mechanical kappa 1.000). The paper and artifact disclose that the evidence packet
and candidate labels were AI-prepared and the author was not blinded to the
detector output, so this is descriptive confirmation rather than independent
reliability evidence.

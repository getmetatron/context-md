# Zenodo archival-readiness audit

Replication artifact for *Context Inheritance: A Git-Native Architecture and
Pre-Registered Study of Repository Context for AI Coding Agents* (AgenticDev
2026). Every value below was read from the repository or produced by running the
documented commands; nothing is assumed.

> **READY FOR ZENODO CONTENT FREEZE: YES.** The registered consultation audit now
> has an author-confirmed record. The manual author review and its AI-prepared,
> non-blinded evidence workflow are disclosed. ACM author-kit metadata belongs
> to the paper workflow, and the
> archival DOI is produced by the eventual Zenodo deposit; neither is a
> prerequisite for depositing the artifact. The annotated release tag named
> below identifies the content freeze containing this audit.

## Correction to the previous version of this audit

The earlier revision of this file reported "runs complete: **PASS**". That was
**wrong**. Only 1,602 of the 3,204 delivery-study episodes had been released:
the B and E arms carried 10 per-episode records per repetition instead of 267,
and those 10 were Paper-1 instances outside the frozen list. `analyze_p2.py`
consequently computed the B/E contrasts on `n=0` while still printing
`raw p=0.0001`, so the defect looked like a result rather than a failure. The
1,602 missing records are now included and the delivery numbers reproduce.
The lesson is recorded here rather than quietly fixed: a PASS that was never
executed end to end is worse than an open FAIL.

## Repository metadata

| check | result |
|---|---|
| `.zenodo.json` valid JSON | **PASS** |
| creators / ORCIDs verified | **PASS** — 4 creators, 4 ORCIDs from the camera-ready `\orcid{}` fields |
| license verified | **PASS** — `mit`, matching `LICENSE` |
| no proceedings metadata invented | **PASS** — no ACM DOI, ISBN or rights fields |

## Reproducibility

| check | result |
|---|---|
| pre-registration present | **PASS** — `experiment/PREREGISTRATION.md` |
| Paper 1 tag/commit verified | **PASS** — `prereg-v1`, annotated, commit `0561566…`, 2026-07-09, ancestor of HEAD, resolvable here |
| Paper 2 tag provenance | **DISCLOSED LIMITATION** — `prereg2-v1` is **not public** and is a *lightweight* tag (no tagger timestamp). Corroboration only: tagged commit 2026-07-15, all delivery evaluations timestamped 2026-07-19/20. Stated in `ARTIFACT.md` and `DEVIATIONS.md`; the tag is **not** pushed, because that repository's history is private. |
| runs complete | **PASS (newly true)** — 3,204 delivery episodes, 801/arm, enforced by assertions in `analyze_p2.py` |
| outcome records complete | **PASS** — 4,713 unique containerized verdicts plus 2 planned frontier attempts whose nonzero runner outcomes are released and scored unresolved |
| promotion decisions/logs | **PASS** — 371 `promotions.jsonl` |
| authoring transcripts | **UNCERTAIN** — no verbatim seed-authoring transcripts were retained; only `seeds/AUDIT.md`. Paper and public docs now say "audit record", not "transcripts". |
| analysis scripts complete | **PASS** — incl. `count_episodes.py` and the two consultation-audit scripts |
| offline reproduction | **PASS** — `make reproduce-paper` → 15/15 in a fresh venv from `requirements-artifact.txt` alone |
| claim verification | **PASS** — `verify_claims.py` covers every Table 3 cell, both delivery contrasts, the token-test family, leakage Jaccard values, ceiling-arm rates/costs, and strict outcome completeness, including the two logged pre-record aborts |
| figure regeneration | **PASS** — one command emits **5** figures (Fig 1 was previously defined after `__main__` and never ran) |
| declared dependencies sufficient | **PASS** — `matplotlib` added; clean-env install verified |

## Research transparency

| check | result |
|---|---|
| `DEVIATIONS.md` | **PASS** |
| exploratory / post-hoc identified | **PASS** |
| leakage analysis included | **PASS** |
| deviations disclosed in the paper | **PASS (new)** — Threats now carries the six material items, including the two pre-record frontier aborts |
| episode/evaluation inventory | **PASS** — `count_episodes.py` reports repository records but explicitly does not present them as a confirmatory sample size; the misleading global manuscript count was removed |
| **registered 40-episode consultation audit** | **PASS with disclosed deviation** — fixed sample (seed 42, 1,602-episode frame); an author manually reviewed every row against transcript evidence and confirmed 40/40 agreement on consultation, deep read, and read-before-edit (38 positive, 2 negative; mechanical kappa 1.000). The evidence packet and candidate labels were AI-prepared, and the author was not blinded to the detector output, so raw agreement is descriptive confirmation rather than independent reliability. Completed CSV, key, row evidence, and attestation are released under `experiment/audit/`; the workflow deviation is in `DEVIATIONS-2.md`. |

## Repository hygiene

| check | result |
|---|---|
| `.DS_Store` / editor artifacts | **PASS** |
| secret scan | **PASS** — pattern + manual across all tracked files; no dedicated scanner installed on the build machine |
| new B/E records scanned | **PASS** — no credentials, no absolute-path disclosures |
| no required untracked files | **PASS after the commit containing this audit** |

## Release

| | |
|---|---|
| audited state | the release commit containing this audit |
| final tag | `v1.0-agenticdev2026-artifact` (annotated) |
| superseded tag | `camera-ready-agenticdev2026` — predates these fixes; must not be archived |
| archived size | ~13 MB compressed before this change; the 1,602 new records add ~11 MB uncompressed |
| **READY FOR ZENODO** | **YES — release checks passed before tagging** |

## Exact safe release and deposit steps

1. Push the audited `main`. Delete the stale public `anonymous-review` branch.
2. Tag `v1.0-agenticdev2026-artifact` (annotated) and push the tag only.
3. Enable the repository in Zenodo, then create the GitHub release **from that
   tag**. Zenodo archives that exact release.
4. Take the **version** DOI (not the concept DOI) and set `\artifactdoi` in
   `main.tex`; it updates the Data Availability Statement and the artifact
   reference together.
5. Insert the ACM eRights values into `\setcopyright`, `\acmDOI`, `\acmISBN`.
6. Rebuild, re-run both checkers, rebuild the submission ZIP, and upload to
   HotCRP/TAPS.

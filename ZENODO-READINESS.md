# Zenodo archival-readiness audit

Audit of `kerbelp/context-md` as the replication artifact for *Context
Inheritance: A Git-Native Architecture and Pre-Registered Study of Repository
Context for AI Coding Agents* (AgenticDev 2026). Every value below was read from
the repository or produced by running the documented commands from a **clean
clone**; nothing is assumed.

## Repository metadata

| check | result |
|---|---|
| `.zenodo.json` present and valid JSON | **PASS** — parses; `upload_type: software`, `access_right: open` |
| creators / ORCIDs verified | **PASS** — 4 creators, 4 ORCIDs, taken from the camera-ready `\orcid{}` fields, affiliation Metatron Research, Tel Aviv, Israel |
| license verified | **PASS** — `"license": "mit"`, matching `LICENSE` (MIT, © 2026 Pavel Kerbel) |
| no proceedings metadata | **PASS** — no ACM DOI, ISBN or rights fields; the record describes the artifact, not the paper |

## Reproducibility

| check | result |
|---|---|
| pre-registration present | **PASS** — `experiment/PREREGISTRATION.md` |
| pre-registration tag/commit verified | **PASS** — tag `prereg-v1` (annotated) → commit `056156679a896f0697198bb240c92110aa2df048`, 2026-07-09 13:05:27 +0300; resolvable in this repository, contains the protocol, and is an ancestor of HEAD |
| runs complete | **PASS** — 408 `predictions.jsonl`, all arms the paper reports (A, A2, B, BT2, C, C2, C_oracle, D, D_oracle, D_oracleT2, E, ET2, FILE, SHARD, opus_ext) |
| evaluation verdicts complete | **PASS** — 380 containerized verdict files + 2 `eval_summary.jsonl` |
| promotion decisions/logs | **PASS** — 371 `promotions.jsonl` |
| authoring transcripts complete | **UNCERTAIN — see note** |
| analysis scripts complete | **PASS** — `analysis/` (4) + camera-ready `analysis/` (3: leakage audit, claim verification, figure generation) |
| offline reproduction | **PASS** — `make reproduce-paper PY=…` → `15/15 claims reproduced` from a clean clone, in a fresh venv built **only** from `requirements-artifact.txt` |
| claim verification | **PASS** — `verify_claims.py` → `all camera-ready claims verified`, same environment |
| no undeclared parent-directory dependencies | **PASS** — no path escapes the checkout in any analysis or harness script |

**Note on authoring transcripts.** The paper's Data Availability statement no
longer promises "seed-authoring transcripts": no verbatim transcripts of the
blind-authoring sessions were retained. What exists is `seeds/AUDIT.md` (and
`AUDIT-P2.md`), an audit record written at authoring time documenting the
procedure, the inputs given to each author, the prohibitions imposed, the
self-reported consulted-file lists and a leakage scan. That is weaker evidence
than a transcript, and it is marked uncertain here rather than PASS so a reader
is not misled. The camera-ready wording was corrected to match.

## Research transparency

| check | result |
|---|---|
| `DEVIATIONS.md` | **PASS** — created; required by `PREREGISTRATION.md` §12 and previously missing |
| exploratory / post-hoc analyses identified | **PASS** — §5 and §6 of `DEVIATIONS.md` |
| blind-seed leakage analysis included | **PASS** — `seed_leakage.py`, `RESULTS-07-seed-leakage.md`, and Table 4 of the paper |

`DEVIATIONS.md` does **not** claim a clean protocol. It records three material
deviations — a permutation test where §7 specified mixed-effects/McNemar; the
registered constraint-violation metric never implemented; and the frontier tier
running 16 pairs against the §8 target of ≥25 — plus registered work never
executed (conditions F and G, RQ3/H3). `PREREGISTRATION.md` and the `prereg-v1`
tag were not modified.

## Repository hygiene

| check | result |
|---|---|
| `.DS_Store` removed | **PASS** — untracked; already covered by `.gitignore` |
| other editor/build artifacts | **PASS** — no tracked `__pycache__`, `.pyc`, `.swp`, `.idea`, `.vscode`, `Thumbs.db` |
| secret scan | **PASS** — see below |
| no required untracked files | **PASS** — a clean clone reproduces every reported number |

**Secret scan.** No dedicated scanner (`gitleaks`, `trufflehog`,
`detect-secrets`) is installed on this machine, so this was pattern-based plus
manual inspection across **all tracked files**: provider key formats
(`sk-ant-`, `sk-`, `ghp_`, `gho_`, `github_pat_`, `AIza`, `xox[baprs]-`,
AWS `AKIA`/`ASIA`), PEM private keys, bearer tokens, assigned
`API_KEY`/`SECRET`/`PASSWORD`/`ACCESS_TOKEN` values, `Set-Cookie` and
`Authorization:` headers, and tracked `.env`/`.pem`/`.key`/credential files —
**zero matches in every category**. Email addresses appearing in tracked files
are the four authors' published paper addresses plus a public mailing-list
address inside an upstream gold patch. The only non-public-looking endpoint is
`http://localhost:11434/api/chat`, the documented local Ollama server. The
harness previously read an absolute path to a local `.env`; it now reads
`ANTHROPIC_API_KEY` from the environment.

**Known, accepted disclosure:** 21 files under `runs/` and `pilot/logs/` contain
absolute `/Users/pavel/...` paths inside raw episode logs and Python tracebacks.
These were already public before this release. They were **not** scrubbed:
rewriting raw experimental logs to tidy cosmetics would damage the evidence the
package exists to provide. Nothing beyond a username and directory layout is
exposed.

## Release

| | |
|---|---|
| current HEAD | `89a27308386e5c5c3ece358219b6468a3e8ef411` |
| proposed final tag | `v1.0-agenticdev2026-artifact` |
| archived size | ~13 MB compressed (`git archive` tarball); ~90 MB checked out, 4,886 tracked files |
| existing tag `camera-ready-agenticdev2026` | **superseded** — predates the metadata, deviations log and ARTIFACT.md corrections; must not be used as the Zenodo snapshot |
| **READY FOR ZENODO** | **YES**, once the tag above is created |

The GitHub release has **not** been created, and no Zenodo record has been
created. Intended order: enable the repository in Zenodo → create the release
from the new tag → let Zenodo archive it → take the **version** DOI (not the
concept DOI) → insert it into the camera-ready `\artifactdoi` macro, which
updates both the Data Availability statement and the artifact reference.

# Repository Context

## Intent
Canonical home of the Repository Context Layer: a one-page manifesto
(README), a minimal spec (SPEC.md), and an example file. The
abstraction is the product; keep it vendor-neutral and small enough
to adopt in an afternoon.

## Constraints
- The spec stays minimal: three required sections and a discovery
  path. Rejected richer schemas (decision logs, pattern catalogs as
  requirements): under-specified and adopted beats complete and
  ignored.
- Vendor neutrality: implementations, including Metatron, appear only
  in the reference-implementation section — never woven into the
  spec itself. The abstraction must outlive any product built on it.
- The manifesto stays one page. Additions must displace weaker
  material, not extend the document.

## Evolved Context
- [2026-07-02] Initial publication: manifesto, spec v0.1, example.
- [2026-07-02] Reframed after external review: the abstraction
  (Repository Context Layer) is the star; context.md is the proposed
  default implementation, not the name of the idea. Added the
  "why existing artifacts are not enough" section to preempt the
  "isn't this just ADRs/RAG?" objection.
- [2026-07-04] Published the companion paper (preprint v0.1) alongside
  the manifesto: formal properties (P1-P6), lifecycle invariants
  (I1-I4), design analysis, and the Metatron reference implementation.
  The spec now reserves both sharding forms (.repo/context/ and root
  context/), a change driven by the reference implementation's layout.
- [2026-07-05] Paper gains a second author (Milana Kerbel) alongside Pavel
  Kerbel; ORCID iDs recorded for both. PDF/HTML re-rendered. Added
  .gitattributes marking binary assets so committed PDFs are never subject
  to EOL normalization.

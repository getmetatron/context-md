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

# Repository Context Layer — Minimal Specification

**Version 0.1** · Status: draft

This document specifies the smallest possible contract for a Repository Context Layer. It is intentionally minimal; see the [manifesto](README.md) for rationale. The key words MUST, SHOULD, and MAY are to be interpreted as described in RFC 2119.

## 1. Discovery

A conforming agent MUST look for the context file in this order and use the first match:

1. `.repo/context.md`
2. `context.md` (repository root)

Discovery is deterministic: agents MUST NOT rely on search or inference to locate the file.

## 2. Format

The context file is plain Markdown (CommonMark). It MUST contain a top-level `# Repository Context` heading and the following three `##` sections, in any order:

| Section | Contents |
|---|---|
| `## Intent` | What the project is and the design philosophy everything else must serve. |
| `## Constraints` | Non-negotiable rules. Each entry SHOULD state its reason, including rejected alternatives. |
| `## Evolved Context` | Append-only ledger of what agents and humans learned while working in the repository. Entries SHOULD be dated (`[YYYY-MM-DD]`) and SHOULD NOT be rewritten or reordered. |

Additional sections MAY be present; agents MUST ignore sections they do not understand.

## 3. Agent lifecycle

A conforming agent:

1. **Consult** — MUST read the context file before planning or modifying the repository.
2. **Execute** — SHOULD treat `Constraints` as binding and `Intent` as the tiebreaker for open design choices.
3. **Update** — SHOULD append durable, non-obvious learnings to `Evolved Context` before committing. Entries MUST be appended, never silently edited.
4. **Commit** — context changes travel in the same commit (or pull request) as the code that motivated them, so humans review both together.

Promotion of an `Evolved Context` entry into `Constraints` is an ordinary edit, reviewed by a human like any other change.

## 4. Branching and merging

The context file follows the repository's branching model. No additional synchronization semantics are defined: it branches, merges, conflicts, and rolls back exactly like source code.

## 5. Versioning of this spec

This specification is versioned with the repository that hosts it. Breaking changes bump the minor version while the spec remains 0.x. Implementations SHOULD tolerate files written against any 0.x version.

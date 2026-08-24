# Findings 06 — Existence check: does a local executor consult context files?

**Date:** 2026-07-15. Pilot gate 1 of PAPER2-DESIGN §8; feasibility only, excluded from confirmatory analysis.
**Setup:** gemma4:e4b, the 10 FINDINGS-03 pilot instances, shipped Metatron layout written into each checkout (`context.md` entry + sharded `context/decisions/*.md` from the frozen E-arm seeds + AGENTS.md, `pr` gate, all verbatim `metatron context setup` output). Two conditions: **files** (shipped AGENTS.md block included in the prompt, mimicking frameworks that auto-load it) and **files-bare** (artifacts on disk, prompt silent). Detector: pilot-grade regex over transcript commands (`context.md|context/|AGENTS.md`), frozen version comes at prereg2 freeze. Runner: `pilot/run_pilot.py` `CONDITION=files|files-bare`.

## Results

| condition | n | consulted | read before first edit | submitted | non-empty patch | gold-file hit |
|---|---|---|---|---|---|---|
| files (shipped contract) | 10 | **4 (40%)** | 3 (30%) | 9 | 7 | 3 |
| files-bare (no contract) | 6* | **0 (0%)** | 0 | 6 | 4 | 1 |

*files-bare run interrupted at 6/10; remaining 4 episodes pending (django set). 0/6 with the exact binomial 95% CI [0, 39%] already supports the qualitative conclusion; complete before citing a rate.

- Within the files condition: consulted episodes hit gold files 2/4; non-consulted 1/6. Directionally the mediation story (RQ4), far too small to mean anything — noted only as "the variance RQ4 needs exists."
- Consultation, when it happens, is early (first read at turns 0, 0, 1, 5).
- The smoke episode (8459) that read nothing even after `ls -F` showed the files is a genuine mode, not a fluke: 6/10 contract-condition episodes behaved the same.

## Decisions triggered (per pre-committed rules in PAPER2-DESIGN)

1. **The design survives as-is.** Consultation under the shipped contract is 40% — far above the <10% threshold that would have forced the contract-strength factor. **No extra factor; arms stay B/I/F/S.** H1 point prediction for the prereg: ⟨40%⟩ ± wide, per-executor.
2. **files-bare confirms the contract is the entire mechanism** (0/6 without it). The paper can state: files in the tree are invisible to a local executor unless the harness surfaces the contract — which is precisely what AGENTS.md auto-loading conventions exist to do. This sharpens the framing: the study measures the shipped contract's *pull-through*, not file discoverability.
3. Consultation rate at 40% means the F/S vs I comparison will mix compliers and non-compliers — unconditional deltas will understate the per-complier effect. RQ4's complier analysis moves from "nice to have" to "the explanatory centerpiece" (still labeled exploratory).

## Open

- Finish the 4 pending files-bare episodes (django) — run was interrupted.
- Same 2×10 on qwen2.5-coder:7b = FINDINGS-07 (capability gate + second consultation estimate; code-tuned lineage may comply very differently).
- Hand-audit the 4 consulted transcripts: did the model read the *relevant* shard, and did the read visibly steer the plan? (Feeds the S-arm shard-relevance metric definition.)

## Addendum (2026-07-15, same day)

The `ls`-not-`cat` observation triggered a product fix: metatron PR #116 tightens the
consult-first wording in every managed artifact ("open the files — a directory listing
is not consultation"). All numbers above were measured under the **old** wording.
Before freeze, re-run the files condition with the new shipped text (pilot cell
"files-v2", 10 episodes/executor) — a before/after on contract wording is a free,
directly H1-relevant data point, and the prereg must embed the post-#116 text anyway.

## Addendum 2 — v2 wording result + detector correction (2026-07-15, evening)

**Detector bug found by hand-audit:** the pilot regex counted `context/` anywhere in a
command; a python edit-script comment ("full context/imports") produced a false
positive (files, django-15499). Corrected detector anchors the match to a shell read
command (`^(cat|ls|grep|head|tail|find|sed)\b … context…`). The frozen detector gets
this form + unit tests; the planned hand-audit protocol just proved its worth.

**Corrected consultation, gemma4:e4b, n=10/condition:**

| condition | consulted (strict) | gold-file hit |
|---|---|---|
| files (v1 contract) | 3/10 | 3/10 |
| files-v2 (0.11.1 contract, "open the files") | 2/10 | 1/10 |
| files-bare (no contract) | 0/10 | 2/10 |

**Conclusions:**
1. **Wording is not the lever at 8B.** The explicit "open the files — a directory
   listing is not consulting" wording did not raise consultation (3/10 → 2/10, noise).
   Which episodes consult is near-random across wordings (10449 consulted only under
   v1; 8459 only under v2). H1 point prediction: ⟨~25%⟩, band 20–40%.
2. **Depth did not move either — and no episode ever `cat`ed a decision file.** All
   observed consultations across all 20 contract episodes were `ls` or `grep` over
   `context/decisions/` — including under v2, whose text forbids exactly that
   (8459/v2: `ls -F context/decisions/` at turn 0). Filename/grep-snippet transfer is
   the *only* observed consumption mode at this capability tier.
3. **Design consequences:** (a) no contract-strength factor — two wordings are
   indistinguishable at pilot n, and the shipped v2 text is what the confirmatory
   study uses; (b) the S-arm token accounting must price `ls`/grep-based partial reads,
   not assume whole-file `cat`s; (c) the v1/v2 cells go in the paper as the
   design-iteration note: the product improved, and the measurement honestly shows
   wording alone doesn't close the compliance gap.

# Findings 07 — qwen2.5-coder:7b capability pilot: dropped as second executor

**Date:** 2026-07-15. Pilot gate 2 of PAPER2-DESIGN §8; feasibility only.
**Setup:** identical to FINDINGS-06 (10 pilot instances, same scaffold), conditions control and files (v1 contract); files-bare interrupted after 1 episode when the drop decision was made.

## Results

| condition | n | submitted | non-empty patch | gold-file hit | consulted |
|---|---|---|---|---|---|
| control | 10 | 3 | 2 | 1 | — |
| files (v1 contract) | 10 | 2 | 0 | 0 | **0** |

Format compliance was fine (0 invalid replies in both conditions); the failure mode is loop stamina — episodes exhaust the 20-turn cap without submitting or without edits that apply. Reference: gemma4:e4b on the same instances/conditions: 9–10/10 submitted, 7/10 non-empty, 40% consultation under the same contract.

## Decision (Pavel, 2026-07-15): drop qwen — gemma4:e4b is the sole executor

- **Fails the FINDINGS-03 capability bar** (non-empty patch 2/10 control vs gemma's 5/10 in the original pilot; submit rate 3/10). Below-floor executors yield no signal per GPU-hour on any arm.
- **0/10 consultation** under the shipped contract — as a second compliance estimate it would only measure the floor.
- Made **before prereg freeze, on pre-registered pilot-gate evidence** — record this file as the justification so the single-executor design needs no defense beyond it.

## Consequences

- PAPER2-DESIGN §3 → single executor; budget: 270 instances × 3 reps × 4 arms = **3,240 episodes ≈ 45 GPU-hours ≈ 3–4 overnight batches**.
- Generality across executors is out of scope for Paper 2 (state plainly in threats; the capability-dependence of compliance is itself visible in this file and citable).
- files-v2 wording comparison proceeds gemma-only.

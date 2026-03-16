# Extensions

Reserved extension points. Each is independent — activate only when
the base loop proves insufficient for your specific problem.

## EXT-1: Mutation-Prompt Co-Evolution

**Signal**: Same mutation type picked 3+ times without improvement.

Evolve the "how to mutate" instructions alongside the target prompt.
A meta-prompt generates mutation strategies; those strategies are scored
by whether they produce better prompts.

Based on: Promptbreeder (DeepMind) — dual-layer self-referential evolution.

## EXT-2: Instruction Effectiveness Tracking

**Signal**: Prompt exceeds 15 instructions; unclear which ones contribute.

Tag each instruction with a unique ID. Track which instructions are
causally relevant to correct outputs across epochs.

| Level | Triggered in | Action |
|-------|-------------|--------|
| Vital | >60% of correct outputs | Protect |
| Useful | 20-60% | Keep |
| Dormant | <5% | Stage 5 deletion candidate |
| Dead | 0% across 3 epochs | Delete |

Based on: Opus Agent `reflexion.ts` — self-observation of tool effectiveness.

## EXT-3: Pareto Frontier

**Signal**: Score oscillation — version A wins on T1-T4, version B wins on T5-T6.

Maintain a set of non-dominated prompt versions. Version A dominates B
iff A ≥ B on ALL test cases and strictly > on at least one.
Next mutation starts from the frontier member weakest on the lowest-scoring case.

Based on: EvoSkill (arXiv 2603.02766) — Pareto frontier for agent program selection.

## EXT-4: Canary Testing

**Signal**: A mutation causes catastrophic regression (>2.0 drop on any test case).

Before running full epoch, test mutation on 2 cases (one positive, one negative).
If either drops >1.5: abort without running full epoch.

Based on: Capability Evolver — canary deployment for prompt mutations.

## EXT-5: Multi-Dimensional Gating

**Signal**: Weighted average hides bad tradeoffs (high recall, terrible precision).

Replace single-score gate with per-dimension floors:

| Dimension | Floor | Stretch |
|-----------|-------|---------|
| (your dim 1) | ≥ 6.0 | ≥ 8.0 |
| (your dim 2) | ≥ 6.0 | ≥ 8.0 |

Accept mutation only if NO dimension drops below floor AND at least one improves.

Based on: plurigrid/skill-evolution — independent fitness axes.

## Activation Summary

| Signal | Extension |
|--------|-----------|
| Stuck on same mutation type | EXT-1 |
| Prompt too long, can't tell what matters | EXT-2 |
| Scores oscillate between versions | EXT-3 |
| Catastrophic regression after mutation | EXT-4 |
| Average score hides bad dimensions | EXT-5 |

**Default: run without extensions.** Add complexity only when earned.

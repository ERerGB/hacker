# Evolution Stages

Use stages as **gates**, not as narrative docs. Stay on a stage until stable.

## Stability Rule

Advance only when two consecutive epochs are within `±0.5` on overall score.

## Stage 1: Can It See? (Recall)

Goal: detect inputs that need action.

- Start with a minimal seed prompt.
- Optimize for missed positives first.

Gate:

- Recall >= 7.0
- Precision >= 5.0

## Stage 2: Does It Filter? (Precision)

Goal: remove false positives without collapsing recall.

- Add negative examples and boundary conditions.
- Tighten constraints only where failures occur.

Gate:

- Precision >= 7.0
- Recall >= 6.5

## Stage 3: Is Output Good? (Quality)

Goal: output is useful, not just correct-ish.

- Add format constraints and quality criteria.
- Keep non-essential style rules out until needed.

Gate:

- Quality >= 7.5
- Recall/Precision do not regress beyond tolerance

## Stage 4: Edge Cases

Goal: robustness under adversarial, ambiguous, or contradictory inputs.

- Add explicit handling for edge cases.
- Verify no weak-case collapse.

Gate:

- No test case below 5.0 on any key dimension

## Stage 5: Pruning

Goal: remove instructions with no measurable value.

- Delete one instruction per iteration.
- Re-run full epoch after every deletion.

Gate:

- Prompt length <= 80% of Stage 4
- Equal or better score profile

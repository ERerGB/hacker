# Mutation Menu

Apply exactly one mutation per iteration.

| ID | Mutation | Use when |
|----|----------|----------|
| M1 | Add constraint | False positives (`X` should not trigger) |
| M2 | Remove constraint | Recall is suppressed by over-filtering |
| M3 | Add positive example | Valid pattern is repeatedly missed |
| M4 | Add negative example | Wrong pattern keeps triggering |
| M5 | Rephrase instruction | Ambiguous wording causes inconsistency |
| M6 | Reorder instructions | Critical rule is buried too deep |
| M7 | Split instruction | One instruction is doing two jobs |
| M8 | Merge instructions | Two instructions duplicate intent |
| M9 | Delete instruction | Rule has no measurable impact |

Rules:

1. One mutation per iteration.
2. Never use `M9` before Stage 5.
3. Record mutation reason and affected failing test.
4. Reject mutation if any single test case drops more than `1.5`.

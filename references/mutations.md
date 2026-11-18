# Mutation Menu (Default Profile Example)

> This is an **example** set of mutation operators, not a fixed menu.
> Define your own operators in project config. See [config-schema.ts](config-schema.ts) for the interface.

Apply exactly one mutation per cycle.

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
2. Delete an instruction when a measured ablation supports it; a project may reserve pruning for a later stage, but there is no universal Stage 5 prerequisite.
3. Record mutation reason and affected failing test.
4. Use the project’s fixed acceptance gates. `1.5` is an example soft-score tolerance, not a default permission to regress.

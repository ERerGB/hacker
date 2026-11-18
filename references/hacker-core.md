# Hacker Core — one-cycle contract

Extracted from `SKILL.md` for composable use. Domain skills that don't need subagent-harness worker dispatch can reference this contract directly.

## Composition

| Sub-skill | Role | When needed |
| --- | --- | --- |
| **hacker-core** (this) | Invariants + one-cycle contract | Always |
| **hacker-loop** | Outer driver per runtime (Claude Code Agent, Cursor Ralph) | When sustaining multiple cycles |
| **hacker-corpus** | Corpus design + scoring contract (see `corpus-format.md`) | When bootstrapping a new corpus |
| **hacker-worker** | Isolated model evaluation; optional subagent-harness composition (see [hacker-worker.md](hacker-worker.md)) | When outputs require model generation; harness only for `.agent.md` |

**Domain example**: dictation = hacker-core + domain scorer (`pnpm dictation:corpus`). No hacker-worker is needed because the existing deterministic scorer evaluates the artifact directly. A SKILL.md candidate whose behavior requires model outputs still needs isolated model evaluation.

## Invariants

Violation of any invariant invalidates the cycle.

- **One behavioral mutation per cycle.** Either extend the candidate one change, or fix one corpus/scoring issue — not both unless they are the same hypothesis. Recording scores, state and the cycle log is bookkeeping, not another behavioral mutation.
- **Full re-run after every mutation.** The entire corpus must be scored after each change. No partial checks.
- **Accept uses fixed gates.** Default to no regression on previously passing cases. An explicitly configured soft-score tolerance may allow a bounded tradeoff; hard requirements still must pass. Never relax gates after seeing a candidate score.
- **Corpus is the contract.** Golden labels are append-only unless a case was wrongly labeled (then fix gold + log lesson).
- **Log every cycle.** Hypothesis, mutation, before/after, decision — even for rollbacks.

## The cycle (5 steps)

### 1. Score

Run the domain scorer against the full corpus.

- Record pass/fail + aggregate stats.
- The scorer is **project-configured** — a script, a function, a test suite. Hacker-core does not prescribe the scorer format.

### 2. Diagnose

If **FAIL**: identify the single worst failing case. Produce a testable hypothesis: "if [change], then [case N] should improve because [reason]."

If **PASS**: identify the single biggest **coverage or clarity gap** — an untested pattern, an ambiguous label, or a missing edge case. Still produce a hypothesis.

If **PASS and no gap remains**: the cycle is complete. Report "no mutation needed" and stop.

### 3. Mutate

Apply exactly **one** change to produce the next candidate state.

Mutation categories (pick one):
- **Candidate edit** — change the artifact under optimization (prompt section, bank entry, config value).
- **Corpus edit** — add/fix a golden row + its expected prediction.
- **Scorer edit** — fix a parsing bug or threshold in the scoring script.

Record: what changed, why, which diagnosis motivated it.

### 4. Re-run

Score the full corpus again after the mutation. Same scorer, same corpus (plus any new rows from step 3).

- If the diagnosed outcome improves and all fixed acceptance gates pass: **accept**. The new state becomes baseline.
- Otherwise: **rollback**, log the reason, and verify the restored baseline against the full corpus.
- A corpus/scorer correction changes the measurement contract: re-establish the baseline and do not claim its score change as candidate improvement.

### 5. Log

Append one row to the cycle log:

| Field | Content |
| --- | --- |
| **Date** | ISO date |
| **Worst fail id** | Case id or `—` (coverage gap) |
| **Hypothesis** | One sentence |
| **Mutation summary** | What changed |
| **Corpus pass** | Scorer output summary |

The log location is **project-configured** — a markdown table, a JSONL file, a scratchpad section.

## Stop conditions

Before starting, set a finite cycle/resource budget, a no-improvement limit and
an invocation deadline. Stop on the first exhausted limit, execution failure or
missing required access. Preserve the best verified candidate, scores and history;
report unmet goals instead of looping indefinitely. These limits apply when this
reference is invoked without the parent skill. See [driver contract](hacker-loop.md).

Within those limits, completion means the agreed success criteria pass and no known
material gap prevents that claim. Report untested cases and unresolved labels; do not
claim exhaustive coverage or keep inventing work after the requested goal is met.

## Anti-patterns

- **Multi-mutation cycles**: "while I'm here, let me also fix X" — breaks traceability.
- **Partial re-runs**: "I only changed bank row 5, so I'll only re-check G-005" — misses regressions.
- **Skipping log on rollback**: rollbacks carry lessons; log them.
- **Guessing without diagnosis**: jumping to mutation without identifying the worst case first.

## Relationship to SKILL.md

[The main skill](../SKILL.md) chooses the evaluator and scope. This reference is the
scorer-agnostic core; [worker dispatch](hacker-worker.md) adds isolation and optional
subagent-harness composition only for model-evaluated candidates.

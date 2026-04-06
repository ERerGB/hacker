# Hacker Core — one-cycle contract

Extracted from `SKILL.md` for composable use. Domain skills that don't need subagent-harness worker dispatch can reference this contract directly.

## Composition

| Sub-skill | Role | When needed |
| --- | --- | --- |
| **hacker-core** (this) | Invariants + one-cycle contract | Always |
| **hacker-loop** | Outer driver per runtime (Claude Code Agent, Cursor Ralph) | When sustaining multiple cycles |
| **hacker-corpus** | Corpus design + scoring contract (see `corpus-format.md`) | When bootstrapping a new corpus |
| **hacker-worker** | subagent-harness dispatch for prompt/agent candidates (see `SKILL.md` steps 1-2) | Only when the candidate is an `.agent.md` file |

**Domain example**: dictation = hacker-core + domain scorer (`pnpm dictation:corpus`). No hacker-worker needed because the candidate is a SKILL.md section, not a prompt agent.

## Invariants

Violation of any invariant invalidates the cycle.

- **One mutation per cycle.** Either extend the candidate one change, or fix one corpus/scoring issue — not both unless they are the same hypothesis.
- **Full re-run after every mutation.** The entire corpus must be scored after each change. No partial checks.
- **Accept requires no regression.** A change that fixes one case but breaks another is rejected.
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

- If green: **accept**. New state becomes baseline.
- If regression: **rollback**. Revert the mutation, log the failure reason.

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

The candidate is done when **all** of:
- Corpus passes with no failures.
- No coverage gap remains (all known patterns have golden rows).
- No clarity gap remains (no ambiguous labels that should be resolved).

## Anti-patterns

- **Multi-mutation cycles**: "while I'm here, let me also fix X" — breaks traceability.
- **Partial re-runs**: "I only changed bank row 5, so I'll only re-check G-005" — misses regressions.
- **Skipping log on rollback**: rollbacks carry lessons; log them.
- **Guessing without diagnosis**: jumping to mutation without identifying the worst case first.

## Relationship to SKILL.md

`SKILL.md` is the full 10-step cycle with subagent-harness integration (parse → validate → compose → dispatch → verify → score → diagnose → mutate → re-run → decide → log). This reference extracts the **scorer-agnostic core** (5 steps) for domains that don't use `.agent.md` candidates or N-worker dispatch.

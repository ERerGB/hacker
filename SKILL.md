---
name: hacker
description: >
  Evidence-driven prompt and agent evolution engine.
  Runs candidates against a test corpus, scores outputs, diagnoses failures,
  explores external evidence, and applies targeted single-variable mutations.
  Use when you need to systematically improve any LLM prompt or agent
  configuration beyond what manual tweaking achieves.
license: MIT
metadata:
  author: ERerGB
  version: "0.2.0"
  tags: prompt-evolution, optimization, breeding, testing, evidence-driven
compatibility: Cursor, Claude Code, Codex
allowed-tools: Read Write Shell WebSearch Grep
---

# Hacker

Evolve any LLM prompt or agent configuration through evidence-driven iteration.

```
Corpus (fixed)       Candidate (evolving)       Golden Labels (fixed)
      ↓                      ↓                         ↓
  [Run] ──▶ isolated outputs ──▶ [Score] ──▶ [Diagnose]
    ▲                                             │
    │                                             ▼
 [Re-run] ◀── [Mutate] ◀── [Select] ◀── [Explore]
    │
 accept / rollback
```

Core idea: treat prompt engineering like training a model.
You need a dataset (corpus), a loss function (scoring), a training loop
(run → score → diagnose → explore → select → mutate → re-run),
and acceptance criteria (regression gate).

---

## Invariants

Violation of any invariant invalidates the cycle.

- **INVARIANT**: each test case runs in an isolated worker context.
- **INVARIANT**: controller never generates model outputs; it only scores.
- **INVARIANT**: workers must not see golden labels, other test cases, or prior context.
- **INVARIANT**: one mutation per cycle.
- **INVARIANT**: accept/rollback decisions require full-corpus re-run.

---

## The Cycle

Each iteration follows this exact sequence.

### 1. Run

Dispatch each corpus entry to an isolated worker.

Worker dispatch shape:

```markdown
You are a worker evaluator. Do not score and do not explain.

## Prompt Under Test
{candidate_verbatim}

## Input
{single_test_case_input}

## Output Schema
{worker_output_schema}

Return ONLY schema-compliant output.
If prompt indicates no action, return:
{"decision":"no_output","outputs":[]}
```

### 2. Verify

Before scoring, confirm isolation:

- [ ] each case ran in a fresh worker
- [ ] workers did not receive golden labels
- [ ] workers did not receive other test cases
- [ ] controller only scored worker outputs (no inline generation)

If any item is unchecked: cycle is invalid, re-run.

### 3. Score

Compare worker outputs against golden labels.

- Produce per-case scores across configured dimensions.
- Record both aggregate (mean, median) and tail (min, failure rate).
- Hard-check failures (format, safety) are separate from soft scores.

Scoring dimensions, weights, and thresholds are **project-level configuration**.
See [Configuration](#configuration) for how to define them.

### 4. Diagnose

Identify the single primary failure mode for this cycle.

- Focus on the worst-scoring case.
- Produce a testable hypothesis: "if [change], then [case N] should improve because [reason]."
- Do not attempt to fix multiple failure modes in one cycle.

### 5. Explore

Search for external evidence that can inform the mutation.

Explore is not optional decoration — it is the upstream supply system for Mutate.
Without evidence, mutations degrade to guesswork.

Sources (configured per project):
- Web search (papers, docs, community discussions)
- Skill hubs (ClawHub, LobeHub, Cursor Skills, etc.)
- Local memory (past cycle logs, prior art)

Each retrieved item must be structured as an **Evidence Card**:

```
artifact        — the skill/prompt/pattern snippet or pointer
source_ref      — URL or internal reference (traceable)
hypothesis      — which failure mode it addresses
risk            — what side effects it might introduce
confidence      — estimated relevance (0-1)
```

### 6. Select

Filter evidence before it enters Mutate. Three gates:

- **Relevance**: directly addresses the diagnosed failure mode.
- **Executability**: can be expressed as a single mutation.
- **Verifiability**: effect is observable in the current corpus.

Reject evidence that fails any gate. Record rejections with reasons.

### 7. Mutate

Apply exactly one change to produce the next candidate.

- The mutation must link to at least one Evidence Card (when Explore is enabled).
- Record: what changed, why, which evidence supported it.
- Do not bundle unrelated improvements.

### 8. Re-run

Re-dispatch the full corpus against the mutated candidate.
Same isolation rules as Step 1.

### 9. Decide

Compare re-run results against the previous baseline.

Acceptance criteria are **project-level configuration**. Common patterns:
- Overall score improves.
- No single case regresses beyond a configured tolerance.
- All hard-check constraints still pass.

If accepted: new candidate becomes baseline.
If rejected: rollback, log the failure reason, carry the lesson forward.

### 10. Log

Record the full cycle for auditability and future strategy selection:

- `hypothesis`
- `evidence_used` (Evidence Card IDs)
- `mutation_applied`
- `before_scores` / `after_scores`
- `decision` (accept/rollback)
- `lesson`

---

## Configuration

Hacker does not ship built-in stages, mutation menus, or scoring thresholds.
These are **project-level policy** that you configure per use case.

A configuration defines:

| Section | What you configure | Example |
|---------|--------------------|---------|
| `evaluation` | Scoring dimensions, weights, hard checks | `{recall: 0.4, precision: 0.3, quality: 0.3}` |
| `explore` | Search providers, budget, evidence schema | `{providers: ["web", "lobehub"], topK: 5}` |
| `mutation` | Available mutators, evidence requirement | `{requireEvidenceLink: true}` |
| `acceptance` | Gate thresholds, regression tolerance | `{minImprovement: 0.1, maxCaseDrop: 1.5}` |
| `stages` | Optional phased curriculum | `[{name: "recall", gate: {...}}, ...]` |
| `guards` | Global invariants | `{maxMutationsPerCycle: 1, fullCorpusRerun: true}` |

See [references/config-schema.ts](references/config-schema.ts) for the full
TypeScript interface. Drop a `hacker.config.ts` (or `.yaml`/`.json`) in your
project root to override defaults.

Default profiles are provided as **examples**, not as canonical truth:
- [references/stages.md](references/stages.md) — a 5-stage curriculum example
- [references/mutations.md](references/mutations.md) — a 9-operator mutation menu example

---

## Corpus Design

See [references/corpus-format.md](references/corpus-format.md) for structure.

Key rules:
- Minimum 6 test cases.
- At least 2 negative cases (expected output: "do nothing").
- At least 1 adversarial case.
- Diversity over volume.

---

## Platform Hints for Isolation

| Platform | Isolation strategy |
|----------|--------------------|
| Cursor | Spawn one `Task` sub-agent per test case |
| Claude Code | Spawn one subagent per test case with fresh context |
| Codex | Run one isolated process per case (no shared state) |

---

## State Tracking

Track all state in a single scratchpad file:

```markdown
## Current Focus
- target: my-classifier-prompt
- candidate_version: v5
- cycle: 12

## Cycle Log

### Cycle 12
- diagnosis: T3 false positive — prompt triggers on frontend errors
- explore: found constraint pattern from [source_ref]
- evidence: {artifact: "exclude frontend frameworks", confidence: 0.8}
- mutation: added exclusion rule for frontend terminology
- before: [T1:7, T2:7, T3:4, T4:8, T5:6, T6:7] avg=6.5
- after:  [T1:7, T2:7, T3:7, T4:8, T5:6, T6:7] avg=7.0
- decision: ACCEPT
- lesson: category exclusions more effective than keyword blocklists

## Current Candidate (v5)
[full prompt text here]
```

---

## Integration with Ralph Loop

Set up scratchpad at `.cursor/ralph/scratchpad.md`.
Each Ralph iteration drives one Hacker cycle:

1. Read scratchpad (candidate version, previous scores).
2. Run full corpus (isolated workers).
3. Verify isolation.
4. Score outputs.
5. Diagnose worst failure.
6. Explore external evidence.
7. Select best-fit evidence.
8. Apply one mutation.
9. Re-run full corpus.
10. Accept or rollback; update scratchpad.

---

## When to Use This

- A prompt works on demos but fails on edge cases.
- You've been tweaking a prompt for hours with diminishing returns.
- You need evidence that version A is better than version B.
- You want to find the minimal prompt that still performs well.
- You want mutations grounded in external evidence, not intuition.

---

## When to Stop

The candidate is done when ALL of:
- Configured stage gates passed with stable scores.
- Pruning completed (if configured).
- No test case below configured floor on any dimension.
- You can explain why every instruction exists.

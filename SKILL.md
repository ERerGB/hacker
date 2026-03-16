---
name: hacker
description: >
  Evolutionary prompt optimization via corpus-evaluated epochs.
  Breeds LLM prompts by running them against a test corpus, scoring outputs
  against golden labels, diagnosing failures, and applying targeted mutations.
  Use when you need to systematically improve any LLM prompt — classifiers,
  extractors, agents, system prompts — beyond what manual tweaking achieves.
license: MIT
metadata:
  author: ERerGB
  version: "0.1.0"
  tags: prompt-evolution, optimization, breeding, testing
compatibility: Cursor, Claude Code, Codex
allowed-tools: Read Write Shell WebSearch Grep
---

# Hacker

Evolve any LLM prompt through data-driven iteration instead of guesswork.

```
Test Corpus (fixed)          Prompt (evolving)           Golden Labels (fixed)
      ↓                             ↓                           ↓
[dispatch N isolated workers] → N raw worker outputs → [controller scoring]
                                                             ↓
                                                    [failure diagnosis]
                                                             ↓
                                                   [one targeted mutation]
                                                             ↓
                                                      [re-dispatch epoch]
                                                             ↓
                                                   accept / rollback
```

The idea is simple: treat prompt engineering like training a model.
You need a dataset (test corpus), a loss function (scoring rubric),
and a training loop (epoch → diagnose → mutate → repeat).

## Protocol-First Quick Start

### 0. Invariant (Read First)

Violation of any invariant invalidates the epoch.

- **INVARIANT**: each test case must run in an isolated worker context.
- **INVARIANT**: controller never generates model outputs; it only scores worker outputs.
- **INVARIANT**: workers must not see golden labels, other test cases, or prior worker context.
- **INVARIANT**: one mutation per iteration.

### 1. Dispatch (Run Isolated Workers)

For each corpus entry, run one isolated worker.

Use this exact worker dispatch shape:

```markdown
You are a worker evaluator. Do not score and do not explain.

## Prompt Under Test
{prompt_version_verbatim}

## Input
{single_test_case_input}

## Output Schema
{fixed_worker_output_schema}

Return ONLY schema-compliant output.
If prompt indicates no action, return:
{"decision":"no_output","outputs":[]}
```

### 2. Verify (Isolation Checklist)

Before moving to scoring and diagnosis:

- [ ] each case was run in a fresh worker
- [ ] workers did not receive golden labels
- [ ] workers did not receive other test cases
- [ ] controller only scored worker outputs (no inline generation)

If any item is unchecked: epoch is invalid, re-run correctly.

### 3. Prepare Corpus and Scoring

Create 6-8 test cases that represent the full range of inputs your prompt
will see in production. Each test case has an input and expected output.

**Read [references/corpus-format.md](references/corpus-format.md) now**
before creating your corpus.

Key: include at least 2 "negative" cases where the correct output is
"do nothing" or "reject." These prevent false-positive overfitting.

Pick 2-4 dimensions that matter for your use case. Examples:

| Use Case | Dimensions |
|----------|-----------|
| Classifier | Recall, Precision, Edge-case handling |
| Extractor | Completeness, Accuracy, Format compliance |
| Agent system prompt | Task success, Safety, Efficiency |
| Creative writing | Relevance, Originality, Tone consistency |

Each dimension scores 0-10. Assign weights that reflect your priorities.

### 4. Start with a Seed Prompt

Write the simplest possible prompt that captures your intent — 2-3 sentences.
Don't optimize upfront. The breeder will grow it.

### 5. Score, Diagnose, Mutate, Re-run

Each iteration follows this exact sequence:

**Step 1: Collect and Score** — Compare each worker output against golden labels.

**Step 2: Diagnose** — Find the worst-scoring test and identify root cause.

**Step 3: Mutate** — Apply exactly one mutation.

**Step 4: Re-run Full Epoch** — Re-dispatch all tests, then compare score profile.

Accept only if:

- overall score improves, and
- no single case drops > 1.5.

Otherwise rollback.

### Platform Hints for Isolation

| Platform | Isolation strategy |
|----------|--------------------|
| Cursor | Spawn one `Task` sub-agent per test case |
| Claude Code | Spawn one subagent per test case with fresh context |
| Codex | Run one isolated process per case (no shared state) |

See [references/stages.md](references/stages.md) for stage goals and gates.
See [references/mutations.md](references/mutations.md) for mutation operators.

## When to Use This

- A prompt works on your demo example but fails on edge cases
- You've been tweaking a prompt for hours with diminishing returns
- You need evidence that version A is better than version B
- You want to find the minimal prompt that still performs well

## State Tracking

Track all state in a single scratchpad file. Recommended format:

```markdown
## Current Focus
- stage: 2
- target: my-classifier-prompt
- prompt_version: v5

## Evolution Log

### Stage 1: Can It See?
- v1 (seed): "Classify whether the input contains..."
  - Worker outputs:
    - T1: {"decision":"output","outputs":[...]}
    - T2: {"decision":"output","outputs":[...]}
    - T3: {"decision":"output","outputs":[...]}  # wrong vs golden
  - Epoch 1 scores: [T1:6, T2:7, T3:4, T4:8, T5:5, T6:7] avg=6.17
  - Isolation check: PASS
  - Diagnosis: T3 — missed subtle case
  - Mutation: M3 — added example of implicit pattern
- v2: [updated prompt]
  - Worker outputs: ...
  - Epoch 2 scores: [T1:7, T2:7, T3:7, T4:8, T5:6, T6:7] avg=7.00 ✓ STABLE
  - Isolation check: PASS
  - → Advance to Stage 2

## Current Prompt (v5)
[full prompt text here]
```

## Integration with Ralph Loop

If using with Cursor's Ralph Loop, set up the scratchpad at
`.cursor/ralph/scratchpad.md` and include the evolution log inline.
The loop's automatic re-invocation drives the epoch cycle.

### One Ralph Iteration with Hacker

1. Read scratchpad (stage, prompt version, previous scores).
2. Dispatch N isolated workers (one per test case).
3. Collect raw worker outputs.
4. Score outputs against golden labels.
5. Run isolation verification checklist.
6. Diagnose worst failure.
7. Apply one mutation.
8. Update scratchpad; next iteration re-runs full epoch.

## Research Protocol

Use web search during diagnosis to ground mutations in evidence:

- "What makes X detectable by LLMs?" → improve recall
- "Common false positive patterns in Y" → improve precision
- "Best practices for Z output format" → improve quality

Every mutation should be traceable to a specific failure on a specific
test case, with a reasoned hypothesis for why the change will help.

## When to Stop

The prompt is done when ALL of:
- All stages passed with stable scores
- Stage 5 pruning completed
- No test case below 5.0 on any dimension
- You can explain why every instruction exists

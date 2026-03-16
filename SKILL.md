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
Test Corpus (fixed)       Prompt (evolving)      Golden Labels (fixed)
      ↓                        ↓                       ↓
   [ epoch run ]  →  outputs  →  [ score ]  →  fitness
                                                   ↓
                                          [ failure diagnosis ]
                                                   ↓
                                          [ targeted mutation ]
                                                   ↓
                                          [ re-run full epoch ]
                                                   ↓
                                     accept (better) / rollback
```

The idea is simple: treat prompt engineering like training a model.
You need a dataset (test corpus), a loss function (scoring rubric),
and a training loop (epoch → diagnose → mutate → repeat).

## When to Use This

- A prompt works on your demo example but fails on edge cases
- You've been tweaking a prompt for hours with diminishing returns
- You need evidence that version A is better than version B
- You want to find the minimal prompt that still performs well

## Quick Start

### 0. Lock Execution Isolation (Required)

Treat each evaluation run as a fresh runtime process.

- Keep one **controller** session for loop control only (score, diagnose, mutate, accept/rollback).
- Run every test case with an isolated **worker** (fresh sub-agent/process).
- Worker input is limited to:
  - current prompt version,
  - current skill set,
  - one test case input,
  - fixed output schema.
- Do **not** reuse controller chat/session context for worker inference.

Why: this prevents context leakage from being mistaken as prompt improvement.

### 1. Define Your Corpus

Create 6-8 test cases that represent the full range of inputs your prompt
will see in production. Each test case has an input and expected output.

See [references/corpus-format.md](references/corpus-format.md) for the format.

Key: include at least 2 "negative" cases where the correct output is
"do nothing" or "reject." These prevent false-positive overfitting.

### 2. Define Your Scoring

Pick 2-4 dimensions that matter for your use case. Examples:

| Use Case | Dimensions |
|----------|-----------|
| Classifier | Recall, Precision, Edge-case handling |
| Extractor | Completeness, Accuracy, Format compliance |
| Agent system prompt | Task success, Safety, Efficiency |
| Creative writing | Relevance, Originality, Tone consistency |

Each dimension scores 0-10. Assign weights that reflect your priorities.

### 3. Start with a Seed Prompt

Write the simplest possible prompt that captures your intent — 2-3 sentences.
Don't optimize upfront. The breeder will grow it.

### 4. Run the Loop

Each iteration follows this exact sequence:

**Step 1: Run Epoch** — For EACH corpus entry, spawn a fresh worker and run inference.
Collect outputs for ALL corpus entries, then score each.

**Step 2: Diagnose** — Find the lowest-scoring test case. Ask: WHY did the
prompt fail here? Map the failure to a mutation type.

**Step 3: Mutate** — Apply exactly ONE change from the mutation menu.
Never change multiple things at once.

**Step 4: Re-run Epoch** — Test the mutated prompt against ALL corpus entries.
If overall score improved and no single test case dropped >1.5 points: accept.
Otherwise: rollback.

**Step 5: Check Stability** — If 2 consecutive epochs score within ±0.5:
current stage is complete. Advance to next stage.

## Evolution Stages

Each stage has a clear goal. Only advance when stable.

### Stage 1: Can It See? (Recall)

The prompt correctly identifies inputs that need action.
Start here. Simplest seed prompt. No fancy instructions.

**Gate**: Recall ≥ 7.0 across all test cases, Precision ≥ 5.0.

### Stage 2: Does It Filter? (Precision)

Eliminate false positives without losing recall.
Add negative examples and boundary conditions.

**Gate**: Precision ≥ 7.0, Recall stays ≥ 6.5.

### Stage 3: Is the Output Good? (Quality)

Output content meets your quality bar.
Add format instructions, examples, and quality standards.

**Gate**: Quality ≥ 7.5, other scores maintained.

### Stage 4: Edge Cases

Test against adversarial and unusual inputs.
Add handling for ambiguous cases, missing data, conflicting signals.

**Gate**: No test case scores below 5.0 on any dimension.

### Stage 5: Pruning

Remove instructions that don't affect scores.
Delete one instruction at a time. Re-run epoch. Keep deletion if scores hold.

This stage almost always makes the prompt shorter AND better.

**Gate**: Prompt is ≤80% of its Stage 4 length with equal or better scores.

## Mutation Menu

When diagnosis identifies a failure, pick the most targeted fix:

| ID | Mutation | When to use |
|----|----------|-------------|
| M1 | Add constraint | False positives: "X does NOT count as Y" |
| M2 | Remove constraint | Missed recall: over-filtering |
| M3 | Add positive example | Prompt doesn't recognize a valid pattern |
| M4 | Add negative example | Prompt triggers on wrong patterns |
| M5 | Rephrase instruction | Ambiguous wording causing inconsistency |
| M6 | Reorder instructions | Important rule buried too deep in prompt |
| M7 | Split instruction | One rule trying to do two things |
| M8 | Merge instructions | Two rules saying the same thing differently |
| M9 | Delete instruction | Instruction has no measurable effect |

**Rules**:
- Apply exactly one mutation per iteration
- Never use M9 before Stage 5
- Always record what you changed and why

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
  - Epoch 1: [T1:6, T2:7, T3:4, T4:8, T5:5, T6:7] avg=6.17
  - Diagnosis: T3 — missed subtle case (no explicit keyword)
  - Mutation: M3 — added example of implicit pattern
- v2: [updated prompt]
  - Epoch 2: [T1:7, T2:7, T3:7, T4:8, T5:6, T6:7] avg=7.00 ✓ STABLE
  - → Advance to Stage 2

## Current Prompt (v5)
[full prompt text here]
```

## Integration with Ralph Loop

If using with Cursor's Ralph Loop, set up the scratchpad at
`.cursor/ralph/scratchpad.md` and include the evolution log inline.
The loop's automatic re-invocation drives the epoch cycle.

Recommended role split:

- **Ralph/controller turn**: chooses mutation, keeps history, computes scores.
- **Worker runs**: execute prompt+skills on transcript cases in isolated fresh runtime.
- **Rule**: no worker may inherit prior worker conversation memory.

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

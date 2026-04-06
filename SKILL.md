---
name: hacker
description: >
  Define a problem. Aggregate all best practices. Hack it.
  Problem-driven optimization engine for LLM prompts and agent configurations.
  Runs candidates against a test corpus, scores outputs, diagnoses failures,
  explores external evidence, and applies targeted single-variable mutations.
  In Cursor, pair with the ralph-loop skill (/ralph-loop) so each chat turn runs
  exactly one Hacker cycle until completion_promise or max_iterations.
license: MIT
metadata:
  author: ERerGB
  version: "0.2.2"
  tags: problem-driven, best-practices, evidence-driven, optimization, agent-evolution, ralph-loop
---

# Hacker

Define a problem. Aggregate all best practices. Hack it.

You have a prompt that mostly works. Some cases fail. You don't know which
change will fix them without breaking the ones that already pass. So you
guess, test one case, ship, and hope.

Hacker eliminates the guessing. You define the problem as a test corpus
with golden labels. The engine scores every case, diagnoses the single
worst failure, searches the world for evidence-backed solutions, applies
one precise change, re-runs the full corpus, and accepts only if nothing
regressed. One cycle, one variable, full accountability.

```
  [Define]                    [Aggregate]              [Hack]
      ↓                            ↓                      ↓
 Corpus + Labels ──▶ Score ──▶ Diagnose ──▶ Explore ──▶ Mutate ──▶ Re-run
                                                                      ↓
                                                              accept / rollback
```

## Sustaining many cycles (Cursor + Ralph Loop)

Hacker defines **one** cycle (steps 1–10). It does **not** re-invoke itself.

To **keep going** turn after turn until a stop rule fires, use Cursor’s **`ralph-loop`** skill (**`/ralph-loop`**) as the outer driver:

1. Run **`/ralph-loop`** (or attach the **Ralph Loop** skill) and set `max_iterations` + optional `completion_promise` in `.cursor/ralph/scratchpad.md`.
2. Put your **Hacker task** in the scratchpad **body** (corpus path, candidate path, scoring command). Instruct the agent: **each iteration = exactly one Hacker cycle** (one diagnosis, one mutation, full re-run, log) — see **Cursor — Ralph Loop** below for a paste-ready template.
3. On every follow-up, Ralph replays the same prompt; the agent reads the scratchpad, runs the next cycle, appends **Cycle Log**, bumps `iteration` in YAML.

If you skip Ralph Loop, you must **manually** send the same “run one Hacker cycle” instruction each time.

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

**Candidate format**: The candidate under optimization is a
[subagent-harness](https://github.com/ERerGB/subagent-harness) `.agent.md` file.
This gives the cycle a structured representation to read, mutate, and write back.

The Run phase is a three-step pipeline:

```
.agent.md → parse → validate → compose → dispatch N workers
```

1. **Parse** — `parseRichAgentMarkdown(path, content)` → `RichAgentDocument`
2. **Validate** — `validateRichAgent(doc, options?)` → confirm schema integrity (optional `extensionValidator` in `options` for `.agent.ext.yaml` fields; see `subagent-harness` `ValidateOptions`)
3. **Compose** — `composeSubagent(doc, target, profile?)` → runtime-ready artifact (`target`: `cursor` | `codex` | `claude-code` | `production`)
4. **Dispatch** — send the composed artifact to N isolated workers (one per test case)

Worker dispatch shape:

```markdown
You are a worker evaluator. Do not score and do not explain.

## Prompt Under Test
{composed_candidate}

## Input
{single_test_case_input}

## Output Schema
{worker_output_schema}

Return ONLY schema-compliant output.
If prompt indicates no action, return:
{"decision":"no_output","outputs":[]}
```

The `composed_candidate` is the output of `composeSubagent()`, not the raw
`.agent.md` source. Workers receive the runtime-native format for their platform.

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
- Skill hubs and public prompt repositories
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

The mutation operates on the structured `RichAgentDocument` via `patchAgent()`:

```
patchAgent(doc, { path, value }) → mutatedDoc (immutable)
```

Supported patch paths:
- `body` — the prompt text (most common mutation target)
- `model.temperature`, `model.name` — model configuration
- `extensions.*` — consumer-defined metadata (e.g. evolution state)

After patching:
1. **Validate** — `validateRichAgent(mutatedDoc, options?)` to confirm the mutation didn't break schema
2. **Serialize** — `serializeAgent(mutatedDoc)` to write back the updated `.agent.md`
3. **Record** — what changed, why, which evidence supported it

Constraints:
- The mutation must link to at least one Evidence Card (when Explore is enabled).
- Do not bundle unrelated improvements.
- One `patchAgent()` call per cycle.

### 8. Re-run

Re-dispatch the full corpus against the mutated candidate.

Same pipeline as Step 1:

```
mutated .agent.md → parse → validate → compose → dispatch N workers
```

Same isolation rules apply. The re-run uses the serialized output from Step 7,
not an in-memory representation — ensuring the written `.agent.md` is the
source of truth for scoring.

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
- `mutation_applied` (the `PatchOp` that was applied)
- `before_scores` / `after_scores`
- `decision` (accept/rollback)
- `lesson`

Cycle metadata is also persisted in the candidate's `extensions` field via:

```
patchAgent(doc, { path: "extensions.evolution", value: { cycle, scores, ... } })
```

This keeps the `.agent.md` self-describing — any consumer can read its
evolution history without external state files.

---

## Configuration

Hacker does not ship built-in stages, mutation menus, or scoring thresholds.
These are **project-level policy** that you configure per use case.

A configuration defines:

| Section | What you configure | Example |
|---------|--------------------|---------|
| `candidate` | Source `.agent.md` path and compose target | `{path: "agents/bot.agent.md", target: "cursor"}` |
| `evaluation` | Scoring dimensions, weights, hard checks | `{recall: 0.4, precision: 0.3, quality: 0.3}` |
| `explore` | Search providers, budget, evidence schema | `{providers: ["web", "lobehub"], topK: 5}` |
| `mutation` | Available mutators, evidence requirement | `{requireEvidenceLink: true}` |
| `acceptance` | Gate thresholds, regression tolerance | `{minImprovement: 0.1, maxCaseDrop: 1.5}` |
| `stages` | Optional phased curriculum | `[{name: "recall", gate: {...}}, ...]` |
| `guards` | Global invariants | `{maxMutationsPerCycle: 1, fullCorpusRerun: true}` |

See [references/config-schema.ts](references/config-schema.ts) for the full
TypeScript interface (re-exports `subagent-harness` types and APIs; run `pnpm install` or `npm install` in the Hacker repo root for typecheck). Drop a `hacker.config.ts` (or `.yaml`/`.json`) in your
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

## Runtime Discovery for Isolation

Use capability discovery instead of hardcoding platform adapters.

1. Discover whether the runtime supports isolated worker execution primitives.
2. Prefer one-worker-per-test-case isolation if available.
3. If subagents are unavailable, use separate processes/contexts to avoid shared state.
4. Validate isolation explicitly in the Verify step before scoring.

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

## Integration with Iterative Loop Runners

Hacker does **not** ship a Ralph Loop plugin, a Claude `/loop` binding, or any
executable loop driver. The skill defines **what one cycle does**; your IDE or
CLI provides **what re-invokes the agent** after each turn.

**Contract**: one external iteration = exactly one Hacker cycle (steps 1–10).
The scratchpad is the durable state between invocations. The loop runner only
needs to feed the same high-level instruction back until `completion_promise`
is satisfied or `max_iterations` is hit.

### Cursor — Ralph Loop

**Pairing**: **`hacker`** (this file) = the procedure for **one** cycle. **`ralph-loop`** = the mechanism that **re-sends** your task each turn. Invoke **`/ralph-loop`** first so the Ralph skill creates the scratchpad; then edit the body to be Hacker-specific.

If you use Cursor's **Ralph Loop** (maintains `.cursor/ralph/scratchpad.md` and re-posts your task each turn):

1. Create `.cursor/ralph/` and initialize `scratchpad.md` with YAML frontmatter (per **ralph-loop** skill): `iteration`, `max_iterations`, `completion_promise` (optional; quote if special chars).
2. **Body — paste-ready Hacker template** (customize paths and stop rule):

   ```markdown
   Read the full file `.cursor/ralph/scratchpad.md` (YAML + body) before acting.

   Run exactly **one** Hacker cycle per `~/.cursor/skills/hacker/SKILL.md` (steps 1–10):
   - Candidate: <path to .agent.md or skill under test>
   - Corpus: <path to gold / test cases>
   - Run → Verify isolation → Score → Diagnose **single** worst case → Explore → **One** Mutate → Re-run full corpus → Decide → Log

   At end of this turn:
   - Append a `### Cycle <n>` block under `## Cycle Log` (diagnosis, evidence, mutation, before/after scores, decision, lesson).
   - Update YAML `iteration` to `<n+1>` (or follow Ralph Loop conventions).

   Stop: output the completion token required by `completion_promise` **only** when <e.g. corpus all green AND no open stage failures>.
   ```

3. Each Ralph iteration re-posts the task; the agent reads the scratchpad,
   executes **one** full Hacker cycle, updates scores and cycle log, bumps iteration.
4. Align `completion_promise` with Hacker stop rules (e.g. all stage gates green,
   or weighted narrative score ≥ target for doc-only runs).

Default scratchpad path: **`.cursor/ralph/scratchpad.md`** (project-local; any path works if the task names it explicitly).

### Claude Code — Agent + CronCreate

Use the **Agent tool** (subagent) for cycle isolation and **CronCreate** for sustained iteration. Each cron fire launches a fresh subagent that reads the corpus, runs one cycle, and returns a one-line summary — no scratchpad needed (stateless).

See **[references/hacker-loop.md](references/hacker-loop.md)** for the full Agent prompt template and setup instructions.

Quick setup: `/loop 10m /hacker <domain>` — creates a cron that delegates each cycle to a subagent.

### Headless / CI (optional)

A shell loop can call your agent CLI with a fixed prompt file that includes
"read `hacker-scratchpad.md`, run one cycle, exit." That is the same contract
without IDE integration.

See **[references/hacker-loop.md](references/hacker-loop.md)** for all three runtimes.

### Per-iteration checklist (all runners)

1. Read scratchpad (candidate version, prior scores, cycle history).
2. Run full corpus (isolated workers).
3. Verify isolation.
4. Score outputs.
5. Diagnose worst failure.
6. Explore external evidence.
7. Select best-fit evidence.
8. Apply one mutation.
9. Re-run full corpus.
10. Accept or rollback; update scratchpad (and bump loop `iteration` if using Ralph frontmatter).

---

## Composable Sub-Skills

For domains that **don't need subagent-harness** (e.g. the candidate is a SKILL.md section scored by a script, not an `.agent.md` dispatched to N workers), use the extracted references:

| Reference | What it covers | When to use |
| --- | --- | --- |
| **[hacker-core.md](references/hacker-core.md)** | 5-step cycle contract (score → diagnose → mutate → re-run → log), invariants, stop conditions | Domain skills that compose with hacker but skip worker dispatch |
| **[hacker-loop.md](references/hacker-loop.md)** | Claude Code Agent template, Cursor Ralph, CI loop drivers | Sustaining cycles across any runtime |
| **[corpus-format.md](references/corpus-format.md)** | Corpus design, golden labels, worker output schema | Bootstrapping a new test corpus |

**Full SKILL.md** (this file) remains the canonical reference for `.agent.md` candidates with subagent-harness integration.

---

## When to Use This

- A prompt works on demos but fails on edge cases.
- You've been tweaking a prompt for hours with diminishing returns.
- You need evidence that version A is better than version B.
- You want to find the minimal prompt that still performs well.
- You want mutations grounded in external evidence, not intuition.
- You want **many** sequential cycles without pasting the same prompt each time → start **`/ralph-loop`** and put the Hacker task + corpus paths in `.cursor/ralph/scratchpad.md` (see **Sustaining many cycles** above).

---

## When to Stop

The candidate is done when ALL of:
- Configured stage gates passed with stable scores.
- Pruning completed (if configured).
- No test case below configured floor on any dimension.
- You can explain why every instruction exists.

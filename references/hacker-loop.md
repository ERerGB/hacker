# Hacker Loop — sustained cycle drivers

This reference documents **how to keep running hacker-core cycles** across different runtimes. The main `SKILL.md` already covers Ralph Loop for Cursor; this file adds first-class support for **Claude Code** and standardizes the contract.

## Contract (all runtimes)

One external iteration = exactly one hacker-core cycle (5 steps). The loop driver only needs to:
1. Feed the same instruction each turn
2. Let the agent read/write the corpus + cycle log
3. Stop when the completion condition is met

## Claude Code — Agent + CronCreate

```
CronCreate (*/Nm) ──> Agent (subagent) ──> one hacker-core cycle ──> one-line summary
                             ^                        |
                        fresh context           read/write corpus + log
```

Each cron fire launches a **fresh subagent** via the Agent tool. The subagent:
1. Reads the corpus, scorer output, and cycle log
2. Runs exactly one hacker-core cycle (score -> diagnose -> mutate -> re-run -> log)
3. Returns a one-line summary to the main conversation

The main conversation is **not blocked** between cycles and **not polluted** with intermediate file reads.

### Agent prompt template

Copy and customize the `{{ }}` placeholders for your domain:

```
Run exactly ONE hacker-core cycle (score -> diagnose -> mutate -> re-run -> log).

## Paths (repo root: {{ repo_root }})
- Corpus: {{ corpus_path }}
- Predictions: {{ predictions_path }}
- Scorer: {{ scorer_command }}
- Cycle log: {{ log_path }}
- Candidate: {{ candidate_path }} -- {{ candidate_description }}

## Cycle (per hacker-core contract)
1. Run `{{ scorer_command }}` from {{ repo_root }}.
2. If FAIL: diagnose single worst failing case.
   If PASS: find biggest coverage/clarity gap in candidate vs corpus.
   If PASS + no gap: report "no mutation needed" and stop.
3. ONE mutation: {{ mutation_description }}.
4. Re-run `{{ scorer_command }}` -- must be green or rollback.
5. Append one row to cycle log at {{ log_path }}.
6. Report: one-line summary + corpus status.
```

### Setup (one-time per session)

```
/loop 10m /hacker {{ domain }}
```

This triggers:
1. **CronCreate** with `*/10 * * * *` (or operator-chosen interval)
2. Each fire -> **Agent tool** with the filled template above
3. Agent runs one cycle, returns summary
4. Loop continues until stop condition or `CronDelete`

### Why subagents

- **Context protection**: corpus analysis doesn't bloat the primary conversation window
- **Parallelism**: cron fires don't block ongoing conversation
- **Isolation**: matches hacker invariant of "isolated worker context" per cycle
- **Stateless**: each agent reads current disk state, no scratchpad needed

## Cursor — Ralph Loop

Already documented in `SKILL.md` section "Sustaining many cycles (Cursor + Ralph Loop)". Summary:

1. Invoke `/ralph-loop` to create `.cursor/ralph/scratchpad.md`
2. Put the hacker task in the scratchpad body
3. Ralph replays the same prompt each turn; agent runs one cycle, bumps `iteration`

Scratchpad serves as durable state between turns (Ralph needs it; Claude Code subagents don't).

## CI / Headless

A shell loop calls the agent CLI with a fixed prompt file:

```bash
while true; do
  agent run --prompt "read hacker-scratchpad.md, run one hacker-core cycle, exit."
  # check if scratchpad says COMPLETE
  grep -q "COMPLETE" hacker-scratchpad.md && break
  sleep 60
done
```

Same contract: one invocation = one cycle. Scratchpad is the state file.

## Comparison

| Runtime | Outer driver | State | Cycle skill |
| --- | --- | --- | --- |
| **Claude Code** | CronCreate + Agent tool | Stateless (reads disk) | hacker-core |
| **Cursor** | Ralph Loop | `.cursor/ralph/scratchpad.md` | hacker-core |
| **CI / headless** | Shell loop + agent CLI | File-based scratchpad | hacker-core |

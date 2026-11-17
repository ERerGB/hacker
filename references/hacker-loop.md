# Hacker Loop — sustained cycle drivers

This reference extends [hacker-core](hacker-core.md) with optional runtime drivers.
Follow the [main skill's stop conditions](../SKILL.md#when-to-stop) in every
runtime. A finite optimization task can run in the current task; no recurring job
or particular loop plugin is required.

## Contract (all runtimes)

One external iteration = exactly one hacker-core cycle. Before starting:

1. Set a finite cycle/resource budget, a no-improvement limit and an execution
   deadline for each invocation. Stop on the first exhausted limit or execution
   failure; retain the best verified candidate and report unmet goals.
2. Store the candidate revision, accepted baseline, scores, cycle history and
   remaining budget in task-owned durable state. Resume from that record. A fresh
   worker context does not make the optimization stateless.
3. Run one cycle, persist its decision and report whether the goal is complete,
   an improvement was accepted, or no improvement was accepted.
4. Use only driver capabilities exposed by the installed runtime. Do not infer
   that a platform-specific command or CLI shown here exists in another host.

## Claude Code — optional Agent and recurring facilities

If the installed runtime provides an Agent tool, it can run an isolated cycle.
The controller retains the durable state and aggregates the result. Follow the
current task's delegation scope and the installed tool contract.

Only use a recurring facility such as `CronCreate` or `/loop` when the user
explicitly requested recurring work and that interface exists in the runtime.
A request to optimize until a finite goal is complete does not imply scheduling.
For an authorized schedule, prevent overlapping cycles, enforce the same finite
budget/deadline and remove the schedule when its stop condition is reached.

### Agent prompt template

Fill the placeholders from the actual project and remaining task budget:

```
Run exactly ONE hacker-core cycle (score -> diagnose -> mutate -> re-run -> log).

## Paths (repo root: {{ repo_root }})
- Corpus: {{ corpus_path }}
- Predictions: {{ predictions_path }}
- Scorer: {{ scorer_command }}
- Cycle log and remaining budget: {{ state_path }}
- Candidate and accepted baseline: {{ candidate_path }}, {{ baseline_revision }}
- Invocation deadline: {{ deadline }}

## Cycle (per hacker-core contract)
1. Read durable state and stop without mutation if the budget is exhausted.
2. Run the full scorer. Diagnose the worst failure or largest coverage/clarity gap.
   If the corpus passes and no known gap remains, report complete and stop.
3. Apply ONE behavioral mutation motivated by that diagnosis.
4. Re-run the full corpus; accept only under configured gates, otherwise rollback.
5. Persist the candidate/baseline, scores, decision, cycle log and remaining budget.
   Bookkeeping is not an additional behavioral mutation.
6. Report complete, improved, or no-improvement with the verified evidence.
```

## Cursor — optional Ralph Loop

When Ralph Loop is installed and chosen as the driver, its scratchpad can carry
instructions and progress. Each invocation still runs one cycle and obeys the
shared budget. Read the runtime's current interface before creating or editing
its scratchpad. Keep candidate/baseline, scores and history in durable state;
other runtimes need that state too, even if their state file has another name.

## CI / headless

The example below calls a project-supplied `run-hacker-cycle.sh` adapter, not a
bundled or universal model CLI. The adapter accepts the task state directory as
its only argument, enforces the invocation deadline and remaining resource budget,
persists the verified cycle record, and writes exactly one status line to stdout:
`complete`, `improved`, or `no-improvement`. Diagnostics go to stderr. It exits
nonzero on execution or validation failure. `complete` must come from verified
acceptance checks, not a text marker found anywhere in a scratchpad.

```bash
#!/usr/bin/env bash
set -eu
hacker_state_dir="${HACKER_STATE_DIR:-./.hacker-state}"
hacker_cycle_runner="${HACKER_CYCLE_RUNNER:-./run-hacker-cycle.sh}"
hacker_max_cycles="${HACKER_MAX_CYCLES:-10}"
hacker_max_stale="${HACKER_MAX_STALE:-3}"
for hacker_limit in "$hacker_max_cycles" "$hacker_max_stale"; do
  if ! [[ "$hacker_limit" =~ ^[1-9][0-9]{0,5}$ ]]; then
    echo "Cycle and no-improvement limits must be integers from 1 to 999999" >&2
    exit 2
  fi
done
mkdir -p "$hacker_state_dir"
hacker_stale=0
for ((hacker_cycle=1; hacker_cycle<=hacker_max_cycles; hacker_cycle++)); do
  if ! "$hacker_cycle_runner" "$hacker_state_dir" > "$hacker_state_dir/last-status.txt"; then
    echo "Cycle execution failed; keep the last verified baseline" >&2
    exit 2
  fi
  hacker_status=$(cat "$hacker_state_dir/last-status.txt")
  case "$hacker_status" in
    complete) exit 0 ;;
    improved) hacker_stale=0 ;;
    no-improvement) hacker_stale=$((hacker_stale + 1)) ;;
    *) echo "Invalid cycle status" >&2; exit 2 ;;
  esac
  if ((hacker_stale >= hacker_max_stale)); then
    echo "No-improvement limit reached; goal remains unmet" >&2
    exit 3
  fi
done
echo "Cycle budget reached; goal remains unmet" >&2
exit 3
```

The adapter also checks persistent remaining budget on restart. Restarting this
wrapper does not authorize replenishing an exhausted task budget. Exit 0 means
verified completion; exit 2 means execution/contract failure; exit 3 means a
limit stopped work before completion. None implies permission to publish or merge.

## Comparison

| Runtime | Optional driver | Durable state | Cycle skill |
| --- | --- | --- | --- |
| Claude Code | Available Agent / explicitly requested recurring facility | Candidate, baseline, scores, history and budget | hacker-core |
| Cursor | Available Ralph Loop | Same state, optionally a Ralph scratchpad | hacker-core |
| CI / headless | Bounded shell wrapper + project adapter | Same task-owned state | hacker-core |

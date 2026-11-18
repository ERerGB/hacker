---
name: hacker
description: >
  Improve a prompt, agent configuration, or script-scored artifact through bounded
  single-change experiments and full-corpus comparisons. Use when the user wants
  evidence-based iteration against an existing or newly designed evaluation set.
license: MIT
metadata:
  author: ERerGB
  version: "0.2.2"
  tags: problem-driven, best-practices, evidence-driven, optimization, agent-evolution, ralph-loop
---

# Hacker

Run a bounded experiment: measure the baseline, diagnose one failure, change one
behavior, rerun the full agreed corpus, and accept or roll back against fixed gates.
The output is the best verified candidate and its evidence, not a claim of universal
optimality or a requirement to install an agent framework.

## Select the evaluation path

| Available evaluator | Path |
| --- | --- |
| Existing deterministic scorer/test suite for a SKILL, config or other artifact | Run it directly; no model workers or subagent-harness are needed. |
| Prompt or agent behavior requiring model-generated answers | Use isolated evaluation workers; read [worker dispatch](references/hacker-worker.md). |
| No usable evaluator or expected outcomes | Define a small task-relevant corpus and acceptance policy first; read [corpus design](references/corpus-format.md). |

A native prompt file need not become `.agent.md` merely to be evaluated. Use
subagent-harness only when that is the candidate’s actual representation.
If required worker isolation or a model is unavailable, report the limitation;
do not manufacture an independent run or silently switch to a paid provider.

## Establish the experiment

Resolve the candidate, scorer, corpus, accepted baseline, allowed edit surface and
user’s success criterion. Reuse existing project definitions. Set a finite cycle
and resource budget, a no-improvement limit and an invocation deadline; a request
for one cycle stays one cycle. Ask only for a missing choice that changes scope.

Fix hard checks, scoring dimensions and regression tolerance before evaluating a
change. With no configured policy, require an improvement in the diagnosed outcome
and no regression on previously passing cases. A project may explicitly permit
bounded soft-score tradeoffs; never relax a hard requirement to accept a candidate.
Small existing corpora can support bounded evidence: report coverage limits rather
than refusing to run until an arbitrary case count is reached.

## One cycle

Follow [the reusable core](references/hacker-core.md) when another workflow invokes
Hacker as a component. The same contract applies here:

1. **Score** the full agreed corpus and record per-case results, hard-check failures
   and useful aggregate/tail measures. Establish the baseline from actual outputs.
2. **Diagnose** one observable failure or task-relevant coverage gap. State a testable
   hypothesis. If the requested criteria already pass and no material gap is known,
   stop without inventing a mutation.
3. **Change one behavior** within the allowed surface. Existing failure evidence may
   suffice. Research only when it resolves a real uncertainty or the configured
   experiment requests it; record the source, relevance and risk of evidence used.
   Do not load arbitrary prompt advice into the candidate without a testable reason.
4. **Rerun the full corpus** from the saved candidate with the same scorer and gates.
   Keep evaluator/gold fixes separate from candidate improvements; if a mislabeled
   case or scorer bug must change, log it and re-establish a comparable baseline.
5. **Decide and log**: accept only under the fixed gates, otherwise restore the
   previous candidate and verify its full-corpus result. Record hypothesis, diff,
   before/after, decision and remaining limits even when the attempt fails.

Model evaluation workers receive the candidate and one case’s input, never gold,
other cases or prior answers. The controller scores their actual returned outputs.
This isolation rule does not turn a deterministic command into a model task.

## Optional policies and drivers

- [Harness configuration](references/config-schema.ts) describes the `.agent.md`
  profile, not a mandatory config file or an implemented universal runner.
- [Stages](references/stages.md), [mutation examples](references/mutations.md), and
  [extensions](references/extensions.md) are opt-in techniques, not completion gates
  imposed on every task. Pruning is justified by regression evidence, not a length quota.
- [Sustained drivers](references/hacker-loop.md) covers available native delegation,
  Cursor Ralph and a bounded CI adapter. A finite sequence can stay in this task.
  Recurring scheduling requires a separately requested recurring job.

## When to stop

Stop at the first reached goal, budget/deadline, no-improvement limit, execution
failure or missing required access. Preserve the best verified candidate and durable
cycle state so a resume does not reset the budget. Report accepted/rolled-back
changes, actual scores and untested or unmet criteria. Tests are evidence within
this corpus, not proof of production performance. Publishing or merging follows
current task authorization and repository rules; a score does not grant permission.

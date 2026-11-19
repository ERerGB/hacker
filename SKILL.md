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

Improve a candidate through bounded, single-change experiments against a fixed
full-corpus evaluator. Deliver the best verified candidate and actual evidence.

## Set the contract

Resolve candidate, scorer, corpus, allowed edits and success criteria. Reuse
existing project definitions; set finite cycle/resource/deadline and no-improvement
limits before running. A one-cycle request stays one cycle. Small corpora are
usable with stated coverage limits; arbitrary case counts are not entry gates.

Use an existing deterministic scorer directly. For model-generated outputs, read
[worker dispatch](references/hacker-worker.md): each isolated worker sees the
candidate and one input, never gold, other cases or prior answers; the controller
scores actual returned outputs. Do not pretend isolation occurred or silently
switch to a paid provider. `.agent.md`/subagent-harness is needed only when it is
the candidate's real representation. With no usable evaluation contract, read
[corpus design](references/corpus-format.md) before proposing changes.

Fix hard requirements and regression tolerance first. Unless explicitly configured
otherwise, accept only an improvement in the diagnosed outcome with no regression
on previously passing cases. A soft-score tradeoff never waives a hard requirement.

## Execute one cycle

1. Run the full corpus; preserve per-case outputs, failures and relevant aggregates.
2. Diagnose one observed failure or material coverage gap and state a testable
   hypothesis. If criteria pass and no material gap is known, stop without a mutation.
3. Change one behavior inside the allowed surface. Research only a real uncertainty.
   Keep scorer/gold corrections separate and rebaseline them; never count a changed
   measurement contract as candidate improvement.
4. Reload the saved candidate and rerun the full corpus with the fixed gates.
5. Accept under those gates, or restore and verify the prior full-corpus result.
   Log hypothesis, diff, before/after, decision and limits, including failed attempts.

[The core contract](references/hacker-core.md) supports composition.
[Configuration](references/config-schema.ts) is an optional `.agent.md` profile,
not a universal runner. [Stages](references/stages.md), [mutations](references/mutations.md),
[extensions](references/extensions.md) and [drivers](references/hacker-loop.md) are
conditional techniques; ordinary iteration need not load them.

Stop at the first reached goal, exhausted budget/deadline/no-improvement limit,
execution failure or missing required access. Preserve durable state and budget
on resume. Report unmet criteria and corpus limits. A score neither proves
production quality nor authorizes publication, merging or recurring scheduling.

# Model evaluation and optional harness dispatch

Read this only when the candidate’s behavior needs model-generated outputs.
Use the installed host’s supported isolated worker tool and the requested model.
Do not infer tool availability from this document or silently substitute a provider.
Run cases within available concurrency and the agreed resource budget.

## Inputs and evidence

Each worker gets only the candidate instructions, one case’s input and the project’s
output contract. It does not see gold labels, other cases, prior outputs or scores.
The controller collects and scores outputs; it must not generate the evaluated
answers itself and call them independent. No-output JSON is appropriate only when
the candidate’s actual task/schema defines that result.

A dispatch prompt can contain:

```text
Apply the candidate below to the single input. Return the task’s requested output.
Candidate: <candidate instructions or supported runtime artifact>
Input: <single case input>
Output contract: <project contract, if any>
```

Record the actual runtime, candidate revision, returned output and failures. Keep
missing output separate from a valid negative answer. If isolation fails, mark the
run invalid and correct the setup within budget; do not score invented results.

## When the candidate is `.agent.md`

Use the installed `subagent-harness` contract:

1. `parseRichAgentMarkdown(path, content)` parses the rich source.
2. Load any companion extension data through the consuming project’s existing
   mechanism and call `validateRichAgent(doc, options?)`; retain its extension validator.
3. `composeSubagent(doc, target, profile?)` produces the target artifact. Supported
   targets/profile behavior come from the installed package; inspect its current API.
4. Dispatch the composed instructions through that runtime’s actual invocation
   interface. A compiler artifact is not itself an executed worker.

A change can use `patchAgent(doc, { path, value })` for `body`, model fields or
consumer-defined `extensions.*`. Validate before saving. Use `serializeAgent()`
and, where the consumer uses sidecars, `serializeExtensions()` through its normal
write path; preserve extension data rather than dropping it on round-trip.
Reload the saved source and compose again before the full rerun, so evaluation
covers the artifact that will actually be delivered.

Keep the model fixed when testing a prompt-only change. Changing model or evaluation
policy is a separate behavioral experiment, with its own baseline and authorization.
Cycle bookkeeping must not alter runtime behavior or expose gold to workers.
The typed [configuration example](config-schema.ts) is policy data, not a loop driver.

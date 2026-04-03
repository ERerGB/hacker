# Hacker

> **Define a problem. Aggregate all best practices. Hack it.**

You spent two hours tuning a classifier prompt. It works perfectly on your three test cases. You deploy it. A user sends an all-caps complaint — the prompt classifies "URGENT BUG FIX" as positive feedback. You add a rule: "ignore all-caps text." Next morning, normal acronyms (API, HTTP, SQL) are being ignored too. Three old cases silently regressed. You didn't know, because you only tested the new one.

Every manual fix is a bet. You can't prove version B is better than version A. You don't know what broke until someone tells you.

**Hacker replaces that loop with a different one:**

1. **Define the problem** — build a test corpus with golden labels. Score your prompt against all of them. The worst-scoring case tells you exactly what's broken.

2. **Aggregate best practices** — search the web, skill hubs, and community patterns for evidence that addresses the diagnosed failure. Don't guess. Find someone who already solved a similar problem.

3. **Hack it** — apply one surgical change backed by that evidence. Re-run the full corpus. Accept only if overall score improves and nothing regresses. Otherwise rollback.

The agent does this autonomously. You tell it to start, go get coffee, and come back to a scratchpad that says: "8 cycles. Found a paper on case-insensitive matching. Borrowed a negative-example pattern from a public skill. Pruned one dead rule. Prompt is 20% shorter, 12% more accurate. Every change has an evidence trail."

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

---

## Quickstart

```bash
# Drop the skill into your project
cp -r hacker/ .cursor/skills/hacker/

# Or clone globally
git clone https://github.com/ERerGB/hacker.git ~/.cursor/skills/hacker

# Tell your agent to start:
"Run hacker against my support_bot.md using corpus.md"
```

The agent enters an autonomous loop — diagnosing, exploring, mutating, and validating — logging every decision.

---

## The Cycle (10 Steps)

| Step | Phase | What happens |
|------|-------|-------------|
| 1 | **Run** | Dispatch corpus to isolated workers |
| 2 | **Verify** | Confirm worker isolation |
| 3 | **Score** | Compare outputs to golden labels |
| 4 | **Diagnose** | Identify the single worst failure mode |
| 5 | **Explore** | Search external evidence (web, skill hubs, memory) |
| 6 | **Select** | Filter evidence by relevance, executability, verifiability |
| 7 | **Mutate** | Apply one evidence-backed change |
| 8 | **Re-run** | Full corpus re-dispatch |
| 9 | **Decide** | Accept if improved, rollback if regressed |
| 10 | **Log** | Record hypothesis, evidence, result, lesson |

See [SKILL.md](SKILL.md) for the full executable protocol.

---

## Configuration — Not Policy

Hacker's core is an abstract optimization loop. Concrete policies — scoring dimensions, stage gates, mutation operators, thresholds — are **project-level configuration**, not baked into the skill.

You configure:
- **Evaluation**: dimensions, weights, hard checks
- **Explore**: search providers, budget, evidence schema
- **Mutation**: available operators, evidence linking requirements
- **Acceptance**: gate thresholds, regression tolerance
- **Stages**: optional phased curriculum (e.g., recall → precision → quality → pruning)

See [references/config-schema.ts](references/config-schema.ts) for the TypeScript interface.

Default profiles are provided as **examples**:
- [references/stages.md](references/stages.md) — a 5-stage curriculum
- [references/mutations.md](references/mutations.md) — a 9-operator mutation menu

---

## Inspired By

| Source | What we adapted |
|--------|-----------------|
| [Promptbreeder](https://arxiv.org/abs/2309.16797) (DeepMind) | Evolutionary prompt mutation via LLM |
| [EvoSkill](https://arxiv.org/abs/2603.02766) | Failure-driven skill discovery, Pareto selection |
| [Opus Self-Evolving Agent](https://dev.to/stefan_nitu/32-more-generations-my-self-evolving-ai-agent-learned-to-delete-its-own-code-18bp) | Reflexion, pruning as evolution |
| [Genetic Prompt Programming](https://github.com/stack-research/genetic-prompt-programming) | Enumerated mutation operators |

*The difference: those are research frameworks. This is a skill file you drop into your project and start using in 5 minutes.*

## License

MIT

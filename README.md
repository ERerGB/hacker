# Hacker

> **Define a problem. Aggregate all best practices. Hack it.**

An agent skill that optimizes any LLM prompt by diagnosing failures, searching the world for evidence-backed fixes, and applying them one at a time — with full regression protection.

---

You spent two hours tuning a classifier prompt. It works on your three test cases. You deploy. A user sends an all-caps complaint — the prompt classifies "URGENT BUG FIX" as positive feedback. You add a rule: "ignore all-caps text." Next morning, normal acronyms (API, HTTP, SQL) are being ignored too. Three old cases silently regressed.

Every manual fix is a bet you can't verify.

Hacker turns it into a process you can trust. You say: "Run hacker against my classifier using corpus.md" — and walk away.

When you come back, the scratchpad reads:

```
Cycle 3  ACCEPT  avg 6.2 → 7.1
  diagnosis: T4 false positive — all-caps acronyms treated as noise
  explored:  arxiv.org/abs/2301.xxxxx — case-folding preserves acronyms
  mutation:  replaced "ignore caps" rule with Unicode category filter
  regressed: none

Cycle 5  ACCEPT  avg 7.1 → 7.8
  diagnosis: T2 missed implicit complaint ("this is ridiculous")
  explored:  lobehub.com/skill/sentiment-boundary — negative-example pattern
  mutation:  added 2 implicit-negative examples from public skill
  regressed: none

Cycle 8  ACCEPT  avg 7.8 → 8.0
  diagnosis: no single case below 6.0 — entering pruning
  mutation:  deleted rule #4 (no measurable effect across 3 epochs)
  result:    prompt 18% shorter, same scores
```

Eight cycles. No guesswork. Every change has a source URL, a hypothesis, and a before/after score. You didn't write a single rule — the agent searched the world for evidence and applied it one cut at a time.

Built for the [Magpie](https://github.com/nicobailey/magpie) agent pipeline. Used in production to evolve sub-agent prompts across 50+ iteration cycles.

```
  [Define]                    [Aggregate]              [Hack]
      ↓                            ↓                      ↓
 Corpus + Labels ──▶ Score ──▶ Diagnose ──▶ Explore ──▶ Mutate ──▶ Re-run
                                                                      ↓
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

---

## What's Next

- **Structured candidates** — `.agent.md` format via [subagent-harness](https://github.com/ERerGB/subagent-harness): parse, mutate, serialize round-trip
- **Explore providers** — SkillRank integration for evidence sourcing from skill hubs
- **Multi-objective Pareto** — maintain a frontier of non-dominated prompt versions instead of a single best

Star the repo to follow along. Issues and discussions welcome.

## License

MIT

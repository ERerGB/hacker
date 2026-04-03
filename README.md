# Hacker

> **Define a problem. Aggregate all best practices. Hack it.**

Drop this skill into Cursor. Your agent diagnoses prompt failures, searches the world for fixes, and applies them one at a time — with full regression protection. No guesswork.

---

A developer spends two hours tuning a support-ticket classifier prompt. It works on three test cases. They deploy. A customer sends an all-caps complaint — the prompt classifies "URGENT BUG FIX" as positive feedback. They add a rule: *"ignore all-caps text."* Next morning, normal acronyms (API, HTTP, SQL) are being ignored too. Three old cases silently regressed. They didn't know, because they only re-tested the new case.

This is what prompt engineering looks like without a regression gate. Every fix is a blind bet. You can't prove version B is better than version A — you can only hope nothing broke.

### What changes

The developer writes 8 test cases with expected outputs — including the all-caps edge case — and tells the agent:

> *"Run hacker against my classifier using corpus.md"*

They walk away. When they come back, the scratchpad reads:

```
Cycle 3  ACCEPT  avg 6.2 → 7.1
  diagnosis: T4 false positive — all-caps acronyms treated as noise
  explored:  arxiv.org/abs/2301.xxxxx — case-folding preserves acronyms
  mutation:  replaced "ignore caps" with Unicode category filter
  regressed: none

Cycle 5  ACCEPT  avg 7.1 → 7.8
  diagnosis: T2 missed implicit complaint ("this is ridiculous")
  explored:  lobehub.com/skill/sentiment-boundary — negative-example pattern
  mutation:  added implicit-negative examples from public skill
  regressed: none

Cycle 8  ACCEPT  avg 7.8 → 8.0
  diagnosis: no case below 6.0 — entering pruning
  mutation:  deleted rule with no measurable effect across 3 epochs
  result:    prompt 18% shorter, same scores
```

They didn't write a single new rule. The agent diagnosed each failure, searched for evidence-backed solutions — a paper, a public skill, a community pattern — and applied them one cut at a time. Every change has a source URL, a hypothesis, and a before/after score.

This README was itself written using Hacker's methodology — 7 cycles of scoring against [NDD](https://github.com/nicobailey/narrative-driven-development) narrative dimensions, with evidence-sourced mutations and accept/rollback gates. The [evolution log](.cursor/hacker-narrative-evolution.md) is in this repo.

Built for the [Magpie](https://github.com/nicobailey/magpie) agent pipeline, where it evolves sub-agent prompts in production.

```
  [Define]                    [Aggregate]              [Hack]
      ↓                            ↓                      ↓
 Corpus + Labels ──▶ Score ──▶ Diagnose ──▶ Explore ──▶ Mutate ──▶ Re-run
                                                                      ↓
                                                              accept / rollback
```

---

## Try It

```bash
# Drop the skill into your project
cp -r hacker/ .cursor/skills/hacker/

# Or clone globally
git clone https://github.com/ERerGB/hacker.git ~/.cursor/skills/hacker
```

Then tell your agent:

> *"Run hacker against my support_bot.md using corpus.md"*

It enters an optimization loop — diagnose, explore, mutate, verify — and logs every decision to a scratchpad you can audit after.

**Continuous runs**: Hacker does not bundle a loop driver. Pair it with your environment's re-invocation mechanism (e.g. Cursor Ralph Loop on `.cursor/ralph/scratchpad.md`, Claude Code's loop, or a shell wrapper) so each automated turn executes **one** full Hacker cycle. See [SKILL.md — Integration with Iterative Loop Runners](SKILL.md#integration-with-iterative-loop-runners).

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

Hacker is actively evolving (using its own methodology, naturally):

- **Structured candidates** — `.agent.md` format via [subagent-harness](https://github.com/ERerGB/subagent-harness) for parse → mutate → serialize round-trips
- **Evidence sourcing** — SkillRank integration to search skill hubs during the Explore phase
- **Pareto frontier** — maintain multiple non-dominated prompt versions instead of a single best

**Try it on your own prompt and [share your scratchpad log](https://github.com/ERerGB/hacker/issues).** The best way to understand Hacker is to watch it think — and the best way to improve it is more real-world evolution logs.

## License

MIT

# Hacker

> **Breed better prompts with evidence, not intuition.**

Hacker is an agent skill that applies evidence-driven evolutionary optimization to LLM prompts and agent configurations. Instead of tweaking prompts by gut feel, it runs them against a test corpus, scores outputs, diagnoses failures, explores external evidence, and applies targeted single-variable mutations — with full regression protection.

---

## The Problem

Manual prompt engineering is blind iteration. You fix one edge case and silently break three older ones. You can't prove version B is better than version A. Every "improvement" is a guess.

## The Solution

A deterministic, evidence-driven loop:

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

**What this fixes:**
1. **No guessing** — the controller identifies which case failed and why.
2. **Evidence-backed mutations** — external search (papers, skill hubs, community patterns) informs every change.
3. **Regression proof** — the mutated candidate must pass the full corpus. If it breaks old cases, it's rolled back.

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

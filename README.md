# Hacker

> **Breed better prompts instead of guessing.**

Hacker is an agent skill that applies evolutionary optimization to LLM prompts. Instead of tweaking prompts by intuition, it runs them against a test corpus, scores the outputs, diagnoses failures, and applies targeted mutations — the same loop that makes neural networks learn, adapted for prompt engineering.

---

## The Problem — Prompt Regression Hell

Alice writes a great prompt for a support ticket classifier. It works perfectly. 
The next day, a weird edge case appears (a user complaining in all caps). Alice uses her intuition to add a new constraint to the prompt: *"Ignore text in ALL CAPS"*. 
The edge case is fixed. But silently, her new constraint just broke 3 older, perfectly normal tickets where users legitimately used acronyms.

> **Root Cause:** Manual prompt engineering is blind. Iteration relies on intuition and isolated testing, leading to endless regressions. You can't scientifically prove version B is better than version A.

---

## The Solution — Data-Driven Evolution

Hacker replaces intuition with a deterministic, data-driven pipeline:

```
Test Corpus                 Prompt (evolving)               Golden Labels
    │                               │                             │
    ▼                               ▼                             ▼
 [Dispatch] ──▶ N isolated worker outputs ──▶ [Score] ──▶ [Diagnose]
    ▲                                                             │
    │                                                             ▼
 [Re-run] ◀──────────────── [Apply 1 Mutation] ◀──────────────────┘
```

**How it fixes Alice's problem:**
1. **No guessing:** The controller identifies exactly *which* case failed and *why*.
2. **Targeted mutation:** It selects a specific operator (e.g., `M1: Add constraint`) to fix the failure.
3. **Regression proof:** The mutated prompt must pass the entire corpus again. If the new fix breaks old cases, the mutation is immediately rolled back.

---

## 5-Minute Quickstart

Stop guessing. Let your Agent breed the prompt for you.

```bash
# 1. Drop the skill into your project
cp -r hacker/ .cursor/skills/hacker/
# Or clone globally: git clone https://github.com/ERerGB/hacker.git ~/.cursor/skills/hacker

# 2. Open Cursor Chat / Claude Code and tell the Agent to start:
"Run the hacker prompt evolution against my support_bot.md using the test cases in corpus.md"
```

### What you will see (Real Showcase)

The agent will start an autonomous loop, logging its exact decisions. You'll see it thinking like this:

```log
[Epoch 3 Complete]
Score: 7.2/10 (↑ 0.4)
Status: ACCEPTED

[Diagnosis]
Case #4 (False Positive) failed. The prompt triggered on "React rendering" when it should only trigger on "Database errors".
[Mutation Applied] 
M1 (Add Constraint): Added instruction -> "CRITICAL: Only flag backend infrastructure errors. Ignore all frontend framework issues."
```

---

## The Hacker Protocol (Under the Hood)

If you are building your own tools around Hacker, you must strictly follow these invariants. Violation of any rule invalidates the epoch.

| Phase | Action | Strict Rule / Invariant |
|-------|--------|-------------------------|
| **1. Dispatch** | Run test cases against the prompt. | Each case MUST run in a fully isolated worker context. No cross-contamination. |
| **2. Verify** | Check worker purity. | Workers cannot see golden labels, other test cases, or prior worker context. |
| **3. Score** | Compare output to golden labels. | The controller never generates outputs, it ONLY scores worker outputs. |
| **4. Diagnose**| Identify the worst performing case. | Focus entirely on the single lowest-scoring case. |
| **5. Mutate** | Apply a fix from the Mutation Menu. | **Only ONE mutation** is allowed per iteration. |
| **6. Re-run** | Run the entire corpus again. | Accept only if overall score improves AND no single case drops > 1.5 points. |

---

## Reference: 5 Stages & 9 Mutations

### The 5 Stages (Gates)
Hacker evolves prompts through specific maturity stages. It only advances when scores are stable (2 consecutive epochs within ±0.5).

| Stage | Focus | Gate |
|-------|-------|------|
| **1. Can It See?** | Recall — does it find what it should? | Recall ≥ 7.0 |
| **2. Does It Filter?** | Precision — does it avoid false positives? | Precision ≥ 7.0 |
| **3. Is It Good?** | Quality — is the output actually useful? | Quality ≥ 7.5 |
| **4. Edge Cases** | Robustness — does it handle weird inputs? | No score < 5.0 |
| **5. Pruning** | Minimality — what instructions can we delete? | ≤80% length, same scores |

*(See `references/stages.md` for full gate details.)*

### The 9 Mutation Operators
Instead of randomly rewriting the whole file, Hacker acts like a surgeon, picking from a targeted menu:

| ID | Operator | When it's used |
|----|----------|----------------|
| **M1** | Add constraint | False positives occurring |
| **M2** | Remove constraint | Missed recall (over-filtered) |
| **M3** | Add positive example | Unrecognized pattern |
| **M4** | Add negative example | Wrong triggers |
| **M5** | Rephrase | Ambiguity in instructions |
| **M6** | Reorder | Important rule is being ignored/buried |
| **M7** | Split | One rule doing two conflicting things |
| **M8** | Merge | Two rules saying the same thing |
| **M9** | Delete | Instruction has no measurable effect (Stage 5 only) |

*(See `references/mutations.md` for usage rules and constraints.)*

---

## Inspired By

| Source | What we adapted |
|--------|-----------------|
| [Promptbreeder](https://arxiv.org/abs/2309.16797) (DeepMind) | Evolutionary prompt mutation via LLM |
| [EvoSkill](https://arxiv.org/abs/2603.02766) | Failure-driven skill discovery, Pareto selection |
| [Opus Self-Evolving Agent](https://dev.to/stefan_nitu/32-more-generations-my-self-evolving-ai-agent-learned-to-delete-its-own-code-18bp) | Reflexion, pruning as evolution, structural > disciplinary |
| [Genetic Prompt Programming](https://github.com/stack-research/genetic-prompt-programming) | Enumerated mutation operators |

*The difference: Those are complex frameworks and research papers. This is a simple Skill file you drop into your project and start using in 5 minutes.*

## License

MIT

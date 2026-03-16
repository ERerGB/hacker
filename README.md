# Hacker

**Breed better prompts instead of guessing.**

Hacker is an agent skill that applies evolutionary optimization to LLM prompts. Instead of tweaking prompts by intuition, it runs them against a test corpus, scores the outputs, diagnoses failures, and applies targeted mutations — the same loop that makes neural networks learn, adapted for prompt engineering.

## The Problem

Manual prompt engineering is:
- **Anecdotal** — you test on 2-3 examples, ship it, and pray
- **Regressive** — fixing one edge case often breaks another
- **Unaccountable** — you can't prove version B is better than version A

## The Solution

```
Test Corpus (fixed)          Prompt (evolving)           Golden Labels (fixed)
      ↓                             ↓                           ↓
[dispatch N isolated workers] → N raw worker outputs → [controller scoring]
                                                             ↓
                                                    [failure diagnosis]
                                                             ↓
                                                   [one targeted mutation]
                                                             ↓
                                                      [re-dispatch epoch]
                                                             ↓
                                                   accept / rollback
```

Each iteration: **run → score → diagnose → mutate → re-run → accept or rollback.**

No guessing. Every change is traced to a specific failure on a specific test case.

## Protocol-First Quick Start

### 0. Invariant (Read First)

Violation of any invariant invalidates the epoch.

- Each test case runs in an isolated worker context.
- Controller never generates model outputs; it only scores worker outputs.
- Workers cannot see golden labels, other test cases, or prior worker context.
- One mutation per iteration.

### 1. Dispatch (Run Isolated Workers)

For each test case, dispatch one isolated worker with:

- Prompt under test (verbatim)
- One test input only
- Fixed output schema

### 2. Verify (Isolation Checklist)

Before scoring/diagnosis, confirm:

- All cases used fresh workers
- Workers did not receive golden labels
- Workers did not receive other case inputs
- Controller only scored outputs

If any check fails, the epoch is invalid.

### 3. Score -> Diagnose -> Mutate -> Re-run

1. Score worker outputs against golden labels.
2. Diagnose the worst case.
3. Apply one targeted mutation.
4. Re-run full epoch.
5. Accept only if overall score improves and no single case drops > 1.5.

### 4. Define Corpus and Scoring

- Use 6-8 diverse test cases.
- Include at least 2 negative cases.
- Score on 2-4 weighted dimensions.
- Use `references/corpus-format.md` for structure and output schema.

## How It Works (Reference Layer)

### 5 Stages (Gates)

| Stage | Focus | Gate |
|-------|-------|------|
| 1. Can It See? | Recall — does it find what it should? | Recall ≥ 7.0 |
| 2. Does It Filter? | Precision — does it avoid false positives? | Precision ≥ 7.0 |
| 3. Is It Good? | Quality — is the output actually useful? | Quality ≥ 7.5 |
| 4. Edge Cases | Robustness — does it handle weird inputs? | No score < 5.0 |
| 5. Pruning | Minimality — what instructions can we delete? | ≤80% length, same scores |

Advance only when scores are stable (2 consecutive epochs within ±0.5).

See `references/stages.md` for full gate details.

### 9 Mutation Operators (Menu)

Instead of randomly rewriting, pick from a targeted menu:

| ID | Mutation | When |
|----|----------|------|
| M1 | Add constraint | False positives |
| M2 | Remove constraint | Missed recall |
| M3 | Add positive example | Unrecognized pattern |
| M4 | Add negative example | Wrong triggers |
| M5 | Rephrase | Ambiguity |
| M6 | Reorder | Important rule buried |
| M7 | Split | One rule doing two things |
| M8 | Merge | Two rules saying the same thing |
| M9 | Delete | No measurable effect (Stage 5 only) |

See `references/mutations.md` for usage rules and constraints.

### Built-in Overfitting Prevention

- Test against ALL corpus entries every epoch, not just the one you're fixing
- Require no single test case drops >1.5 points after mutation
- Include "negative" test cases where the correct output is "do nothing"
- Stage 5 specifically removes instructions that don't earn their keep

## Install

### Cursor

```bash
# Copy to project skills
cp -r hacker/ .cursor/skills/hacker/

# Or clone globally
git clone https://github.com/ERerGB/hacker.git ~/.cursor/skills/hacker
```

### Claude Code

```bash
git clone https://github.com/ERerGB/hacker.git .claude/skills/hacker
```

### OpenClaw / ClawHub

```bash
openclaw skill install ERerGB/hacker
```

### LobeHub

```bash
npx -y @lobehub/market-cli skills install erergb-hacker
```

## What's Inside

```
hacker/
├── SKILL.md                    # Core workflow (< 200 lines)
├── claw.json                   # ClawHub manifest
├── references/
│   ├── corpus-format.md        # How to structure test cases
│   ├── stages.md               # Stage goals and gates
│   ├── mutations.md            # Mutation operator reference
│   └── extensions.md           # 5 optional advanced features
├── examples/
│   └── classifier.md           # Worked example: sentiment classifier
├── LICENSE                     # MIT
└── README.md
```

## Inspired By

| Source | What we took |
|--------|-------------|
| [Promptbreeder](https://arxiv.org/abs/2309.16797) (DeepMind) | Evolutionary prompt mutation via LLM |
| [EvoSkill](https://arxiv.org/abs/2603.02766) | Failure-driven skill discovery, Pareto selection |
| [Opus Self-Evolving Agent](https://dev.to/stefan_nitu/32-more-generations-my-self-evolving-ai-agent-learned-to-delete-its-own-code-18bp) | Reflexion, pruning as evolution, structural > disciplinary |
| [Genetic Prompt Programming](https://github.com/stack-research/genetic-prompt-programming) | Enumerated mutation operators |

The difference: those are frameworks and research papers. This is a skill file you drop into your project and start using in 5 minutes.

## Extensions

Five optional extension points activate when the base loop isn't enough:

| Signal | Extension |
|--------|-----------|
| Stuck on same mutation 3+ times | Co-evolving mutation strategies |
| Prompt > 15 instructions | Instruction effectiveness tracking |
| Scores oscillate between versions | Pareto frontier selection |
| Catastrophic regression (>2.0 drop) | Canary testing |
| Average hides bad dimensions | Multi-dimensional gating |

See [references/extensions.md](references/extensions.md) for details.

**Default: run without extensions.** Add complexity only when earned.

## License

MIT

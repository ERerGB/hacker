# Show HN: Hacker – Breed better LLM prompts instead of guessing

---

**Title**: Show HN: Hacker – Evolutionary prompt optimization as an agent skill

**URL**: https://github.com/ERerGB/hacker

**Text**:

I got tired of the "tweak → test on 2 examples → ship → pray" cycle of prompt engineering, so I packaged an evolutionary approach into a single agent skill file.

**The idea**: treat prompt optimization like training a model. You need a test corpus (6-8 diverse inputs with expected outputs), a scoring rubric (2-4 dimensions), and a training loop (run all tests → diagnose worst failure → apply one targeted mutation → re-run → accept or rollback).

**What makes it different from just "iterate on your prompt":**

- You test against ALL corpus entries every iteration, not just the one you're fixing (prevents regression)
- 9 enumerated mutation operators (add constraint, add example, rephrase, reorder, split, merge, delete...) so you're not randomly rewriting
- 5 stages with gates: Recall → Precision → Quality → Edge Cases → Pruning. You only advance when scores are stable across 2 consecutive epochs
- Negative test cases (correct output = "do nothing") prevent false-positive overfitting
- Stage 5 specifically deletes instructions that don't measurably affect scores — prompts almost always get shorter AND better

**Inspired by**: Promptbreeder (DeepMind's evolutionary prompt mutation), EvoSkill (failure-driven skill discovery with Pareto selection), and that blog post about the self-evolving Opus agent that went from 39 tools to 32 by measuring which ones actually got used.

**What it is**: A SKILL.md file (~200 lines) you drop into `.cursor/skills/` or `.claude/skills/`. Works with Cursor, Claude Code, Codex, OpenClaw. No dependencies, no framework, no API keys. The agent reads the instructions and follows the protocol.

**What it isn't**: Not automated prompt tuning (like DSPy or OPRO). The agent does the reasoning. The skill provides the discipline — what to measure, when to mutate, when to stop.

I built this because I was optimizing prompts for a content extraction pipeline and realized I was making the same mistakes every time: fixing one test case while breaking another, adding instructions that didn't measurably help, and never knowing when to stop. This is the process I wish I'd had from the start.

Feedback welcome — especially from anyone who's tried systematic prompt optimization at scale.

---

## Posting Notes

- Post on weekday morning US time (Tue-Thu, 9-11am ET) for best visibility
- Keep title ≤ 80 characters
- "Show HN" requires the URL to be the repo, not a blog post
- Don't include the text body if the URL is self-explanatory (HN shows URL OR text, not both) — but since the README tells the story, just submit the URL

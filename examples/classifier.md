# Example: Evolving a Sentiment Classifier Prompt

A walkthrough of using Hacker to optimize a sentiment classification prompt.

## The Problem

You have a prompt that classifies customer feedback as positive/negative/neutral.
It works on obvious cases but fails on sarcasm, mixed sentiment, and very short inputs.

## Corpus (6 test cases)

```
T1: Clear positive — "Love this product, best purchase this year!"
T2: Clear negative — "Terrible experience, want a refund immediately"
T3: Sarcasm — "Oh great, another update that breaks everything"
T4: Mixed — "The UI is beautiful but it crashes every 10 minutes"
T5: Neutral/informational — "The package arrived on Tuesday"
T6: Very short — "meh"
```

## Stage 1 Evolution (3 iterations)

**v1 (seed)**: "Classify the sentiment of the following text as positive, negative, or neutral."

- Epoch 1: [T1:9, T2:9, T3:3, T4:4, T5:7, T6:5] avg=6.17
- Failure: T3 — classified sarcasm as positive (took words literally)
- Mutation: M3 — added: "Watch for sarcasm — words may express the opposite of their literal meaning"

**v2**: Added sarcasm instruction.
- Epoch 2: [T1:9, T2:9, T3:7, T4:5, T5:7, T6:5] avg=7.00
- Failure: T4 — classified as positive (focused on "beautiful", ignored "crashes")
- Mutation: M1 — added: "If both positive and negative elements exist, classify as mixed"

**v3**: Added mixed sentiment handling.
- Epoch 3: [T1:9, T2:9, T3:7, T4:8, T5:7, T6:6] avg=7.67 ✓ STABLE
- → Advance to Stage 2

## Result

After 9 total iterations across 3 stages, the prompt improved from avg 6.17 to 8.5,
with the weakest test case going from 3 to 7. The final prompt was 8 sentences —
each traceable to a specific failure it was designed to fix.

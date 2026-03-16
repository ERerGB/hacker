# Test Corpus Format

## Directory Structure

```
corpus/
├── T1-basic-positive.md
├── T2-edge-case.md
├── T3-negative-zero.md
├── T4-adversarial.md
├── T5-ambiguous.md
├── T6-high-density.md
├── T7-needle-in-haystack.md
└── T8-contradiction.md
```

## Test Case Format

Each file follows this structure:

```markdown
# T{N}: {Short Description}

## Metadata
- type: {positive | negative | edge-case | adversarial}
- complexity: {low | medium | high}
- expected_outputs: {number of expected outputs, 0 for negative cases}

## Input
[The actual input your prompt will receive]

## Golden Labels
[Expected outputs with enough detail to score against]

### Label 1
- segment: [which part of input triggers this output]
- expected_type: [classification, extraction, action, etc.]
- expected_content: [what the output should contain]
- quality_notes: [what makes a good vs mediocre output here]
```

## Corpus Design Rules

1. **Minimum 6 test cases** — fewer gives unreliable scores
2. **At least 2 negative cases** (expected_outputs: 0) — prevents false-positive overfitting
3. **At least 1 adversarial case** — input that looks like it should trigger but shouldn't
4. **At least 1 high-density case** — input with many valid outputs
5. **At least 1 needle-in-haystack** — long input with one subtle valid output
6. **Diversity over volume** — 8 varied cases beat 20 similar ones

## Scoring a Single Output

Compare each output against golden labels:

| Match Level | Score |
|-------------|-------|
| Exact match (right segment, right content) | 10 |
| Partial (right segment, weak content) | 7 |
| Partial (right content, wrong segment) | 5 |
| Hallucinated (no matching golden label) | 0, plus -3 precision penalty |
| Missed (golden label with no output) | 0, plus -5 recall penalty |

Quality score (0-10) is judged per output: is it actually useful?

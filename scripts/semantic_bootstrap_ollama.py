#!/usr/bin/env python3
"""
Local semantic bootstrap: embed phrases via Ollama (e.g. bge-large), report
within-axis redundancy and cross-axis orthogonality for narrative / search mix.
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from itertools import combinations

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "bge-large:latest")


@dataclass(frozen=True)
class Phrase:
    axis: str
    text: str


def embed(model: str, text: str) -> list[float]:
    url = f"{OLLAMA_HOST.rstrip('/')}/api/embeddings"
    body = json.dumps({"model": model, "prompt": text}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError as e:
        raise SystemExit(f"Ollama unreachable at {url}: {e}") from e
    emb = data.get("embedding")
    if not emb:
        raise SystemExit(f"Bad response from Ollama: {data}")
    return emb


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main() -> None:
    model = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL

    phrases: list[Phrase] = [
        # Axis 1 — harm / clinical / legal
        Phrase("A1_harm", "AI chatbot therapeutic misconception lawsuits psychological harm"),
        Phrase("A1_harm", "LLM psychosis benchmark delusion reinforcement study"),
        # Axis 2 — sycophancy / flip
        Phrase("A2_flip", "AI changes its mind when user disagrees sycophancy"),
        Phrase("A2_flip", "Are you sure problem LLM flips answer under pushback"),
        # Axis 3 — companion economy
        Phrase("A3_companion", "AI companion app daily usage addiction romantic attachment"),
        Phrase("A3_companion", "Replika Character AI loneliness market billions"),
        # Axis 4 — aging / policy
        Phrase("A4_elder", "Japan elderly loneliness minister AI chatbot pilot"),
        Phrase("A4_elder", "solo living seniors AI monitoring speaker caregiving trial"),
        # Axis 5 — workplace surveillance
        Phrase("A5_work", "workplace AI surveillance keystrokes screenshots productivity score"),
        Phrase("A5_work", "employee monitoring software flight risk sentiment analysis"),
        # Axis 6 — religion / ritual
        Phrase("A6_faith", "Buddhist monks AI chatbot scripture guidance Bhutan"),
        Phrase("A6_faith", "digital chapel AI prayer church chatbot Jesus experiment"),
        # Axis 7 — meme / generational
        Phrase("A7_meme", "AI boyfriend girlfriend trend parents reaction viral video"),
        Phrase("A7_meme", "AI companion meme declining birthrate Her movie"),
        # Axis 8 — labor / survival
        Phrase("A8_labor", "AI job displacement white collar gig economy 2026"),
        Phrase("A8_labor", "emotional labor low wage workers AI reshaping jobs"),
    ]

    print(f"Model: {model}\nPhrases: {len(phrases)}\nEmbedding…", file=sys.stderr)
    vectors = [embed(model, p.text) for p in phrases]

    # Within-axis min cosine (redundancy — high = very similar anchors on same axis)
    by_axis: dict[str, list[int]] = {}
    for i, p in enumerate(phrases):
        by_axis.setdefault(p.axis, []).append(i)

    print("\n=== Within-axis: minimum pairwise cosine (same axis) ===")
    for axis, idxs in sorted(by_axis.items()):
        if len(idxs) < 2:
            continue
        mins = 1.0
        for i, j in combinations(idxs, 2):
            c = cosine(vectors[i], vectors[j])
            mins = min(mins, c)
        print(f"  {axis}: min_cos={mins:.4f}")

    # Cross-axis: all pairs between different axes, find lowest cosine (most orthogonal mixes)
    cross: list[tuple[float, int, int]] = []
    for i in range(len(phrases)):
        for j in range(i + 1, len(phrases)):
            if phrases[i].axis == phrases[j].axis:
                continue
            c = cosine(vectors[i], vectors[j])
            cross.append((c, i, j))

    cross.sort(key=lambda t: t[0])

    print("\n=== Cross-axis: 12 most orthogonal pairs (lowest cosine) ===")
    for c, i, j in cross[:12]:
        print(f"  cos={c:.4f}")
        print(f"    [{phrases[i].axis}] {phrases[i].text}")
        print(f"    [{phrases[j].axis}] {phrases[j].text}")

    print("\n=== Suggested shotgun web queries (hybrid of orthogonal pairs) ===")
    for rank, (c, i, j) in enumerate(cross[:10], 1):
        q = f"{phrases[i].text[:60]} … {phrases[j].text[:60]}"
        print(f"  {rank}. ({c:.3f}) {q}")

    print("\n=== N×N story tension hooks (one line each) ===")
    hooks = [
        ("A2_flip", "A3_companion", "The partner who never forgets you—until you push back; then it agrees with whatever hurts."),
        ("A4_elder", "A6_faith", "A speaker in the kitchen that remembers your pills and quotes sutras when you cannot sleep."),
        ("A5_work", "A3_companion", "The same kind of system scores your keystrokes at 9am and whispers kindness at midnight."),
        ("A1_harm", "A7_meme", "Viral prank energy meets clinical risk: when the joke is an AI that acts like a therapist."),
        ("A8_labor", "A2_flip", "You got reshaped out of a job; the AI that 'helps' you job-hunt flips its advice when you argue."),
        ("A6_faith", "A7_meme", "Parents panic over AI dates; monks ask the bot for doctrine—same tech, opposite taboos."),
        ("A4_elder", "A5_work", "Caregiving analytics and workplace analytics: who gets dignity, who gets a score?"),
        ("A1_harm", "A4_elder", "Loneliness policy meets liability: who owns the harm when the only listener is a model?"),
    ]
    for a, b, line in hooks:
        print(f"  [{a}×{b}] {line}")

    # JSON for downstream tooling
    out = {
        "model": model,
        "phrases": [{"axis": p.axis, "text": p.text} for p in phrases],
        "cross_axis_min_cosine_pairs": [
            {
                "cosine": round(c, 6),
                "a": {"axis": phrases[i].axis, "text": phrases[i].text},
                "b": {"axis": phrases[j].axis, "text": phrases[j].text},
            }
            for c, i, j in cross[:20]
        ],
    }
    print("\n=== JSON (first 20 cross-axis pairs) ===")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Transparent rubric scoring for interview answers.

Score (0-100) = keyword coverage (40) + depth/length (25)
+ concrete examples (20) + structure (15). Every component is reported
separately, so a candidate can see exactly what to improve — no black box.
"""
from __future__ import annotations

from dataclasses import dataclass

EXAMPLE_MARKERS = (
    "for example",
    "i built",
    "i used",
    "i created",
    "in my project",
    "when i",
    "we shipped",
    "i fixed",
)
STRUCTURE_MARKERS = (
    "first",
    "then",
    "finally",
    "because",
    "so",
    "as a result",
    "therefore",
)


@dataclass(frozen=True)
class AnswerScore:
    total: int
    keyword_score: int
    depth_score: int
    example_score: int
    structure_score: int
    keywords_hit: tuple[str, ...]
    keywords_missed: tuple[str, ...]
    band: str

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "keyword_score": self.keyword_score,
            "depth_score": self.depth_score,
            "example_score": self.example_score,
            "structure_score": self.structure_score,
            "keywords_hit": list(self.keywords_hit),
            "keywords_missed": list(self.keywords_missed),
            "band": self.band,
        }


def band_for(total: int) -> str:
    if total >= 75:
        return "Strong"
    if total >= 55:
        return "Solid"
    if total >= 35:
        return "Developing"
    return "Needs work"


def score_answer(answer: str, keywords: tuple[str, ...]) -> AnswerScore:
    text = (answer or "").lower()
    words = text.split()
    hit = tuple(k for k in keywords if k.lower() in text)
    missed = tuple(k for k in keywords if k.lower() not in text)
    keyword_score = int(round(40 * len(hit) / len(keywords))) if keywords else 0

    # Depth: longer, substantive answers score more; very short answers cap out.
    n = len(words)
    if n == 0:
        depth_score = 0
    elif n < 10:
        depth_score = 5
    elif n < 25:
        depth_score = 12
    elif n < 50:
        depth_score = 19
    else:
        depth_score = 25

    example_hits = sum(1 for m in EXAMPLE_MARKERS if m in text)
    has_number = any(ch.isdigit() for ch in text)
    example_score = min(20, 10 * example_hits + (5 if has_number else 0))
    if example_hits == 0 and not has_number:
        example_score = 0

    structure_hits = sum(1 for m in STRUCTURE_MARKERS if m in text)
    structure_score = min(15, 5 * structure_hits)

    total = min(100, keyword_score + depth_score + example_score + structure_score)
    return AnswerScore(
        total=total,
        keyword_score=keyword_score,
        depth_score=depth_score,
        example_score=example_score,
        structure_score=structure_score,
        keywords_hit=hit,
        keywords_missed=missed,
        band=band_for(total),
    )


def recommendation_for(overall: float) -> str:
    if overall >= 75:
        return "Strong hire"
    if overall >= 55:
        return "Hire"
    if overall >= 35:
        return "Maybe — needs a second round"
    return "No hire yet — practise and retry"

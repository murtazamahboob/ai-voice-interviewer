"""The interview state machine: ask, listen, score, follow up, report.

One core question at a time. After each answer the interviewer scores it
and adapts: strong answers (>=70) get a stretch follow-up, weak answers
(<40) get a scaffolded follow-up with a hint, everything else gets the
standard follow-up. The follow-up answer can add up to 10 bonus points to
that question's score, capped at 100. The final report gives an overall
score, a hire recommendation, and the exact keywords each answer missed.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .audio import ToneCodec, write_wav
from .questions import Question, Role, get_role
from .scoring import AnswerScore, recommendation_for, score_answer


@dataclass
class Turn:
    question_id: str
    question: str
    answer: str
    followup: str
    followup_answer: str
    score: AnswerScore
    followup_score: AnswerScore | None = None
    question_total: int = 0


@dataclass
class InterviewResult:
    role: str
    role_title: str
    turns: list[Turn] = field(default_factory=list)
    overall: float = 0.0
    recommendation: str = ""
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    duration_s: float = 0.0

    def as_dict(self) -> dict:
        return {
            "role": self.role,
            "role_title": self.role_title,
            "overall": self.overall,
            "recommendation": self.recommendation,
            "strengths": self.strengths,
            "gaps": self.gaps,
            "duration_s": round(self.duration_s, 2),
            "turns": [
                {
                    "question_id": t.question_id,
                    "question": t.question,
                    "answer": t.answer,
                    "followup": t.followup,
                    "followup_answer": t.followup_answer,
                    "score": t.score.as_dict(),
                    "followup_score": t.followup_score.as_dict() if t.followup_score else None,
                    "question_total": t.question_total,
                }
                for t in self.turns
            ],
        }


def pick_followup(question: Question, score: AnswerScore) -> str:
    """Adapt the follow-up to how strong the answer was."""
    if score.total >= 70:
        return question.stretch_followup
    if score.total < 40:
        return question.scaffold_followup
    return question.standard_followup


def run_interview(role_id: str, answers: dict[str, str], followup_answers: dict[str, str] | None = None) -> InterviewResult:
    """Run a full interview. ``answers`` maps question id -> spoken answer text.

    Answers travel through the tone codec (encode then decode) so the
    listen step is exercised exactly as in a live voice turn.
    """
    role: Role = get_role(role_id)
    followup_answers = followup_answers or {}
    codec = ToneCodec()
    started = time.monotonic()
    turns: list[Turn] = []
    for question in role.questions:
        raw = answers.get(question.id, "")
        heard = codec.decode_audio(codec.encode_text(raw))
        score = score_answer(heard, question.keywords)
        followup = pick_followup(question, score)
        raw_fu = followup_answers.get(question.id, "")
        heard_fu = codec.decode_audio(codec.encode_text(raw_fu)) if raw_fu else ""
        fu_score = score_answer(heard_fu, question.keywords) if heard_fu else None
        bonus = 0
        if fu_score is not None:
            # A good follow-up can rescue a weak first answer: up to +10.
            bonus = min(10, fu_score.total // 10)
        total = min(100, score.total + bonus)
        turns.append(
            Turn(
                question_id=question.id,
                question=question.text,
                answer=heard,
                followup=followup,
                followup_answer=heard_fu,
                score=score,
                followup_score=fu_score,
                question_total=total,
            )
        )
    overall = round(sum(t.question_total for t in turns) / len(turns), 1) if turns else 0.0
    strengths = sorted({k for t in turns for k in t.score.keywords_hit})
    gaps = sorted({k for t in turns for k in t.score.keywords_missed})
    return InterviewResult(
        role=role.id,
        role_title=role.title,
        turns=turns,
        overall=overall,
        recommendation=recommendation_for(overall),
        strengths=strengths,
        gaps=gaps,
        duration_s=time.monotonic() - started,
    )


def write_report(result: InterviewResult, report_path: str, scores_path: str, wav_path: str | None = None) -> dict[str, str]:
    """Write the Markdown report + scores JSON (+ optional question audio)."""
    lines = [
        f"# Interview report — {result.role_title}",
        "",
        f"- Overall score: **{result.overall}/100** — {result.recommendation}",
        f"- Questions: {len(result.turns)}",
        "",
        "## Per-question scores",
        "",
        "| Question | Score | Band | Missed keywords |",
        "|---|---:|---|---",
    ]
    for t in result.turns:
        missed = ", ".join(t.score.keywords_missed) or "none"
        lines.append(f"| {t.question_id} | {t.question_total} | {t.score.band} | {missed} |")
    lines += [
        "",
        "## Strengths (keywords covered)",
        "",
        ", ".join(result.strengths) or "none yet",
        "",
        "## Gaps to practise (keywords missed)",
        "",
        ", ".join(result.gaps) or "none — every keyword covered",
        "",
        "## Transcript",
        "",
    ]
    for t in result.turns:
        lines += [
            f"**Q ({t.question_id}):** {t.question}",
            "",
            f"**A:** {t.answer or '(no answer)'}",
            "",
            f"**Follow-up:** {t.followup}",
            "",
            f"**A:** {t.followup_answer or '(no answer)'}",
            "",
        ]
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(result.as_dict(), f, indent=2)
    out = {"report": report_path, "scores": scores_path}
    if wav_path and result.turns:
        codec = ToneCodec()
        audio = codec.encode_text(result.turns[0].question)
        write_wav(wav_path, audio)
        out["wav"] = wav_path
    return out

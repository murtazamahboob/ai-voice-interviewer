"""AI Voice Interviewer — offline mock job interviews by voice.

Asks structured questions, listens through a tone codec, scores each
answer on a transparent rubric, adapts follow-ups to the answer, and
writes a report with a hire recommendation. No microphone, network or
API key needed.
"""
from .interview import InterviewResult, Turn, run_interview
from .questions import get_role, list_roles
from .scoring import AnswerScore, score_answer

__all__ = [
    "AnswerScore",
    "InterviewResult",
    "Turn",
    "get_role",
    "list_roles",
    "run_interview",
    "score_answer",
]
__version__ = "1.0.0"

import json

from interviewer.cli import DEMO_ANSWERS, DEMO_FOLLOWUPS
from interviewer.interview import pick_followup, run_interview, write_report
from interviewer.questions import get_role
from interviewer.scoring import score_answer


def test_demo_interview_is_strong_and_deterministic():
    first = run_interview("python-developer", DEMO_ANSWERS, DEMO_FOLLOWUPS)
    second = run_interview("python-developer", DEMO_ANSWERS, DEMO_FOLLOWUPS)
    assert first.overall == second.overall
    assert first.overall >= 55
    assert first.recommendation in ("Hire", "Strong hire")
    assert len(first.turns) == 4
    assert all(0 <= t.question_total <= 100 for t in first.turns)
    assert first.duration_s >= 0


def test_weak_answers_get_scaffolded_followup():
    result = run_interview("python-developer", {"py-1": "i do not know"}, {})
    turn = result.turns[0]
    assert turn.score.total < 40
    assert turn.followup == get_role("python-developer").questions[0].scaffold_followup
    assert result.overall < 55


def test_pick_followup_branches():
    q = get_role("python-developer").questions[0]
    mid = score_answer(
        "a list is mutable and a tuple is immutable, so I use lists when I need to change things",
        q.keywords,
    )
    assert 40 <= mid.total < 70
    assert pick_followup(q, mid) == q.standard_followup
    strong = score_answer(
        "lists are mutable, tuples are immutable and hashable, for example I built a cache "
        "with a tuple key in 2024, first I chose the key then I tested it because it had to "
        "be hashable, so it worked as a result",
        q.keywords,
    )
    assert strong.total >= 70
    assert pick_followup(q, strong) == q.stretch_followup


def test_followup_can_rescue_a_weak_answer():
    weak = run_interview("python-developer", {"py-1": "a tuple"}, {})
    rescued = run_interview(
        "python-developer",
        {"py-1": "a tuple"},
        {"py-1": "a tuple is immutable and hashable, lists are mutable, for example I built a cache keyed by a tuple in 2024"},
    )
    assert rescued.turns[0].question_total > weak.turns[0].question_total


def test_empty_interview_reports_gaps_not_crash():
    result = run_interview("data-analyst", {}, {})
    assert result.overall == 0.0
    assert result.recommendation.startswith("No hire")
    assert result.gaps  # every keyword missed


def test_write_report_creates_report_and_scores(tmp_path):
    result = run_interview("python-developer", DEMO_ANSWERS, DEMO_FOLLOWUPS)
    paths = write_report(
        result,
        str(tmp_path / "demo_report.md"),
        str(tmp_path / "scores.json"),
        str(tmp_path / "first_question.wav"),
    )
    report = (tmp_path / "demo_report.md").read_text()
    assert result.recommendation in report
    assert "Per-question scores" in report
    scores = json.loads((tmp_path / "scores.json").read_text())
    assert scores["overall"] == result.overall
    assert len(scores["turns"]) == 4
    assert (tmp_path / "first_question.wav").stat().st_size > 44
    assert paths["report"].endswith("demo_report.md")

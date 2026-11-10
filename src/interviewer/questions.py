"""Interview question bank: 3 roles, 4 core questions each.

Every question carries the keywords a strong answer should hit, a stretch
follow-up for strong answers and a scaffolded follow-up (with a hint) for
weak ones. The interviewer picks between them from the scored answer, so
the same question plays differently for a strong and a struggling candidate.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    keywords: tuple[str, ...]
    stretch_followup: str
    scaffold_followup: str
    standard_followup: str


@dataclass(frozen=True)
class Role:
    id: str
    title: str
    intro: str
    questions: tuple[Question, ...]


def _q(qid, text, keywords, stretch, scaffold, standard):
    return Question(qid, text, tuple(keywords), stretch, scaffold, standard)


ROLES: dict[str, Role] = {
    "python-developer": Role(
        id="python-developer",
        title="Python Developer",
        intro="Welcome to your Python developer mock interview. I will ask four questions, listen to each answer, and score it on content, depth and examples.",
        questions=(
            _q(
                "py-1",
                "Explain the difference between a list and a tuple in Python, and when you would choose each one.",
                ("immutable", "mutable", "hashable", "list", "tuple"),
                "When would you use a tuple as a dictionary key, and what breaks if you try that with a list?",
                "Hint: think about which one you can change after creating it. Which one is mutable and which is immutable?",
                "Can you give an example where mutability caused a bug for you?",
            ),
            _q(
                "py-2",
                "How does Python handle memory, and what is the garbage collector doing for you?",
                ("reference counting", "garbage collector", "memory", "reference", "cycle"),
                "How would you find and fix a reference cycle that keeps objects alive?",
                "Hint: Python counts references to each object. What happens when that count reaches zero?",
                "What happens to an object nobody references any more?",
            ),
            _q(
                "py-3",
                "Walk me through how you would design a small REST API for a to-do app.",
                ("endpoint", "rest", "api", "database", "validation"),
                "How would you add authentication and rate limiting without slowing the API down?",
                "Hint: start with the resources — what endpoints would a to-do app need, and what should each return?",
                "How would you handle a request with missing or invalid data?",
            ),
            _q(
                "py-4",
                "Tell me about a bug that took you a long time to find. How did you track it down?",
                ("debug", "reproduce", "log", "test", "fix"),
                "What would you change in your workflow so that class of bug is caught automatically next time?",
                "Hint: walk through the steps — how did you reproduce it, and what clue finally pointed at the cause?",
                "What tool or technique helped you most while debugging it?",
            ),
        ),
    ),
    "data-analyst": Role(
        id="data-analyst",
        title="Data Analyst",
        intro="Welcome to your data analyst mock interview. I will ask four questions, listen to each answer, and score it on content, depth and examples.",
        questions=(
            _q(
                "da-1",
                "You get a sales dataset with missing values and duplicate rows. How do you clean it?",
                ("missing", "duplicate", "clean", "impute", "validate"),
                "How do you decide between dropping rows and imputing values when 30 percent of a column is missing?",
                "Hint: start with the missing values — when would you fill them in, and when would you drop the row?",
                "How would you check that your cleaning did not distort the data?",
            ),
            _q(
                "da-2",
                "Explain the difference between correlation and causation, with an example.",
                ("correlation", "causation", "confounding", "experiment", "variable"),
                "How would you design a test to check whether a correlation you found is causal?",
                "Hint: two things can move together without one causing the other. What else could explain it?",
                "Can you give an example of a misleading correlation?",
            ),
            _q(
                "da-3",
                "How would you build a dashboard for a non-technical manager?",
                ("dashboard", "kpi", "visualisation", "visualization", "audience"),
                "How do you stop a dashboard from becoming a wall of charts nobody reads?",
                "Hint: think about the audience first — what three numbers does the manager actually decide on?",
                "What chart would you choose for a trend over time, and why?",
            ),
            _q(
                "da-4",
                "Tell me about a time your analysis changed a decision. What did you find?",
                ("analysis", "insight", "decision", "data", "impact"),
                "How did you convince a sceptical stakeholder who disagreed with your finding?",
                "Hint: walk through it — what was the question, what did the data show, and what changed?",
                "How did you present the finding so people acted on it?",
            ),
        ),
    ),
    "ml-engineer": Role(
        id="ml-engineer",
        title="Machine Learning Engineer",
        intro="Welcome to your machine learning engineer mock interview. I will ask four questions, listen to each answer, and score it on content, depth and examples.",
        questions=(
            _q(
                "ml-1",
                "Explain overfitting, and how you would detect and fix it.",
                ("overfitting", "validation", "regularisation", "regularization", "generalisation", "generalization"),
                "How do you tell overfitting apart from a data leak in the training set?",
                "Hint: the model does well on training data and badly on new data. What would you check first?",
                "What is the simplest fix you would try first?",
            ),
            _q(
                "ml-2",
                "How do you choose evaluation metrics for a classification problem with imbalanced classes?",
                ("precision", "recall", "f1", "accuracy", "imbalanced"),
                "When would you optimise for recall even if precision falls, and how would you explain that trade-off?",
                "Hint: accuracy can look great while the model misses every rare case. Which metrics catch that?",
                "Why is accuracy alone misleading here?",
            ),
            _q(
                "ml-3",
                "Walk me through deploying a model to production and monitoring it afterwards.",
                ("deploy", "monitor", "drift", "pipeline", "version"),
                "How would you roll back a model that starts drifting in production without downtime?",
                "Hint: think in stages — packaging, serving, then watching it. What would you watch for after launch?",
                "What would you log for every prediction?",
            ),
            _q(
                "ml-4",
                "Tell me about a model that performed worse than expected. How did you investigate?",
                ("debug", "error analysis", "data", "baseline", "metric"),
                "What systematic error analysis would you run before trying a bigger model?",
                "Hint: start with the errors — which examples is it getting wrong, and what do they have in common?",
                "What baseline did you compare against?",
            ),
        ),
    ),
}


def list_roles() -> list[str]:
    return sorted(ROLES)


def get_role(role_id: str) -> Role:
    try:
        return ROLES[role_id]
    except KeyError as exc:
        raise ValueError(
            f"unknown role {role_id!r}; choose one of: {', '.join(list_roles())}"
        ) from exc

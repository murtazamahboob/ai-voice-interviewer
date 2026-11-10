"""Command line: `interviewer demo` / `interviewer interview --role …`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .interview import run_interview, write_report
from .questions import list_roles

# Scripted demo answers: strong on purpose, so the demo shows the stretch
# follow-up path. Every answer is deterministic.
DEMO_ANSWERS = {
    "py-1": "A list is mutable and a tuple is immutable, so I use a list when I need to change items and a tuple for fixed data. Tuples are hashable, so I use them as dictionary keys. For example, I built a cache keyed by a tuple of user id and date.",
    "py-2": "Python uses reference counting, so each object tracks how many references point at it, and the garbage collector frees cycles the counter cannot catch. I used memory profiling to find a leak, then I fixed it by clearing a cache that held references for too long.",
    "py-3": "I would design a REST API with endpoints for each resource, so GET lists todos and POST creates one, backed by a database with validation on every request. For example, I built a small API with FastAPI, and I added tests for invalid input first, then I shipped it.",
    "py-4": "I had a bug where a cache returned stale data, so I reproduced it with a small test first, then I added logging around the cache, and I found the key was missing the user id. I fixed it by including the user id in the key, and then I added a regression test.",
}
DEMO_FOLLOWUPS = {
    "py-1": "Yes, I use tuples as dictionary keys for pairs, because lists are unhashable and would raise an error, so I convert the list to a tuple first.",
    "py-2": "I would use gc to find the cycle, then I would break it by using a weak reference, because that lets the garbage collector free the objects.",
    "py-3": "I would add token authentication and rate limiting with a cache, so a single user cannot flood the API, and I would return 429 when the limit is hit.",
    "py-4": "I would add a test for that class of bug and run it in CI, so the same stale cache bug is caught automatically before it ships again.",
}


def _demo(role: str = "python-developer") -> int:
    result = run_interview(role, DEMO_ANSWERS, DEMO_FOLLOWUPS)
    root = Path(__file__).resolve().parents[2]
    outdir = root / "outputs"
    outdir.mkdir(exist_ok=True)
    paths = write_report(
        result,
        str(outdir / "demo_report.md"),
        str(outdir / "scores.json"),
        str(outdir / "first_question.wav"),
    )
    print(f"role: {result.role_title}")
    for t in result.turns:
        print(f"{t.question_id}: {t.question_total}/100 ({t.score.band})")
    print(f"overall: {result.overall}/100 — {result.recommendation}")
    print(f"report={paths['report']}")
    return 0


def _interview(args) -> int:
    answers = json.loads(args.answers) if args.answers else {}
    followups = json.loads(args.followups) if args.followups else {}
    result = run_interview(args.role, answers, followups)
    print(f"role: {result.role_title}")
    for t in result.turns:
        print(f"Q: {t.question}")
        print(f"A: {t.answer or '(no answer)'}  -> {t.question_total}/100 ({t.score.band})")
        print(f"Follow-up: {t.followup}")
        if t.followup_answer:
            print(f"A: {t.followup_answer}")
    print(f"overall: {result.overall}/100 — {result.recommendation}")
    if result.gaps:
        print("practise: " + ", ".join(result.gaps))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="interviewer", description="AI Voice Interviewer — offline mock interviews by voice.")
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("demo", help="Run the scripted demo interview and write outputs/")
    d.add_argument("--role", default="python-developer", choices=list_roles())
    i = sub.add_parser("interview", help="Run an interview from JSON answers.")
    i.add_argument("--role", default="python-developer", choices=list_roles())
    i.add_argument("--answers", default="{}", help='JSON map question id -> answer, e.g. \'{"py-1": "..."}\'')
    i.add_argument("--followups", default="{}", help="JSON map question id -> follow-up answer")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        return _demo(args.role)
    return _interview(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

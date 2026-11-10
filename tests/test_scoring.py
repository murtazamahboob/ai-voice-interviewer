from interviewer.scoring import band_for, recommendation_for, score_answer

KEYWORDS = ("immutable", "mutable", "hashable", "list", "tuple")


def test_strong_answer_scores_high():
    answer = (
        "A list is mutable and a tuple is immutable, so I use a list when I need to change items "
        "and a tuple for fixed data. Tuples are hashable, so I use them as dictionary keys. "
        "For example, I built a cache keyed by a tuple of user id and date in 2024, first I chose "
        "the key, then I tested it, because it had to be hashable."
    )
    s = score_answer(answer, KEYWORDS)
    assert s.total >= 75
    assert s.band == "Strong"
    assert s.keywords_missed == ()
    assert s.total == s.keyword_score + s.depth_score + s.example_score + s.structure_score


def test_empty_answer_scores_zero():
    s = score_answer("", KEYWORDS)
    assert s.total == 0
    assert s.band == "Needs work"
    assert len(s.keywords_missed) == len(KEYWORDS)


def test_short_answer_capped_on_depth():
    s = score_answer("a tuple is immutable", KEYWORDS)
    assert s.depth_score == 5
    assert s.total < 55


def test_keyword_coverage_drives_score():
    low = score_answer("i like python very much and it is nice", KEYWORDS)
    high = score_answer("lists are mutable, tuples are immutable and hashable", KEYWORDS)
    assert high.keyword_score > low.keyword_score
    assert high.total > low.total


def test_bands_and_recommendations():
    assert band_for(80) == "Strong"
    assert band_for(60) == "Solid"
    assert band_for(40) == "Developing"
    assert band_for(10) == "Needs work"
    assert recommendation_for(80) == "Strong hire"
    assert recommendation_for(60) == "Hire"
    assert recommendation_for(40).startswith("Maybe")
    assert recommendation_for(10).startswith("No hire")

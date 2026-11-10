import pytest

from interviewer.questions import get_role, list_roles


def test_three_roles_each_with_four_questions():
    roles = list_roles()
    assert roles == ["data-analyst", "ml-engineer", "python-developer"]
    for role_id in roles:
        role = get_role(role_id)
        assert len(role.questions) == 4
        for q in role.questions:
            assert q.text and len(q.keywords) >= 4
            assert q.stretch_followup != q.scaffold_followup != q.standard_followup


def test_unknown_role_raises_helpful_error():
    with pytest.raises(ValueError, match="unknown role"):
        get_role("chef")


def test_no_duplicate_question_ids_within_a_role():
    for role_id in list_roles():
        ids = [q.id for q in get_role(role_id).questions]
        assert len(ids) == len(set(ids))

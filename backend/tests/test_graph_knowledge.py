from services.graph_knowledge import lookup_symptoms

ROWS = [
    {"name": "khát nhiều", "source_id": "s", "source_title": "T", "section": "Symptoms", "evidence": "e1"},
    {"name": "mờ mắt", "source_id": "s", "source_title": "T", "section": "Symptoms", "evidence": "e2"},
]


class FakeGraph:
    def run(self, cypher, params=None):
        return ROWS


def test_general_question_returns_all_symptoms():
    assert len(lookup_symptoms(FakeGraph(), "triệu chứng đái tháo đường là gì")) == 2


def test_specific_symptom_filters_results():
    out = lookup_symptoms(FakeGraph(), "bị khát nhiều có sao không")
    assert [r["name"] for r in out] == ["khát nhiều"]


def test_unrelated_question_returns_nothing():
    assert lookup_symptoms(FakeGraph(), "cách nấu phở bò") == []
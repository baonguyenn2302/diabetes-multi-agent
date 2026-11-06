import pytest

from agents.medical_knowledge_agent import (
    STATUS_INSUFFICIENT,
    STATUS_SUCCESS,
    MedicalKnowledgeAgent,
)
from services.chroma_service import KnowledgeUnavailableError


def hit(distance, document="Symptoms\n\nText", source_id="who"):
    return {
        "document": document,
        "distance": distance,
        "source_id": source_id,
        "source_title": "Tiêu đề",
        "publisher": "Cơ quan",
        "date": "2024-11-14",
        "url": "https://example.org",
        "section": "Symptoms",
        "subsection": "",
    }


class FakeStore:
    def __init__(self, hits=None, exc=None):
        self.hits = hits or []
        self.exc = exc

    def query(self, question, top_k=4):
        if self.exc is not None:
            raise self.exc
        return self.hits


def make_task(question):
    return {"session_id": "s1", "task_id": "t1", "input": {"question": question}}


def test_success_keeps_only_relevant_hits():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.14), hit(0.30), hit(0.60)]), max_distance=0.40)
    out = agent.run(make_task("triệu chứng"))
    assert out["status"] == STATUS_SUCCESS
    sources = out["result"]["sources"]
    vector_sources = [source for source in sources if source["origin"] == "chroma"]
    graph_sources = [source for source in sources if source["origin"] == "graph_csv"]
    assert len(vector_sources) == 2
    assert all(source["distance"] <= 0.40 for source in vector_sources)
    assert len(graph_sources) == 4


def test_success_includes_citation_fields():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.14)]), max_distance=0.40)
    src = agent.run(make_task("triệu chứng"))["result"]["sources"][0]
    assert src["source_title"] == "Tiêu đề"
    assert src["url"] == "https://example.org"
    assert src["section"] == "Symptoms"


def test_insufficient_when_all_hits_far():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.55), hit(0.73)]), max_distance=0.40)
    out = agent.run(make_task("cách nấu phở"))
    assert out["status"] == STATUS_INSUFFICIENT
    assert out["result"]["sources"] == []
    assert out["result"]["best_distance"] == 0.55


def test_insufficient_when_store_empty_result():
    agent = MedicalKnowledgeAgent(FakeStore([]), max_distance=0.40)
    out = agent.run(make_task("bất kỳ"))
    assert out["status"] == STATUS_INSUFFICIENT
    assert out["result"]["best_distance"] is None


def test_unavailable_store_returns_error():
    agent = MedicalKnowledgeAgent(FakeStore(exc=KnowledgeUnavailableError("rỗng")))
    out = agent.run(make_task("triệu chứng"))
    assert out["status"] == "error"
    assert out["error"]["code"] == "knowledge_unavailable"


def test_missing_question_returns_error():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.1)]))
    out = agent.run({"session_id": "s", "task_id": "t", "input": {}})
    assert out["status"] == "error"
    assert out["error"]["code"] == "missing_question"


def test_excerpt_is_truncated():
    long_doc = "Symptoms\n\n" + "a" * 2000
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.1, document=long_doc)]), max_distance=0.40)
    excerpt = agent.run(make_task("triệu chứng"))["result"]["sources"][0]["excerpt"]
    assert len(excerpt) <= 400
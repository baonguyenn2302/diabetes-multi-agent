from agents.medical_knowledge_agent import STATUS_SUCCESS, MedicalKnowledgeAgent
from services.neo4j_service import Neo4jUnavailableError

GRAPH_ROW = {
    "name": "khát nhiều",
    "source_id": "who_diabetes_fact_sheet_2024-11-14",
    "source_title": "Diabetes – Fact sheet (WHO)",
    "section": "Symptoms",
    "evidence": "feeling very thirsty",
}


class FakeStore:
    def __init__(self, hits=None):
        self.hits = hits or []

    def query(self, question, top_k=4):
        return self.hits


class FakeGraph:
    def __init__(self, rows=None, exc=None, configured=True):
        self.rows = rows or []
        self.exc = exc
        self.configured = configured

    def run(self, cypher, params=None):
        if self.exc is not None:
            raise self.exc
        return self.rows


def hit(distance):
    return {"document": "Symptoms\n\ntext", "distance": distance,
            "source_id": "who", "source_title": "WHO", "publisher": "", "date": "",
            "url": "", "section": "Symptoms", "subsection": ""}


def task(question):
    return {"session_id": "s", "task_id": "t", "input": {"question": question}}


def test_graph_sources_appended_with_origin():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.2)]), graph=FakeGraph([GRAPH_ROW]))
    out = agent.run(task("triệu chứng đái tháo đường"))
    assert [s["origin"] for s in out["result"]["sources"]] == ["chroma", "neo4j"]


def test_graph_only_result_is_success():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.9)]), graph=FakeGraph([GRAPH_ROW]))
    out = agent.run(task("triệu chứng"))
    assert out["status"] == STATUS_SUCCESS
    assert out["result"]["sources"][0]["origin"] == "neo4j"


def test_graph_unavailable_keeps_chroma_and_warns():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.2)]),
                                  graph=FakeGraph(exc=Neo4jUnavailableError("down")))
    out = agent.run(task("triệu chứng"))
    assert out["status"] == STATUS_SUCCESS
    assert len(out["result"]["sources"]) == 1
    assert any("Neo4j không khả dụng" in w for w in out["result"]["warnings"])


def test_graph_not_configured_adds_no_warning():
    agent = MedicalKnowledgeAgent(FakeStore([hit(0.2)]), graph=FakeGraph(configured=False))
    out = agent.run(task("triệu chứng"))
    assert out["result"]["warnings"] == []
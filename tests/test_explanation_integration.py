"""Coordinator + Explanation Agent với luồng thật (DL giả, không cần TensorFlow/Neo4j)."""
from app.agents.data_agent import PatientDataAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.kg_rag_agent import KGRAGAgent
from app.agents.rule_agent import RuleBasedAgent
from app.coordinator import CoordinatorAgent
from app.schemas import AgentMessage
from tests.test_coordinator_integration import FakeDL, HIGH, LOW
from tests.test_kg_rag_agent import fake_runner as kg_runner
from tests.test_rule_agent import runner as rule_runner


def coord(dl):
    return CoordinatorAgent(PatientDataAgent(), dl, RuleBasedAgent.from_runner(rule_runner),
                            KGRAGAgent(kg_runner), explainer=ExplanationAgent())


class BadDL:
    def run(self, rid, feats):
        return AgentMessage.fail(rid, "BadDL", "model không tải được")


def test_high_risk_report_has_flags_and_sources():
    r = coord(FakeDL(lambda f: 0.95)).handle(HIGH)
    assert r["status"] == "ok"
    assert "[R01]" in r["report"] and "Nguồn:" in r["report"]
    assert [t for t in r["trace"] if t["agent"] == "explain"][0]["status"] == "ok"


def test_conflict_is_shown_for_review():
    r = coord(FakeDL(lambda f: 0.1)).handle(HIGH)
    assert r["needs_human_review"] is True
    assert "Cần chuyên gia y tế xem xét" in r["report"]


def test_report_still_produced_when_dl_fails():
    r = coord(BadDL()).handle(LOW)
    assert r["status"] == "partial" and r["report"] is not None
    assert "Không có kết quả dự đoán" in r["report"]


def test_no_report_when_validation_fails():
    r = coord(FakeDL(lambda f: 0.1)).handle({"gender": "Female", "age": "abc"})
    assert r["status"] == "validation_error" and r["report"] is None
    assert all(t["agent"] != "explain" for t in r["trace"])

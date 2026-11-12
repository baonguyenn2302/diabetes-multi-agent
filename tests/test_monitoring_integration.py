"""Coordinator ghi log thật: kiểm tra log không chứa dữ liệu bệnh nhân."""
import json, pathlib, tempfile
from app.agents.data_agent import PatientDataAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.kg_rag_agent import KGRAGAgent
from app.agents.monitoring_agent import MonitoringAgent
from app.agents.rule_agent import RuleBasedAgent
from app.coordinator import CoordinatorAgent
from tests.test_coordinator_integration import FakeDL, HIGH, LOW
from tests.test_kg_rag_agent import fake_runner as kg_runner
from tests.test_rule_agent import runner as rule_runner


def test_coordinator_logs_each_request_without_patient_values():
    p = pathlib.Path(tempfile.mkdtemp()) / "audit.jsonl"
    c = CoordinatorAgent(PatientDataAgent(), FakeDL(lambda f: 0.1),
                         RuleBasedAgent.from_runner(rule_runner), KGRAGAgent(kg_runner),
                         explainer=ExplanationAgent(), monitor=MonitoringAgent(p))
    c.handle(LOW)
    c.handle(HIGH)
    c.handle({"gender": "Female", "age": "abc"})
    text = p.read_text(encoding="utf-8")
    recs = [json.loads(l) for l in text.splitlines()]
    assert [r["outcome"] for r in recs] == ["ok", "ok", "validation_error"]
    assert "Female" not in text and "Male" not in text and "HbA1c_level" not in text
    assert recs[0]["steps"] == ["data", "dl", "rule", "kg", "explain"]

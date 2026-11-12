"""Luồng thật: Data Agent + Rule Agent + KG/RAG Agent (ngưỡng và bằng chứng từ KB), DL là bản giả
để không cần TensorFlow. Không cần kết nối Neo4j."""
from app.agents.data_agent import PatientDataAgent
from app.agents.rule_agent import RuleBasedAgent
from app.agents.kg_rag_agent import KGRAGAgent
from app.coordinator import CoordinatorAgent
from app.schemas import AgentMessage
from tests.test_kg_rag_agent import fake_runner as kg_runner
from tests.test_rule_agent import runner as rule_runner

LOW = dict(gender="Female", age=25, hypertension=0, heart_disease=0, smoking_history="never",
           bmi=22.0, HbA1c_level=5.0, blood_glucose_level=100)
HIGH = dict(gender="Male", age=62, hypertension=1, heart_disease=1, smoking_history="former",
            bmi=33.5, HbA1c_level=8.2, blood_glucose_level=220)


class FakeDL:
    def __init__(self, score_fn): self.score_fn = score_fn
    def run(self, rid, feats):
        s = self.score_fn(feats)
        return AgentMessage.ok(rid, "FakeDL", {"prediction": int(s >= 0.85),
                               "label": "nguy cơ cao" if s >= 0.85 else "nguy cơ thấp",
                               "score": s}, version="fake")


def build(score_fn):
    return CoordinatorAgent(PatientDataAgent(), FakeDL(score_fn),
                            RuleBasedAgent.from_runner(rule_runner), KGRAGAgent(kg_runner))


def ids(r):
    return [f["id"] for f in r["rules"]["flags"]]


def test_low_risk_end_to_end_is_ok():
    r = build(lambda f: 0.1).handle(LOW)
    assert r["status"] == "ok" and r["prediction"]["label"] == "nguy cơ thấp"
    assert r["needs_human_review"] is False
    assert r["evidence"] and all(e["source_title"] for e in r["evidence"])


def test_high_risk_gets_lab_and_risk_flags():
    r = build(lambda f: 0.95).handle(HIGH)
    assert r["status"] == "ok"
    for fid in ("R01", "R03", "R06", "R07", "R08", "R09"):
        assert fid in ids(r), fid
    assert r["needs_human_review"] is False


def test_model_says_low_but_labs_high_triggers_review():
    r = build(lambda f: 0.1).handle(HIGH)
    assert "C01" in ids(r) and r["needs_human_review"] is True


def test_question_is_used_for_evidence():
    r = build(lambda f: 0.1).handle(LOW, "Triệu chứng của tiểu đường là gì?")
    assert any(e.get("relation") == "SYMPTOM_OF" for e in r["evidence"])


def test_invalid_input_stops_with_validation_error():
    r = build(lambda f: 0.1).handle({"gender": "Female", "age": "abc"})
    assert r["status"] == "validation_error" and r["prediction"] is None and r["evidence"] == []

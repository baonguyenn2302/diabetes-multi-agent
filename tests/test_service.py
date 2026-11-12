"""Test lớp service: ánh xạ trạng thái sang mã HTTP. Không cần fastapi."""
import json
from app.agents.data_agent import PatientDataAgent
from app.agents.kg_rag_agent import KGRAGAgent
from app.agents.rule_agent import RuleBasedAgent
from app.coordinator import CoordinatorAgent
from app.schemas import AgentMessage
from app.service import assess
from tests.test_coordinator_integration import LOW, build
from tests.test_kg_rag_agent import fake_runner as kg_runner
from tests.test_rule_agent import runner as rule_runner


class BadDL:
    def run(self, rid, feats):
        return AgentMessage.fail(rid, "BadDL", "model không tải được")


def test_ok_is_200():
    code, res = assess(build(lambda f: 0.1), LOW)
    assert code == 200 and res["status"] == "ok"


def test_validation_error_is_422():
    code, res = assess(build(lambda f: 0.1), {"gender": "Female", "age": "abc"})
    assert code == 422 and res["status"] == "validation_error"


def test_partial_is_still_200():
    c = CoordinatorAgent(PatientDataAgent(), BadDL(), RuleBasedAgent.from_runner(rule_runner), KGRAGAgent(kg_runner))
    code, res = assess(c, LOW)
    assert code == 200 and res["status"] == "partial"


def test_result_is_json_serializable():
    _, res = assess(build(lambda f: 0.95), LOW, "Triệu chứng là gì?")
    json.dumps(res, ensure_ascii=False)

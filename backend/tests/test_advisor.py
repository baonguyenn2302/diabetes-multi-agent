"""Run from backend: python -m unittest discover -s tests -p test_advisor.py -v"""
import json
import tempfile
import unittest
from pathlib import Path

from agents.medical_advisor_agent import MedicalAdvisorAgent
from agents.coordinator import Coordinator
from agents.registry import build_registry
from schemas.agent_messages import make_task, validate_result


class FakeAgent:
    def __init__(self, name, result):
        self.name, self.result, self.calls = name, result, []

    def run(self, task):
        self.calls.append(task)
        return {"session_id": task["session_id"], "task_id": task["task_id"],
                "agent": self.name, "status": "success", "result": self.result, "error": None}


class FakeOllama:
    def __init__(self, output):
        self.output = output

    def classify_intent(self, message):
        return "symptoms"

    def summarize(self, question, sources, prediction_text):
        return self.output


class AdvisorTests(unittest.TestCase):
    def setUp(self):
        self.advisor = MedicalAdvisorAgent()

    def review(self, question="Tôi có triệu chứng gì?", draft="Đây là thông tin tham khảo."):
        task = make_task("session-test", "medical_advisor_agent", "review_advice",
                         {"question": question, "draft": draft})
        return validate_result(self.advisor.run(task), task)

    def test_safe_draft_approved(self):
        response = self.review(draft="Một số biểu hiện được đề cập trong nguồn tham khảo.")
        self.assertTrue(response["result"]["approved"])
        self.assertIn("không thay thế", response["result"]["revised_answer"])

    def test_diagnostic_assertion_replaced(self):
        response = self.review(draft="Bạn chắc chắn mắc bệnh tiểu đường.")
        self.assertFalse(response["result"]["approved"])
        self.assertNotIn("Bạn chắc chắn mắc", response["result"]["revised_answer"])
        self.assertIn("diagnostic_claim", response["result"]["review_flags"])

    def test_medication_directive_replaced(self):
        response = self.review(draft="Bạn nên ngừng thuốc ngay.")
        self.assertFalse(response["result"]["approved"])
        self.assertIn("treatment_instruction", response["result"]["review_flags"])

    def test_missing_draft(self):
        response = self.review(draft="")
        self.assertEqual(response["status"], "needs_input")

    def test_invalid_task(self):
        task = make_task("session-test", "medical_advisor_agent", "wrong_task", {})
        response = validate_result(self.advisor.run(task), task)
        self.assertEqual(response["status"], "invalid_input")

    def test_registry_includes_advisor(self):
        # Stub both B modules to avoid TensorFlow / Chroma imports.
        import sys
        from types import ModuleType
        from unittest.mock import patch
        risk_module = ModuleType("agents.risk_assessment_agent")
        knowledge_module = ModuleType("agents.medical_knowledge_agent")
        risk_module.RiskAssessmentAgent = lambda: object()
        knowledge_module.MedicalKnowledgeAgent = lambda: object()
        with patch.dict(sys.modules, {
            "agents.risk_assessment_agent": risk_module,
            "agents.medical_knowledge_agent": knowledge_module,
        }):
            registry = build_registry()
        self.assertIsInstance(registry["medical_advisor_agent"], MedicalAdvisorAgent)



class CoordinatorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.meta = Path(self.tmp.name) / "metadata.json"
        self.meta.write_text(json.dumps({"input_fields": ["age", "bmi"]}), encoding="utf-8")
        self.risk = FakeAgent("risk_assessment_agent", {"prediction": 1, "probability": 0.75})
        self.knowledge = FakeAgent("medical_knowledge_agent", {
            "sources": [{"excerpt": "Một số dấu hiệu cần được đánh giá thêm.", "source_title": "Tài liệu thử nghiệm"}]
        })
        self.agents = {"risk_assessment_agent": self.risk, "medical_knowledge_agent": self.knowledge,
                       "medical_advisor_agent": MedicalAdvisorAgent()}

    def tearDown(self):
        self.tmp.cleanup()

    def test_symptoms_answer_passes_real_advisor(self):
        result = Coordinator(self.agents, self.meta, ollama=FakeOllama("Thông tin từ nguồn tham khảo.")).run(
            "Tôi khát nước và đi tiểu nhiều")
        self.assertIn("không thay thế", result["answer"])
        self.assertEqual(len(self.risk.calls), 0)
        self.assertEqual([x["status"] for x in result["agent_trace"] if x["agent"] == "medical_advisor_agent"],
                         ["running", "success"])

    def test_unsafe_llm_answer_is_replaced(self):
        result = Coordinator(self.agents, self.meta, ollama=FakeOllama("Bạn chắc chắn mắc bệnh tiểu đường.")).run(
            "Tôi khát nước và đi tiểu nhiều")
        self.assertNotIn("Bạn chắc chắn mắc", result["answer"])
        self.assertTrue(any("khẳng định" in w for w in result["warnings"]))

    def test_risk_uses_advisor_and_retains_no_diagnosis(self):
        result = Coordinator(self.agents, self.meta, ollama=FakeOllama("Đây là dữ liệu tham khảo từ nguồn.")).run(
            "Tôi muốn đánh giá nguy cơ tiểu đường", {"age": 30, "bmi": 23})
        self.assertEqual(len(self.risk.calls), 1)
        self.assertIn("không thay thế", result["answer"])

    def test_missing_features_skips_all_agents(self):
        result = Coordinator(self.agents, self.meta, ollama=FakeOllama("N/A")).run(
            "Tôi muốn đánh giá nguy cơ tiểu đường", {"age": 30})
        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(len(self.risk.calls), 0)

    def test_missing_advisor_does_not_return_unchecked_answer(self):
        agents = {"medical_knowledge_agent": self.knowledge}
        result = Coordinator(agents, self.meta, ollama=FakeOllama("Bạn chắc chắn mắc bệnh tiểu đường.")).run(
            "Tôi khát nước và đi tiểu nhiều")
        self.assertEqual(result["status"], "error")
        self.assertNotIn("Bạn chắc chắn mắc", result["answer"])


if __name__ == "__main__":
    unittest.main()

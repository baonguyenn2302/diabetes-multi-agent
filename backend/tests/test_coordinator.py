"""Run: cd backend && python -m unittest discover -s tests -p test_coordinator.py -v"""
import json
import tempfile
import unittest
from pathlib import Path
from agents.coordinator import Coordinator


class FakeAgent:
    def __init__(self, name, result):
        self.name, self.result, self.calls = name, result, []

    def run(self, task):
        self.calls.append(task)
        return {"session_id": task["session_id"], "task_id": task["task_id"],
                "agent": self.name, "status": "success", "result": self.result, "error": None}


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        metadata = Path(self.temp.name) / 'metadata.json'
        metadata.write_text(json.dumps({"input_fields": ["age", "bmi"]}), encoding='utf-8')
        self.risk = FakeAgent('risk_assessment_agent', {"prediction": 0, "probability": 0.2})
        self.knowledge = FakeAgent('medical_knowledge_agent', {"sources": [{"excerpt": "Tài liệu mẫu dùng để kiểm thử", "source_title": "Nguồn kiểm thử"}]})
        self.advisor = FakeAgent('medical_advisor_agent', {"warnings": []})
        self.coordinator = Coordinator({a.name: a for a in (self.risk, self.knowledge, self.advisor)}, metadata)

    def tearDown(self):
        self.temp.cleanup()

    def test_knowledge_only_calls_knowledge(self):
        result = self.coordinator.run('Tiểu đường type 2 là gì?')
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(self.knowledge.calls), 1)
        self.assertEqual(len(self.risk.calls), 0)
        self.assertEqual(len(self.advisor.calls), 0)

    def test_missing_features_do_not_call_model(self):
        result = self.coordinator.run('Tôi muốn đánh giá nguy cơ tiểu đường', {"age": 30})
        self.assertEqual(result['status'], 'needs_input')
        self.assertEqual(result['missing_fields'], ['bmi'])
        self.assertEqual(len(self.risk.calls), 0)

    def test_risk_calls_all_three(self):
        result = self.coordinator.run('Tôi muốn đánh giá nguy cơ tiểu đường', {"age": 30, "bmi": 23})
        self.assertEqual(result['status'], 'success')
        self.assertEqual((len(self.risk.calls), len(self.knowledge.calls), len(self.advisor.calls)), (1, 1, 1))

    def test_symptoms_do_not_trigger_prediction(self):
        self.coordinator.run('Tôi khát nước và đi tiểu nhiều, cần làm gì?')
        self.assertEqual((len(self.risk.calls), len(self.knowledge.calls), len(self.advisor.calls)), (0, 1, 1))


if __name__ == '__main__':
    unittest.main()

"""Step 5 Flask API persistence tests; mock Coordinator, actual SQLite database."""
import tempfile
import unittest
from pathlib import Path
from app import create_app


class CoordinatorStub:
    def run(self, message, health_data=None, session_id=None):
        return {"session_id": session_id or "demo-generated", "intent": "knowledge", "status": "success",
                "answer": "Phản hồi demo", "warnings": [], "sources": [],
                "agent_trace": [{"agent": "coordinator", "status": "success", "message": "Nhận nhiệm vụ"},
                                {"agent": "medical_knowledge_agent", "status": "success", "message": "Hoàn thành"}]}


class SQLiteAPITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = str(Path(self.tmp.name) / "test.sqlite3")
        self.config = {"TESTING": True, "SQLITE_PATH": self.db_path,
                       "COORDINATOR_FACTORY": CoordinatorStub}
        self.app = create_app(self.config)
        self.client = self.app.test_client()

    def test_persistence_survives_recreating_app(self):
        resp = self.client.post("/api/chat", json={"session_id": "abc", "message": "Câu hỏi 1"})
        self.assertEqual(resp.status_code, 200)
        second_app = create_app(self.config)
        status = second_app.test_client().get("/api/agents/status?session_id=abc").get_json()
        self.assertEqual(status["tracking"], "sqlite_persistent")
        self.assertEqual(status["latest_execution"]["agent_trace"][1]["agent"], "medical_knowledge_agent")
        items = second_app.test_client().get("/api/history?session_id=abc").get_json()
        self.assertEqual(items["count"], 1)
        self.assertEqual(items["history"][0]["message"], "Câu hỏi 1")

    def test_history_isolated_and_validated(self):
        self.client.post("/api/chat", json={"session_id": "abc", "message": "Kiến thức"})
        self.assertEqual(self.client.get("/api/history?session_id=xyz").get_json()["count"], 0)
        self.assertEqual(self.client.get("/api/history").status_code, 400)
        self.assertEqual(self.client.get("/api/history?session_id=abc&limit=0").status_code, 400)
        self.assertEqual(self.client.get("/api/history?session_id=abc&limit=no").status_code, 400)

    def test_chats_same_session_have_ordered_history(self):
        self.client.post("/api/chat", json={"session_id": "abc", "message": "Lần đầu"})
        self.client.post("/api/chat", json={"session_id": "abc", "message": "Lần sau"})
        items = self.client.get("/api/history?session_id=abc&limit=1").get_json()
        self.assertEqual(items["count"], 1)
        self.assertEqual(items["history"][0]["message"], "Lần sau")

if __name__ == "__main__":
    unittest.main()

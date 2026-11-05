"""SQLite persistence tests (no Flask, TensorFlow, or ChromaDB needed)."""
import tempfile
from contextlib import closing
import unittest
from pathlib import Path
from services.sqlite_service import SQLiteService


class SQLiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "history.sqlite3"
        self.service = SQLiteService(self.path)
        self.result = {
            "session_id": "demo-a", "intent": "symptoms", "status": "success",
            "answer": "Tư vấn có nguồn (demo)",
            "agent_trace": [
                {"agent": "coordinator", "status": "success", "message": "Chọn Agent"},
                {"agent": "medical_knowledge_agent", "status": "running", "task_id": "task1", "message": "retrieve"},
                {"agent": "medical_knowledge_agent", "status": "success", "task_id": "task1", "message": "Hoàn thành"}
            ],
            "sources": [{"source_title": "Tài liệu thử nghiệm"}], "warnings": ["Thông tin tham khảo"]
        }

    def test_can_persist_and_reopen(self):
        self.service.add(self.result, "Các triệu chứng là gì?")
        reopened = SQLiteService(self.path)
        found = reopened.history("demo-a")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["answer"], self.result["answer"])
        self.assertEqual(found[0]["agent_trace"], self.result["agent_trace"])
        self.assertEqual(reopened.latest("demo-a")["status"], "success")

    def test_session_isolation_and_latest(self):
        self.service.add(self.result, "Câu hỏi 1")
        second = dict(self.result, session_id="demo-b", answer="Trả lời B")
        self.service.add(second, "Câu hỏi B")
        self.assertEqual(self.service.latest()["session_id"], "demo-b")
        self.assertEqual(self.service.latest("demo-a")["session_id"], "demo-a")
        self.assertIsNone(self.service.latest("unknown"))
        self.assertEqual(self.service.history("demo-a")[0]["message"], "Câu hỏi 1")

    def test_returns_newest_first_and_applies_limit(self):
        self.service.add(self.result, "Lần 1")
        self.service.add(self.result, "Lần 2")
        self.assertEqual(self.service.history("demo-a", limit=1)[0]["message"], "Lần 2")

    def test_does_not_store_health_data(self):
        with closing(self.service._connect()) as connection:
            columns = [r[1] for r in connection.execute("PRAGMA table_info(chat_executions)")]
        self.assertNotIn("health_data", columns)
        self.service.add(self.result, "Hỏi sức khỏe")
        self.assertNotIn("health_data", str(self.service.history("demo-a")))

    def test_rejects_invalid_data(self):
        with self.assertRaises(ValueError):
            self.service.add({"session_id": "demo", "agent_trace": "wrong"})
        with self.assertRaises(ValueError):
            self.service.history("demo", limit=0)

    def test_health_check(self):
        self.assertEqual(self.service.health()["status"], "ok")

if __name__ == "__main__":
    unittest.main()

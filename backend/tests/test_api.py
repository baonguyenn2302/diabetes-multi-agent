"""Step 4 API tests using Flask test client and mock Coordinator (no ML DB required)."""
import unittest

from app import create_app


class MockCoordinator:
    def run(self, message, health_data=None, session_id=None):
        session_id = session_id or "generated-test-session"
        if "thiếu" in message:
            return {"session_id": session_id, "intent": "risk", "status": "needs_input",
                    "answer": "Cần bổ sung dữ liệu", "missing_fields": ["bmi"],
                    "agent_trace": [{"agent": "coordinator", "status": "needs_input", "message": "Thiếu đầu vào"}],
                    "sources": [], "warnings": []}
        return {"session_id": session_id, "intent": "knowledge", "status": "success",
                "answer": "Nội dung test có nguồn", "sources": [{"source_title": "Mock test"}],
                "warnings": [], "agent_trace": [
                    {"agent": "coordinator", "status": "success", "message": "Chọn Knowledge Agent"},
                    {"agent": "medical_knowledge_agent", "status": "running", "message": "Truy vấn"},
                    {"agent": "medical_knowledge_agent", "status": "success", "message": "Đã truy xuất"}]}


class TestAPI(unittest.TestCase):
    def setUp(self):
        app = create_app({"TESTING": True, "COORDINATOR_FACTORY": MockCoordinator})
        self.client = app.test_client()

    def test_chat_valid(self):
        response = self.client.post("/api/chat", json={"session_id": "demo", "message": "Tiểu đường là gì?"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["answer"], "Nội dung test có nguồn")
        self.assertEqual(data["session_id"], "demo")
        self.assertEqual(data["agent_trace"][-1]["status"], "success")

    def test_chat_requires_json(self):
        self.assertEqual(self.client.post("/api/chat", data="abc").status_code, 415)

    def test_chat_rejects_empty_message(self):
        self.assertEqual(self.client.post("/api/chat", json={"message": "  "}).status_code, 400)

    def test_chat_rejects_health_data_list(self):
        self.assertEqual(self.client.post("/api/chat", json={"message": "x", "health_data": []}).status_code, 400)

    def test_chat_rejects_session_id_object(self):
        self.assertEqual(self.client.post("/api/chat", json={"message": "x", "session_id": {}}).status_code, 400)

    def test_missing_input_is_normal_chat_response(self):
        resp = self.client.post("/api/chat", json={"message": "thiếu dữ liệu"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "needs_input")
        self.assertEqual(resp.get_json()["missing_fields"], ["bmi"])

    def test_actual_status_from_last_request(self):
        before = self.client.get("/api/agents/status").get_json()
        self.assertIsNone(before["latest_execution"])
        self.client.post("/api/chat", json={"session_id": "demo", "message": "Kiến thức"})
        after = self.client.get("/api/agents/status?session_id=demo").get_json()
        self.assertEqual(after["latest_execution"]["agent_trace"][1]["agent"], "medical_knowledge_agent")
        self.assertIsNone(self.client.get("/api/agents/status?session_id=unknown").get_json()["latest_execution"])

    def test_health_endpoint(self):
        from unittest.mock import patch
        with patch("routes.health.check_ollama", return_value={"status": "ok", "detail": "mock"}), \
             patch("routes.health.check_model", return_value={"status": "ok", "detail": "mock"}), \
             patch("routes.health.check_chroma", return_value={"status": "ok", "detail": "mock"}), \
             patch("routes.health.check_neo4j", return_value={"status": "unavailable", "detail": "mock"}):
            resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "degraded")
        self.assertEqual(resp.get_json()["services"]["neo4j"]["status"], "unavailable")

    def test_coordinator_exception_returns_503(self):
        class Broken:
            def run(self, **kwargs):
                raise RuntimeError("private testing failure")
        app = create_app({"TESTING": True, "COORDINATOR_FACTORY": Broken})
        with self.assertLogs(app.logger, level="ERROR"):
            resp = app.test_client().post("/api/chat", json={"message": "tiểu đường"})
        self.assertEqual(resp.status_code, 503)
        self.assertNotIn("private testing failure", resp.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()

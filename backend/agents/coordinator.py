"""Rule-based Coordinator MVP: no fabricated predictions, source citations or traces."""
from __future__ import annotations

from validators.safety_triage import triage

import json
from pathlib import Path
from uuid import uuid4

from schemas.agent_messages import make_task, validate_result

MODEL_METADATA = Path(__file__).resolve().parents[2] / "models" / "model_metadata.json"
RISK_KEYWORDS = ("đánh giá nguy cơ", "dự đoán nguy cơ", "ước tính nguy cơ", "nguy cơ mắc", "risk assessment", "predict risk")
SYMPTOM_KEYWORDS = ("triệu chứng", "dấu hiệu", "khát nước", "đi tiểu", "tiểu nhiều", "mệt mỏi", "symptom")
DISCLAIMER = "Thông tin chỉ dùng để tham khảo, không thay thế đánh giá của chuyên gia y tế."


class Coordinator:
    def __init__(self, agents=None, metadata_path=MODEL_METADATA, ollama=None):
        self.ollama = ollama
        self.agents = agents  # injected for tests; real registry is loaded on first call
        self.metadata_path = Path(metadata_path)

    def _agents(self):
        if self.agents is None:
            from agents.registry import build_registry
            self.agents = build_registry()
        return self.agents

    def _required_fields(self):
        try:
            with self.metadata_path.open(encoding="utf-8") as f:
                return json.load(f)["input_fields"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(f"Không đọc được metadata model: {exc}") from exc

    @staticmethod
    def classify(message):
        text = message.casefold()
        if any(word in text for word in RISK_KEYWORDS):
            return "risk"
        if any(word in text for word in SYMPTOM_KEYWORDS):
            return "symptoms"
        return "knowledge"

    @staticmethod
    def _rule_intent(message):
        text = message.casefold()
        if any(word in text for word in RISK_KEYWORDS):
            return "risk"
        if any(word in text for word in SYMPTOM_KEYWORDS):
            return "symptoms"
        # A few high-confidence, topic-specific cases need no LLM.
        if any(word in text for word in ("tiểu đường", "đái tháo đường", "diabetes")):
            return "knowledge"
        return None

    def _resolve_intent(self, message, trace, warnings):
        certain = self._rule_intent(message)
        if certain is not None:
            trace.append({"agent": "coordinator", "status": "success", "message": "Phân loại bằng rule: " + certain})
            return certain
        try:
            service = self.ollama
            if service is None:
                from services.ollama_service import OllamaService
                service = OllamaService()
            choice = service.classify_intent(message)
            trace.append({"agent": "coordinator", "status": "success", "message": "Phân loại ý định qua Ollama: " + choice})
            return choice
        except Exception as exc:
            warnings.append("Không thể phân loại bằng Ollama: " + str(exc))
            trace.append({"agent": "coordinator", "status": "error", "message": "Ollama không khả dụng để phân loại"})
            return "unresolved"

    def run(self, message, health_data=None, session_id=None):
        session_id = session_id or str(uuid4())
        trace, sources, warnings = [], [], [DISCLAIMER]
        alert = triage(message) if isinstance(message, str) else None
        if alert:
            trace.append({"agent": "coordinator", "status": "success",
                          "message": f"Luật an toàn: {alert['level']}"})
            return self._finish(session_id, "safety", alert["message"], trace, sources,
                                warnings, "safety_alert")
        if not isinstance(message, str) or not message.strip():
            return {"session_id": session_id, "answer": "Vui lòng nhập câu hỏi.",
                    "intent": "invalid", "agent_trace": trace, "sources": sources,
                    "warnings": warnings, "status": "invalid_input"}
        intent = self._resolve_intent(message, trace, warnings)
        if intent in ("out_of_scope", "unresolved"):
            return self._finish(session_id, intent, "Mình chỉ hỗ trợ thông tin về tiểu đường. Vui lòng hỏi rõ hơn về chủ đề này.", trace, sources, warnings, "success" if intent == "out_of_scope" else "error")
        if health_data is not None and not isinstance(health_data, dict):
            return self._finish(session_id, intent, "health_data phải là object hoặc null.", trace, sources, warnings, "invalid_input")
        if intent == "risk":
            try:
                fields = self._required_fields()
            except RuntimeError as exc:
                warnings.append(str(exc))
                return self._finish(session_id, intent, "Không thể đọc cấu hình dữ liệu của mô hình.", trace, sources, warnings, "error")
            missing = [field for field in fields if health_data is None or health_data.get(field) is None or health_data.get(field) == ""]
            if missing:
                trace.append({"agent": "coordinator", "status": "needs_input", "message": "Thiếu dữ liệu đầu vào; không gọi model."})
                result = self._finish(session_id, intent, "Cần bổ sung: " + ", ".join(missing), trace, sources, warnings, "needs_input")
                result["missing_fields"] = missing
                return result
            risk = self._invoke("risk_assessment_agent", "estimate_diabetes_risk", {"features": health_data}, session_id, trace)
            if risk["status"] != "success":
                return self._finish(session_id, intent, self._error_text(risk), trace, sources, warnings, risk["status"])
            prediction = risk.get("result") or {}
            intro = "Mô hình đã tạo kết quả ước tính: nhãn = {}, điểm đầu ra = {}. Không dùng kết quả này để chẩn đoán.".format(
                prediction.get("prediction"), prediction.get("probability"))
        else:
            intro = ""
        knowledge = self._invoke("medical_knowledge_agent", "retrieve_medical_knowledge", {"question": message}, session_id, trace)
        graph_symptoms = list(dict.fromkeys(
            source["symptom"]
            for source in (knowledge.get("result") or {}).get("sources", [])
            if isinstance(source, dict)
            and source.get("origin") in ("neo4j", "graph_csv")
            and isinstance(source.get("symptom"), str)
        )) if knowledge["status"] == "success" else []
        if knowledge["status"] == "success":
            sources = (knowledge.get("result") or {}).get("sources", [])
            if intent == "symptoms" and graph_symptoms:
                explanation = "Nguồn tri thức ghi nhận các biểu hiện: " + ", ".join(graph_symptoms) + "."
            else:
                # Only source-grounded excerpts; LLM summarization is added in Step 2.
                snippets = [s.get("excerpt", "")[:400] for s in sources[:4] if isinstance(s, dict) and s.get("excerpt")]
                explanation = "Trích đoạn nguồn tham khảo: " + " | ".join(snippets) if snippets else "Đã truy xuất nguồn nhưng chưa có trích đoạn để hiển thị."
        else:
            explanation = "Kho tri thức chưa cung cấp được thông tin phù hợp."
            warnings.append(self._error_text(knowledge))
        # A local LLM may rephrase source-grounded text, but must never invent sources.
        if knowledge["status"] == "success" and sources and not (intent == "symptoms" and graph_symptoms):
            try:
                service = self.ollama
                if service is None:
                    from services.ollama_service import OllamaService
                    service = OllamaService()
                summary = service.summarize(message, sources, intro)
                if summary:
                    explanation = summary
                    trace.append({"agent": "coordinator", "status": "success", "message": "Ollama tổng hợp dựa trên nguồn truy xuất"})
            except Exception as exc:
                warnings.append("Ollama không khả dụng; hiển thị trích đoạn gốc: " + str(exc))
                trace.append({"agent": "coordinator", "status": "error", "message": "Không thể tổng hợp bằng Ollama; sử dụng trích đoạn nguồn"})
        elif intent == "symptoms" and graph_symptoms:
            trace.append({"agent": "coordinator", "status": "success", "message": "Tổng hợp triệu chứng từ dữ liệu đồ thị có cấu trúc"})
        draft = (intro + " " + explanation).strip()
        answer = draft
        if intent in ("risk", "symptoms"):
            # Advisor reviews the ACTUAL draft, and its output controls the final answer.
            advisor = self._invoke("medical_advisor_agent", "review_advice",
                                   {"question": message, "draft": draft,
                                    "prediction": prediction if intent == "risk" else None,
                                    "sources": sources}, session_id, trace)
            if advisor["status"] == "success":
                review = advisor.get("result") or {}
                if isinstance(review.get("warnings"), list):
                    warnings.extend(w for w in review["warnings"] if isinstance(w, str))
                revised = review.get("revised_answer")
                if isinstance(revised, str) and revised.strip():
                    answer = revised.strip()
                elif review.get("approved") is False:
                    # A rejected draft must never leak through unchanged.
                    answer = "Nội dung tư vấn chưa vượt qua bước kiểm tra an toàn. Vui lòng tham khảo nhân viên y tế."
                    warnings.append("Advisor đã từ chối nội dung tư vấn.")
            else:
                # Fail closed: do not return unchecked generated medical advice.
                warnings.append("Chưa hoàn tất rà soát bởi Medical Advisor Agent.")
                answer = "Chưa thể cung cấp phần tư vấn đã được rà soát an toàn. Vui lòng thử lại sau hoặc tham khảo nhân viên y tế."
                return self._finish(session_id, intent, answer, trace, sources, warnings,
                                    "error" if advisor["status"] == "error" else advisor["status"])
        return self._finish(session_id, intent, answer, trace, sources, warnings,
                            "success" if knowledge["status"] == "success" else knowledge["status"])

    def _invoke(self, name, action, payload, session_id, trace):
        task = make_task(session_id, name, action, payload)
        agent = self._agents().get(name)
        trace.append({"agent": name, "status": "running", "task_id": task["task_id"], "message": action})
        if agent is None:
            response = {"session_id": session_id, "task_id": task["task_id"], "agent": name, "status": "error", "result": {},
                        "error": {"code": "agent_unavailable", "message": "Agent chưa được triển khai"}}
        else:
            try:
                response = validate_result(agent.run(task), task)
            except Exception as exc:
                response = {"session_id": session_id, "task_id": task["task_id"], "agent": name, "status": "error", "result": {},
                            "error": {"code": "agent_failed", "message": str(exc)}}
        trace.append({"agent": name, "status": response["status"], "task_id": task["task_id"],
                      "message": "Hoàn thành" if response["status"] == "success" else self._error_text(response)})
        return response

    @staticmethod
    def _error_text(response):
        error = response.get("error") or {}
        return error.get("message", response.get("status", "unknown")) if isinstance(error, dict) else str(error)

    @staticmethod
    def _finish(session_id, intent, answer, trace, sources, warnings, status):
        return {"session_id": session_id, "intent": intent, "answer": answer, "status": status,
                "agent_trace": trace, "sources": sources, "warnings": warnings}

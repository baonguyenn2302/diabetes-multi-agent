"""POST /api/chat: request validation and dispatch only; no agent business logic."""
from __future__ import annotations
import re
from flask import Blueprint, current_app, jsonify, request

chat_bp = Blueprint("chat", __name__)
_SESSION = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def _error(detail, status_code=400):
    return jsonify({"status": "invalid_input" if status_code < 500 else "error",
                    "error": detail}), status_code


@chat_bp.post("/api/chat")
def chat():
    if not request.is_json:
        return _error("Content-Type phải là application/json.", 415)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("JSON body phải là object hợp lệ.")
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > 4000:
        return _error("message phải là chuỗi không rỗng, tối đa 4000 ký tự.")
    health_data = payload.get("health_data")
    if health_data is not None and not isinstance(health_data, dict):
        return _error("health_data phải là object hoặc null.")
    session_id = payload.get("session_id")
    if session_id is not None and (not isinstance(session_id, str) or not _SESSION.fullmatch(session_id)):
        return _error("session_id chỉ cho phép chữ, số, dấu gạch, chấm hoặc gạch dưới, tối đa 128 ký tự.")
    try:
        factory = current_app.config.get("COORDINATOR_FACTORY")
        if factory is None:
            # Import only when handling a request; prevents eager TensorFlow/ChromaDB initialization.
            from agents.coordinator import Coordinator
            coordinator = Coordinator()
        else:
            coordinator = factory()
        result = coordinator.run(message=message.strip(), health_data=health_data, session_id=session_id)
        if not isinstance(result, dict) or not isinstance(result.get("agent_trace"), list):
            raise ValueError("Coordinator trả kết quả không đúng contract")
        # Persistence is best-effort: a database issue must not fabricate or
        # erase an otherwise valid Coordinator result.
        try:
            current_app.extensions["sqlite_service"].add(result, message=message.strip())
        except Exception:
            current_app.logger.exception("SQLite persistence failed")
            result.setdefault("warnings", []).append("Không lưu được lịch sử phiên vào SQLite.")
        # Missing user input / insufficient evidence are normal chatbot states, not HTTP errors.
        return jsonify(result), 200
    except Exception:
        # Do not expose traceback, secrets, model details or sensitive user input via API.
        current_app.logger.exception("/api/chat processing failed")
        return jsonify({"status": "error", "answer": "Hệ thống tạm thời chưa xử lý được yêu cầu.",
                        "agent_trace": [], "sources": [], "warnings": ["Lỗi dịch vụ backend, hãy kiểm tra log trên terminal."]}), 503

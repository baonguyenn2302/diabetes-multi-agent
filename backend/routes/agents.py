"""GET /api/agents/status: latest persisted execution trace."""
import re
from flask import Blueprint, current_app, jsonify, request
_SESSION = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")

agents_bp = Blueprint("agents", __name__)

@agents_bp.get("/api/agents/status")
def agents_status():
    session_id = request.args.get("session_id")
    if session_id is not None and not _SESSION.fullmatch(session_id):
        return jsonify({"status": "invalid_input", "error": "session_id không hợp lệ"}), 400
    try:
        last = current_app.extensions["sqlite_service"].latest(session_id=session_id)
    except Exception:
        current_app.logger.exception("Failed to read latest agent trace")
        return jsonify({"status": "error", "error": "Không đọc được Agent Trace"}), 503
    # None means no persisted execution matching the optional session_id.
    return jsonify({
        "status": "success",
        "tracking": "sqlite_persistent",
        "session_id": session_id,
        "latest_execution": last,
        "agents": [
            {"name": "coordinator", "role": "Điều phối ý định và các Agent"},
            {"name": "risk_assessment_agent", "role": "Gọi Keras model"},
            {"name": "medical_knowledge_agent", "role": "Truy xuất ChromaDB/Neo4j"},
            {"name": "medical_advisor_agent", "role": "Rà soát nội dung"},
        ],
        "note": "Danh sách vai trò khai báo, không khẳng định dịch vụ đang chạy. latest_execution là trace thực tế của request gần nhất, hoặc null nếu chưa có.",
    })

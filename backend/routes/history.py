"""Read a local demo session's stored chat/agent execution history."""
from __future__ import annotations
import re
from flask import Blueprint, current_app, jsonify, request

history_bp = Blueprint("history", __name__)
_SESSION = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


@history_bp.get("/api/history")
def history():
    sid = request.args.get("session_id", "")
    if not _SESSION.fullmatch(sid):
        return jsonify({"status": "invalid_input", "error": "session_id không hợp lệ hoặc bị thiếu"}), 400
    raw = request.args.get("limit", "20")
    try:
        limit = int(raw)
        if not 1 <= limit <= 100:
            raise ValueError()
    except ValueError:
        return jsonify({"status": "invalid_input", "error": "limit phải là số nguyên từ 1 đến 100"}), 400
    try:
        entries = current_app.extensions["sqlite_service"].history(sid, limit)
    except Exception:
        current_app.logger.exception("Cannot query chat history")
        return jsonify({"status": "error", "error": "Không đọc được lịch sử SQLite"}), 503
    return jsonify({"status": "success", "session_id": sid,
                    "count": len(entries), "history": entries}), 200

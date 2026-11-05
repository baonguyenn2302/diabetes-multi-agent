"""GET /api/health: dependency checks, with explicit probe depth.
Default is lightweight, no forced TensorFlow load or embedding downloads.
Use ?deep=1 for actual model and vector DB functional checks.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from urllib import request as urllib_request
from flask import Blueprint, current_app, jsonify, request

health_bp = Blueprint("health", __name__)
ROOT = Path(__file__).resolve().parents[2]


def check_ollama(base_url, model, timeout=2):
    if not (base_url.startswith("http://127.0.0.1:") or base_url.startswith("http://localhost:")):
        return {"status": "unavailable", "detail": "Ollama phải chạy local"}
    try:
        with urllib_request.urlopen(base_url.rstrip("/") + "/api/tags", timeout=timeout) as resp:
            names = [m.get("name", "") for m in json.load(resp).get("models", [])]
        if model not in names:
            return {"status": "unavailable", "detail": "Ollama hoạt động nhưng chưa thấy model cấu hình: " + model}
        return {"status": "ok", "detail": "Ollama local có model: " + model}
    except Exception:
        return {"status": "unavailable", "detail": "Không gọi được Ollama /api/tags"}


def check_model(deep=False):
    model_dir = ROOT / "models"
    metadata = model_dir / "model_metadata.json"
    if not metadata.is_file():
        return {"status": "unavailable", "detail": "Không thấy model_metadata.json"}
    try:
        info = json.loads(metadata.read_text(encoding="utf-8"))
        model_file = info.get("model_file", "")
        ready = (model_dir / "preprocessor.pkl").is_file() and bool(model_file) and (model_dir / model_file).is_file()
    except Exception:
        ready = False
    if not ready:
        return {"status": "unavailable", "detail": "Thiếu file model hoặc preprocessor"}
    if not deep:
        return {"status": "not_checked", "detail": "Có file model, chưa thử load. Dùng ?deep=1"}
    try:
        from services.model_service import ModelService
        return ModelService().health()
    except Exception:
        return {"status": "unavailable", "detail": "Lỗi khi kiểm tra model; xem log backend"}


def check_chroma(path, deep=False):
    directory = Path(path)
    if not (directory / "chroma.sqlite3").is_file():
        return {"status": "unavailable", "detail": "Chưa thấy chroma.sqlite3 tại CHROMA_PATH"}
    if not deep:
        return {"status": "not_checked", "detail": "Có file ChromaDB; chưa thử query. Dùng ?deep=1"}
    try:
        from services.chroma_service import KnowledgeStore
        return KnowledgeStore(persist_dir=directory).health()
    except Exception:
        return {"status": "unavailable", "detail": "Lỗi khi kiểm tra ChromaDB; xem log backend"}


def check_neo4j(deep=False):
    if not os.getenv("NEO4J_URI", ""):
        return {"status": "unavailable", "detail": "Chưa cấu hình NEO4J_URI"}
    if not deep:
        return {"status": "not_checked", "detail": "Đã cấu hình Neo4j; chưa thử kết nối. Dùng ?deep=1"}
    try:
        from services.neo4j_service import Neo4jService
        svc = Neo4jService()
        try:
            return svc.health()
        finally:
            svc.close()
    except Exception:
        return {"status": "unavailable", "detail": "Lỗi khi kiểm tra Neo4j; xem log backend"}


@health_bp.get("/api/health")
def health():
    deep = request.args.get("deep") == "1"
    cfg = current_app.config
    status = {
        "flask": {"status": "ok", "detail": "API đang trả lời"},
        "ollama": check_ollama(cfg["OLLAMA_BASE_URL"], cfg["OLLAMA_MODEL"]),
        "keras_model": check_model(deep),
        "chromadb": check_chroma(cfg["CHROMA_PATH"], deep),
        "neo4j": check_neo4j(deep),
        "sqlite": current_app.extensions["sqlite_service"].health(),
    }
    return jsonify({"status": "ok" if all(item["status"] == "ok" for item in status.values()) else "degraded",
                    "check_mode": "deep" if deep else "lightweight", "services": status}), 200

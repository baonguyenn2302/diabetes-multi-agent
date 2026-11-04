"""Medical Knowledge Agent: truy xuất đoạn tri thức có nguồn từ ChromaDB.

Agent không tự sinh câu trả lời. Nó trả về các đoạn gốc kèm nguồn để tầng
tổng hợp trình bày. Nếu không có đoạn đủ liên quan, trả về insufficient_evidence.
"""
from __future__ import annotations

from typing import Any

from services.chroma_service import KnowledgeStore, KnowledgeUnavailableError

AGENT_NAME = "medical_knowledge_agent"

# Khoảng cách cosine tối đa để coi một đoạn là liên quan.
# Giá trị tạm thời, sẽ hiệu chỉnh lại sau khi có bộ câu hỏi kiểm thử.
MAX_DISTANCE = 0.50
TOP_K = 4
EXCERPT_CHARS = 400

DISCLAIMER = (
    "Thông tin tham khảo từ tài liệu y khoa đã được nạp, "
    "không thay thế chẩn đoán hoặc tư vấn của bác sĩ."
)

STATUS_SUCCESS = "success"
STATUS_INSUFFICIENT = "insufficient_evidence"
STATUS_ERROR = "error"


class MedicalKnowledgeAgent:
    name = AGENT_NAME

    def __init__(self, store: Any | None = None, max_distance: float = MAX_DISTANCE):
        self.store = store if store is not None else KnowledgeStore()
        self.max_distance = max_distance

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        session_id = task.get("session_id")
        task_id = task.get("task_id")
        question = ((task.get("input") or {}).get("question") or "").strip()

        if not question:
            return self._build(session_id, task_id, STATUS_ERROR, error={
                "code": "missing_question",
                "message": "Thiếu câu hỏi",
            })

        try:
            hits = self.store.query(question, top_k=TOP_K)
        except KnowledgeUnavailableError as exc:
            return self._build(session_id, task_id, STATUS_ERROR, error={
                "code": "knowledge_unavailable",
                "message": str(exc),
            })
        except Exception as exc:
            return self._build(session_id, task_id, STATUS_ERROR, error={
                "code": "retrieval_failed",
                "message": str(exc),
            })

        relevant = [h for h in hits if h["distance"] <= self.max_distance]

        if not relevant:
            return self._build(session_id, task_id, STATUS_INSUFFICIENT, result={
                "message": "Không tìm thấy tài liệu đủ liên quan đến câu hỏi trong kho tri thức.",
                "best_distance": round(hits[0]["distance"], 3) if hits else None,
                "max_distance": self.max_distance,
                "sources": [],
                "disclaimer": DISCLAIMER,
            })

        sources = [
            {
                "source_id": h.get("source_id", ""),
                "source_title": h.get("source_title", ""),
                "publisher": h.get("publisher", ""),
                "date": h.get("date", ""),
                "url": h.get("url", ""),
                "section": h.get("section", ""),
                "subsection": h.get("subsection", ""),
                "distance": round(h["distance"], 3),
                "excerpt": h["document"][:EXCERPT_CHARS],
            }
            for h in relevant
        ]
        return self._build(session_id, task_id, STATUS_SUCCESS, result={
            "sources": sources,
            "max_distance": self.max_distance,
            "disclaimer": DISCLAIMER,
        })

    def _build(self, session_id, task_id, status, result=None, error=None) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "task_id": task_id,
            "agent": AGENT_NAME,
            "status": status,
            "result": result or {},
            "error": error,
        }
"""Medical Knowledge Agent: truy xuất đoạn tri thức có nguồn từ ChromaDB và Neo4j.

Agent không tự sinh câu trả lời. Khi Neo4j chưa cấu hình hoặc không khả dụng,
Agent dùng triples.csv đã kiểm tra trong repository và ghi đúng nguồn dữ liệu.
"""
from __future__ import annotations

import csv
from typing import Any

from services.chroma_service import KnowledgeStore, KnowledgeUnavailableError
from services.graph_knowledge import lookup_local_symptoms, lookup_symptoms
from services.neo4j_service import Neo4jService, Neo4jUnavailableError

AGENT_NAME = "medical_knowledge_agent"

# Khoảng cách cosine tối đa để coi một đoạn là liên quan (hiệu chỉnh trên bộ câu hỏi thử).
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

EXCERPT_CHARS = 400
# Nội dung đầy đủ đưa cho LLM tổng hợp. Chunk tối đa khoảng 900 ký tự + tiêu đề,
# nhưng một đoạn văn dài hơn vẫn không bị cắt khi chunk, nên dùng ngưỡng rộng hơn.
MAX_CONTEXT_CHARS = 1500


class MedicalKnowledgeAgent:
    name = AGENT_NAME

    def __init__(self, store: Any | None = None, max_distance: float = MAX_DISTANCE,
                 graph: Neo4jService | None = None):
        self.store = store if store is not None else KnowledgeStore()
        self.max_distance = max_distance
        self.graph = graph if graph is not None else Neo4jService()

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
        sources = [self._vector_source(h) for h in relevant]
        graph_sources, warnings = self._graph_sources(question)
        sources += graph_sources

        if not sources:
            return self._build(session_id, task_id, STATUS_INSUFFICIENT, result={
                "message": "Không tìm thấy tài liệu đủ liên quan đến câu hỏi trong kho tri thức.",
                "best_distance": round(hits[0]["distance"], 3) if hits else None,
                "max_distance": self.max_distance,
                "sources": [],
                "warnings": warnings,
                "disclaimer": DISCLAIMER,
            })

        return self._build(session_id, task_id, STATUS_SUCCESS, result={
            "sources": sources,
            "max_distance": self.max_distance,
            "warnings": warnings,
            "disclaimer": DISCLAIMER,
        })

    @staticmethod
    def _vector_source(h: dict[str, Any]) -> dict[str, Any]:
        return {
            "origin": "chroma",
            "source_id": h.get("source_id", ""),
            "source_title": h.get("source_title", ""),
            "publisher": h.get("publisher", ""),
            "date": h.get("date", ""),
            "url": h.get("url", ""),
            "section": h.get("section", ""),
            "subsection": h.get("subsection", ""),
            "distance": round(h["distance"], 3),
            "excerpt": h["document"][:EXCERPT_CHARS],
            "full_text": h["document"][:MAX_CONTEXT_CHARS],
        }

    def _graph_sources(self, question: str) -> tuple[list[dict[str, Any]], list[str]]:
        warnings: list[str] = []
        if self.graph.configured:
            try:
                rows = lookup_symptoms(self.graph, question)
            except Neo4jUnavailableError as exc:
                warnings.append(f"Neo4j không khả dụng, dùng triples.csv: {exc}")
            else:
                if rows:
                    return self._format_graph_sources(rows, "neo4j"), warnings

        try:
            rows = lookup_local_symptoms(question)
        except (OSError, csv.Error) as exc:
            warnings.append(f"Không đọc được kho triệu chứng triples.csv: {exc}")
            return [], warnings
        return self._format_graph_sources(rows, "graph_csv"), warnings

    @staticmethod
    def _format_graph_sources(rows: list[dict[str, Any]], origin: str) -> list[dict[str, Any]]:
        sources = [{
            "origin": origin,
            "symptom": r["name"],
            "source_id": r["source_id"],
            "source_title": r["source_title"],
            "publisher": "",
            "date": "",
            "url": "",
            "section": r["section"],
            "subsection": "",
            "distance": None,
            "excerpt": f"Đái tháo đường típ 2 có triệu chứng: {r['name']} ({r['evidence']})",
        } for r in rows]
        return sources

    def _build(self, session_id, task_id, status, result=None, error=None) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "task_id": task_id,
            "agent": AGENT_NAME,
            "status": status,
            "result": result or {},
            "error": error,
        }
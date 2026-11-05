"""Medical Advisor MVP: deterministic review, not medical diagnosis.

Checks a draft produced by other agents and returns a *review* to Coordinator.
No clinical rules, prescriptions, external LLM, or invented source material.
"""
from __future__ import annotations

import re
from typing import Any

from agents.base_agent import BaseAgent

AGENT_NAME = "medical_advisor_agent"
DISCLAIMER = "Đây chỉ là thông tin tham khảo, không thay thế đánh giá của chuyên gia y tế."
SAFE_FALLBACK = (
    "Hệ thống chưa thể cung cấp nội dung tư vấn đã được kiểm tra an toàn cho yêu cầu này. "
    "Vui lòng tham khảo nhân viên y tế nếu bạn lo ngại về tình trạng sức khỏe."
)
# Match *affirmative* claims, not a generic reference to diabetes or a negated diagnosis.
DIAGNOSIS_PATTERNS = (
    re.compile(r"\b(?:bạn|anh|chị|em)\s+(?:chắc chắn\s+)?(?:đã\s+)?(?:mắc|bị)\s+(?:bệnh\s+)?(?:tiểu đường|đái tháo đường|diabetes)\b", re.I),
    re.compile(r"\b(?:bạn|anh|chị|em)\s+(?:chắc chắn\s+)?không\s+(?:mắc|bị)\s+(?:bệnh\s+)?(?:tiểu đường|đái tháo đường|diabetes)\b", re.I),
    re.compile(r"\b(?:kết luận|chẩn đoán)\s*:\s*(?:bạn\s+)?(?:mắc|bị|không mắc|không bị)\b", re.I),
)
# Clear unsafe instructions only. Deliberately avoid prescribing a general clinical rule.
TREATMENT_PATTERNS = (
    re.compile(r"\b(?:hãy|nên|phải)\s+(?:tự\s+)?(?:uống|dùng|tiêm)\s+\d+(?:[.,]\d+)?\s*(?:mg|ml|đơn vị|iu)\b", re.I),
    re.compile(r"\b(?:hãy|nên|phải)\s+(?:ngừng|bỏ|tăng|giảm)\s+(?:thuốc|liều thuốc|liều insulin)\b", re.I),
)


class MedicalAdvisorAgent(BaseAgent):
    name = AGENT_NAME

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        session_id = task.get("session_id") if isinstance(task, dict) else None
        task_id = task.get("task_id") if isinstance(task, dict) else None
        if not isinstance(task, dict) or task.get("task") != "review_advice":
            return self._build(session_id, task_id, "invalid_input", error={
                "code": "invalid_task", "message": "Advisor chỉ hỗ trợ task review_advice"
            })
        payload = task.get("input")
        if not isinstance(payload, dict):
            return self._build(session_id, task_id, "invalid_input", error={
                "code": "invalid_payload", "message": "input phải là object"
            })
        question, draft = payload.get("question"), payload.get("draft")
        if not isinstance(question, str) or not question.strip() or not isinstance(draft, str):
            return self._build(session_id, task_id, "invalid_input", error={
                "code": "invalid_content", "message": "question và draft phải là chuỗi; question không được rỗng"
            })
        if not draft.strip():
            return self._build(session_id, task_id, "needs_input", result={
                "approved": False, "revised_answer": "", "warnings": ["Chưa có nội dung để rà soát."],
                "review_flags": ["empty_draft"]
            })

        flags: list[str] = []
        warnings: list[str] = []
        if any(p.search(draft) for p in DIAGNOSIS_PATTERNS):
            flags.append("diagnostic_claim")
            warnings.append("Nội dung có khẳng định tình trạng bệnh vượt quá giới hạn mô hình demo.")
        if any(p.search(draft) for p in TREATMENT_PATTERNS):
            flags.append("treatment_instruction")
            warnings.append("Nội dung có chỉ dẫn thuốc/liều dùng không phù hợp để tư vấn tự động.")

        # Source grounding is checked by the Coordinator and Knowledge Agent.
        # A simple regex filter cannot certify medical accuracy.
        approved = not flags
        revised = draft.strip() if approved else SAFE_FALLBACK
        if DISCLAIMER.casefold() not in revised.casefold():
            revised = revised.rstrip() + "\n\n" + DISCLAIMER
        return self._build(session_id, task_id, "success", result={
            "approved": approved,
            "revised_answer": revised,
            "warnings": warnings,
            "review_flags": flags,
            "review_method": "rule_based_mvp",
        })

    @staticmethod
    def _build(session_id: Any, task_id: Any, status: str, result: dict | None = None,
               error: dict | None = None) -> dict:
        return {"session_id": session_id, "task_id": task_id, "agent": AGENT_NAME,
                "status": status, "result": result or {}, "error": error}

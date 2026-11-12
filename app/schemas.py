"""Schema dùng chung cho toàn hệ thống.

Mọi agent trả về AgentMessage: m = (id, agent, status, payload, evidence, version)
(theo mục 6.1 của tài liệu kiến trúc).
Nguyên tắc 'failure awareness': agent KHÔNG ném lỗi ra ngoài mà trả status="error".
"""
from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    request_id: str
    agent: str
    status: str                                   # "ok" | "error"
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    version: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, request_id: str, agent: str, payload: dict | None = None,
           evidence: list | None = None, version: str | None = None) -> "AgentMessage":
        return cls(request_id=request_id, agent=agent, status="ok",
                   payload=payload or {}, evidence=evidence or [], version=version)

    @classmethod
    def fail(cls, request_id: str, agent: str, error: str,
             version: str | None = None) -> "AgentMessage":
        return cls(request_id=request_id, agent=agent, status="error",
                   error=error, version=version)


class PatientRequest(BaseModel):
    features: dict[str, Any]
    question: Optional[str] = None


class ChatRequest(BaseModel):
    question: str
    context: Optional[dict[str, Any]] = None   # Chỉ số bệnh nhân (nếu liên kết từ trang đánh giá)
    history: Optional[list[dict[str, str]]] = None


class ChatResponse(BaseModel):
    request_id: str
    status: str = "ok"                          # "ok" | "partial" | "error"
    answer: str                                 # Câu trả lời hội thoại có cấu trúc
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    has_patient_context: bool = False
    errors: list[dict[str, Any]] = Field(default_factory=list)


"""Risk Assessment Agent: kiểm tra đầu vào, gọi model Keras, trả kết quả có cấu trúc.

Agent chỉ trả số liệu của model, không diễn giải thành chẩn đoán.
"""
from __future__ import annotations

from typing import Any

from services.model_service import ModelService, ModelUnavailableError
from validators.health_input import (
    STATUS_INVALID_INPUT,
    STATUS_NEEDS_INPUT,
    STATUS_SUCCESS,
    validate_health_input,
)

AGENT_NAME = "risk_assessment_agent"
STATUS_ERROR = "error"


class RiskAssessmentAgent:
    name = AGENT_NAME

    def __init__(self, model_service: ModelService | None = None):
        self.model_service = model_service or ModelService()

    def run(self, task: dict[str, Any]) -> dict[str, Any]:
        session_id = task.get("session_id")
        task_id = task.get("task_id")
        features = (task.get("input") or {}).get("features")

        try:
            self.model_service.load()
        except ModelUnavailableError as exc:
            return self._build(session_id, task_id, STATUS_ERROR, error={
                "code": "model_unavailable",
                "message": str(exc),
            })

        metadata = self.model_service.metadata
        check = validate_health_input(features, metadata)

        if check["status"] == STATUS_NEEDS_INPUT:
            return self._build(session_id, task_id, STATUS_NEEDS_INPUT, result={
                "missing_fields": check["missing_fields"],
                "errors": check["errors"],
            })

        if check["status"] == STATUS_INVALID_INPUT:
            return self._build(session_id, task_id, STATUS_INVALID_INPUT, error={
                "code": "invalid_input",
                "message": "Dữ liệu đầu vào không hợp lệ",
                "fields": check["errors"],
            })

        try:
            probability = self.model_service.predict_probability(check["clean_features"])
        except Exception as exc:  # lỗi kỹ thuật không được làm sập backend
            return self._build(session_id, task_id, STATUS_ERROR, error={
                "code": "prediction_failed",
                "message": str(exc),
            })

        threshold = metadata["metrics"]["threshold"]
        return self._build(session_id, task_id, STATUS_SUCCESS, result={
            "prediction": int(probability >= threshold),
            "probability": round(probability, 4),
            "threshold": threshold,
            "model_metrics": metadata["metrics"],
            "trained_on": metadata.get("trained_on"),
            "limitations": metadata["limitations"],
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
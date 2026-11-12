"""API FastAPI: lớp giao tiếp của hệ thống (Layer 2 trong tài liệu kiến trúc).

Chạy:  uvicorn app.api:app --reload      (tài liệu: http://localhost:8000/docs)
Endpoint:
  GET  /health          kiểm tra dịch vụ
  POST /assess          phân tích một bệnh nhân
  GET  /audit/summary   thống kê vận hành từ logs/audit.jsonl
"""
from functools import lru_cache
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import PatientRequest, ChatRequest
from app.service import assess, chat

app = FastAPI(
    title="Diabetes MAS",
    version="0.8.0",
    description="Prototype học tập. Kết quả KHÔNG phải chẩn đoán xác định và không thay thế bác sĩ.",
)


@lru_cache(maxsize=1)
def _build_coordinator():
    # lru_cache không lưu exception, nên nếu lần đầu lỗi thì lần sau vẫn thử lại
    from app.coordinator import build_default_coordinator
    return build_default_coordinator()


def get_coordinator():
    try:
        return _build_coordinator()
    except Exception as e:
        raise HTTPException(status_code=503,
                            detail=f"Chưa khởi tạo được hệ thống: {type(e).__name__}: {e}")


@app.get("/health")
def health():
    return {"status": "ok", "service": "diabetes-mas"}


@app.post("/assess")
def assess_endpoint(req: PatientRequest, coord=Depends(get_coordinator)):
    code, body = assess(coord, req.features, req.question)
    return JSONResponse(status_code=code, content=body)


@app.get("/audit/summary")
def audit_summary(last: Optional[int] = None):
    from app.agents.monitoring_agent import MonitoringAgent
    return MonitoringAgent().summary(last_n=last)


@app.post("/chat")
def chat_endpoint(req: ChatRequest, coord=Depends(get_coordinator)):
    code, body = chat(coord, req.question, req.context)
    return JSONResponse(status_code=code, content=body)

"""Logic dùng chung cho API: chuyển kết quả Coordinator thành mã HTTP.

Tách riêng khỏi FastAPI để kiểm thử được mà không cần cài fastapi.
"""
from typing import Any, Optional

STATUS_CODE = {"ok": 200, "partial": 200, "validation_error": 422, "error": 500}


def assess(coord, features: Any, question: Optional[str] = None):
    """Trả về (mã HTTP, kết quả). Kết quả partial vẫn là 200 vì đã có một phần đáng tin."""
    res = coord.handle(features, question)
    return STATUS_CODE.get(res.get("status"), 500), res


def chat(coord, question: str, context: Optional[dict] = None):
    """Trả về (mã HTTP, kết quả chat). Chỉ gọi KG Agent."""
    res = coord.handle_chat(question, context)
    return STATUS_CODE.get(res.get("status"), 500), res

"""Patient Data Agent: kiểm tra và chuẩn hóa dữ liệu đầu vào của bệnh nhân.

Input : dict thô (đúng tên cột trong app/features.py)
Output: AgentMessage
  - ok   : payload = {"features": {...đã chuẩn hóa...}, "ignored_fields": [...]}
  - error: payload = {"errors": [...]} và error = mô tả gộp
Agent không ném lỗi ra ngoài (failure awareness).
"""
import math
from typing import Any, Optional

from app.schemas import AgentMessage
from app.features import (FEATURE_NAMES, NUMERIC_FEATURES, BINARY_FEATURES,
                          CATEGORICAL_FEATURES, ALLOWED_CATEGORIES, VALUE_RANGES)


def _to_float(v: Any) -> Optional[float]:
    """Chuyển sang số thực hữu hạn; bool, chuỗi không phải số, NaN/inf đều trả về None."""
    if isinstance(v, bool):
        return None
    try:
        x = float(str(v).strip().replace(",", ".")) if isinstance(v, str) else float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _canonical(feature: str, v: Any) -> Optional[str]:
    """Đưa giá trị categorical về đúng dạng trong dataset (không phân biệt hoa thường)."""
    if not isinstance(v, str):
        return None
    key = v.strip().lower()
    for allowed in ALLOWED_CATEGORIES[feature]:
        if allowed.lower() == key:
            return allowed
    return None


class PatientDataAgent:
    NAME = "PatientDataAgent"
    VERSION = "data_v1"

    def run(self, request_id: str, raw: Any) -> AgentMessage:
        try:
            return self._validate(request_id, raw)
        except Exception as e:
            return AgentMessage.fail(request_id, self.NAME, f"{type(e).__name__}: {e}", self.VERSION)

    def _validate(self, request_id: str, raw: Any) -> AgentMessage:
        if not isinstance(raw, dict):
            return AgentMessage.fail(request_id, self.NAME,
                                     "Dữ liệu đầu vào phải là một đối tượng (dict)", self.VERSION)
        errors, clean = [], {}
        for f in FEATURE_NAMES:
            v = raw.get(f)
            if v is None or (isinstance(v, str) and not v.strip()):
                errors.append(f"Thiếu feature: {f}")
            elif f in CATEGORICAL_FEATURES:
                c = _canonical(f, v)
                if c is None:
                    errors.append(f"{f}={v!r} không hợp lệ, phải thuộc {ALLOWED_CATEGORIES[f]}")
                else:
                    clean[f] = c
            elif f in BINARY_FEATURES:
                x = None if isinstance(v, bool) else _to_float(v)
                if x is None or x not in (0.0, 1.0):
                    errors.append(f"{f} phải là 0 hoặc 1, nhận được {v!r}")
                else:
                    clean[f] = int(x)
            elif f in NUMERIC_FEATURES:
                x = _to_float(v)
                lo, hi = VALUE_RANGES[f]
                if x is None:
                    errors.append(f"{f} phải là số, nhận được {v!r}")
                elif not lo <= x <= hi:
                    errors.append(f"{f}={x:g} nằm ngoài khoảng hợp lý [{lo}, {hi}]")
                else:
                    clean[f] = x
        if errors:
            return AgentMessage(request_id=request_id, agent=self.NAME, status="error",
                                payload={"errors": errors}, error="; ".join(errors),
                                version=self.VERSION)
        ignored = sorted(k for k in raw if k not in FEATURE_NAMES)
        return AgentMessage.ok(request_id, self.NAME,
                               payload={"features": clean, "ignored_fields": ignored},
                               version=self.VERSION)

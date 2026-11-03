"""Kiểm tra dữ liệu đầu vào sức khỏe theo model_metadata.json.

Không tự điền giá trị thiếu và không suy đoán giá trị sai.
"""
from __future__ import annotations

import math
from typing import Any

STATUS_SUCCESS = "success"
STATUS_NEEDS_INPUT = "needs_input"
STATUS_INVALID_INPUT = "invalid_input"

BINARY_FIELDS = {"hypertension", "heart_disease"}
MIN_AGE = 18


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def validate_health_input(features: dict[str, Any] | None, metadata: dict[str, Any]) -> dict[str, Any]:
    """Trả về dict gồm: status, clean_features, missing_fields, errors."""
    input_fields = metadata["input_fields"]

    if not isinstance(features, dict):
        return {
            "status": STATUS_NEEDS_INPUT,
            "clean_features": {},
            "missing_fields": list(input_fields),
            "errors": {},
        }

    categorical_values = metadata["categorical_values"]
    numeric_ranges = metadata["numeric_ranges"]
    units = metadata.get("units", {})

    missing: list[str] = []
    errors: dict[str, str] = {}
    clean: dict[str, Any] = {}

    for field in input_fields:
        value = features.get(field)
        if _is_missing(value):
            missing.append(field)
            continue

        # Trường phân loại: phải khớp đúng giá trị lúc huấn luyện
        if field in categorical_values:
            text = str(value).strip()
            if text in categorical_values[field]:
                clean[field] = text
            else:
                errors[field] = f"Giá trị phải thuộc {categorical_values[field]}"
            continue

        # Trường số
        if isinstance(value, bool):
            errors[field] = "Phải là số, không phải giá trị logic"
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            errors[field] = "Phải là số"
            continue
        if not math.isfinite(number):
            errors[field] = "Giá trị không hợp lệ"
            continue

        if field in BINARY_FIELDS and number not in (0.0, 1.0):
            errors[field] = "Chỉ nhận 0 hoặc 1"
            continue

        if field == "age" and number < MIN_AGE:
            errors[field] = "Hệ thống chỉ hỗ trợ người từ 18 tuổi trở lên"
            continue

        low, high = numeric_ranges[field]
        if not (low <= number <= high):
            unit = units.get(field, "")
            errors[field] = f"Ngoài khoảng dữ liệu huấn luyện [{low}, {high}] {unit}".strip()
            continue

        clean[field] = number

    if missing:
        return {
            "status": STATUS_NEEDS_INPUT,
            "clean_features": {},
            "missing_fields": missing,
            "errors": errors,
        }
    if errors:
        return {
            "status": STATUS_INVALID_INPUT,
            "clean_features": {},
            "missing_fields": [],
            "errors": errors,
        }
    return {
        "status": STATUS_SUCCESS,
        "clean_features": clean,
        "missing_fields": [],
        "errors": {},
    }
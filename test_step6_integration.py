"""Step 6 smoke test for the diabetes multi-agent demo.

Run from repository root or backend: python path/to/test_step6_integration.py
Requires Flask at http://127.0.0.1:5000, local Ollama and project services.
Uses a de-identified row from the project's existing dataset and validates it
against the model's metadata. Does not hardcode model feature values or train.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:5000"
REPO = Path(__file__).resolve().parent
if not (REPO / "models" / "model_metadata.json").is_file():
    REPO = REPO.parent
BACKEND = REPO / "backend"
sys.path.insert(0, str(BACKEND))

from validators.health_input import validate_health_input  # noqa: E402


def call(path, data=None):
    body = None if data is None else json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(BASE_URL + path, data=body, headers={"Content-Type": "application/json; charset=utf-8"} if body is not None else {}, method="POST" if body is not None else "GET")
    try:
        with urlopen(req, timeout=180) as resp:
            return resp.status, json.load(resp)
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def load_valid_dataset_row():
    with (REPO / "models" / "model_metadata.json").open(encoding="utf-8") as f:
        metadata = json.load(f)
    with (REPO / "data" / "raw" / "dataset.csv").open(encoding="utf-8-sig", newline="") as f:
        for line_no, row in enumerate(csv.DictReader(f), start=2):
            selected = {key: row.get(key) for key in metadata["input_fields"]}
            result = validate_health_input(selected, metadata)
            if result["status"] == "success":
                return result["clean_features"], metadata, line_no
    raise RuntimeError("Không tìm thấy dòng CSV hợp lệ theo metadata/validator hiện tại")


def called_agents(response):
    return [e.get("agent") for e in response.get("agent_trace", []) if e.get("status") == "running"]


def show(label, http, data, expected_agents=None):
    agents = called_agents(data)
    print(f"\n=== {label} ===")
    print("HTTP:", http, "| intent:", data.get("intent"), "| status:", data.get("status"))
    print("Agents thực sự được gọi:", " -> ".join(agents) or "không có")
    print("Nguồn:", len(data.get("sources", [])), "| Trace events:", len(data.get("agent_trace", [])))
    print("Trích phản hồi:", str(data.get("answer", ""))[:350].replace("\n", " "))
    if data.get("warnings"):
        print("Warnings:", data["warnings"])
    if expected_agents is not None:
        ok = agents == expected_agents
        print("Luồng Agent:", "PASS" if ok else "CHƯA ĐẠT", "| Kỳ vọng:", expected_agents)
    return agents


def main():
    features, metadata, line_no = load_valid_dataset_row()
    print("Dùng dữ liệu mẫu từ data/raw/dataset.csv, dòng:", line_no)
    print("Thứ tự trường từ metadata:", metadata["input_fields"])
    print("Validator: success | Chỉ sử dụng cho kiểm thử, không phải dữ liệu người dùng")

    scenarios = [
        ("A - hỏi kiến thức", "test6-knowledge", "Người mắc đái tháo đường nên lựa chọn thực phẩm như thế nào?", None, ["medical_knowledge_agent"]),
        ("B1 - thiếu dữ liệu", "test6-missing", "Tôi muốn đánh giá nguy cơ tiểu đường", None, []),
        ("B2 - có dữ liệu", "test6-risk", "Tôi muốn đánh giá nguy cơ tiểu đường. Các triệu chứng thường gặp của đái tháo đường là gì?", features, ["risk_assessment_agent", "medical_knowledge_agent", "medical_advisor_agent"]),
        ("C - triệu chứng", "test6-symptoms", "Các triệu chứng thường gặp của đái tháo đường là gì?", None, ["medical_knowledge_agent", "medical_advisor_agent"]),
    ]
    for label, session, message, health_data, expected in scenarios:
        http, result = call("/api/chat", {"session_id": session, "message": message, "health_data": health_data})
        agents = show(label, http, result, expected)
        if session == "test6-missing":
            print("Missing fields hợp lệ:", result.get("missing_fields") == metadata["input_fields"])
            print("Model không gọi:", "risk_assessment_agent" not in agents)
        if session == "test6-risk":
            print("Risk chạy:", "risk_assessment_agent" in agents)
            print("Không suy đoán nhãn/probability; kiểm tra kết quả thực tế trong answer và trace.")
        params = urlencode({"session_id": session, "limit": 10})
        http2, history = call("/api/history?" + params)
        print("SQLite history:", "PASS" if http2 == 200 and any(row.get("session_id") == session for row in history.get("history", [])) else "CHƯA ĐẠT")
        http3, status = call("/api/agents/status?" + urlencode({"session_id": session}))
        print("SQLite trace:", "PASS" if http3 == 200 and status.get("tracking") == "sqlite_persistent" and status.get("latest_execution") else "CHƯA ĐẠT")

    invalid = dict(features)
    category = next(iter(metadata["categorical_values"]))
    invalid[category] = "__INVALID_TEST_VALUE__"
    http, result = call("/api/chat", {"session_id": "test6-invalid", "message": "Tôi muốn đánh giá nguy cơ tiểu đường", "health_data": invalid})
    show("B3 - sai giá trị phân loại", http, result)
    print("Mong đợi status invalid_input, không có kết quả dự đoán:", result.get("status") == "invalid_input")


if __name__ == "__main__":
    try:
        main()
    except (OSError, URLError, ValueError, KeyError, RuntimeError) as exc:
        print("LỖI KIỂM THỬ:", exc)
        sys.exit(1)

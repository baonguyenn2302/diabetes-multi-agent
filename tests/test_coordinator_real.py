"""Luồng ĐẦY ĐỦ với model thật + Neo4j Aura. Tự bỏ qua nếu thiếu model hoặc chưa kết nối được.
Log ghi vào thư mục tạm, không đụng logs/audit.jsonl thật."""
import pathlib
import tempfile

import pytest


def test_real_pipeline_high_risk():
    from app.agents.monitoring_agent import MonitoringAgent
    tmp_log = MonitoringAgent(pathlib.Path(tempfile.mkdtemp()) / "audit.jsonl")
    try:
        from app.coordinator import build_default_coordinator
        c = build_default_coordinator(monitor=tmp_log)
    except Exception as e:
        pytest.skip(f"Chưa dựng được luồng thật: {type(e).__name__}: {e}")
    try:
        r = c.handle(dict(gender="Male", age=62, hypertension=1, heart_disease=1, smoking_history="former",
                          bmi=33.5, HbA1c_level=8.2, blood_glucose_level=220))
        if r["status"] != "ok" and any("Thiếu ngưỡng" in e["error"] for e in r["errors"]):
            pytest.skip("Neo4j chưa có KB: chạy python scripts/load_kb.py")
        assert r["status"] == "ok"
        assert r["prediction"] is not None and r["prediction"]["prediction"] == 1
        assert any(f["id"] == "R01" for f in r["rules"]["flags"])
        assert len(r["evidence"]) > 0
        assert "[R01]" in r["report"]
    finally:
        c.kg.close()
